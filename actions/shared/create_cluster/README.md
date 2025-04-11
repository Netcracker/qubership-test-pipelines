# 🚀 Create Kubernetes cluster GitHub Action  
This Action automates creation of Kubernetes clusters using Kind (Kubernetes in Docker).

## Features
- Creating test cluster using predefined Kind configuration from pipeline repository
- Fixed Kind (v0.25.0) and Kubernetes (v1.32.2) versions

## 📌 Inputs

| Name              | Description                                        | Required | Default  |
|-------------------|----------------------------------------------------|----------|----------|
| `pipeline_branch` | Branch name in qubership-test-pipelines repository | Yes      | `main`   |

## Usage Example

```yaml
name: Create Kind Cluster

on:
  workflow_dispatch:

jobs:
  create-cluster:
    runs-on: ubuntu-latest
    steps:
      - name: Create Kubernetes Cluster
        uses: Netcracker/qubership-test-pipelines/actions/shared/create_cluster@main
        with:
          pipeline_branch: 'test_branch'