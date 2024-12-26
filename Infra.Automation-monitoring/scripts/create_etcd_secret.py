import ExternalPlatformLib
import argparse
import base64


def get_encoded_cert(result):
    if 'RSA' in result:
        etcd_crt = result[31:-30].replace(" ", "\n")
        begin = '-----BEGIN RSA PRIVATE KEY-----'
        end = '\n-----END RSA PRIVATE KEY-----\n'
    else:
        etcd_crt = result[27:-26].replace(" ", "\n")
        begin = '-----BEGIN CERT-----'
        end = '\n-----END CERTIFICATE-----'
    etcd_client_ca_crt = f"{begin}{etcd_crt}{end}"
    etcd_client_ca_crt_encode = etcd_client_ca_crt.encode("ascii")
    base64_bytes = base64.b64encode(etcd_client_ca_crt_encode)
    return base64_bytes

def create_secret_with_certs_for_prometheus(args_):
    k8slib = ExternalPlatformLib.ExternalPlatformLib(args_.cloud_token, args_.cloud_host)
    pods = k8slib.list_namespaced_pod(namespace='kube-system')
    etcd_pods = []
    for pod in pods.items:
        if 'etcd' in pod.metadata.name:
            etcd_pods.append(pod.metadata.name)
    command = ['echo $(</etc/kubernetes/pki/etcd/ca.crt)', 'echo $(</etc/kubernetes/pki/etcd/peer.crt)', 'echo $(</etc/kubernetes/pki/etcd/peer.key)']
    if etcd_pods:
        certs = []
        for i in range(3):
            result, error = k8slib.execute_command_in_pod(etcd_pods[0], 'kube-system', command[i], 'etcd', '/bin/sh')
            base64_bytes = get_encoded_cert(result)
            certs.append(base64_bytes)
    else:
        print('\033[33m NO one etc pod found \033[0m')
    secrets = k8slib.list_namespaced_secret_names(namespace=args_.prometheus_namespace)
    # print(secrets)
    if 'kube-etcd-client-certs' in secrets:
        kube_etcd_client_certs = k8slib.read_namespaced_secret('kube-etcd-client-certs', args_.prometheus_namespace)
        kube_etcd_client_certs.data = {'etcd-client-ca.crt': certs[0].decode('utf-8'), 'etcd-client.crt': certs[1].decode('utf-8'), 'etcd-client.key': certs[2].decode('utf-8')}
        k8slib.replace_namespaced_secret('kube-etcd-client-certs', args_.prometheus_namespace, kube_etcd_client_certs)
    else:
        print(f'\033[33m Secret: kube-etcd-client-certs not found in namespace: {args_.prometheus_namespace}. Please, create it and rebuild this job!\033[0m')





if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to execute Openshift commands')

    parser.add_argument('--cloud-host',
                        help='Cloud host')
    parser.add_argument('--cloud-token',
                        help='Cloud token')
    parser.add_argument('--prometheus-namespace',
                        help='Prometheus namespace',
                        default='prometheus-operator')
    args = parser.parse_args()
    create_secret_with_certs_for_prometheus(args)