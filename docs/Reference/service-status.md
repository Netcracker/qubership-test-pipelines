# Service Status Report

## Overview

The Service Status Report is a **manually started** workflow that builds the status table of the
services listed in [`workflow-config/service-status.yaml`](../../workflow-config/service-status.yaml).
It does not run any tests: for every service it analyses the last nightly runs of the service
nightly workflow (the caller workflow in the service repository, e.g.
[`run_nightly_tests.yaml`](https://github.com/Netcracker/qubership-consul/actions/workflows/run_nightly_tests.yaml)
in `Netcracker/qubership-consul`) and reports the state of those runs and every failed job with its
failing step and reason.

## Triggers

- **Manual**: via `workflow_dispatch`, with the optional `services` input.
- **Push**: so the report can be produced for a branch before the workflow is available on the
  default branch — a `workflow_dispatch`-only workflow cannot be started from the Actions UI before
  that.

The workflow has no schedule.

## Manual run inputs

| Parameter  | Type   | Required | Description                                                                                      |
|------------|--------|----------|--------------------------------------------------------------------------------------------------|
| `services` | string | No       | Comma-separated list of service names to include (case-insensitive). Empty = all from the config |

Service names are compared case-insensitively with the `name` field of the config entries
(exact match, not a substring); services that do not match are skipped.

## Configuration

The list of reported services is stored in
[`workflow-config/service-status.yaml`](../../workflow-config/service-status.yaml).

| Field           | Description                                                                     |
|-----------------|---------------------------------------------------------------------------------|
| `name`          | Service name as it appears in the report                                        |
| `repository`    | GitHub repository hosting the nightly workflow (`owner/repo`)                   |
| `workflow_file` | File name of the caller nightly workflow in the service repository              |
| `branch`        | Branch to analyse (default: `main`)                                             |
| `runs_count`    | How many recent runs to analyse (default: 10, can also be set for all services) |
| `lookback_days` | Runs older than this many days are ignored (default: 10)                        |
| `note`          | Free-form note shown in the service row (for example the expected durations)    |

## Report

The workflow generates `service-status-report.md`, publishes it to the job summary and uploads it as
the `service-status-report` artifact (kept for 7 days). The report is rebuilt on every run and
contains one row per service plus one row per failed job of the analysed window:

```text
# Service Status Report

_Generated at: 2026-01-05 06:10:12 UTC_

| Service | State | Links to failed jobs | Issue | Failing step | Reason | Duration |
|---------|-------|----------------------|-------|--------------|--------|----------|
| [Consul](https://github.com/Netcracker/qubership-consul/actions/workflows/run_nightly_tests.yaml) | 9/10 | | | | image build up to 4 min, tests up to 12 min | 1h 12m 0s |
| | | <a href="https://github.com/Netcracker/qubership-consul/actions/runs/27922954156/job/82619842405">Clean [main] &#124; Monitoring</a><br>[#192 (2026-09-12)](https://github.com/Netcracker/qubership-consul/actions/runs/27922954156) | | `Verify resources` _(top-level: `Clean Install Consul main`)_ | Error: ❌ Resources not ready after 180 retries<br>ERROR_FLAG: true | 30m 0s |
| | | <a href="https://github.com/Netcracker/qubership-consul/actions/runs/27855021514/job/82440795283">final-status-check</a><br>[#186 (2026-09-06)](https://github.com/Netcracker/qubership-consul/actions/runs/27855021514) | | `Check job status` | Job status: failure | 28m 12s |
```

### Columns

- **Service** — the service name from the config; it links to the nightly workflow of the service.
- **State** — `<passed>/<analysed>` completed nightly runs of the analysed window: `10/10` means
  stable, `1..9/10` unstable and `0/10` not working. The window is the most recent `runs_count`
  runs of the last `lookback_days` days; runs that are still in progress are not counted, so the
  denominator can be smaller than the configured number of runs.
- **Links to failed jobs** — one row per failed job of the analysed window contains the link to the
  job and the link to its run; the run link shows the run number and the date of the run, so it is
  always clear which run a row belongs to. Failed jobs of different runs are always in different
  rows, so runs with failures are separated. Runs older than `lookback_days` are not analysed at all.
- **Issue** — not filled in yet.
- **Failing step** — the step of the job that failed. The script detects the inner step in the job
  log and shows the top-level step from the API in parentheses when the two differ.
- **Reason** — the error snippet of the failing step: the first error of that step's log window with
  a few context lines before and after it (see
  [Nightly Status Check](nightly-status-check.md#failure-details-section) for how it is extracted),
  with the check-run annotations as a fallback when the log cannot be read. In the service row this
  column shows the `note` from the config. The snippet of the example above is trimmed to keep the
  table row short; in a real report it contains the whole window with `<br>` as the line separator.
- Jobs such as `Check job status` / `final-status-check` only repeat the result of the pipeline, so
  their reason is the generic `Job status: failure` — the real cause is in the row of the job that
  actually failed (for example `Verify resources` above).
- **Duration** — in the service row the duration of the latest run, in the failed job rows the
  duration of the run the job belongs to. Durations are rendered as `Xh Ym Zs`.

## Authentication

The workflow runs the script with `GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}` and `contents: read`
permissions — no additional secret is required. Downloading an Actions log of another repository
requires admin rights on that repository, so with the default token the failure reasons usually come
from the check-run annotations instead of the raw log.

## Running locally

[`scripts/service_status_report.sh`](../../scripts/service_status_report.sh) can be run manually;
`gh`, `jq`, `yq` and `curl` must be installed. The script sources the shared helpers from
[`scripts/lib/nightly_status_lib.sh`](../../scripts/lib/nightly_status_lib.sh).

```bash
GH_TOKEN=<token> ./scripts/service_status_report.sh \
  workflow-config/service-status.yaml \
  service-status-report.md \
  "Consul"
```

Arguments:

- `CONFIG_FILE` — path to the services config (default: `workflow-config/service-status.yaml`);
- `REPORT_FILE` — path of the generated markdown report (default: `service-status-report.md`);
- `SERVICES_FILTER` — optional comma-separated service filter (default: empty, all services).

Without `GH_TOKEN` the API is queried anonymously, which is rate limited and cannot read the logs.
