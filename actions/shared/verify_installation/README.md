# 🚀 Verify Installation GitHub Action  
This Action verifies Kubernetes deployments including status checks, log collection, and test validation.

## Features
- Verifies pod readiness and final status
- Gathers diagnostic data in structured format
- Automatically checks Robot Framework test results
- Configurable attempts with custom timeouts
- Automatic exit on critical failures

## 📌 Inputs

| Name           | Description                  | Required | Default |
|----------------|------------------------------|----------|---------|
| `namespace`    | Target Kubernetes namespace  | Yes      | -       |
| `max_attempts` | Maximum verification retries | Yes      | 40      |
| `timeout`      | Delay between attempts       | Yes      | 10s     |
| `check_tests`  | Enable test pod validation   | Yes      | false   |

## Usage Example

```yaml
name: Verify Deployment

on:
  workflow_dispatch:

jobs:
  verification:
    runs-on: ubuntu-latest
    steps:
      - name: Run Deployment Verification
        uses: Netcracker/your-repo/actions/verify-installation@main
        with:
          namespace: 'consul'
          max_attempts: 30
          timeout: '15s'
          check_tests: 'true'