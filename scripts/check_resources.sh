check_resources() {
    local namespace="$1"
    local all_ready=true

    deployments=$(kubectl get deployments -n "$namespace" -o jsonpath='{.items[*].metadata.name}')
    for deployment in $deployments; do
        ready=$(kubectl get deployment "$deployment" -n "$namespace" -o jsonpath="{.status.readyReplicas}" 2>/dev/null)
        total=$(kubectl get deployment "$deployment" -n "$namespace" -o jsonpath="{.status.replicas}" 2>/dev/null)
        ready=${ready:-0}
        total=${total:-0}

        if [[ "$ready" -eq "$total" ]] && [[ "$total" -gt 0 ]]; then
            echo "Deployment $deployment is ready"
        else
            echo "Deployment $deployment is not ready: $ready/$total"
            all_ready=false
        fi
    done

    statefulsets=$(kubectl get statefulsets -n "$namespace" -o jsonpath="{.items[*].metadata.name}")
    for statefulset in $statefulsets; do
        ready=$(kubectl get statefulset "$statefulset" -n "$namespace" -o jsonpath="{.status.readyReplicas}" 2>/dev/null)
        total=$(kubectl get statefulset "$statefulset" -n "$namespace" -o jsonpath="{.status.replicas}" 2>/dev/null)
        ready=${ready:-0}
        total=${total:-0}

        if [[ "$ready" -eq "$total" ]] && [[ "$total" -gt 0 ]]; then
            echo "StatefulSet $statefulset is ready"
        else
            echo "StatefulSet $statefulset is not ready: $ready/$total"
            all_ready=false
        fi
    done

    daemonsets=$(kubectl get daemonsets -n "$namespace" -o jsonpath="{.items[*].metadata.name}")
    for daemonset in $daemonsets; do
        ready=$(kubectl get daemonset "$daemonset" -n "$namespace" -o jsonpath="{.status.numberReady}" 2>/dev/null)
        desired=$(kubectl get daemonset "$daemonset" -n "$namespace" -o jsonpath="{.status.desiredNumberScheduled}" 2>/dev/null)
        ready=${ready:-0}
        desired=${desired:-0}

        if [[ "$ready" -eq "$desired" ]] && [[ "$desired" -gt 0 ]]; then
            echo "DaemonSet $daemonset is ready"
        else
            echo "DaemonSet $daemonset is not ready: $ready/$desired"
            all_ready=false
        fi
    done

    if [ "$all_ready" = true ]; then
        #All resources are ready
        return 0
    else
        #Some resources are not ready
        return 1
    fi
}

check_resources "$@"
