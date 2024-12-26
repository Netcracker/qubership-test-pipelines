# Infra.Automation
Repository for developments in Automation of Cloud Platform.

## Pipelines for certification
|Branch|Description|Additional info|
|---|---|---|
|`certification_v1`|Pipeline for deploy all infra services via Deployer (from admin or restricted).|[README.md]|
|`helm`|Pipeline for deploy all infra services via Helm|[README.md]|

`NOTE:` `certification_v1` can be used for certification process of services on Kubernetes and Ocp clouds. `helm` is used for the same reason, but like first stage when Deployer is not adopted for the new version of cloud.

## Regression installation pipelines
|Branch|Description|Additional info|
|---|---|---|
|`Core_Framework`|Pipeline for regression cases for SaQs services.|[README.md]|
|`postgres`|Pipeline for regression cases for PostgreSQL service.|[README.md] |
|`arangodb`|Pipeline for regression cases for ArangoDB service.|[README.md] |
|`clickhouse`|Pipeline for regression cases for ClickHouse service.|[README.md] |
|`greenplum`|Pipeline for regression cases for GreenplumDB service.|[README.md] |
|`mongo`|Pipeline for regression cases for MongoDB service.|[README.md] |
|`cassandra`|Pipeline for regression cases for Cassandra service.|[README.md] |
|`redis`|Pipeline for regression cases for Redis service.|[README.md] |
|`monitoring`|Pipeline for regression cases for Monitoring service.|[README.md] |
|`logging-automated`|Pipeline for regression cases for Logging service.|[README.md] |
|`profiler-automated`|Pipeline for regression cases for Profiler service.|[README.md] |
|`jaeger`|Pipeline for regression cases for Jaeger service.|[README.md] |
|`ams`|Pipeline for regression cases for AMS service.|[README.md] |
|`airflow`|Pipeline for regression cases for Airflow service.|[README.md] |
|`spark`|Pipeline for regression cases for Spark service.|[README.md] |
|`Mistral`|Pipeline for regression cases for Mistral service.|[README.md] |
|`cert_and_site_managers_pipeline`|Pipeline for regression cases for Cert And Site Manager service.|[README.md] |



## Additional libs/scripts
|Branch|Description|Additional info|
|---|---|---|
|`pipe_image`|Libs for work with cloud cluster resources and VMs via SSH. Script for check status of pods, count of restart and parsing logs to find error.|[ExternalPlatformLib.py]|
|`app_for_clean`|App for clean up resources in namespace and patching PVs. Also, there is possibility to clean PV data on nodes.|[Web UI](http://flask-app-for-clean.test-app.qa-kubernetes.openshift.sdntest.qubership.org/)|
