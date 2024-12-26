from ExternalPlatformLib import ExternalPlatformLib
import argparse


def main(args_):
    k8slib = ExternalPlatformLib(args_.cloud_token, args_.cloud_host)
    if args_.label == 'add':
        k8slib.annotate_namespace_labels(args_.namespace, 'baseline')
        print(f'Label baseline successfully added to ns: {args_.namespace}')
    elif args_.label == 'remove':
        k8slib.remove_namespace_label(args_.namespace)
        print(f'Label baseline successfully removed from ns: {args_.namespace}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to prepare namespaces in cloud')
    parser.add_argument('--cloud-host',
                        help='Cloud host')
    parser.add_argument('--cloud-token',
                        help='Cloud token')
    parser.add_argument('--namespace',
                        help='Namespace')
    parser.add_argument('--label',
                        help='add or remove')
    args = parser.parse_args()
    main(args)