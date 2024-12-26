## Quick Start Guide
This mini guide contains an explanation of how to launch pipelines for check deployment cases and an explanation of stages and variables that need to be configured before launching.

## How to run pipelines

All pipelines have been already configured with different deploy cases and stages. 
It's possible to run pipelines for deploy to 2 clouds: `qa_kubernetes` and `ocp_cert_1`. 

In order to run to `qa_kubernetes` cloud you should uncomment following parameters under `qa_kubernetes configuration` comment:
```
  PREFIX: qa_kubernetes
  JENKINS_URL: ''
  JENKINS_USER: ''
  JENKINS_PASS: ''
  CREDS_IN_DEPLOYER: ''
  RESTRICTED_USER_APP: ''
  CLOUD_HOST_OVERALL: ${QA_KUBER_HOST}
  CLOUD_TOKEN_OVERALL: ${QA_KUBER_TOKEN}
  PROJECT: kafka-service
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
  PROJECT: kafka-service
```
This is an example for `kafka`, other services are similar

`Pay Attention` only ONE configuration block can be uncommented, another should be commented out.



After committing changes, pipeline will be run automatically.

For run a new pipeline without changes open `CI/CD` -> `Pipelines` in sidebar and click on button `Run Pipeline`. After this select branch `Core_Framework` and click on `Run Pipeline` button again.

Below is a list of variables and jobs for Zookeeper.


# Zookeeper
## Zookeeper variables
<!-- markdownlint-disable line-length -->
| Variable           | Description                                                                         |
|--------------------|-------------------------------------------------------------------------------------|
| N2_RELEASE   | Previous-previous release manifest (n-2, where n – actual release) for Deployer | 
| N1_RELEASE    | Previous release manifest (n-1, where n – actual release) for Deployer          | 
| PREVIOUS_SPRINT        | Previous sprint manifest for Deployer                                           | 
| LATEST_SPRINT        | New sprint manifest for Deployer                                                | 
| LATEST_SPRINT_TAG                | Tag (branch name) name with CRD for new sprint                                      | 
| PREVIOUS_SPRINT_TAG            | Tag (branch name) name with CRD for previous sprint                                      | 
<!-- markdownlint-enable line-length -->

## Zookeeper jobs list
<!-- markdownlint-disable line-length -->
| Stage                                        | Job                                                   | Description                                                                              |
|----------------------------------------------|-------------------------------------------------------|------------------------------------------------------------------------------------------|
| clean_previous_sprint                       | 1-Clean [PREVIOUS_SPRINT]                         | Clean Deploy job with previous sprint manifest                                           | 
| upgrade_from_previous_sprint_to_latest_sprint                             | 2-Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT]                     | Rolling Update job to latest sprint manifest from previous sprint                                  | 
| clean_latest_sprint                                 | 3-Clean [LATEST_SPRINT]                           | Clean Deploy with latest sprint manifest                                                           | 
| upgrade_latest_sprint_diff_params                   | 4-Upgrade [LATEST_SPRINT] Diff Params | Rolling Update with same manifest from previous step, but with changed deployment config | 
| clean_n1_release                               | 5-Clean [N1_RELEASE]                       | Clean Deploy with previous release manifest                                              | 
| upgrade_from_n1_release_to_latest_sprint               | 6-Upgrade From [N1_RELEASE] To [LATEST_SPRINT]       | Rolling Update from previous release manifest to latest sprint manifest                            | 
| clean_n1_release_for_rolling_update             | 7-Clean [N1_RELEASE] For Rolling Update                | Clean Deploy with previous release manifest for update parameters                                             | 
| upgrade_from_n1_release_to_latest_sprint_rolling_update | 8-Upgrade From [N1_RELEASE] To [LATEST_SPRINT] Rolling Update                  | Rolling Update to latest sprint manifest from previous release manifest                            | 
| clean_n2_release                            | 9-Clean [N2_RELEASE]                           | Clean Deploy with previous-previous release manifest (n-2, where n – actual release)     | 
| upgrade_from_n2_release_to_latest_sprint                         | 10-Upgrade From [N2_RELEASE] To [LATEST_SPRINT]                   | Rolling Update to latest sprint manifest from n-2 manifest                                         |
| clean_latest_sprint_without_components              | 11-Clean [LATEST_SPRINT] W/O Components                                | Clean Deploy of latest sprint version with minimal deployment config                               | 
| upgrade_latest_sprint_all_components_s3            | 12-Upgrade [LATEST_SPRINT] All Components S3           | Rolling Update to latest sprint version with all components and connection to S3                   | 
| clean_latest_sprint_non_tls              | 13-Clean [LATEST_SPRINT] non-TLS                                | Clean Deploy of latest sprint version with TLS disabled                               | 
| upgrade_latest_sprint_tls            | 14-Upgrade [LATEST_SPRINT] TLS           | Rolling Update to latest sprint version with TLS enabled                   | 
| clean_latest_sprint_tls                             | 15-Clean [LATEST_SPRINT] TLS                        | Clean Deploy of latest sprint version with enabled TLS                                             | 
| clean_latest_sprint_tls_secret              | 16-Clean [LATEST_SPRINT] TLS Secrets                                | Clean Deploy of latest sprint version with pre-created secrets with TLS certificates                               | 
| upgrade_latest_sprint_tls_certificates            | 17-Upgrade [LATEST_SPRINT] TLS Certificates           | Rolling Update to latest sprint version with TLS certificates specified in parameters                   | 
| clean_latest_sprint_pv                     | 18-Clean [LATEST_SPRINT] PV                | Clean Deploy of latest sprint version with hostpath PV                                             | 
| clean_latest_sprint_infra_passport                     | 19-Clean [LATEST_SPRINT] Infra Passport                | Clean Deploy of latest sprint version infra passport                                             | 
| clean_previous_sprint_restricted                 | 20-Clean [PREVIOUS_SPRINT] Restricted                 | Clean Deploy job with previous sprint manifest in restricted mode                         | 
| upgrade_from_previous_sprint_to_latest_sprint_restricted             | 21-Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT] Restricted            | Rolling Update job to latest sprint manifest from previous sprint in restricted mode               | 
| clean_latest_sprint_restricted                 | 22-Clean [LATEST_SPRINT] Restricted                 | Clean Deploy with latest sprint manifest in restricted mode                                        | 
<!-- markdownlint-enable line-length -->
