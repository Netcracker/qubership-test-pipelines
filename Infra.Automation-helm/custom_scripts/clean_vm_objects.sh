KUBECTL=/builds/PROD.Platform.HA/Infra.Automation/binary/kubectl

set +e

namespace="$1"

$KUBECTL patch deployment victoriametrics-operator --type json -p '[{"op": "replace", "path": "/spec/replicas", "value": 0}]' -n "$namespace" || true
$KUBECTL patch deployment victoriametrics-operator --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n "$namespace" || true
$KUBECTL patch deployment vmsingle-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n "$namespace" || true
$KUBECTL patch deployment vmalert-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n "$namespace" || true
$KUBECTL patch deployment vmagent-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n "$namespace" || true
$KUBECTL patch deployment vmauth-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n "$namespace" || true
$KUBECTL patch statefulset vmalertmanager-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n "$namespace" || true
$KUBECTL patch configmap relabelings-assets-vmagent-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n "$namespace" || true
$KUBECTL patch configmap stream-aggr-vmagent-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n "$namespace" || true
$KUBECTL patch serviceaccount vmagent-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n "$namespace" || true
$KUBECTL patch serviceaccount vmsingle-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n "$namespace" || true
$KUBECTL patch serviceaccount vmauth-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n "$namespace" || true
$KUBECTL patch secret tls-assets-vmagent-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n "$namespace" || true
$KUBECTL patch secret vmagent-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n "$namespace" || true
$KUBECTL patch secret vmauth-config-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n "$namespace" || true
$KUBECTL patch pvc vmsingle-vmsingle --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n "$namespace" || true
$KUBECTL patch service vmsingle-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n "$namespace" || true
$KUBECTL patch service vmagent-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n "$namespace" || true
$KUBECTL patch configmap vm-vmalert-rulefiles-0 --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n "$namespace" || true
$KUBECTL patch configmap vm-k8s-rulefiles-0 --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n "$namespace" || true
$KUBECTL patch serviceaccount vmalertmanager-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n "$namespace" || true
$KUBECTL patch serviceaccount vmalert-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n "$namespace" || true
$KUBECTL patch secret tls-assets-vmalert-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n "$namespace" || true
$KUBECTL patch secret vmalertmanager-k8s-config --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n "$namespace" || true
$KUBECTL patch secret vmuser-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n "$namespace" || true
$KUBECTL patch service vmalert-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n "$namespace" || true
$KUBECTL patch service vmalertmanager-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n "$namespace" || true
$KUBECTL patch service vmauth-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n "$namespace" || true
$KUBECTL patch service vmauth-oauth2-proxy --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n "$namespace" || true
$KUBECTL patch vmsingle k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n "$namespace" || true
$KUBECTL patch vmagent k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n "$namespace" || true
$KUBECTL patch vmalertmanager k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n "$namespace" || true
$KUBECTL patch vmalert k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n "$namespace" || true
$KUBECTL patch VMAuth k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n "$namespace" || true
$KUBECTL patch PersistentVolumeClaim vmsingle-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n "$namespace" || true
$KUBECTL patch role vmauth-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n "$namespace" || true
$KUBECTL patch rolebinding vmauth-k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n "$namespace" || true
$KUBECTL patch VMUser k8s --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n "$namespace" || true
$KUBECTL delete apiservices v1beta1.custom.metrics.k8s.io || true

