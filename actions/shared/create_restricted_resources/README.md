# 🚀 Create Restricted Resources Action

GitHub Action to create RBAC resources and a client certificate for a restricted Helm
installation. Sets up a `restricted` user in kubeconfig and switches to a `restricted-context`
so that subsequent Helm commands run under that user's permissions.

---

## Features

- Optionally creates service-specific ClusterRoles and ClusterRoleBindings from files in
  `qubership-test-pipelines/restricted/<service_name>/` (skips with a warning if absent)
- Generates a 2048-bit RSA client key and certificate via the Kubernetes CSR API
- Creates a namespace-scoped `Role` and `RoleBinding` granting the `restricted` user full
  access within the target namespace
- Registers the `restricted` user credentials in the current kubeconfig
- Creates and activates a `restricted-context` pointing to `kind-kind` and the target namespace

---

## 📌 Inputs

| Name | Description | Required | Default |
|---|---|---|---|
| `service_name` | Helm release name. Also used as the subdirectory name under `qubership-test-pipelines/restricted/` when looking for service-specific ClusterRoles and ClusterRoleBindings. | Yes | - |
| `repository_name` | Service repository name. Accepted for call-site compatibility with `helm_deploy` but not used by any step in this action. | No | - |
| `path_to_chart` | Path to the Helm chart within the service repository. Accepted for call-site compatibility with `helm_deploy` but not used by any step in this action. | No | - |
| `namespace` | Kubernetes namespace for the installation. Used as the `metadata.namespace` in the `Role` and `RoleBinding` and as the default namespace in the kubeconfig context. | Yes | - |

---

## 📌 Outputs

This action produces no step outputs. Its side-effects are the RBAC objects created in the
cluster and the kubeconfig context switch to `restricted-context`.

---

## How it works

The action sets up a restricted user identity for a Helm install in four phases:

**Phase 1 — Service-specific cluster RBAC (optional):**
Looks for `qubership-test-pipelines/restricted/<service_name>/clusterRoles/` and
`clusterRoleBindings/` directories. If either is present, every file in it is applied with
`kubectl create`. If either directory is missing, a warning annotation is emitted and the
phase is skipped — the action does not fail.

**Phase 2 — Client certificate:**
Generates a 2048-bit RSA private key (`restricted.key`) and a CSR with subject
`CN=restricted/O=dev-team`. Any pre-existing `restricted-csr` CertificateSigningRequest
object is deleted first. A new CSR object (`kubernetes.io/kube-apiserver-client` signer,
`client auth` usage) is submitted, approved, and the signed certificate is retrieved as
`restricted.crt`.

**Phase 3 — Namespace Role and RoleBinding:**
Patches `qubership-test-pipelines/restricted/restricted-role.yml` and
`qubership-test-pipelines/restricted/restricted-rb.yml` in-place, setting
`metadata.namespace` to `inputs.namespace` using `scripts/update_yaml.py`. Then applies both
files. The Role grants `["*"]` verbs on `["*"]` resources within the namespace; the
RoleBinding binds the `restricted` User to that Role.

**Phase 4 — kubeconfig setup:**
Registers the `restricted` credentials (certificate + key) in kubeconfig, creates
`restricted-context` targeting the `kind-kind` cluster and the target namespace, and switches
the active context to `restricted-context`. All subsequent `kubectl` and `helm` calls in the
job run as the `restricted` user until the context is changed again.

---

## Additional Information

### Service-specific ClusterRole directory layout

Place service-specific cluster-scoped resources under:

```text
qubership-test-pipelines/
  restricted/
    <service_name>/
      clusterRoles/
        my-clusterrole.yaml
      clusterRoleBindings/
        my-clusterrolebinding.yaml
```

Both subdirectories are optional. If neither exists (no entry for the service at all),
both phases emit a warning and continue. Existing services with files:

- `consul` — 2 ClusterRoleBindings, 2 ClusterRoles
- `opensearch` — 2 ClusterRoleBindings, 3 ClusterRoles
- `rabbitmq` — 1 ClusterRoleBinding

### Role permissions

The `restricted-role.yml` template grants the following within the target namespace:

```yaml
rules:
- apiGroups: ["*"]
  resources: ["*"]
  verbs: ["*"]
```

This is full namespace admin access, not a narrowly scoped restricted role. The name
`restricted` refers to the authentication identity (certificate-based user), not to
limited permissions.

### update_yaml.py

`scripts/update_yaml.py` modifies YAML files on disk using a slash-delimited path
(`metadata/namespace`). It overwrites the file in-place and re-serialises it with PyYAML,
which may alter key ordering and comment stripping. The `restricted-role.yml` and
`restricted-rb.yml` files are modified every time this action runs.

### Context switch

After this action completes, the active kubeconfig context is `restricted-context`. The
caller (`helm_deploy`) must switch back to `kind-kind` after the Helm call. The `helm_deploy`
action does this with `kubectl config use-context kind-kind` when `restricted: true`.

---

## Usage

```yaml
name: Create Restricted Resources

on:
  workflow_dispatch:

jobs:
  restricted-install:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - name: Checkout pipeline repo
        uses: actions/checkout@v4
        with:
          path: qubership-test-pipelines

      - name: Create restricted resources
        uses: Netcracker/qubership-test-pipelines/actions/shared/create_restricted_resources@905b88900dc8c14291eaeff4eddcf4d4f734aee1 # v1.9.0
        with:
          service_name: consul
          repository_name: Netcracker/qubership-consul
          path_to_chart: charts/helm/consul-service
          namespace: consul
```

---

## Notes

- The CSR YAML submitted to Kubernetes contains the base64-encoded CSR (derived from
  `restricted.key`) and is printed to the log as part of `kubectl apply` output.
- The `restricted-role.yml` and `restricted-rb.yml` files are modified on disk. If the same
  runner reuses the workspace across jobs without a clean checkout, the namespace value from
  a previous run may persist.
- This action is designed for `kind` clusters. The kubeconfig context is hardcoded to
  `kind-kind` as the cluster name.
- Pin to a full 40-character commit SHA with the release tag as a trailing comment, e.g.
  `@905b88900dc8c14291eaeff4eddcf4d4f734aee1 # v1.9.0`. The SHA is the immutable pin; the
  comment shows which release it points to. Tags alone are mutable and can be moved —
  acceptable only when callers explicitly want auto-updates within a minor version. Never
  use `@main` or short SHAs.
