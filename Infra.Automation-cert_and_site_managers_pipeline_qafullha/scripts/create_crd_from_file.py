from ExternalPlatformLib import ExternalPlatformLib
import argparse
import yaml


def main(args_):
    k8slib = ExternalPlatformLib(args_.cloud_token, args_.cloud_host)
    file = yaml.safe_load_all(open(args_.file, "r"))
    for crd in file:
        name = crd.get('metadata').get('name')
        try:
            if k8slib.get_custom_resource_definition(name=name, version='v1'):
                k8slib.patch_custom_resource_definition(name=name, body=crd)
            else:
                k8slib.create_custom_resource_definition(crd, version='v1')
        except:
            print(f'Issue with crd (creating/patching crd): {name}')
    print(f'CRDs from file created')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to create CRD in cloud')
    parser.add_argument('--cloud-host',
                        help='Cloud host')
    parser.add_argument('--cloud-token',
                        help='Cloud token')
    parser.add_argument('--file',
                        help='YAML file')
    args = parser.parse_args()
    main(args)