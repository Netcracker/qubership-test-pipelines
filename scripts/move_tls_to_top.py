#!/usr/bin/env python3
"""
Move tls flag from inside install/upgrade blocks to job level in workflow-config YAML files.
Only add tls for jobs that actually had it. Add it only once per job.
"""

import re
import os

CONFIG_DIR = "workflow-config"


def get_job_indent(line):
    """Get the indent of a list item marker like '  - name:' or '  - purpose:'."""
    m = re.match(r"^(\s*)-\s", line)
    return len(m.group(1)) if m else None


def is_job_start(line):
    """Check if a line starts a new job (list item with name/purpose)."""
    return bool(re.match(r"^\s+-\s+(name|purpose):", line))


def fix_yaml(content: str) -> str:
    """Parse the YAML as lines, detect job boundaries, move tls to job level where needed."""
    lines = content.splitlines()
    result = []
    i = 0
    n = len(lines)

    while i < n:
        line = lines[i]
        if is_job_start(line):
            job_indent = get_job_indent(line)
            # Collect all lines for this job
            job_lines = [line]
            i += 1
            while i < n:
                next_line = lines[i]
                # Empty lines and comments belong to the current job
                if next_line.strip() == "" or next_line.strip().startswith("#"):
                    job_lines.append(next_line)
                    i += 1
                    continue
                # A new job at same indent level ends this job
                if is_job_start(next_line) and get_job_indent(next_line) == job_indent:
                    break
                job_lines.append(next_line)
                i += 1

            processed = _process_job(job_lines, job_indent)
            result.extend(processed)
        else:
            result.append(line)
            i += 1

    return "\n".join(result)


def _process_job(job_lines, job_indent):
    """Process a single job's lines. Return modified lines."""
    text = "\n".join(job_lines)

    # Find tls inside install/upgrade blocks (at 6+ spaces indent within the job)
    # The install/upgrade content is at job_indent + 4 spaces (usually 6)
    inner_indent = job_indent + 4
    tls_pattern = re.compile(r"^ {" + str(inner_indent) + r",}tls:\s*(.*)", re.MULTILINE)
    tls_matches = tls_pattern.findall(text)

    if not tls_matches:
        return job_lines

    # Get unique tls values
    tls_vals = set(v.strip() for v in tls_matches)
    tls_val = tls_vals.pop() if tls_vals else "false"

    # Remove tls lines from inside install/upgrade blocks
    clean_lines = [l for l in job_lines if not re.match(r"^ {" + str(inner_indent) + r",}tls:", l)]

    # Insert tls at job level (job_indent + 2 spaces = 4) before first install:/upgrade:
    insert_pos = None
    for idx, l in enumerate(clean_lines):
        stripped = l.strip()
        if stripped in ("install:", "upgrade:", "migrate:"):
            insert_pos = idx
            break

    if insert_pos is not None:
        tls_line = " " * (job_indent + 2) + f"tls: {tls_val}"
        clean_lines.insert(insert_pos, tls_line)

    return clean_lines


def main():
    for fname in sorted(os.listdir(CONFIG_DIR)):
        if not fname.endswith(".yaml"):
            continue
        fpath = os.path.join(CONFIG_DIR, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            original = f.read()

        fixed = fix_yaml(original)

        if fixed != original:
            with open(fpath, "w", encoding="utf-8", newline="") as f:
                f.write(fixed)
            print(f"Fixed: {fpath}")
        else:
            print(f"No change: {fpath}")


if __name__ == "__main__":
    main()
