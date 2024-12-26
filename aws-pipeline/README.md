# Quick Start Guide

## How to run AWS pipeline
1. Check parameters are empty in .
2. Check [`services_specific.yml`](http://***.***.***.***/qa-group/aws-pipeline/-/blob/main/configuration/services_specific.yml) file.
Attention! If \<Service\>_version is not empty, value from CCI will be overridden!
3. Add correct value to `RELEASE` variable.
4. Check AWS managed URLs are correct if managed services are already created.
Attention! Managed services with label CLPL-AUTOMATIZATION will be deleted automatically
5. Check AWS managed services versions. 
If variables `AWS_MANAGED_OPENSEARCH_VERSION`, `AWS_MANAGED_MSK_VERSION`, `AWS_MANAGED_MQ_VERSION` exist, versions in templates will be overridden.
6. Commit changes or run pipeline in gl.
7. Run job `CCI Integration` to get versions from CCI
8. Run job `Start EKS Cluster In AWS` to start EKS (if it isn't enabled)

## Variables
<!-- markdownlint-disable line-length -->
| Variable                        | Description                                                                                                                                           |
|---------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------|
| DELETE_PIPELINE                 | If "true", pipeline only with job for deleting services will be run                                                                                   |
| CCI_INTEGRATION                 | Integration with CCI. It is possible to override services versions in `services_specific.yml`. If "false" jobs get value from `services_specific.yml` |
| IGNORE_ERRORS                   | Is used with `CCI_INTEGRATION="true"`. If versions are not found for all services, "env_cci" artifact will still be created                           |
| RELEASE                         | Release name                                                                                                                                          |
| DEPLOY_MODE                     | Deploy mode in deployer. Possible values: `Clean` or `Rolling Update`                                                                         |
| AWS_MANAGED_OPENSEARCH_URL      | OpenSearch managed service URL. Is used only if `Create Amazon OpenSearch Instance In AWS` failed or wasn't started                                   |
| AWS_MANAGED_KAFKA_URL           | Kafka managed service URL. Is used only if `Create Amazon MSK Instance In AWS` failed or wasn't started.                                              |
| AWS_MANAGED_RABBIT_URL          | Rabbit managed service URL. Is used only if `Create Amazon MQ Instance In AWS` failed or wasn't started.                                              | 
| AWS_MANAGED_RABBIT_CLUSTER_NAME | Rabbit cluster name. Is used only if `Create Amazon MQ Instance In AWS` failed or wasn't started.                                                     |
| AWS_MANAGED_OPENSEARCH_VERSION  | Opensearch managed service version. If variable exists, version in template will be overridden.                                                       |
| AWS_MANAGED_MSK_VERSION         | Kafka managed service version. If variable exists, version in template will be overridden.                                                            |
| AWS_MANAGED_MQ_VERSION          | Rabbit managed service version. If variable exists, version in template will be overridden.                                                           |
<!-- markdownlint-enable line-length -->

## Variables in services_specific.yml

<!-- markdownlint-disable line-length -->
| Variable             | Description                                                                                                     | Example                        |
|----------------------|-----------------------------------------------------------------------------------------------------------------|--------------------------------|
| \<Service\>_version  | Descriptor version. If <Service>_version is not empty, service is deployed with version from <Service>_version. | Kafka_version: ""              |
| \<Service\>_ns       | Namespace, where service will be deployed                                                                       | Kafka_ns: kafka-service        |
| \<Service\>_install  | If "true" service will be deployed                                                                              | Kafka_install: "true"          |
| \<Service\>_app_name | Application name for service. "-" replaced with "_"                                                             | Kafka_app_name: kafka_services |
<!-- markdownlint-enable line-length -->




