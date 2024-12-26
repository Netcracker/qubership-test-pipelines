#!/bin/bash

KUBECTL=/builds/PROD.Platform.HA/Infra.Automation/binary/kubectl
error_flag=0

clusterIssuers=$($KUBECTL get clusterIssuer --no-headers=true)

while read -r line; do
    issuerState=$(echo "$line" | awk '{print $2}')
    if [ "$issuerState" != "True" ] && [ -n "$issuerState" ]; then
        echo "$line"
        error_flag=1
    fi
done <<< "$clusterIssuers"

# If there is at least one pod not in "Running" or "Completed" state, exit with code 1
if [ $error_flag -eq 1 ]; then
    echo "---------- At least one clusterIssuer is not READY. ----------"
    exit 1
fi

echo "---------- All clusterIssuers are in READY state. ----------"