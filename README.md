# qubership-test-pipelines

This repository automates the end-to-end testing qubership services in a Kubernetes cluster using Kind. 
It implements a complete CI/CD lifecycle from infrastructure provisioning to post-deployment verification.

- [Repository Structure](#repository-structure)
- [How to create a test workflow for new service](#how-to-create-a-test-workflow-for-new-service)
- [Workflows list](#workflows-list)
    - [Consul](#consul)

## Repository Structure
```
.github/
├── workflows/                              # Service-specific test workflows
├── actions/                                # Custom GitHub Actions
    ├── shared/                             # Shared actions for all services
        ├── create_cluster
        ├── create_restricted_resources
        ├── helm_deploy
        └── verify_installation
    └── [service]/
        └── helm_deploy_[service]/           # Reuse of shared actions with service specifics   
├── kind-configs/                            # Kind cluster configurations
├── python/                                  # Helper scripts
├── restricted/                              # Resources for restricted installation
└── templates/                               # Service configuration templates
    └── [service]/
        └── [config].yml
```

## How to create a test workflow for new service

1. Add '.github/charts-values-update-config.yaml' (file with images) to service. 
```yaml
charts:
  - name: <repository_name>
    chart_file: <path_to_chart>/Chart.yaml
    values_file: <path_to_values>/values.yaml
    image:
      - ghcr.io/netcracker/<component1_name>:${release}
      - ghcr.io/netcracker/<component2_name>:${release}
      ...
```
2. Add '.github/versions.yaml' (file with old releases) to service.
```yaml
release-2025.1-0.11.1
release-2025.1-0.11.2
```
3. Add '.github/workflows/run_tests.yaml' workflow to service.
Example:
```yaml
name: Run Consul Pipeline

on:
  pull_request:
    types: [opened, synchronize, reopened]
    branches: [main]

jobs:
  Consul-Pipeline:
    uses: Netcracker/qubership-test-pipelines/.github/workflows/<service>.yaml@main
    with:
      service_branch: '${{ github.head_ref || github.ref_name }}'
      versions_file: '.github/versions.yaml'
      pipeline_branch: 'main' #this value must match the value after '@' in 'uses'
```
4. Add service-specific actions to this repository  
Location: 'qubership-test-pipelines/actions/<service>'  
**Example of <service> action**:
```yaml
name: "<Shared action> for <service>"
description: "<description>"
inputs:
  param1:
    description: 'See <shared_action>.param1'
    required: true
    #Dynamic value for <service>
    #for example, path to template with values
  param2:
    description: 'See <shared_action>.param2'
    required: true
    default: 'charts/helm/<service>'
    #Static value for the <service>
    #for example, path to helm chart
runs:
  using: 'composite'
  steps:
    - name: Run <shared action> for <service>
      uses: ./qubership-test-pipelines/actions/shared/<shared_action> 
      with:
        param1: ${{inputs.param1}}
        param2: ${{inputs.param2}}
```
5. Add files with values to 'qubership-test-pipelines/templates/<service>'
6. Add workflow with pipeline to this repository   
Location: 'qubership-test-pipelines/.github/workflows/<service>.yaml'
```yaml
name: <Service> Tests

on:
  workflow_call:
    inputs:
      service_branch:
        required: false
        type: string
      versions_file:
        description: 'Path to versions list file'
        type: string
        required: true
      pipeline_branch:
        description: 'Test pipeline branch name'
        type: string
        required: true
```
7. Add jobs with test deploys to workflow  
If you want to check upgrade of some service, you need to add steps with clean deploy and upgrade to one job.   
**Job Structure Overview**:  
  Step 1: Cluster Creation  
  Step 2: Monitoring Installation (for alert tests)  
  Step 3: Service clean installation  
  Step 4: Validation (logs, events, tests)  
  Step 5: Service upgrade  
  Step 6: Validation
**Example**:
```yaml
jobs:
  Clean-Latest-Upgrade-Diff-Params:
    runs-on: ${{inputs.runner_type}}
    name: Clean [LATEST], Upgrade [LATEST] Diff Params  
    steps:
      - name: Checkout pipeline
        uses: actions/checkout@v4
        with:
          ref: '${{inputs.pipeline_branch}}'
          repository: 'Netcracker/qubership-test-pipelines'
          path: 'qubership-test-pipelines'
      - name: Create cluster
        uses: ./qubership-test-pipelines/actions/shared/create_cluster
      - name: Clean Install <Service> [LATEST]
        uses: ./qubership-test-pipelines/actions/<service>/helm_deploy_<service>
        with:
          path_to_template: '<path to template with service parameters>'
          service_branch: '${{inputs.service_branch}}'
      - name: Verify <Service> installation
        uses: ./qubership-test-pipelines/actions/<service>/verify_installation_<service>
      - name: Update to [LATEST] Version With Diff Params
        uses: ./qubership-test-pipelines/actions/<service>/helm_deploy_<service>
        with:
          path_to_template: '<path to template with service parameters>'
          service_branch: '${{inputs.service_branch}}'
          deploy_mode: upgrade
      - name: Verify <Service> upgrade
        uses: ./qubership-test-pipelines/actions/<service>/verify_installation_<service>
```
## Workflows list
Added workflow for the following services:
- [Consul](https://github.com/Netcracker/qubership-consul)

### Consul

#### Jobs list
<!-- markdownlint-disable line-length -->
| Job                                                       | Name                                                        | Type       | Steps                                                                                             | Description                                                                                                                               |
|-----------------------------------------------------------|-------------------------------------------------------------|------------|---------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------| 
| Clean-Latest-Upgrade-Diff-Params                          | Clean [LATEST], Upgrade [LATEST] Diff Params                | Single Job | Clean Install Consul [LATEST],  Update to [LATEST] Version With Diff Params                       | Clean Deploy with latest release.  Rolling Update with same manifest from previous step, but with changed deployment config               |
| Clean-Previous-Update-To-Latest                           | Clean [PREVIOUS], Update to [LATEST]                        | Matrix     | Clean Install Consul [PREVIOUS],  Update Consul to [LATEST]                                       | Clean Deploy with previous releases from file.  Rolling Update from previous release to latest                                            |
| Clean-Previous-Upgrade-To-Latest-Restricted               | Clean [PREVIOUS] Restricted, Upgrade To [LATEST] Restricted | Single Job | Clean Install Consul [PREVIOUS] in Restricted mode,  Update Consul to [LATEST] in Restricted mode | Clean Deploy job with previous release in restricted mode.  Rolling Update job to latest release from previous release in restricted mode |
| Clean-Latest-Restricted                                   | Clean [LATEST] Restricted                                   | Single Job | Clean Install Consul [LATEST] in Restricted mode                                                  | Clean Deploy with latest release in restricted mode                                                                                       | 
| Clean-WO-Components                                       | Clean [LATEST] W/O Components                               | Single Job | Clean Install Consul [LATEST] W/O Components                                                      | Clean Deploy with latest release without additional components                                                                            |
| Clean-Latest-Full-At-ports-Specifying-Custom-Labels       | Clean [LATEST] Full-AT Ports-specifying Custom-labels       | Single Job | Clean Install Consul [LATEST] Full-At                                                             | Clean Deploy of latest release with Ports specifying for global, servers and clients and with full scope auto-tests                       |
<!-- markdownlint-enable line-length -->
