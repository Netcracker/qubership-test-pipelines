#!/bin/bash

# Parameters
PIPELINE_ID=$1
MAX_ATTEMPTS=${2:-10}
TIMEOUT=${3:-10}
PRIVATE_TOKEN=$GIT_TOKEN
PROJECT=${4:-https://gl.qubership.org/api/v4/projects/20633}


check_pipeline_status() {
    local response
    response=$(curl -s -X GET --header "PRIVATE-TOKEN: $PRIVATE_TOKEN" "$PROJECT/pipelines/$PIPELINE_ID")
    echo "$response"
}

attempt=1

while [ $attempt -le $MAX_ATTEMPTS ]; do	
    echo "Attempt $attempt/$MAX_ATTEMPTS: Checking pipeline status..."
	echo "Ping: '$PROJECT/pipelines/$PIPELINE_ID'"
    response=$(check_pipeline_status)
    if [[ $? -ne 0 || -z "$response" ]]; then
        echo "Error: Failed to retrieve pipeline response."
    fi
    
    # status=$(echo "$response" | grep -o '"status":"[^"]*"' | sed 's/"status":"\(.*\)"/\1/')
    status=$(echo "$response" | grep -o '"text":"[^"]*"' | sed 's/"text":"\(.*\)"/\1/')
	label=$(echo "$response" | grep -o '"label":"[^"]*"' | sed 's/"label":"\(.*\)"/\1/')

    if [[ "$status" == "created" ]]; then
        echo "Pipeline $PIPELINE_ID is created. Waiting for the next check..."
    elif [[ "$status" == "running" ]]; then
        echo "Pipeline $PIPELINE_ID is still running. Waiting for the next check..."
    elif [[ "$status" == "pending" ]]; then
        echo "Pipeline $PIPELINE_ID is pending. Waiting for the next check..."
    elif [[ "$status" == "passed" ]]; then
        echo "Pipeline $PIPELINE_ID is $label."
        exit 0
    elif [[ "$status" == "failed" ]]; then
        echo "Pipeline $PIPELINE_ID is $label."
        exit 1
	elif [[ "$status" == "warning" ]]; then
        echo "Pipeline $PIPELINE_ID is $label."
        exit 2
    else
        echo "Unknown pipeline status: $status"
    fi

    attempt=$((attempt + 1))
    sleep $TIMEOUT
done

echo "Maximum attempts reached. Pipeline status did not reach 'success' or 'failed'."
exit 1