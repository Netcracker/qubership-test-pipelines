#!/usr/bin/env bash
# Shared helpers for the nightly status scripts. This file is meant to be sourced, not executed:
#
#   SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
#   # shellcheck source=lib/nightly_status_lib.sh
#   source "${SCRIPT_DIR}/lib/nightly_status_lib.sh"
#
# Provided functions:
#   format_duration      - format seconds as "Xh Ym Zs" (omits zero units)
#   fetch_job_log        - download a job's raw log (curl first, gh api as fallback)
#   build_log_index      - index a raw log: run groups, ##[error] messages, retry markers
#   log_find_line        - find the first/last line of a log region matching a regex
#   log_region           - print a cleaned log region (whole range, error + continuations, window)
#   analyze_failed_job   - detect the failing step and its error snippet
#
# fetch_job_log() and analyze_failed_job() use the GH_TOKEN environment variable.
#
# analyze_failed_job() returns the failing step through the JOB_FAIL_PATH variable, which is
# read by the calling script after the function returns (hence SC2034 is disabled here).
#
# The rules below can be overridden from the environment (they are all extended regular
# expressions). They encode the conventions of the composite actions of this repository:
# a step such as "Check job status" only fails at the very end and only summarises the errors
# that earlier steps already reported ("Check service is ready", "Get logs from test pod").
# shellcheck disable=SC2034

# Steps whose output never contains the real cause, only a summary of the steps above them.
SUMMARY_STEPS_REGEX="${SUMMARY_STEPS_REGEX:-Check job status|final-status-check|final status check|Check pipeline status}"

# Steps that carry the diagnostic output, in priority order (the first match wins).
DETAIL_STEPS_REGEX="${DETAIL_STEPS_REGEX:-Check service is ready|Get logs from test pod}"

# Meaningful error lines, in priority order: when one of them is found, only this line (with its
# continuation lines) is reported instead of the first generic error of the step.
REASON_PATTERNS_REGEX="${REASON_PATTERNS_REGEX:-UPGRADE FAILED|INSTALLATION FAILED|Resources not ready after|CR check failed|CR check not successful|Tests failed|Tests not completed|timed out waiting for}"

# A step that is stuck in a retry loop reports the state of the last attempt: the block starts at
# the last "Attempt N/M" line and ends at the error itself.
RETRY_ATTEMPT_REGEX="${RETRY_ATTEMPT_REGEX:-^Attempt [0-9]+/[0-9]+([[:space:]]|$)}"
RETRY_REASON_REGEX="${RETRY_REASON_REGEX:-Resources not ready after|CR check not ready|CR check not successful|Tests not completed}"

# Lines that must never be reported as the reason.
IGNORE_REASON_REGEX="${IGNORE_REASON_REGEX:-Process completed with exit code}"

# Summary messages printed by the wrapping actions: they come from the step that fails, but the
# real cause is reported elsewhere (an earlier step or a check-run annotation).
GENERIC_REASON_REGEX="${GENERIC_REASON_REGEX:-Service was installed with errors!|Job status: failure}"

# Generic error patterns, used when no meaningful pattern matched.
GENERIC_ERROR_REGEX="${GENERIC_ERROR_REGEX:-Error|ERROR|❌|Exception|Traceback|panic|fatal|FAILED|Failed to}"

# Context lines around a generic error, and the number of lines printed when nothing matched.
REASON_CONTEXT_BEFORE="${REASON_CONTEXT_BEFORE:-2}"
REASON_CONTEXT_AFTER="${REASON_CONTEXT_AFTER:-3}"
REASON_TAIL_LINES="${REASON_TAIL_LINES:-12}"

# Format a duration in seconds as "Xh Ym Zs" (omits zero units)
format_duration() {
    local seconds="$1"
    local hours=$((seconds / 3600))
    local minutes=$(((seconds % 3600) / 60))
    local secs=$((seconds % 60))
    local out=""
    if [[ "${hours}" -gt 0 ]]; then
        out="${hours}h "
    fi
    if [[ "${minutes}" -gt 0 || -n "${out}" ]]; then
        out="${out}${minutes}m "
    fi
    out="${out}${secs}s"
    echo "${out}"
}

# Download a failed job's raw log. The /logs endpoint returns a 302 redirect, so curl
# with -L is used first; gh api is kept as a fallback.
# Usage: fetch_job_log <repo> <job_id> <output_file>
# Returns 0 on success, 1 otherwise.
fetch_job_log() {
    local repo="$1"
    local job_id="$2"
    local out="$3"

    if command -v curl >/dev/null 2>&1; then
        if curl -fsSL --retry 2 \
            -H "Accept: application/vnd.github+json" \
            ${GH_TOKEN:+-H "Authorization: Bearer ${GH_TOKEN}"} \
            "https://api.github.com/repos/${repo}/actions/jobs/${job_id}/logs" \
            -o "${out}" 2>/dev/null; then
            return 0
        fi
    fi
    if command -v gh >/dev/null 2>&1; then
        if gh api -H "Accept: text/plain" "repos/${repo}/actions/jobs/${job_id}/logs" > "${out}" 2>/dev/null; then
            return 0
        fi
    fi
    return 1
}

# Print the first check-run annotation that can be used as a reason and return 1 when there is no
# such annotation. The annotations are the "::error::" messages of the steps in chronological
# order, so the first message that is neither the "Process completed with exit code N" marker nor
# a summary message of the wrapper is the real cause.
# Usage: fetch_reason_from_annotations <check_run_url>
fetch_reason_from_annotations() {
    local check_run_url="$1"
    local ignore_re="${IGNORE_REASON_REGEX:-Process completed with exit code}"
    local generic_re="${GENERIC_REASON_REGEX:-}"
    local messages message

    [[ -n "${check_run_url}" && "${check_run_url}" != "null" ]] || return 1
    command -v gh >/dev/null 2>&1 || return 1

    messages=$(gh api "${check_run_url}/annotations" \
        --jq '.[] | select(.annotation_level == "failure") | .message' 2>/dev/null || true)
    [[ -n "${messages}" ]] || return 1

    while IFS= read -r message; do
        message="${message#"${message%%[![:space:]]*}"}"
        [[ -z "${message}" ]] && continue
        [[ "${message}" =~ ${ignore_re} ]] && continue
        if [[ -n "${generic_re}" ]] && [[ "${message}" =~ ${generic_re} ]]; then
            continue
        fi
        printf '%s\n' "${message}"
        return 0
    done <<< "${messages}"
    return 1
}

# Index a raw Actions log. Every index line is "<TAG><TAB>...":
#   GROUP <line> <name>       - "##[group]Run ..." header of a step (name without the markers)
#   ERROR <line> <message>    - "##[error]<message>" line (the message is also an annotation)
#   MARKER <line>             - "##[error]Process completed with exit code N." of the failed step
#   PLAIN <line>              - plain log line that looks like an error
#   ATTEMPT <line>            - "Attempt N/M" line of a retry loop
#   ACTION <start> <stop> <display> - first failing "##[start-action]/##[end-action]" pair
# Usage: build_log_index <raw_file>
build_log_index() {
    awk -v gen_re="${GENERIC_ERROR_REGEX}" -v ignore_re="${IGNORE_REASON_REGEX}" \
        -v attempt_re="${RETRY_ATTEMPT_REGEX}" '
        BEGIN {
            esc = sprintf("%c", 27)
            ansi = esc "\\[[0-9;]*m"
            startFail = 0
        }
        {
            line = $0
            # Strip only the "2026-01-01T00:00:00.0000000Z " prefix of the log line, so that the
            # indentation of the continuation lines of a multi-line error is preserved.
            if (match(line, /^[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[^ ]* /) > 0) {
                line = substr(line, RLENGTH + 1)
            }
            if (line ~ ansi) next
            if (line ~ /^##\[group\]Run /) {
                name = line
                sub(/^##\[group\]Run /, "", name)
                sub(/^[^A-Za-z0-9_]+/, "", name)
                printf "GROUP\t%d\t%s\n", NR, name
                next
            }
            if (line ~ /^##\[start-action /) {
                id = ""; disp = ""
                if (match(line, /id=[^;]*/)) id = substr(line, RSTART + 3, RLENGTH - 3)
                if (match(line, /display=[^;]*/)) disp = substr(line, RSTART + 8, RLENGTH - 8)
                if (id != "" && !(id in seenStart)) {
                    seenStart[id] = 1
                    dispOf[id] = disp
                    startOf[id] = NR
                }
                next
            }
            if (line ~ /^##\[end-action / && !startFail) {
                id = ""
                if (match(line, /id=[^;]*/)) id = substr(line, RSTART + 3, RLENGTH - 3)
                if ((line ~ /outcome=failure/ || line ~ /conclusion=failure/) && (id in dispOf)) {
                    startFail = 1
                    printf "ACTION\t%d\t%d\t%s\n", startOf[id], NR - 1, dispOf[id]
                }
                next
            }
            if (line ~ /^##\[error\]/) {
                msg = line
                sub(/^##\[error\]/, "", msg)
                sub(/^ /, "", msg)
                if (msg ~ ignore_re) {
                    printf "MARKER\t%d\n", NR
                } else {
                    printf "ERROR\t%d\t%s\n", NR, msg
                }
                next
            }
            if (line ~ /^##\[/) next
            if (line ~ attempt_re) {
                printf "ATTEMPT\t%d\n", NR
            }
            if (line ~ gen_re && line !~ ignore_re) {
                printf "PLAIN\t%d\n", NR
            }
        }
    ' "$1"
}

# Print the number of the first (or last) line of [start,end] whose cleaned text matches a regex.
# The "##[error]" prefix is stripped before matching, so the messages of the steps are matched
# like any other text; lines that must never be a reason are skipped.
# Usage: log_find_line <raw_file> <start> <end> <regex> <ignore_regex> [first|last]
log_find_line() {
    local raw_file="$1" start="$2" end="$3" re="$4" ignore_re="$5" order="${6:-first}"
    ignore_re="${ignore_re:-Process completed with exit code}"
    [[ "${start}" -lt 1 ]] && start=1
    [[ "${end}" -lt "${start}" ]] && return 0
    sed -n "${start},${end}p" "${raw_file}" | awk -v off="$((start - 1))" -v re="${re}" \
        -v ignore_re="${ignore_re}" -v order="${order}" '
        BEGIN { esc = sprintf("%c", 27); ansi = esc "\\[[0-9;]*m"; found = 0; printed = 0 }
        {
            line = $0
            if (match(line, /^[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[^ ]* /) > 0) {
                line = substr(line, RLENGTH + 1)
            }
            if (line ~ ansi) next
            if (line ~ /^##\[error\]/) {
                line = substr(line, 10)
                sub(/^ /, "", line)
            } else if (line ~ /^##\[/) next
            if (line ~ ignore_re) next
            if (line ~ re) {
                found = NR + off
                if (order == "first" && printed == 0) {
                    print found
                    printed = 1
                }
            }
        }
        END { if (order == "last" && found > 0 && printed == 0) print found }
    '
}

# Print a cleaned region of a raw log:
#   range    - every line of [start,end] (used for the last attempt of a retry loop, and for the
#              generic error with its context lines)
#   continue - the line <start> and the continuation lines that follow it (multi-line errors)
# Timestamps, ANSI colors, "##[" markers and the `shell:`/`env:` header of a step are stripped.
# Usage: log_region <raw_file> <start> <end> [continue]
log_region() {
    local raw_file="$1" start="$2" end="$3" mode="${4:-range}"
    local ignore_re="${IGNORE_REASON_REGEX:-Process completed with exit code}"
    [[ "${start}" -lt 1 ]] && start=1
    [[ "${end}" -lt "${start}" ]] && return 0
    if [[ "${mode}" == "continue" ]]; then
        end=$((start + 5))
    fi
    sed -n "${start},${end}p" "${raw_file}" | awk -v mode="${mode}" -v ignore_re="${ignore_re}" '
        BEGIN {
            esc = sprintf("%c", 27)
            ansi = esc "\\[[0-9;]*m"
            in_env = 0
            seen = 0
            stop = 0
        }
        {
            line = $0
            had_ts = (match(line, /^[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]T[^ ]* /) > 0)
            if (had_ts) {
                line = substr(line, RLENGTH + 1)
            }
            if (line ~ ansi) next
            if (line ~ /^##\[error\]/) {
                line = substr(line, 10)
                sub(/^ /, "", line)
            } else if (line ~ /^##\[/) next
            if (line ~ /^shell: / || line == "env:") {
                in_env = 1
                next
            }
            # Values of the `env:` header of a step ("  NAME: value") are never part of a reason
            if (line ~ /^[ \t]+[A-Za-z_][A-Za-z0-9_]*: /) next
            in_env = 0
            if (line ~ ignore_re) next
            if (line == "") next
            if (mode == "continue") {
                if (seen == 0) {
                    print line
                    seen = 1
                    next
                }
                if (stop == 0) {
                    # Continuation lines of a multi-line error: indented or bulleted lines, lines
                    # without a timestamp (multi-line output of a command) and YAML-style keys of
                    # a dumped value ("zookeeper-service:").
                    if (line ~ /^[ \t]/ || line ~ /^[-*]/ || line ~ /^[A-Za-z0-9_.-]+:$/ || !had_ts) {
                        print line
                    } else {
                        stop = 1
                    }
                }
                next
            }
            print line
        }
    '
}

# Analyze a failed job's raw log and produce an error snippet.
#
# Step selection (structure of the log, no text guessing):
#   1. The failing step is the run group that directly precedes the first
#      `##[error]Process completed with exit code N.` marker.
#   2. When that step only summarises the pipeline (SUMMARY_STEPS_REGEX) or its own output has no
#      error at all, the reason is looked up in the groups ABOVE it, following the priority of
#      DETAIL_STEPS_REGEX and, as a fallback, the nearest group that has an error. This is what
#      makes a job that fails in "Check job status" report the real cause of "Check service is
#      ready" or "Get logs from test pod". The selected group is also the reported failing step.
#   3. If no such marker exists, the first failing `##[start-action]/##[end-action]` pair is used.
#
# Reason selection (inside the selected step):
#   1. The first line matching REASON_PATTERNS_REGEX (for example "Error: UPGRADE FAILED: ..."),
#      printed with its continuation lines.
#   2. If that line belongs to a retry loop (RETRY_REASON_REGEX), the whole state of the last
#      attempt is printed, starting at the last "Attempt N/M" line.
#   3. Otherwise the first generic error with a few context lines, or the tail of the step.
#
# On success it sets the global JOB_FAIL_PATH to the failing step display and prints a concise
# error snippet (the "reason") on stdout. When the reason would be only a summary message of the
# wrapper, the check-run annotations are used instead.
# Usage: analyze_failed_job <repo> <job_id> [check_run_url]
analyze_failed_job() {
    local repo="$1"
    local job_id="$2"
    local check_run_url="${3:-}"
    local raw_file index_file
    local tag f1 f2 f3
    local -a g_lines=() g_names=() e_lines=() p_lines=()
    local marker_line="" action_display=""
    local total_lines group_count

    JOB_FAIL_PATH=""
    raw_file=$(mktemp)
    if ! fetch_job_log "${repo}" "${job_id}" "${raw_file}"; then
        rm -f "${raw_file}"
        return 1
    fi

    index_file=$(mktemp)
    build_log_index "${raw_file}" > "${index_file}"

    while IFS=$'\t' read -r tag f1 f2 f3; do
        case "${tag}" in
            GROUP)
                g_lines+=("${f1}")
                g_names+=("${f2}")
                ;;
            ERROR) e_lines+=("${f1}") ;;
            PLAIN) p_lines+=("${f1}") ;;
            MARKER) marker_line="${f1}" ;;
            ACTION) action_display="${f3}" ;;
        esac
    done < "${index_file}"

    total_lines=$(wc -l < "${raw_file}")
    group_count=${#g_lines[@]}

    # Line ranges of every group (from its header to the line before the next header)
    local -a g_end=()
    local i j
    for ((i = 0; i < group_count; i++)); do
        if [[ "$((i + 1))" -lt "${group_count}" ]]; then
            g_end+=("$((g_lines[i + 1] - 1))")
        else
            g_end+=("${total_lines}")
        fi
    done

    # Does a group contain an error of its own (an ##[error] message or an error line)?
    group_has_error() {
        local idx="$1"
        local start="${g_lines[idx]}"
        local end="${g_end[idx]}"
        local k
        for ((k = 0; k < ${#e_lines[@]}; k++)); do
            if [[ "${e_lines[k]}" -ge "${start}" && "${e_lines[k]}" -le "${end}" ]]; then
                return 0
            fi
        done
        for ((k = 0; k < ${#p_lines[@]}; k++)); do
            if [[ "${p_lines[k]}" -ge "${start}" && "${p_lines[k]}" -le "${end}" ]]; then
                return 0
            fi
        done
        return 1
    }

    # Does a group contain a *diagnostic* error: an ##[error] message or a line matching the
    # meaningful patterns? This is used to look for the cause in the steps above the failing one,
    # so unrelated output of other steps (git checkout, helm status, ...) is never picked up.
    group_has_detail_error() {
        local idx="$1"
        local start="${g_lines[idx]}"
        local end="${g_end[idx]}"
        local k line
        for ((k = 0; k < ${#e_lines[@]}; k++)); do
            if [[ "${e_lines[k]}" -ge "${start}" && "${e_lines[k]}" -le "${end}" ]]; then
                return 0
            fi
        done
        line=$(log_find_line "${raw_file}" "${start}" "${end}" \
            "${REASON_PATTERNS_REGEX}" "${IGNORE_REASON_REGEX}")
        if [[ -n "${line}" && "${line}" -gt 0 ]]; then
            return 0
        fi
        return 1
    }

    # The step in which the job actually fails
    local fail_idx=-1
    if [[ -n "${marker_line}" ]]; then
        for ((i = 0; i < group_count; i++)); do
            if [[ "${g_lines[i]}" -lt "${marker_line}" ]]; then
                fail_idx="${i}"
            else
                break
            fi
        done
    fi

    # Selection of the step that carries the reason
    local selected_idx=-1
    if [[ "${fail_idx}" -ge 0 ]]; then
        local fail_name="${g_names[fail_idx],,}" summary_re="${SUMMARY_STEPS_REGEX,,}"
        if [[ "${fail_name}" =~ ${summary_re} ]] || ! group_has_error "${fail_idx}"; then
            local -a detail_pats=()
            local pat
            local IFS='|'
            read -r -a detail_pats <<< "${DETAIL_STEPS_REGEX,,}"
            for pat in "${detail_pats[@]}"; do
                for ((i = fail_idx - 1; i >= 0; i--)); do
                    if [[ "${g_names[i],,}" =~ ${pat} ]] && group_has_detail_error "${i}"; then
                        selected_idx="${i}"
                        break
                    fi
                done
                if [[ "${selected_idx}" -ge 0 ]]; then
                    break
                fi
            done
        fi
        if [[ "${selected_idx}" -lt 0 ]]; then
            selected_idx="${fail_idx}"
        fi
        JOB_FAIL_PATH="${g_names[selected_idx]}"
    elif [[ -n "${action_display}" ]]; then
        JOB_FAIL_PATH="${action_display}"
    fi

    # Region in which the reason is searched
    local sel_start=1 sel_end="${total_lines}"
    if [[ "${selected_idx}" -ge 0 ]]; then
        sel_start="${g_lines[selected_idx]}"
        sel_end="${g_end[selected_idx]}"
    elif [[ -n "${marker_line}" ]]; then
        sel_end=$((marker_line - 1))
        sel_start=$((sel_end - 40))
        [[ "${sel_start}" -lt 1 ]] && sel_start=1
    fi

    local reason_line attempt_line generic_line reason_text reason=""
    reason_line=$(log_find_line "${raw_file}" "${sel_start}" "${sel_end}" \
        "${REASON_PATTERNS_REGEX}" "${IGNORE_REASON_REGEX}")

    if [[ -n "${reason_line}" && "${reason_line}" -gt 0 ]]; then
        reason_text=$(log_find_line "${raw_file}" "${reason_line}" "${reason_line}" \
            "${RETRY_REASON_REGEX}" "${IGNORE_REASON_REGEX}" first)
        if [[ -n "${reason_text}" ]]; then
            # The step retried and finally gave up: show the state of the last attempt
            attempt_line=$(log_find_line "${raw_file}" "${sel_start}" "${reason_line}" \
                "${RETRY_ATTEMPT_REGEX}" "${IGNORE_REASON_REGEX}" last)
            if [[ -n "${attempt_line}" && "${attempt_line}" -gt 0 ]]; then
                reason=$(log_region "${raw_file}" "${attempt_line}" "${reason_line}")
            else
                reason=$(log_region "${raw_file}" "${reason_line}" "${reason_line}" continue)
            fi
        else
            # Multi-line errors (for example "Error: UPGRADE FAILED: ..." of helm)
            reason=$(log_region "${raw_file}" "${reason_line}" "${reason_line}" continue)
        fi
    else
        generic_line=$(log_find_line "${raw_file}" "${sel_start}" "${sel_end}" \
            "${GENERIC_ERROR_REGEX}" "${IGNORE_REASON_REGEX}")
        if [[ -n "${generic_line}" && "${generic_line}" -gt 0 ]]; then
            reason=$(log_region "${raw_file}" "$((generic_line - REASON_CONTEXT_BEFORE))" \
                "$((generic_line + REASON_CONTEXT_AFTER))")
        else
            reason=$(log_region "${raw_file}" "$((sel_end - REASON_TAIL_LINES + 1))" "${sel_end}")
        fi
    fi

    # A summary message of the wrapper is not a useful reason: the check-run annotations hold the
    # "::error::" messages of the steps in chronological order, so the first meaningful one is used.
    local annotation_reason
    if [[ -z "${reason}" ]] || { [[ -n "${GENERIC_REASON_REGEX}" ]] && [[ "${reason}" =~ ${GENERIC_REASON_REGEX} ]]; }; then
        annotation_reason=$(fetch_reason_from_annotations "${check_run_url}" || true)
        if [[ -n "${annotation_reason}" ]]; then
            reason="${annotation_reason}"
        fi
    fi

    if [[ -n "${reason}" ]]; then
        printf '%s\n' "${reason}"
    fi

    rm -f "${raw_file}" "${index_file}"
}
