check_cr_conditions() {
    local crd_name="$1"
    local namespace="$2"
    local all_success=true
    local any_in_progress=false

    echo "Start checking CR"

    cr_list=$(kubectl get "$crd_name" -n "$namespace" --no-headers -o custom-columns=":metadata.name" 2>/dev/null)
    echo cr_list $cr_list
    for cr_name in $cr_list; do
        echo "Checking CR: $cr_name"

        if ! cr_json=$(kubectl get "$crd_name" "$cr_name" -n "$namespace" -o json 2>/dev/null); then
            echo "::error:: CR '$cr_name' not found or inaccessible"
            all_success=false
            continue
        fi

        echo "Json:"
        echo $cr_json

        if [ -z "$cr_json" ]; then
            echo "::error:: Empty response for CR '$cr_name'"
            all_success=false
            continue
        fi

        conditions_json=$(echo "$cr_json" | jq -r '.status.conditions // "[]"')
        echo "Conditions for $cr_name:"
        echo "$conditions_json"

        failed_conditions=$(echo "$conditions_json" | jq -r '.[] | select(.status == "False" or .reason == "Failed" or (.type | ascii_downcase | contains("failed"))) | .type' 2>/dev/null)
        in_progress_conditions=$(echo "$conditions_json" | jq -r '.[] | select(.status == "Unknown" or .reason == "Progressing" or (.type | ascii_downcase | contains("progress"))) | .type' 2>/dev/null)

        if [ -n "$failed_conditions" ]; then
            echo "Found failed conditions in $cr_name: $failed_conditions"
            all_success=false
        elif [ -n "$in_progress_conditions" ]; then
            echo "Found conditions in progress for $cr_name: $in_progress_conditions"
            any_in_progress=true
        else
            echo "CR '$cr_name' is healthy"
        fi
    done

    if [ "$all_success" = false ]; then
        return 2
    elif [ "$any_in_progress" = true ]; then
        return 1
    else
        return 0
    fi
}

check_cr_conditions "$@"

