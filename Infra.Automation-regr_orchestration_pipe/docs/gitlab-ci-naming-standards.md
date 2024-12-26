All Regression pipelines should match this standarts of naming.

## Commit message

`IMPORTANT:` Please, specify commit message by the following structure:

`[<SERVICE_NAME>] Regression <release/sprint> pipeline <RELEASE # Sprint #> (<CLOUD>)`

For example:

```
[Postgres] Regression release pipeline R2024.3 Sprint 4 (qa_kubernetes)
[Postgres] Regression sprint pipeline R2024.3 Sprint 3 (ocp_cert_1)
```

## Variable naming

Example of variable naming in Regression pipeline:

```
LATEST_SPRINT
PREVIOUS_SPRINT
N1_RELEASE
N2_RELEASE
```
where:

- `LATEST_SPRINT` - latest version (version that you are testing);
- `PREVIOUS_SPRINT` - version from the previous Sprint;
- `N1_RELEASE` - version from the N-1 Release (N - current release, N-1 - previous release);
- `N2_RELEASE` - version from the N-2 Release.

Example of variable naming (for service with supplementary feature) in Regression pipeline:

```
LATEST_SPRINT
LATEST_SUPPL_SPRINT

PREVIOUS_SPRINT
PREVIOUS_SUPPL_SPRINT

N1_RELEASE
N1_SUPPL_RELEASE

N2_RELEASE
N2_SUPPL_RELEASE
```

For the Supplementary part we add `SUPPL` in the middle of the variable name.

## For restricted installations

```
  LATEST_SPRIN_TAG: "1.37.0"
  PREVIOUS_SPRINT_TAG: ''
```
where:

- `LATEST_SPRIN_TAG` - tag name for the latest version (version that you are testing);
- `PREVIOUS_SPRINT_TAG` - tag name for the version from the previous Sprint.

## Job naming

Job name should match the following structure:

`<#_JOB_NUMBER>-<DEPLOY_TYPE> <VERSION> <TYPE_OF_PARAMETERS>`

where:

- `#_JOB_NUMBER` - integer value (1, 2, ..., 27);
- `DEPLOY_TYPE` - Clean/Upgrade/Migration;
- `VERSION` - in case of Clean  installation: `[LATEST_SPRINT]`. In case of Upgrade: `From [PREVIOUS_SPRINT] To [LATEST_SPRINT]`. Name of variable from the version should be added in square brackets. See more in examples.
- `TYPE_OF_PARAMETERS` - any clear description of parameters type: `TLS, Full-AT, S3, PV, Single Schema, Consul Integration`... Can be list of types.


For example:

```
1-Clean [PREVIOUS_SPRINT]
2-Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT]
3-Clean [LATEST_SPRINT]
4-Upgrade [LATEST_SPRINT] Diff Params

5-Clean [N1_RELEASE]
6-Upgrade From [N1_RELEASE] To [LATEST_SPRINT]
7-Clean [N2_RELEASE]
8-Upgrade From [N2_RELEASE] To [LATEST_SPRINT]

9-Clean [PREVIOUS_SPRINT] Restricted
10-Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT] Restricted
11-Clean [LATEST_SPRINT] Restricted

12-Migration From [PG15_LATEST_SPRINT] To [PG16_LATEST_SPRINT]

13-Clean [LATEST_SPRINT] TLS
14-Upgrade [LATEST_SPRINT] From Non-TLS To TLS
15-Clean [LATEST_SPRINT] TLS Secrets
16-Upgrade [LATEST_SPRINT] TLS Certs

17-Clean [LATEST_SPRINT] Vault Integration
18-Clean [LATEST_SPRINT] Consul Integration
19-Clean [LATEST_SPRINT] Profiler Integration

20-Clean [LATEST_SPRINT] Full-AT
21-Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT] Full-AT DRD S3 
22-Upgrade From [PREVIOUS_SPRINT] To [LATEST_SPRINT] Full-AT

23-Clean [LATEST_SPRINT] PV
24-Clean [LATEST_SPRINT] DRD
25-Clean [LATEST_SPRINT] S3

26-Clean [LATEST_SPRINT] Infra Passport
27-Clean [LATEST_SPRINT] Zoo+Kafka Infra Passport

28-Clean [ZOOKEEPER_LATEST] TLS

29-Clean [LATEST_SPRINT] Custom Creds

30-Clean [LATEST_SPRINT] W/O Components
31-Clean [LATEST_SPRINT] Separate Mode
32-Clean [LATEST_SPRINT] Arbiter Mode/Schema
33-Clean [LATEST_SPRINT] Single Schema
34-Clean [LATEST_SPRINT] NFS

35-Migration [LATEST_SPRINT] To Kraft Schema
```

## Stage naming

Name of stage should be the similar with job name, but in lower case and using `_` instead of space.

```
  - clean_previous_sprint
  - upgrade_from_previous_sprint_to_latest_sprint
  - clean_latest
  - upgrade_latest_diff_params
  ...
  - clean_latest_sprint_tls
```
