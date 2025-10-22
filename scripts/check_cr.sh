check_cr_conditions() {
    crd_name="$1"
    namespace="$2"
    echo "Start checking CR"
#    for crd_name in "${crd_list[@]}"; do
#        if ! kubectl get crd "$crd_name" &>/dev/null; then
#            echo "::error:: CRD "$crd_name" does not exist!"
#            return 2
#        fi
        cr_list=$(kubectl get "$crd_name" -n "$namespace" --no-headers -o custom-columns=":metadata.name" 2>/dev/null)
        for cr_name in $cr_list; do
            cr_json=$(kubectl get "$crd_name" "$cr_name" -n "$namespace" -o json 2>/dev/null)
            if [ $? -eq 0 ] && [ -n "$cr_json" ]; then
                echo 'Conditions:'
                echo "$cr_json" | jq -r '.status.conditions'
                conditions_json=$(echo "$cr_json" | jq -r '.status.conditions')
                echo $conditions_json
                failed_conditions=$(echo "$conditions_json" | jq -r '.[] | select(.type | ascii_downcase | ("failed") | contains(.)) | .type')
                in_progress_conditions=$(echo "$conditions_json" | jq -r '.[] | select(.type | ascii_downcase | ("in progress") | contains(.)) | .type')
                if [ -n "$failed_conditions" ]; then
                    echo "Found failed conditions"
                    return 1
                elif [ -n "$in_progress_conditions" ]; then
                    echo "Found conditions in progress"
                    return 1
                else
                    echo "CR '$cr_name' has no failed conditions"
                    return 0
                fi
            else
                echo "::error:: CR '$cr_name' not found"
                return 1
            fi
        done
#    done
#    exit 0
}

check_cr_conditions "$@"

