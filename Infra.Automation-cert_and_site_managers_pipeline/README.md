# Infra.Automation
Repository for developments in Automation of Cloud Platform.

## Branches description
|Branch|Description|Additional info|
|---|---|---|
|`restricted_pipe_v2`|Pipeline for deploy services via restricted user.|[README.md]|
|`image_for_paramiko`|Repo for build docker image with Paramiko library for work via SSH|[Dockerfile]|
|`app_for_clean`|App for clean up resources in namespace and patching PVs. Also, there is possibility to clean PV data on nodes.|[Web UI](http://flask-app-for-clean.test-app.qa-kubernetes.openshift.sdntest.qubership.org/)|
|`pipe_image`|Libs for work with cloud cluster resources and VMs via SSH. Script for check status of pods, count of restart and parsing logs to find error.|[ExternalPlatformLib.py]|
|`gke_tests_only`|Pipeline for run services tests in any cloud.|[README.md]|
|`run_dr_k8s`|Pipeline for run DR cases in k8s (switchover, failover, activate).|[Script]|
|`kuber_regression_pipeline`|Pipeline for run regress cases for k8s (deploy, maintenance).|[.gl-ci.yml]|
|`examples`|Examples of parameters for deploy services in different clouds.|[Repo]|
|`service pipelines`|Links to service pipelines.|[PostgreSQL]|


