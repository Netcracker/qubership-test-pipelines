import requests
import base64
import argparse
from utils import log
import logging
import sys
import yaml
import argparse
import yaml
import re


cci_url = 'https://cci.qubership.org'
oauth_provider = 'https://fc-sso.qubership.org/auth/realms/cci/protocol/openid-connect/token'

def str_to_bool(value):
    if isinstance(value, bool):
        return value
    if value.lower() in {'false', '0', 'no', 'off'}:
        return False
    elif value.lower() in {'true', '1', 'yes', 'on'}:
        return True
    else:
        raise argparse.ArgumentTypeError(f"Invalid boolean value: {value}")
    
def get_token(cci_user, cci_password):
    idp_client = base64.b64encode((cci_user + ':' + cci_password).encode())
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic ' + idp_client.decode("utf-8"),
        'Accept': 'application/json'
    }
    data = {'grant_type': 'client_credentials'}
    try:
        resp = requests.post(oauth_provider, data=data, headers=headers)
        if resp.status_code == 200:
            return resp.json()['access_token']
        else:
            logging.error(f"Failed to get token. Status Code: {resp.status_code}, Response: {resp.json()}")
            sys.exit(1)
    except Exception as e:
        logging.error(f"Error during token generation: {e}")
        sys.exit(1)

def get_all_releases(headers):
    resp = requests.get(url=f'{cci_url}/api/v1/public/projects/2/configurations',
                        headers=headers)
    if resp.status_code != 200:
        logging.error(f"Failed to fetch releases. Status Code: {resp.status_code}")
        sys.exit(1)

    releases = [release['name'] for release in resp.json()]
    releases.sort(reverse=True)
    return releases

def get_prefix(service_name):
    prefix = ""
    if service_name == "postgres":
        prefix = "PG15_"
    return prefix

def get_system_configuration_release_id(name, headers):
    resp = requests.get(url=f'{cci_url}/api/v1/public/systemConfigurations?name={name}',
                        headers=headers)
    if resp.status_code == 401:
        logging.error('[ERROR] Unauthorized 401 to CCI')
        sys.exit(1)
    return resp.json()[0]['id']

def get_services_versions_by_release_id(release_id, headers):
    resp = requests.get(url=f'{cci_url}/api/v1/public/sys-config/{release_id}/versions', headers=headers)
    if resp.status_code != 200:
        logging.error(f"Failed to fetch services for release ID {release_id}. Status Code: {resp.status_code}")
        return {}
    return {service['applicationName']: service['versionValue'] for service in resp.json()}

def defining_releases_sequence(current_release, all_releases):
    if current_release not in all_releases:
        logging.error(f"\033[91mRelease '{current_release}' not found in available releases.\033[0m")
        sys.exit(1)

    current_release_index = all_releases.index(current_release)
    previous_sprint = all_releases[current_release_index+1]
    lts_releases = [release for release in all_releases[current_release_index+1:] if "LTS" in release]
    if len(lts_releases) == 0:
        logging.error('Seems like you specified so old `RELEASE`, CCI doesn`t contain releases for N-1/N-2, please override values for that releases via `--override-versions` flag')
        lts_releases = [None, None]
    elif len(lts_releases) < 2:
        logging.error('Seems like you specified so old `RELEASE`, CCI doesn`t contain releases for N-2, please override values for that release via `--override-versions` flag')
        lts_releases = [lts_releases[0], None]
    return current_release, previous_sprint, lts_releases[0], lts_releases[1]

def ensure_all_release_keys_exist(all_services_versions, releases_dict):
    for service, releases in all_services_versions.items():
        prefix = ""
        if service == "postgres":
            prefix = "PG15_"
        for key, value in releases_dict.items():
            new_key = f"{prefix}{key}"
            if new_key not in releases:
                releases[new_key] = None
    return all_services_versions

def log_services_with_missing_values(all_services_versions):
    
    for service, releases in all_services_versions.items():
        result = []
        log(f"Service '\033[95m{service}\033[0m'\n")
        for key, value in releases.items():
            msg = f"\033[32m{key}: {value}\033[0m"
            result.append(msg)
            if value is None:
                msg = f"\033[31m{key}: {value}\033[0m"
                result.append(msg)
            print(f"    {msg}")
        print(f"\n")

def extract_branch_tag_by_regexp(value):
    pattern = r"release-\d+\.\d+-\d+\.\d+\.\d+(?:-\d+)?|release-\d+\.\d+-\d+-\d+\.\d+\.\d+|(?<!\d)\d+\.\d+\.\d+(?!\d)"
    match = re.search(pattern, value)
    if match:
        return match.group()
    else:
        print(f" No match found for manifest {value}")
        return None
    
def create_service_versions_with_tag(all_service_versions):
    all_service_versions_with_tag = all_service_versions.copy()
    for service, versions in all_service_versions.items():
        all_service_versions_with_tag[service]["LATEST_SPRINT_TAG"] = None
        all_service_versions_with_tag[service]["PREVIOUS_SPRINT_TAG"] = None
        if service == "MONITORING" and "N1_RELEASE" in versions and versions["N1_RELEASE"] is not None:
            tag = extract_branch_tag_by_regexp(versions["N1_RELEASE"])
            if tag:
                all_service_versions_with_tag[service]["N1_RELEASE_TAG"] = tag
        if service == "MONITORING" and "N2_RELEASE" in versions and versions["N2_RELEASE"] is not None:
            tag = extract_branch_tag_by_regexp(versions["N2_RELEASE"])
            if tag:
                all_service_versions_with_tag[service]["N2_RELEASE_TAG"] = tag
        if "LATEST_SPRINT" in versions and versions["LATEST_SPRINT"] is not None:
            tag = extract_branch_tag_by_regexp(versions["LATEST_SPRINT"])
            if tag:
                all_service_versions_with_tag[service]["LATEST_SPRINT_TAG"] = tag
        if "PREVIOUS_SPRINT" in versions and versions["PREVIOUS_SPRINT"] is not None:
            tag = extract_branch_tag_by_regexp(versions["PREVIOUS_SPRINT"])
            if tag:
                all_service_versions_with_tag[service]["PREVIOUS_SPRINT_TAG"] = tag
        if "PG15_LATEST_SPRINT" in versions and versions["PG15_LATEST_SPRINT"] is not None:
            tag = extract_branch_tag_by_regexp(versions["PG15_LATEST_SPRINT"])
            if tag:
                all_service_versions_with_tag[service]["LATEST_SPRINT_TAG"] = tag
        if "PG15_PREVIOUS_SPRINT" in versions and versions["PG15_PREVIOUS_SPRINT"] is not None:
            tag = extract_branch_tag_by_regexp(versions["PG15_PREVIOUS_SPRINT"])
            if tag:
                all_service_versions_with_tag[service]["PREVIOUS_SPRINT_TAG"] = tag
    return all_service_versions_with_tag

def fetch_versions_for_all_services(releases_dict, headers):
    results = {}
    
    for release_name, release_value in releases_dict.items():
        if not release_value:
            log(f"Skipping release {release_name} as no release value is defined.")
            continue

        release_id = get_system_configuration_release_id(release_value, headers)
        services_versions = get_services_versions_by_release_id(release_id, headers)
        for service, version in services_versions.items():
            prefix = get_prefix(service)
            release_name_with_prefix = f"{prefix}{release_name}"
            if service not in results:
                results[service] = {}
            results[service][release_name_with_prefix] = f'{service}:{version}'

    return results

def generate_yaml_from_versions(all_versions, file_name):
    with open(file_name, 'w') as yaml_file:
        yaml.dump(all_versions, yaml_file, default_flow_style=False)
    log(f"YAML file '{file_name}' created successfully.")

def cci_integration_main(release, cci_user, cci_password, output_file):
    log(f"Current Release/Sprint => \033[95m{release}\033[0m\n")
    user_token = get_token(cci_user, cci_password)
    headers = {
        'Authorization': f'Bearer {user_token}'
    }

    all_releases = get_all_releases(headers)
    current_version, previous_sprint, n_1_release, n_2_release = defining_releases_sequence(release, all_releases)

    releases_dict = {
        'LATEST_SPRINT': current_version,
        'PREVIOUS_SPRINT': previous_sprint,
        'N1_RELEASE': n_1_release,
        'N2_RELEASE': n_2_release
    }

    logging.info(f"Automatically detected following releases/versions for pipeline:\n"
                 f"     \033[95mLATEST_SPRINT: ''
                 f"     PREVIOUS SPRINT: {releases_dict['PREVIOUS_SPRINT']}\n"
                 f"     N1_RELEASE: ''
                 f"     N2_RELEASE: ''

    all_service_versions = fetch_versions_for_all_services(releases_dict, headers)
    all_service_versions = ensure_all_release_keys_exist(all_service_versions, releases_dict)
    all_service_versions_with_tags = create_service_versions_with_tag(all_service_versions)
    log_services_with_missing_values(all_service_versions_with_tags)
    
    
    generate_yaml_from_versions(all_service_versions_with_tags, output_file)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)-5s[%(name)s] - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    
    parser = argparse.ArgumentParser(description='CCI Integration Script to Fetch Versions')
    parser.add_argument('--release', required=True, help='Name of the current release/sprint')
    parser.add_argument('--cci_user', required=True, help='CCI user/client ID')
    parser.add_argument('--cci_password', required=True, help='CCI secret/password')
    parser.add_argument('--output_file', default='services_versions.yml', help='Output YAML file name')
    parser.add_argument("--cci_mode", type=str_to_bool, default=True, help="Enable/Disable CCI integration")

    args = parser.parse_args()
    log(f"CCI_MODE is {args.cci_mode}")
    if not args.cci_mode:
        log("CCI_MODE is set to False. Skipping CCI integration.")
        log(f"Job will proceed with manual values")
        exit(1)
    cci_integration_main(args.release, args.cci_user, args.cci_password, args.output_file)