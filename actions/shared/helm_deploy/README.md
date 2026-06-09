# 🚀 Helm Deploy Action

GitHub Action to install or upgrade Kubernetes services using Helm.

---

## Features

- Checks out the target service repository at the specified branch or commit
- Creates the target namespace when deploying in `install` mode
- Applies pre-installation Kubernetes resources from a configurable folder
- Creates or replaces CRDs found in the chart's `crds/` directory
- Sets up restricted RBAC resources (ServiceAccount, ClusterRoleBinding) when running in restricted mode
- Patches `values.yaml` to override a specific Docker image tag (`image_replacement`)
- Updates the `tags` field in the values template for test filtering (`test_tags`)
- Runs `charts-values-update-action` to propagate the service branch or commit tag into chart values
  (skipped when `service_branch` is a release version)
- Installs or upgrades the Helm release with a configurable values template
- Logs all running pod images after deploy
- Restores the default kubeconfig context after restricted-mode deploys

---

## 📌 Inputs

| Name | Description | Required | Default |
| --- | --- | --- | --- |
| `deploy_mode` | Deployment mode: `install` for a clean installation, `upgrade` to upgrade an existing release. | Yes | `install` |
| `restricted` | When `true`, installs using a user with restricted rights and passes `--skip-crds` to Helm. When `false`, installs as cluster admin. | Yes | `false` |
| `path_to_template` | Path to the values template file inside the `qubership-test-pipelines` repository. Example: `templates/consul-service/consul_clean_infra_passport.yml` | Yes | - |
| `service_branch` | Branch, tag, or commit SHA in the service repository to check out. A value matching `vX.Y.Z` is treated as a release and skips chart-values update. | Yes | - |
| `service_name` | Helm release name used in `helm install`/`upgrade`. | Yes | - |
| `repository_name` | Full `org/repo` name of the service repository. Example: `Netcracker/qubership-consul` | Yes | - |
| `path_to_chart` | Path to the Helm chart directory within the service repository. Example: `charts/helm/consul-service` | Yes | - |
| `namespace` | Kubernetes namespace for the installation. Created automatically in `install` mode. | Yes | - |
| `resource_folder` | Path (relative to repo root) to a folder of Kubernetes manifests applied with `kubectl create` before installation. Pass an empty string to skip. | Yes | - |
| `image_replacement` | Full image name including tag to pin in `values.yaml`, e.g. `pgskipper-docker-patroni-18`. The base name (everything before the last `-`) is used to locate the existing value. Skipped when empty. | No | `""` |
| `test_tags` | Replacement value for the `tags:` field in the values template. Skipped when empty. | Yes | `""` |

---

## 📌 Outputs

This action produces no outputs.

---

## How it works

1. The service repository is checked out into a subdirectory named after `repository_name`.
2. In `install` mode the target namespace is created if it does not already exist.
3. If `resource_folder` is non-empty, every file in that folder is applied with `kubectl create`.
4. The chart's `crds/` directory is walked and each CRD is created or replaced via `kubectl`.
5. When `restricted: true` and `deploy_mode: install`, the
   `actions/shared/create_restricted_resources` local action runs to set up RBAC objects.
6. The values template is copied from `qubership-test-pipelines` into the chart directory.
7. `service_branch` is classified as a release (`vX.Y.Z`) or non-release. For non-release branches
   and commits, `charts-values-update-action` rewrites image tags in chart values to match the
   branch name or a normalised commit hash (`git-<7chars>`). For release branches this step is
   skipped entirely.
8. If `image_replacement` is set, the matching image tag in `values.yaml` is replaced with the
   provided value using `sed`.
9. If `test_tags` is set, the `tags:` line in the copied template file is replaced.
10. `helm install` or `helm upgrade` runs against the chart directory, using the copied template as
    `-f <template>`. Restricted mode adds `--skip-crds`. Timeout is always 10 minutes.
11. Pod images in the namespace are printed with `kubectl get pods`.
12. When `restricted: true`, the kubeconfig context is restored to `kind-kind` after the deploy.
13. `kubectl get all -n <namespace>` runs unconditionally (`if: always()`) to show post-deploy state.

---

## Additional Information

### `service_branch` normalisation

Before passing the branch or commit to `charts-values-update-action`, slashes are replaced with
underscores. Commit SHAs (7–40 hex characters) are normalised to `git-<first7chars>`, e.g.
`git-a1b2c3d`.

### `restricted` mode

When `restricted: true`:

- The `create_restricted_resources` sub-action runs (install mode only), creating a dedicated
  ServiceAccount and ClusterRoleBinding for the chart.
- Helm is called with `--skip-crds` — CRDs are still managed separately in step 4 above.
- After the Helm call, `kubectl config use-context kind-kind` restores the default context so
  subsequent steps are not affected.

### `image_replacement` matching

The input must be the full image name including the version suffix, e.g.
`pgskipper-docker-patroni-18`. The action strips the last `-<segment>` to derive the search
pattern (`pgskipper-docker-patroni-`) and replaces the first occurrence in `values.yaml`. If the
pattern is not found, the step fails with an error.

### `resource_folder`

The folder path is resolved relative to the `qubership-test-pipelines` checkout root. All files
found recursively are applied with `kubectl create`. The input is required in the action signature;
pass an empty string (`""`) to skip resource creation.

### CRD management

CRDs are always processed regardless of `deploy_mode`. The `crds/` directory must exist inside the
chart path — its absence causes an error. Each CRD is applied with `kubectl replace` if it already
exists, or `kubectl create` otherwise.

---

## Usage

```yaml
name: Deploy Service with Helm

on:
  workflow_dispatch:

jobs:
  helm-deploy:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - name: Checkout pipeline repo
        uses: actions/checkout@v4
        with:
          path: qubership-test-pipelines

      - name: Run helm deploy
        uses: Netcracker/qubership-test-pipelines/actions/shared/helm_deploy@905b88900dc8c14291eaeff4eddcf4d4f734aee1 # v1.9.0
        with:
          deploy_mode: install
          restricted: false
          path_to_template: templates/consul-service/consul_clean_infra_passport.yml
          service_branch: main
          service_name: consul
          repository_name: Netcracker/qubership-consul
          path_to_chart: charts/helm/consul-service
          namespace: consul
          resource_folder: ""
          test_tags: ""
```

---

## Notes

- `deploy_mode` accepts `install` or `upgrade` — not `update`.
- The chart's `crds/` directory **must** exist; a missing directory causes an immediate failure.
- `repository_name` must be the full `org/repo` form (e.g. `Netcracker/qubership-consul`), not
  just the repo name. The checkout path and all subsequent paths are derived from this value.
- `resource_folder` is declared `required: true` in the action signature — pass `""` when no
  pre-installation resources are needed.
- When `restricted: true`, both the CRD step and the Helm step run under separate contexts;
  the context is always restored to `kind-kind` at the end.
- For non-release branches, `charts-values-update-action` is pinned at commit
  `d558e10a6537924292e7dd7ff4109c2bda9b406e` (v2.0.5) in the action source.
- Pin to a full 40-character commit SHA with the release tag as a trailing comment, e.g.
  `@905b88900dc8c14291eaeff4eddcf4d4f734aee1 # v1.9.0`. The SHA is the immutable pin; the
  comment shows which release it points to. Tags alone are mutable and can be moved — acceptable
  only when callers explicitly want auto-updates within a minor version. Never use `@main` or
  short SHAs.
