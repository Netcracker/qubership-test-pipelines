# Nightly Status Check

## Overview
The Nightly Status Check workflow monitors the status of nightly test workflows of the platform services.
It does not run the tests itself — it only checks the latest runs of the caller workflows in the service
repositories (e.g. [`run_nightly_tests.yaml`](https://github.com/Netcracker/qubership-consul/actions/workflows/run_nightly_tests.yaml)
in `Netcracker/qubership-consul`) and produces a summary table.

## Triggers
- **Schedule**: every day at **09:00 MSK (UTC+3)** — `0 6 * * *` UTC
- **Manual**: via `workflow_dispatch`

## Manual run inputs
| Parameter    | Type   | Required | Description                                                                   |
|--------------|--------|----------|-------------------------------------------------------------------------------|
| components   | string | No       | Comma-separated list of component names to check. Empty = all from the config |

## Configuration
The list of monitored components is stored in [`workflow-config/nightly-status.yaml`](../../workflow-config/nightly-status.yaml).

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
|-----------|--------|-----|----------------|----------|------|-------------|

Statuses:
- :white_check_mark: **passed**
- :x: **failed**
- :hourglass_flowing_sand: **in progress**
- :grey_question: **no runs** (no runs in the lookback window)

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

The `Failed step(s)` line names the top-level steps of the job that ended with the
`failure` conclusion (from the `/jobs` API). GitHub's `/jobs` API only exposes top-level
steps, so to find which inner step of a composite `uses:` action actually failed the script
parses the **raw log structure** — it does not guess by matching words like `error`:

1. GitHub appends `##[error]Process completed with exit code N.` right after the output of
   the step that failed. The failing step is the run-group whose header
   (`##[group]Run # ▶️ <name>`) directly precedes that marker. The script takes the **first**
   such marker in the log (the root failure) and names that step, e.g.
   `Install/update service with Helm`. Later markers produced by follow-on `if: always()`
   steps (artifact upload, diagnostics) are ignored.
2. If no such marker exists, it uses the first `##[end-action` with `outcome=failure` and the
   display of its paired `##[start-action`.
3. As a last resort (log not readable), it reports the top-level step from the `/jobs` API
   plus the job's check-run annotation.

The `Reason:` text is the **tail of the failing step's own log window** (from its run-group
header to the failure marker). Timestamps, ANSI colors, `##[` markers, the colored command
preview and `shell:`/`env:` metadata are stripped, and only the last real output lines of
that step are kept. Because the window is bounded to the failing step, follow-on steps (e.g.
an `if: always()` artifact-upload) cannot pollute the snippet, and real errors such as a
Helm `INSTALLATION FAILED: ... got string, want boolean` message are shown instead of a
generic exit code. If the log cannot be read, the job's **check-run annotations** are used
as a fallback; otherwise the generic `No details available` message is shown. Reasons are
truncated to 800 characters and rendered inside a `text` code block.

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

The report is published to the job summary and uploaded as the `nightly-status-report` artifact.

## Secret
The workflow uses `NIGHTLY_STATUS_TOKEN` (set as `GH_TOKEN` in the job, falling back to the
default `GITHUB_TOKEN`) to query the GitHub API and download the logs of the service
repositories. **Important:** GitHub only allows downloading a repository's Actions logs to a
token that has admin rights on that repository. The repo-scoped `GITHUB_TOKEN` of this
repository therefore returns `403` for logs of other repos, so without `NIGHTLY_STATUS_TOKEN`
the `Inner step(s)` line and the real error text cannot be retrieved (the report falls back
to the generic check-run annotation). Configure a PAT with at least `repo`/`actions:read`
scopes **and admin access to each monitored service repository** as the
`NIGHTLY_STATUS_TOKEN` repository secret.
