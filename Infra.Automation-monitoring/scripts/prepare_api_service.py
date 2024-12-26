from ExternalPlatformLib import ExternalPlatformLib
import argparse
import yaml

import os
import time

gl = gl.Gl('https://git.qubership.org',private_token='')

def main(args_):
    k8slib = ExternalPlatformLib(args_.cloud_token, args_.cloud_host)
    # Create Restriced Role and RB
    if args_.api_version != '' and args_.api_version is not None:
        av_list = args_.api_version.split(',')
        print(f'Api_services to create: {av_list}')
        get_content_and_apply_api_version(k8slib, args_.crd_tag, args_.namespace, av_list)

def prepare_cluster_resources(policy_file, namespace):
    input_dict = replace_namespace_field(policy_file, namespace)
    return input_dict

def replace_namespace_field(input_dict, new_namespace):
    for key, value in input_dict.items():
        if isinstance(value, str):
            input_dict[key] = value.replace("<platform-monitoring-namespace>", new_namespace)
        elif isinstance(value, dict):
            replace_namespace_field(value, new_namespace)
        elif isinstance(value, list):
            for index, item in enumerate(value):
                if isinstance(item, str):
                    value[index] = item.replace("<platform-monitoring-namespace>", new_namespace)
                elif isinstance(item, dict):
                    replace_namespace_field(item, new_namespace)
    return input_dict

def get_info_for_cluster_resources(file, crd_tag, resource_type):
    with open(file, "r") as stream:
        path = []
        data = yaml.safe_load(stream)
        service_path = data[resource_type]
        project_id = data['id']
        print(f'[INFO] crd_tag == {crd_tag}')
        if 'tag' in crd_tag:
            ref = data[crd_tag]
        else:
            ref = crd_tag
    if service_path:
        for link in service_path:
            path.append(link)
        return path, ref, project_id

def get_content_and_apply_api_version(k8slib, crd_tag, namespace, api_list):
    path_to_api, ref, project_id = get_info_for_cluster_resources(file='./restricted/crd_links.yml', crd_tag=crd_tag, resource_type='api-version')
    print(f'[INFO] Api Version data: path_to_api_version - {path_to_api}, ref - {ref}, project_id - {project_id}')
    project = gl.projects.get(project_id)
    for path in path_to_api:
        for d in project.repository_tree(path=path, ref=ref):
            filename = d.get('name')
            if 'clusterrole' not in filename and 'clusterrolebinding' not in filename:
                id = d.get('id')
                file_content = project.repository_raw_blob(id)
                yaml_obj = yaml.safe_load(file_content)
                name = yaml_obj.get('metadata').get('name')
                if name in api_list:
                    print(f'Start to create api_version: {name}')
                    input_dict = prepare_cluster_resources(yaml_obj, namespace)
                    k8slib.create_api_service(input_dict)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to prepare namespaces in cloud')
    parser.add_argument('--cloud-host',
                        help='Cloud host')
    parser.add_argument('--cloud-token',
                        help='Cloud token')
    parser.add_argument('--namespace',
                        help='Namespace')
    parser.add_argument('--crd-tag',
                        default='tag',
                        help='Crd tag: tag/old-tag')
    parser.add_argument('--api-version',
                        default=None,
                        help='v1beta1.custom.metrics.k8s.io,v1beta1.metrics.k8s.io')
    args = parser.parse_args()
    main(args)
