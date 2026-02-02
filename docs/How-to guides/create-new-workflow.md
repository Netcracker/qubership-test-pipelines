# How to create a test workflow for new service

1. Add '.github/helm-charts-release-config.yaml' (file with images) to service. 
If it is not possible to add file to service project, then add it to 'qubership-test-pipelines/release_configs/<service>/helm-charts-release-config.yaml'
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


