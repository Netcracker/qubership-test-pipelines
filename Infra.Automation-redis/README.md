# Quick Start Guide
This mini guide contains an explanation of how to launch a Redis pipeline for check deployment cases and an explanation of stages and variables that need to be configured before launching.

## How to run Redis pipeline
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
  PROJECT: redis-test
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
  CLOUD_TOKEN_OVERALL: sha256~6uEozMa1nOT8_eePFx6c59Bh1jlnxm_PXXTzvMyQdDA
  PROJECT: redis-test
```

`Pay Attention` only ONE configuration block can be uncommented, another should be commented out.



After committing changes, pipeline will be run automatically.

For run a new pipeline without changes open `CI/CD` -> `Pipelines` in sidebar and click on button `Run Pipeline`. After this select branch `redis` and click on `Run Pipeline` button again.

## Variables
<!-- markdownlint-disable line-length -->
| Variable            | Description                                                                           |
|---------------------|---------------------------------------------------------------------------------------|
| PREVIOUS_SPRINT     | Previous sprint manifest for Deployer.                                            |
| LATEST_SPRINT       | New sprint manifest for Deployer.                                                 |
| N1_RELEASE          | Previous release manifest (n-1, where n – actual release) for Deployer.           |
| N2_RELEASE          | Previous-previous release manifest (n-2, where n – actual release)  for Deployer. |
| VAULT_URL           | Vault URL                                                                             | 
| VAULT_TOKEN         | Vault token. Related Vault jobs will be created only if this value is not equal ""    |
| LATEST_SPRINT_TAG    | Tag (branch name) name with CRD for new sprint                                        |
| PREVIOUS_SPRINT_TAG | Tag (branch name) with CRD for previous sprint                                        |
<!-- markdownlint-enable line-length -->


## Jobs list
<!-- markdownlint-disable line-length -->
| Stage                                     | Job                                                             | Description                                                                                   |
|-------------------------------------------|-----------------------------------------------------------------|-----------------------------------------------------------------------------------------------|
| clean_previous_sprint                     | 1-Clean [PREVIOUS_SPRINT]                                       | Clean Deploy job with previous sprint manifest.                                               | 
| upgrade_from_previous_to_latest           | 2-Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT]             | Rolling Update job to new manifest from previous sprint.                                      | 
| clean_latest_sprint                       | 3-Clean [LATEST_SPRINT]                                         | Clean Deploy with new manifest.                                                               | 
| upgrade_to_latest_diff_params             | 4-Upgrade [LATEST_SPRINT] Diff Params                           | Rolling Update with same manifest from previous step, but with changed deployment parameters. | 
| clean_n1_release                          | 5-Clean [N1_RELEASE]                                            | Clean Deploy with previous release manifest                                                   | 
| upgrade_from_n1_to_latest                 | 6-Upgrade From [N1_RELEASE] To [LATEST_SPRINT]                  | Rolling Update from previous release manifest to new manifest.                                | 
| clean_n2_release                          | 7-Clean [N2_RELEASE]                                            | Clean Deploy with previous-previous release manifest (n-2, where n – actual release).         | 
| upgrade_from_n2_to_latest                 | 8-Upgrade From [N2_RELEASE] To [LATEST_SPRINT]                  | Rolling Update to new manifest from n-2 manifest.                                             | 
| clean_latest_sprint_tls                   | 9-Clean [LATEST_SPRINT] TLS                                     | Clean Deploy with new manifest and enabled TLS.                                               | 
| clean_latest_sprint_vault                 | 10-Clean [LATEST_SPRINT] Vault                                  | Clean Deploy with new manifest and Vault integration.                                         | 
| clean_latest_sprint_vault_tls             | 11-Clean [LATEST_SPRINT] Vault TLS                              | Clean Deploy with new manifest with enabled TLS and Vault.                                    | 
| clean_latest_sprint_without_dbaas         | 12-Clean [LATEST_SPRINT] Without Dbaas Or Backup                | Clean Deploy with minimal set of parameters.                                                  | 
| clean_latest_sprint_non_default_creds     | 13-Clean [LATEST_SPRINT] Non Default Creds                      | Clean Deploy with new manifest and not default creds.                                         | 
| clean_previous_sprint_restricted          | 14-Clean [PREVIOUS_SPRINT] Restricted                           | Clean Deploy job with previous sprint manifestin restricted mode                              | 
| update_from_previous_to_latest_restricted | 15-Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT] Restricted | Restricted rolling Update to new manifest from previous sprint.                               | 
| clean_latest_sprint_restricted            | 16-Clean [LATEST_SPRINT] Restricted                             | Restricted clean Deploy with new manifest.                                                    |
<!-- markdownlint-enable line-length -->
