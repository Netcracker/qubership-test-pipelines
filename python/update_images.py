import os
import yaml
import argparse

#path to values.yaml. Repository name and path to chart we are getting from evn variables
path_to_values = f'{os.environ["repository_name"]}/{os.environ["path_to_chart"]}/values.yaml'
#list of components for which we need to replace images
components = os.environ["components"]

def main(args_):
    branch = args_.service_branch
    with open(path_to_values) as file:
        try:
            values = yaml.safe_load(file)
        except yaml.YAMLError as exc:
            print(exc)

    branch_tag = branch.replace("/", "_")
    new_images = ""
    for component in components.split(','):
        image = values[component]["image"].split(":")[0]
        new_images += f'--set {component}.image={image}:{branch_tag} '
    env_file = os.getenv('GITHUB_ENV')
    with open(env_file, "a") as myfile:
        myfile.write(f'SET_NEW_IMAGES={new_images}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to prepare namespaces in cloud')
    parser.add_argument('--service_branch', type=str, default='main',
                        help='branch name in repository with service')
    args = parser.parse_args()
    main(args)