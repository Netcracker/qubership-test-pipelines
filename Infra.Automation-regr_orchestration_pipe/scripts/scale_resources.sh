KUBECTL=/builds/PROD.Platform.HA/Infra.Automation/binary/kubectl

system_ns=("app-deployer,
cert-manager,
site-manager,
kube-csi-cinder,
kube-csi-nfs-external,
kube-monkey,
kube-node-lease,
kube-public,
kube-system,
kubereq,
kubernetes-dashboard,
local-path-storage,
ingress-nginx,
argocd,
minio,
resource-reporter")

IFS=',' read -a exeptions <<< "$(tr -d ' ''\n' <<< "$system_ns")"
IFS=',' read -a nc_not_be_cleaned <<< "$(tr -d ' ''\n' <<< "$1")"

for i in "${nc_not_be_cleaned[@]}"
do
  if ! [[ ${exeptions[@]} =~ $i ]]; then
    exeptions+=($i)
  fi
done

ns_names=$($KUBECTL get ns  --no-headers -o custom-columns=":metadata.name")

for i in $ns_names; do
  if ! [[ ${exeptions[@]} =~ $i ]]; then
    ns_list+=($i)
  fi
done

echo "EXCEPTED NAMESPACES (resources not be scaled): "${exeptions[@]}

echo "Scaling deployments and statefulsets ..."

for namespace in "${ns_list[@]}"; do
  echo "namespace: " "$namespace"
  $KUBECTL scale statefulset,deployment -n "$namespace" --all --replicas=0
done


