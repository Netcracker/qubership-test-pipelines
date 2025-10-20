check_resources() {
    echo 'Start checking resources'
    namespace="$1"
    deployments=$(kubectl get deployments -n "$namespace" -o jsonpath='{.items[*].metadata.name}')
    for deployment in $deployments; do
        ready=$(kubectl get deployment "$deployment" -n "$namespace" -o jsonpath='{.status.readyReplicas}' 2>/dev/null)
        total=$(kubectl get deployment "$deployment" -n "$namespace" -o jsonpath='{.status.replicas}' 2>/dev/null)
        if [[ "$ready" -eq "$total" ]] && [[ "$total" -gt 0 ]]; then
            echo "Deployment $deployment is ready"
        else
            echo "Deployment $deployment is not ready"
            return 1
        fi
    done

    statefulsets=$(kubectl get statefulsets -n "$namespace" -o jsonpath='{.items[*].metadata.name}')
    for statefulset in $statefulsets; do
        ready=$(kubectl get statefulset "$statefulset" -n "$namespace" -o jsonpath='{.status.readyReplicas}' 2>/dev/null)
        total=$(kubectl get statefulset "$statefulset" -n "$namespace" -o jsonpath='{.status.replicas}' 2>/dev/null)
        if [[ "$ready" -eq "$total" ]] && [[ "$total" -gt 0 ]]; then
            echo "StatefulSet $statefulset is ready"
        else
            echo "StatefulSet $statefulset is not ready"
            return 1
        fi
    done

    daemonsets=$(kubectl get daemonsets -n "$namespace" -o jsonpath='{.items[*].metadata.name}')
    for daemonset in $daemonsets; do
        ready=$(kubectl get daemonset "$daemonset" -n "$namespace" -o jsonpath='{.status.numberReady}' 2>/dev/null)
        desired=$(kubectl get daemonset "$daemonset" -n "$namespace" -o jsonpath='{.status.desiredNumberScheduled}' 2>/dev/null)
        if [[ "$ready" -eq "$desired" ]] && [[ "$desired" -gt 0 ]]; then
            echo "DaemonSet $daemonset is ready"
        else
            echo "DaemonSet $daemonset is not ready"
            return 1
        fi
    done

    return 0
}

check_resources "$@"
