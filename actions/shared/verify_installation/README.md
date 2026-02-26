# 🚀 Verify Installation GitHub Action
This Action verifies Kubernetes deployments including status checks, log collection, and test validation.

## Features
- Verifies pod readiness and final status
- Gathers diagnostic data in structured format
- Automatically checks Robot Framework test results
- Configurable attempts with custom timeouts
- Automatic exit on critical failures

## 📌 Inputs

| Name                             | Description                  | Required | Default |
|----------------------------------|------------------------------|----------|---------|
| `namespace`                      | Target Kubernetes namespace  | Yes      | -       |
| `test_completion_max_retries`    | Maximum verification retries | Yes      | 40      |
| `test_completion_retry_interval` | Delay between attempts       | Yes      | 10s     |

## Usage Example

```yaml
name: Verify Deployment

on:
  workflow_dispatch:

jobs:
  verification:
    runs-on: ${{inputs.runner_type}}
    steps:
      - name: Run Deployment Verification
        uses: Netcracker/your-repo/actions/verify-installation@main
        with:
          namespace: 'consul'
          test_completion_max_retries: 30
          test_completion_retry_interval: '15s'
```
