from ExternalPlatformLib import ExternalPlatformLib
from FilesPlatformLib import FilesPlatformLib
import argparse
import yaml

import os
import time
from kubernetes import client, config

gl = gl.Gl('https://git.qubership.org',private_token='')

def main(args_):
    k8slib = ExternalPlatformLib(args_.cloud_token, args_.cloud_host)
    file_lib = FilesPlatformLib()
    # Create Restriced Role and RB
    print(f'\033[32m---------- Start to create Restricted Roles and RoleBindings in namespace: {args_.namespace}\033[0m')
    k8slib.create_restricted_roles([args_.namespace])
    k8slib.create_restricted_role_bindings([args_.namespace], restricted_sa_name='restricted-sa')
    # Create CRDs and Cluster Resources
    if os.path.exists('./scripts/'):
        print(f'\033[36m StartToCreateCRDForService: {args_.namespace}\033[0m')
        cloud_type = k8slib.get_cloud_type()
        print(cloud_type)
        get_content_and_apply_crd(k8slib, crd_tag=args_.crd_tag)
        get_content_and_apply_cluster_resources(k8slib, crd_tag=args_.crd_tag, namespace=args_.namespace, cloud_type=cloud_type)
    else:
        print(f'There is no folder with configuration of CRDs')

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

def get_content_and_apply_cluster_resources(k8slib, crd_tag, namespace, cloud_type):
    path_to_crd, ref, project_id = get_info_for_cluster_resources(file='./restricted/crd_links.yml', crd_tag=crd_tag, resource_type='crs')
    print(f'[INFO] Cluster Resources data: path_to_cr - {path_to_crd}, ref - {ref}, project_id - {project_id}')
    project = gl.projects.get(project_id)
    for path in path_to_crd:
        for d in project.repository_tree(path=path, ref=ref):
            filename = d.get('name')
            filepath = d.get('path')
            if filename != 'kubernetes' and filename != 'openshift':
                id = d.get('id')
                name = d.get('name')
                file_content = project.repository_raw_blob(id)
                yaml_obj = yaml.safe_load(file_content)
                # Replace <platform-monitoring-namespace> to namespace
                input_dict = replace_namespace_field(yaml_obj, namespace)
                # Delete and Create Cluster Resources
                name = input_dict.get('metadata').get('name')
                kind = input_dict.get('kind')
                def apply_resources(name, body, namespace):
                    namespace_etcd = input_dict.get('metadata').get('namespace')
                    if kind == 'ClusterRoleBinding':
                        k8slib.delete_cluster_role_binding(name=name)
                        time.sleep(10)
                        k8slib.create_cluster_role_binding(body=body)
                    elif kind == 'ClusterRole':
                        k8slib.delete_cluster_role(name=name)
                        time.sleep(10)
                        k8slib.create_cluster_role(body=body)
                    elif kind == 'RoleBinding':
                        k8slib.delete_namespaced_role_binding_by_name(name=name, namespace=namespace_etcd)
                        time.sleep(10)
                        k8slib.create_namespaced_role_binding(body=body, namespace=namespace_etcd)
                    elif kind == 'Role':
                        k8slib.delete_namespaced_role(name=name, namespace=namespace_etcd)
                        time.sleep(10)
                        k8slib.create_namespaced_role(body=body, namespace=namespace_etcd)
                    elif kind == 'SecurityContextConstraints':
                        apiVersion = input_dict.get('apiVersion')
                        getVersion = apiVersion.split("/")
                        version = getVersion[1]
                        k8slib.delete_security_context_constraints(name=name, version=version)
                        time.sleep(10)
                        k8slib.create_security_context_constraints(body=body, version=version)
                    elif kind == 'Service':
                        if(cloud_type == 'kubernetes'):
                            k8slib.delete_namespaced_service(name=name, namespace=namespace_etcd)
                            time.sleep(10)
                            k8slib.create_namespaced_service(body=body, namespace=namespace_etcd)
                if ('openshift' in filepath and cloud_type == 'openshift'):
                    apply_resources(name=name, body=input_dict, namespace=namespace)
                elif ('openshift' in filepath and cloud_type == 'kubernetes'):
                    continue
                elif ('openshift' not in filepath and cloud_type == 'openshift' and 'etcd' in filepath):
                    continue
                elif(cloud_type == 'openshift' and 'kubernetes' in filepath):
                    continue
                else:
                    apply_resources(name=name, body=input_dict, namespace=namespace)

def get_content_and_apply_crd(k8slib, crd_tag):
    path_to_crd, ref, project_id = get_info_for_cluster_resources(file='./restricted/crd_links.yml', crd_tag=crd_tag, resource_type='crds')
    print(f'[INFO] CRDs data: path_to_crd - {path_to_crd}, ref - {ref}, project_id - {project_id}')
    project = gl.projects.get(project_id)
    for path in path_to_crd:
        for d in project.repository_tree(path=path, ref=ref, iterator=True):
            filename = d.get('name')
            if filename != 'README.md':
                id = d.get('id')
                file_content = project.repository_raw_blob(id)
                if b'- =~' in file_content and filename == 'monitoring.coreos.com_alertmanagerconfigs.yaml':
                    file_content = file_content.replace(b"- =~", b"- '=~'")
                if b'- =' in file_content and filename == 'monitoring.coreos.com_alertmanagerconfigs.yaml':
                    file_content = file_content.replace(b"- =", b"- '='")
                yaml_obj = yaml.safe_load(file_content)
                name = yaml_obj.get('metadata').get('name')
                if k8slib.get_custom_resource_definition(name=name, version='v1'):
                    with open(f'crds/{filename}', 'w',) as f :
                        #print(filename)
                        yaml.dump(yaml_obj,f,sort_keys=False)
                else:
                    k8slib.create_custom_resource_definition(body=yaml_obj, version='v1')

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
    args = parser.parse_args()
    main(args)
    print('End')
