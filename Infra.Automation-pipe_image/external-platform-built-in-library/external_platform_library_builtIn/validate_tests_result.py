from ExternalPlatformLib import ExternalPlatformLib
import argparse
import time
import sys
import re

def find_test_pods(client, namespace, attempts_for_wait_pod, retry_timeout):
    tests_pod = []
    for attempt in range(attempts_for_wait_pod):
        pods = client.list_namespaced_pod(namespace=namespace)
        print(f'Attempt: {attempt} for found test pods')
        for pod in pods.items:
            if ("tests" in pod.metadata.name or "integration-tests" in pod.metadata.name) and not "provisioner" in pod.metadata.name:
                tests_pod.append(pod.metadata.name)
        if tests_pod:
            return tests_pod
        time.sleep(retry_timeout*2)
        print(f'Trying to find a tests pod, attempt: {attempt+1} from {attempts_for_wait_pod}...')
    return None

def find_and_print_result(tests_pod, logs):
    try:
        result = re.findall(r'(.*) tests, (.*) passed, (.*) failed', logs)[-1]
    except:
        print("It's unusual case with test logs... Checkhing `test` instead of `tests`")
        result = re.findall(r'(.*) test, (.*) passed, (.*) failed', logs)[-1]
    if result and int(result[2]) > 0:
        print(f'\033[95mTests pod for checking logs: {tests_pod}, result:\033[0m')
        print(f'\033[95mtotal tests: {result[0].split(" ")[-1]}, passed: {result[1]}, failed: {result[2]}\033[0m')
        print('\033[1m-----------------------------------------------------------------------------------------------------------\033[0m')
        print(f'FULL TESTS LOGS: {logs}')
        print('\033[1m-----------------------------------------------------------------------------------------------------------\033[0m')
        return 1
    elif result and int(result[2]) == 0:
        print(f'\033[95mTests pod for checking logs: {tests_pod}, result:\033[0m')
        print(f'\033[95mtotal tests: {result[0].split(" ")[-1]}, passed: {result[1]}, failed: {result[2]}\033[0m')
        return 0

def get_tests_result(client, namespace, timeout, attempts_for_wait_pod, retry_timeout):
    status_codes = []
    tests_pod = find_test_pods(client, namespace, attempts_for_wait_pod, retry_timeout)
    if tests_pod:
        print(f'Found test pods: {tests_pod}')
        for pod in tests_pod:
            print(f'START checking for pod: {pod}')
            timeout_start = time.time()
            while time.time() < timeout_start + timeout:
                print(f"[SCRIPT] Obtaining test execution status from pod every {retry_timeout} seconds...")
                try:
                    logs = client.read_namespaced_pod_log(pod, namespace, container=None)
                except:
                    logs = None
                    print(f'Something wrong during getting pod logs: {pod}')
                if logs is not None and "Output" in str(logs):
                    resp = find_and_print_result(pod, logs)
                    status_codes.append(int(resp))
                    break
                time.sleep(retry_timeout)
        if 1 in status_codes:
            sys.exit(1)
        elif not status_codes or len(status_codes) != len(tests_pod):
            print(f'\033[91mTests pods found, but there is no result for tests in timeout {timeout}...\033[0m')
            if logs is not None:
              print(f'FULL TESTS LOGS: {logs}')
              print('\033[1m-----------------------------------------------------------------------------------------------------------\033[0m')
            sys.exit(1)
    else:
        print(f"[SCRIPT] No test pods found in project {namespace}, exiting.")
        sys.exit(1)

def main(args_):
    if args_.cloud_token and args_.cloud_host:
        client = ExternalPlatformLib(token=args_.cloud_token, host=args_.cloud_host)
    elif args_.kubeconfig:
        client = ExternalPlatformLib(kubeconfig=args_.kubeconfig)
    print('\033[1m-----------------------------------------------------------------------------------------------------------\033[0m')
    print('\033[95mSTART CHECKING TEST RESULTS\033[0m')
    print('-----------------------------------------------------------------------------------------------------------')
    get_tests_result(client, args_.namespace, int(args_.timeout), int(args_.attempts_for_wait_pod), int(args_.retry_timeout))
    print('\033[1m-----------------------------------------------------------------------------------------------------------\033[0m')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to execute Openshift commands')
    parser.add_argument('--cloud-host',
                        help='Cloud host',
                        default=None)
    parser.add_argument('--cloud-token',
                        help='Cloud token',
                        default=None)
    parser.add_argument('--kubeconfig',
                        help='Kubeconfig file',
                        default=None)
    parser.add_argument('--namespace',
                        help='Cloud namespace')
    parser.add_argument('--timeout',
                        help='Test parsing timeout (in seconds)')
    parser.add_argument('--attempts-for-wait-pod',
                        help='Amount of attempts to wait creating integration tests pod',
                        default=1)
    parser.add_argument('--retry-timeout',
                        help='Timeout between attempts to obtain result of tests',
                        default=30)
    args = parser.parse_args()
    main(args)
