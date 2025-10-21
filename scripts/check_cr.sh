check_cr_conditions() {
    crd_list=("$1")
    namespace="$2"
    echo "Start checking CR"
    for crd_name in "${crd_list[@]}"; do
        if ! kubectl get crd "$crd_name" &>/dev/null; then
            echo "::error:: CRD "$crd_name" does not exist!"
            exit 1
        fi
        cr_list=$(kubectl get "$crd_name" -n "$namespace" --no-headers -o custom-columns=":metadata.name" 2>/dev/null)
        for cr_name in $cr_list; do
            cr_json=$(kubectl get "$crd_name" "$cr_name" -n "$namespace" -o json 2>/dev/null)
            if [ $? -eq 0 ] && [ -n "$cr_json" ]; then
                #echo "$cr_json"
                echo 'Conditions:'
                echo "$cr_json" | jq -r '.status.conditions'
                conditions_count=$(echo "$cr_json" | jq -r '.status.conditions | length')
                conditions_json=$(echo "$cr_json" | jq -r '.status.conditions')
                echo $conditions_json
                for ((i=0; i<${conditions_count}; i++)); do
                    type=$(echo "$conditions_json" | jq -r '.[${i}].type')
                    status=$(echo "$conditions_json" | jq -r '.[${i}].status')
                    echo "Type: $type"
                    echo "Status: $status"
                    type_lower=$(echo "$type" | tr '[:upper:]' '[:lower:]')
                    if [ "$type_lower" = "failed" ] || [ "$type_lower" = "in progress" ]; then
                        echo "Error: Found condition type: $type"
                        exit 1
                    else
                        echo "CR '$cr_name' has no failed conditions"
                    fi
                done
            else
                echo "Error: CR '$cr_name' not found"
                exit 1
            fi
        done
    done
    exit 0
}

check_cr_conditions "$@"

