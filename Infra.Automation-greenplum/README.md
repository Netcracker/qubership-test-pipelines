# Quick Start Guide
This mini guide contains an explanation of how to launch a Greenplum pipeline for check deployment cases and an explanation of stages and variables that need to be configured before launching.

## How to run greenplum pipeline
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
  PROJECT: greenplum
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
  CLOUD_TOKEN_OVERALL: sha256~7iKH7-1HbWh9VxnXW8PsMlgyb0zrHLoAJJOo3B4DLto
  PROJECT: greenplum
```

`Pay Attention` only ONE configuration block can be uncommented, another should be commented out.



After committing changes, pipeline will be run automatically.

For run a new pipeline without changes open `CI/CD` -> `Pipelines` in sidebar and click on button `Run Pipeline`. After this select branch `cassandra` and click on `Run Pipeline` button again.

## Variables
<!-- markdownlint-disable line-length -->
| Variable         | Description                                                                          |
|------------------|--------------------------------------------------------------------------------------|
| N2_RELEASE | Previous-previous release manifest (n-2, where n – actual release)  for Deployer |
| N1_RELEASE  | Previous release manifest (n-1, where n – actual release) for Deployer           |
| PREVIOUS_SPRINT      | Previous sprint manifest for Deployer                                            |
| LATEST_SPRINT      | New sprint manifest for Deployer                                                 |
| LATEST_SPRINT_TAG              | Tag (branch name) name with CRD for new sprint                                       |
| PREVIOUS_SPRINT_TAG          | Tag (branch name) with CRD for previous sprint                                       |
<!-- markdownlint-enable line-length -->


## Jobs list
<!-- markdownlint-disable line-length -->
| Stage                            | Job                                                         | Description                                                                              | Job is avaliable                            |
|----------------------------------|-------------------------------------------------------------|------------------------------------------------------------------------------------------|---------------------------------------------|
| clean_previous_sprint            | 1-Clean [PREVIOUS_SPRINT]                         | Clean Deploy job with previous sprint manifest                                           |                                             |
| ugrate_from_previous_to_latest                 | 2-Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT]                     | Rolling Update job to new manifest from previous sprint                                  |                                             |
| clean_latest                     | 3-Clean [LATEST_SPRINT]                           | Clean Deploy with new manifest                                                           |                                             |
| upgrade_latest_diff_params       | 4-Upgrade [LATEST_SPRINT] Diff Params | Rolling Update with same manifest from previous step, but with changed deployment config |                                             |
| clean_n1_release                   | 5-Clean [N1_RELEASE]                       | Clean Deploy with previous release manifest                                              |                                             |
| upgrade_from_n1_to_latest   | 6-Upgrade From [N1_RELEASE] To [LATEST_SPRINT]       | Rolling Update from previous release manifest to new manifest                            |                                             |
| clean_n2_release               | 7-Clean [N2_RELEASE]                            | Clean Deploy with previous-previous release manifest (n-2, where n – actual release)     |                                             |
| upgrade_from_n2_to_latest            | 8-Upgrade From [N2_RELEASE] To [LATEST_SPRINT]                     | Rolling Update to new manifest from n-2 manifest                                         |                                             |
| clean_latest_minimal             | 9-Clean [LATEST_SPRINT] Minimal                          | Clean Deploy with new manifest and minimal deployment config                             |                                             |
| clean_previous_sprint_restricted     | 10-Clean [PREVIOUS_SPRINT] Restricted             | Clean Deploy with previous sprint manifest in restricted mode                            | if variable RESTRICTED_USER_APP isn't empty |
| update_from_previous_to_latest_restricted | 11-Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT] Restricted        | Rolling Update to new manifest from previous sprint manifest in restricted mode          | if variable RESTRICTED_USER_APP isn't empty |
| clean_latest_sprint_restricted     | 12-Clean [LATEST_SPRINT] Restricted             | Clean Deploy with new manifest in restricted mode                                        | if variable RESTRICTED_USER_APP isn't empty |
<!-- markdownlint-enable line-length -->
