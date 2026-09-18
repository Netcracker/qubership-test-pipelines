# Nightly Status Check

## Overview

The Nightly Status Check workflow monitors the status of nightly test workflows of the platform services.
It does not run the tests itself — it only checks the latest runs of the caller workflows in the service
repositories (e.g. [`run_nightly_tests.yaml`](https://github.com/Netcracker/qubership-consul/actions/workflows/run_nightly_tests.yaml)
in `Netcracker/qubership-consul`) and produces a summary table. It is a reporting workflow:
failed nightly runs are reported there, but they do not fail this workflow itself.

## Triggers

- **Schedule**: every day at `0 6 * * *` UTC
- **Manual**: via `workflow_dispatch`

The workflow is not triggered by pushes or pull requests.

## Manual run inputs

| Parameter    | Type   | Required | Description                                                                   |
|--------------|--------|----------|-------------------------------------------------------------------------------|
| components   | string | No       | Comma-separated list of component names to check. Empty = all from the config |

Component names are compared **case-insensitively** with the `name` field of the config entries
(exact match, not a substring); components that do not match are skipped.

## Configuration

The list of monitored components is stored in
[`workflow-config/nightly-status.yaml`](../../workflow-config/nightly-status.yaml).

Each component entry:

| Field            | Description                                                    |
|------------------|----------------------------------------------------------------|
| `name`           | Component name as it appears in the report                     |
| `repository`     | GitHub repository hosting the nightly workflow (`owner/repo`)  |
| `workflow_file`  | File name of the nightly workflow in the service repository    |
| `branch`         | Branch to check (default: `main`)                              |
| `lookback_hours` | Consider only runs not older than this many hours (default: 24)|

To add a new component, append an entry to the config file.

## Report

The workflow generates `nightly-status-report.md` with a table:

| Component | Status | Run | Started (UTC) | Duration | Link | Failed jobs |
|-----------|--------|-----|---------------|----------|------|-------------|

Statuses:

- :white_check_mark: **passed**
- :x: **failed**
- :hourglass_flowing_sand: **in progress**
- :grey_question: **no runs** (no run in the lookback window, rendered as `no runs in the last <N> h`)

After the table the report contains a `## Summary` section with the number of passed, failed,
in-progress and "no runs" components.

`Duration` is the run duration in `Xh Ym Zs` format, computed from the run's
`run_started_at` and `updated_at` timestamps. It is shown as `-` when no run is found.

`Failed jobs` lists the names of the jobs that finished with the `failure` conclusion,
each job on its own line inside the cell (rendered with `<br>`). It is shown as `-`
when there are no failed jobs or no run is found. Note: a literal `|` in matrix job
names is escaped (`\|`) so it does not break the markdown table.

### Failure Details section

When at least one workflow run contains failed jobs, the report is extended (right after
the `## Summary`) with a **`## Failure Details`** block. It lists every failed job per
component with the failure reason beneath it:

- `### <Component>` — one heading per component that has failed jobs; consecutive component
  blocks are separated with a horizontal rule (`---`);
- a `#### <job-name>` heading per failed job, where the whole job name is a link to that job
  (the script renders it as an HTML `<a>` so names containing brackets/pipes stay valid);
- below it a bold `Failing step:` line (the top-level step is shown in parentheses when an
  inner step was found) and the reason inside a `text` code block.

The `Failing step:` line names the step of the job that ended with the `failure` conclusion
(from the `/jobs` API). GitHub's `/jobs` API only exposes top-level steps, so to find which
inner step of a composite `uses:` action actually failed the script parses the **raw log
structure**:

1. GitHub appends `##[error]Process completed with exit code N.` right after the output of
   the step that failed. The failing step is the run-group whose header
   (`##[group]Run # ▶️ <name>`) directly precedes that marker. The script takes the **first**
   such marker in the log (the root failure), e.g. `Install/update service with Helm`. Later
   markers produced by follow-on `if: always()` steps (artifact upload, diagnostics) are ignored.
2. **Summary steps.** The composite actions of this repository report the real problems with
   `::error::` in earlier steps and only fail at the very end: `Check job status`,
   `final-status-check` and `Check pipeline status` add nothing new and just summarise the steps
   above them. When such a step is the one that failed (or when its own output contains no error
   at all), the script looks for the reason in the steps **above** it — first in
   `Check service is ready` and `Get logs from test pod`, then in the nearest step that has an
   error — and reports **that** step as the failing one. This is what makes a Consul-style failure
   report `Check service is ready` with `❌ Resources not ready after 180 retries` instead of
   `Check job status` with its generic message.
3. If no such marker exists, it uses the first `##[end-action` with `outcome=failure` and the
   display of its paired `##[start-action`.
4. As a last resort (log not readable), it reports the top-level step from the `/jobs` API
   plus the job's check-run annotation.

The `Reason:` text is taken from the **log of the selected step**. Timestamps, ANSI colors,
`##[` markers, the colored command preview, the `shell:`/`env:` header of the step and the
`Process completed with exit code N` marker are stripped. Then:

1. the first line matching a meaningful error pattern is used — `UPGRADE FAILED`,
   `INSTALLATION FAILED`, `Resources not ready after …`, `CR check failed`, `Tests failed`,
   `timed out waiting for` — together with its continuation lines (indented/bulleted lines, lines
   without a timestamp and YAML-style `key:` lines of a dumped value). A Helm upgrade failure is
   therefore reported as `Error: UPGRADE FAILED: post-upgrade hooks failed: 1 error occurred:`
   plus `* timed out waiting for the condition`, and a schema error keeps its
   `zookeeper-service: - at '...': got string, want boolean` part;
2. if that line belongs to a retry loop (resources/CR/tests readiness), the whole state of the
   **last attempt** is printed, starting at the last `Attempt N/M` line, so the Consul case shows
   `Attempt 180/180`, `Deployment ... is not ready: 0/1`, `⏳ Some resources are not ready` and
   `❌ Resources not ready after 180 retries`;
3. otherwise the first generic error line (`Error`, `ERROR`, `❌`, `FAILED`, `panic`, …) is
   printed with two lines of context before and three lines after it; when the step produced no
   recognizable error, its last lines are printed instead.

Only the selected step is used, so follow-on steps (e.g. an `if: always()` artifact-upload) cannot
pollute the snippet, and the steps above the failing one are searched **only** for the diagnostic
steps (`Check service is ready`, `Get logs from test pod`) so unrelated output (git checkout, helm
status, …) is never picked up. If the log cannot be read — see [Authentication](#authentication) —
or when it would only yield a summary message of the wrapper (`Service was installed with errors!`,
`Job status: failure`), the **first check-run annotation** that is not the
`Process completed with exit code N` marker is used instead (annotations are the `::error::`
messages of the steps in chronological order) and the `Failing step:` name comes from the
`/jobs` API; when there are no usable annotations either, the generic
`No details available (see the run log)` message is shown. Reasons are truncated to 800 characters
and rendered inside a `text` code block.

Example:

````markdown
## Failure Details

### ZooKeeper

#### [Nightly-Zookeeper-Pipeline / Clean [main] with Monitoring and Allure](https://github.com/Netcracker/qubership-zookeeper/actions/runs/34178894644/job/101913778885)

**Failing step:** `Install/update service with Helm` _(top-level: `Clean Install Zookeeper main`)_

**Reason:**

```text
zookeeper_install_APP_k8s_monitoring_allure.yml
Error: INSTALLATION FAILED: values don't meet the specifications of the schema(s) in the following chart(s):
zookeeper-service:
- at '/integrationTests/atpReport/enabled': got string, want boolean
```

#### [Nightly-Zookeeper-Pipeline / final-status-check](https://github.com/Netcracker/qubership-zookeeper/actions/runs/34178894644/job/101913778886)

**Failing step:** `Check job status`

**Reason:**

```text
Job status: failure
```

---

### Kafka

#### [Nightly-Kafka-Pipeline / Clean [main] with Monitoring and Allure](https://github.com/Netcracker/qubership-kafka/actions/runs/555/job/666)

**Failing step:** `Install/update service with Helm` _(top-level: `Clean Install Kafka main`)_

**Reason:**

```text
Error: INSTALLATION FAILED: ... got string, want boolean
```
````

The report is written to the job summary by the script (`$GITHUB_STEP_SUMMARY`), printed to the
workflow log and uploaded as the `nightly-status-report` artifact (kept for 7 days).

## Authentication

The job runs the script with `GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}` and `contents: read`
permissions — no additional secret or personal access token is required, and none is used.

The token is used for the GitHub API calls (`gh api`, and `curl` with an `Authorization: Bearer`
header when downloading a job log):

- reading the runs, jobs and check-run annotations of the monitored repositories works with the
  default token;
- downloading an Actions **log** of another repository requires admin rights on that repository,
  so the repository-scoped `GITHUB_TOKEN` gets `403` for the logs of the service repositories.

That means the failure reason usually comes from the check-run annotations (see
[Failure Details](#failure-details-section)) rather than from the raw log. To get the
log-derived reasons, run the script with a token that has admin access to the monitored
repositories (see below).

## Running locally

The script can be run manually; `gh`, `jq`, `yq` and `curl` must be installed.

```bash
GH_TOKEN=<token> ./scripts/check_nightly_status.sh \
  workflow-config/nightly-status.yaml \
  nightly-status-report.md \
  "Consul,Kafka"
```

Arguments:

- `CONFIG_FILE` — path to the component config (default: `workflow-config/nightly-status.yaml`);
- `REPORT_FILE` — path of the generated markdown report (default: `nightly-status-report.md`);
- `COMPONENTS_FILTER` — optional comma-separated component filter (default: empty, all components).

Without `GH_TOKEN` the API is queried anonymously, which is rate limited and cannot read the logs.
