from ExternalPlatformLib import ExternalPlatformLib
import argparse


def main(args_):
    k8slib = ExternalPlatformLib(args_.cloud_token, args_.cloud_host)
    try:
        k8slib.create_namespace(args_.namespace)
        print(f'Namespace {args_.namespace} created')
    except Exception as e:
        print(f'{e}')
    


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to prepare namespaces in cloud')
    parser.add_argument('--cloud-host',
                        help='Cloud host')
    parser.add_argument('--cloud-token',
                        help='Cloud token')
    parser.add_argument('--namespace',
                        help='Namespace')
    args = parser.parse_args()
    main(args)