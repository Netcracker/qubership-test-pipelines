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

`Pay Attention` only ONE configuration block can be uncommented, another should be commented out.



After committing changes, pipeline will be run automatically.

For run a new pipeline without changes open `CI/CD` -> `Pipelines` in sidebar and click on button `Run Pipeline`. After this select branch `Core_Framework` and click on `Run Pipeline` button again.

Below is a list of variables and jobs for all services.

## Variables
<!-- markdownlint-disable line-length -->
| Variable               | Description                                                                                        |
|------------------------|----------------------------------------------------------------------------------------------------|
| PREVIOUS_SPRINT        | Previous sprint manifest with kafka for Deployer.                                              |
| PREVIOUS_SUPPL_SPRINT  | Previous sprint manifest with kafka-services for Deployer.                                     |
| LATEST_SPRINT          | New sprint manifest with kafka for Deployer.                                                   |
| LATEST_SUPPL_SPRINT    | New sprint manifest with kafka-services for Deployer.                                          |
| N1_RELEASE             | Previous release manifest (n-1, where n – actual release) with kafka for Deployer.             |
| N1_SUPPL_RELEASE       | Previous release manifest (n-1, where n – actual release) with kafka-services for Deployer.    |
| N2_RELEASE             | Previous-previous release manifest (n-2, where n – actual release) with kafka for Deployer.    |
| N2_SUPPL_RELEASE       | Previous-previous release manifest (n-2, where n – actual release) with services for Deployer. |
| ZOOKEEPER_LATEST       | Zookeeper manifest for installation for some cases                                                 |
| ZOO_PROJECT            | Namespace in k8s for zoo installation                                                              | 
| PREVIOUS_3PARTY        | Manifest with support version of thirdparty kafka for Deployer                                 |
| PREVIOUS_SUPPL_3PARTY  | Manifest with support version of thirdparty kafka with services for Deployer                   |
| LATEST_SPRINT_TAG      | Tag (branch name) name with CRD for new sprint                                                     | 
| PREVIOUS_SPRINT_TAG    | Tag (branch name) name with CRD for previous sprint                                                | 
<!-- markdownlint-enable line-length -->


## Jobs list
<!-- markdownlint-disable line-length -->
| Stage                                                              | Job                                                                     | Description                                                                                                                    |
|--------------------------------------------------------------------|-------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------|
| clean_zookeeper_latest_tls                                         | 1-Clean [ZOOKEEPER_LATEST] TLS                                          | Clean Deploy job for zookeeper-service with tls enabled                                                                        | 
| clean_latest_sprint_tls_zookeeper_tls                              | 2-Clean [LATEST_SPRINT] TLS ZookeeperTLS                                | Clean Deploy job with kafka in tls mode                                                                                        | 
| clean_zookeeper_latest_non_tls                                     | 3-Clean [ZOOKEEPER_LATEST] non-TLS                                      | Clean Deploy job for zookeeper-service with tls disabled                                                                       |
| clean_previous_sprint                                              | 4-Clean [PREVIOUS_SPRINT]                                               | Clean Deploy job kafka previous sprint version with services for upgrade manifest                                              | 
| upgrade_from_previous_sprint_to_latest_sprint                      | 5-Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT]                     | Rolling update job with kafka + services to latest sprint manifest                                                             | 
| clean_latest_sprint                                                | 6-Clean [LATEST_SPRINT]                                                 | Clean Deploy job latest sprint kafka with services for upgrade params                                                          | 
| upgrade_latest_sprint_diff_params                                  | 7-Upgrade [LATEST_SPRINT] Diff Params                                   | Rolling update job with kafka + services and updated params in deployment config                                               |
| clean_latest_sprint_non_kraft_schema                               | 8-Clean [LATEST_SPRINT] non-KRaft schema                                | Clean Deploy job latest sprint kafka with services                                                                             |
| migration_latest_sprint_to_kraft_schema                            | 9-Migration [LATEST_SPRINT] To Kraft Schema                             | Migration update job latest sprint kafka from non-KRaft to KRaft with services                                                 |
| clean_latest_sprint_consul_integration_kraft_cruisecontrol_full_at | 10-Clean [LATEST_SPRINT] Consul Integration KRaft CruiseControl Full-AT | Clean Deploy job latest sprint kafka in KRaft mode with Consul integration, CruiseControl enabled and full scope of auto-tests |
| clean_latest_sprint_zoo_kafka_infra_passport                       | 11-Clean [LATEST_SPRINT] Zoo+Kafka Infra Passport                       | Clean Deploy job latest sprint kafka+zookeeper infra passport                                                                  |
| clean_previous_sprint_non_tls                                      | 12-Clean [PREVIOUS_SPRINT] non-TLS                                      | Clean Deploy job previous sprint kafka with services with tls disabled                                                         |
| migration_from_previous_sprint_non_tls_to_latest_sprint_tls        | 14-Migration From [PREVIOUS_SPRINT] Non-TLS To [LATEST_SPRINT] TLS      | Migration update job from previous sprint to latest sprint kafka from non-TLS to TLS mode with services                        | 
| clean_latest_sprint_drd_tls_secrets                                | 15-Clean [LATEST_SPRINT] DRD TLS Secrets                                | Clean Deploy job latest sprint kafka with DRD enabled and pre-created secrets with TLS certificates                            |
| upgrade_latest_sprint_drd_tls_certs                                | 16-Upgrade [LATEST_SPRINT] DRD TLS Certs                                | Rolling update job latest sprint kafka with DRD enabled and TLS certificates specified in parameters                           |
| clean_previous_sprint_s3                                           | 17-Clean [PREVIOUS_SPRINT] S3                                           | Clean Deploy job previous sprint kafka with services and backup daemon with s3 storage                                         |
| upgrade_from_previous_sprint_to_latest_sprint_s3                   | 18-Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT] S3                 | Rolling update job latest sprint kafka with services and backup daemon with s3 storage                                         |
| clean_n1_release                                                   | 19-Clean [N1_RELEASE]                                                   | Clean Deploy kafka + services with previous release manifest (n-1, where n – actual release)                                   |
| upgrade_from_n1_release_to_latest_sprint                           | 20-Upgrade From [N1_RELEASE] To [LATEST_SPRINT]                         | Rolling update job to actual kafka with services from previous release                                                         |
| clean_n2_release                                                   | 21-Clean [N2_RELEASE]                                                   | Clean Deploy kafka + services with previous-previous release manifest (n-2)                                                    |
| upgrade_from_n2_release_to_latest_sprint                           | 22-Upgrade From [N2_RELEASE] To [LATEST_SPRINT]                         | Rolling update job to actual kafka with services from two previous releases                                                    |
| clean_previous_sprint_pv                                           | 23-Clean [PREVIOUS_SPRINT] PV                                           | Clean Deploy previous sprint kafka with services with hostpath PV                                                              |
| upgrade_from_previous_sprint_to_latest_sprint_pv                   | 24-Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT] PV                 | Rolling update job to latest sprint kafka + services with hostpath PV                                                          |
| clean_latest_sprint_pv                                             | 25-Clean [LATEST_SPRINT] PV                                             | Clean Deploy from previous sprint to latest sprint kafka with services with hostpath PV                                        |
| clean_previous_sprint_restricted                                   | 26-Clean [PREVIOUS_SPRINT] Restricted                                   | Restricted clean Deploy job previous sprint kafka + services for update to latest sprint                                       |
| upgrade_from_previous_sprint_to_latest_sprint_restricted           | 27-Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT] Restricted         | Restricted rolling update job kafka + services from previous sprint to latest sprint version                                   |
| clean_latest_sprint_restircted                                     | 28-Clean [LATEST_SPRINT] Restricted                                     | Restricted clean Deploy job latest sprint kafka + services                                                                     |
| clean_previous_3rdparty                                            | 29-Clean [PREVIOUS_3RDPARTY]                                            | Clean Deploy kafka previous thirdparty support version + services for update to latest sprint thirdparty version               |
| migration_from_previous_3rdparty_to_latest_sprint                  | 30-Migration From [PREVIOUS_3RDPARTY] To [LATEST_SPRINT]                | Migration from previous thirdparty support version to latest sprint thirdparty version kafka + services                        |
<!-- markdownlint-enable line-length -->
