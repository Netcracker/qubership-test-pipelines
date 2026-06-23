check_tests() {
    local namespace="$1"
    local pod_prefix="$2"
    local IFS=" "
    local -a pods
    IFS=" " read -ra pods <<< "$(kubectl get pods --no-headers -o custom-columns=":metadata.name" -n "$namespace" | tr "\n" " ")"
    local test_pod=""

    for pod in "${pods[@]}"; do
      if [[ "$pod" == *"$pod_prefix"* ]]; then
        test_pod="$pod"
        break
      fi
    done

    if ! [[ "$test_pod" ]]; then
      echo "::warning:: ℹ️ No test pod found in namespace $namespace"
      exit 0
    fi

    echo "Test pod found: $test_pod"

    status=$(kubectl get pod "$test_pod" -n "$namespace" -o jsonpath="{.status.phase}")
    echo "Pod status: $status"

    logs=$(kubectl logs "$test_pod" -n "$namespace")
    if [[ "$logs" =~ Report.*html ]]; then
      echo "📄 TEST LOGS:"
      echo "$logs"
      if [[ "$logs" == *"| FAIL |"* ]]; then
        exit 2
      else
        exit 0
      fi
    else
       exit 1
    fi
}

check_tests "$@"
