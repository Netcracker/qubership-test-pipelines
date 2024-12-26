## Quick Start Guide
This mini guide contains an explanation of how to launch pipelines for check deployment cases and an explanation of stages and variables that need to be configured before launching.

## How to run pipelines

## Opensearch variables
<!-- markdownlint-disable line-length -->
| Variable              | Description                                                                         |
|-----------------------|-------------------------------------------------------------------------------------|
| N2_RELEASE            | Previous-previous release manifest (n-2, where n – actual release) for Deployer | 
| N1_RELEASE            | Previous release manifest (n-1, where n – actual release) for Deployer          | 
| PREVIOUS_SPRINT       | Previous sprint manifest for Deployer                                           | 
| LATEST_SPRINT         | New sprint manifest for Deployer                                                | 
| PREVIOUS_3PARTY       | Previous 3-party version manifest for Deployer                                  |
| DEPLOY_SCHEME         | `Basic` or `full`. Set `basic` to run only basic jobs, `full` to run all jobs       |
| LATEST_SPRINT_TAG     | Tag (branch name) name with CRD for new sprint                                      | 
| PREVIOUS_SPRINT_TAG   | Tag (branch name) name with CRD for previous sprint                                 | 
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
