# Quick Start Guide
This mini guide contains an explanation of how to launch a Logging pipeline for check deployment cases and an explanation of stages and variables that need to be configured before launching.

## How to run Logging pipeline
This pipeline has been already configured with different deploy cases and stages. 
It's possible to run pipeline for deploy to 2 clouds: `qa_kubernetes` and `ocp_cert_1`. 

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
  PROJECT: logging-operator 
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
  PROJECT: logging-operator 
```

`Pay Attention` only ONE configuration block can be uncommented, another should be commented out.



After committing changes, pipeline will be run automatically.

For run a new pipeline without changes open `CI/CD` -> `Pipelines` in sidebar and click on button `Run Pipeline`. After this select branch `logging-automated` and click on `Run Pipeline` button again.

## Variables
<!-- markdownlint-disable line-length -->
| Variable                 | Description                                                                                        |
|--------------------------|----------------------------------------------------------------------------------------------------|
| N2_RELEASE               | Previous-previous release manifest (n-2, where n – actual release)  for Deployer (Graylog 5)   |
| N1_RELEASE               | Previous release manifest (n-1, where n – actual release) for Deployer (Graylog 5)             |
| PREVIOUS_SPRINT          | Previous sprint manifest for Deployer (Graylog 5)                                              |
| LATEST_SPRINT            | New sprint manifest for Deployer (Graylog 5)                                                   |
| GR4_LATEST               | Graylog 4 latest version                                                                           |
| SCHEME_GRAYLOG_FLUENTD   | Deploy scheme with internal graylog and fluentd. Set `true` to run jobs according to this scheme   |
| SCHEME_GRAYLOG_FLUENTBIT | Deploy scheme with internal graylog and fluentbit. Set `true` to run jobs according to this scheme |
| SCHEME_ONLY_FLUENTD      | Deploy scheme with fluentd only. Set `true` to run jobs according to this scheme                   |
| SCHEME_ONLY_FLUENTBIT    | Deploy scheme with fluentbit only. Set `true` to run jobs according to this scheme                 |
| SCHEME_HA                | HA deploy scheme. Set `true` to run jobs according to this scheme                                  |
| LATEST_SPRINT_TAG         | Tag (branch name) name with CRD for new sprint                                                     |
| PREVIOUS_SPRINT_TAG      | Tag (branch name) with CRD for previous sprint                                                     |
<!-- markdownlint-enable line-length -->

## Jobs list
 **Internal Graylog With Fluentd**              
<!-- markdownlint-disable line-length -->
| Stage                                   | Job                                                                             | Description                                                                               | Job is avaliable                                  |
|-----------------------------------------|---------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------|---------------------------------------------------|
| gr_fld_clean_previous_sprint            | 1-Graylog Fluentd Clean [PREVIOUS_SPRINT]                                       | Clean Deploy job with previous sprint manifest                                            | if variable `$SCHEME_GRAYLOG_FLUENTD` is "true"   |
| gr_fld_update_to_latest                 | 2-Graylog Fluentd Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT]             | Rolling Update job to new manifest from previous sprint                                   | if variable `$SCHEME_GRAYLOG_FLUENTD` is "true"   |
| gr_fld_clean_latest                     | 3-Graylog Fluentd Clean [LATEST_SPRINT]                                         | Clean Deploy with new manifest                                                            | if variable `$SCHEME_GRAYLOG_FLUENTD` is "true"   |
| gr_fld_upgrade_latest_diff_params       | 4-Graylog Fluentd Upgrade [LATEST_SPRINT] Diff Params                           | Rolling Update with same manifest from previous step, but with changed deployment config. | if variable `$SCHEME_GRAYLOG_FLUENTD` is "true"   |
| gr_fld_clean_n1_release                 | 5-Graylog Fluentd Clean [N1_RELEASE]                                            | Clean Deploy with previous release manifest                                               | if variable `$SCHEME_GRAYLOG_FLUENTD` is "true"   |
| gr_fld_upgrade_from_n1_to_latest_sprint | 6-Graylog Fluentd Upgrade From [N1_RELEASE] To [LATEST_SPRINT]                  | Rolling Update from previous release manifest to new manifest                             | if variable `$SCHEME_GRAYLOG_FLUENTD` is "true"   |
| gr_fld_clean_n2_release                 | 7-Graylog Fluentd Clean [N2_RELEASE]                                            | Clean Deploy with previous-previous release manifest (n-2, where n – actual release)      | if variable `$SCHEME_GRAYLOG_FLUENTD` is "true"   |
| gr_fld_upgrade_from_n2_to_latest_sprint | 8-Graylog Fluentd Upgrade From [N2_RELEASE] To [LATEST_SPRINT]                  | Rolling Update to new manifest from n-2 manifest.                                         | if variable `$SCHEME_GRAYLOG_FLUENTD` is "true"   |
| gr_fld_clean_previous_sprint_restricted | 9-Graylog Fluentd Restricted Clean [PREVIOUS_SPRINT]                            | Clean Deploy with previous sprint manifest in restricted mode.                            | if variable `$SCHEME_GRAYLOG_FLUENTD` is "true"   |
| gr_fld_update_to_latest_restricted      | 10-Graylog Fluentd Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT] Restricted | Rolling Update to new manifest from previous sprint manifest in restricted mode.          | if variable `$SCHEME_GRAYLOG_FLUENTD` is "true"   |
| gr_fld_clean_latest_sprint_restricted   | 11-Graylog Fluentd Clean [PREVIOUS_SPRINT] Restricted                           | Clean Deploy with new manifest in restricted mode                                         | if variable `$SCHEME_GRAYLOG_FLUENTD` is "true"   |
| gr_clean_latest_tls                     | 50-Graylog Clean [LATEST_SPRINT] TLS                                            | Clean Deploy new manifest in  in tls mode                                                 | if variable `$SCHEME_GRAYLOG_FLUENTD` is "true"   |
**Internal Graylog With Fluentbit**
<!-- markdownlint-disable line-length -->
| Stage                                   | Job                                                                               | Description                                                                               | Job is avaliable                                  |
|-----------------------------------------|-----------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------|---------------------------------------------------|
| gr_flb_clean_previous_sprint            | 12-Graylog Fluentbit Clean [PREVIOUS_SPRINT]                                      | Clean Deploy job with previous sprint manifest                                            | if variable `$SCHEME_GRAYLOG_FLUENTBIT` is "true" |
| gr_flb_update_to_latest                 | 13-Graylog Fluentbit Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT]            | Rolling Update job to new manifest from previous sprint                                   | if variable `$SCHEME_GRAYLOG_FLUENTBIT` is "true" |
| gr_flb_clean_latest                     | 14-Graylog Fluentbit Clean [LATEST_SPRINT]                                        | Clean Deploy with new manifest                                                            | if variable `$SCHEME_GRAYLOG_FLUENTBIT` is "true" |
| gr_flb_upgrade_latest_diff_params       | 15-Graylog Fluentbit Upgrade [LATEST_SPRINT] Diff Params                          | Rolling Update with same manifest from previous step, but with changed deployment config. | if variable `$SCHEME_GRAYLOG_FLUENTBIT` is "true" |
| gr_flb_clean_n1_release                 | 16-Graylog Fluentbit Clean [N1_RELEASE]                                           | Clean Deploy with previous release manifest                                               | if variable `$SCHEME_GRAYLOG_FLUENTBIT` is "true" |
| gr_flb_upgrade_from_n1_to_latest_sprint | 17-Graylog Fluentbit Upgrade From [N1_RELEASE] To [LATEST_SPRINT]                 | Rolling Update from previous release manifest to new manifest                             | if variable `$SCHEME_GRAYLOG_FLUENTBIT` is "true" |
| gr_flb_clean_n2_release                 | 18-Graylog Fluentbit Clean [N2_RELEASE]                                           | Clean Deploy with previous-previous release manifest (n-2, where n – actual release)      | if variable `$SCHEME_GRAYLOG_FLUENTBIT` is "true" |
| gr_flb_upgrade_from_n2_to_latest_sprint | 19-Graylog Fluentbit Upgrade From [N2_RELEASE] To [LATEST_SPRINT]                 | Rolling Update to new manifest from n-2 manifest.                                         | if variable `$SCHEME_GRAYLOG_FLUENTBIT` is "true" |
| gr_flb_clean_previous_sprint_restricted | 20-Graylog Fluentbit Restricted Clean [PREVIOUS_SPRINT]                           | Clean Deploy with previous sprint manifest in restricted mode.                            | if variable `$SCHEME_GRAYLOG_FLUENTBIT` is "true" |
| gr_flb_update_to_latest_restricted      | 21-Graylog Fluentbit Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT] Restricted | Rolling Update to new manifest from previous sprint manifest in restricted mode.          | if variable `$SCHEME_GRAYLOG_FLUENTBIT` is "true" |
| gr_flb_clean_latest_sprint_restricted   | 22-Graylog Fluentbit Clean [PREVIOUS_SPRINT] Restricted                           | Clean Deploy with new manifest in restricted mode                                         | if variable `$SCHEME_GRAYLOG_FLUENTBIT` is "true" |
 **Only Fluentd**                          
<!-- markdownlint-disable line-length -->
| Stage                                 | Job                                                                          | Description                                                                               | Job is avaliable                                  |
|---------------------------------------|------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------|---------------------------------------------------|
| fld_clean_previous_sprint             | 23-Only Fluentd Clean [PREVIOUS_SPRINT]                                      | Clean Deploy job with previous sprint manifest                                            | if variable `SCHEME_ONLY_FLUENTD` is "true"       |
| fld_update_to_latest                  | 24-Only Fluentd Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT]            | Rolling Update job to new manifest from previous sprint                                   | if variable `SCHEME_ONLY_FLUENTD` is "true"       |
| fld_clean_latest                      | 25-Only Fluentd Clean [LATEST_SPRINT]                                        | Clean Deploy with new manifest                                                            | if variable `SCHEME_ONLY_FLUENTD` is "true" |
| fld_clean_n1_release                  | 26-Only Fluentd Clean [N1_RELEASE]                                           | Clean Deploy with previous release manifest                                               | if variable `SCHEME_ONLY_FLUENTD` is "true" |
| fld_upgrade_from_n1_to_latest_sprint  | 27-Only Fluentd Upgrade From [N1_RELEASE] To [LATEST_SPRINT]                 | Rolling Update from previous release manifest to new manifest                             | if variable `SCHEME_ONLY_FLUENTD` is "true" |
| fld_clean_n2_release                  | 28-Only Fluentd Clean [N2_RELEASE]                                           | Clean Deploy with previous-previous release manifest (n-2, where n – actual release)      | if variable `SCHEME_ONLY_FLUENTD` is "true" |
| fld_upgrade_from_n2_to_latest_sprint  | 29-Only Fluentd Upgrade From [N2_RELEASE] To [LATEST_SPRINT]                 | Rolling Update to new manifest from n-2 manifest.                                         | if variable `SCHEME_ONLY_FLUENTD` is "true" |
| fld_clean_previous_sprint_restricted  | 30-Only Fluentd Restricted Clean [PREVIOUS_SPRINT]                           | Clean Deploy with previous sprint manifest in restricted mode.                            | if variable `SCHEME_ONLY_FLUENTD` is "true" |
| fld_update_to_latest_restricted       | 31-Only Fluentd Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT] Restricted | Rolling Update to new manifest from previous sprint manifest in restricted mode.          | if variable `SCHEME_ONLY_FLUENTD` is "true" |
| fld_clean_latest_sprint_restricted    | 32-Only Fluentd Clean [PREVIOUS_SPRINT] Restricted                           | Clean Deploy with new manifest in restricted mode                                         | if variable `SCHEME_ONLY_FLUENTD` is "true" |
 **Only Fluentbit**
<!-- markdownlint-disable line-length -->
| Stage                                 | Job                                                                            | Description                                                                               | Job is avaliable                                  |
|---------------------------------------|--------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------|---------------------------------------------------|
| flb_clean_previous_sprint             | 33-Only Fluentbit Clean [PREVIOUS_SPRINT]                                      | Clean Deploy job with previous sprint manifest                                            | if variable `SCHEME_ONLY_FLUENTBIT` is "true" |
| flb_update_to_latest                  | 34-Only Fluentbit Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT]            | Rolling Update job to new manifest from previous sprint                                   | if variable `SCHEME_ONLY_FLUENTBIT` is "true" |
| flb_clean_latest                      | 35-Only Fluentbit Clean [LATEST_SPRINT]                                        | Clean Deploy with new manifest                                                            | if variable `SCHEME_ONLY_FLUENTBIT` is "true" |
| flb_clean_n1_release                  | 36-Only Fluentbit Clean [N1_RELEASE]                                           | Clean Deploy with previous release manifest                                               | if variable `SCHEME_ONLY_FLUENTBIT` is "true" |
| flb_upgrade_from_n1_to_latest_sprint  | 37-Only Fluentbit Upgrade From [N1_RELEASE] To [LATEST_SPRINT]                 | Rolling Update from previous release manifest to new manifest                             | if variable `SCHEME_ONLY_FLUENTBIT` is "true" |
| flb_clean_n2_release                  | 38-Only Fluentbit Clean [N2_RELEASE]                                           | Clean Deploy with previous-previous release manifest (n-2, where n – actual release)      | if variable `SCHEME_ONLY_FLUENTBIT` is "true" |
| flb_upgrade_from_n2_to_latest_sprint  | 39-Only Fluentbit Upgrade From [N2_RELEASE] To [LATEST_SPRINT]                 | Rolling Update to new manifest from n-2 manifest.                                         | if variable `SCHEME_ONLY_FLUENTBIT` is "true" |
| flb_clean_previous_sprint_restricted  | 40-Only Fluentbit Restricted Clean [PREVIOUS_SPRINT]                           | Clean Deploy with previous sprint manifest in restricted mode.                            | if variable `SCHEME_ONLY_FLUENTBIT` is "true" |
| flb_update_to_latest_restricted       | 41-Only Fluentbit Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT] Restricted | Rolling Update to new manifest from previous sprint manifest in restricted mode.          | if variable `SCHEME_ONLY_FLUENTBIT` is "true" |
| flb_clean_latest_sprint_restricted    | 42-Only Fluentbit Clean [PREVIOUS_SPRINT] Restricted                           | Clean Deploy with new manifest in restricted mode                                         | if variable `SCHEME_ONLY_FLUENTBIT` is "true" |
 **HA Scheme**                             
<!-- markdownlint-disable line-length -->
| Stage                                | Job                                                       | Description                                                                          | Job is avaliable                  |
|--------------------------------------|-----------------------------------------------------------|--------------------------------------------------------------------------------------|-----------------------------------|
| ha_clean_n2_release                  | 43-Ha Scheme Clean [N2_RELEASE]                           | Clean Deploy with previous-previous release manifest (n-2, where n – actual release) | if variable `SCHEME_HA` is "true" |
| ha_upgrade_from_n2_to_latest_sprint  | 44-Ha Scheme Upgrade From [N2_RELEASE] To [LATEST_SPRINT] | Rolling Update to new manifest from n-2 manifest.                                    | if variable `SCHEME_HA` is "true" |
| ha_clean_n1_release                  | 45-Ha SchemeClean [N1_RELEASE]                            | Clean Deploy with previous release manifest (n-1, where n – actual release)          | if variable `SCHEME_HA` is "true" |
| ha_upgrade_from_n1_to_latest_sprint  | 46-Ha SchemeUpgrade From [N1_RELEASE] To [LATEST_SPRINT]  | Rolling Update from previous release manifest to new manifest                        | if variable `SCHEME_HA` is "true" |
| ha_clean_previous_sprint             | 47-Ha Scheme Clean [PREVIOUS_SPRINT]                      | Clean Deploy job with previous sprint manifest                                       | if variable `SCHEME_HA` is "true" |
| ha_update_to_latest                  | 48-Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT]      | Rolling Update job to new manifest from previous sprint                              | if variable `SCHEME_HA` is "true" |
| ha_clean_latest                      | 49-Ha Scheme Clean [LATEST_SPRINT]                        | Clean Deploy with new manifest                                                       | if variable `SCHEME_HA` is "true"                                  |