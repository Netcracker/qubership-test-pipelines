import sys
sys.path.insert(0, '/scripts/external_platform_lib')
from ExternalPlatformLib import ExternalPlatformLib
import argparse
import re
import json
import requests
import urllib3


urllib3.disable_warnings()

def check_containers_status(pod):
    i = 0  # count not running containers
    state_not_running_containers = 'True'
    if pod.status.container_statuses is not None:
        for index in range(len(pod.status.container_statuses)):
            # print(f'POD_NAME: {pod.metadata.name}')
            try:
                if pod.status.phase == "Failed":
                    state_not_running_containers = pod.status.container_statuses[index].state.terminated.reason
                    i += 1
                elif not pod.status.container_statuses[index].ready and pod.status.container_statuses[index].state.waiting.reason is not None:
                    state_not_running_containers = pod.status.container_statuses[index].state.waiting.reason
                    i += 1
                elif not pod.status.container_statuses[index].ready and pod.status.container_statuses[index].last_state.terminated.reason is not None:
                    state_not_running_containers = pod.status.container_statuses[index].last_state.terminated.reason
                    i += 1
            except:
                state_not_running_containers = 'NotPossibleToGetStatus'
                i += 1
    else:
        print(f'\033[91mThere are no container_statuses in pod: {pod.metadata.name}\033[0m')
        return 0, 0, 'NotPossibleToGetStatus'
    return len(pod.status.container_statuses), i, state_not_running_containers

def check_pod_restarts(pod):
    restart_count = 0
    if pod.status.container_statuses != None:
        for index in range(len(pod.status.container_statuses)):
            if pod.status.container_statuses[index].restart_count > restart_count:
                restart_count = pod.status.container_statuses[index].restart_count
    else:
        print(f'\033[91mThere are no container_statuses in pod: {pod.metadata.name} not possible to check restarts count!\033[0m')
        return -1
    return restart_count

def check_pods_with_restarts(namespace, client):
    pods = client.list_namespaced_pod(namespace=namespace)
    pods_with_restarts = {}
    for pod in pods.items:
        restart_count = check_pod_restarts(pod)
        if restart_count:
            pods_with_restarts[pod.metadata.name] = restart_count
    return pods_with_restarts

def check_not_running_pods(namespace, client):
    pods = client.list_namespaced_pod(namespace=namespace)
    not_running_pods = {}
    for pod in pods.items:
        if pod.status.phase == "Succeeded":
            if pod.status.container_statuses[0].state.terminated.reason == 'Completed':
                continue
            else:
                containers_count, failed_containers_count, reason = 1, 0, 'Failed'
                state = (pod.status.phase, containers_count, failed_containers_count, reason)
                not_running_pods[pod.metadata.name] = state
        elif pod.status.phase != "Running" and pod.status.phase == "Pending":
            for condition in pod.status.conditions:
                reason = "NotReady"
                if condition.type == "Ready":
                    reason = condition.reason
                    break  
            state = (pod.status.phase, 1, 1, reason)
            not_running_pods[pod.metadata.name] = state
        elif pod.status.phase != "Running" and pod.status.phase != "Completed":
            containers_count, failed_containers_count, reason = check_containers_status(pod)
            state = (pod.status.phase, containers_count, failed_containers_count, reason)
            not_running_pods[pod.metadata.name] = state
        elif pod.status.phase == "Running":
            containers_count, failed_containers_count, reason = check_containers_status(pod)
            if failed_containers_count:
                state = (pod.status.phase, containers_count, failed_containers_count, reason)
                not_running_pods[pod.metadata.name] = state
    return not_running_pods

def check_containers_names_for_pod(pod):
    containers_names = []
    for pd in range(len(pod.spec.containers)):
        containers_names.append(pod.spec.containers[pd].name)
    return containers_names

def check_containers_names_for_all_pods_in_ns(namespace, client):
    pods = client.list_namespaced_pod(namespace=namespace)
    pods_containers = {}
    for pod in pods.items:
        containers_names = check_containers_names_for_pod(pod)
        pods_containers[pod.metadata.name] = containers_names
    with open('.env', 'w') as writer:
        writer.write(f'export PC="{pods_containers}"')
        writer.write(f'export COUNT="{len(pods_containers)}"')
    return pods_containers

def find_errors_in_logs(logs):
    count_duplicates = 0
    error_lines = []
    splited_lines = re.split(r'\n', logs)
    w_o_timestamp = []
    w_timestamp = []
    for m in splited_lines:
        if 'error' in m or 'ERROR' in m or 'FATAL' in m or 'Error' in m or 'fatal' in m:
            if not 'warning' in m and not 'errorOccured":false' in m and not 'Warning' in m and not 'warn' in m and not 'WARNING' in m and not 'WARN' in m and not 'INFO' in m and not 'info' in m and not 'errorOccured: false' in m and not 'errorOccured:false' in m:
                if len(m) > 80:
                    w_o_timestamp.append(m[80:])
                    w_timestamp.append(m)
                else:
                    w_o_timestamp.append(m)
                    w_timestamp.append(m)
    result = []
    if w_o_timestamp:
        index = []
        for i in w_o_timestamp:
            if i not in error_lines:
                error_lines.append(i)
                index.append(w_o_timestamp.index(i))
            else:
                count_duplicates += 1
        for x in index:
            result.append(w_timestamp[x])
    return len(w_o_timestamp), count_duplicates, result

def collect_pod_logs(namespace, client):
    pods_containers = check_containers_names_for_all_pods_in_ns(namespace, client)
    count_for_container = {}
    logs_by_container = {}
    for key, value in pods_containers.items():
        for container in value:
            try:
                logs = client.read_namespaced_pod_log(key, namespace, container=container)
                count, count_duplicates, error_lines = find_errors_in_logs(logs)
                count_for_container[f'{key}:{container}'] = count
                logs_by_container[f'{key}:{container}'] = error_lines
            except:
                count_for_container[f'{key}:{container}'] = 0
                logs_by_container[f'{key}:{container}'] = ['Not possible to read logs from pod']
    return count_for_container, logs_by_container

def show_logs_for_pod(pods_list, pod_count, cloud_host, cloud_token, namespace, logs_to_display=100):
    client = ExternalPlatformLib(cloud_token, cloud_host)
    pods_list = pods_list.replace('}export', '}')
    json_acceptable_string = pods_list.replace("'", "\"")
    d = json.loads(json_acceptable_string)
    key = list(d)[pod_count-1]
    value = list(d.values())[pod_count-1]
    for con in value:
        try:
            logs = client.read_namespaced_pod_log(key, namespace, container=con)
            count, count_duplicates, error_lines = find_errors_in_logs(logs)
            if count_duplicates > 0:
                print(f'\033[95m--- Count of duplicates logs with error: {count_duplicates}, it\'s not printed ---\033[0m')
            if error_lines:
                j = 0
                for line in error_lines:
                    if j > int(logs_to_display):
                        print(f'\033[95mPod has a large number of error logs.. displayed {logs_to_display}, another are skipped\033[0m')
                        break
                    else:
                        j += 1
                        print(line)
            else:
                print(f'\033[95m ----- There are no logs with error in pod: {key}, container: {con} ----- \033[0m')
        except:
            print(f'\033[91m ----- Not possible to read logs from pod: {key}, container: {con} ----- \033[0m')

def print_splitted_names(pods_list, pod_count):
    key, value = split_names(pods_list, pod_count)
    print(f'\033[1mPOD_NAME:\033[0m \033[96m{key}\033[0m, \033[1mCONTAINERS:\033[0m \033[96m{value}\033[0m')

def split_names(pods_list, pod_count):
    # print(f'----- {pods_list}')
    pods_list = pods_list.replace('}export', '}')
    json_acceptable_string = pods_list.replace("'", "\"")
    d = json.loads(json_acceptable_string)
    key = list(d)[pod_count-1]
    value = list(d.values())[pod_count-1]
    return key, value

def print_graylog_link(graylog_host, graylog_user, graylog_pass, namespace, pods_list, pod_count, cloud_host, cloud_token):
    graylog_state = check_graylog_availability(graylog_user=graylog_user,
                                               graylog_pass=graylog_pass,
                                               cloud_host=cloud_host,
                                               cloud_token=cloud_token,
                                               host=graylog_host)
    if graylog_state:
        key, value = split_names(pods_list, pod_count)
        for vl in value:
            link = make_link_to_logs_in_graylog(namespace, key, vl)
            print(f'\033[92mLink to find logs:\033[0m \033[4m{graylog_host}{link}\033[0m')

#_________________ Work with Graylog _______________________________

def check_graylog_availability(graylog_user, graylog_pass, cloud_host, cloud_token, host='http://***.***.***.***:80'):
    try:
        r = requests.get(host, auth=(graylog_user, graylog_pass), verify=False)
        if r.status_code == 200:
            nodes_worker = []
            client = ExternalPlatformLib(cloud_token, cloud_host)
            nodes = client.list_nodes()
            for node in nodes.items:
                if 'worker' in node.metadata.name:
                    nodes_worker.append(node.metadata.name)
                elif 'node' in node.metadata.name:
                    nodes_worker.append(node.metadata.name)
            if nodes_worker:
                if len(nodes_worker) == 3:
                    query = f'(host:"{nodes_worker[0]}" OR host:"{nodes_worker[1]}" OR host:"{nodes_worker[2]}")'
                elif len(nodes_worker) == 6:
                    query = f'host:"{nodes_worker[0]}" OR host:"{nodes_worker[1]}" OR host:"{nodes_worker[2]}" OR host:"{nodes_worker[3]}" OR host:"{nodes_worker[4]}" OR host:"{nodes_worker[5]}"'
                else:
                    query = f'(host:"{nodes_worker[0]}")'
                host = str(host) + f'/api/search/universal/relative?query={query}&range=3600&limit=5&sort=timestamp:desc&pretty=true'
            else:
                print(f'\033[91mNo worker nodes found\033[0m')
                return False
            resp = requests.get(host, auth=(graylog_user, graylog_pass), verify=False)
            data = json.loads(resp.text)
            if len(data['messages']) > 0:
                return True
            else:
                print(f'\033[91mThere are no any logs in Graylog: {host}\033[0m')
                return False
        else:
            print(f'\033[91m Seems like Graylog: {host} is not available, status code: {r.status_code}\033[0m')
            return False
    except:
        print(f'\033[91mGraylog: {host} is not available\033[0m')
        return False

def make_link_to_logs_in_graylog(namespace, pod_name, container_name):
    return f'/search?q=message%3A%2AError%2A+AND+namespace_name%3A%22{namespace}%22+AND+pod_name%3A%22{pod_name}%22+AND+container_name%3A%22{container_name}%22&rangetype=relative&from=1800'

def set_state(cloud_host, cloud_token, namespaces, restart_count = 2, errors_count = 100):
    client = ExternalPlatformLib(cloud_token, cloud_host)
    # ns_status[0] == notRunningPods, ns_status[1] == podsWithRestarts, ns_status[2] == podsWithBigAmountOfErrors
    overal_state = {}
    namespaces = namespaces.split(' ')
    for namespace in namespaces:
        ns_status = [False, False, False]
        not_running_pods = check_not_running_pods(namespace=namespace, client=client)
        if not_running_pods:
            print(f'\033[91mThere are pods in NS: {namespace} in not running state! WARNING\033[0m')
            ns_status[0] = True
            # exit(1)
        pods_with_restarts = check_pods_with_restarts(namespace=namespace, client=client)
        restarts = list(pods_with_restarts.values())
        is_restarts = False
        for restart in restarts:
            if restart > restart_count:
                is_restarts = True
                ns_status[1] = True
        if is_restarts:
            print(f'\033[91mThere are pods in NS: {namespace} with count of restarts > {restart_count}! WARNING\033[0m')
        count_for_container, logs_by_container = collect_pod_logs(namespace, client)
        errors = list(count_for_container.values())
        is_errors = False
        for error in errors:
            if error > errors_count:
                is_errors = True
                ns_status[2] = True
        if is_errors:
            print(f'\033[91mThere are pods in NS: {namespace} with big amount of errors > {errors_count}! WARNING\033[0m')
        overal_state[namespace] = ns_status
    print(f'INFO: for aggregate job: {overal_state}')
    for value in overal_state.values():
        if True in value:
            print(f'Found True in overal_state.values().. exit_code 1')
            exit(1)

#____________________________________________________________________
def main(args_):
    client = ExternalPlatformLib(args_.cloud_token, args_.cloud_host)
    print(f'\033[92mStart to check namespace: {args_.namespace}\033[0m')

    not_running_pods = check_not_running_pods(namespace=args_.namespace, client=client)
    pods_with_restarts = check_pods_with_restarts(namespace=args_.namespace, client=client)
    print('\n')
    # Print table with not running pods
    print("|--- \033[93mPods in Not Running State\033[0m ----------------------------------------------------------------------------------------|")
    print('| NAMESPACE: {:<105} |'.format(args_.namespace))
    print("|----------------------------------------------------------------------------------------------------------------------|")
    print("| {:<55} | {:<20} | {:<10} | {:<22} |".format('POD NAME', 'STATUS', 'CONTAINERS', 'REASON'))
    print("|---------------------------------------------------------+----------------------+------------+------------------------|")
    for key, value in not_running_pods.items():
        phase, total_containers, failed_containers, status = value
        cs = total_containers - failed_containers
        containers = f'{cs}/{total_containers}'
        print("| {:<55} | {:<20} | {:<10} | {:<22} |".format(key, phase, containers, status))
        print("|---------------------------------------------------------+----------------------+------------+------------------------|")

    print('\n')
    # Print table with count for restarts
    print("|--- \033[93mPods that have been restarted\033[0m -----------------------------------------|")
    print('| NAMESPACE: {:<62} |'.format(args_.namespace))
    print("|---------------------------------------------------------------------------|")
    print("| {:<50} | {:<20} |".format('POD NAME', 'RESTARTS COUNT'))
    print("|----------------------------------------------------+----------------------|")
    for key, value in pods_with_restarts.items():
        restarts_count = value
        print("| {:<50} | {:<20} |".format(key, restarts_count))
        print("|----------------------------------------------------+----------------------|")

    count_for_container, logs_by_container = collect_pod_logs(args_.namespace, client)
    print('\n')
    print("|--- \033[93mNumber of errors per pod\033[0m --------------------------------------------------------------------------------------------------------|")
    print('| NAMESPACE: {:<118} |'.format(args_.namespace))
    print("|-----------------------------------------------------------------------------------------------------------------------------------|")
    print("| {:<106} | {:<20} |".format('<POD_NAME>:<CONTAINER_NAME>', 'COUNT_ERRORS'))
    print("|------------------------------------------------------------------------------------------------------------+----------------------|")
    for key, value in count_for_container.items():
        print("| {:<106} | {:<20} |".format(key, value))
        print("|------------------------------------------------------------------------------------------------------------+----------------------|")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script for post-deploy validation')
    parser.add_argument('--cloud-host',
                        help='Cloud host')
    parser.add_argument('--cloud-token',
                        help='Cloud token')
    parser.add_argument('--namespace',
                        help='Namespace for work')
    args = parser.parse_args()
    main(args)
