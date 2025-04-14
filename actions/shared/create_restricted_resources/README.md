# 🚀 Create Restricted Resources Action 
This Action creates resources before restricted installation

## Features
- Creates ClusterRoles, ClusterRoleBindings and CRDs
- Generates client certificates for restricted access
- Creates restricted Role and RoleBinding
- Creates Kubernetes context for restricted user

## 📌 Inputs

| Name              | Required | Description                                           |
|-------------------|----------|-------------------------------------------------------|
| `service_name`    | Yes      | Helm release name                                     |
| `repository_name` | Yes      | Service repository name (without organization prefix) |
| `path_to_chart`   | Yes      | Path to Helm chart in service repository              |
| `namespace`       | Yes      | Target Kubernetes namespace                           |

## Usage Example

```yaml
name: Create Restricted Resources

on:
  workflow_dispatch:

jobs:
  restricted-install:
    runs-on: ubuntu-latest
    steps:
      - name: Create restricted resources
        uses: Netcracker/qubership-test-pipelines/actions/shared/create_restricted_resources@main
        with:
          service_name: 'consul'
          repository_name: 'qubership-consul'
          path_to_chart: 'charts/helm/consul-service'
          namespace: 'consul'
```
