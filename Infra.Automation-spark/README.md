# Quick Start Guide
This mini guide contains an explanation of how to launch an Spark pipeline for check deployment cases and an explanation of stages and variables that need to be configured before launching.

## How to run Spark pipeline
This pipeline has been already configured with different deploy cases and stages. 
It's possible to run pipeline for deploy to 3 clouds: `qa_kubernetes`, `fenrir` and `ocp_cert_1`. 

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
  PROJECT: spark
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
  PROJECT: spark
```
For run pipeline to `fenrir` cloud following parameters under `fenrir configuration` comment should be uncommented:
```
  PREFIX: fenrir_orchestration
  JENKINS_URL: ''
  JENKINS_USER: ''
  JENKINS_PASS: ''
  CREDS_IN_DEPLOYER: ''
  RESTRICTED_USER_APP: ''
  CLOUD_HOST_OVERALL: ${FENRIR_KUBER_HOST}
  CLOUD_TOKEN_OVERALL: ${FENRIR_KUBER_TOKEN}
  PROJECT: spark
```

`Pay Attention` only ONE configuration block can be uncommented, others should be commented out.



After committing changes, pipeline will be run automatically.

For run a new pipeline without changes open `CI/CD` -> `Pipelines` in sidebar and click on button `Run Pipeline`. After this select branch `spark` and click on `Run Pipeline` button again.

## Variables
<!-- markdownlint-disable line-length -->
| Variable                           | Description                                                                                            |
|------------------------------------|--------------------------------------------------------------------------------------------------------|
| PREVIOUS_SPRINT            | Previous sprint manifest for Deployer.                                                             |
| LATEST_SPRINT                 | New sprint manifest for Deployer.                                                                  |
| N1_RELEASE    | Previous release manifest (n-1, where n – actual release) for Deployer.                            |
| N2_RELEASE | Previous-previous release manifest (n-2, where n – actual release)  for Deployer.                  |
| LATEST_SPRINT_TAG                                | Tag (branch name) name with CRD for new sprint                                                         |
| PREVIOUS_SPRINT_TAG                            | Tag (branch name) with CRD for previous sprint                                                         |
<!-- markdownlint-enable line-length -->


## Jobs list
<!-- markdownlint-disable line-length -->
| Stage                                     | Job                                                             | Description                                                                                   |
|-------------------------------------------|-----------------------------------------------------------------|-----------------------------------------------------------------------------------------------|
| clean_previous_sprint                     | Clean [PREVIOUS_SPRINT]                                         | Clean Deploy job with previous sprint manifest.                                               | 
| upgrade_from_previous_to_latest           | 2-Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT]             | Rolling Update job to new manifest from previous sprint.                                      | 
| clean_latest_sprint                       | 3-Clean [LATEST_SPRINT]                                         | Clean Deploy with new manifest.                                                               |
| upgrade_to_latest_diff_params             | 4-Upgrade [LATEST_SPRINT] Diff Params                           | Rolling Update with same manifest from previous step, but with changed deployment parameters. | 
| clean_n1_release                          | 5-Clean [N1_RELEASE]                                            | Clean Deploy with previous release manifest.                                                  | 
| upgrade_from_n1_to_latest                 | 6-Upgrade From [N1_RELEASE] To [LATEST_SPRINT]                  | Rolling Update from previous release manifest to new manifest.                                |
| clean_n2_release                          | 7-Clean [N2_RELEASE]                                            | Clean Deploy with previous-previous release manifest (n-2, where n – actual release).         |
| upgrade_from_n2_to_latest                 | 8-Upgrade From [N2_RELEASE] To [LATEST_SPRINT]                  | Rolling Update to new manifest from n-2 manifest.                                             |
| clean_latest_sprint_without_components    | 9-Clean [LATEST_SPRINT] W/O Components                          | Clean Deploy with minimal set of parameters                                                   |
| clean_previous_sprint_restricted          | 10-Clean [PREVIOUS_SPRINT] Restricted                           | Restricted clean Deploy with previous manifest.                                               |
| update_from_previous_to_latest_restricted | 11-Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT] Restricted | Restricted update Deploy with new manifest.                                                   |
| clean_latest_sprint_restricted            | 12-Clean [LATEST_SPRINT] Restricted                             | Restricted clean Deploy with new manifest.                                                    | 
| clean_latest_sprint_tls_issuer            | 13-Clean [LATEST_SPRINT] TLS ClusterIssuer                      | Clean Deploy with tls issuer in ingress annotation                                            | 
| update_latest_sprint_tls_cert             | 14-Update [LATEST_SPRINT] TLS CertManager                       | Clean Deploy with certManagerInegration                                                       | 
<!-- markdownlint-enable line-length -->
