# Quick Start Guide
This mini guide contains an explanation of how to launch an Airflow pipeline for check deployment cases and an explanation of stages and variables that need to be configured before launching.

## How to run Airflow pipeline
This pipeline has been already configured with different deploy cases and stages. 
It's possible to run pipeline for deploy to 3 clouds: `qa_kubernetes`, `fenrir` and `ocp_cert_1`. 

In order to run to `qa_kubernetes` cloud you should uncomment following parameters under `qa_kubernetes configuration` comment:
```
  PREFIX: qa_kubernetes_orchestration
  JENKINS_URL: ''
  JENKINS_USER: ''
  JENKINS_PASS: ''
  CREDS_IN_DEPLOYER: ''
  RESTRICTED_USER_APP: ''
  CLOUD_HOST_OVERALL: ${QA_KUBER_HOST}
  CLOUD_TOKEN_OVERALL: ${QA_KUBER_TOKEN}
  PROJECT: airflow-pipeline
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
  PROJECT: airflow-pipeline
```
For run pipeline to `fenrir` cloud following parameters under `fenrir configuration` comment should be uncommented:
```
  PREFIX: fenrir_orchestration
  JENKINS_URL: ''
  JENKINS_USER: ''
  JENKINS_PASS: ''
  CREDS_IN_DEPLOYER: ''
  RESTRICTED_USER_APP: ''
  CLOUD_HOST_OVERALL: ${FENRIR_KUBER_HOST}
  CLOUD_TOKEN_OVERALL: ${FENRIR_KUBER_TOKEN}
  PROJECT: airflow-pipeline
```

`Pay Attention` only ONE configuration block can be uncommented, others should be commented out.



After committing changes, pipeline will be run automatically.

For run a new pipeline without changes open `CI/CD` -> `Pipelines` in sidebar and click on button `Run Pipeline`. After this select branch `airflow` and click on `Run Pipeline` button again.

## Variables
<!-- markdownlint-disable line-length -->
| Variable        | Description                                                                           |
|-----------------|---------------------------------------------------------------------------------------|
| PREVIOUS_SPRINT | Previous sprint manifest for Deployer.                                            |
| LATEST_SPRINT   | New sprint manifest for Deployer.                                                 |
| N1_RELEASE      | Previous release manifest (n-1, where n – actual release) for Deployer.           |
| N2_RELEASE      | Previous-previous release manifest (n-2, where n – actual release)  for Deployer. |
<!-- markdownlint-enable line-length -->


## Jobs list
<!-- markdownlint-disable line-length -->
| Stage                                      | Job                                                                          | Description                                                                                                   |
|--------------------------------------------|------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------|
| clean_previous_sprint                      | 1-Clean [PREVIOUS_SPRINT] Minimal Dbaas                                      | Clean Deploy job with previous sprint manifest. Dbaas integration (minimal params)                            | 
| upgrade_from_previous_to_latest            | 2-Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT] Dbaas With Git Sync      | Rolling Update job to new manifest from previous sprint. Dbaas integration with params + gitsync              | 
| clean_latest_sprint                        | 3-Clean [LATEST_SPRINT] Dbaas With Git Sync                                  | Clean Deploy with new manifest. Dbaas integration with params + gitsync                                       |
| upgrade_to_latest_diff_params              | 4-Upgrade [LATEST_SPRINT] Diff Params Dbaas With Git Sync                    | Rolling Update with same manifest from previous step, but with changed deployment parameters. Dbaas + gitsync | 
| clean_n1_release                           | 5-Clean [N1_RELEASE]                                                         | Clean Deploy with previous release manifest. Without Dbaas.                                                   | 
| upgrade_from_n1_to_latest                  | 6-Upgrade From [N1_RELEASE] To [LATEST_SPRINT] Version Standrat And Git Sync | Rolling Update from previous release manifest to new manifest. Without Dbaas + gitsync                        |
| clean_n2_release                           | 7-Clean [N2_RELEASE]                                                         | Clean Deploy with previous-previous release manifest (n-2, where n – actual release). Without Dbaas           |
| upgrade_from_n2_to_latest                  | 8-Upgrade From [N2_RELEASE] To [LATEST_SPRINT] Standrat And Rclone           | Rolling Update to new manifest from n-2 manifest. Without Dbaas + rclone                                      |
| clean_previous_sprint_executor             | 9-Clean [PREVIOUS_SPRINT] With Executor                                      | Clean Deploy with previous manifest and k8s executor for worker.                                              |
| upgrade_to_latest_executor                 | 10-Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT] With Executor           | Update Deploy with new manifest and k8s executor for worker.                                                  |
| clean_latest_sprint_executor               | 11-Clean [LATEST_SPRINT] With Executor and DBaaS With R-Clone                | Clean Deploy with new manifest and k8s executor for worker.                                                   | 
| clean_latest_sprint_for_update_to_executor | 12-Clean [LATEST_SPRINT] With Git Sync For Update To Executor                | Clean Deploy with new manifest. Dbaas integration with params + gitsync                                       |
| update_from_previous_to_latest_executor    | 13-Upgrade To [LATEST_SPRINT] With Executor                                  | Update Deploy with new manifest and k8s executor for worker.                                                  |
| clean_previous_sprint_restricted           | 14-Clean [PREVIOUS_SPRINT] Restricted                                        | Restricted clean Deploy with previous manifest. Dbaas integration (minimal params)                            |
| update_from_previous_to_latest_restricted  | 15-Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT] Restricted              | Restricted update Deploy with new manifest. Dbaas integration + gitsync                                       |
| clean_latest_sprint_restricted             | 16-Clean [LATEST_SPRINT] Restricted                                          | Restricted clean Deploy with new manifest. Without Dbaas + rclone                                             | 
| clean_latest_standart_git_sync_ssh         | 17-Clean [LATEST_SPRINT] With Git Sync And SSH                               | Clean Deploy with git sync and SSH                                                                            | 
| update_latest_dbaas_gitsync_connection     | 18-Update [LATEST_SPRINT] With Custom Dbaas GitSync And Connection           | Rolling Update with custom dbaas gitSync and connection                                                       | 
<!-- markdownlint-enable line-length -->
