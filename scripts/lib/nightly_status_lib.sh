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
#   clean_window_snippet - strip timestamps/ANSI colors/##[ markers from a log window
#   analyze_failed_job   - detect the failing step and its error snippet
#
# fetch_job_log() and analyze_failed_job() use the GH_TOKEN environment variable.
#
# analyze_failed_job() returns the failing step through the JOB_FAIL_PATH variable, which is
# read by the calling script after the function returns (hence SC2034 is disabled here).
# shellcheck disable=SC2034

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

# Print a cleaned snippet from lines [start,end] of a raw Actions log: strips timestamps and
# ANSI colors, drops ##[ markers, the `shell:`/`env:` header of the step and the colored
# command echo, then prints the FIRST error of the step together with a few context lines.
# The first error is used on purpose: the last lines of a step are usually the summary printed
# by the wrapping composite action (for example "Service was installed with errors!"), while
# the real cause (for example "Resources not ready after 180 retries") comes before it.
# When the step produced no recognizable error, the last <tail> lines are printed instead.
# Usage: clean_window_snippet <raw_file> <start> <end> <tail>
clean_window_snippet() {
    local raw_file="$1"
    local start="$2"
    local end="$3"
    local tail_n="$4"
    awk -v s="${start}" -v e="${end}" -v t="${tail_n}" '
        BEGIN {
            esc = sprintf("%c", 27)
            ansi = esc "\\[[0-9;]*m"
            errpat = "Error|ERROR|❌|Exception|Traceback|panic|fatal|FAILED|Failed to"
            ctx_before = 2
            ctx_after = 3
            in_env = 0
        }
        NR < s || NR > e { next }
        {
            line = $0
            sub(/^[^ ]+ /, "", line)
            had_ansi = (line ~ ansi)
            gsub(ansi, "", line)
            if (had_ansi) next
            if (line ~ /^##\[/) next
            if (line ~ /^shell: / || line == "env:") {
                in_env = (line == "env:")
                next
            }
            # Only the variables of the step env header are dropped, not the step output.
            if (in_env) {
                if (line ~ /^[[:space:]]+[A-Za-z_][A-Za-z0-9_]*: /) next
                in_env = 0
            }
            if (line == "") next
            kept[++n] = line
        }
        END {
            if (n == 0) exit
            first = 0
            for (i = 1; i <= n; i++) {
                if (kept[i] ~ errpat) {
                    first = i
                    break
                }
            }
            if (first > 0) {
                from = first - ctx_before
                if (from < 1) from = 1
                to = first + ctx_after
                if (to > n) to = n
            } else {
                from = n - t + 1
                if (from < 1) from = 1
                to = n
            }
            for (i = from; i <= to; i++) print kept[i]
        }
    ' "${raw_file}"
}

# Analyze a failed job's raw log and produce an error snippet.
#
# Reliability order (structural, no text guessing):
#   1. GitHub appends `##[error]Process completed with exit code N.` right after the output of
#      the step that failed. That step is the run-group whose header
#      (`##[group]Run ...`, typically `##[group]Run # ▶️ <name>`) directly precedes the
#      marker. The FIRST such marker in the log is the root failure; later markers from
#      follow-on `if: always()` steps (e.g. artifact upload, diagnostics) are ignored.
#   2. If no such marker exists, use the first `##[end-action ...outcome=failure` and the
#      display of its paired `##[start-action`.
#   3. Otherwise nothing usable -> the caller falls back to /jobs API + check-run annotations.
#
# On success it sets the global JOB_FAIL_PATH to the failing step display and prints a concise
# error snippet (the "reason") on stdout.
# Usage: analyze_failed_job <repo> <job_id>
analyze_failed_job() {
    local repo="$1"
    local job_id="$2"
    local raw_file info mode
    local display_val start_line end_line

    JOB_FAIL_PATH=""
    raw_file=$(mktemp)
    if ! fetch_job_log "${repo}" "${job_id}" "${raw_file}"; then
        rm -f "${raw_file}"
        return 1
    fi

    # Pass A: find the failing run-group via the first "Process completed" marker, and also
    # record the first failing start/end-action as a fallback.
    info=$(awk '
        {
            line = $0
            sub(/^[^ ]+ /, "", line)
        }
        line ~ /^##\[group\]Run / {
            cur = line
            sub(/^##\[group\]Run /, "", cur)
            sub(/^[^A-Za-z0-9_]+/, "", cur)   # drop leading "# ▶️ " / emoji markers
            curName = cur
            curRunLine = NR
            next
        }
        line ~ /^##\[start-action / {
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
        line ~ /^##\[end-action / && !endFail {
            id = ""
            if (match(line, /id=[^;]*/)) id = substr(line, RSTART + 3, RLENGTH - 3)
            if (line ~ /outcome=failure/ || line ~ /conclusion=failure/) {
                if (id in dispOf) {
                    endFail = 1
                    endDisp = dispOf[id]
                    endStart = startOf[id]
                    endStop = NR - 1
                }
            }
            next
        }
        line ~ /^##\[error\]Process completed with exit code/ && !markerHit {
            markerHit = 1
            markerStop = NR - 1
            markName = curName
            markRunLine = curRunLine
        }
        END {
            if (markerHit && markRunLine > 0) {
                print "MODE=marker"
                print "DISPLAY=" markName
                print "START=" markRunLine
                print "END=" markerStop
            } else if (markerHit) {
                print "MODE=marker"
                print "DISPLAY=" markName
                print "START=0"
                print "END=" markerStop
            } else if (endFail) {
                print "MODE=action"
                print "DISPLAY=" endDisp
                print "START=" endStart
                print "END=" endStop
            } else {
                print "MODE=none"
            }
        }
    ' "${raw_file}")

    mode=$(echo "${info}" | sed -n 's/^MODE=//p')
    if [[ "${mode}" == "marker" || "${mode}" == "action" ]]; then
        display_val=$(echo "${info}" | sed -n 's/^DISPLAY=//p')
        start_line=$(echo "${info}" | sed -n 's/^START=//p')
        end_line=$(echo "${info}" | sed -n 's/^END=//p')
        JOB_FAIL_PATH="${display_val}"
        if [[ "${start_line}" -gt 0 ]]; then
            clean_window_snippet "${raw_file}" "${start_line}" "${end_line}" 12
        else
            # No run-group header known; fall back to the tail before the marker.
            start_line=$((end_line - 40))
            [[ "${start_line}" -lt 1 ]] && start_line=1
            clean_window_snippet "${raw_file}" "${start_line}" "${end_line}" 12
        fi
    fi

    rm -f "${raw_file}"
}
