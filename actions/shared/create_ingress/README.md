# 🚀 Create Ingress-Controller

GitHub Action that installs ingress-nginx into a `kind` cluster and configures CoreDNS
with a wildcard `*.testdomain.local` DNS zone pointing to the ingress controller's ClusterIP.

---

## Features

- Deploys the official `ingress-nginx` controller for `kind` clusters
- Patches the `nginx` IngressClass to be the cluster-wide default
- Configures CoreDNS to resolve all `*.testdomain.local` hostnames to the nginx ClusterIP,
  enabling in-cluster DNS-based routing without external DNS
- Restarts CoreDNS pods and waits up to 180 seconds for them to become ready
- Prints pod and event status for the `ingress-nginx` namespace after setup

---

## 📌 Inputs

This action has no inputs.

---

## 📌 Outputs

This action produces no outputs.

---

## How it works

The action performs four cluster-level changes, all of which are permanent for the lifetime
of the `kind` cluster:

1. **Install ingress-nginx**: applies the official `kind` ingress manifest from
   `https://kind.sigs.k8s.io/examples/ingress/deploy-ingress-nginx.yaml` and patches the
   `nginx` IngressClass to be the default class. Any Ingress resource without an explicit
   `ingressClassName` will be handled by this controller.
2. **Configure wildcard DNS**: reads the ClusterIP of the `ingress-nginx-controller` service
   in the `ingress-nginx` namespace, then replaces the `kube-system/coredns` ConfigMap with
   an updated Corefile. The new Corefile adds a `testdomain.local:53` zone that answers any
   query matching `*.testdomain.local` with the nginx ClusterIP:

   ```text
   testdomain.local:53 {
       template ANY ANY  {
           match .*\.testdomain\.local\.$
           answer "{{ .Name }} 60 IN A <nginx-clusterip>"
           fallthrough
       }
   }
   ```

3. **Restart CoreDNS**: deletes all pods with label `k8s-app=kube-dns` in `kube-system` to
   force a reload of the new ConfigMap. Kubernetes recreates them automatically.
4. **Wait for readiness**: runs `kubectl wait --for=condition=Ready` on the new CoreDNS pods
   with a 180-second timeout. The action fails if pods do not become ready in time.

After setup, any workload in the cluster can reach the ingress controller by pointing an
Ingress resource to a `*.testdomain.local` hostname — no external DNS configuration is needed.

---

## Additional Information

### testdomain.local DNS zone

The wildcard zone is cluster-internal only. `*.testdomain.local` hostnames resolve to the
nginx ClusterIP, which is not routable outside the cluster. This is designed for in-cluster
test scenarios where services communicate via Ingress resources using fixed hostnames.

The CoreDNS ConfigMap is replaced (not patched) using `kubectl replace`. The full Corefile,
including the original `cluster.local` zone configuration, is embedded in the action and
printed to the workflow log during the replace step.

### kind cluster requirement

The ingress manifest is sourced directly from `https://kind.sigs.k8s.io/examples/ingress/deploy-ingress-nginx.yaml`.
This action is designed exclusively for `kind` clusters and will not work correctly on other
cluster types without modification.

### No waiting for ingress-nginx readiness

The action does not wait for the `ingress-nginx-controller` deployment to become ready before
reading its ClusterIP. The ClusterIP is assigned at Service creation time and is available
immediately after `kubectl apply`, but the controller pods themselves may still be starting.
If subsequent steps depend on the controller being fully functional, add a `kubectl wait`
step after this action.

---

## Usage

```yaml
name: Setup Kind Ingress

on:
  workflow_dispatch:

jobs:
  setup:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - name: Checkout pipeline repo
        uses: actions/checkout@v4
        with:
          path: qubership-test-pipelines

      - name: Create ingress controller
        uses: Netcracker/qubership-test-pipelines/actions/shared/create_ingress@905b88900dc8c14291eaeff4eddcf4d4f734aee1 # v1.9.0
```

---

## Notes

- This action modifies the `kube-system/coredns` ConfigMap using `kubectl replace` — it
  overwrites any previous custom CoreDNS configuration. Run it before any step that adds
  additional CoreDNS rules.
- The full Corefile content (including the nginx ClusterIP) is printed to the workflow log
  during the CoreDNS patch step.
- Designed for `kind` clusters only. The ingress manifest URL is pinned to the official
  `kind.sigs.k8s.io` example and may not suit production or other cluster types.
- If CoreDNS pods do not reach `Ready` within 180 seconds, the action fails and subsequent
  steps will not run. Check `kubectl get pods -n kube-system` and `kubectl describe` output
  in the workflow log for the root cause.
- Pin to a full 40-character commit SHA with the release tag as a trailing comment, e.g.
  `@905b88900dc8c14291eaeff4eddcf4d4f734aee1 # v1.9.0`. The SHA is the immutable pin; the
  comment shows which release it points to. Tags alone are mutable and can be moved —
  acceptable only when callers explicitly want auto-updates within a minor version. Never
  use `@main` or short SHAs.
