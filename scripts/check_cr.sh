check_cr_conditions() {
    local crd_name="$1"
    local namespace="$2"

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
        # ▶️ Fallback for operators which do not expose .status.conditions.
        # For example Altinity ClickHouseInstallation reports progress in
        # .status.status: '', 'InProgress', 'Completed', 'Aborted'.
        status_value=$(echo "$cr_json" | jq -r '.items[0].status.status // .items[0].status.state // empty' 2>/dev/null)
        status_value_lower=$(echo "$status_value" | tr '[:upper:]' '[:lower:]')

        echo "Conditions not found, .status.status is '${status_value}'"

        case "$status_value_lower" in
            completed|succeeded|ready|healthy)
                echo "✅ CR '$crd_name' is ready (.status.status='${status_value}')"
                return 0
                ;;
            failed|aborted|error)
                echo "::error:: ❌ CR '$crd_name' failed (.status.status='${status_value}')"
                echo "📄 CR JSON:"
                echo "$cr_json"
                return 2
                ;;
            *)
                echo "::warning:: Conditions not found"
                return 1
                ;;
        esac
    fi

    failed_conditions=$(echo "$conditions_json" | jq -r '.[] |
    select(
        (.type | ascii_downcase | contains("failed"))
    ) | .type' 2>/dev/null)

    in_progress_conditions=$(echo "$conditions_json" | jq -r '.[] |
    select(
        (.type | ascii_downcase | contains("progress"))
    ) | .type' 2>/dev/null)

    successful_conditions=$(echo "$conditions_json" | jq -r '.[] |
    select(
        (.type | ascii_downcase | contains("success"))
    ) | .type' 2>/dev/null)

    if [ -n "$failed_conditions" ]; then
        echo "📄 Conditions JSON:"
        echo "$conditions_json"
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
