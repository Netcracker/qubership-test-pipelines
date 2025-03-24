import os
import yaml
import argparse

#path to values.yaml. Repository name and path to chart we are getting from env variables
#path_to_values = f'{os.environ["repository_name"]}/{os.environ["path_to_chart"]}/values.yaml'
#list of components for which we need to replace images
#components = os.environ["components"]

def main(args_):
    branch = args_.service_branch
    path_to_values = args_.path_to_values
    components = args_.components
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
    parser.add_argument('--path_to_values', type=str,
                        help='path to values.yaml')
    parser.add_argument('--components', type=str,
                        help='list of components in which images should be replaced with images from the current branch')
    args = parser.parse_args()
    main(args)