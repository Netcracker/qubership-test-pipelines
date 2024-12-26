from ExternalPlatformLib import ExternalPlatformLib
from FilesPlatformLib import FilesPlatformLib
import argparse
import yaml
import gl
import os

gl = gl.Gl('https://git.qubership.org',private_token='')

def main(args_):
    k8slib = ExternalPlatformLib(args_.cloud_token, args_.cloud_host)
    file_lib = FilesPlatformLib()
    # Create Restriced Role and RB
    print(f'\033[32m---------- Start to create Restricted Roles and RoleBindings in namespace: {args_.namespace}\033[0m')
    k8slib.create_restricted_roles([args_.namespace])
    k8slib.create_restricted_role_bindings([args_.namespace], restricted_sa_name='restricted-sa')

    # Delete existed ClusterRoles and ClusterRoleBindings
    cluster_roles_files = None
    cluster_roles_binding_files = None
    if os.path.exists('./restricted/clusterRoles/'):
        print(f'\033[36m----------- Clean UP Cluster Resources from cluster -----------\033[0m')
        cluster_roles_files = file_lib.get_files('./restricted/clusterRoles/')
        if cluster_roles_files:
            cluster_roles_names = list(file_lib.get_resources_name(cluster_roles_files))
            if args_.service:
                cluster_roles_names = [item for item in cluster_roles_names if args_.service in item]
            print(f'\033[36m Following ClusterRoles should be deleted in cloud: {str(cluster_roles_names)} \033[0m')
            k8slib.delete_cluster_roles(cluster_roles_names)
    if os.path.exists('./restricted/clusterRoleBindings/'):
        cluster_roles_binding_files = file_lib.get_files('./restricted/clusterRoleBindings/')
        if cluster_roles_binding_files:
            cluster_role_bindings_names = list(file_lib.get_resources_name(cluster_roles_binding_files))
            if args_.service:
                cluster_role_bindings_names = [item for item in cluster_role_bindings_names if args_.service in item]
            print(f'\033[36m Following ClusterRoleBindings should be deleted in cloud: {cluster_role_bindings_names} \033[0m')
            k8slib.delete_cluster_role_bindings(cluster_role_bindings_names)
        print(f'\033[32m----------- Existed ClusterRoles and ClusterRoleBindings are deleted! -----------\033[0m')

    # Create ClusterRoles and ClusterRoleBindings
    if cluster_roles_files:
        if args_.service:
            cluster_roles_files = [item for item in cluster_roles_files if args_.service in item]
        print(f'\033[36m Start to create the following Cluster Roles: {cluster_roles_files} \033[0m')
        k8slib.create_cluster_roles_by_path(cluster_roles_files)
    if cluster_roles_binding_files:
        if args_.service:
            cluster_roles_binding_files = [item for item in cluster_roles_binding_files if args_.service in item]
        print(f'\033[36m Start to create the following Cluster Roles Bindings: {cluster_roles_binding_files}\033[0m')
        k8slib.create_cluster_role_bindings_by_path(cluster_roles_binding_files)

    # Create CRDs
    if os.path.exists('./restricted/crd/'):
        try:
            print(f'\033[36m StartToCreateCRDForService: {args_.namespace}\033[0m')
            get_content_and_apply_crd(k8slib, crd_tag=args_.crd_tag, service=args_.service)
        except:
            print(f'Not possible to apply CRD for service: {args_.namespace}')
        print('\033[32m CRDs, ClusterRoles, ClusterRoleBindings are created successfully! \033[0m')
    else:
        print(f'There is no folder with configuration of CRDs')

def get_info_for_crd(file, crd_tag, service):
    with open(file, "r") as stream:
        try:
            path = []
            data = yaml.safe_load(stream)
            print(f'[INFO] crd_tag == {crd_tag}')
            if service:
                service_path = data[f'{service}-crds']
                project_id = data[f'{service}-id']
                if 'tag' in crd_tag:
                    ref = data[f'{service}-{crd_tag}']
                else:
                    ref = crd_tag
            else:
                service_path = data['crds']
                if 'tag' in crd_tag:
                    ref = data[crd_tag]
                else:
                    ref = crd_tag
                project_id = data['id']
            if service_path:
                for link in service_path:
                    path.append(link)
                    print(f'path, ref, project_id: {path}, {ref}, {project_id}')
                return path, ref, project_id
        except yaml.YAMLError as exc:
            print(exc)

def get_content_and_apply_crd(k8slib, crd_tag, service):
    path_to_crd, ref, project_id = get_info_for_crd(file='./restricted/crd/crd_links.yml', crd_tag=crd_tag, service=service)
    project = gl.projects.get(project_id)
    for path in path_to_crd:
        for d in project.repository_tree(path=path, ref=ref):
            id = d.get('id')
            name = d.get('name')
            file_content = project.repository_raw_blob(id)
            try:
                crds_list = list(yaml.safe_load_all(file_content))
                for crd in crds_list:
                    name = crd.get('metadata').get('name')
                    if k8slib.get_custom_resource_definition(name=name, version='v1'):
                        k8slib.patch_custom_resource_definition(name=name, body=crd)
                    else:
                        k8slib.create_custom_resource_definition(crd, version='v1')
            except:
                print(f'Issue with crd (get yaml content): {name}')

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
    parser.add_argument('--service',
                        default='',
                        help='Service name: zookeeper/kafka/streaming/opensearch/rabbit/consul/vault')
    args = parser.parse_args()
    main(args)
