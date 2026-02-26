import os
import yaml
import argparse


def main(args_):
    path_to_file = args_.path_to_file
    with open(path_to_file) as file:
        try:
            template = yaml.safe_load(file)
        except yaml.YAMLError as exc:
            print(exc)
    template['metadata']['namespace'] = args_.nc
    with open(path_to_file, 'w') as file:
        file.write(yaml.dump(template, default_flow_style=False))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to replace namespace in templates of resources')
    parser.add_argument('--path_to_file', type=str,
                        help='path to yaml file with template')
    parser.add_argument('--nc', type=str,
                        help='new namespace')
    args = parser.parse_args()
    main(args)