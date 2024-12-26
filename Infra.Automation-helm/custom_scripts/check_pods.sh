#!/bin/bash

KUBECTL=/builds/PROD.Platform.HA/Infra.Automation/binary/kubectl

namespace="$1"
error_flag=0

pods_status=$($KUBECTL get pods -n "$namespace" --no-headers=true)

# Check if any pod's status is not "Running" or "Completed"
while read -r line; do
    pod_status=$(echo "$line" | awk '{print $3}')
    if [ "$pod_status" != "Running" ] && [ "$pod_status" != "Completed" ] && [ -n "$pod_status" ]; then
        echo "$line"
        error_flag=1
    fi
done <<< "$pods_status"

# If there is at least one pod not in "Running" or "Completed" state, exit with code 1
if [ $error_flag -eq 1 ]; then
    echo "---------- At least one pod is not in 'Running' state. ----------"
    exit 1
fi

echo "---------- All pods in '$namespace' namespace are either 'Running' or 'Completed'. ----------"