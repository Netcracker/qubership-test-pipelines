import requests
import base64
import argparse

cci_url = 'https://cci.qubership.org'
oauth_provider = 'https://fc-sso.qubership.org/auth/realms/cci/protocol/openid-connect/token'

def get_token(user, password):
    idp_client = base64.b64encode((user + ':' + password).encode())
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Authorization': 'Basic ' + idp_client.decode("utf-8"),
        'Accept': 'application/json'
    }
    data = {'grant_type': 'client_credentials'}
    try:
        resp = requests.request('POST',
                                oauth_provider,
                                data=data,
                                headers=headers)
        content = resp.json()
    except:
        print('Not possible to get token')
        content = None
    return content['access_token']

def get_system_configuration_release_id(name, headers):
    resp = requests.get(url=f'{cci_url}/api/v1/public/systemConfigurations?name={name}',
                        headers=headers)
    if resp.status_code == 401:
        print('[ERROR] Unauthorized 401 to CCI')
    return resp.json()[0]['id']

def get_services_versions_by_release_id(id, headers):
    resp = requests.get(url=f'{cci_url}/api/v1/public/sys-config/{id}/versions', headers=headers)
    versions = {}
    for service in resp.json():
        versions[service['applicationName']] = service['versionValue']
    return versions

def main(args):
    versions = None
    user_token = get_token(args.user, args.password)
    headers = {
        'Authorization': f'Bearer {user_token}'
    }
    try:
        id = get_system_configuration_release_id(args.release, headers)
        print(f'ID={id} for release={args.release}')
        versions = get_services_versions_by_release_id(id, headers)
    except:
        print(f'Something wrong happened during work with CCI API')
    if versions:
        with open('.env', 'w') as writer:
            for key, value in versions.items():
                key = key.replace('-', '_')
                writer.write(f'export {key}={value}\n')
    else:
        print(f'Versions are not defined, Exit_code 1')
        exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to get service version from CCI')
    parser.add_argument('--release',
                        help='Name of Release/Sprint')
    parser.add_argument('--user',
                        help='User for CCI')
    parser.add_argument('--password',
                        help='Password for user to CCI')
    args = parser.parse_args()
    main(args)