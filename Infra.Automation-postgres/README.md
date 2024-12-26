# Quick Start Guide
This mini guide contains an explanation how to launch a PostgreSQL pipeline for check deployment cases and an explanation of stages and variables that need to be configured before launching.

## How to run PostgreSQL pipeline
After committing changes, pipeline will be run automatically.

For run a new pipeline without changes open `CI/CD` -> `Pipelines` in sidebar and click on button `Run Pipeline`. After this select branch `postgres` and click on `Run Pipeline` button again.

## Variables
<!-- markdownlint-disable line-length -->
| Variable                   | Description                                                                                            |
|----------------------------|--------------------------------------------------------------------------------------------------------|
| PG15_LATEST_SPRINT         | Latest sprint manifest for Deployer. PG version is 15                                              |
| PG16_LATEST_SPRINT         | Latest sprint manifest for Deployer. PG version is 16                                              |
| LATEST_SUPPL_SPRINT        | Latest sprint manifest for Deployer. Supplementary part                                            |
| PG15_PREVIOUS_SPRINT       | Previous sprint manifest for Deployer. PG version is 15                                            |
| PG16_PREVIOUS_SPRINT       | Previous sprint manifest for Deployer. PG version is 16                                            |
| PREVIOUS_SUPPL_SPRINT      | Previous sprint manifest for Deployer. Supplementary part                                          |
| PG15_N1_RELEASE            | Previous release manifest (n-1, where n – actual release) for Deployer. PG version is 15           |
| N1_SUPPL_RELEASE           | Previous release manifest (n-1, where n – actual release) for Deployer. Supplementary part         |
| PG15_N2_RELEASE            | Previous-previous release manifest (n-2, where n – actual release)  for Deployer. PG version is 15 |
| N2_SUPPL_RELEASE           | Previous-previous release manifest (n-2, where n – actual release)  for Deployer. PG version is 15 |
| LATEST_SPRIN_TAG           | Tag (branch name) name with CRD for latest sprint                                                      |
| PREVIOUS_SPRINT_TAG        | Tag (branch name) with CRD for previous sprint                                                         |
<!-- markdownlint-enable line-length -->


## Jobs list
<!-- markdownlint-disable line-length -->
| Job                                                                       | Description                                                                                                        | Deploy Scheme |
|---------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------|---------------|
| 1-Clean [PG15_PREVIOUS_SPRINT]                                            | Clean Deploy job with previous sprint manifest. PG version is 15                                                   | basic         | 
| 2-Upgrade From [PG15_PREVIOUS_SPRINT] To [PG15_LATEST_SPRINT]             | Upgrade from previous sprint manifest to latest sprint. PG version is 15                                   | basic         |
| 3-Clean [PG15_LATEST_SPRINT]                                              | Clean Deploy with latest manifest. PG version is 15.                                                               | basic         |
| 4-Upgrade [PG15_LATEST_SPRINT] Diff Params                                | Rolling Update with same manifest from previous step, but with changed resources. PG version is 15                 | basic         |
| 5-Clean [PG16_PREVIOUS_SPRINT]                                            | Clean Deploy job with previous sprint manifest. PG version is 16                                                   | basic         | 
| 6-Upgrade From [PG16_PREVIOUS_SPRINT] To [PG16_LATEST_SPRINT]             | Upgrade from previous sprint manifest to latest sprint. PG version is 16                                   | basic         |
| 7-Clean [PG16_LATEST_SPRINT]                                              | Clean Deploy with latest manifest. PG version is 16.                                                               | basic         |
| 8-Upgrade [PG16_LATEST_SPRINT] Diff Params                                | Rolling Update with same manifest from previous step, but with changed resources. PG version is 16                 | basic         |
| 9-Clean [PG16_LATEST_SPRINT] Restricted                                   | Clean Deploy with latest manifest in restricted mode. PG version is 16                                             | basic         |
| 10-Clean [PG15_PREVIOUS_SPRINT] Restricted                                | Clean Deploy with previous sprint manifest in restricted mode. PG version is 15                                    | basic         |
| 11-Upgrade From [PG15_PREVIOUS_SPRINT] To [PG15_LATEST_SPRINT] Restricted | Rolling Update to latest manifest from previous sprint manifest in restricted mode. PG version is 15               | basic         |
| 12-Clean [PG15_LATEST_SPRINT] Restricted                                  | Clean Deploy with latest manifest in restricted mode. PG version is 15                                             | basic         |
| 13-Upgrade [PG15_LATEST_SPRINT] From Non-TLS To TLS                       | Rolling Update from Non TLS to TLS. PG version is 15                                                              | full          |
| 14-Clean [PG15_LATEST_SPRINT] TLS                                         | Clean deploy latest version with TLS. PG version is 15                                                             | full          |
| 15-Clean [PG16_LATEST_SPRINT] TLS                                         | Clean deploy latest version with TLS. PG version is 16                                                             | full          |
| 16-Clean [PG15_N2_RELEASE] Appropriate CRD                                | Clean deploy N-2 Release version with CRD from N-2 Release. PG version is 15                                       | full          |
| 17-Upgrade From [PG15_N2_RELEASE] To [PG15_N1_RELEASE] Appropriate CRD    | Upgrade from N-2 Release to N-1 Release with upgrading CRD to N-1 Release version. PG version is 15                | basic         |
| 18-Clean [PG15_N1_RELEASE] Appropriate CRD                                | Clean deploy N-1 Release version with CRD from N-1 Release. PG version is 15                                       | basic         |
| 19-Upgrade From [PG15_N1_RELEASE] To [PG16_LATEST_SPRINT] Appropriate CRD | Upgrade from N-1 Release to Latest version. Migration from PG15 to PG16.                                   | basic         |
| 20-Clean [PG15_N2_RELEASE]                                                | Clean Deploy N-2 Release, CRD from latest version. PG version is 15.                                               | basic         |
| 21-Upgrade From [PG15_N2_RELEASE] To [PG16_LATEST_SPRINT]                 | Upgrade From N-2 Release to Latest version. Migration from PG15 to PG16.                                   | basic         |
| 22-Clean [PG15_N1_RELEASE]                                                | Clean deploy N-1 Release, CRD from latest version. PG version is 15.                                               | basic         |
| 23-Upgrade From [PG15_N1_RELEASE] To [PG16_LATEST_SPRINT]                 | Upgrade From N-1 Release to Latest version. Migration from PG15 to PG16.                                   | basic         |
| 24-Migration From [PG15_LATEST_SPRINT] To [PG16_LATEST_SPRINT]            | Migration from PG15 to PG16 latest versions.                                                                       | basic         |
| Report                                                                    | Creating report job                                                                                                | manual        |
<!-- markdownlint-enable line-length -->
