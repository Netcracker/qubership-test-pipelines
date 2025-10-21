check_tests() {
    echo "run script"
    namespace="$1"
    file_name=artifacts/"$namespace"_tests.txt
    IFS=' ' read -ra pods <<< "$(kubectl get pods --no-headers -o custom-columns=":metadata.name" -n "$namespace" | tr $'\n' ' ')"
    test_pod=""
    for pod in "${pods[@]}"; do
      if [[ $pod == *"tests"* ]]; then
        test_pod=$pod
        break
      fi
    done
    if ! [[ $test_pod ]]; then
      echo "There is no test pod"
      exit
    fi
    echo "test_pod=$test_pod"

    status=$(kubectl get pod $test_pod -n "$namespace" -o jsonpath="{.status.phase}")
    echo "Pod status: $status"

    logs=$(kubectl logs $test_pod -n "$namespace")
    if [[ $logs =~ Report.*html ]]; then
      echo "$logs" > $file_name
      echo 'TEST LOGS:'
      echo "$logs"
      if [[ $logs == *"| FAIL |"* ]]; then
        echo "::error:: Tests failed!"
        exit
      fi

      if ! kubectl cp $test_pod:/opt/robot/output artifacts/robot-results -n "$namespace"; then
        echo "::warning:: Failed to copy robot results"
      fi
    else
       exit
    fi
}

check_tests "$@"
