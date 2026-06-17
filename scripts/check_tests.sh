check_tests() {
    local namespace="$1"
    local IFS=" "
    local -a pods
    IFS=" " read -ra pods <<< "$(kubectl get pods --no-headers -o custom-columns=":metadata.name" -n "$namespace" | tr "\n" " ")"
    local test_pod=""

    for pod in "${pods[@]}"; do
      if [[ "$pod" == *"tests"* ]]; then
        test_pod="$pod"
        break
      fi
    done

    if ! [[ "$test_pod" ]]; then
      echo "::warning:: ℹ️ check_tests set to 'true', but there is no test pod"
      exit 0
    fi

    echo "Test pod found: $test_pod"

    status=$(kubectl get pod "$test_pod" -n "$namespace" -o jsonpath="{.status.phase}")
    echo "Pod status: $status"

    logs=$(kubectl logs "$test_pod" -n "$namespace")
    if [[ "$logs" =~ Report.*html ]]; then
      if [[ "$logs" == *"| FAIL |"* ]]; then
        echo "::error:: ❌ Tests failed"
        exit 2
      else
        echo "✅ Tests passed successfully"
        exit 0
      fi
    else
       #echo "⏳ Tests are still running"
       exit 1
    fi
}

check_tests "$@"
