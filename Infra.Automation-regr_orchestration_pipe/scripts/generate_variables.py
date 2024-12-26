import os
import sys
import argparse
import logging
from utils import parse_yml
from utils import log
from cci_integration import cci_integration_main

def str_to_bool(value):
    if isinstance(value, bool):
        return value
    if value.lower() in {'false', '0', 'no', 'off'}:
        return False
    elif value.lower() in {'true', '1', 'yes', 'on'}:
        return True
    else:
        raise argparse.ArgumentTypeError(f"Invalid boolean value: {value}")

def parse_versions_file(file_path):
    try:
        return parse_yml(file_path)
    except Exception as e:
        log(f"Error parsing versions file {file_path}: {e}")
        sys.exit(1)


def transform_suppl_keys(suppl_versions):   
    key_mapping = {
        "LATEST_SPRINT": "LATEST_SUPPL_SPRINT",
        "PREVIOUS_SPRINT": "PREVIOUS_SUPPL_SPRINT",
        "N1_RELEASE": "N1_SUPPL_RELEASE",
        "N2_RELEASE": "N2_SUPPL_RELEASE"
    }

    transformed = {}
    for key, value in suppl_versions.items():
        new_key = key_mapping.get(key, key)
        transformed[new_key] = value
    return transformed


def merge_main_and_suppl_versions(main_versions, suppl_versions=None):
    all_versions = main_versions.copy()
    
    if suppl_versions:
        for key, value in suppl_versions.items():
            if key in ["LATEST_SPRINT_TAG", "PREVIOUS_SPRINT_TAG"]:
                continue
            all_versions[key] = value
    return all_versions


def merge_versions(variables, cci_versions):
    for key, value in cci_versions.items():
        if not variables.get(key):  
            variables[key] = value
    return variables


def check_error_warning(variables, args_, cci_mode):
    msg = (
        f"is empty in both CCI and the {args_.file} config file."
        if cci_mode
        else f"is empty in the {args_.file} config file."
)
    for key, value in variables.items():
        log_msg = f"\033[95m{key}: {value}\033[0m"
        if value is None:
            log_msg = f"\033[31m{key}: {value}\033[0m"
        print(f"    {log_msg}")

    if "LATEST_SPRINT" in variables and variables["LATEST_SPRINT"] is None:
        logging.error(f"\033[31mLATEST_SPRINT {msg} \033[0m")
        exit(1)
    if "PG15_LATEST_SPRINT" in variables and variables["PG15_LATEST_SPRINT"] is None:
        logging.error(f"\033[31mPG15_LATEST_SPRINT {msg} \033[0m")
        exit(1)
    if "PG15_PREVIOUS_SPRINT" in variables and variables["PG15_PREVIOUS_SPRINT"] is None:
        logging.warning(f"\033[38;5;208mPG15_PREVIOUS_SPRINT {msg} \033[0m")
    if "PREVIOUS_SPRINT" in variables and  variables["PREVIOUS_SPRINT"] is None:
        logging.warning(f"\033[38;5;208mPREVIOUS_SPRINT {msg}\033[0m")    
    if "PG15_N2_RELEASE" in variables and variables["PG15_N2_RELEASE"] is None:
        logging.warning(f"\033[38;5;208mPG15_N2_RELEASE {msg}\033[0m")  
    if "N2_RELEASE" in variables and variables["N2_RELEASE"] is None:
        logging.warning(f"\033[38;5;208mN2_RELEASE {msg}\033[0m")    
    if "PG15_N1_RELEASE" in variables and variables["PG15_N1_RELEASE"] is None:
        logging.warning(f"\033[38;5;208mPG15_N1_RELEASE {msg}\033[0m")  
    if "N1_RELEASE" in variables and variables["N1_RELEASE"] is None:
        logging.warning(f"\033[38;5;208mN1_RELEASE {msg}\033[0m")
    if "LATEST_SUPPL_SPRINT" in variables and  variables["LATEST_SUPPL_SPRINT"] is None:
        logging.warning(f"\033[38;5;208mLATEST_SUPPL_SPRINT {msg}\033[0m")
    if "PREVIOUS_SUPPL_SPRINT" in variables and  variables["PREVIOUS_SUPPL_SPRINT"] is None:
        logging.warning(f"\033[38;5;208mPREVIOUS_SUPPL_SPRINT {msg}\033[0m")
    if "N1_SUPPL_RELEASE" in variables and  variables["N1_SUPPL_RELEASE"] is None:
        logging.warning(f"\033[38;5;208mPREVIOUS_SUPPL_SPRINT {msg}\033[0m")
    if "N2_SUPPL_RELEASE" in variables and  variables["N2_SUPPL_RELEASE"] is None:
        logging.warning(f"\033[38;5;208mN2_SUPPL_RELEASE {msg}\033[0m")
    
def add_aditional_service_versions(cci_versions, service, key_version):
    main_versions = {}
    versions = cci_versions.get(service, {})
    if "LATEST_SPRINT" in versions :
        main_versions[key_version] = versions["LATEST_SPRINT"]
    return main_versions
    
def main(args_):
    cci_mode = os.getenv("CCI_INTEGRATION", 'True')
    cci_mode = str_to_bool(cci_mode)
    log(f'CCI_INTEGRATION is: {cci_mode}')
    try:
        variables = parse_yml(args_.file)
    except Exception as e:
        variables = ''
        log(f"Error parsing YAML file: {e}")

    if not cci_mode:
        log("CCI_INTEGRATION is set to False. Skipping CCI integration.")
        logging.warning(f"Job will proceed with manual values")
        log(f'Current params from {args_.file} config file:')
        check_error_warning(variables, args_, cci_mode) 
    else:
        try:
            transformed_suppl_versions = None
            cci_versions = parse_versions_file('versions.yml')
            main_versions = cci_versions.get(args_.service_main, {})
            print(f"main_versions = {main_versions}")
            if args_.service_main == 'kafka':
                aditioanal_version = add_aditional_service_versions(cci_versions, "zookeeper-service", "ZOOKEEPER_LATEST")
                if aditioanal_version:
                    main_versions.update(aditioanal_version)
            if args_.service_main == 'streaming-service':
                aditioanal_version = add_aditional_service_versions(cci_versions, "kafka", "KAFKA_VERSION")
                if aditioanal_version:
                    main_versions.update(aditioanal_version)
            if args_.service_suppl:
                suppl_versions = cci_versions.get(args_.service_suppl, {})
                transformed_suppl_versions = transform_suppl_keys(suppl_versions)
            all_versions = merge_main_and_suppl_versions(main_versions, transformed_suppl_versions)

            variables = merge_versions(variables, all_versions)
            logging.info(f"Merged Manifest's params:\n")
            check_error_warning(variables, args_, cci_mode)        
            
        except Exception as e:
            logging.error(f"Error during CCI integration or merging: {e}")

    config_file=args_.config
    try:
        deployer_config = parse_yml(config_file)
        log(f'DEPLOYER CONFIG: {deployer_config}')
    except:
        log('File with deployer config is not found!')

    result = ''
    if variables:
        for i in variables:
            result += '--form variables[' + i + ']=' + str(variables[i]) + ' '
    if deployer_config:
        for i in deployer_config:
            if i == "KUBECONFIG":
                result += '--form variables[' + i + ']=\\' + deployer_config[i] + ' '
                log(f'KUBECONFIG: {deployer_config[i]}')
            else:
                result += '--form variables[' + i + ']=' + str(deployer_config[i]) + ' '

    with open('variables.env', 'w+') as env:
        env.write(f'VARIABLES="{result}"')


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)-5s[%(name)s] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    parser = argparse.ArgumentParser(description='Script to generate VARIABLES string')

    parser.add_argument('-f', '--file',
                        help='Link to yaml file with variables')    
    parser.add_argument('--service_main',
                        help='Main service name')    
    parser.add_argument('--service_suppl',
                        help='Supplementary service name',
                        default=None)
    parser.add_argument('--config',
                        help='Deployer and cloud config',
                        default='qa_kuber_config.yml')


    args = parser.parse_args()
    main(args)

