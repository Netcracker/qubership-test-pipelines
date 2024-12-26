# Quick Start Guide

## How to run Azure pipeline
1. Check parameters are empty in .
2. Check [`services_specific.yml`](http://***.***.***.***/qa-group/azure-pipeline/-/blob/main/configuration/services_specific.yml) file.
Attention! If \<Service\>_version is not empty, value from CCI will be overridden!
3. Add correct value to `RELEASE` variable.
4. Commit changes or run pipeline in gl.
5. Run job `CCI Integration` to get versions from CCI
6. Run job `Start AKS Cluster` to start AKS (if it isn't enabled)
7. To deploy logging you need to start [`logging-vm`] manually before job
8. Patch for ClickHouse (clean): 
```
kubectl patch ClickHouseInstallation cluster --type json -p '[{"op": "replace", "path": "/metadata/finalizers", "value": null}]' -n clickhouse
```

## Variables
<!-- markdownlint-disable line-length -->
| Variable                        | Description                                                                                                                                           |
|---------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------| 
| CCI_INTEGRATION                 | Integration with CCI. It is possible to override services versions in `services_specific.yml`. If "false" jobs get value from `services_specific.yml` |
| IGNORE_ERRORS                   | Is used with `CCI_INTEGRATION="true"`. If versions are not found for all services, "env_cci" artifact will still be created                           |
| RELEASE                         | Release name                                                                                                                                          |
| DEPLOY_MODE                     | Deploy mode in deployer. Possible values: `Clean` or `Rolling Update`                                                                         |
<!-- markdownlint-enable line-length -->

## Variables in services_specific.yml

<!-- markdownlint-disable line-length -->
| Variable             | Description                                                                                                     | Example                                                                                                |
|----------------------|-----------------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------|
| \<Service\>_version  | Descriptor version. If <Service>_version is not empty, service is deployed with version from <Service>_version. | Kafka_version: "";  Kafka_version: release-2024.3-1.8.2-delivery_kafka_3.7.0-20240910.064115-1-RELEASE |
| \<Service\>_ns       | Namespace, where service will be deployed                                                                       | Kafka_ns: kafka-service                                                                                |
| \<Service\>_install  | If "true" service will be deployed                                                                              | Kafka_install: "true"                                                                                  |
| \<Service\>_app_name | Application name for service. "-" replaced with "_"                                                             | Kafka_app_name: kafka_services                                                                         |
<!-- markdownlint-enable line-length -->




