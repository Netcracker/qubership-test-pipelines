KUBECTL=/builds/qa-group/azure-pipeline/binary/kubectl

set +e

namespace="$1"

$KUBECTL delete clickhouseinstallations.clickhouse.altinity.com cluster --wait=false -n "$namespace" || true
$KUBECTL patch clickhouseinstallations.clickhouse.altinity.com cluster --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n "$namespace" || true
$KUBECTL delete ClickHouseInstallation cluster --wait=false -n "$namespace" || true
$KUBECTL patch ClickHouseInstallation cluster --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n "$namespace" || true
