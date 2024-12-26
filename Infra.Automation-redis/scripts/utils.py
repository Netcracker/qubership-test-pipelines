import yaml


def log(mes, indent=1):
    print(f'{"=" * indent}> {mes}')


def parse_yml(file):
    with open(file) as f:
        params = yaml.safe_load(f)
    return params


def read_ini(file):
    with open(file) as f:
        params = f.read()
    return params
