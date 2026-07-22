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
        with:
          enable-owner-references-permission-enforcement: true
```

The `enable-owner-references-permission-enforcement` input is disabled by default. When enabled, the action uses a Kind configuration that preserves Kind's `NodeRestriction` admission plugin and adds `OwnerReferencesPermissionEnforcement`.
