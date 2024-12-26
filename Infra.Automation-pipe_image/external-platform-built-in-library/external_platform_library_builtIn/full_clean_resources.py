import argparse
from ExternalPlatformLib import ExternalPlatformLib
import time

def delete_namespace_with_check():
    is_exist = k8slib.is_namespace_exist(args.cloud_namespace)
    if not is_exist:
        return
    k8slib.delete_namespace(args.cloud_namespace)
    timeout = 60
    timeout_start = time.time()
    while time.time() < timeout_start + timeout:
        time.sleep(5)
        is_exist = k8slib.is_namespace_exist(args.cloud_namespace)
        if not is_exist:
            return
    print(f'Namespaces {args.cloud_namespace} is still exist...')
    exit(1)

def delete_service_crds(crds_list):
    for crd in crds_list:
        k8slib.delete_crd_with_undefine_version(crd, with_check=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to execute Kubernetes commands')
    parser.add_argument('--cloud-token', help='Cloud token')
    parser.add_argument('--cloud-host', help='Cloud host')
    parser.add_argument('--cloud-namespace', help='Cloud namespace')
    parser.add_argument('--crd-list', help='List of CRDs names', default="")
    parser.add_argument('--cluster-role-list', help='List of cluster role names', default="")
    parser.add_argument('--cluster-role-binding-list', help='List of cluster role binding names', default="")
    args = parser.parse_args()
    k8slib = ExternalPlatformLib(args.cloud_token, args.cloud_host)
    delete_namespace_with_check()
    if args.crd_list:
        delete_service_crds(args.crd_list.split(","))
    if args.cluster_role_list:
        k8slib.delete_cluster_roles(args.cluster_role_list.split(","))
    if args.cluster_role_binding_list:
        k8slib.delete_cluster_role_bindings(args.cluster_role_binding_list.split(","))
