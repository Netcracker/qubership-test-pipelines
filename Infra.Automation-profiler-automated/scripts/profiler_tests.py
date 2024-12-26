from ExternalPlatformLib import ExternalPlatformLib
import argparse
import time
import requests

esc_collector_service = 'esc-collector-service'
esc_ui_service = 'esc-ui-service'
esc_test_service = 'esc-test-service'
esc_static_service = 'esc-static-service'

# Check readiness of profiler pods
def check_ready_deployments(client, namespace, service):
    try:
        deployments = client.get_deployment_entities_count_for_service(namespace, service, label='name')
        ready_deployments = client.get_active_deployment_entities_count_for_service(namespace, service, label='name')
        print(f'[Check status] [{service}] deployments: {deployments}, ready deployments: {ready_deployments}')
        if deployments == ready_deployments and deployments != 0:
            print(f'Component deployment [{service}] is ready!')
            return True
        else:
            return False
    except Exception as e:
        print(f'Something wrong during getting status for deployment: {service}')
        print(e)

def check_profiler_status(client, namespace):
    timeout_start = time.time()
    timeout = 300
    while time.time() < timeout_start + timeout:
        esc_collector_service_status = check_ready_deployments(client, namespace, esc_collector_service)
        esc_ui_service_status = check_ready_deployments(client, namespace, esc_ui_service)
        esc_test_service_status = check_ready_deployments(client, namespace, esc_test_service)
        esc_static_service_status = check_ready_deployments(client, namespace, esc_static_service)
        print('-----------------------------------------------------------------------------------------------------------')
        if esc_collector_service_status and esc_ui_service_status and esc_test_service_status and esc_static_service_status:
            print('All components are RUNNING!')
            return True
        time.sleep(10)
    print(f'Profiler deployments are not ready at least {timeout} seconds')
    return False

# Check PASSED of tests
def check_status_in_logs(client, test_pod_name, project, timeout):
    timeout_start = time.time()
    while time.time() < timeout_start + timeout:
        print(f"[SCRIPT] Obtaining tests execution status from pod: {test_pod_name} every 60 seconds...")
        logs = client.read_namespaced_pod_log(test_pod_name, project, 'esc-test-service')
        if "Test finished" in str(logs):
            print(f"'Test finished' found in pod: {test_pod_name} logs. PASSED")
            return True
        elif "Error in test orchestrator thread" in str(logs):
            return False
        time.sleep(60)
    return False

def get_tests_result(client, project, timeout=1500):
    pods = client.list_namespaced_pod(namespace=project)
    for pod in pods.items:
        if "esc-test" in pod.metadata.name:
            test_pod_name = pod.metadata.name
            print(f'Tests pod for check: {test_pod_name}')
    result = check_status_in_logs(client, test_pod_name, project, timeout=int(timeout))
    return result

# Run tests
def run_tests(url):
    resp = requests.post(f'{url}/launch', verify=False)
    if resp.status_code == 200:
        print('resp.status_code == 200, Tests is in running')
    else:
        print(f'Something went wrong with running tests, resp.status_code {resp.status_code}')
        exit(2)

def main(args_):
    client = ExternalPlatformLib(args_.token, args_.host)
    print('Start to RUN Profiler integration tests')
    print('-----------------------------------------------------------------------------------------------------------')
    profiler_status = check_profiler_status(client, args_.namespace)
    if profiler_status:
        run_tests(args_.url)
        result = get_tests_result(client=client, project=args_.namespace, timeout=args_.timeout)
        if result:
            print('[RESULT] Tests passed.')
            exit(0)
    print('-----------------------------------------------------------------------------------------------------------')
    print('Tests is not passed for 1 attempt. Deleting all pods and restart tests!')
    print('-----------------------------------------------------------------------------------------------------------')
    client.delete_collection_namespaced_pod(args_.namespace)
    time.sleep(30)
    profiler_status = check_profiler_status(client, args_.namespace)
    if profiler_status:
        run_tests(args_.url)
        result = get_tests_result(client=client, project=args_.namespace, timeout=args_.timeout)
        if result:
            print('[RESULT] Tests passed.')
            exit(0)
        elif not result:
            print(f'[RESULT] FAILED. There is no "Test finished" in logs for 2 attempts.')
            exit(1)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to execute Openshift commands')

    parser.add_argument('--url',
                        help='URL to test app')
    parser.add_argument('--token',
                        help='Token to the Cloud')
    parser.add_argument('--host',
                        help='URL to the Cloud')
    parser.add_argument('--namespace',
                        help='Namespace where Profiler is installed')
    parser.add_argument('--timeout',
                        help='Test parsing timeout (in seconds)',
                        default=1500)
    args = parser.parse_args()
    main(args)
