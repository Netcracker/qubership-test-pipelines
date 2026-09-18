#!/usr/bin/env bash
# This script checks the status of nightly test workflows for platform services.
# It reads the component list from a YAML config, queries the GitHub API for the
# latest run of each component's nightly workflow and generates a markdown report
# with a status table (passed / failed / in progress).
#
# The nightly workflows are reusable workflows from this repository, triggered by
# a caller workflow in the service repository. This script only checks their runs.
#
# Usage:
#   check_nightly_status.sh [CONFIG_FILE] [REPORT_FILE] [COMPONENTS_FILTER]
#
#   CONFIG_FILE       - path to the components config (default: workflow-config/nightly-status.yaml)
#   REPORT_FILE       - path where the markdown report is written (default: nightly-status-report.md)
#   COMPONENTS_FILTER - optional comma-separated list of component names to check (default: all)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source-path=SCRIPTDIR source=lib/nightly_status_lib.sh disable=SC1091
source "${SCRIPT_DIR}/lib/nightly_status_lib.sh"

CONFIG_FILE="${1:-workflow-config/nightly-status.yaml}"
REPORT_FILE="${2:-nightly-status-report.md}"
COMPONENTS_FILTER="${3:-}"

if [[ ! -f "${CONFIG_FILE}" ]]; then
    echo "::error::Config file not found: ${CONFIG_FILE}"
    exit 1
fi

NOW_EPOCH=$(date +%s)

# Build the filter set (lowercased) from the optional components input
FILTER_SET=()
if [[ -n "${COMPONENTS_FILTER}" ]]; then
    IFS=',' read -r -a FILTER_RAW <<< "${COMPONENTS_FILTER}"
    for item in "${FILTER_RAW[@]}"; do
        FILTER_SET+=("$(echo "${item}" | tr '[:upper:]' '[:lower:]' | tr -d '[:space:]')")
    done
fi

component_count=$(yq -o=json '.components' "${CONFIG_FILE}" | jq 'length')

# Initialize the report
{
    echo "# Nightly Workflows Status Report"
    echo ""
    echo "_Generated at: $(date -u '+%Y-%m-%d %H:%M:%S UTC')_"
    echo ""
    echo "| Component | Status | Run | Started (UTC) | Duration | Link | Failed jobs |"
    echo "|-----------|--------|-----|---------------|----------|------|-------------|"
} > "${REPORT_FILE}"

passed_count=0
failed_count=0
in_progress_count=0
no_run_count=0

# Accumulates the "Failure Details" section (per component: failed jobs + reasons).
# Populated only when at least one failed job is detected, appended after the summary.
failure_section=""
# Set by analyze_failed_job(): inner "##[group]" step chain of the failing step (from the log).
JOB_FAIL_PATH=""

for ((i = 0; i < component_count; i++)); do
    name=$(yq -r ".components[${i}].name" "${CONFIG_FILE}")
    repo=$(yq -r ".components[${i}].repository" "${CONFIG_FILE}")
    workflow_file=$(yq -r ".components[${i}].workflow_file" "${CONFIG_FILE}")
    branch=$(yq -r ".components[${i}].branch // \"main\"" "${CONFIG_FILE}")
    lookback_hours=$(yq -r ".components[${i}].lookback_hours // 24" "${CONFIG_FILE}")

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

    api_url="repos/${repo}/actions/workflows/${workflow_file}/runs?per_page=1&branch=${branch}"
    run_json=""
    if output=$(gh api "${api_url}" --jq '.workflow_runs[0]' 2>/dev/null); then
        run_json="${output}"
    else
        echo "::warning::Failed to fetch runs for ${name}"
    fi

    if [[ -z "${run_json}" || "${run_json}" == "null" ]]; then
        status_text="no runs"
        emoji=":grey_question:"
        run_cell="-"
        started_cell="-"
        duration_cell="-"
        failed_jobs_cell="-"
        link_cell="-"
        no_run_count=$((no_run_count + 1))
    else
        run_id=$(echo "${run_json}" | jq -r '.id')
        run_status=$(echo "${run_json}" | jq -r '.status')
        run_conclusion=$(echo "${run_json}" | jq -r '.conclusion // ""')
        run_number=$(echo "${run_json}" | jq -r '.run_number')
        html_url=$(echo "${run_json}" | jq -r '.html_url')
        created_at=$(echo "${run_json}" | jq -r '.created_at')
        created_epoch=$(date -d "${created_at}" +%s 2>/dev/null || echo "0")
        age_hours=$(((NOW_EPOCH - created_epoch) / 3600))

        # Collect the failed job names for this run (if any).
        # Each job is placed on its own line inside the cell (rendered with <br> in markdown).
        # Escape "|" (used in matrix job names) so it does not break the markdown table.
        # Additionally, for the "Failure Details" section, record each failed job together
        # with the failing step name(s) and a failure reason (from the job log, with
        # check-run annotations as fallback).
        failed_jobs_cell="-"
        component_failures=""
        if [[ -n "${run_id}" && "${run_id}" != "null" ]]; then
            jobs_json=$(gh api "repos/${repo}/actions/runs/${run_id}/jobs" 2>/dev/null || echo "")
            if [[ -n "${jobs_json}" && "${jobs_json}" != "null" ]]; then
                # Linked failed job names for the summary table (each name points to the job).
                failed_jobs=$(echo "${jobs_json}" | jq -r \
                    --arg base "https://github.com/${repo}/actions/runs/${run_id}/job" \
                    '[.jobs[] | select(.status == "completed" and .conclusion == "failure") | "<a href=\"" + $base + "/" + (.id|tostring) + "\">" + (.name | gsub("[|]"; "&#124;")) + "</a>"] | join("<br>")' \
                    2>/dev/null || echo "")
                if [[ -n "${failed_jobs}" ]]; then
                    failed_jobs_cell="${failed_jobs}"
                fi

                # For each failed job, derive the failing step name(s) and a failure reason.
                while IFS=$'\t' read -r job_name job_id check_run_url; do
                    [[ -z "${job_name}" ]] && continue
                    # Name of the step(s) that failed inside this job (the "what").
                    failed_steps=$(echo "${jobs_json}" | jq -r --arg jid "${job_id}" \
                        '[.jobs[] | select((.id|tostring) == $jid) | .steps[]? | select(.conclusion == "failure") | .name] | join(", ")' \
                        2>/dev/null || echo "")
                    # Failure reason (the "why"): the real error snippet from the failed job's
                    # log; analyze_failed_job falls back to the check-run annotations (the
                    # "::error::" messages of the steps) when the log only holds a summary
                    # message of the wrapper. It also sets JOB_FAIL_PATH to the step that
                    # carries the cause, which may be an earlier step than the one that failed.
                    reason=""
                    inner_steps=""
                    if [[ -n "${job_id}" && "${job_id}" != "null" ]]; then
                        # Run in the CURRENT shell (NOT a $( ) subshell) so the global
                        # JOB_FAIL_PATH set inside analyze_failed_job survives; capture the
                        # printed snippet through a temp file instead.
                        reason_file=$(mktemp)
                        analyze_failed_job "${repo}" "${job_id}" "${check_run_url}" > "${reason_file}" 2>/dev/null || true
                        inner_steps="${JOB_FAIL_PATH}"
                        reason=$(<"${reason_file}")
                        rm -f "${reason_file}"
                    fi
                    if [[ -z "${reason}" ]]; then
                        reason="No details available (see the run log)"
                    fi
                    # Keep the report compact: truncate long reasons.
                    if [[ ${#reason} -gt 800 ]]; then
                        reason="${reason:0:800}…"
                    fi
                    # Failing step display: prefer the inner (log-detected) step name.
                    fail_step="${inner_steps}"
                    if [[ -z "${fail_step}" ]]; then
                        fail_step="${failed_steps}"
                    fi
                    if [[ -z "${fail_step}" ]]; then
                        fail_step="unknown"
                    fi

                    # Variant A layout: one #### heading per failed job (the whole job name is
                    # a link to the concrete job), then the failing step and the reason in a
                    # fenced code block.
                    job_url="https://github.com/${repo}/actions/runs/${run_id}/job/${job_id}"
                    component_failures+="#### <a href=\"${job_url}\">${job_name}</a>"$'\n'
                    component_failures+=$'\n'
                    component_failures+="**Failing step:** \`${fail_step}\`"
                    if [[ -n "${inner_steps}" && -n "${failed_steps}" && "${inner_steps}" != "${failed_steps}" ]]; then
                        component_failures+=" _(top-level: \`${failed_steps}\`)_"
                    fi
                    component_failures+=$'\n'
                    component_failures+=$'\n'
                    component_failures+="**Reason:**"$'\n'
                    component_failures+=$'\n'
                    component_failures+="\`\`\`text"$'\n'
                    component_failures+="${reason}"$'\n'
                    component_failures+="\`\`\`"$'\n'
                    component_failures+=$'\n'
                done < <(echo "${jobs_json}" | jq -r '.jobs[] | select(.status == "completed" and .conclusion == "failure") | [.name, (.id|tostring), (.check_run_url // "")] | @tsv' 2>/dev/null || true)
            fi
        fi

        # Compute the run duration from run_started_at to updated_at
        run_started_at=$(echo "${run_json}" | jq -r '.run_started_at // empty')
        updated_at=$(echo "${run_json}" | jq -r '.updated_at // empty')
        if [[ -n "${run_started_at}" && -n "${updated_at}" ]]; then
            started_epoch=$(date -d "${run_started_at}" +%s 2>/dev/null || echo "0")
            updated_epoch=$(date -d "${updated_at}" +%s 2>/dev/null || echo "0")
            if [[ "${started_epoch}" -gt 0 && "${updated_epoch}" -ge "${started_epoch}" ]]; then
                duration_seconds=$((updated_epoch - started_epoch))
                duration_cell=$(format_duration "${duration_seconds}")
            else
                duration_cell="-"
            fi
        else
            duration_cell="-"
        fi

        if [[ "${created_epoch}" == "0" || "${age_hours}" -gt "${lookback_hours}" ]]; then
            status_text="no runs in the last ${lookback_hours} h"
            emoji=":grey_question:"
            no_run_count=$((no_run_count + 1))
        elif [[ "${run_status}" == "completed" && "${run_conclusion}" == "success" ]]; then
            status_text="passed"
            emoji=":white_check_mark:"
            passed_count=$((passed_count + 1))
        elif [[ "${run_status}" == "completed" ]]; then
            status_text="failed"
            emoji=":x:"
            failed_count=$((failed_count + 1))
        else
            status_text="in progress"
            emoji=":hourglass_flowing_sand:"
            in_progress_count=$((in_progress_count + 1))
        fi

        run_cell="#${run_number}"
        started_cell="${created_at}"
        link_cell="[#${run_number}](${html_url})"

        # Feed the accumulated per-component failures into the "Failure Details" section.
        # Separate consecutive component blocks with a horizontal rule.
        if [[ -n "${component_failures}" ]]; then
            if [[ -n "${failure_section}" ]]; then
                failure_section+=$'---\n\n'
            fi
            failure_section+="### ${name}"$'\n\n'
            failure_section+="${component_failures}"
        fi
    fi

    echo "Status: ${emoji} ${status_text}"
    echo "::endgroup::"

    {
        echo "| ${name} | ${emoji} ${status_text} | ${run_cell} | ${started_cell} | ${duration_cell} | ${link_cell} | ${failed_jobs_cell} |"
    } >> "${REPORT_FILE}"
done

# Append a summary section
{
    echo ""
    echo "## Summary"
    echo ""
    echo "- :white_check_mark: Passed: **${passed_count}**"
    echo "- :x: Failed: **${failed_count}**"
    echo "- :hourglass_flowing_sand: In progress: **${in_progress_count}**"
    echo "- :grey_question: No runs: **${no_run_count}**"
} >> "${REPORT_FILE}"

# Append the "Failure Details" section (only when at least one failed job was found)
if [[ -n "${failure_section}" ]]; then
    {
        echo ""
        echo "## Failure Details"
        echo ""
        echo "_Per-workflow list of failed jobs with the failing step and a failure reason extracted from the job log (check-run annotations when the log cannot be read)._"
        echo ""
        printf '%s' "${failure_section}"
    } >> "${REPORT_FILE}"
fi

echo "::group::Report"
cat "${REPORT_FILE}"
echo "::endgroup::"

# Publish the report to the GitHub Actions step summary if available
if [[ -n "${GITHUB_STEP_SUMMARY:-}" ]]; then
    cat "${REPORT_FILE}" >> "${GITHUB_STEP_SUMMARY}"
fi
