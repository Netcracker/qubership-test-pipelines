KUBECTL=/builds/PROD.Platform.HA/Infra.Automation/binary/kubectl

set +e

$KUBECTL delete SecurityContextConstraints 'logging-fluentbit' 'logging-fluentd' 'logging-graylog' || true
$KUBECTL delete ClusterRole 'logging-fluentd-cluster-role' 'logging-fluentbit-aggregator-cluster-role' 'logging-fluentbit-cluster-role' 'logging-graylog-cluster-role' 'logging-service-operator' || true
$KUBECTL delete ClusterRoleBinding 'logging-fluentbit-aggregator-cluster-reader' 'logging-service-operator' 'fluentbit-cluster-reader' 'fluentd-cluster-reader' 'graylog-cluster-role' || true