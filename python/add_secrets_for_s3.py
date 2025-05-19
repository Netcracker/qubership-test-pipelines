import os
import yaml
import argparse


def main(args_):
    path_to_file = args_.path_to_file
    key_id = args_.key_id
    secret_key = args_.secret_key
    print('key_id', key_id)
    with open(path_to_file) as file:
        try:
            template = yaml.safe_load(file)
        except yaml.YAMLError as exc:
            print(exc)
    template['backupDaemon']['s3']['keyId'] = key_id
    template['backupDaemon']['s3']['keySecret'] = secret_key
    with open(path_to_file, 'w') as file:
        file.write(yaml.dump(template, default_flow_style=False))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to replace namespace in templates of resources')
    parser.add_argument('--path_to_file', type=str,
                        help='path to yaml file with template')
    parser.add_argument('--key_id', type=str,
                        help='Access key ID for S3')
    parser.add_argument('--secret_key', type=str,
                        help='Secret access key for S3')
    args = parser.parse_args()
    main(args)
