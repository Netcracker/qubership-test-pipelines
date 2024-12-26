* [Kafka](#kafka)
* [Consul](#consul)
* [Opensearch](#opensearch) 
* [Rabbitmq](#rabbitmq)
* [Streaming](#streaming)
* [Vault](#vault)
* [Zookeeper](#zookeeper)
* [Elasticsearch](#elasticsearch)
* [Opendistro](#opendistro)


## Quick Start Guide
This mini guide contains an explanation of how to launch pipelines for check deployment cases and an explanation of stages and variables that need to be configured before launching.

## How to run pipelines
To run pipeline for your service you need to copy file content from `Test_case/full_<service_name>.yml` to `gl-ci.yaml`
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

Also specify correct values for parameters described in `Variables` block of this doc in `.gl-ci.yaml` file.

After committing changes, pipeline will be run automatically.

For run a new pipeline without changes open `CI/CD` -> `Pipelines` in sidebar and click on button `Run Pipeline`. After this select branch `Core_Framework` and click on `Run Pipeline` button again.

Below is a list of variables and jobs for all services.

# Kafka
## Kafka variables
<!-- markdownlint-disable line-length -->
| Variable                        | Description                                                                                            |
|---------------------------------|--------------------------------------------------------------------------------------------------------|
| PREVIOUS_SPRINT                   | Previous sprint manifest with kafka for Deployer.                                                  |
| PREVIOUS_SUPPL_SPRINT                | Previous sprint manifest with kafka-services for Deployer.                                         |
| LATEST_SPRINT                   | New sprint manifest with kafka for Deployer.                                                       |
| LATEST_SUPPL_SPRINT                | New sprint manifest with kafka-services for Deployer.                                              |
| N1_RELEASE               | Previous release manifest (n-1, where n – actual release) with kafka for Deployer.                 |
| N1_SUPPL_RELEASE            | Previous release manifest (n-1, where n – actual release) with kafka-services for Deployer.        |
| N2_RELEASE              | Previous-previous release manifest (n-2, where n – actual release) with kafka for Deployer.        |
| N2_SUPPL_RELEASE           | Previous-previous release manifest (n-2, where n – actual release) with services for Deployer.     |
| ZOOKEEPER_LATEST                         | Zookeeper manifest for installation for some cases                                                     |
| ZOO_PROJECT                     | Namespace in k8s for zoo installation                                                                  | 
| PREVIOUS_3PARTY                    | Manifest with support version of thirdparty kafka for Deployer                                     |
| PREVIOUS_SUPPL_3PARTY                 | Manifest with support version of thirdparty kafka with services for Deployer                       |
| LATEST_SPRINT_TAG    | Tag (branch name) name with CRD for new sprint                                      | 
| PREVIOUS_SPRINT_TAG  | Tag (branch name) name with CRD for previous sprint                                 | 
<!-- markdownlint-enable line-length -->


## Kafka jobs list
<!-- markdownlint-disable line-length -->
| Stage                                         | Job                                                | Description                                                                                   |
|-----------------------------------------------|----------------------------------------------------|-----------------------------------------------------------------------------------------------|
| clean_zookeeper_latest_tls                         | 1-Clean [ZOOKEEPER_LATEST] TLS                             | Clean Deploy job for zookeeper-service with tls enabled                                                        | 
| clean_latest_sprint_tls_zookeeper_tls          | 2-Clean [LATEST_SPRINT] TLS ZookeeperTLS                   | Clean Deploy job with kafka in tls mode                                                          | 
| clean_zookeeper_latest_non_tls                             | 3-Clean [ZOOKEEPER_LATEST] non-TLS                 | Clean Deploy job for zookeeper-service with tls disabled                                                   |
| clean_previous_sprint                      | 4-Clean [PREVIOUS_SPRINT]           | Clean Deploy job kafka previous sprint version with services for upgrade manifest                                       | 
| upgrade_from_previous_sprint_to_latest_sprint                        | 5-Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT]                   | Rolling update job with kafka + services to latest sprint manifest                                        | 
| clean_latest_sprint                  | 6-Clean [LATEST_SPRINT]             | Clean Deploy job latest sprint kafka with services for upgrade params                                | 
| upgrade_latest_sprint_diff_params                    | 7-Upgrade [LATEST_SPRINT] Diff Params                     | Rolling update job with kafka + services and updated params in deployment config                            |
| clean_latest_sprint_non_kraft_schema                | 8-Clean [LATEST_SPRINT] non-KRaft schema           | Clean Deploy job latest sprint kafka with services                                  |
| migration_latest_sprint_to_kraft_schema                | 9-Migration [LATEST_SPRINT] To Kraft Schema           | Migration update job latest sprint kafka from non-KRaft to KRaft with services             |
| clean_latest_sprint_consul_integration_kraft_cruisecontrol_full_at                | 10-Clean [LATEST_SPRINT] Consul Integration KRaft CruiseControl Full-AT          | Clean Deploy job latest sprint kafka in KRaft mode with Consul integration, CruiseControl enabled and full scope of auto-tests             |
| clean_latest_sprint_zoo_kafka_infra_passport                | 11-Clean [LATEST_SPRINT] Zoo+Kafka Infra Passport           | Clean Deploy job latest sprint kafka+zookeeper infra passport                                  |
| clean_previous_sprint_non_tls                | 12-Clean [PREVIOUS_SPRINT] non-TLS           | Clean Deploy job previous sprint kafka with services with tls disabled                                 |
| migration_from_previous_sprint_non_tls_to_latest_sprint_tls                         | 14-Migration From [PREVIOUS_SPRINT] Non-TLS To [LATEST_SPRINT] TLS                         | Migration update job from previous sprint to latest sprint kafka from non-TLS to TLS mode with services                              | 
| clean_latest_sprint_drd_tls_secrets                | 15-Clean [LATEST_SPRINT] DRD TLS Secrets           | Clean Deploy job latest sprint kafka with DRD enabled and pre-created secrets with TLS certificates                                  |
| upgrade_latest_sprint_drd_tls_certs                | 16-Upgrade [LATEST_SPRINT] DRD TLS Certs           | Rolling update job latest sprint kafka with DRD enabled and TLS certificates specified in parameters                                  |
| clean_previous_sprint_s3                | 17-Clean [PREVIOUS_SPRINT] S3           | Clean Deploy job previous sprint kafka with services and backup daemon with s3 storage                                 |
| upgrade_from_previous_sprint_to_latest_sprint_s3                 | 18-Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT] S3           | Rolling update job latest sprint kafka with services and backup daemon with s3 storage                               |
| clean_n1_release              | 19-Clean [N1_RELEASE]  | Clean Deploy kafka + services with previous release manifest (n-1, where n – actual release)  |
| upgrade_from_n1_release_to_latest_sprint  | 20-Upgrade From [N1_RELEASE] To [LATEST_SPRINT]                  | Rolling update job to actual kafka with services from previous release                       |
| clean_n2_release             | 21-Clean [N2_RELEASE]          | Clean Deploy kafka + services with previous-previous release manifest (n-2)                   |
| upgrade_from_n2_release_to_latest_sprint | 22-Upgrade From [N2_RELEASE] To [LATEST_SPRINT]                  | Rolling update job to actual kafka with services from two previous releases              |
| clean_previous_sprint_pv         | 23-Clean [PREVIOUS_SPRINT] PV     | Clean Deploy previous sprint kafka with services with hostpath PV                                    |
| upgrade_from_previous_sprint_to_latest_sprint_pv               | 24-Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT] PV        | Rolling update job to latest sprint kafka + services with hostpath PV                               |
| clean_latest_sprint_pv             | 25-Clean [LATEST_SPRINT] PV                 | Clean Deploy from previous sprint to latest sprint kafka with services with hostpath PV                                 |
| clean_previous_sprint_restricted                   | 26-Clean [PREVIOUS_SPRINT] Restricted                  | Restricted clean Deploy job previous sprint kafka + services for update to latest sprint          |
| upgrade_from_previous_sprint_to_latest_sprint_restricted             | 27-Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT] Restricted             | Restricted rolling update job kafka + services from previous sprint to latest sprint version                      |
| clean_latest_sprint_restircted                | 28-Clean [LATEST_SPRINT] Restricted                  | Restricted clean Deploy job latest sprint kafka + services                              |
| clean_previous_3rdparty         | 29-Clean [PREVIOUS_3RDPARTY]                     | Clean Deploy kafka previous thirdparty support version + services for update to latest sprint thirdparty version  |
| migration_from_previous_3rdparty_to_latest_sprint           | 30-Migration From [PREVIOUS_3RDPARTY] To [LATEST_SPRINT]                      | Migration from previous thirdparty support version to latest sprint thirdparty version kafka + services                             |
<!-- markdownlint-enable line-length -->

# Consul
## Consul variables
<!-- markdownlint-disable line-length -->
| Variable           | Description                                                                         |
|--------------------|-------------------------------------------------------------------------------------|
| N2_RELEASE           | Previous-previous release manifest (n-2, where n – actual release) for Deployer | 
| N1_RELEASE           | Previous release manifest (n-1, where n – actual release) for Deployer          | 
| PREVIOUS_SPRINT      | Previous sprint manifest for Deployer                                           | 
| LATEST_SPRINT        | Latest sprint manifest for Deployer                                             | 
| PREVIOUS_3PARTY      | Previous 3-party version manifest for Deployer                                  | 
| LATEST_SPRINT_TAG    | Tag (branch name) name with CRD for new sprint                                      | 
| PREVIOUS_SPRINT_TAG  | Tag (branch name) name with CRD for previous sprint                                 | 
<!-- markdownlint-enable line-length -->

## Consul jobs list
<!-- markdownlint-disable line-length -->
| Stage                                | Job                                                  | Description                                                                                    |
|--------------------------------------|------------------------------------------------------|------------------------------------------------------------------------------------------------|
| clean_latest_sprint_infra_passport                       | 1-Clean [LATEST_SPRINT] Infra Passport                          | Clean Deploy with latest sprint manifest using infra passport parameters only                                               |
| clean_previous_sprint                                    | 2-Clean [PREVIOUS_SPRINT]                                       | Clean Deploy job with previous sprint manifest                                                                              | 
| upgrade_from_previous_sprint_to_latest_sprint            | 3-Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT]             | Rolling Update job to latest sprint manifest from previous sprint                                                             | 
| clean_latest_sprint                                      | 4-Clean [LATEST_SPRINT]                                         | Clean Deploy with latest sprint manifest                                                                                    | 
| upgrade_latest_sprint_diff_params                        | 5-Upgrade [LATEST_SPRINT] Diff Params                           | Rolling Update with same manifest from previous step, but with changed deployment config                                      |
| clean_n1_release                                         | 6-Clean [N1_RELEASE]                                            | Clean Deploy with previous release manifest                                                                                 | 
| upgrade_from_n1_release_to_latest_sprint                 | 7-Upgrade From [N1_RELEASE] To [LATEST_SPRINT]                  | Rolling Update from previous release manifest to latest sprint manifest                                                       | 
| clean_n2_release                                         | 8-Clean [N2_RELEASE]                                            | Clean Deploy with previous-previous release manifest (n-2, where n – actual release)                                        | 
| upgrade_from_n2_release_to_latest_sprint                 | 9-Upgrade From [N2_RELEASE] To [LATEST_SPRINT]                  | Rolling Update to latest sprint manifest from n-2 manifest                                                                    | 
| clean_previous_sprint_restricted                         | 10-Clean [PREVIOUS_SPRINT] Restricted                            | Clean Deploy job with previous sprint manifest in restricted mode                                                           |
| upgrade_from_previous_sprint_to_latest_sprint_restricted | 11-Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT] Restricted | Rolling Update job to latest sprint manifest from previous sprint in restricted mode                                          |
| clean_latest_sprint_restricted                           | 12-Clean [LATEST_SPRINT] Restricted                             | Clean Deploy with latest sprint manifest in restricted mode                                                                 | 
| clean_latest_sprint_w/o_components                       | 13-Clean [LATEST_SPRINT] W/O Components                         | Clean Deploy with latest sprint manifest without additional components                                                      |
| upgrade_latest_sprint_all_components_s3_drd              | 14-Upgrade [LATEST_SPRINT] All Components S3 DRD                | Rolling Update with same manifest from previous step, but with enabled all components, S3 and DRD                             |
| clean_latest_sprint_pv_s3                                | 15-Clean [LATEST_SPRINT] PV S3                                  | Clean Clean Deploy with latest sprint manifest with hostpath PV and S3                                                      | 
| clean_latest_sprint_without_clients                      | 16-Clean [LATEST_SPRINT] Without Clients                        | Clean Deploy with latest sprint manifest without clients                                                                    | 
| upgrade_latest_sprint_drd_s3                             | 17-Upgrade [LATEST_SPRINT] DRD S3                               | Update with same manifest from previous step, but with clients, DRD and S3                                                   | 
| upgrade_latest_sprint_drd_s3_tls                         | 18-Upgrade [LATEST_SPRINT] DRD S3 TLS                           | Rolling Update to same manifest from previous step with enabled TLS, DRD and S3                                               | 
| clean_latest_sprint_drd_s3_tls                           | 19-Clean [LATEST_SPRINT] DRD S3 TLS                             | Clean Deploy of latest sprint version with DRD, S3 and enabled TLS using cert-manager                                       | 
| clean_latest_sprint_tls-certs                            | 20-Clean [LATEST_SPRINT] DRD S3 TLS-certs                       | Clean Deploy of latest sprint version with DRD, S3 and enabled TLS using specified in deployment parameters certificates    |
| clean_previous_3party                                    | 21-Clean [PREVIOUS_3PARTY]                                      | Clean Deploy with previous 3-party version manifest                                                                         |
| migration_from_previous_3party_to_latest_sprint          | 22-Migration From [PREVIOUS_3PARTY] To [LATEST_SPRINT]          | Rolling Update to latest sprint manifest from previous 3-party version                                                        |
| clean_previous_3party_pv                                 | 23-Clean [PREVIOUS_3PARTY] PV                                   | Clean Deploy with previous 3-party version manifest on hostpath PV                                                          |
| migration_from_previous_3party_to_latest_sprint_pv       | 24-Migration From [PREVIOUS_3PARTY] To [LATEST_SPRINT] PV       | Rolling Update to latest sprint manifest from previous 3-party version on hostpath PV                                         |
| clean_latest_sprint_full-at_ports-specifying             | 25-Clean [LATEST_SPRINT] Full-AT Ports-specifying               | Clean Deploy of latest sprint manifest with Ports specifying for global, servers and clients and with full scope auto-tests |
<!-- markdownlint-enable line-length -->

# Opensearch
## Opensearch variables
<!-- markdownlint-disable line-length -->
| Variable               | Description                                                                         |
|------------------------|-------------------------------------------------------------------------------------|
| N2_RELEASE          | Previous-previous release manifest (n-2, where n – actual release) for Deployer | 
| N1_RELEASE          | Previous release manifest (n-1, where n – actual release) for Deployer          | 
| PREVIOUS_SPRINT     | Previous sprint manifest for Deployer                                           | 
| LATEST_SPRINT       | New sprint manifest for Deployer                                                | 
| PREVIOUS_3PARTY     | Previous 3-party version manifest for Deployer                                  |
| DEPLOY_SCHEME       | `Basic` or `full`. Set `basic` to run only basic jobs, `full` to run all jobs       |
| LATEST_SPRINT_TAG   | Tag (branch name) name with CRD for new sprint                                      | 
| PREVIOUS_SPRINT_TAG | Tag (branch name) name with CRD for previous sprint                                 | 
<!-- markdownlint-enable line-length -->

## Opensearch jobs list
<!-- markdownlint-disable line-length -->
| Stage                           | Job                                | Description                                                                          | Deploy Scheme |
|---------------------------------|------------------------------------|--------------------------------------------------------------------------------------|---------------|
| clean_latest_sprint_infra_passport                                 | 1-Clean [LATEST_SPRINT] Infra passport parameters | Clean Deploy using infra-passport paremeters only with latest sprint manifest | Basic |
| clean_previous_sprint_s3                                           | 2-Clean [PREVIOUS_SPRINT] S3 | Clean Deploy with previous sprint manifest | Basic |
| upgrade_from_previous_sprint_to_latest_sprint_s3                   | 3-Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT] S3 | Rolling Update to latest sprint manifest from previous sprint                              | Basic         |
| clean_n1_release_s3                                                | 4-Clean [N1_RELEASE] S3 | Clean Deploy with previous release manifest                                          | Basic         |
| upgrade_from_n1_release_to_latest_sprint_s3                        | 5-Upgrade From [N1_RELEASE] To [LATEST_SPRINT] S3 | Rolling Update to latest sprint manifest from previous sprint | Basic |
| clean_n2_release_s3                                                | 6-Clean [N2_RELEASE] S3 | Clean Deploy with previous-previous release manifest (n-2, where n – actual release) | Full |
| upgrade_from_n2_release_to_latest_sprint_s3                        | 7-Upgrade From [N2_RELEASE] To [LATEST_SPRINT] S3 | Rolling Update to latest sprint manifest from n-2 manifest | Full |
| clean_latest_sprint_s3_separate                                    | 8-Clean [LATEST_SPRINT] S3 Separate | Clean Deploy with latest sprint manifest in separate mode | Basic |
| clean_latest_sprint_s3_separate_arbiter                            | 9-Clean [LATEST_SPRINT] S3 Separate Arbiter | Clean Deploy latest sprint manifest in separate mode with arbiter | Basic |
| upgrade_latest_sprint_s3_separate_arbiter_change_resources_full-at | 10-Upgrade [LATEST_SPRINT] S3 Separate Arbiter Change Resources Full-AT | Rolling Update with latest sprint manifest in separate mode with arbiter, change resources and full AT scope | Basic |
| clean_latest_sprint_w/o_components                                 | 11-Clean [LATEST_SPRINT] W/O Components | Clean Deploy latest sprint version with minimal deployment config | Full |
| upgrade_latest_sprint_all_components_s3                            | 12-Upgrade [LATEST_SPRINT] All components S3 | Update with all components and S3 with latest sprint manifest | Full |
| clean_latest_sprint_s3_drd_tls-secrets                             | 13-Clean [LATEST_SPRINT] S3 DRD TLS-secrets | Clean Deploy latest sprint manifest with S3, DRD and TLS using pre-created tls secrets | Basic |
| upgrade_latest_sprint_s3_drd_tls-certs                             | 14-Upgrade [LATEST_SPRINT] S3 DRD TLS-Certs | Update latest sprint manifest with S3, DRD and TLS using specified tls certificates | Basic |
| clean_latest_sprint_s3_drd_tls                                     | 15-Clean [LATEST_SPRINT] S3 DRD TLS | Clean Deploy of new version with enabled TLS using cert-manager and DRD | Basic |
| clean_latest_sprint_s3                                             | 16-Clean [LATEST_SPRINT] S3 | Clean Deploy latest sprint manifest with S3 | Basic |
| upgrade_latest_sprint_from_non-tls_to_tls_s3                       | 17-Upgrade [LATEST_SPRINT] From Non-TLS To TLS S3 | Upgrade latest sprint manifest with S3 and enable TLS using cert-manager from non-TLS | Basic |
| clean_latest_sprint_s3_tls                                         | 18-Clean [LATEST_SPRINT] S3 TLS | Clean Deploy latest sprint manifest with S3 and enable TLS using cert-manager | Full |
| clean_latest_sprint_nfs                                            | 19-Clean [LATEST_SPRINT] NFS | Clean Deploy latest sprint version with NFS | Basic |
| clean_latest_sprint_s3_custom_creds                                | 20-Clean [LATEST_SPRINT] S3 Custom Creds | Clean Deploy latest sprint version with not default creds | Full |
| clean_previous_3party_s3                                           | 21-Clean [PREVIOUS_3PARTY] S3 | Clean Deploy previous 3-party version with S3 | Basic |
| migration_from_previous_3party_to_latest_sprint_s3                 | 22-Migration From [PREVIOUS_3PARTY] To [LATEST_SPRINT] S3 | Upgrade from previous 3-party version to latest sprint with S3 | Basic |
| clean_previous_3party_s3_pv                                        | 23-Clean [PREVIOUS_3PARTY] S3 PV | Clean Deploy previous 3-party version with S3 on hostpath PV | Basic |
| migration_from_previous_3party_to_latest_sprint_s3_pv              | 24-Migration From [PREVIOUS_3PARTY] To [LATEST_SPRINT] S3 PV | Upgrade from previous 3-party version to latest sprint with S3 on hostpath PV | Basic |
| clean_previous_sprint_s3_pv                                        | 25-Clean [PREVIOUS_SPRINT] S3 PV | Clean Deploy previous sprint version with S3 on hostpath PV | Full |
| upgrade_from_previous_sprint_to_latest_sprint_s3_pv                | 26-Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT] S3 PV | Upgrade from previous sprint version to latest sprint with S3 on hostpath PV | Full |
| clean_previous_sprint_s3_restricted                                | 27-Clean [PREVIOUS_SPRINT] S3 Restricted | Clean Deploy previous sprint manifest in restricted mode | Basic |
| upgrade_from_previous_sprint_to_latest_sprint_s3_restricted        | 28-Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT] S3 Restricted | Rolling Update to latest sprint manifest from previous sprint in restricted mode | Basic |
| clean_latest_sprint_s3_restricted                                  | 29-Clean [LATEST_SPRINT] S3 Restricted | Clean Deploy latest sprint manifest in restricted mode | Basic |
| clean_latest_sprint_s3_pv                                          | 30-Clean [LATEST_SPRINT] S3 PV | Clean Deploy latest sprint manifest with S3 on hostpath PV | Basic | 
| upgrade_latest_sprint_s3_pv_full-at_custom-labels                  | 31-Upgrade [LATEST_SPRINT] S3 PV Full-AT Custom-labels | Rolling Update latest sprint manifest from previous sprint with full tests scope and custom labels on hostpath PV | Basic | 
<!-- markdownlint-enable line-length -->

# Rabbitmq
## Variables
<!-- markdownlint-disable line-length -->
| Variable           | Description                                                                          |
|--------------------|--------------------------------------------------------------------------------------|
| N2_RELEASE          | Previous-previous release manifest (n-2, where n – actual release) for Deployer  | 
| N1_RELEASE          | Previous release manifest (n-1, where n – actual release) for Deployer           | 
| PREVIOUS_SPRINT     | Previous sprint manifest for Deployer                                            | 
| LATEST_SPRINT       | New sprint manifest for Deployer                                                 |
| PREVIOUS_3PARTY     | Previous 3-party version manifest for Deployer                                   | 
| DEPLOY_SCHEME       | `Basic` or `full`. Set `basic` to run only basic jobs, `full` to run all jobs        |
| LATEST_SPRINT_TAG   | Tag (branch name) name with CRD for new sprint                                       | 
| PREVIOUS_SPRINT_TAG | Tag (branch name) name with CRD for previous sprint                                  | 
<!-- markdownlint-enable line-length -->

## Rabbitmq jobs list
<!-- markdownlint-disable line-length -->
| Stage                                     | Job                                                        | Description                                                                              | Deploy Scheme |
|-------------------------------------------|------------------------------------------------------------|------------------------------------------------------------------------------------------|---------------|
| clean_latest_sprint_infra-passport                       | 1-Clean [LATEST_SPRINT] Infra Passport | Clean Deploy with latest sprint manifest and infra passport parameters | basic |
| clean_previous_sprint                                    | 2-Clean [PREVIOUS_SPRINT] | Clean Deploy with previous sprint manifest | basic |
| upgrade_from_previous_sprint_to_latest_sprint            | 3-Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT] | Rolling Update to latest sprint manifest from previous sprint | basic |
| clean_latest_sprint                                      | 4-Clean [LATEST_SPRINT] | Clean Deploy with latest sprint manifest | basic |
| upgrade_latest_sprint_diff_params                        | 5-Upgrade [LATEST_SPRINT] Diff Params | Rolling Update with same manifest from previous step, but with changed deployment config | basic |
| clean_n1_release                                         | 6-Clean [N1_RELEASE] | Clean Deploy with previous release manifest | full |
| upgrade_from_n1_release_to_latest_sprint                 | 7-Upgrade From [N1_RELEASE] To [LATEST_SPRINT] | Rolling Update from previous release manifest to latest sprint manifest | full |
| clean_n2_release                                         | 8-Clean [N2_RELEASE] | Clean Deploy with previous-previous release manifest (n-2, where n – actual release) | full |
| upgrade_from_n2_release_to_latest_sprint                 | 9-Upgrade From [N2_RELEASE] To [LATEST_SPRINT] | Rolling Update to latest sprint manifest from n-2 manifest | full |
| clean_previous_3party                                    | 10-Clean [PREVIOUS_3PARTY] | Clean Deploy with previous 3-party version manifest | basic |
| migration_from_previous_3party_to_latest_sprint          | 11-Migration From [PREVIOUS_3PARTY] To [LATEST_SPRINT] | Rolling Update to latest sprint manifest from previous 3-party version | basic |
| clean_previous_3party_pv                                 | 12-Clean [PREVIOUS_3PARTY] PV | Clean Deploy with previous 3-party version on hostpath PV | basic |
| migration_from_previous_3party_to_latest_sprint_pv       | 13-Migration From [PREVIOUS_3PARTY] To [LATEST_SPRINT] PV | Rolling Update to latest sprint manifest from previous 3-party version on hostpath PV | basic |
| clean_previous_sprint_pv                                 | 14-Clean [PREVIOUS_SPRINT] PV | Clean Deploy with previous sprint manifest on hostpath PV | basic |
| upgrade_from_previous_sprint_to_latest_sprint_pv         | 15-Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT] PV | Rolling Update to latest sprint manifest from previous sprint on hostpath PV | basic |
| clean_latest_sprint_pv                                   | 16-Clean [LATEST_SPRINT] PV | Clean Deploy with latest sprint manifest on hostpath PV | basic |
| clean_previous_sprint_restricted                         | 17-Clean [PREVIOUS_SPRINT] Restricted | Clean Deploy with previous sprint manifestin restricted mode | basic | 
| upgrade_from_previous_sprint_to_latest_sprint_restricted | 18-Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT] Restricted | Rolling Update to latest sprint manifest from previous sprint in restricted mode | basic |
| clean_latest_sprint_restricted                           | 19-Clean [LATEST_SPRINT] Restricted | Clean Deploy with latest sprint manifest in restricted mode | basic | 
| clean_latest_sprint_w/o_components                       | 20-Clean [LATEST_SPRINT] W/O Components | Clean Deploy of latest sprint version with minimal deployment config | full |
| upgrade_latest_sprint_all_components_s3_drd              | 21-Upgrade [LATEST_SPRINT] All Components S3 DRD | Update with latest sprint manifest with all components, S3 and DRD | full |
| clean_latest_sprint_s3                                   | 22-Clean [LATEST_SPRINT] S3 | Clean Deploy of latest sprint version with S3 | full |
| upgrade_latest_sprint_custom_creds                       | 23-Upgrade [LATEST_SPRINT] Custom Creds | Rolling Update with latest sprint manifest with updated creds | basic |
| clean_latest_sprint_s3_drd_tls-secrets                   | 24-Clean [LATEST_SPRINT] S3 DRD TLS Secrets | Clean Deploy of latest sprint version with enabled TLS using pre-created secrets, DRD and S3 | basic |
| upgrade_latest_sprint_s3_drd_tls-certs                   | 25-Upgrade [LATEST_SPRINT] S3 DRD TLS Certs | Rolling Update latest sprint manifest with enabled TLS using specified certificates, DRD and S3 | basic |
| clean_latest_sprint_s3_drd                               | 26-Clean [LATEST_SPRINT] S3 DRD | Clean Deploy of latest sprint version with enabled DRD and S3 | full |
| upgrade_latest_sprint_from_non-tls_to_tls_s3_drd         | 27-Upgrade [LATEST_SPRINT] From Non-TLS To TLS S3 DRD | Rolling Update latest sprint manifest with enabled TLS using cert-manager, DRD and S3 | basic |
| clean_latest_sprint_s3_drd_tls                           | 28-Clean [LATEST_SPRINT] TLS S3 DRD | Clean Deploy of latest sprint version with enabled TLS using cert-manager, DRD and S3 | full |
| clean_latest_sprint_full-at_custom-labels_nodeport       | 29-Clean [LATEST_SPRINT] Full-AT Custom-Labels Nodeport | Clean Deploy of latest sprint version with full scope AT, custom labels and nodeport | basic |
<!-- markdownlint-enable line-length -->

# Streaming
## Streaming variables
<!-- markdownlint-disable line-length -->
| Variable         | Description                                                                         |
|------------------|-------------------------------------------------------------------------------------|
| N2_RELEASE | Previous-previous release manifest (n-2, where n – actual release) for Deployer | 
| N1_RELEASE  | Previous release manifest (n-1, where n – actual release) for Deployer          | 
| PREVIOUS_SPRINT      | Previous sprint manifest for Deployer                                           | 
| LATEST_SPRINT      | New sprint manifest for Deployer                                                | 
| KAFKA_PROJECT    | Kafka projest name                                                                  |
| KAFKA_VERSION    | Kafka version                                                                       |
| DEPLOY_SCHEME    | `Basic` or `full`. Set `basic` to run only basic jobs, `full` to run all jobs       |
| LATEST_SPRINT_TAG              | Tag (branch name) name with CRD for new sprint                                      | 
| PREVIOUS_SPRINT_TAG          | Tag (branch name) name with CRD for previous sprint                                      | 
<!-- markdownlint-enable line-length -->

## Streaming jobs list
<!-- markdownlint-disable line-length -->
| Stage                                             | Job                                                                | Description                                                                                                               | Deploy Scheme |
|---------------------------------------------------|--------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------|-------------|
| clean_previous_sprint                         | 1-Clean [PREVIOUS_SPRINT]                              | Clean Deploy job with previous sprint manifest                                                                            | basic       |
| upgrade_from_previous_sprint_to_latest_sprint                        | 2-Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT]                                | Rolling Update job to latest sprint manifest from previous sprint                                                                   | basic       |
| clean_latest_sprint                             | 3-Clean [LATEST_SPRINT]                                          | Clean Deploy with latest manifest                                                                                            | basic       |
| upgrade_latest_sprint_diff_params_full_at | 4-Upgrade [LATEST_SPRINT] Diff Params Full-AT | Rolling Update with same manifest from previous step, but with changed deployment config and full-AT                                 | basic       |
| clean_n1_release                        | 5-Clean [N1_RELEASE]                             | Clean Deploy with previous release manifest                                                                               | full        |
| upgrade_from_n1_release_to_latest_sprint               | 6-Upgrade From [N1_RELEASE] To [LATEST_SPRINT]                | Rolling Update from previous release manifest to latest sprint manifest                                                             | full        |
| clean_n2_release                    | 7-Clean [N2_RELEASE]                         | Clean Deploy with previous-previous release manifest (n-2, where n – actual release)                                      | full        |
| upgrade_from_n2_release_to_latest_sprint           | 8-Upgrade From [N2_RELEASE] To [LATEST_SPRINT]                | Rolling Update to latest sprint manifest from n-2 manifest                                                                          | full        |
| clean_latest_sprint_infra_pasport                             | 9-Clean [LATEST_SPRINT] Infra Passport                                      | Clean Deploy infra passport with latest sprint manifest                                                                                            | basic       |
| clean_previous_sprint_restricted                  | 10-Clean [PREVIOUS_SPRINT] Restricted                             | Clean Deploy job with previous sprint manifest in restricted mode                                                          | basic       |
| upgrade_from_previous_sprint_to_latest_sprint_restricted              | 11-Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT] Restricted                         | Rolling Update job to latest sprint manifest from previous sprint in restricted mode                                                | basic       | 
| clean_latest_sprint_restricted                  | 12-Clean [LATEST_SPRINT] Restricted                              | Clean Deploy with latest sprint manifest in restricted mode                                                                         | basic       | 
| clean_latest_sprint_without_components                      | 13-Clean [LATEST_SPRINT] W/O Components                               | Clean Deploy of latest sprint version with minimal deployment config                                                                | full        |
| upgrade_latest_sprint_from_1_to_3_replicas                         | 14-Upgrade [LATEST_SPRINT] From 1 To 3 Replicas                                 | Rolling Update with latest sprint manifest from 1 to 3 streaming replicas                                                                  | full       |
| clean_latest_sprint_connector_crd                           | 15-Clean [LATEST_SPRINT] Connector CRD                   | Clean of latest sprint version with connector configurator on CRD                                                           | full        |
| upgrade_latest_sprint_custom_creds                         | 16-Upgrade [LATEST_SPRINT] Custom Creds                                    | Rolling Update with latest sprint manifest with updated creds                                                                       | full       |
| clean_latest_sprint_non_tls                         | 17 - Clean [LATEST_SPRINT] non TLS                             | Clean Deploy job with latest sprint manifest and TLS disabled                                                                           | full       |
| upgrade_latest_sprint_from_non_tls_to_tls                        | 18 - Upgrade [LATEST_SPRINT] From non-TLS To TLS                              | Rolling Update job to latest sprint manifest and TLS enabled                                                          | full       |
| clean_latest_sprint_tls                         | 19-Clean [LATEST_SPRINT] TLS                             | Clean Deploy job with latest sprint manifest and TLS enabled                                                                           | full       |
| upgrade_latest_sprint_from_tls_to_non_tls                        | 20-Upgrade [LATEST_SPRINT] From TLS To Non-TLS                             | Rolling Update job to latest manifest and TLS disabled                                                          | full       |
| clean_latest_sprint_drd_tls_secrets                         | 21-Clean [LATEST_SPRINT] DRD TLS Secrets                            | Clean Deploy job with latest sprint manifest, DRD enabled and pre-created secrets with TLS certificates                                                                           | full       |
| upgrade_latest_sprint_drd_from_tls_secrets_to_tls_certs                        | 22-Upgrade [LATEST_SPRINT] DRD From TLS Secrets To TLS Cetificates                           | Rolling Update job to latest sprint manifest and TLS certificates specified in parameters                                                          | full       |
| clean_latest_sprint_profiler_jaeger_integration                           | 23-Clean [LATEST_SPRINT] Profiler Jaeger Integration                 | Clean of latest sprint version with Profiler and Jaeger integration. Job launched manually                                                           | full        |
| clean_kafka_latest_sprint_with_tls                          | 24-Clean Kafka [LATEST_SPRINT] With TLS                                    | Clean Deploy kafka with TLS for installing streaming with kafka. Job is avaliabliable only if `KAFKA_VERSION` isn't empty | basic       | 
| clean_latest_sprint_full_at_tls_with_tls_kafka                          | 25-Clean [LATEST_SPRINT] Full-AT TLS With TLS Kafka                               | Clean Deploy of latest sprint version with kafka with TLS and full-AT enabled. Job is available only if `KAFKA_VERSION` isn't empty                          | basic       |
<!-- markdownlint-enable line-length -->

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

# Elasticsearch
## Elasticsearch variables
<!-- markdownlint-disable line-length -->
| Variable      | Description                               |
|---------------|-------------------------------------------|
| PYTHON_IMAGE  |                                           |
| PREVIOUS_SPRINT   | Previous sprint manifest for Deployer | 
| LATEST_SPRINT   | New sprint manifest for Deployer      | 
| MAN_DP_OLD    | Previous sprint manifest for DP Deployer  | 
| MAN_DP_NEW    | New sprint manifest for DP Deployer       | 
<!-- markdownlint-enable line-length -->

## Elasticsearch jobs list
<!-- markdownlint-disable line-length -->
| Stage                          | Job               | Description |
|--------------------------------|-------------------|-------------|
| app_clean_install_old          | elasticsearch-1   |             |
| app_upgrade_to_current_version | elasticsearch-2   |             |
| clear_namespace_1              | elasticsearch-3   |             |
| app_clean_install              | elasticsearch-4   |             |
| app_upgrade                    | elasticsearch-5   |             |
| clear_namespace_2              | elasticsearch-6   |             |
| dp_clean_install               | elasticsearch-7   |             |
| dp_upgrade                     | elasticsearch-8   |             |
<!-- markdownlint-enable line-length -->

# Opendistro
## Opendistro variables
<!-- markdownlint-disable line-length -->
| Variable      | Description                               |
|---------------|-------------------------------------------|
| PYTHON_IMAGE  |                                           |
<!-- markdownlint-enable line-length -->

## Opendistro jobs list
<!-- markdownlint-disable line-length -->
| Stage                                 | Job           | Description |
|---------------------------------------|---------------|-------------|
| distro_app_clean_install_old          | OpenDistro-1  |             |
| distro_app_upgrade_to_current_version | OpenDistro-2  |             |
| k8s_clear_namespace_1                 | OpenDistro-3  |             |
| distro_app_clean_install              | OpenDistro-4  |             |
| distro_app_upgrade                    | OpenDistro-5  |             |
| k8s_clear_namespace_2                 | OpenDistro-6  |             |
| distro_dp_clean_install               | OpenDistro-7  |             |
| distro_dp_upgrade                     | OpenDistro-8  |             |
| OS_clear_namespace_3                  | OpenDistro-9  |             |
| distro_OS_app_clean_install           | OpenDistro-10 |             |
| distro_OS_app_upgrade                 | OpenDistro-11 |             |
<!-- markdownlint-enable line-length -->
