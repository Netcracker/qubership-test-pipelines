#!/usr/bin/env bash
# This script builds the service status report: for every service from the config it analyses
# the last N runs of the service nightly workflow and generates a markdown table with the test
# pipeline version, the state, the links to the failed runs, the failure reasons and the
# durations of the runs.
#
# The analysed nightly workflow is the caller workflow of the service repository, e.g.
#   https://github.com/Netcracker/qubership-consul/actions/workflows/run_nightly_tests.yaml
# The test pipeline version is read from the `uses:` line of that workflow:
#   uses: Netcracker/qubership-test-pipelines/.github/workflows/consul.yaml@<sha> # v1.16.0
#
# Usage:
#   service_status_report.sh [CONFIG_FILE] [REPORT_FILE] [SERVICES_FILTER]
#
#   CONFIG_FILE     - path to the services config (default: workflow-config/service-status.yaml)
#   REPORT_FILE     - path where the markdown report is written (default: service-status-report.md)
#   SERVICES_FILTER - optional comma-separated list of service names to include (default: all)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source-path=SCRIPTDIR source=lib/nightly_status_lib.sh disable=SC1091
source "${SCRIPT_DIR}/lib/nightly_status_lib.sh"

CONFIG_FILE="${1:-workflow-config/service-status.yaml}"
REPORT_FILE="${2:-service-status-report.md}"
SERVICES_FILTER="${3:-}"

if [[ ! -f "${CONFIG_FILE}" ]]; then
    echo "::error::Config file not found: ${CONFIG_FILE}"
    exit 1
fi

# Read the test pipeline version from the caller workflow of the service repository:
#   uses: Netcracker/qubership-test-pipelines/.github/workflows/consul.yaml@<sha> # v1.16.0
# Prints the version from the trailing comment (e.g. "v1.16.0"), or nothing when the
# workflow file or the comment cannot be read.
# Usage: fetch_pipeline_version <repo> <workflow_file> <branch>
fetch_pipeline_version() {
    local repo="$1"
    local workflow_file="$2"
    local branch="$3"
    local content version=""

    content=$(gh api -H "Accept: application/vnd.github.raw" \
        "repos/${repo}/contents/${workflow_file}?ref=${branch}" 2>/dev/null || true)
    if [[ -n "${content}" ]]; then
        version=$(printf '%s\n' "${content}" \
            | grep -m1 -oE 'qubership-test-pipelines/\.github/workflows/[^@[:space:]]+@[0-9a-fA-F]+[[:space:]]*#[[:space:]]*[^[:space:]]+' \
            | sed -E 's/.*#[[:space:]]*//' || true)
    fi
    printf '%s' "${version}"
}

# Format the duration of a run (run_started_at -> updated_at) as "Xh Ym Zs".
# Usage: run_duration <run_json_object>
run_duration() {
    local run_json="$1"
    local started_at updated_at started_epoch updated_epoch

    started_at=$(echo "${run_json}" | jq -r '.run_started_at // empty')
    updated_at=$(echo "${run_json}" | jq -r '.updated_at // empty')
    if [[ -z "${started_at}" || -z "${updated_at}" ]]; then
        echo "-"
        return 0
    fi
    started_epoch=$(date -d "${started_at}" +%s 2>/dev/null || echo "0")
    updated_epoch=$(date -d "${updated_at}" +%s 2>/dev/null || echo "0")
    if [[ "${started_epoch}" -gt 0 && "${updated_epoch}" -ge "${started_epoch}" ]]; then
        format_duration "$((updated_epoch - started_epoch))"
    else
        echo "-"
    fi
}

# Build the links to the failed jobs of a run (one <a> element per failed job).
# Usage: failed_job_links <repo> <run_id> <jobs_json>
failed_job_links() {
    local repo="$1"
    local run_id="$2"
    local jobs_json="$3"

    echo "${jobs_json}" | jq -r \
        --arg base "https://github.com/${repo}/actions/runs/${run_id}/job" \
        '[.jobs[] | select(.status == "completed" and .conclusion == "failure") | "<a href=\"" + $base + "/" + (.id|tostring) + "\">" + (.name | gsub("[|]"; "&#124;")) + "</a>"] | join("<br>")' \
        2>/dev/null || true
}

# Collect the failure reasons of the failed jobs of a run: the error snippet from the job log,
# with the check-run annotations as a fallback (see analyze_failed_job for the log parsing).
# Reasons are joined with <br> and are safe to place inside a markdown table cell.
# Usage: failure_reasons <repo> <jobs_json>
failure_reasons() {
    local repo="$1"
    local jobs_json="$2"
    local job_id check_run_url reason reason_file reasons=""

    while IFS=$'\t' read -r job_id check_run_url; do
        if [[ -z "${job_id}" || "${job_id}" == "null" ]]; then
            continue
        fi
        reason=""
        reason_file=$(mktemp)
        analyze_failed_job "${repo}" "${job_id}" > "${reason_file}" 2>/dev/null || true
        reason=$(<"${reason_file}")
        rm -f "${reason_file}"
        if [[ -z "${reason}" && -n "${check_run_url}" && "${check_run_url}" != "null" ]]; then
            reason=$(gh api "${check_run_url}/annotations" \
                --jq '[.[] | select(.annotation_level == "failure") | .message] | unique | join(" | ")' \
                2>/dev/null || true)
        fi
        if [[ -z "${reason}" ]]; then
            reason="No details available (see the run log)"
        fi
        # Keep the report compact and escape the table separators.
        if [[ ${#reason} -gt 800 ]]; then
            reason="${reason:0:800}…"
        fi
        reason="${reason//$'\n'/<br>}"
        reason="${reason//|/&#124;}"
        if [[ -n "${reasons}" ]]; then
            reasons+="<br>"
        fi
        reasons+="${reason}"
    done < <(echo "${jobs_json}" | jq -r \
        '.jobs[] | select(.status == "completed" and .conclusion == "failure") | [(.id|tostring), (.check_run_url // "")] | @tsv' \
        2>/dev/null || true)

    printf '%s' "${reasons}"
}

# Build the filter set (lowercased) from the optional services input
FILTER_SET=()
if [[ -n "${SERVICES_FILTER}" ]]; then
    IFS=',' read -r -a FILTER_RAW <<< "${SERVICES_FILTER}"
    for item in "${FILTER_RAW[@]}"; do
        FILTER_SET+=("$(echo "${item}" | tr '[:upper:]' '[:lower:]' | tr -d '[:space:]')")
    done
fi

default_runs_count=$(yq -r '.runs_count // 10' "${CONFIG_FILE}")
service_count=$(yq -o=json '.services' "${CONFIG_FILE}" | jq 'length')

# Initialize the report
{
    echo "# Статус nightly-запусков сервисов"
    echo ""
    echo "_Сформировано: $(date -u '+%Y-%m-%d %H:%M:%S UTC')_"
    echo ""
    echo "| Сервис | Версия тестового пайпа | Состояние | Ссылки на запуски | Issue | Комментарий | Длительность запуска |"
    echo "|--------|------------------------|-----------|-------------------|-------|-------------|----------------------|"
} > "${REPORT_FILE}"

for ((i = 0; i < service_count; i++)); do
    name=$(yq -r ".services[${i}].name" "${CONFIG_FILE}")
    repo=$(yq -r ".services[${i}].repository" "${CONFIG_FILE}")
    workflow_file=$(yq -r ".services[${i}].workflow_file" "${CONFIG_FILE}")
    branch=$(yq -r ".services[${i}].branch // \"main\"" "${CONFIG_FILE}")
    runs_count=$(yq -r ".services[${i}].runs_count // ${default_runs_count}" "${CONFIG_FILE}")
    comment=$(yq -r ".services[${i}].comment // \"\"" "${CONFIG_FILE}")
    comment="${comment//|/&#124;}"

    # Apply the optional filter
    if [[ ${#FILTER_SET[@]} -gt 0 ]]; then
        lower_name=$(echo "${name}" | tr '[:upper:]' '[:lower:]')
        matched=false
        for f in "${FILTER_SET[@]}"; do
            if [[ "${f}" == "${lower_name}" ]]; then
                matched=true
                break
            fi
        done
        if [[ "${matched}" == "false" ]]; then
            echo "Skipping ${name} (not in filter)"
            continue
        fi
    fi

    echo "::group::Checking ${name}"
    echo "Repository: ${repo}"
    echo "Workflow file: ${workflow_file}"
    echo "Branch: ${branch}"
    echo "Runs analysed: ${runs_count}"

    pipeline_version=$(fetch_pipeline_version "${repo}" "${workflow_file}" "${branch}")
    workflow_url="https://github.com/${repo}/actions/workflows/${workflow_file}"

    runs_json=""
    if output=$(gh api \
        "repos/${repo}/actions/workflows/${workflow_file}/runs?per_page=${runs_count}&branch=${branch}" \
        --jq '[.workflow_runs[]]' 2>/dev/null); then
        runs_json="${output}"
    else
        echo "::warning::Failed to fetch runs for ${name}"
    fi
    if [[ -z "${runs_json}" || "${runs_json}" == "null" ]]; then
        runs_json="[]"
    fi

    # State: passed runs out of the completed runs of the analysed window
    completed_count=$(echo "${runs_json}" | jq '[.[] | select(.status == "completed")] | length')
    passed_count=$(echo "${runs_json}" | jq '[.[] | select(.status == "completed" and .conclusion == "success")] | length')
    if [[ "${completed_count}" -eq 0 ]]; then
        state_cell="-"
    else
        state_cell="${passed_count}/${completed_count}"
    fi

    latest_duration=$(run_duration "$(echo "${runs_json}" | jq '.[0] // {}')")

    echo "Pipeline version: ${pipeline_version:-unknown}"
    echo "State: ${state_cell}"

    {
        echo "| ${name} | ${pipeline_version} | ${state_cell} | [${workflow_file}](${workflow_url}) | | ${comment} | ${latest_duration} |"
    } >> "${REPORT_FILE}"

    # One extra row per failed run of the analysed window: links to the failed jobs, the
    # failure reasons and the duration of that run.
    while IFS= read -r failed_run; do
        if [[ -z "${failed_run}" ]]; then
            continue
        fi
        run_id=$(echo "${failed_run}" | jq -r '.id')
        run_number=$(echo "${failed_run}" | jq -r '.run_number')
        run_url=$(echo "${failed_run}" | jq -r '.html_url')
        run_dur=$(run_duration "${failed_run}")

        job_links=""
        reasons=""
        jobs_json=$(gh api "repos/${repo}/actions/runs/${run_id}/jobs" 2>/dev/null || true)
        if [[ -n "${jobs_json}" && "${jobs_json}" != "null" ]]; then
            job_links=$(failed_job_links "${repo}" "${run_id}" "${jobs_json}")
            reasons=$(failure_reasons "${repo}" "${jobs_json}")
        fi
        if [[ -z "${job_links}" ]]; then
            job_links="[#${run_number}](${run_url})"
        else
            job_links="${job_links}<br>[#${run_number}](${run_url})"
        fi
        if [[ -z "${reasons}" ]]; then
            reasons="No details available (see the run log)"
        fi
        {
            echo "| | | | ${job_links} | | ${reasons} | ${run_dur} |"
        } >> "${REPORT_FILE}"
        echo "Failed run #${run_number}: ${run_url}"
    done < <(echo "${runs_json}" | jq -c '.[] | select(.status == "completed" and .conclusion != "success")' 2>/dev/null || true)

    echo "::endgroup::"
done

# Append the legend that explains how the table is filled
cat >> "${REPORT_FILE}" <<'LEGEND'

## Как читать отчёт

- **Состояние** — `<прошедших>/<проанализированных>` завершённых запусков nightly-пайплайна
  за последние запуски (количество задаётся в конфиге, по умолчанию 10):
  `10/10` — стабильный, `1..9/10` — нестабильный, `0/10` — не работает.
- **Версия тестового пайпа** — версия `qubership-test-pipelines` из комментария к строке `uses:`
  в caller-воркфлоу сервиса (например `...@<sha> # v1.16.0`); пусто, если прочитать не удалось.
- **Ссылки на запуски** — в строке сервиса ссылка на nightly-воркфлоу, в строках запусков —
  ссылки на упавшие jobs и на сам запуск.
- **Issue** — пока не заполняется.
- **Комментарий** — в строке сервиса примечание из конфига, в строках запусков — причина
  падения (из лога job, при недоступности лога — из аннотаций check-run).
- **Длительность запуска** — в строке сервиса длительность последнего запуска,
  в строках запусков — длительность этого запуска.
LEGEND

echo "::group::Report"
cat "${REPORT_FILE}"
echo "::endgroup::"

# Publish the report to the GitHub Actions step summary if available
if [[ -n "${GITHUB_STEP_SUMMARY:-}" ]]; then
    cat "${REPORT_FILE}" >> "${GITHUB_STEP_SUMMARY}"
fi
