import requests, re, yaml, time, sys, os
import kubernetes.client
from kubernetes import client, config
from kubernetes.stream import stream
from openshift.dynamic import DynamicClient
from openshift.dynamic import exceptions
from datetime import datetime, timedelta

def generate_k8s_client(token, host):
    aToken = token
    aConfiguration = client.Configuration()
    aConfiguration.host = host

    aConfiguration.verify_ssl = False
    aConfiguration.api_key = {"authorization": "Bearer " + aToken}
    aApiClient = client.ApiClient(aConfiguration)

    v1 = client.CoreV1Api(aApiClient)
    return v1

def generate_os_client(token, host):
    aConfiguration = kubernetes.client.Configuration()
    aConfiguration.host = host
    aConfiguration.verify_ssl = False
    aConfiguration.api_key['authorization'] = token
    aConfiguration.api_key_prefix['authorization'] = 'Bearer'

    # create an instance of the API class
    k8s_client = kubernetes.client.ApiClient(aConfiguration)
    dyn_client = DynamicClient(k8s_client)
    return dyn_client

def generate_os_token(host, login, passwd):
    # Retrieve bearer token for client generating
    session = requests.session()
    token_retriever = host + '/oauth/authorize?client_id=openshift-challenging-client&response_type=token'
    x=session.post(token_retriever, auth=(login, passwd), verify=False, allow_redirects=False)
    loc_ext = str(x.headers)
    start = loc_ext.find("access_token=") + len("access_token=")
    end = loc_ext.find("&")
    bearer_token = loc_ext[start:end]
    return bearer_token

# Kubernetes only
def exec_command(cmd, client, pod, namespace):
    exec_command = [
        '/bin/sh',
        '-c',
        cmd]
    resp = stream(client.connect_get_namespaced_pod_exec, pod, namespace,
                command=exec_command,
                stderr=True, stdin=False,
                stdout=True, tty=False)
    return resp

# Openshift only
def update_access_control_dc(client, token, project):    
    v1_services = client.resources.get(api_version='v1', kind='DeploymentConfig')
    api_response = v1_services.get(name='access-control', namespace=project)

    # IDENTITY_PROVIDER_URL
    api_response.spec.template.spec.containers[0].env[7].value = "http://identity-management.{}.svc.cluster.local:8080".format(project)
    # USER_MANAGEMENT_URL
    api_response.spec.template.spec.containers[0].env[8].value = "http://identity-management.{}.svc.cluster.local:8080".format(project)
    # TOKEN_URL
    api_response.spec.template.spec.containers[0].env[13].value = "http://identity-management.{}.svc.cluster.local:8080/token".format(project)
    v1_services.patch(name='access-control', body=api_response, namespace=project)

# Openshift only
def delete_resources_ac(client, token, project):
    resources = {
        'DeploymentConfig': 'access-control',
        'Service': 'access-control',
        'Route': 'access-control'
    }
    for k, v in resources.items():
        v1_services = client.resources.get(api_version='v1', kind=k)
        try:
            print('Trying to delete {} {}...'.format(k, v))
            v1_services.delete(name=v, namespace=project)
        except exceptions.NotFoundError:
            print('{} {} is not found, so skip this step...'.format(k, v))

    resources = {
        'access-control.monitoring-config': 'ConfigMap',
        'deployment-info-access-control': 'ConfigMap',
        'deploy-pips-config': 'ConfigMap',
        'deploy-policies-config': 'ConfigMap',
        'access-control-client-credentials': 'Secret',
        'access-control-pg-credentials': 'Secret',
        'registered-client-access-control': 'Secret'
    }
    for k, v in resources.items():
        v1_services = client.resources.get(api_version='v1', kind=v)
        try:
            print('Trying to delete {} {}...'.format(v, k))
            v1_services.delete(name=k, namespace=project)
        except exceptions.NotFoundError:
            print('{} {} is not found, so skip this step...'.format(v, k))

    v1_services = client.resources.get(api_version='v1', kind='ReplicationController')
    api_response = v1_services.get(namespace=project)
    rcs = re.findall('(?<=openshift.io/deployment.name: )access-control-[0-9]+', str(api_response))
    for rc in rcs:
        api_response = v1_services.get(name=rc, namespace=project)
        try:
            v1_services.delete(name=rc, namespace=project)
        except exceptions.NotFoundError:
            print('Unknown error with {} RC deletion. Contact someone.'.format(rc))

    v1_services = client.resources.get(api_version='v1', kind='Pod')
    api_response = v1_services.get(namespace=project)
    pods = re.findall('(?<=name: )access-control-.*-(?:\d+[a-z]|[a-z]+\d)[a-z\d]*', str(api_response))
    for name in pods:
        try:
            print("Trying to delete pod with name", name)
            v1_services.delete(name=name, namespace=project)
        except exceptions.NotFoundError:
                print('Unknown error with {} pod deletion. Contact someone.'.format(name))

def create_ui_route(client, token, project):
    v1_routes = client.resources.get(api_version='v1', kind='Route')
    route = """
    kind: Route
    apiVersion: v1
    metadata:
        name: access-control
    spec:
        to:
            kind: Service
            name: access-control
        port:
            targetPort: tcp
    """
    route_data = yaml.load(route)
    resp = v1_routes.create(body=route_data, namespace=project)

def get_vault_status(client, project):
    res = exec_command("vault status", client, "vault-operator-0", project)
    print(res)
    if "Initialized     false" in str(res):
        raise Exception('Vault service was not initialized!')
    else:
        print("Vault was successfully INITIALIZED after deployment")
    if "Sealed          true" in str(res):
        raise Exception('Vault service was not unsealed!')
    else:
        print("Vault was successfully UNSEALED after deployment")


def get_tests_result(client, project, timeout):
    os.environ["TEST_VARIABLE_FOR_DUMMIES"] = "1"
    print(os.environ)
    tick_start = time.time(); tick_round = 15.0
    timeout = datetime.now() + timedelta(minutes=int(timeout))
    
    ret = client.list_namespaced_pod(namespace=project)
    for i in ret.items:
        if "test" in i.metadata.name:
            while True:
                print("[SCRIPT] Obtaining test execution status from pod every 15 seconds...")
                log = client.read_namespaced_pod_log(i.metadata.name, project)
                if "Output" in str(log):
                    m = re.findall(r'(.*) tests total, (.*) passed, (.*) failed', log)[-1]
                    if m != None and int(m[2]) > 0:
                        print(log)
                        sys.exit(1)
                    elif m != None and int(m[2]) == 0:
                        print(log)
                        sys.exit(0)

                if timeout < datetime.now():
                    print("[SCRIPT] Timeout exceeded for test checking, abort script.")
                    sys.exit(1)

                time.sleep(tick_round - ((time.time() - tick_start) % tick_round))
    
    print(f"[SCRIPT] No test pods found in project {project}, exiting.")
    sys.exit(1)