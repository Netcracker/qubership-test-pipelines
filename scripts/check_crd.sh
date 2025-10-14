check_crd_conditions() {
    local crd_list=("$@")
    echo 'Start checking CRD'
    for crd_name in "${crd_list[@]}"; do
        echo "Checking CRD: $crd_name"
        if ! kubectl get crd "$crd_name" &>/dev/null; then
            echo "CRD "$crd_name" does not exist!"
            return 1
        fi
        crd_json=$(kubectl get crd "$crd_name" -o json 2>/dev/null)
        echo "Conditions: "
        echo $(echo "$crd_json" | jq '.status.conditions')
        failed_conditions=$(echo "$crd_json" | jq '.status.conditions | map(select(.status == "Failed"))')
        failed_count=$(echo "$failed_conditions" | jq 'length')
        if [[ $failed_count -gt 0 ]]; then
            echo "CRD "$crd_name" has $failed_count failed conditions:"
            echo "$failed_conditions"
            return 1
        else
            echo "CRD "$crd_name" has no failed conditions"
        fi
    done
    return 0
}

check_crd_conditions "$@"

