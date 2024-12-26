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

Below is a list of variables and jobs for all services.

## Variables
<!-- markdownlint-disable line-length -->
| Variable            | Description                                                                         |
|---------------------|-------------------------------------------------------------------------------------|
| N2_RELEASE          | Previous-previous release manifest (n-2, where n – actual release) for Deployer | 
| N1_RELEASE          | Previous release manifest (n-1, where n – actual release) for Deployer          | 
| PREVIOUS_SPRINT     | Previous sprint manifest for Deployer                                           | 
| LATEST_SPRINT       | New sprint manifest for Deployer                                                | 
| KAFKA_PROJECT       | Kafka projest name                                                                  |
| KAFKA_VERSION       | Kafka version                                                                       |
| DEPLOY_SCHEME       | `Basic` or `full`. Set `basic` to run only basic jobs, `full` to run all jobs       |
| LATEST_SPRINT_TAG   | Tag (branch name) name with CRD for new sprint                                      | 
| PREVIOUS_SPRINT_TAG | Tag (branch name) name with CRD for previous sprint                                 | 
<!-- markdownlint-enable line-length -->

## Jobs list
<!-- markdownlint-disable line-length -->
| Stage                                                    | Job                                                                  | Description                                                                                                                         | Deploy Scheme |
|----------------------------------------------------------|----------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------|---------------|
| clean_previous_sprint                                    | 1-Clean [PREVIOUS_SPRINT]                                            | Clean Deploy job with previous sprint manifest                                                                                      | basic         |
| upgrade_from_previous_sprint_to_latest_sprint            | 2-Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT]                  | Rolling Update job to latest sprint manifest from previous sprint                                                                   | basic         |
| clean_latest_sprint                                      | 3-Clean [LATEST_SPRINT]                                              | Clean Deploy with latest manifest                                                                                                   | basic         |
| upgrade_latest_sprint_diff_params_full_at                | 4-Upgrade [LATEST_SPRINT] Diff Params Full-AT                        | Rolling Update with same manifest from previous step, but with changed deployment config and full-AT                                | basic         |
| clean_n1_release                                         | 5-Clean [N1_RELEASE]                                                 | Clean Deploy with previous release manifest                                                                                         | full          |
| upgrade_from_n1_release_to_latest_sprint                 | 6-Upgrade From [N1_RELEASE] To [LATEST_SPRINT]                       | Rolling Update from previous release manifest to latest sprint manifest                                                             | full          |
| clean_n2_release                                         | 7-Clean [N2_RELEASE]                                                 | Clean Deploy with previous-previous release manifest (n-2, where n – actual release)                                                | full          |
| upgrade_from_n2_release_to_latest_sprint                 | 8-Upgrade From [N2_RELEASE] To [LATEST_SPRINT]                       | Rolling Update to latest sprint manifest from n-2 manifest                                                                          | full          |
| clean_latest_sprint_infra_pasport                        | 9-Clean [LATEST_SPRINT] Infra Passport                               | Clean Deploy infra passport with latest sprint manifest                                                                             | basic         |
| clean_previous_sprint_restricted                         | 10-Clean [PREVIOUS_SPRINT] Restricted                                | Clean Deploy job with previous sprint manifest in restricted mode                                                                   | basic         |
| upgrade_from_previous_sprint_to_latest_sprint_restricted | 11-Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT] Restricted      | Rolling Update job to latest sprint manifest from previous sprint in restricted mode                                                | basic         | 
| clean_latest_sprint_restricted                           | 12-Clean [LATEST_SPRINT] Restricted                                  | Clean Deploy with latest sprint manifest in restricted mode                                                                         | basic         | 
| clean_latest_sprint_without_components                   | 13-Clean [LATEST_SPRINT] W/O Components                              | Clean Deploy of latest sprint version with minimal deployment config                                                                | full          |
| upgrade_latest_sprint_from_1_to_3_replicas               | 14-Upgrade [LATEST_SPRINT] From 1 To 3 Replicas                      | Rolling Update with latest sprint manifest from 1 to 3 streaming replicas                                                           | full          |
| clean_latest_sprint_connector_crd                        | 15-Clean [LATEST_SPRINT] Connector CRD                               | Clean of latest sprint version with connector configurator on CRD                                                           | full          |
| upgrade_latest_sprint_custom_creds                       | 16-Upgrade [LATEST_SPRINT] Custom Creds                              | Rolling Update with latest sprint manifest with updated creds                                                                       | full          |
| clean_latest_sprint_non_tls                              | 17 - Clean [LATEST_SPRINT] non TLS                                   | Clean Deploy job with latest sprint manifest and TLS disabled                                                                       | full          |
| upgrade_latest_sprint_from_non_tls_to_tls                | 18 - Upgrade [LATEST_SPRINT] From non-TLS To TLS                     | Rolling Update job to latest sprint manifest and TLS enabled                                                                        | full          |
| clean_latest_sprint_tls                                  | 19-Clean [LATEST_SPRINT] TLS                                         | Clean Deploy job with latest sprint manifest and TLS enabled                                                                        | full          |
| upgrade_latest_sprint_from_tls_to_non_tls                | 20-Upgrade [LATEST_SPRINT] From TLS To Non-TLS                       | Rolling Update job to latest manifest and TLS disabled                                                                              | full          |
| clean_latest_sprint_drd_tls_secrets                      | 21-Clean [LATEST_SPRINT] DRD TLS Secrets                             | Clean Deploy job with latest sprint manifest, DRD enabled and pre-created secrets with TLS certificates                             | full          |
| upgrade_latest_sprint_drd_from_tls_secrets_to_tls_certs  | 22-Upgrade [LATEST_SPRINT] DRD From TLS Secrets To TLS Cetificates   | Rolling Update job to latest sprint manifest and TLS certificates specified in parameters                                           | full          |
| clean_latest_sprint_profiler_jaeger_integration          | 23-Clean [LATEST_SPRINT] Profiler Jaeger Integration                 | Clean of latest sprint version with Profiler and Jaeger integration. Job launched manually                                  | full          |
| clean_kafka_latest_sprint_with_tls                       | 24-Clean Kafka [LATEST_SPRINT] With TLS                              | Clean Deploy kafka with TLS for installing streaming with kafka. Job is avaliabliable only if `KAFKA_VERSION` isn't empty           | basic         | 
| clean_latest_sprint_full_at_tls_with_tls_kafka           | 25-Clean [LATEST_SPRINT] Full-AT TLS With TLS Kafka                  | Clean Deploy of latest sprint version with kafka with TLS and full-AT enabled. Job is available only if `KAFKA_VERSION` isn't empty | basic         |
<!-- markdownlint-enable line-length -->
