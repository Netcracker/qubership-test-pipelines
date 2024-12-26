KUBECTL=/builds/PROD.Platform.HA/Infra.Automation/binary/kubectl
HELM=/builds/PROD.Platform.HA/Infra.Automation/binary/helm

set +e

$HELM uninstall configurations-streamer -n prometheus-operator || true
$HELM uninstall grafana-plugins-init -n prometheus-operator || true
$HELM uninstall graphite-remote-adapter -n prometheus-operator || true
$HELM uninstall monitoring-operator -n prometheus-operator || true
$HELM uninstall network-latency-exporter -n prometheus-operator || true
$HELM uninstall prometheus-adapter -n prometheus-operator || true
$HELM uninstall prometheus-adapter-operator -n prometheus-operator || true

sleep 10

$KUBECTL patch deployment victoriametrics-operator --type json -p '[{"op": "replace", "path": "/spec/replicas", "value": 0}]' -n prometheus-operator || true
$KUBECTL patch deployment victoriametrics-operator --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n prometheus-operator || true
$KUBECTL patch deployment vmsingle-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n prometheus-operator || true
$KUBECTL patch deployment vmalert-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n prometheus-operator || true
$KUBECTL patch deployment vmagent-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n prometheus-operator || true
$KUBECTL patch deployment vmauth-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n prometheus-operator || true
$KUBECTL patch statefulset vmalertmanager-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n prometheus-operator || true
$KUBECTL patch configmap relabelings-assets-vmagent-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n prometheus-operator || true
$KUBECTL patch configmap stream-aggr-vmagent-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n prometheus-operator || true
$KUBECTL patch serviceaccount vmagent-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n prometheus-operator || true
$KUBECTL patch serviceaccount vmsingle-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n prometheus-operator || true
$KUBECTL patch serviceaccount vmauth-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n prometheus-operator || true
$KUBECTL patch secret tls-assets-vmagent-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n prometheus-operator || true
$KUBECTL patch secret vmagent-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n prometheus-operator || true
$KUBECTL patch secret vmauth-config-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n prometheus-operator || true
$KUBECTL patch pvc vmsingle-vmsingle --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n prometheus-operator || true
$KUBECTL patch service vmsingle-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n prometheus-operator || true
$KUBECTL patch service vmagent-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n prometheus-operator || true
$KUBECTL patch configmap vm-vmalert-rulefiles-0 --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n prometheus-operator || true
$KUBECTL patch configmap vm-k8s-rulefiles-0 --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n prometheus-operator || true
$KUBECTL patch serviceaccount vmalertmanager-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n prometheus-operator || true
$KUBECTL patch serviceaccount vmalert-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n prometheus-operator || true
$KUBECTL patch secret tls-assets-vmalert-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n prometheus-operator || true
$KUBECTL patch secret vmalertmanager-k8s-config --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n prometheus-operator || true
$KUBECTL patch secret vmuser-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n prometheus-operator || true
$KUBECTL patch service vmalert-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n prometheus-operator || true
$KUBECTL patch service vmalertmanager-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n prometheus-operator || true
$KUBECTL patch service vmauth-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n prometheus-operator || true
$KUBECTL patch service vmauth-oauth2-proxy --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n prometheus-operator || true
$KUBECTL patch vmsingle k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n prometheus-operator || true
$KUBECTL patch vmagent k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n prometheus-operator || true
$KUBECTL patch vmalertmanager k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n prometheus-operator || true
$KUBECTL patch vmalert k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n prometheus-operator || true
$KUBECTL patch VMAuth k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n prometheus-operator || true
$KUBECTL patch PersistentVolumeClaim vmsingle-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n prometheus-operator || true
$KUBECTL patch role vmauth-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n prometheus-operator || true
$KUBECTL patch rolebinding vmauth-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n prometheus-operator || true
$KUBECTL patch VMUser k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n prometheus-operator || true
$KUBECTL patch vmusers k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n prometheus-operator || true
$KUBECTL delete apiservice/v1beta1.custom.metrics.k8s.io -n prometheus-operator || true


# --- vm-cluster ---#
#$KUBECTL patch statefulset vmstorage-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n prometheus-operator || true
#$KUBECTL patch statefulset vmselect-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n prometheus-operator || true
#$KUBECTL patch service vminsert-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n prometheus-operator || true
#$KUBECTL patch service vmselect-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n prometheus-operator || true
#$KUBECTL patch service vmstorage-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n prometheus-operator || true

$KUBECTL delete clusterrolebinding configurations-streamer prometheus-operator-grafana-operator prometheus-operator-kube-state-metrics-viewer prometheus-operator-kube-state-metrics prometheus-operator-node-exporter prometheus-operator-prometheus prometheus-operator-prometheus-operator prometheus-operator-prometheus-adapter-operator cert-exporter prometheus-operator-network-latency-exporter prometheus-operator-cert-exporter prometheus-adapter-custom-metrics monitoring-list-namespaces-deploy-user prometheus-operator-prometheus-adapter-operator monitoring-operator prometheus-operator-kube-state-metrics-viewer prometheus-operator-victoriametrics-operator prometheus-operator-version-exporter prometheus-operator-vmalert prometheus-operator-vmalertmanager prometheus-operator-vmauth prometheus-operator-vmagent prometheus-operator-vmsingle prometheus-operator-monitoring-operator prometheus-operator-prometheus-adapter-custom-metrics prometheus-operator-monitoring-tests -n prometheus-operator || true
$KUBECTL delete clusterrole configurations-streamer prometheus-operator-grafana-operator prometheus-operator-kube-state-metrics prometheus-operator-node-exporter prometheus-operator-prometheus prometheus-operator-prometheus-operator prometheus-operator-prometheus-adapter-operator monitoring-operator prometheus-operator-cert-exporter prometheus-operator-grafana-operator prometheus-operator-kube-state-metrics prometheus-operator-network-latency-exporter cert-exporter prometheus-adapter-custom-metrics monitoring-list-namespaces prometheus-operator-victoriametrics-operator prometheus-operator-vmagent prometheus-operator-vmsingle prometheus-operator-vmauth prometheus-operator-vmalertmanager prometheus-operator-vmalert prometheus-operator-version-exporter prometheus-operator-monitoring-operator prometheus-operator-prometheus-adapter-custom-metrics prometheus-operator-monitoring-tests prometheus-operator-configurations-streamer -n prometheus-operator || true

$KUBECTL delete SecurityContextConstraints prometheus-operator-cert-exporter prometheus-operator-node-exporter prometheus-operator-victoriametrics-operator victoriametrics-operator || true
