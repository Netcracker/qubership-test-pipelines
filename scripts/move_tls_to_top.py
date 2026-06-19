#!/usr/bin/env python3
"""Move `tls` from inside install:/upgrade: blocks to top level in workflow-config YAML files."""
import re, os, sys

config_dir = "workflow-config"

for fname in sorted(os.listdir(config_dir)):
    if not fname.endswith((".yaml", ".yml")):
        continue
    fpath = os.path.join(config_dir, fname)
    with open(fpath, "r") as f:
        content = f.read()

    # Find all tls inside install/upgrade blocks (6-space indent)
    matches = list(re.finditer(r"^      tls: (true|false)$", content, re.MULTILINE))
    if not matches:
        continue

    # Determine combined value
    combined = any(m.group(1) == "true" for m in matches)
    tls_val = "true" if combined else "false"

    # Remove tls from inside blocks
    content = re.sub(r"\n      tls: (true|false)", "", content)

    # Insert tls at job level before 'install:' or 'upgrade:' in each job
    # Only add before the first occurrence in each job
    content = re.sub(
        r"^(\s{4})(install:|upgrade:)",
        f"    tls: {tls_val}\n\\g<1>\\g<2>",
        content,
        flags=re.MULTILINE,
    )

    with open(fpath, "w", newline="") as f:
        f.write(content)

    print(f"  {fname}: tls={tls_val} ({len(matches)} occurrences)")

print("Done!")
