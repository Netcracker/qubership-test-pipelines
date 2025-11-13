check_cr_conditions() {
    local crd_name="$1"
    local namespace="$2"
    local all_success=true
    local any_in_progress=false

    cr_list=$(kubectl get "$crd_name" -n "$namespace" --no-headers -o custom-columns=":metadata.name" 2>/dev/null)

    for cr_name in $cr_list; do
        echo "Checking CR: $cr_name"

        if ! cr_json=$(kubectl get "$crd_name" "$cr_name" -n "$namespace" -o json 2>/dev/null); then
            echo "::error:: ❌ CR '$cr_name' not found or inaccessible"
            all_success=false
            continue
        fi

        if [ -z "$cr_json" ]; then
            echo "::error:: ❌ Empty response for CR '$cr_name'"
            all_success=false
            continue
        fi

        failed_conditions=$(echo "$conditions_json" | jq -r '.[] | select(.status == "False" or .reason == "Failed" or (.type | ascii_downcase | contains("failed"))) | .type' 2>/dev/null)
        in_progress_conditions=$(echo "$conditions_json" | jq -r '.[] | select(.status == "Unknown" or .reason == "Progressing" or (.type | ascii_downcase | contains("progress"))) | .type' 2>/dev/null)

        if [ -n "$failed_conditions" ]; then
            all_success=false
        elif [ -n "$in_progress_conditions" ]; then
            any_in_progress=true
        fi
    done

    if [ "$all_success" = false ]; then
        echo "Some CRs have failed conditions"
        echo "📄 JSON:"
        echo "$cr_json"
        return 2
    elif [ "$any_in_progress" = true ]; then
        echo "Some CRs are still in progress"
        echo "📄 JSON:"
        echo "$cr_json"
        return 1
    else
        echo "All CRs are healthy"
        return 0
    fi
}

check_cr_conditions "$@"
