import argparse
import os
from utils import log
from ExternalPlatformLib import ExternalPlatformLib
import time

def main(args_):
    namespace = args_.cloud_namespace
    pv_str = args_.pv_list
    cr_str = args_.cr_list
    api_services = args_.api_services
    pv_list = None
    cr_list = None
    api_services_list = None
    if pv_str:
      pv_list = pv_str.split(",")
    if cr_str:
      cr_list = cr_str.split(",")
    if api_services:
      api_services_list = api_services.split(",")
    k8slib = ExternalPlatformLib(args_.cloud_token, args_.cloud_host)
    k8slib.delete_collection_namespaced_deployment(namespace)
    k8slib.delete_collection_namespaced_stateful_set(namespace)
    k8slib.delete_collection_namespaced_replication_controller(namespace)
    k8slib.delete_collection_namespaced_replica_set(namespace)
    k8slib.delete_collection_namespaced_pod(namespace)
    k8slib.delete_collection_namespaced_service(namespace)
    k8slib.delete_collection_namespaced_ingress(namespace)
    k8slib.delete_collection_namespaced_event(namespace)
    k8slib.delete_collection_namespaced_config_map(namespace)
    k8slib.delete_collection_namespaced_daemon_set(namespace)
    k8slib.delete_collection_namespaced_persistent_volume_claim(namespace)
    time.sleep(10)
    k8slib.delete_collection_namespaced_deployment(namespace)
    k8slib.delete_collection_namespaced_stateful_set(namespace)
    k8slib.delete_collection_namespaced_replication_controller(namespace)
    k8slib.delete_collection_namespaced_replica_set(namespace)
    k8slib.delete_collection_namespaced_pod(namespace)
    k8slib.delete_collection_namespaced_service(namespace)
    k8slib.delete_collection_namespaced_secret_exclude_helm_based(namespace)
    k8slib.delete_collection_namespaced_service_account(namespace)
    k8slib.delete_collection_namespaced_role(namespace)
    k8slib.delete_collection_namespaced_role_binding(namespace)
    k8slib.delete_collection_namespaced_dashboards(namespace)
    k8slib.delete_collection_namespaced_service_monitors(namespace)
    k8slib.delete_collection_namespaced_pod_monitors(namespace)
    k8slib.delete_collection_namespaced_prometheus_rules(namespace)
    k8slib.delete_collection_namespaced_persistent_volume_claim(namespace)
    time.sleep(5)
    if cr_list:
        for cr in cr_list:
            k8slib.delete_collection_namespaced_custom_object(group=args_.group, version=args_.version, namespace=namespace, plural=cr)
    if pv_list:
        try:
            k8slib.patch_pv(pv_list)
        except:
            print('Issue during patching PVs')
    if api_services_list:
        for api_service in api_services_list:
            k8slib.delete_api_service(api_service)
    time.sleep(5)


if __name__ == '__main__':
    log(f'Running script "{os.path.basename(__file__)}"...', 0)
    log('Parse command line arguments...')

    parser = argparse.ArgumentParser(description='Script to execute Kubernetes commands')

    parser.add_argument('--cloud-token',
                        help='Cloud token')
    parser.add_argument('--cloud-host',
                        help='Cloud host')
    parser.add_argument('--cloud-namespace',
                        help='Cloud namespace')
    parser.add_argument('--pv-list',
                        help='PV list', default="")
    parser.add_argument('--cr-list',
                        help='List of plurals for custom resources', default="")
    parser.add_argument('--group',
                        help='Group in custom resources', default="qubership.org")
    parser.add_argument('--version',
                        help='Version in custom resources', default="v1")
    parser.add_argument('--api-services',
                        help='List of api services', default="")
    args = parser.parse_args()

    main(args)
