# Certification pipeline for deploy Infra services via Helm

- [Pipeline Architectire](#pipeline-architecture)
- [How to run](#how-to-run)
- [Restricted installation](#restricted-installation)

## Pipeline Architectire

The following list displays the step by step architecture of certification pipeline via helm:

1. Get Service versions from CCI if `CCI_INTEGRATION == "true"`, otherwise versions must be specified in `apps_configuration/applications.yml`.

2. Deploy Service via Helm:

- prepare ns (kubectl delete/create);
- get version of service to be deployed;
- get images from DD file from artifactory;
- modify deploy parameters template with images;
- modify deploy parameters template with cloud specific parameters;
- download and unzip chart;
- prepare CRDs;
- helm install chart;

3. Check pods status and status of ATs.
    

## How to run

1. Configure CI/CD variable with KUBECONFIG file from cloud you work with.

2. Set this variable for `KUBECONFIG` in variables block, for example: `KUBECONFIG: $PLATCERT01_KUBECONFIG`.

3. Specify RElEASE name, for example: `RELEASE`. In case `CCI_INTEGRATION: "true"` release name must be the same as in CCI.

`Optional:` you can set up which services will be installed in `apps_configuration/maven_coordinates.yml` file.

4. Configure values for cloud specific parameters in `apps_configuration/cloud_specific.yml` file.

5. Deploy parameters located in `quickstart-samples` folder. Depends on type of cloud you should replace content of `quickstart-samples` folder from `k8s` or `ocp` folder.

6. Commit changes, pipeline will be started automatically.


## Restricted installation

Pipeline supports only installation from admin user.

