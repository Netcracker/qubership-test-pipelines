# 🚀 Verify Installation Action

GitHub Action to verify Kubernetes deployments including Custom Resource status checks,
pod readiness validation, and Robot Framework test result collection.

---

## Features

- Polls Custom Resource conditions (`failed` / `progress` / `success`) until ready or timed out
- Validates readiness of all Deployments, StatefulSets, and DaemonSets in the namespace
- Optionally verifies VictoriaMetrics Custom Resource statuses for monitoring pipelines
- Detects and waits for a test pod (name contains `tests`) to complete
- Collects Robot Framework HTML reports and output artifacts from the test pod
- Saves test logs to `artifacts/<namespace>_tests.txt`
- Aggregates all check results via a shared `ERROR_FLAG` and fails the step at the end
  if any check did not pass

---

## 📌 Inputs

| Name | Description | Required | Default |
| --- | --- | --- | --- |
| `namespace` | Kubernetes namespace where the service is installed. | Yes | - |
| `service_ready_max_retries` | Maximum number of poll attempts for CR and resource readiness checks. | Yes | - |
| `service_ready_retry_interval` | Delay in seconds between CR and resource readiness poll attempts. | Yes | - |
| `test_completion_max_retries` | Maximum number of poll attempts for the test pod to complete. Skipped when `check_tests` is `false`. | Yes | - |
| `test_completion_retry_interval` | Delay in seconds between test pod completion poll attempts. Skipped when `check_tests` is `false`. | Yes | - |
| `crd_list` | Space-separated list of Custom Resource names to check (e.g. `consul`). Pass empty to skip CR checks. | No | - |
| `check_tests` | When `true`, waits for the test pod to complete and collects Robot Framework results. Set to `false` to skip test checks entirely. | No | `true` |
| `monitoring_pipeline` | When `true`, runs additional VictoriaMetrics CR status checks using `check-vm-cr-statuses.sh`. Requires `repository_name` and the expected-vm-cr-statuses.json file to be present. | No | `false` |
| `repository_name` | Full `org/repo` checkout path of the service repository. Required when `monitoring_pipeline` is `true` — used to locate `.github/expected-vm-cr-statuses.json`. | No | `""` |

---

## 📌 Outputs

This action produces no step outputs. Results are communicated via exit code: the action
exits with code `1` if any check failed, `0` on full success.

---

## How it works

The action runs three sequential verification phases, collecting failures into a shared
`ERROR_FLAG` environment variable, then fails or succeeds at the end:

**Phase 1 — Service readiness** (always runs):

- For each attempt up to `service_ready_max_retries`, `check_cr.sh` is called with the
  `crd_list`. It inspects `.status.conditions` on the CR and classifies the result as
  success (exit 0), in-progress (exit 1), or failed (exit 2). A failure exits the loop
  and sets `ERROR_FLAG=true`; in-progress retries after `service_ready_retry_interval`
  seconds.
- After the CR loop, `check_resources.sh` polls readiness of all Deployments, StatefulSets,
  and DaemonSets in the namespace. It checks `readyReplicas == replicas` for each resource.
  Pods are printed on each not-ready attempt.

**Phase 2 — Monitoring checks** (only when `monitoring_pipeline: true`):

- The full service-readiness sequence from Phase 1 is repeated specifically for monitoring
  resources.
- `check-vm-cr-statuses.sh` reads `<repository_name>/.github/expected-vm-cr-statuses.json`,
  filters components by what is enabled in the `PlatformMonitoring` CR, and checks each
  VictoriaMetrics CR's status field or conditions. The JSON file is printed to the log
  before the check (see Notes).

**Phase 3 — Test validation** (only when `check_tests: true`):

- `check_tests.sh` scans all pods in the namespace for one whose name contains `tests`.
- Once found, it polls the pod phase and inspects logs for a `Report.*html` pattern that
  signals Robot Framework has finished writing output.
- On completion it copies `/opt/robot/output` and `/tmp/clone` from the pod into
  `artifacts/robot-results/` and writes logs to `artifacts/<namespace>_tests.txt`.
- Exit codes: `0` = passed, `1` = still running (retry), `2` = tests failed.
- If no test pod is found, a warning is emitted and the phase is skipped.
- After `test_completion_max_retries` attempts without completion, `ERROR_FLAG=true` is set.

**Final step**: if `ERROR_FLAG` is `true`, the action exits with code `1`.

---

## Additional Information

### CR condition classification

`check_cr.sh` reads `.status.conditions[]` and classifies by matching condition `type`
(case-insensitive substring):

- Contains `failed` → exit 2 (hard failure, stops retrying)
- Contains `progress` → exit 1 (still running, retry)
- Contains `success` → exit 0 (done)
- No matching condition → treated as in-progress (exit 1)

If `crd_list` is empty, `check_cr.sh` returns exit 0 immediately and CR checking is skipped.

### Resource readiness check

`check_resources.sh` checks Deployments, StatefulSets, and DaemonSets:

- Deployment / StatefulSet: `readyReplicas == replicas` and `replicas > 0`
- DaemonSet: `numberReady == desiredNumberScheduled` and `desiredNumberScheduled > 0`

A resource with zero replicas/desired is treated as not ready.

### Test pod discovery

The test pod is found by scanning all pod names in `namespace` for one containing the
substring `tests`. Only the first matching pod is used. If the service deploys multiple
pods with `tests` in their name, only the first one returned by kubectl is checked.

### monitoring_pipeline expected-vm-cr-statuses.json

The JSON file at `<repository_name>/.github/expected-vm-cr-statuses.json` defines which
VictoriaMetrics components to check and what their expected state is. Its contents are
printed to the workflow log before the check runs (see Notes for implications).

Example file structure:

```json
[
  {
    "kind": "VMSingle",
    "name": "victoria-metrics",
    "component": "vmSingle",
    "check": "updateStatus",
    "jsonPath": ".status.updateStatus",
    "expected": "operational"
  },
  {
    "kind": "VMAgent",
    "name": "vmagent-primary",
    "component": "vmAgent",
    "check": "conditionsMatch",
    "expectedConditions": {
      "reason": "Reconciled",
      "status": "True"
    }
  }
]
```

The script filters this list against the `install` flags in the `PlatformMonitoring` CR
so only enabled components are checked.

### Artifact folder

An `artifacts/` directory is created (and cleared) at the start of every run. Robot
Framework results are placed under `artifacts/robot-results/`. Test logs are written to
`artifacts/<namespace>_tests.txt`. Upload this folder as a workflow artifact to preserve
results between jobs.

---

## Usage

```yaml
name: Verify Service Installation

on:
  workflow_dispatch:

jobs:
  verify:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - name: Checkout pipeline repo
        uses: actions/checkout@v4
        with:
          path: qubership-test-pipelines

      - name: Verify installation
        uses: Netcracker/qubership-test-pipelines/actions/shared/verify_installation@905b88900dc8c14291eaeff4eddcf4d4f734aee1 # v1.9.0
        with:
          namespace: consul
          service_ready_max_retries: 20
          service_ready_retry_interval: 30
          test_completion_max_retries: 40
          test_completion_retry_interval: 15
          crd_list: consul
          check_tests: true

      - name: Upload artifacts
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: verify-results
          path: artifacts/
```

---

## Notes

- The `artifacts/` folder is wiped at action start — do not rely on content from previous
  steps being present there.
- The `monitoring_pipeline` step prints the full contents of `expected-vm-cr-statuses.json`
  to the workflow log before checking. Avoid storing secrets or sensitive values in that file.
- When `check_tests: true` but no pod with `tests` in its name exists, the step emits a
  warning and exits cleanly (does not set `ERROR_FLAG`).
- `service_ready_max_retries` and `test_completion_max_retries` have no defaults in
  `action.yml` — callers must always provide explicit values.
- Pin to a full 40-character commit SHA with the release tag as a trailing comment, e.g.
  `@905b88900dc8c14291eaeff4eddcf4d4f734aee1 # v1.9.0`. The SHA is the immutable pin; the
  comment shows which release it points to. Tags alone are mutable and can be moved —
  acceptable only when callers explicitly want auto-updates within a minor version. Never
  use `@main` or short SHAs.
