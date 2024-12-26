from ExternalPlatformLib import ExternalPlatformLib
import argparse


def main(args_):
    k8slib = ExternalPlatformLib(args_.cloud_token, args_.cloud_host)
    k8slib.delete_crd_with_undefine_version(args_.crd_name, with_check=True)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to prepare namespaces in cloud')
    parser.add_argument('--cloud-host',
                        help='Cloud host')
    parser.add_argument('--cloud-token',
                        help='Cloud token')
    parser.add_argument('--crd-name',
                        help='CRD name to be deleted')                    
    args = parser.parse_args()
    main(args)
