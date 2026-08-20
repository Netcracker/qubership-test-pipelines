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

The report is published to the job summary and uploaded as the `nightly-status-report` artifact.

## Secret
The workflow uses `NIGHTLY_STATUS_TOKEN` to query the GitHub API of the service repositories.
If it is not set, it falls back to the default `GITHUB_TOKEN` (which works for public repositories).
For private repositories, configure a PAT with `repo` and `read:org` scopes as the `NIGHTLY_STATUS_TOKEN` secret.
