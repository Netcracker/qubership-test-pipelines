import argparse
import sys

import yaml


def set_new_value(data, path, value):
    keys = path.split('/')
    current = data
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        elif not isinstance(current[key], (dict, list)):
            current[key] = {}
        current = current[key]
    current[keys[-1]] = value


def main(args_):
    path_to_file = args_.file
    try:
        with open(path_to_file) as f:
            data_ = yaml.safe_load(f)
    except yaml.YAMLError as exc:
        print(f'YAML loading error: {exc}')
        sys.exit(1)
    set_new_value(data_, args_.path, args_.value)
    with open(path_to_file, 'w') as f:
        yaml.dump(data_, f, default_flow_style=False, sort_keys=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Script for changing values in YAML files'
    )
    parser.add_argument('-f', '--file', required=True, help='Path to YAML file')
    parser.add_argument(
        '-p',
        '--path',
        required=True,
        help='Path to value to be changed (format: key1/key2/key3)',
    )
    parser.add_argument('-v', '--value', required=True, help='New value')

    args = parser.parse_args()
    main(args)
