from ExternalPlatformLib import ExternalPlatformLib
import argparse
import yaml
import gl

gl = gl.Gl('https://git.qubership.org',private_token='')

def main(args_):
    k8slib = ExternalPlatformLib(args_.cloud_token, args_.cloud_host)
    # Create CRDs
    try:
        print('\033[36m StartToCreateCRDForService\033[0m')
        get_content_and_replace_crd(k8slib, args_.service, args_.crd_tag)
    except:
        print('Not possible to apply CRD for service')
    print('\033[32m CRDs, ClusterRoles, ClusterRoleBindings are created successfully! \033[0m')

def get_info_for_crd(file, service, crd_tag):
    with open(file, "r") as stream:
        try:
            path = []
            data = yaml.safe_load(stream)
            print(f'[INFO] crd_tag == {crd_tag}')
            if service:
                service_path = data[f'{service}-crds']
                if 'tag' in crd_tag:
                    ref = data[f'{service}-{crd_tag}']
                else:
                    ref = crd_tag
                project_id = data[f'{service}-id']
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
                return path, ref, project_id
        except yaml.YAMLError as exc:
            print(exc)

def get_content_and_replace_crd(k8slib, service, crd_tag):
    path_to_crd, ref, project_id = get_info_for_crd(file='./restricted/crd/crd_links.yml', service=service, crd_tag=crd_tag)
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
                    k8slib.patch_custom_resource_definition(name=name, body=crd)
            except:
                print(f'Issue with crd (get yaml content): {name}')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to upgrade CRD in cloud')
    parser.add_argument('--cloud-host',
                        help='Cloud host')
    parser.add_argument('--cloud-token',
                        help='Cloud token')
    parser.add_argument('--crd-tag',
                        default='tag',
                        help='Crd tag: tag/old-tag')
    parser.add_argument('--service',
                        default='',
                        help='Service name: zookeeper/kafka/streaming/opensearch/rabbit/consul/vault')
    args = parser.parse_args()
    main(args)
