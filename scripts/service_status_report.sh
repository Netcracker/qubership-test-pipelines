#!/usr/bin/env bash
# This script builds the service status report: for every service from the config it analyses
# the last N runs of the service nightly workflow, writes the state of those runs on a line above
# the table and then, for every failed run, a group row with the link to the run and the duration
# of that run, followed by one row per failed job with the link to the job, the failing step and
# the reason taken from the job log (the same way the nightly status check does).
#
# The analysed nightly workflow is the caller workflow of the service repository, e.g.
#   https://github.com/Netcracker/qubership-consul/actions/workflows/run_nightly_tests.yaml
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

# Append one row per failed job of a run: the link to the job, the failing step and the reason.
# The rows of a run always follow the group row with the link to that run, so the failed jobs of
# different runs are separated. The duration is not repeated here: it belongs to the whole run and
# is reported in the group row only.
# Usage: emit_failed_job_rows <repo> <jobs_json>
emit_failed_job_rows() {
    local repo="$1"
    local jobs_json="$2"
    local job_name job_id job_url check_run_url job_link failed_steps inner_step step_cell
    local reason reason_file

    while IFS=$'\t' read -r job_name job_id job_url check_run_url; do
        if [[ -z "${job_id}" || "${job_id}" == "null" ]]; then
            continue
        fi
        if [[ -z "${job_url}" || "${job_url}" == "null" ]]; then
            job_url="https://github.com/${repo}/actions/jobs/${job_id}"
        fi
        job_link="<a href=\"${job_url}\">${job_name//|/\&#124;}</a>"
        # Top-level steps of the job that failed (from the /jobs API), used as a fallback.
        failed_steps=$(echo "${jobs_json}" | jq -r --arg jid "${job_id}" \
            '[.jobs[] | select((.id|tostring) == $jid) | .steps[]? | select(.conclusion == "failure") | .name] | join(", ")' \
            2>/dev/null || true)

        # The reason comes from the job log, with the check-run annotations as a fallback.
        # analyze_failed_job also sets JOB_FAIL_PATH to the inner step detected in the log; it
        # runs in the CURRENT shell (not in a subshell) so that JOB_FAIL_PATH survives, and the
        # printed snippet is captured through a temp file instead.
        reason=""
        inner_step=""
        reason_file=$(mktemp)
        analyze_failed_job "${repo}" "${job_id}" > "${reason_file}" 2>/dev/null || true
        inner_step="${JOB_FAIL_PATH}"
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
        # Keep the report compact and make the text safe for a markdown table cell.
        if [[ ${#reason} -gt 800 ]]; then
            reason="${reason:0:800}…"
        fi
        reason="${reason//$'\n'/<br>}"
        reason="${reason//|/\&#124;}"

        step_cell="${inner_step}"
        if [[ -z "${step_cell}" ]]; then
            step_cell="${failed_steps}"
        fi
        if [[ -z "${step_cell}" ]]; then
            step_cell="unknown"
        fi
        step_cell="\`${step_cell//|/\&#124;}\`"
        if [[ -n "${inner_step}" && -n "${failed_steps}" && "${inner_step}" != "${failed_steps}" ]]; then
            step_cell+=" _(top-level: \`${failed_steps//|/\&#124;}\`)_"
        fi

        printf '| %s | %s | %s | |\n' \
            "${job_link}" "${step_cell}" "${reason}" \
            >> "${REPORT_FILE}"
    done < <(echo "${jobs_json}" | jq -r \
        '.jobs[] | select(.status == "completed" and .conclusion == "failure") | [.name, (.id|tostring), (.html_url // ""), (.check_run_url // "")] | @tsv' \
        2>/dev/null || true)
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
default_lookback_days=$(yq -r '.lookback_days // 10' "${CONFIG_FILE}")
service_count=$(yq -o=json '.services' "${CONFIG_FILE}" | jq 'length')

# Initialize the report
{
    echo "# Service Status Report"
    echo ""
    echo "_Generated at: $(date -u '+%Y-%m-%d %H:%M:%S UTC')_"
    echo ""
} > "${REPORT_FILE}"

for ((i = 0; i < service_count; i++)); do
    name=$(yq -r ".services[${i}].name" "${CONFIG_FILE}")
    repo=$(yq -r ".services[${i}].repository" "${CONFIG_FILE}")
    workflow_file=$(yq -r ".services[${i}].workflow_file" "${CONFIG_FILE}")
    branch=$(yq -r ".services[${i}].branch // \"main\"" "${CONFIG_FILE}")
    runs_count=$(yq -r ".services[${i}].runs_count // ${default_runs_count}" "${CONFIG_FILE}")
    lookback_days=$(yq -r ".services[${i}].lookback_days // ${default_lookback_days}" "${CONFIG_FILE}")
    note=$(yq -r ".services[${i}].note // \"\"" "${CONFIG_FILE}")
    note="${note//|/\&#124;}"
    note="${note//$'\n'/<br>}"

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
    echo "Runs analysed: up to ${runs_count} runs of the last ${lookback_days} days"

    workflow_url="https://github.com/${repo}/actions/workflows/${workflow_file}"

    # Only the most recent runs are requested and anything older than the lookback window is
    # dropped, so the report can never show a failure of an old run.
    window_start=$(date -u -d "${lookback_days} days ago" '+%Y-%m-%dT%H:%M:%SZ' 2>/dev/null || echo "")

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
    elif [[ -n "${window_start}" ]]; then
        runs_json=$(echo "${runs_json}" | jq --arg since "${window_start}" '[.[] | select(.created_at >= $since)]')
    fi
    if [[ "$(echo "${runs_json}" | jq 'length')" -eq 0 ]]; then
        echo "::warning::No nightly runs in the last ${lookback_days} days for ${name}"
    fi

    # State: passed runs out of the completed runs of the analysed window
    completed_count=$(echo "${runs_json}" | jq '[.[] | select(.status == "completed")] | length')
    passed_count=$(echo "${runs_json}" | jq '[.[] | select(.status == "completed" and .conclusion == "success")] | length')
    if [[ "${completed_count}" -eq 0 ]]; then
        state_cell="-"
    else
        state_cell="${passed_count}/${completed_count}"
    fi

    echo "State: ${state_cell}"

    # The service line goes above the table: the service name links to the nightly workflow and
    # the state of the analysed window is written next to it.
    {
        echo "## [${name}](${workflow_url}): ${state_cell}"
        echo ""
    } >> "${REPORT_FILE}"
    if [[ -n "${note}" ]]; then
        {
            echo "_${note}_"
            echo ""
        } >> "${REPORT_FILE}"
    fi

    # The table is written only when the analysed window has failed runs; its header is written
    # once per service, before the first group row.
    table_started=false

    # One group row per failed run of the analysed window, every group row followed by the rows
    # of the failed jobs of that run.
    while IFS= read -r failed_run; do
        if [[ -z "${failed_run}" ]]; then
            continue
        fi
        run_id=$(echo "${failed_run}" | jq -r '.id')
        run_number=$(echo "${failed_run}" | jq -r '.run_number')
        run_url=$(echo "${failed_run}" | jq -r '.html_url')
        run_date=$(echo "${failed_run}" | jq -r '.created_at' | cut -dT -f1)
        run_dur=$(run_duration "${failed_run}")
        # The run link carries the run number and the date of the run.
        run_link="[#${run_number} (${run_date})](${run_url})"

        if [[ "${table_started}" == "false" ]]; then
            {
                echo "| Links to failed jobs | Failing step | Reason | Duration |"
                echo "|----------------------|--------------|--------|----------|"
            } >> "${REPORT_FILE}"
            table_started=true
        fi
        # The group row with the link to the failed run and the duration of that run: a markdown
        # table has no merged cells, so the link goes into the first cell and the other cells stay
        # empty.
        printf '| %s | | | %s |\n' "${run_link}" "${run_dur}" >> "${REPORT_FILE}"

        jobs_json=$(gh api "repos/${repo}/actions/runs/${run_id}/jobs" 2>/dev/null || true)
        if [[ -n "${jobs_json}" && "${jobs_json}" != "null" ]]; then
            emit_failed_job_rows "${repo}" "${jobs_json}"
        else
            echo "::warning::Failed to fetch jobs of run #${run_number} for ${name}"
            printf '| | unknown | No details available (see the run log) | |\n' >> "${REPORT_FILE}"
        fi
        echo "Failed run #${run_number} (${run_date}): ${run_url}"
    done < <(echo "${runs_json}" | jq -c '.[] | select(.status == "completed" and .conclusion != "success")' 2>/dev/null || true)

    # Keep a blank line between the table of a service and the heading of the next one. A service
    # without failed jobs already ends with the blank line written after its heading.
    if [[ "${table_started}" == "true" ]]; then
        echo "" >> "${REPORT_FILE}"
    fi

    echo "::endgroup::"
done

# Append the legend that explains how the report is filled
cat >> "${REPORT_FILE}" <<'LEGEND'
## How to read the report

Every service has a line above its table with the state of the analysed window:
`<passed>/<analysed>` completed nightly runs (the number of runs is set in the config, 10 by
default), where `10/10` is stable, `1..9/10` unstable and `0/10` not working. The service name
links to the nightly workflow and the note from the config is printed below it. Runs that are
still in progress are not counted, so the denominator can be smaller than the configured number
of runs. A service without failed runs has no table at all.

- **Links to failed jobs** — the first row of a group is the link to the failed run
  (`#<number> (<date>)`); the rows below it are the failed jobs of that run, every job linked to
  its job page. Failed jobs of different runs are always in different groups. Markdown tables have
  no merged cells, so the run link is written into the first cell of the group row.
- **Failing step** — the step of the job that failed (the inner step detected in the log, with the
  top-level step from the API in parentheses when they differ).
- **Reason** — the error snippet of the failed step (from the job log, with the check-run
  annotations as a fallback).
- **Duration** — filled in only in the group row of a run, because it is the duration of the whole
  run and not of a single job; the job rows leave the column empty. Rendered as `Xh Ym Zs`.
LEGEND

echo "::group::Report"
cat "${REPORT_FILE}"
echo "::endgroup::"

# Publish the report to the GitHub Actions step summary if available
if [[ -n "${GITHUB_STEP_SUMMARY:-}" ]]; then
    cat "${REPORT_FILE}" >> "${GITHUB_STEP_SUMMARY}"
fi
