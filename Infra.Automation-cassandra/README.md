# Quick Start Guide
This mini guide contains an explanation of how to launch a Cassandra pipeline for check deployment cases and an explanation of stages and variables that need to be configured before launching.

## How to run cassandra pipeline
This pipeline has been already configured with different deploy cases and stages. 
It's possible to run pipeline for deploy to 2 clouds: `qa_kubernetes_orchestration` and `ocp_cert_1`. 

In order to run to `qa_kubernetes_orchestration` cloud you should uncomment following parameters under `qa_kubernetes_orchestration configuration` comment:
```
  PREFIX: qa_kubernetes_orchestration
  JENKINS_URL: ''
  JENKINS_USER: ''
  JENKINS_PASS: ''
  CREDS_IN_DEPLOYER: ''
  RESTRICTED_USER_APP: ''
  CLOUD_HOST_OVERALL: ${QA_KUBER_HOST}
  CLOUD_TOKEN_OVERALL: ${QA_KUBER_TOKEN}
  PROJECT: cassandra
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
  PROJECT: cassandra
```

`Pay Attention` only ONE configuration block can be uncommented, another should be commented out.



After committing changes, pipeline will be run automatically.

For run a new pipeline without changes open `CI/CD` -> `Pipelines` in sidebar and click on button `Run Pipeline`. After this select branch `cassandra` and click on `Run Pipeline` button again.

## Variables
<!-- markdownlint-disable line-length -->
| Variable                         | Description                                                                          |
|----------------------------------|--------------------------------------------------------------------------------------|
| PREVIOUS_SPRINT                  | Previous sprint manifest for Deployer                                            |
| LATEST_SPRINT                    | New sprint manifest for Deployer                                                 |
| N1_RELEASE                       | Previous release manifest (n-1, where n – actual release) for Deployer           |
| N2_RELEASE                       | Previous-previous release manifest (n-2, where n – actual release)  for Deployer |
| CASSANDRA_4_1                    | Manifest for update from 4.0 to 4.1 version                                          |
| VAULT_URL                        | Vault URL                                                                            | 
| VAULT_TOKEN                      | Vault token. Related Vault jobs will be created only if this value is not equal ""   |
| KEY_VALUE_FORMAT                 | Variable defines deployment config format                                            |
| LATEST_SPRINT_TAG                | Tag (branch name) name with CRD for new sprint                                       |
| PREVIOUS_SPRINT_TAG              | Tag (branch name) with CRD for previous sprint                                       |
<!-- markdownlint-enable line-length -->

if KEY_VALUE_FORMAT != "true" jobs are available with deployment config in format:
```
|
  cassandra='
    install: true
    deploymentSchema:
      dataCenters:
        - name: dc1
          replicas: 3
          seeds: 1
          storage:            
            size: 4Gi
            storageClasses:
              - csi-cinder-sc-delete
  ';
  ...
```

if KEY_VALUE_FORMAT == "true" jobs are available with deployment config in format:
```
|
  operator.resources.requests.cpu=200m;
  operator.resources.requests.memory=256Mi;
  operator.resources.limits.cpu=200m;
  operator.resources.limits.memory=256Mi;
  ...
```

## Jobs list
<!-- markdownlint-disable line-length -->
| Stage                                 | Job                                                    | Description                                                                                                    | Job is avaliable                                    |
|---------------------------------------|--------------------------------------------------------|----------------------------------------------------------------------------------------------------------------|-----------------------------------------------------|
| clean_previous_sprint                 | 1-Clean [PREVIOUS_SPRINT]                              | Clean Deploy job with previous sprint manifest                                                                 | only if variable `KEY_VALUE_FORMAT` != "true"       | 
| upgrade_from_previous_sprint_to_latest_sprint                 | 2-Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT]                                  | Rolling Update job to new manifest from previous sprint                                                        | only if variable `KEY_VALUE_FORMAT` != "true"       |
| clean_latest_sprint                   | 3-Clean [LATEST_SPRINT]                                      | Clean Deploy with new manifest                                                                                 | only if variable `KEY_VALUE_FORMAT` != "true"       |
| upgrade_latest_diff_params            | 4-Upgrade [LATEST_SPRINT] Diff Params                      | Rolling Update with same manifest from previous step, but with changed deployment config                       | only if variable `KEY_VALUE_FORMAT` != "true"       |
| clean_n1_release                      | 5-Clean [N1_RELEASE]                         | Clean Deploy with previous release manifest                                                                    | only if variable `KEY_VALUE_FORMAT` != "true"       |
| upgrade_from_n1_release_to_latest_sprint         | 6-Upgrade From [N1_RELEASE] To [LATEST_SPRINT]                      | Rolling Update from previous release manifest to new manifest                                                  | only if variable `KEY_VALUE_FORMAT` != "true"       |
| clean_n2_release                     | 7-Clean [N2_RELEASE]                              | Clean Deploy with previous-previous release manifest (n-2, where n – actual release)                           | only if variable `KEY_VALUE_FORMAT` != "true"       |
| upgrade_from_n2_release_to_latest_sprint         | 8-Upgrade From [N2_RELEASE] To [LATEST_SPRINT]                     | Rolling Update to new manifest from n-2 manifest                                                               | only if variable `KEY_VALUE_FORMAT` != "true"       |
| clean_latest_not_default_creds               | 9-Clean [LATEST_SPRINT] With Not Default Creds                           | Clean Deploy with not default creds                                                                            | only if variable `KEY_VALUE_FORMAT` != "true"       |
| clean_latest_without_backup_dbaas            | 10-Clean [LATEST_SPRINT] W/O Backup And Dbaas                         | Clean Deploy without backup and dbaas                                                                          | only if variable `KEY_VALUE_FORMAT` != "true"       |
| update_latest_with_reaper                    | 11-Update [LATEST_SPRINT] With Reaper                                     | Rolling Update with reaper                                                                                     | only if variable `KEY_VALUE_FORMAT` != "true"       |
| clean_latest_with_custom_configuration       | 12-Clean [LATEST_SPRINT] With Custom Configurations                       | Clean Deploy with custom configurations                                                                        | only if variable `KEY_VALUE_FORMAT` != "true"       |
| clean_latest_backup_s3                       | 13-Clean [LATEST_SPRINT] With Backuper On S3                              | Clean Deploy with backuper on S3                                                                               | only if variable `KEY_VALUE_FORMAT` != "true"       |
| latest_sprint_scaling                     | 14-Check [LATEST_SPRINT] Scaling Case                           | Clean Deploy with scaling config and Rolling Update with changed scaling config                                | only if variable `KEY_VALUE_FORMAT` != "true"       |
| upgrade_latest_sprint_tls                     | 15-Upgrade [LATEST_SPRINT] From Non-TLS To TLS                           |  Clean Deploy of latest sprint version with TLS disabled and Rolling Update to latest sprint version with TLS enabled                              | only if variable `KEY_VALUE_FORMAT` != "true"       |
| clean_latest_sprint_tls                        | 16-Clean [LATEST_SPRINT] TLS                               | Clean Deploy with TLS                                                                                          | only if variable `KEY_VALUE_FORMAT` != "true"       |
| clean_latest_sprint_vault                      | 17-Clean [LATEST_SPRINT] Vault                             | Clean Deploy with Vault                                                                                        | only if variable `VAULT_TOKEN` isn't empty          |
| clean_latest_sprint_vault_tls                  | 18-Clean [LATEST_SPRINT] Vault And TLS                     | Clean Deploy with Vault and TLS                                                                                | only if variable `VAULT_TOKEN` isn't empty          |
| clean_previous_sprint_restricted      | 19-Clean [PREVIOUS_SPRINT] Restricted                       | Clean Deploy with previous sprint manifest in restricted mode                                                  | only if variable `$RESTRICTED_USER_APP` isn't empty |
| update_from_previous_sprint_to_latest_sprint_restricted  | 20-Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT] Restricted                  | Rolling Update to new manifest from previous sprint manifest in restricted mode                                | only if variable `$RESTRICTED_USER_APP` isn't empty |
| clean_latest_sprint_restricted      | 21-Clean [LATEST_SPRINT] Restricted                       | Clean Deploy with new manifest in restricted mode                                                              | only if variable `$RESTRICTED_USER_APP` isn't empty |
| update_to_4_1_version                 | Update To 4.1 Version                                  | Rolling Update from 4.0 to 4.1 version  
| clean_latest_sprint_multiusers                 | 23-Clean [LATEST_SPRINT] multiUsers                                  | Clean Deploy with multiUsers                                                                         | only if variable `$CASSANDRA_4_1` isn't empty       |
| clean_previous_sprint                    | 24-Clean [PREVIOUS_SPRINT] Key Value Parameters            | Clean Deploy job with previous sprint manifest and key-value deployment config                                 | only if variable `KEY_VALUE_FORMAT` == "true"       |
| upgrade_from_previous_sprint_to_latest_sprint                 | 25-Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT] Key Value Parameters             | Rolling Update job to new manifest from previous sprint with key-value deployment config                       | only if variable `KEY_VALUE_FORMAT` == "true"       |
| clean_latest_sprint                     | 26-Clean [LATEST_SPRINT] Key Value Parameters                 | Clean Deploy with new manifest and key-value deployment config                                                 | only if variable `KEY_VALUE_FORMAT` == "true"       |
| upgrade_latest_diff_params | 27-Upgrade [LATEST_SPRINT] Diff Params Key Value Parameters | Rolling Update with same manifest from previous step, but with changed deployment config (in key-value format) | only if variable `KEY_VALUE_FORMAT` == "true"       |
| clean_n1_release                | 28-Clean [N1_RELEASE] Key Value Parameters    | Clean Deploy with previous release manifest and key-value deployment config                                    | only if variable `KEY_VALUE_FORMAT` == "true"       |
| upgrade_from_n1_release_to_latest_sprint         | 29-Upgrade From [N1_RELEASE] To [LATEST_SPRINT] Key Value Parameters | Rolling Update from previous release manifest to new manifest with key-value deployment config                 | only if variable `KEY_VALUE_FORMAT` == "true"       |
<!-- markdownlint-enable line-length -->

