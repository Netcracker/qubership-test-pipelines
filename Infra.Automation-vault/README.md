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

Below is a list of variables and jobs for Vault service.

# Vault
## Vault variables
<!-- markdownlint-disable line-length -->
| Variable           | Description                                                                         |
|--------------------|-------------------------------------------------------------------------------------|
| N2_RELEASE          | Previous-previous release manifest (n-2, where n – actual release) for Deployer  | 
| N1_RELEASE          | Previous release manifest (n-1, where n – actual release) for Deployer           | 
| PREVIOUS_SPRINT     | Previous sprint manifest for Deployer                                            | 
| LATEST_SPRINT       | New sprint manifest for Deployer                                                 |
| PREVIOUS_3PARTY     | Previous 3-party version manifest for Deployer                                   |  
| LATEST_SPRINT_TAG   | Tag (branch name) name with CRD for new sprint                                       | 
| PREVIOUS_SPRINT_TAG | Tag (branch name) name with CRD for previous sprint                                  | 
<!-- markdownlint-enable line-length -->

## Vault jobs list
<!-- markdownlint-disable line-length -->
| Stage                            | Job                                 | Description                                                                              |
|----------------------------------|-------------------------------------|------------------------------------------------------------------------------------------|
| clean_previous_sprint_restricted                                    | 1-Clean [PREVIOUS_SPRINT] Restricted | Clean Deploy job with previous sprint manifest in restricted mode | 
| upgrade_from_previous_sprint_to_latest_sprint_restricted            | 2-Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT] Restricted | Rolling Update to latest sprint manifest from previous sprint in restricted mode | 
| clean_latest_sprint_restricted                                      | 3-Clean [LATEST_SPRINT] Restricted | Clean Deploy with latest sprint manifest in restricted mode | 
| clean_n2_release                                                    | 4-Clean [N2_RELEASE] | Clean Deploy with previous-previous release manifest (n-2, where n – actual release) |
| upgrade_from_n2_release_to_latest_sprint                            | 5-Upgrade From [N2_RELEASE] To [LATEST_SPRINT] | Rolling Update to latest sprint manifest from previous sprint |
| clean_n1_release                                                    | 6-Clean [N1_RELEASE] | Clean Deploy with previous release manifest |
| upgrade_from_n1_release_to_latest_sprint                            | 7-Upgrade From [N1_RELEASE] To [LATEST_SPRINT] | Rolling Update to latest sprint manifest from previous sprint |
| clean_previous_sprint                                               | 8-Clean [PREVIOUS_SPRINT] | Clean Deploy job with previous sprint manifest |
| upgrade_from_previous_sprint_to_latest_sprint                       | 9-Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT] | Rolling Update to latest sprint manifest from previous sprint |
| clean_latest_sprint                                                 | 10-Clean [LATEST_SPRINT] | Clean Deploy with latest sprint manifest |
| upgrade_latest_sprint_diff_params                                   | 11-Upgrade [LATEST_SPRINT] Diff Params | Rolling Update with same manifest from previous step, but with changed deployment config |
| clean_latest_sprint_dev-mode                                        | 12-Clean [LATEST_SPRINT] Dev mode | Clean Deploy with latest sprint manifest in dev mode |
| clean_previous_sprint_consul-server-connect                         | 13-Clean [PREVIOUS_SPRINT] consul-server connect | Clean Deploy with previous sprint manifest with consul server connection |
| upgrade_from_previous_sprint_to_latest_sprint_consul-server-connect | 14-Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT] consul-server connect | Rolling Update to latest sprint manifest with consul server connection|
| clean_latest_sprint_tls-secrets                                     | 15-Clean [LATEST_SPRINT] TLS Secrets | Clean Deploy with latest sprint manifest and pre-created tls secrets |
| upgrade_latest_sprint_tls-certs                                     | 16-Upgrade [LATEST_SPRINT] TLS Certs | Rolling Update with same manifest from previous step, but with specified tls certificates in deployment parameters |
| clean_latest_sprint_tls                                             | 17-Clean [LATEST_SPRINT] TLS | Clean Deploy with latest sprint manifest and tls using cert manager |
| clean_latest_sprint_consul-server-connect                           | 18-Clean [LATEST_SPRINT] consul-server connect | Clean Deploy with latest sprint manifest with new consul server |
| upgrade_latest_sprint_from_non-tls_to_tls                           | 19-Upgrade [LATEST_SPRINT] From Non-TLS To TLS | Rolling Update with same manifest from previous step, but with tls using cert manager |
| clean_previous_3party                                               | 20-Clean [PREVIOUS_3PARTY] | Clean Deploy with previous 3-party version manifest |
| migration_from_previous_3party_to_latest_sprint                     | 21-Migration From [PREVIOUS_3PARTY] To [LATEST_SPRINT] | Rolling Update to latest sprint manifest from previous 3-party version |
<!-- markdownlint-enable line-length -->
