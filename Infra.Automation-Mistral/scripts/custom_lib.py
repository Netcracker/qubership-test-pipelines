import argparse
import os
import sys
import time
from kubernetes import client, config
from utils import log
from utils import parse_yml


def main(args_):
    aToken = args_.cloud_token
    aConfiguration = client.Configuration()
    aConfiguration.host = args_.cloud_host
    aNamespace = args_.cloud_namespace
    pv_str = args_.pv_list
    pv_list = pv_str.split(",")
    
    print("For debug purposes", aToken, aConfiguration.host, pv_list)

    aConfiguration.verify_ssl = False
    aConfiguration.api_key = {"authorization": "Bearer " + aToken}
    aApiClient = client.ApiClient(aConfiguration)

    v1 = client.CoreV1Api(aApiClient)
    k8s_beta = client.AppsV1Api(aApiClient)
    k8s_job = client.BatchV1Api(aApiClient)
    rbac_beta = client.RbacAuthorizationV1beta1Api(aApiClient)
    k8s_CR = client.CustomObjectsApi(aApiClient)
    
    for service in v1.list_namespaced_service(aNamespace).items:
        service_name = service.metadata.name
        v1.delete_namespaced_service(service_name, aNamespace)
        print('service deleted ', service_name)
    
    k8s_beta.delete_collection_namespaced_deployment(aNamespace)
    print('deployments deleted')
    k8s_beta.delete_collection_namespaced_stateful_set(aNamespace)
    print('stateful_set deleted')
    k8s_beta.delete_collection_namespaced_replica_set(aNamespace)
    print('replica_set deleted')
    k8s_job.delete_collection_namespaced_job(aNamespace)
    print('jobs deleted')
    v1.delete_collection_namespaced_secret(aNamespace)
    print('secrets deleted')
    v1.delete_collection_namespaced_event(aNamespace)
    print('events deleted')
    v1.delete_collection_namespaced_config_map(aNamespace)
    print('config-maps deleted')
    v1.delete_collection_namespaced_service_account(aNamespace)
    print('service-accounts deleted')
    v1.delete_collection_namespaced_pod(aNamespace)
    print('pods deleted')
    v1.delete_collection_namespaced_persistent_volume_claim(aNamespace)
    print('pvc deleted')
    rbac_beta.delete_collection_namespaced_role_binding(aNamespace)
    print('role bindings deleted')
    rbac_beta.delete_collection_namespaced_role(aNamespace)
    print('role deleted')
    k8s_CR.delete_collection_namespaced_custom_object(
        group='qubership.org',
        version='v1alpha',
        namespace=aNamespace,
        plural='rabbitmqservices')
    time.sleep(120)
    necessary_body = [
        {
            'op': 'replace',
            'path': '/spec/claimRef',
            'value': None
        },
        {
            'op': 'replace',
            'path': '/status/phase',
            'value': 'Available'
        }
    ]

    for i in pv_list:
        result = v1.patch_persistent_volume(i, necessary_body)
        print(f'{i} was patched')
    



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
                        help='PV list')
    args = parser.parse_args()

    main(args)
