# Infra.Automation

Topics covered in this section:

- [Automate build image](#automate-build-image)

# Tool for post-deploy checks of service 

- [Architecture](#architecture)
- [Add check logs script to your pipeline](#add-check-logs-script-to-your-pipeline)
    - [Using image and job template](#using-image-and-job-template)
    - [Using all templates and files in your local pipeline](#using-all-templates-and-files-in-your-local-pipeline)

## Automate build image:

1. Open job https://cisrvrecn.qubership.org/job/DP.Pub.Microservice_builder_v2 and click `Build With Paramaters`

2. Set parameters:

`REPOSITORY_NAME: PROD.Platform.HA/Infra.Automation`
`LOCATION: pipe_image`
and click button `Build`

3. Wait finishing job and after that check your image in `Status` -> `service timestamp` or just use lates version `service latest`.

## For using libs in your Pipeline

For the some library will be available in your updated scripts, it must be copied to the stage
`default` with the following commands:
```
default:
  before_script:
    - ...
    - cd /pipe
    - cp -a lib_name /builds/PROD.Platform.HA/Infra.Automation/scripts
    - cd /builds/PROD.Platform.HA/Infra.Automation`
```
# Architecture

The script will be useful for check service state after deploy. Script checks the following:
  - pods in Not Running State;
  - pods that have been restarted;
  - number of errors per pod;
  - display logs that contain errors, count of duplicate logs and link to Graylog where we can check logs per pod/container. 

# Add check logs script to your pipeline

There are two ways how to add script for check status and errors to any pipeline.

## Using image and job template

1.Open `.gl-ci.yml` in your repo and add following block:

```
include:
  - project: 'PROD.Platform.HA/Infra.Automation'
    ref: pipe_image
    file: 'api.yaml'
```

In this block you include a template of extension with verification steps.

2.Add a new job.

For example:

```
Check Logs After Clean:
  stage: check_logs
  extends: .check_state_logs_script.run
  variables:
    CLOUD_HOST: $CLOUD_URL
    CLOUD_TOKEN: $TOKEN_KUB
    ARRAY_NS: $CLOUD_NAMESPACE
```

where:

- `Check Logs After Clean` - name of your job; `required`
- `check_logs` - name of stage; `required`
- `.check_state_logs_script.run` - name of extends, shouldn't be changed; `required`
- `CLOUD_HOST` - URL of OS or k8s where you want to validate service ; `required`
- `CLOUD_TOKEN` - token for access to cloud (it's better to have admin rights); `required`
- `ARRAY_NS` - one ot several namespaces for check; `required`

Also, available additional variables to configure:

- `GRAYLOG_HOST` - host to available graylog for your cloud; `optional`
- `GRAYLOG_USER` - graylog user; `optional`
- `GRAYLOG_PASS` - graylog password; `optional`
- `ALLOWED_RESTARTS_AMOUNT` - allowed number of pod restarts, if the number of restarts is greater, the script will be failed; `optional`
- `ALLOWED_ERROR_LOGS_AMOUNT` - allowed number of errors in pod, if the number of errors is greater, the script will be failed. `optional`

All of them can be overridden in your job in block `variables`.

3.Add the name of stage from the job to block `stages` in required position.

```
stages:
  ...
  - app_run_clean_install_kuber
  - check_logs
  ...
```

## Using all templates and files in your local pipeline

This is a second way for adding script to your pipeline. In this case it's not required to use image.

1.First of all add to your `.gl-ci.yml` file job for post-deploy checks.

Example:

```
Check Logs:
  <<: *test-case
  stage: check_logs
  script:
    - |
      for NS in $ARRAY_NS
        do
          python3 ./postdeploy_checks.py --cloud-host="${CLOUD_HOST}" --cloud-token="${CLOUD_TOKEN}" --namespace="${NS}"
          source .env
          for i in $(seq 1 $COUNT); do
            echo "------------------------------------------------------------------------------------------------------------------------------------"
            python3 -c "import postdeploy_checks; postdeploy_checks.print_splitted_names(\"$PC\", $i)"
            echo -e "\e[0Ksection_start:`date +%s`:my_first_section[collapsed=true]\r\e[0KPost-check after deploy for namespace ${NS}, pod count $i"
            python3 -c "import postdeploy_checks; postdeploy_checks.print_graylog_link(\"$GRAYLOG_HOST\", \"$GRAYLOG_USER\", \"$GRAYLOG_PASS\", \"$NS\", \"$PC\", $i, \"$CLOUD_HOST\", \"$CLOUD_TOKEN\")"
            python3 -c "import postdeploy_checks; postdeploy_checks.show_logs_for_pod(\"$PC\", $i, \"$CLOUD_HOST\", \"$CLOUD_TOKEN\", \"$NS\")"
            echo -e "\e[0Ksection_end:`date +%s`:my_first_section\r\e[0K"
          done
        done
      python3 -c "import postdeploy_checks; postdeploy_checks.set_state(\"$CLOUD_HOST\", \"$CLOUD_TOKEN\", \"$ARRAY_NS\", $ALLOWED_RESTARTS_AMOUNT, $ALLOWED_ERROR_LOGS_AMOUNT)"
  allow_failure: true
```

Don't forget to add a new stage with this job in the correct position.

```
stages:
  ...
  - check_logs
  ...
```

`Important` Please, don't change a structure of job, all steps are required for correct running and displaying.

2.Add new variables to block `variables` in `.gl-ci.yml` file:

```
  GRAYLOG_HOST: http://***.***.***.***:80
  GRAYLOG_USER: admin
  GRAYLOG_PASS: admin
  CLOUD_HOST: https://dashboard.qa-kubernetes.openshift.sdntest.qubership.org:6443
  CLOUD_TOKEN: token123
  LOGS_NS: prometheus-operator
  ALLOWED_RESTARTS_AMOUNT: 2
  ALLOWED_ERROR_LOGS_AMOUNT: 100
```

where:

- `GRAYLOG_HOST` - host of Graylog which configured on your cloud;
- `GRAYLOG_USER` - user to login to Graylog;
- `GRAYLOG_PASS` - password to login to Graylog;
- `CLOUD_HOST` - host to k8s;
- `CLOUD_TOKEN` - token for login to k8s;
- `LOGS_NS` - namespace name (where is deployed service for check);
- `ALLOWED_RESTARTS_AMOUNT` - allowed number of pod restarts, if the number of restarts is greater, the script will be failed;
- `ALLOWED_ERROR_LOGS_AMOUNT` - allowed number of errors in pod, if the number of errors is greater, the script will be failed.

3.Add new files: `postdeploy_checks.py`, `ExternalPlatformLib.py` and `utils.py` to your repo.

You can find it there: 

- `postdeploy_checks.py` - [postdeploy_checks.py].
- `ExternalPlatformLib.py` - [ExternalPlatformLib.py].
- `utils.py` - [utils.py].

`Important` Location of files should be on the same level as `.gl-ci.yml` file.

## Example

This is an example of configuration stages in the pipeline, good way in order to reuse job code and minimize code duplication.

```
variables:
  PYTHON_IMAGE: python:3.8.3-alpine3.11
  LOGS_NS: prometheus-operator
  GRAYLOG_HOST: ''
  GRAYLOG_USER: admin
  GRAYLOG_PASS: admin
  CLOUD_HOST: ''
  CLOUD_TOKEN: ''
  ALLOWED_RESTARTS_AMOUNT: 2
  ALLOWED_ERROR_LOGS_AMOUNT: 100

stages:
  - check_logs_after_clean
  - check_logs_after_upgrade

...

.check_logs_script:
  script:
    - |
      for NS in $ARRAY_NS
        do
          python3 ./postdeploy_checks.py --cloud-host="${CLOUD_HOST}" --cloud-token="${CLOUD_TOKEN}" --namespace="${NS}"
          source .env
          for i in $(seq 1 $COUNT); do
            echo "------------------------------------------------------------------------------------------------------------------------------------"
            python3 -c "import postdeploy_checks; postdeploy_checks.print_splitted_names(\"$PC\", $i)"
            echo -e "\e[0Ksection_start:`date +%s`:my_first_section[collapsed=true]\r\e[0KPost-check after deploy for namespace ${NS}, pod count $i"
            python3 -c "import postdeploy_checks; postdeploy_checks.print_graylog_link(\"$GRAYLOG_HOST\", \"$GRAYLOG_USER\", \"$GRAYLOG_PASS\", \"$NS\", \"$PC\", $i, \"$CLOUD_HOST\", \"$CLOUD_TOKEN\")"
            python3 -c "import postdeploy_checks; postdeploy_checks.show_logs_for_pod(\"$PC\", $i, \"$CLOUD_HOST\", \"$CLOUD_TOKEN\", \"$NS\")"
            echo -e "\e[0Ksection_end:`date +%s`:my_first_section\r\e[0K"
          done
        done
      python3 -c "import postdeploy_checks; postdeploy_checks.set_state(\"$CLOUD_HOST\", \"$CLOUD_TOKEN\", \"$ARRAY_NS\", $ALLOWED_RESTARTS_AMOUNT, $ALLOWED_ERROR_LOGS_AMOUNT)"

Check Logs After Clean Deploy:
  <<: *test-case
  stage: check_logs_after_clean
  extends: .check_logs_script

Check Logs After Upgrade Deploy:
  <<: *test-case
  stage: check_logs_after_upgrade
  extends: .check_logs_script
```

`Important` If you use base alpine image for the job you need to add all libs and packages required for `postdeploy_checks.py`.
