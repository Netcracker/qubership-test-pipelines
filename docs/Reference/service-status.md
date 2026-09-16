# Service Status Report

## Overview

The Service Status Report is a **manually started** workflow that builds the status table of the
services listed in [`workflow-config/service-status.yaml`](../../workflow-config/service-status.yaml).
It does not run any tests: for every service it analyses the last nightly runs of the service
nightly workflow (the caller workflow of the service repository, e.g.
[`run_nightly_tests.yaml`](https://github.com/Netcracker/qubership-consul/actions/workflows/run_nightly_tests.yaml)
in `Netcracker/qubership-consul`) and reports the test pipeline version, the state, the links to the
failed runs, the failure reasons and the durations.

## Triggers

- **Manual only**: via `workflow_dispatch`. The workflow has no schedule and is not triggered by
  pushes or pull requests.

## Manual run inputs

| Parameter    | Type   | Required | Description                                                                             |
|--------------|--------|----------|-----------------------------------------------------------------------------------------|
| `services`   | string | No       | Comma-separated list of service names to include (case-insensitive). Empty = all from the config |

Service names are compared case-insensitively with the `name` field of the config entries
(exact match, not a substring); services that do not match are skipped.

## Configuration

The list of reported services is stored in
[`workflow-config/service-status.yaml`](../../workflow-config/service-status.yaml).

| Field           | Description                                                                   |
|-----------------|-------------------------------------------------------------------------------|
| `name`          | Service name as it appears in the report                                      |
| `repository`    | GitHub repository hosting the nightly workflow (`owner/repo`)                  |
| `workflow_file` | File name of the caller nightly workflow in the service repository             |
| `branch`        | Branch to analyse (default: `main`)                                           |
| `runs_count`    | How many recent runs to analyse (default: 10, can also be set for all services) |
| `comment`       | Free-form note shown in the service row (for example the expected durations)    |

The `uses:` line of the caller workflow is read to get the version of the test pipeline, so the
service entry must point to the workflow that calls a reusable workflow of this repository:

```yaml
jobs:
  Nightly-Consul-Pipeline:
    uses: Netcracker/qubership-test-pipelines/.github/workflows/consul.yaml@e1905f040398e9ae733b0cefa7e7793b6204ecfe # v1.16.0
```

## Report

The workflow generates `service-status-report.md`, publishes it to the job summary and uploads it as
the `service-status-report` artifact (kept for 7 days). The report contains one row per service plus
one row per failed run of the analysed window:

```text
# Статус nightly-запусков сервисов

_Сформировано: 2026-01-05 13:02:12 UTC_

| Сервис | Версия тестового пайпа | Состояние | Ссылки на запуски | Issue | Комментарий | Длительность запуска |
|--------|------------------------|-----------|-------------------|-------|-------------|----------------------|
| Консул | v1.16.0 | 9/10 | [run_nightly_tests.yaml](https://github.com/Netcracker/qubership-consul/actions/workflows/run_nightly_tests.yaml) | | сборка имаджей - до 4 мин, тесты - до 12 мин | 1h 12m 0s |
| | | | <a href="https://github.com/Netcracker/qubership-consul/actions/runs/27922954156/job/82619842405">Clean [main] &#124; Monitoring</a><br>[#27922954156](https://github.com/Netcracker/qubership-consul/actions/runs/27922954156) | | Error: INSTALLATION FAILED: ... got string, want boolean | 30m 0s |
```

### Columns

- **Сервис** — the service name from the config.
- **Версия тестового пайпа** — the version of `qubership-test-pipelines` taken from the comment of
  the `uses:` line of the caller workflow (for example `# v1.16.0`). It is empty when the workflow
  file or the comment cannot be read.
- **Состояние** — `<passed>/<analysed>` completed nightly runs of the analysed window:
  `10/10` means stable, `1..9/10` unstable and `0/10` not working. Runs that are still in progress
  are not counted, so the denominator can be smaller than `runs_count`.
- **Ссылки на запуски** — in the service row the link to the nightly workflow; in the rows of the
  failed runs the links to the failed jobs and to the run itself.
- **Issue** — not filled in yet.
- **Комментарий** — in the service row the note from the config; in the rows of the failed runs the
  failure reason (from the job log, see [Nightly Status Check](nightly-status-check.md#failure-details-section)).
- **Длительность запуска** — in the service row the duration of the latest run; in the rows of the
  failed runs the duration of that run. Durations are rendered as `Xh Ym Zs`.

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
  "Консул"
```

Arguments:

- `CONFIG_FILE` — path to the services config (default: `workflow-config/service-status.yaml`);
- `REPORT_FILE` — path of the generated markdown report (default: `service-status-report.md`);
- `SERVICES_FILTER` — optional comma-separated service filter (default: empty, all services).

Without `GH_TOKEN` the API is queried anonymously, which is rate limited and cannot read the logs.
