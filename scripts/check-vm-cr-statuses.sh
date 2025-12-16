#!/usr/bin/env bash
set -euo pipefail

NAMESPACE=${1:-monitoring}
MAX_ATTEMPTS=${2:-10}
SLEEP_SEC=${3:-10}
EXPECTED_JSON=${4:-expected-cr-statuses.json}

echo "Namespace: $NAMESPACE"
echo "Max attempts: $MAX_ATTEMPTS, sleep: $SLEEP_SEC sec"
echo "Expected JSON: $EXPECTED_JSON"

# --- 1. Get install_map from PlatformMonitoring ---
install_map=$(kubectl get platformmonitorings.monitoring.qubership.org platformmonitoring \
  -n "$NAMESPACE" -o json | jq '{
  platformmonitoring: true,
  grafana:        (.spec.grafana.install // false),
  vmAgent:        (.spec.victoriametrics.vmAgent.install // false),
  vmAlert:        (.spec.victoriametrics.vmAlert.install // false),
  vmAlertManager: (.spec.victoriametrics.vmAlertManager.install // false),
  vmAuth:         (.spec.victoriametrics.vmAuth.install // false),
  vmSingle:       (.spec.victoriametrics.vmSingle.install // false),
  vmUser:         (.spec.victoriametrics.vmUser.install // false)
}')

# --- 2. Filter expected JSON by install_map ---
filtered_json=$(jq --argjson install "$install_map" '
  map(select(($install[.component] // false) == true))
' "$EXPECTED_JSON")

# --- 3. Status check loop ---
attempt=1
while [ $attempt -le "$MAX_ATTEMPTS" ]; do
  echo "Attempt $attempt/$MAX_ATTEMPTS..."

  all_ok=true

  for i in $(echo "$filtered_json" | jq -r 'to_entries|.[]|.key'); do
    cr=$(echo "$filtered_json" | jq ".[$i]")

    kind=$(echo "$cr" | jq -r '.kind')
    name=$(echo "$cr" | jq -r '.name')
    component=$(echo "$cr" | jq -r '.component')

    # Check type of check
    check_type=$(echo "$cr" | jq -r 'if has("check") then .check else "updateStatus" end')

    if [ "$check_type" = "conditionsMatch" ]; then
      expected_reason=$(echo "$cr" | jq -r '.expectedConditions.reason')
      expected_status=$(echo "$cr" | jq -r '.expectedConditions.status')

      # Получаем фактический статус по reason
      actual=$(kubectl get "$kind" "$name" -n "$NAMESPACE" -o json | jq -r '
        .status.conditions[]? | select(.reason=="'"$expected_reason"'") | .status
      ')

      if [ "$actual" != "$expected_status" ]; then
        echo "  $component: NOT OK (expected $expected_status/$expected_reason, got ${actual:-null})"
        all_ok=false
      else
        echo "  $component: OK"
      fi

    else
      # обычная проверка updateStatus
      json_path=$(echo "$cr" | jq -r '.jsonPath'_
