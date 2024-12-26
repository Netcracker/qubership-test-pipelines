## Quick Start Guide
This mini guide contains an explanation of how to launch pipelines for check deployment cases and an explanation of stages and variables that need to be configured before launching.

## How to run pipelines
All pipelines have been already configured with different deploy cases and stages. 
It's possible to run pipelines for deploy to 2 clouds: `qa_kubernetes` and `ocp_cert_1`. 

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
  PROJECT: consul-service
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
  PROJECT: consul-service
```

`Pay Attention` only ONE configuration block can be uncommented, another should be commented out.



After committing changes, pipeline will be run automatically.

For run a new pipeline without changes open `CI/CD` -> `Pipelines` in sidebar and click on button `Run Pipeline`. After this select branch `Core_Framework` and click on `Run Pipeline` button again.

## Variables
<!-- markdownlint-disable line-length -->
| Variable            | Description                                                                         |
|---------------------|-------------------------------------------------------------------------------------|
| N2_RELEASE          | Previous-previous release manifest (n-2, where n – actual release) for Deployer | 
| N1_RELEASE          | Previous release manifest (n-1, where n – actual release) for Deployer          | 
| PREVIOUS_SPRINT     | Previous sprint manifest for Deployer                                           | 
| LATEST_SPRINT       | Latest sprint manifest for Deployer                                             | 
| PREVIOUS_3PARTY     | Previous 3-party version manifest for Deployer                                  | 
| LATEST_SPRINT_TAG   | Tag (branch name) name with CRD for new sprint                                      | 
| PREVIOUS_SPRINT_TAG | Tag (branch name) name with CRD for previous sprint                                 | 
<!-- markdownlint-enable line-length -->

## Jobs list
<!-- markdownlint-disable line-length -->
| Stage                                                    | Job                                                              | Description                                                                                                                  |
|----------------------------------------------------------|------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------|
| clean_latest_sprint_infra_passport                         | 1-Clean [LATEST_SPRINT] Infra Passport                           | Clean Deploy with latest sprint manifest using infra passport parameters only                                                |
| clean_previous_sprint                                      | 2-Clean [PREVIOUS_SPRINT]                                        | Clean Deploy job with previous sprint manifest                                                                               | 
| upgrade_from_previous_sprint_to_latest_sprint              | 3-Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT]              | Rolling Update job to latest sprint manifest from previous sprint                                                            | 
| clean_latest_sprint                                        | 4-Clean [LATEST_SPRINT]                                          | Clean Deploy with latest sprint manifest                                                                                     | 
| upgrade_latest_sprint_diff_params                          | 5-Upgrade [LATEST_SPRINT] Diff Params                            | Rolling Update with same manifest from previous step, but with changed deployment config                                     |
| clean_n1_release                                           | 6-Clean [N1_RELEASE]                                             | Clean Deploy with previous release manifest                                                                                  | 
| upgrade_from_n1_release_to_latest_sprint                   | 7-Upgrade From [N1_RELEASE] To [LATEST_SPRINT]                   | Rolling Update from previous release manifest to latest sprint manifest                                                      | 
| clean_n2_release                                           | 8-Clean [N2_RELEASE]                                             | Clean Deploy with previous-previous release manifest (n-2, where n – actual release)                                         | 
| upgrade_from_n2_release_to_latest_sprint                   | 9-Upgrade From [N2_RELEASE] To [LATEST_SPRINT]                   | Rolling Update to latest sprint manifest from n-2 manifest                                                                   | 
| clean_previous_sprint_restricted                           | 10-Clean [PREVIOUS_SPRINT] Restricted                            | Clean Deploy job with previous sprint manifest in restricted mode                                                            |
| upgrade_from_previous_sprint_to_latest_sprint_restricted   | 11-Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT] Restricted  | Rolling Update job to latest sprint manifest from previous sprint in restricted mode                                         |
| clean_latest_sprint_restricted                             | 12-Clean [LATEST_SPRINT] Restricted                              | Clean Deploy with latest sprint manifest in restricted mode                                                                  | 
| clean_latest_sprint_w/o_components                         | 13-Clean [LATEST_SPRINT] W/O Components                          | Clean Deploy with latest sprint manifest without additional components                                                       |
| upgrade_latest_sprint_all_components_s3_drd                | 14-Upgrade [LATEST_SPRINT] All Components S3 DRD                 | Rolling Update with same manifest from previous step, but with enabled all components, S3 and DRD                            |
| clean_latest_sprint_pv_s3                                  | 15-Clean [LATEST_SPRINT] PV S3                                   | Clean Clean Deploy with latest sprint manifest with hostpath PV and S3                                                       | 
| clean_latest_sprint_without_clients                        | 16-Clean [LATEST_SPRINT] Without Clients                         | Clean Deploy with latest sprint manifest without clients                                                                     | 
| upgrade_latest_sprint_drd_s3                               | 17-Upgrade [LATEST_SPRINT] DRD S3                                | Update with same manifest from previous step, but with clients, DRD and S3                                                   | 
| upgrade_latest_sprint_drd_s3_tls                           | 18-Upgrade [LATEST_SPRINT] DRD S3 TLS                            | Rolling Update to same manifest from previous step with enabled TLS, DRD and S3                                              | 
| clean_latest_sprint_drd_s3_tls                             | 19-Clean [LATEST_SPRINT] DRD S3 TLS                              | Clean Deploy of latest sprint version with DRD, S3 and enabled TLS using cert-manager                                        | 
| clean_latest_sprint_tls-certs                              | 20-Clean [LATEST_SPRINT] DRD S3 TLS-certs                        | Clean Deploy of latest sprint version with DRD, S3 and enabled TLS using specified in deployment parameters certificates     |
| clean_previous_3party                                      | 21-Clean [PREVIOUS_3PARTY]                                       | Clean Deploy with previous 3-party version manifest                                                                          |
| migration_from_previous_3party_to_latest_sprint            | 22-Migration From [PREVIOUS_3PARTY] To [LATEST_SPRINT]           | Rolling Update to latest sprint manifest from previous 3-party version                                                       |
| clean_previous_3party_pv                                   | 23-Clean [PREVIOUS_3PARTY] PV                                    | Clean Deploy with previous 3-party version manifest on hostpath PV                                                           |
| migration_from_previous_3party_to_latest_sprint_pv         | 24-Migration From [PREVIOUS_3PARTY] To [LATEST_SPRINT] PV        | Rolling Update to latest sprint manifest from previous 3-party version on hostpath PV                                        |
| clean_latest_sprint_full-at_ports-specifying_custom_labels | 25-Clean [LATEST_SPRINT] Full-AT Ports-specifying Custom-labels  | Clean Deploy of latest sprint manifest with Ports specifying for global, servers and clients and with full scope auto-tests  |
<!-- markdownlint-enable line-length -->
