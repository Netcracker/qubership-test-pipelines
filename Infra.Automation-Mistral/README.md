# Quick Start Guide
This mini guide contains an explanation of how to launch a pipeline with deployments and an explanation of stages and variables that need to be configured before launching

## How to run.
For running new pipeline without changes open CI/CD -> Pipelines in sidebar and click on button “Run Pipeline”. After this click on “Run Pipeline” button again.

This pipeline has been already configured with different deploy cases and stages. 
It's possible to run pipeline for deploy to 3 clouds: `qa_kubernetes_orchestration`, `fenrir` and `ocp_cert_1`. 

In order to run to `qa_kubernetes_orchestration` cloud you should uncomment following parameters under `qa_kubernetes configuration` comment:
```
  PREFIX: qa_kubernetes_orchestration
  JENKINS_URL: ''
  JENKINS_USER: ''
  JENKINS_PASS: ''
  CREDS_IN_DEPLOYER: ''
  RESTRICTED_USER_APP: ''
  CLOUD_HOST_OVERALL: ${QA_KUBER_HOST}
  CLOUD_TOKEN_OVERALL: ${QA_KUBER_TOKEN}
  PROJECT: mistral
  CORE_PROJECT: ""
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
  PROJECT: mistral
  CORE_PROJECT: cloudcore
```

For run pipeline to `ocp_cert_1` cloud following parameters under `ocp_cert_1 configuration` comment should be uncommented:
```
  PREFIX: ocp_cert_1
  JENKINS_URL: ''
  JENKINS_USER: ''
  JENKINS_PASS: ''
  CREDS_IN_DEPLOYER: ''
  RESTRICTED_USER_APP: ''
  CLOUD_HOST_OVERALL: https://api.ocp-cert-1.openshift.sdntest.qubership.org:6443
  CLOUD_TOKEN_OVERALL:
  PROJECT: mistral
  CORE_PROJECT: ""
```

`Pay Attention` only ONE configuration block can be uncommented, another should be commented out.



After committing changes, pipeline will be run automatically.

For run a new pipeline without changes open `CI/CD` -> `Pipelines` in sidebar and click on button `Run Pipeline`. After this select branch `Mistral` and click on `Run Pipeline` button again.

## Cases and stages list
1.	RollingUpdate In Clean Namespace – rolling update job in clean namespace
2.	Clean Previous Version – clean job for update to new manifest
3.	Update To New Version – update job to new manifest from previous sprint
4.	Clean New Version – clean job with new manifest
5.	Update On New Version Diff Params – update with same manifest from previous step, but with changed deployment config
6.	Clean Previous Release Version – clean job with previous sprint 4 manifest
7.	Update To Current Release Version – update job from previous release sprint 4 manifest to new manifest
8.	Clean Previous Release Version N-2 - clean job with previous-previous release sprint 4 manifest(n-2, where n – actual release)
9.	Update To Current Release Version From N-2 Release – update job to new manifest from n-2 manifest
10.	Clean Deploy Without Components – clean deploy job without any additional components
11.	Clean Previous Version Lite – clean deploy previous sprint manifest in lite scheme
12.	Update To New Version Lite – update job to new manifest from previous sprint 4 in lite scheme
13.	Clean New Version Lite – clean job with new manifest in lite scheme
14.	Clean Previous Release Version Lite - clean job with previous release sprint 4 manifest in lite scheme
15.	Update To Current Release Version Lite – update job to new manifest from previous release sprint 4 manifest in lite scheme
16.	Clean Previous Version OS – clean job with previous sprint manifest in openshift environment
17.	Update To New Version OS – update job to new manifest from previous sprint manifest in openshift environment
18.	Clean New Version OS – clean job with new manifest in openshift environment
19.	Clean Old Version Restricted APP – clean job with previous sprint manifest in restricted mode
20.	Upgrade To New Version Restricted APP – update to new manifest from previous sprint manifest in restricted mode
21.	Clean New Version Restricted APP - clean job with new manifest in restricted mode
22.	Core Namespace Install Previous Version – install mistral in namespace with deployed core services with rolling update mode, previous sprint manifest
23.	Core Namespace Update To New Version – upgrade to new manifest from previous sprint manifest, namespace with installed core services
24.	Core Namespace Install New Version - install mistral in namespace with deployed core services with rolling update mode, new manifest
Except this in stages we have 1 stage with get kubeconfig and 3 with helm uninstall job, this stages required for rollingUpdate case(1) and cases with install to core services namespace(22-24)
<!-- markdownlint-disable line-length -->
| Stage                                      | Job                                                | Description                                                                                     | Job is avaliable                                            |
|--------------------------------------------|----------------------------------------------------|-------------------------------------------------------------------------------------------------|-------------------------------------------------------------|
| get_kubeconfig                             | kubernetes_get_kubeconfig                          | required for rollingUpdate case                                                                 | if variable CORE_PROJECT isn't empty                        |
| uninstall_mistral                          | Uninstall Mistral                                  | helm uninstall job                                                                              | if variable CORE_PROJECT isn't empty                        |
| rollingupdate_in_clean_namespace           | 1-Update [LATEST_SPRINT] In Clean Namespace                   | Rolling Update In Clean Namespace – rolling update job in clean namespace|                                                             |
| clean_previous_sprint                         | 2-Clean [PREVIOUS_SPRINT]                             | Clean Previous Version – clean job for update to new manifest  |                                                             |
| upgrade_from_previous_to_latest                      | 3-Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT]   | Update To New Version – update job to new manifest from previous sprint   |                                                             |
| clean_latest_sprint                          | 4-Clean [LATEST_SPRINT]                                  | Clean New Version – clean job with new manifest     |                                                             |
| upgrade_to_latest_diff_params      | 5-Upgrade [LATEST_SPRINT] Diff Params                  | Update On New Version Diff Params – update with same manifest from previous step, but with changed deployment config|                                                             |
| clean_n1_release                     | 6-Clean [N1_RELEASE]                     | Clean Previous Release Version – clean job with previous sprint 4 manifest|                                                             |
| upgrade_from_n1_to_latest              | 7-Upgrade From [N1_RELEASE] To [LATEST_SPRINT]                  | Update To Current Release Version – update job from previous release sprint 4 manifest to new manifest                              |                                                             |
| clean_n2_release                  | 8-Clean [N2_RELEASE]                 | Clean Previous Release Version N-2 - clean job with previous-previous release sprint 4 manifest(n-2, where n – actual release)       | if variable DESCRIPTOR_FOR_PREVIOUS_RELEASE_N_2 isn't empty |
| upgrade_from_n2_to_latest              | 9-Upgrade From [N2_RELEASE] To [LATEST_SPRINT] | Update To Current Release Version From N-2 Release – update job to new manifest from n-2 manifest                                                    | if variable DESCRIPTOR_FOR_PREVIOUS_RELEASE_N_2 isn't empty |
| update_latest_sprint_tls              | 10-Update [LATEST_SPRINT] TLS | Rolling update job in tls mode                                                    | if variable DESCRIPTOR_FOR_PREVIOUS_RELEASE_N_2 isn't empty |
| clean_latest_sprint_tls              | 11-Clean [LATEST_SPRINT] TLS | Clean Deploy job in tls mode                                                     | if variable DESCRIPTOR_FOR_PREVIOUS_RELEASE_N_2 isn't empty |
| clean_latest_sprint_without_components            | 12-Clean [LATEST_SPRINT] W/O Components                    | Clean Deploy Without Components – clean deploy job without any additional components                                             |                                                             |
| clean_previous_sprint_restricted           | 16-Clean [PREVIOUS_SPRINT] Restricted                   | Clean Deploy with previous sprint manifest in restricted mode                                      | if variable RESTRICTED_USER_APP isn't empty                 |
| update_from_previous_to_latest_restricted       | 17-Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT] Restricted              | Rolling Update to new manifest from previous sprint manifest in restricted mode                         | if variable RESTRICTED_USER_APP isn't empty                 |
| clean_latest_sprint_restricted           | 18-Clean [LATEST_SPRINT] Restricted                   | Clean Deploy with new manifest in restricted mode                                                  | if variable RESTRICTED_USER_APP isn't empty                 |
| uninstall_mistral_2                        | 19-Uninstall Mistral 2                                | helm uninstall job                                                                              | if variable CORE_PROJECT isn't empty                        |
| install_previous_core                  | 20-Core Namespace Install [PREVIOUS_SPRINT]            | Upgrade to new manifest from previous sprint manifest, namespace with installed core services   | if variable CORE_PROJECT isn't empty                        |
| upgrade_from_previous_to_latest_core                 | 21-Core Namespace Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT]               | Upgrade to new manifest from previous sprint manifest, namespace with installed core services   | if variable CORE_PROJECT isn't empty                        |
| uninstall_mistral_3                        | 22-Uninstall Mistral 3                                | helm uninstall job                                                                              | if variable CORE_PROJECT isn't empty                        |
| install_latest_core                   | 23-Core Namespace Install [LATEST_SPRINT]                 | Install mistral in namespace with deployed core services with rolling update mode, new manifest | if variable CORE_PROJECT isn't empty                        |

## How to configure.
First block of variables is ‘hardcoded’ variables with the most important functions/URLs, and included next variables: PYTHON_IMAGE, JENKINS_URL, JOB_NAME_CLEAN, JOB_NAME_UPDATE, JENKINS_USER, JENKINS_PASS, DEPLOY_SCRIPT, UPGRADE_CRD_SCRIPT, APPLY_RESOURCES_SCRIPT, CLEAN_NS_SCRIPT and PATCH_NS_SCRIPT.
Do not touch all of them without an important reason, if in your cases need another deployer (cloud-deployer for example) – change all of required variables (URLs and user+password)

Next block of variables is setting up the environment where the pipeline will run cases:
* PROJECT – namespace in environment for service
* CORE_PROJECT – namespace with installed CORE services, required for cases where need install mistral to one namespace with CORE. If this variable set as “” – CORE + Mistral in 1 namespace cases will be skipped. 
* CREDS_IN_DEPLOYER – credentials for starting job in deployer, you can see and match this in URL for your deploy job
* PREFIX – prefix for deployer
* CLOUD_HOST – URL to environment, can be presented as a link to repository variable (example - ${QA_KUBER_HOST}, this is global variable for QA Kubernetes environment)
* CLOUD_TOKEN – token for auth in environment, can be presented as a link to repository variable
* RESTRICTED_USER_APP – same as CREDS_IN_DEPLOYER, but for restricted cases when you need specific grants for deploy user. If this variable set as “” – restricted cases will be skipped.

Manifest and CRD branches block:
* PREVIOUS_DESCRIPTOR_APP – manifest from previous sprint, used in cases with upgrade from previous sprint to actual
* NEW_DESCRIPTOR_APP – actual sprint manifest for test in pipeline
* DESCRIPTOR_FOR_PREVIOUS_RELEASE – manifest from previous sprint 4(previous release), used in cases with upgrade from previous sprint 4 to actual
* DESCRIPTOR_FOR_PREVIOUS_RELEASE_N_2 – manifest from previous n-2 release (n – actual release), used in cases with upgrade from n-2 sprint 4 to actual
* TAG – tag with actual CRD, in common case should be from the same branch/tag with NEW_DESCRIPTOR_APP manifest
* OLD_TAG - tag with previous CRD, in common case should be from the same branch/tag with PREVIOUS_DESCRIPTOR_APP manifest
* CHECK_MISTAL_LITE – Boolean variable for activate-deactivate mistral-lite cases in pipeline. True – lite cases will be run in pipeline, false – cases will be skipped