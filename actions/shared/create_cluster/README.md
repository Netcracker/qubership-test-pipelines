# 🚀 Create Kubernetes cluster GitHub Action  
This Action automates creation of Kubernetes clusters using Kind (Kubernetes in Docker).

## Features
- Creating test cluster using predefined Kind configuration from pipeline repository
- Fixed Kind (v0.25.0) and Kubernetes (v1.32.2) versions

## Usage Example

```yaml
name: Create Kind Cluster

on:
  workflow_dispatch:

jobs:
  create-cluster:
    runs-on: ${{inputs.runner_type}}
    steps:
      - name: Create Kubernetes Cluster
        uses: Netcracker/qubership-test-pipelines/actions/shared/create_cluster@main
```
