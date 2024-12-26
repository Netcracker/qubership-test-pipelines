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
  PROJECT: rabbitmq
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
  PROJECT: rabbitmq
```

`Pay Attention` only ONE configuration block can be uncommented, another should be commented out.



After committing changes, pipeline will be run automatically.

For run a new pipeline without changes open `CI/CD` -> `Pipelines` in sidebar and click on button `Run Pipeline`. After this select branch `Core_Framework` and click on `Run Pipeline` button again.

Below is a list of variables and jobs for all services.

## Variables
<!-- markdownlint-disable line-length -->
| Variable            | Description                                                                            |
|---------------------|----------------------------------------------------------------------------------------|
| N2_RELEASE          | Previous-previous release manifest (n-2, where n – actual release) for Deployer    | 
| N1_RELEASE          | Previous release manifest (n-1, where n – actual release) for Deployer             | 
| PREVIOUS_SPRINT     | Previous sprint manifest for Deployer                                              | 
| LATEST_SPRINT       | New sprint manifest for Deployer                                                   |
| PREVIOUS_3PARTY     | Previous 3-party version manifest for Deployer                                     | 
| DEPLOY_SCHEME       | `Basic` or `full`. Set `basic` to run only basic jobs, `full` to run all jobs          |
| LATEST_SPRINT_TAG   | Tag (branch name) name with CRD for new sprint                                         | 
| PREVIOUS_SPRINT_TAG | Tag (branch name) name with CRD for previous sprint                                    | 
<!-- markdownlint-enable line-length -->

## Jobs list
<!-- markdownlint-disable line-length -->
| Stage                                                    | Job                                                             | Description                                                                                     | Deploy Scheme |
|----------------------------------------------------------|-----------------------------------------------------------------|-------------------------------------------------------------------------------------------------|---------------|
| clean_latest_sprint_infra-passport                       | 1-Clean [LATEST_SPRINT] Infra Passport                          | Clean Deploy with latest sprint manifest and infra passport parameters                          | basic         |
| clean_previous_sprint                                    | 2-Clean [PREVIOUS_SPRINT]                                       | Clean Deploy with previous sprint manifest                                                      | basic         |
| upgrade_from_previous_sprint_to_latest_sprint            | 3-Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT]             | Rolling Update to latest sprint manifest from previous sprint                                   | basic         |
| clean_latest_sprint                                      | 4-Clean [LATEST_SPRINT]                                         | Clean Deploy with latest sprint manifest                                                        | basic         |
| upgrade_latest_sprint_diff_params                        | 5-Upgrade [LATEST_SPRINT] Diff Params                           | Rolling Update with same manifest from previous step, but with changed deployment config        | basic         |
| clean_n1_release                                         | 6-Clean [N1_RELEASE]                                            | Clean Deploy with previous release manifest                                                     | full          |
| upgrade_from_n1_release_to_latest_sprint                 | 7-Upgrade From [N1_RELEASE] To [LATEST_SPRINT]                  | Rolling Update from previous release manifest to latest sprint manifest                         | full          |
| clean_n2_release                                         | 8-Clean [N2_RELEASE]                                            | Clean Deploy with previous-previous release manifest (n-2, where n – actual release)            | full          |
| upgrade_from_n2_release_to_latest_sprint                 | 9-Upgrade From [N2_RELEASE] To [LATEST_SPRINT]                  | Rolling Update to latest sprint manifest from n-2 manifest                                      | full          |
| clean_previous_3party                                    | 10-Clean [PREVIOUS_3PARTY]                                      | Clean Deploy with previous 3-party version manifest                                             | basic         |
| migration_from_previous_3party_to_latest_sprint          | 11-Migration From [PREVIOUS_3PARTY] To [LATEST_SPRINT]          | Rolling Update to latest sprint manifest from previous 3-party version                          | basic         |
| clean_previous_3party_pv                                 | 12-Clean [PREVIOUS_3PARTY] PV                                   | Clean Deploy with previous 3-party version on hostpath PV                                       | basic         |
| migration_from_previous_3party_to_latest_sprint_pv       | 13-Migration From [PREVIOUS_3PARTY] To [LATEST_SPRINT] PV       | Rolling Update to latest sprint manifest from previous 3-party version on hostpath PV           | basic         |
| clean_previous_sprint_pv                                 | 14-Clean [PREVIOUS_SPRINT] PV                                   | Clean Deploy with previous sprint manifest on hostpath PV                                       | basic         |
| upgrade_from_previous_sprint_to_latest_sprint_pv         | 15-Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT] PV         | Rolling Update to latest sprint manifest from previous sprint on hostpath PV                    | basic         |
| clean_latest_sprint_pv                                   | 16-Clean [LATEST_SPRINT] PV                                     | Clean Deploy with latest sprint manifest on hostpath PV                                         | basic         |
| clean_previous_sprint_restricted                         | 17-Clean [PREVIOUS_SPRINT] Restricted                           | Clean Deploy with previous sprint manifestin restricted mode                                    | basic         | 
| upgrade_from_previous_sprint_to_latest_sprint_restricted | 18-Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT] Restricted | Rolling Update to latest sprint manifest from previous sprint in restricted mode                | basic         |
| clean_latest_sprint_restricted                           | 19-Clean [LATEST_SPRINT] Restricted                             | Clean Deploy with latest sprint manifest in restricted mode                                     | basic         | 
| clean_latest_sprint_w/o_components                       | 20-Clean [LATEST_SPRINT] W/O Components                         | Clean Deploy of latest sprint version with minimal deployment config                            | full          |
| upgrade_latest_sprint_all_components_s3_drd              | 21-Upgrade [LATEST_SPRINT] All Components S3 DRD                | Update with latest sprint manifest with all components, S3 and DRD                              | full          |
| clean_latest_sprint_s3                                   | 22-Clean [LATEST_SPRINT] S3                                     | Clean Deploy of latest sprint version with S3                                                   | full          |
| upgrade_latest_sprint_custom_creds                       | 23-Upgrade [LATEST_SPRINT] Custom Creds                         | Rolling Update with latest sprint manifest with updated creds                                   | basic         |
| clean_latest_sprint_s3_drd_tls-secrets                   | 24-Clean [LATEST_SPRINT] S3 DRD TLS Secrets                     | Clean Deploy of latest sprint version with enabled TLS using pre-created secrets, DRD and S3    | basic         |
| upgrade_latest_sprint_s3_drd_tls-certs                   | 25-Upgrade [LATEST_SPRINT] S3 DRD TLS Certs                     | Rolling Update latest sprint manifest with enabled TLS using specified certificates, DRD and S3 | basic         |
| clean_latest_sprint_s3_drd                               | 26-Clean [LATEST_SPRINT] S3 DRD                                 | Clean Deploy of latest sprint version with enabled DRD and S3                                   | full          |
| upgrade_latest_sprint_from_non-tls_to_tls_s3_drd         | 27-Upgrade [LATEST_SPRINT] From Non-TLS To TLS S3 DRD           | Rolling Update latest sprint manifest with enabled TLS using cert-manager, DRD and S3           | basic         |
| clean_latest_sprint_s3_drd_tls                           | 28-Clean [LATEST_SPRINT] TLS S3 DRD                             | Clean Deploy of latest sprint version with enabled TLS using cert-manager, DRD and S3           | full          |
| clean_latest_sprint_full-at_custom-labels_nodeport       | 29-Clean [LATEST_SPRINT] Full-AT Custom-Labels Nodeport         | Clean Deploy of latest sprint version with full scope AT, custom labels and nodeport            | basic         |
<!-- markdownlint-enable line-length -->
