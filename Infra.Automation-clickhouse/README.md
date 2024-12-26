# Quick Start Guide
This mini guide contains an explanation of how to launch a Clickhouse pipeline for check deployment cases and an explanation of stages and variables that need to be configured before launching.

## How to run Clickhouse pipeline
This pipeline has been already configured with different deploy cases and stages. 
It's possible to run pipeline for deploy to 2 clouds: `qa_kubernetes` and `ocp_cert_1`. 

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
  PROJECT: clickhouse-test
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
  CLOUD_TOKEN_OVERALL: sha256~6uEozMa1nOT8_eePFx6c59Bh1jlnxm_PXXTzvMyQdDA
  PROJECT: clickhouse
```

`Pay Attention` only ONE configuration block can be uncommented, another should be commented out.



After committing changes, pipeline will be run automatically.

For run a new pipeline without changes open `CI/CD` -> `Pipelines` in sidebar and click on button `Run Pipeline`. After this select branch `redis` and click on `Run Pipeline` button again.
## Variables
<!-- markdownlint-disable line-length -->
| Variable            | Description                                                                                                                         |
|---------------------|-------------------------------------------------------------------------------------------------------------------------------------|
| MAN_APP_OLD         | Previous sprint manifest for Deployer                                                                                           |
| MAN_APP_NEW         | New sprint manifest for Deployer                                                                                                |
| MAN_APP_RELEASE     | Previous release manifest (n-1, where n – actual release) for Deployer                                                          |
| MAN_APP_RELEASE2    | Previous-previous release manifest (n-2, where n – actual release)  for Deployer                                                |
| UPGRADE_MAN         | Manifest for upgrade from old clickhouse version to new. If you need to run pipeline with latest clickhouse version, leave it empty | 
| RESTRICTED_USER_APP | Restricted user token                                                                                                               |
| TAG                 | Tag (branch name) name with CRD for new sprint                                                                                      |
| OLD_TAG             | Tag (branch name) with CRD for previous sprint                                                                                      |
<!-- markdownlint-enable line-length -->

Versions of clickhouse in manifests `MAN_APP_OLD`, `MAN_APP_NEW`, `MAN_APP_RELEASE`, `MAN_APP_RELEASE2` must be the same (for example, 22.8).
`UPGRADE_MAN` - manifest with new version (23.3)

## Jobs list
<!-- markdownlint-disable line-length -->
| Stage                            | Job                                                          | Description                                                                                              | Job is avaliable                                   |
|----------------------------------|--------------------------------------------------------------|----------------------------------------------------------------------------------------------------------|----------------------------------------------------|
| clean_previous_sprint            | 1 - Clickhouse Clean Previous Sprint                         | Clean Deploy job with previous sprint manifest                                                           |                                                    | 
| update_to_latest                 | 2 - Clickhouse Upgrade To Latest Version                     | Rolling Update job to new manifest from previous sprint                                                  |                                                    |
| clean_latest                     | 3 - Clickhouse Clean Latest Sprint                           | Clean Deploy with new manifest                                                                           |                                                    |
| update_with_changes_params       | 4 - Clickhouse Upgrade To Latest Version With Changed Params | Rolling Update with same manifest from previous step, but with changed deployment config                 |                                                    |
| clean_sprint_4                   | 5 - Clickhouse Clean Previous Sprint 4                       | Clean Deploy with previous release sprint 4 manifest (n-1, where n – actual release)                     |                                                    |
| update_to_latest_from_sprint_4   | 6 - Clickhouse Upgrade To Latest Version from Sprint 4       | Rolling Update from previous release manifest to new manifest                                            |                                                    |
| clean_release_n-2                | 7 - Clickhouse Clean Previous N-2                            | Clean Deploy with previous-previous release manifest (n-2, where n – actual release)                     |                                                    |
| update_to_latest_n-2             | 8 - Clickhouse Update From N-2 To Latest                     | Rolling Update to new manifest from n-2 manifest                                                         |                                                    |
| clean_latest_s3                  | 9 -  Clickhouse Clean Latest With S3                         | Clean Deploy new manifest with S3                                                                        |                                                    |
| clean_latest_tls                 | 10 - Clickhouse Clean Latest With TLS                        | Clean Deploy new manifest with enabled TLS                                                               |                                                    |
| clean_latest_hostpath_pv         | 11 - Clickhouse Clean Latest With Hostpath PV                | Clean Deploy new manifest with Hostpath PV                                                               |                                                    |
| clean_old_version_restricted     | 12 - Clickhouse Clean Old Version Restricted APP             | Clean Deploy with previous sprint manifest in restricted mode                                            | only if variable `RESTRICTED_USER_APP` isn't empty |
| update_to_new_version_restricted | 13 - Clickhouse Upgrade To New Version Restricted APP        | Rolling Update to new manifest from previous sprint manifest in restricted mode                          | only if variable `RESTRICTED_USER_APP` isn't empty |
| clean_new_version_restricted     | 14 - Clickhouse Clean New Version Restricted APP             | Clean Deploy with new manifest in restricted mode                                                        | only if variable `RESTRICTED_USER_APP` isn't empty |
| clean_old_228_for_upgrade        | 15 - Clickhouse Clean For Upgrade Version                    | Clean Deploy with previous sprint manifest of old clickhouse (22.8) for upgrade to new clickhouse (23.3) | only if variable `UPGRADE_MAN` isn't empty         |
| upgrade_to_233_latest_version    | 16 - Clickhouse Upgrade Version                              | Rolling Update to latest version of new clickhouse (23.3)                                                | only if variable `UPGRADE_MAN` isn't empty         |
<!-- markdownlint-enable line-length -->
