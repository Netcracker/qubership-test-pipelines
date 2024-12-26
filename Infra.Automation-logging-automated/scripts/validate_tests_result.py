from ExternalPlatformLib import ExternalPlatformLib
import argparse
import time
import sys
import re

def get_tests_result(client, namespace, timeout):
    tests_pod = None
    pods = client.list_namespaced_pod(namespace=namespace)
    for pod in pods.items:
        if "tests" in pod.metadata.name or "integration-tests" in pod.metadata.name:
            tests_pod = pod.metadata.name
    if tests_pod:
        timeout_start = time.time()
        while time.time() < timeout_start + timeout:
            print("[SCRIPT] Obtaining test execution status from pod every 30 seconds...")
            logs = client.read_namespaced_pod_log(tests_pod, namespace, container=None)
            if "Output" in str(logs):
                result = re.findall(r'(.*) tests, (.*) passed, (.*) failed', logs)[-1]
                if result and int(result[2]) > 0:
                    print(f'\033[95mTests pod for checking logs: {tests_pod}, result:\033[0m')
                    print(f'\033[95mtotal tests: {result[0].split(" ")[-1]}, passed: {result[1]}, failed: {result[2]}\033[0m')
                    print('\033[1m-----------------------------------------------------------------------------------------------------------\033[0m')
                    print(f'FULL TESTS LOGS: {logs}')
                    print('\033[1m-----------------------------------------------------------------------------------------------------------\033[0m')
                    sys.exit(1)
                elif result and int(result[2]) == 0:
                    print(f'\033[95mTests pod for checking logs: {tests_pod}, result:\033[0m')
                    print(f'\033[95mtotal tests: {result[0].split(" ")[-1]}, passed: {result[1]}, failed: {result[2]}\033[0m')
                    sys.exit(0)
            time.sleep(30)
        print(f'\033[91mTests pods found, but there is no result for tests in timeout {timeout}...\033[0m')
    else:
        print(f"[SCRIPT] No test pods found in project {namespace}, exiting.")
        sys.exit(1)

def main(args_):
    client = ExternalPlatformLib(args_.cloud_token, args_.cloud_host)
    print('\033[1m-----------------------------------------------------------------------------------------------------------\033[0m')
    print('\033[95mSTART CHECKING TEST RESULTS\033[0m')
    print('-----------------------------------------------------------------------------------------------------------')
    get_tests_result(client, args_.namespace, int(args_.timeout))
    print('\033[1m-----------------------------------------------------------------------------------------------------------\033[0m')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to execute Openshift commands')
    parser.add_argument('--cloud-host',
                        help='Cloud host')
    parser.add_argument('--namespace',
                        help='Cloud namespace')
    parser.add_argument('--cloud-token',
                        help='Cloud token')
    parser.add_argument('--timeout',
                        help='Test parsing timeout (in seconds)')
    args = parser.parse_args()
    main(args)
