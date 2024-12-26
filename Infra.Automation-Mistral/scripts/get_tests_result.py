import custom_lib as lib
import argparse
import os
from utils import log

def main(args_):
    client = lib.generate_k8s_client(args_.cloud_token, args_.cloud_host)
    log('START CHECKING TEST RESULTS')
    lib.get_tests_result(client, args_.cloud_project, args_.timeout)

if __name__ == '__main__':
    log(f'Running script "{os.path.basename(__file__)}"...', 0)
    log('Parse command line arguments...')

    parser = argparse.ArgumentParser(description='Script to execute Openshift commands')

    parser.add_argument('--cloud-host',
                        help='Cloud host')
    parser.add_argument('--cloud-project',
                        help='Cloud project')
    parser.add_argument('--cloud-token',
                        help='Cloud token')
    parser.add_argument('--timeout',
                        help='Test parsing timeout (in minutes)')
    args = parser.parse_args()

    main(args)
