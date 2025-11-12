check_tests() {
    local namespace="$1"
    local file_name="artifacts/${namespace}_tests.txt"
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
      echo "::error:: ❌ There is no test pod"
      exit 2
    fi

    echo "Test pod found: $test_pod"

    status=$(kubectl get pod "$test_pod" -n "$namespace" -o jsonpath="{.status.phase}")
    echo "Pod status: $status"

    logs=$(kubectl logs "$test_pod" -n "$namespace")
    if [[ "$logs" =~ Report.*html ]]; then
      echo "$logs" > "$file_name"
      echo "📄 TEST LOGS:"
      echo "$logs"

      if ! kubectl cp "$test_pod":/opt/robot/output artifacts/robot-results -n "$namespace"; then
        echo "::warning:: ⚠️ Failed to copy robot results"
      else
        echo "✅ Robot results copied successfully"
      fi

      if [[ "$logs" == *"| FAIL |"* ]]; then
        #Tests failed
        exit 2
      else
        #Tests passed successfully
        exit 0
      fi
    else
       #Tests are still running
       exit 1
    fi
}

check_tests "$@"
