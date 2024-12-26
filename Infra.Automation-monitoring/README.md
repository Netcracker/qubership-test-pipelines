# Quick Start Guide
This mini guide contains an explanation of how to launch a monitoring pipeline for check deployment cases and an explanation of stages and variables that need to be configured before launching.

## How to run monitoring pipeline
This pipeline has been already configured with different deploy cases and stages. 
It's possible to run pipeline for deploy to 2 clouds: `qa_kubernetes_orchestration` and `ocp_cert_1`. 

In order to run to `qa_kubernetes_orchestration` cloud you should uncomment following parameters under `qa_kubernetes configuration` comment:
```
  PREFIX: qa_kubernetes_orchestration
  JENKINS_URL: ''
  JENKINS_USER: ''
  JENKINS_PASS: ''
  CREDS_IN_DEPLOYER: ''
  RESTRICTED_USER_APP: ''
  CLOUD_HOST_OVERALL: ${QA_KUBER_HOST}
  CLOUD_TOKEN_OVERALL: ${QA_KUBER_TOKEN}
  PROJECT: prometheus-operator
```
For run pipeline to `ocp_cert_1` cloud following parameters under `ocp_cert_1 configuration` comment should be uncommented:
```
  PREFIX: ocp_cert_1
  JENKINS_URL: ''
  JENKINS_USER: ''
  JENKINS_PASS: ''
  CREDS_IN_DEPLOYER: ''
  RESTRICTED_USER_APP: ''
  CLOUD_HOST_OVERALL: ${OCP_CERT_1_HOST}
  CLOUD_TOKEN_OVERALL: ${OCP_CERT_1_TOKEN}
  PROJECT: prometheus-operator
```

`Pay Attention` only ONE configuration block can be uncommented, another should be commented out.



After committing changes, pipeline will be run automatically.

For run a new pipeline without changes open `CI/CD` -> `Pipelines` in sidebar and click on button `Run Pipeline`. After this select branch `monitoring` and click on `Run Pipeline` button again.

## Variables
<!-- markdownlint-disable line-length -->
| Variable                 | Description                                                                          |
|--------------------------|--------------------------------------------------------------------------------------|
| N2_RELEASE    | Previous-previous release manifest (n-2, where n – actual release)  for Deployer |
| N1_RELEASE    | Previous release manifest (n-1, where n – actual release) for Deployer           |
| PREVIOUS_SPRINT  | Previous sprint manifest for Deployer                                            |
| LATEST_SPRINT           | New sprint manifest for Deployer                                                 |
| LATEST_SPRINT_TAG                      | Tag (branch name) name with CRD for new sprint                                       |
| PREVIOUS_SPRINT_TAG                  | Tag (branch name) with CRD for the previous sprint                                   | 
| N1_RELEASE_TAG                  | Tag (branch name) with CRD for the n-1 release                                       |
| N2_RELEASE_TAG                  | Tag (branch name) with CRD for the n-2 release                                       |
| N1_RELEASES              | Enable or disable upgrades from the n-1 release                                      |
| N2_RELEASES              | Enable or disable upgrades from the n-2 release                                      |
<!-- markdownlint-enable line-length -->

## Jobs list
<!-- markdownlint-disable line-length -->
| Stage                                      | Job                                                    | Description                                                                                                                  |
|--------------------------------------------|--------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------|
| vm_clean_previous_sprint                   | 1-Vm Clean [PREVIOUS_SPRINT]                             | Clean Deploy Victoria Metrics with previous sprint manifest                                                                  |
| vm_upgrade_from_previous_sprint_to_latest_sprint                        | 2-Vm Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT]                                 | Rolling Update Victoria Metrics to new manifest from previous sprint                                                         |
| vm_clean_latest                            | 3-Vm Clean [LATEST_SPRINT]                                      | Clean Deploy Victoria Metrics with new manifest                                                                              |
| vm_upgrade_latest_diff_params              | 4-Vm Upgrade [LATEST_SPRINT] Diff Params             | Rolling Update Victoria Metrics with same manifest from previous step, but with changed deployment config                    |
| vm_clean_release_n1                       | 5-Vm Clean [N1_RELEASE]                                 | Clean Deploy Victoria Metrics with previous release manifest                                                                 |
| vm_update_from_n1_to_latest               | 6-Vm Upgrade From [N1_RELEASE] To [LATEST_SPRINT]                | Rolling Update Victoria Metrics from previous release manifest to new manifest                                               |
| vm_clean_release_n2                       | 7-Vm Clean [N2_RELEASE]                                 | Clean Deploy Victoria Metrics with previous-previous release manifest (n-2, where n – actual release)                        |
| vm_update_from_n2_to_latest               | 8-Vm Upgrade From [N2_RELEASE] To [LATEST_SPRINT]                | Rolling Update Victoria Metrics to new manifest from n-2 manifest                                                            |
| vm_clean_previous_sprint_restricted        | 9-Vm Clean [PREVIOUS_SPRINT] Restricted                  | Clean Deploy Victoria Metrics with previous sprint manifest in restricted mode                                               |
| vm_update_to_latest_restricted             | 10-Vm Upgrade [LATEST_SPRINT] Restricted                    | Rolling Update Victoria Metrics to new manifest from previous sprint manifest in restricted mode                             |
| vm_clean_release_n1_restricted            | 11-Vm Clean [N1_RELEASE] Restricted                     | Clean Deploy Victoria Metrics with with previous release manifest in restricted mode                                         |
| vm_update_from_n1_to_latest_restricted    | 12-Vm Upgrade From [N1_RELEASE] To [LATEST_SPRINT] Restricted    | Rolling Update Victoria Metrics from previous release manifest to new manifest in restricted mode                            |
| vm_clean_release_n2_restricted            | 13-Vm Clean [N2_RELEASE] Restricted                     | Clean Deploy Victoria Metrics with previous-previous release manifest (n-2, where n – actual release) in restricted mode     |
| vm_update_from_n2_to_latest_restricted    | 14-Vm Upgrade From [N2_RELEASE] To [LATEST_SPRINT] Restricted    | Rolling Update Victoria Metrics to new manifest from n-2 manifest in restricted mode                                         |
| vm_clean_latest_restricted                 | 15-Vm Clean [LATEST_SPRINT] Restricted                          | Clean Deploy Victoria Metrics with new manifest in restricted mode                                                           |
| clean_previous_sprint_without_components        | 16-Clean [PREVIOUS_SPRINT] W/O Components                 | Deployment without Grafana and node exporter with minimal components                                                         |
| update_to_latest_without_components             | 17-Upgrade To [LATEST_SPRINT] W/O Components                     | Deployment without Grafana and node exporter with minimal components                                                         |
| clean_release_n1_without_components            | 18-Clean [N1_RELEASE] W/O Components                     | Deployment without Grafana and node exporter with minimal components                                                         |
| update_to_latest_from_n1_without_components    | 19-Upgrade From [N1_RELEASE] To [LATEST_SPRINT] W/O Components    | Deployment without Grafana and node exporter with minimal components                                                         |
| clean_release_n2_without_components            | 20-Clean [N2_RELEASE] W/O Components                     | Deployment without Grafana and node exporter with minimal components                                                         |
| update_from_n2_to_latest_without_components    | 21-Upgrade From [N2_RELEASE] To [LATEST_SPRINT] W/O Components    | Deployment without Grafana and node exporter with minimal components                                                         |
| prom_clean_previous_sprint                 | 22-Prom Clean [PREVIOUS_SPRINT]                          | Clean Deploy Prometheus with previous sprint manifest                                                                        |
| prom_update_to_latest                      | 23-Prom Upgrade To [LATEST_SPRINT]                              | Rolling Update Prometheus to new manifest from previous sprint                                                               |
| prom_clean_latest                          | 24-Prom Clean [LATEST_SPRINT]                                   | Clean Deploy Prometheus with new manifest                                                                                    |
| update_from_prom_to_vm                     | 25-Prom Upgrade To VM                                  | Rolling Update from Prometheus to Victoria Metrics                                                                           |
| prom_clean_release_n1                     | 26-Prom Clean [N1_RELEASE]                              | Clean Deploy Prometheus with previous release manifest                                                                       |
| prom_update_from_n1_to_latest             | 27-Prom Upgrade From [N1_RELEASE] To [LATEST_SPRINT]             | Rolling Update Prometheus from previous release manifest to new manifest                                                     |
| prom_clean_release_n2                     | 28-Prom Clean [N2_RELEASE]                              | Clean Deploy Prometheus with previous-previous release manifest (n-2, where n – actual release)                              |
| prom_update_from_n2_to_latest             | 29-Prom Upgrade From [N2_RELEASE] To [LATEST_SPRINT]             | Rolling Update Prometheus to new manifest from n-2 manifest                                                                  |
| prom_clean_previous_sprint_restricted      | 30-Prom Clean [PREVIOUS_SPRINT] Restricted               | Clean Deploy Prometheus with previous sprint manifest in restricted mode                                                     |
| prom_update_to_latest_restricted           | 31-Prom Upgrade To [LATEST_SPRINT] Restricted                   | Rolling Update Prometheus to new manifest from previous sprint in restricted mode                                            |
| prom_clean_release_n1_restricted          | 32-Prom Clean [N1_RELEASE] Restricted                   | Clean Deploy Prometheus with previous release manifest in restricted mode                                                    |
| prom_update_from_n1_to_latest_restricted  | 33-Prom Upgrade From [N1_RELEASE] To [LATEST_SPRINT] Restricted  | Rolling Update Prometheus from previous release manifest to new manifest in restricted mode                                  |
| prom_clean_release_n2_restricted          | 34-Prom Clean [N2_RELEASE] Restricted                   | Clean Deploy Prometheus with previous-previous release manifest (n-2, where n – actual release) in restricted mode           |
| prom_update_from_n2_to_latest_restricted  | 35-Prom Upgrade From [N2_RELEASE] To [LATEST_SPRINT] Restricted  | Rolling Update Prometheus from n-2 release manifest to new manifest in restricted mode                                       |
| prom_clean_latest_restricted               | 36-Prom Clean [LATEST_SPRINT] Restricted                        | Clean Deploy Prometheus with new manifest in restricted mode                                                                 |
| vm_clean_latest_with_vmauth                | 37-Vm Clean With Vmauth                                | Clean Deploy Victoria Metrics with Vmauth                                                                                    |                          