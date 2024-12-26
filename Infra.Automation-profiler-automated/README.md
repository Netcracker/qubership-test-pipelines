# Quick Start Guide
This mini guide contains an explanation of how to launch a Profiler pipeline for check deployment cases and an explanation of stages and variables that need to be configured before launching.

## How to run Profiler pipeline

After committing changes, pipeline will be run automatically.

For run a new pipeline without changes open `CI/CD` -> `Pipelines` in sidebar and click on button `Run Pipeline`. After this select branch `profiler-automated` and click on `Run Pipeline` button again.

## Variables
<!-- markdownlint-disable line-length -->
| Variable              | Description                                                                            |
|-----------------------|--------------------------------------------------------------------------------------- |
| PREVIOUS_SPRINT           | Previous sprint manifest for Deployer.                                             |
| LATEST_SPRINT           | New sprint manifest for Deployer.                                                  |
| N1_RELEASE       | Previous release manifest (n-1, where n – actual release) for Deployer.            |
| N2_RELEASE      | Previous-previous release manifest (n-2, where n – actual release)  for Deployer.  |
| PROFILER_TEST_INGRESS | URL to profiler test pod                                                               |
<!-- markdownlint-enable line-length -->


## Jobs list
<!-- markdownlint-disable line-length -->
| Stage                                    | Job                                                | Description                                                                                   |
|------------------------------------------|----------------------------------------------------|-----------------------------------------------------------------------------------------------|
| clean_latest_sprint                        | 1-Clean [LATEST_SPRINT]                            | Clean Deploy with new manifest.                                                               |
| clean_previous_sprint                    | 2-Clean [PREVIOUS_SPRINT]                | Clean Deploy job with previous sprint manifest.                                               | 
| update_from_previous_to_latest                   | 3-Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT]                   | Rolling Update job to new manifest from previous sprint.                                      | 
| clean_n1_release                   | 4-Clean [N1_RELEASE]               | Clean Deploy with previous release manifest                                                   | 
| upgrade_from_n1_release_to_latest_sprint          | 5-Upgrade From [N1_RELEASE] To [LATEST_SPRINT]  | Rolling Update from previous release manifest to new manifest.                                |
| clean_n2_release               | 6-Clean [N2_RELEASE]           | Clean Deploy with previous-previous release manifest (n-2, where n – actual release).         |
| upgrade_from_n2_release_to_latest_sprint      | 7-Upgrade From [N2_RELEASE] To [LATEST_SPRINT]  | Rolling Update to new manifest from n-2 manifest.                                             |
| clean_latest_sprint_with_opensearch        | 8-Clean [LATEST_SPRINT] With Opensearch                            | Clean Deploy with new manifest.                                                               |
| clean_previous_sprint_with_opensearch    | 9-Clean [PREVIOUS_SPRINT] With Opensearch                | Clean Deploy job with previous sprint manifest.                                               | 
| upgrade_to_latest_sprint_with_opensearch   | 10-Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT] With Opensearch                  | Rolling Update job to new manifest from previous sprint.                                      | 
| clean_previous_sprint_restricted             | 11-Clean [PREVIOUS_SPRINT] Restricted                    | Restricted clean Deploy job with previous sprint manifest.                                    | 
| update_from_previous_to_latest_restricted         | 12-Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT] Restricted               | Restricted rolling Update to new manifest from previous sprint.                               |
| clean_latest_sprint_restricted             | 13-Clean [LATEST_SPRINT] Restricted                    | Restricted clean Deploy with new manifest.                                                    |
| clean_latest_sprint_with_basic_auth        | 14-Clean [LATEST_SPRINT] With Basic auth               | Clean Deploy with basic auth.                                                                 |
| clean_latest_sprint_emptyDIR               | 15-Clean [LATEST_SPRINT] With emptyDIR                 | Clean Deploy with empty dir                                                                   | 
| clean_latest_sprint_with_test_service      | 16-Clean [LATEST_SPRINT] With Test-service             | Clean Deploy with test service + check result of AT                                           | 
<!-- markdownlint-enable line-length -->
