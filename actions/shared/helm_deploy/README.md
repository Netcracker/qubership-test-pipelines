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

| Name               | Description                                                                | Required | Default   | Type    |
|--------------------|----------------------------------------------------------------------------|----------|-----------|---------|
| `deploy_mode`      | Deployment mode: 'install'/'update'                                        | Yes      | `install` | string  |
| `restricted`       | Use restricted mode or not (installation by user with restricted rights)   | Yes      | `false`   | boolean |
| `path_to_template` | Path to template file in qubership-test-pipelines repository               | Yes      | -         | string  |
| `service_branch`   | Branch in service repository                                               | Yes      | -         | string  |
| `pipeline_branch`  | Branch in qubership-test-pipelines repository                              | Yes      | `main`    | string  |
| `service_name`     | Helm release name                                                          | Yes      | -         | string  |
| `repository_name`  | Service repository name (without organization prefix)                      | Yes      | -         | string  |
| `path_to_chart`    | Path to Helm chart in service repository                                   | Yes      | -         | string  |
| `components`       | List of components for image updates                                       | Yes      | -         | string  |
| `namespace`        | Kubernetes target namespace                                                | Yes      | -         | string  |


## Usage Example

```yaml
name: Deploy Service with Helm

on:
  push

jobs:
  helm-deploy:
    runs-on: ubuntu-latest
    name: Run helm_deploy action
    steps:
      - name: Run helm_deploy action
        uses: Netcracker/qubership-test-pipelines/actions/shared/helm_deploy@main
        with:
          deploy_mode: 'install'
          restricted: 'false'
          path_to_template: 'templates/consul-service/consul_clean_infra_passport.yml'
          service_branch: 'main'
          pipeline_branch: 'main'
          service_name: 'consul'
          repository_name: 'qubership-consul'
          path_to_chart: 'charts/helm/consul-service'
          components: 'statusProvisioner,integrationTests'
          namespace: 'consul'