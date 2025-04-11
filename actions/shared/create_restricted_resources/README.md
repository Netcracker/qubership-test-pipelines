# 🚀 Create Restricted Resources Action 
This Action creates resources before restricted installation

## Features
- Creates ClusterRoles, ClusterRoleBindings and CRDs
- Generates client certificates for restricted access
- Creates restricted Role and RoleBinding
- Creates Kubernetes context for restricted user

## 📌 Inputs

| Name              | Description                                           | Required | 
|-------------------|-------------------------------------------------------|----------|
| `service_name`    | Helm release name                                     | Yes      |
| `repository_name` | Service repository name (without organization prefix) | Yes      |
| `path_to_chart`   | Path to Helm chart in service repository              | Yes      |
| `namespace`       | Target Kubernetes namespace                           | Yes      |

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
          path_to_template: 'templates/consul-service/consul_clean_infra_passport.yml'
          service_branch: 'main'
          service_name: 'consul'
          repository_name: 'qubership-consul'
          path_to_chart: 'charts/helm/consul-service'
          namespace: 'consul'