# 🚀 Get Certs Action

GitHub Action to extract TLS certificate data from a Kubernetes secret and write
the base64-encoded values to files in the runner's temporary directory.

---

## Features

- Reads a named Kubernetes TLS secret from the specified namespace
- Extracts `ca.crt`, `tls.crt`, and `tls.key` fields from the secret's `data` block
- Fails immediately if any of the three fields is absent or empty
- Writes each base64-encoded value to a separate file in `${{ runner.temp }}`
  for consumption by subsequent steps

---

## 📌 Inputs

| Name | Description | Required | Default |
| --- | --- | --- | --- |
| `service_name` | Helm release name. Accepted for call-site compatibility but not used by any step in this action. | No | - |
| `secret_name` | Name of the Kubernetes secret containing the TLS certificates. Also used as the prefix for the output file names. | Yes | - |
| `namespace` | Kubernetes namespace where the secret is located. | Yes | - |

---

## 📌 Outputs

This action produces no step outputs. Certificate data is written to files in
`${{ runner.temp }}` (see Additional Information for file paths and format).

---

## How it works

The action installs `yq` via `snap`, then reads the named Kubernetes secret from the cluster
and extracts three certificate fields. If any field is missing or empty the action exits with
an error. On success, the three base64-encoded values are written to files under
`${{ runner.temp }}`:

| File | Content |
| --- | --- |
| `${{ runner.temp }}/<secret_name>_ca_crt.txt` | `data["ca.crt"]` — base64-encoded CA certificate |
| `${{ runner.temp }}/<secret_name>_tls_crt.txt` | `data["tls.crt"]` — base64-encoded server certificate |
| `${{ runner.temp }}/<secret_name>_tls_key.txt` | `data["tls.key"]` — base64-encoded private key |

Subsequent steps in the same job can read these files directly. The `runner.temp` directory
is not uploaded as a workflow artifact and is cleaned up at the end of the job.

---

## Additional Information

### Output file format

The values written to disk are the **base64-encoded** strings exactly as they appear in the
Kubernetes secret's `data` block — not the raw PEM content. Callers that need the decoded
PEM must base64-decode the file content:

```bash
base64 --decode < "${{ runner.temp }}/<secret_name>_ca_crt.txt" > ca.crt
base64 --decode < "${{ runner.temp }}/<secret_name>_tls_crt.txt" > tls.crt
base64 --decode < "${{ runner.temp }}/<secret_name>_tls_key.txt" > tls.key
```

### Expected secret structure

The action expects a standard Kubernetes TLS secret with the following `data` keys:

```yaml
apiVersion: v1
kind: Secret
type: kubernetes.io/tls
metadata:
  name: <secret_name>
  namespace: <namespace>
data:
  ca.crt: <base64>
  tls.crt: <base64>
  tls.key: <base64>
```

If any of `ca.crt`, `tls.crt`, or `tls.key` is absent or empty, the action exits with
`exit 1` and a `ERROR: Failed to extract certificates!` message.

### yq installation

The action installs `yq` via `sudo snap install yq` on every run. This requires:

- The runner to support `snap` (standard on Ubuntu GitHub-hosted runners)
- Network access to the snap store
- Approximately 10–30 seconds of additional setup time per run

There is no version pin on the `snap install` command — the latest available `yq` snap is
always installed.

---

## Usage

```yaml
name: Get TLS Certificates

on:
  workflow_dispatch:

jobs:
  get-certs:
    runs-on: ubuntu-latest
    permissions:
      contents: read
    steps:
      - name: Checkout pipeline repo
        uses: actions/checkout@v4
        with:
          path: qubership-test-pipelines

      - name: Get TLS certificates from secret
        uses: Netcracker/qubership-test-pipelines/actions/shared/get_certs@905b88900dc8c14291eaeff4eddcf4d4f734aee1 # v1.9.0
        with:
          secret_name: consul-tls
          namespace: consul

      - name: Use certificate
        shell: bash
        run: |
          base64 --decode < "${{ runner.temp }}/consul-tls_ca_crt.txt" > ca.crt
          echo "CA certificate extracted."
```

---

## Notes

- The full Kubernetes secret YAML (all fields, all data keys) is fetched into a shell
  variable during extraction. The raw secret content passes through the step's shell
  environment but is not echoed to the log by this action.
- Output files contain base64-encoded data, not decoded PEM. Decode with
  `base64 --decode` before passing to tools that expect PEM format.
- Files in `${{ runner.temp }}` persist for the lifetime of the job but are not automatically
  uploaded as workflow artifacts. If certificate data is needed across jobs, upload it
  explicitly (with care given the sensitivity of private key material).
- The `tls.key` file contains the base64-encoded private key. Treat the runner's temp
  directory as sensitive storage and avoid logging its contents.
- Pin to a full 40-character commit SHA with the release tag as a trailing comment, e.g.
  `@905b88900dc8c14291eaeff4eddcf4d4f734aee1 # v1.9.0`. The SHA is the immutable pin; the
  comment shows which release it points to. Tags alone are mutable and can be moved —
  acceptable only when callers explicitly want auto-updates within a minor version. Never
  use `@main` or short SHAs.
