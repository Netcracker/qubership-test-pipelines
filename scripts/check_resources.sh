check_resources() {
    namespace="$1"
    deployments=$(kubectl get deployments -n "$namespace" -o jsonpath='{.items[*].metadata.name}')
    for deployment in $deployments; do
        echo "Deployment: $deployment"
        ready=$(kubectl get deployment "$deployment" -n "$namespace" -o jsonpath='{.status.readyReplicas}' 2>/dev/null)
        total=$(kubectl get deployment "$deployment" -n "$namespace" -o jsonpath='{.status.replicas}' 2>/dev/null)
        echo "${ready:-0}/${total:-0} replicas are ready"
        if [[ "$ready" -ne "$total" ]] && [[ "$total" -gt 0 ]]; then
            echo "Deployment $deployment is not ready"
            return 1
        fi
    done

    statefulsets=$(kubectl get statefulsets -n "$namespace" -o jsonpath='{.items[*].metadata.name}')
    for statefulset in $statefulsets; do
        echo "StatefulSet: $statefulset"
        ready=$(kubectl get statefulset "$statefulset" -n "$namespace" -o jsonpath='{.status.readyReplicas}' 2>/dev/null)
        total=$(kubectl get statefulset "$statefulset" -n "$namespace" -o jsonpath='{.status.replicas}' 2>/dev/null)
        echo "${ready:-0}/${total:-0} replicas are ready"
        if [[ "$ready" -ne "$total" ]] && [[ "$total" -gt 0 ]]; then
            echo "StatefulSet $statefulset is not ready"
            return 1
        fi
    done

    daemonsets=$(kubectl get daemonsets -n "$namespace" -o jsonpath='{.items[*].metadata.name}')
    for daemonset in $daemonsets; do
        echo "DaemonSet: $daemonset"
        ready=$(kubectl get daemonset "$daemonset" -n "$namespace" -o jsonpath='{.status.numberReady}' 2>/dev/null)
        desired=$(kubectl get daemonset "$daemonset" -n "$namespace" -o jsonpath='{.status.desiredNumberScheduled}' 2>/dev/null)
        echo "${ready:-0}/${desired:-0} replicas are ready"
        if [[ "$ready" -ne "$desired" ]] && [[ "$desired" -gt 0 ]]; then
            echo "DaemonSet $daemonset is not ready"
            return 1
        fi
    done

    return 0
}

check_resources "$@"
