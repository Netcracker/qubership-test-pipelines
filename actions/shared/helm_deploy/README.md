# 🚀 Helm Deploy GitHub Action  
This Action automates Helm install/upgrade services using Helm
## Features
- Checkout service and pipeline repositories
- Namespace creation for new installations
- Creation necessary resources before restricted installation
- Replace Docker image versions in Helm charts for specified components
- Deploy service with specified templates  
- Deploy (install/upgrade) service using Helm
- Deploy with restricted permissions or cluster-admin rights

## 📌 Inputs

| Name               | Required | Default   | Type    | Description                                                                |
|--------------------|----------|-----------|---------|----------------------------------------------------------------------------|
| `deploy_mode`      | Yes      | `install` | string  | Deployment mode: 'install'/'update'                                        |
| `restricted`       | Yes      | `false`   | boolean | Use restricted mode or not (installation by user with restricted rights)   |
| `path_to_template` | Yes      | -         | string  | Path to template file in qubership-test-pipelines repository               |
| `service_branch`   | Yes      | -         | string  | Branch in service repository                                               |
| `service_name`     | Yes      | -         | string  | Helm release name                                                          |
| `repository_name`  | Yes      | -         | string  | Service repository name (without organization prefix)                      |
| `path_to_chart`    | Yes      | -         | string  | Path to Helm chart in service repository                                   |
| `components`       | Yes      | -         | string  | List of components for image updates                                       |
| `namespace`        | Yes      | -         | string  | Kubernetes target namespace                                                |

## Usage Example

```yaml
name: Deploy Service with Helm

on:
  push

jobs:
  helm-deploy:
    runs-on: ${{inputs.runner_type}}
    name: Run helm_deploy action
    steps:
      - name: Run helm_deploy action
        uses: Netcracker/qubership-test-pipelines/actions/shared/helm_deploy@main
        with:
          deploy_mode: 'install'
          restricted: false
          path_to_template: 'templates/consul-service/consul_clean_infra_passport.yml'
          service_branch: 'main'
          service_name: 'consul'
          repository_name: 'qubership-consul'
          path_to_chart: 'charts/helm/consul-service'
          namespace: 'consul'
```
