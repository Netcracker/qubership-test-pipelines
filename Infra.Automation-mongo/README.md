# Quick Start Guide
This mini guide contains an explanation of how to launch a MongoDB pipeline for check deployment cases and an explanation of stages and variables that need to be configured before launching.

## How to run MongoDB pipeline
This pipeline has been already configured with different deploy cases and stages. 
It's possible to run pipeline for deploy to 2 clouds: `qa_kubernetes` and `ocp_cert_1`. 

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
  PROJECT: mongo-test
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
  PROJECT: mongo-test
```

`Pay Attention` only ONE configuration block can be uncommented, another should be commented out.



After committing changes, pipeline will be run automatically.

For run a new pipeline without changes open `CI/CD` -> `Pipelines` in sidebar and click on button `Run Pipeline`. After this select branch `redis` and click on `Run Pipeline` button again.

## Variables
<!-- markdownlint-disable line-length -->
| Variable              | Description                                                                           |
|-----------------------|---------------------------------------------------------------------------------------|
| PREVIOUS_SPRINT       | Previous sprint manifest with mongodb for Deployer.                               |
| PREVIOUS_SUPPL_SPRINT | Previous sprint manifest with mongodb-services for Deployer.                      |
| LATEST_SPRINT         | New sprint manifest with mongodb for Deployer.                                    |
| LATEST_SUPPL_SPRINT   | New sprint manifest with mongodb-services for Deployer.                           |
| N1_RELEASE            | Previous release manifest (n-1, where n – actual release) for Deployer.           |
| N2_RELEASE            | Previous-previous release manifest (n-2, where n – actual release)  for Deployer. |
| LATEST_SPRIN_TAG      | Tag (branch name) name with CRD for new sprint                                        |
| PREVIOUS_SPRINT_TAG   | Tag (branch name) with CRD for previous sprint                                        |
| MONGO_6               | Version 6.x of MongoDB for migrate procedure                                          |
| VAULT_URL             | Vault URL                                                                             | 
| VAULT_TOKEN           | Vault token. Related Vault jobs will be created only if this value is not equal ""    |
<!-- markdownlint-enable line-length -->


## Jobs list
<!-- markdownlint-disable line-length -->
| Stage                                         | Job                                                            | Description                                                                                   |
|-----------------------------------------------|----------------------------------------------------------------|-----------------------------------------------------------------------------------------------|
| clean_previous_sprint                         | 1-Clean [PREVIOUS_SPRINT]                                      | Clean Deploy job with previous sprint manifest.                                               | 
| upgrade_from_previous_sprint_to_latest_sprint | 2-Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT]            | Rolling Update job to new manifest from previous sprint.                                      | 
| clean_latest                                  | 3-Clean [LATEST_SPRINT]                                        | Clean Deploy with new manifest.                                                               |
| update_to_latest_sprint_diff_params           | 4-Upgrade [LATEST_SPRINT] Diff Params                          | Rolling Update with same manifest from previous step, but with changed deployment parameters. | 
| clean_previous_for_migration                  | 4.1-Clean Previous Version Before Migrat                       | Clean Deploy job with previous sprint manifest for check migration                            | 
| update_to_mongo6                              | 4.3-Update To Mongo 6 Version                                  | Migration to higher 6.x version of MongoDB                                                    | 
| update_to_mongo7                              | 4.4-Update To Mongo 7 Version                                  | Migration to higher 7.x version of MongoDB                                                    | 
| clean_previous_restricted                     | 5-Clean [PREVIOUS_SPRINT] Restricted                           | Restricted clean Deploy job with previous sprint manifest.                                    | 
| update_to_latest_restricted                   | 6-Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT] Restricted | Restricted rolling Update to new manifest from previous sprint.                               |
| clean_latest_restricted                       | 7-Clean [LATEST_SPRINT] Restricted                             | Restricted clean Deploy with new manifest.                                                    |
| clean_n1_release                              | 8-Clean [N1_RELEASE]                                           | Clean Deploy with previous release manifest                                                   | 
| update_to_current_release_app                 | 9-Upgrade From [N1_RELEASE] To [LATEST_SPRINT]                 | Rolling Update from previous release manifest to new manifest.                                |
| clean_n2_release                              | 10-Clean [N2_RELEASE]                                          | Clean Deploy with previous-previous release manifest (n-2, where n – actual release).         |
| upgrade_from_n2_to_latest_sprint              | 11-Upgrade From [N2_RELEASE] To [LATEST_SPRINT]                | Rolling Update to new manifest from n-2 manifest.                                             |
| clean_latest_not_default_creds                | 12-Clean [LATEST_SPRINT] Not Default Creds                     | Clean deploy new version with not default creds                                               |
| clean_latest_custom_config                    | 13-Clean [LATEST_SPRINT] Custom Config                         | Clean deploy new version with custom configuration                                            |
| clean_latest_backup_s3                        | 14-Clean [LATEST_SPRINT] Backuper On S3                        | Clean deploy new version with s3 integration in backup                                        |
| clean_latest_without_dbaas_or_backup          | 15-Clean [LATEST_SPRINT] Without Dbaas Or Backup               | Clean deploy new version with minimal set of components                                       |
| clean_latest_single_schema                    | 16-Clean [LATEST_SPRINT] Single Schema                         | Clean deploy new version in single scheme                                                     |
| clean_latest_arbiter_schema                   | 17-Clean [LATEST_SPRINT] Arbiter Schema                        | Clean deploy new version in arbiter scheme                                                    |
| clean_latest_simple_schema                    | 18-Clean [LATEST_SPRINT] Simple Schema                         | Clean deploy new version in simple scheme                                                     |
| upgrade_from_non_tls_to_tls                   | 19-Upgrade [LATEST_SPRINT] From Non-TLS To TLS                 | Rolling Update From Non-TLS To TLS                                                            |
| clean_latest_tls                              | 20-Clean [LATEST_SPRINT] TLS                                   | Clean Deploy with new manifest and enabled TLS.                                               |
| clean_latest_vault                            | 21-Clean [LATEST_SPRINT] Vault                                 | Clean Deploy with new manifest and Vault integration.                                         |
| clean_latest_vault_tls                        | 22-Clean [LATEST_SPRINT] Vault TLS                             | Clean Deploy with new manifest with enabled TLS and Vault.                                    |
| clean_latest_multiusers                        | 23-Clean [LATEST_SPRINT] multiUsers                            | Clean Deploy with multiUsers.                                                                 |
<!-- markdownlint-enable line-length -->
