check_cr_conditions() {
    local crd_name="$1"
    local namespace="$2"

    local fail_on_failed="${3:-true}"
    local active_only="${4:-false}"

    # normalize the flag: it is passed as a JSON boolean to jq (--argjson)
    case "$active_only" in
        true|True|TRUE) active_only="true" ;;
        *) active_only="false" ;;
    esac

    if [ -z "$crd_name" ]; then
        echo "CRD name not specified"
        return 0
    fi

    echo "Checking CR: $crd_name"

    if ! cr_json=$(kubectl get "$crd_name" -n "$namespace" -o json 2>/dev/null); then
        echo "::error:: ❌ CR '$crd_name' not found"
        return 2
    fi

    conditions_json=$(echo "$cr_json" | jq '.items[0].status.conditions')

    if [ -z "$conditions_json" ] || [ "$conditions_json" = "null" ]; then
        echo "::warning:: Conditions not found"
        return 1
    fi

    if [ "$active_only" = "true" ]; then
        echo "Only active conditions (status: true) are taken into account"
    fi

    # 'failed' is always matched by type regardless of status to keep the existing
    # failure detection behaviour for every service.
    failed_conditions=$(echo "$conditions_json" | jq -r '.[] |
    select(
        (.type | ascii_downcase | contains("failed"))
    ) | .type' 2>/dev/null)

    # With active_only=true conditions left in the CR with status: false (historical or
    # not yet reached) are ignored. Some operators (e.g. Mistral) keep an inactive
    # 'In Progress' condition after the deployment has already succeeded.
    in_progress_conditions=$(echo "$conditions_json" | jq -r --argjson active_only "$active_only" '.[] |
    select(
        (.type | ascii_downcase | contains("progress"))
    ) |
    select(
        ($active_only | not) or ((.status | tostring | ascii_downcase) == "true")
    ) | .type' 2>/dev/null)

    successful_conditions=$(echo "$conditions_json" | jq -r --argjson active_only "$active_only" '.[] |
    select(
        (.type | ascii_downcase | contains("success"))
    ) |
    select(
        ($active_only | not) or ((.status | tostring | ascii_downcase) == "true")
    ) | .type' 2>/dev/null)

    if [ -n "$failed_conditions" ]; then
        echo "📄 Conditions JSON:"
        echo "$conditions_json"
        if [ "$fail_on_failed" = "false" ]; then
            echo "::warning:: ❌ CR '$crd_name' has failed conditions but fail_on_failed=false; treating as in-progress and continuing to poll"
            return 1
        fi
        return 2
    elif [ -n "$in_progress_conditions" ]; then
        return 1
    elif [ -n "$successful_conditions" ]; then
        echo "📄 Conditions JSON:"
        echo "$conditions_json"
        return 0
    else
        echo "::warning:: No matching conditions found, considering as in progress"
        return 1
    fi
}

check_cr_conditions "$@"
