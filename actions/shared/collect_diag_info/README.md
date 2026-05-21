# 🚀 Collect Diagnostics Action

GitHub Action to collect logs, resource manifests, and artifacts from a Kubernetes namespace
and upload them as a workflow artifact for post-deploy or post-failure investigation.

---

## Features

- Creates an `artifacts/` working directory for all collected files
- Collects pod list, per-pod YAML manifests, namespace events, PVC and PV information
- Captures container logs for all containers in all pods, with a pending-retry loop
  (up to 300 seconds) for containers that are not yet running or terminated
- Captures previous-run logs for containers that have restarted at least once
- Lists all resources (`kubectl get all`) and secret names in the namespace
- Optionally collects VictoriaMetrics Custom Resource YAML files for monitoring pipelines
- Generates a timestamped artifact name automatically, or uses a caller-supplied name
- Uploads all collected files as a single GitHub Actions artifact

---

## 📌 Inputs

| Name | Description | Required | Default |
|---|---|---|---|
| `namespace` | Kubernetes namespace to collect diagnostics from. | Yes | - |
| `service_branch` | Branch or tag name of the service being tested. Used in the auto-generated artifact name — slashes are replaced with underscores, whitespace is stripped. Ignored when `artifact_name` is provided. | No | - |
| `artifact_name` | Custom base name for the uploaded artifact. When provided, the final name is `<artifact_name>_<timestamp>`. When empty, the name is generated as `<job>_<namespace>_<branch>_<version>_artifacts_<timestamp>`. | No | `""` |
| `version` | Matrix dimension value (e.g. `${{ matrix.service_image }}`) appended as a suffix in the auto-generated artifact name. Has no effect when `artifact_name` is provided. | No | `""` |
| `monitoring_pipeline` | When `true`, dumps VictoriaMetrics CRs (`VMAlertManager`, `VMAlert`, `VMAgent`, `VMSingle`, `VMAuth`, `PlatformMonitoring`) as YAML files into `artifacts/`. | No | `false` |

---

## 📌 Outputs

This action produces no step outputs. All collected data is uploaded as a workflow artifact
whose name is derived from the inputs (see Additional Information).

---

## How it works

The action gathers diagnostics in the following order, with most steps running under
`if: always()` so they execute even when previous steps failed:

1. **Monitoring resources** (only when `monitoring_pipeline: true`, runs under `if: always()`): exports six
   VictoriaMetrics and `PlatformMonitoring` CRs as YAML files into `artifacts/`.
2. **Pod list**: runs `kubectl get pods` and saves output to
   `artifacts/<namespace>_get_pods.txt`.
3. **Pod YAML manifests**: saves each pod's full YAML to
   `artifacts/pod_yamls/<pod-name>.yaml`. Failures write a `_FAILED.txt` marker instead.
4. **Namespace events**: saves `kubectl events` output to
   `artifacts/<namespace>_get_events.txt`.
5. **PVC YAML**: saves all PersistentVolumeClaim manifests to
   `artifacts/<namespace>_get_pvc_yaml.yaml`.
6. **PV list**: filters cluster-wide PVs for those bound to the namespace and saves to
   `artifacts/<namespace>_get_pv.txt`.
7. **Container logs**: for every container in every pod, collects current logs to
   `artifacts/logs/<pod>__<container>.log`. Containers not yet in `running` or `terminated`
   state are queued and retried every 5 seconds until ready or the 300-second hard timeout
   is reached. Containers with `restartCount > 0` also get their previous logs saved to
   `artifacts/logs/<pod>__<container>__previous.log`.
8. **All resources**: prints `kubectl get all` to the workflow log (not saved to a file).
9. **Secrets list**: prints `kubectl get secrets` to the log (names only, not values).
10. **Artifact upload**: generates a timestamped artifact name and uploads the entire
    `artifacts/` folder via `actions/upload-artifact@v4`.

---

## Additional Information

### Artifact naming

When `artifact_name` is empty (the default), the artifact name is built as:

```text
<github.job>_<namespace>_<service_branch>_<version>_artifacts_<YYYYMMDDHHmmssSSS>
```

- `service_branch` has whitespace stripped and `/` replaced with `_`.
- `<version>_` is included only when the `version` input is non-empty.
- The timestamp uses UTC with millisecond precision.

When `artifact_name` is provided, the name is:

```text
<artifact_name>_<YYYYMMDDHHmmssSSS>
```

Slashes in `artifact_name` are replaced with `_`.

### Container log collection

The log-collection step uses a two-pass approach:

- **First pass**: iterates all pods and containers. Running or terminated containers have
  logs collected immediately. All others are added to a pending list.
- **Retry loop**: pending containers are re-checked every 5 seconds. The loop exits when all
  pending containers have been processed or the 300-second timeout is reached; timed-out
  containers are skipped with a log message.

Log files for the first pass use a double-underscore separator (`pod__container.log`).
Log files collected in the retry loop use a single-underscore separator (`pod_container.log`).

### Monitoring YAML files

When `monitoring_pipeline: true`, the following files are written to `artifacts/`:

| File | Resource |
|---|---|
| `vmalertmanagers.yaml` | `VMAlertManager` |
| `vmalerts.yaml` | `VMAlert` |
| `vmagent.yaml` | `VMAgent` |
| `vmsingles.yaml` | `VMSingle` |
| `vmauths.yaml` | `VMAuth` |
| `PlatformMonitoring.yaml` | `PlatformMonitoring platformmonitoring` |

All commands use `|| true` — missing CRDs do not fail the step.

---

## Usage

```yaml
name: Collect Diagnostics

on:
  workflow_dispatch:

jobs:
  diagnostics:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - name: Checkout pipeline repo
        uses: actions/checkout@v4
        with:
          path: qubership-test-pipelines

      - name: Collect diagnostics
        if: always()
        uses: Netcracker/qubership-test-pipelines/actions/shared/collect_diag_info@905b88900dc8c14291eaeff4eddcf4d4f734aee1 # v1.9.0
        with:
          namespace: consul
          service_branch: ${{ github.ref_name }}
```

---

## Notes

- All diagnostic steps run with `if: always()` — they collect data even when earlier steps
  in the caller's job have failed. Call this action with `if: always()` as well to ensure
  it runs after a failed Helm deploy or verification step.
- The `artifacts/` directory is created but **not** cleared by this action. If a prior step
  in the same job already populated `artifacts/`, those files will be included in the upload.
- The `Get Secrets` step logs secret names to the workflow run log (not values). Anyone with
  read access to the workflow run can see the secret names in the namespace.
- The `version` input is used as a suffix in the auto-generated artifact name. Pass the
  relevant matrix dimension (e.g. `${{ matrix.service_image }}`) explicitly — omit the input
  to leave the suffix empty.
- Pin to a full 40-character commit SHA with the release tag as a trailing comment, e.g.
  `@905b88900dc8c14291eaeff4eddcf4d4f734aee1 # v1.9.0`. The SHA is the immutable pin; the
  comment shows which release it points to. Tags alone are mutable and can be moved —
  acceptable only when callers explicitly want auto-updates within a minor version. Never
  use `@main` or short SHAs.
