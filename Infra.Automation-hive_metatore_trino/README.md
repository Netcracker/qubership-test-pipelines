# prometheus-deploy-test

Tool to automate deploying Prometheus in different configurations with Helm Deployer
For now, tool can be used for deploy in 3 ways: 

1. Deploy with Helm Deployer
2. Deploy with Deployer
3. Common deploy mode

The last one is supposed to be able to call **any** job with **any** specified parameters.
Parameters should be placed to yml-file and should match the job's parameters.

## Tool usage

You can run several deploy jobs with predefined parameters via GitLab pipeline:

1. Create new branch
1. Add to `.gl-ci.yml` with new jobs configuration. Each job should be inherited base `.test-case` job and override script section.
1. Add to the script section of creted jobs calling proper python script and specify parameters
1. Commit `.gl-ci.yml`
1. Run new pipeline. Before that you can set variables, used in `.gl-ci.yml`
1. Activate each job manually in any order

## .gl-ci.yml configuration

File `.gl-ci.yml` contains all information about pipeline. The main part of it is defining jobs running in pipeline. Each deploy-job should be inherited from `.test-case` job:

```yaml
.test-case: &test-case
  stage: run_test 
  image: ${PYTHON_IMAGE}
  tags:
    - ''
  script:
    - pip config set global.index-url qubership.org/api/pypi/pypi_python_org.pypi.proxy/simple
    - pip config set global.trusted-host dockerhub.qubership.org
    - python3 -m pip install --upgrade pip
    - pip install --no-cache-dir -r requirements.txt
  allow_failure: true
  when: manual
```

It contains common settings for all jobs. New job should contains all field of `.test-case` job and overrides script section. **Note**, that python configuration from base `.test-case` job **should be included** in each inherited job.

The main part of the job is running python deploy script. You can run either   `./scripts/deploy_with_helmdeployer.py` or `./scripts/deploy\_with\_deployer.py` scripts with needed parameters

### Example of helm-deployer job

```yaml
.helm-deployer-test:
  <<: *test-case
  script:
    - pip config set global.index-url qubership.org/api/pypi/pypi_python_org.pypi.proxy/simple
    - pip config set global.trusted-host dockerhub.qubership.org
    - python3 -m pip install --upgrade pip
    - pip install --no-cache-dir -r requirements.txt
    - >
      python3 ./scripts/deploy_with_helmdeployer.py -f "./specific-deployer-templates/job-params/helm-deployer/job-params.yml" --jenkins-url="${JENKINS_URL}" --jenkins-user="${JENKINS_USER}" --jenkins-pass="${JENKINS_PASS}" 
      # --cloud-token="${CLOUD_TOKEN}" --custom-params="./specific-deployer-templatescustom-params/helm-deployer/custom-params.yml" --add_options=skip-crds,dry-run
```

### Example of app-deployer job

```yaml
app-deployer job:
  <<: *test-case
  script:
    - pip config set global.index-url qubership.org/api/pypi/pypi_python_org.pypi.proxy/simple
    - pip config set global.trusted-host dockerhub.qubership.org
    - python3 -m pip install --upgrade pip
    - pip install --no-cache-dir -r requirements.txt
    - >
      python3 ./scripts/deploy\_with\_deployer.py -f "./specific-deployer-templates/job-params/app-deployer/job-params.yml" --jenkins-url="${JENKINS_URL}" --jenkins-user="${JENKINS_USER}" --jenkins-pass="${JENKINS_PASS}" 
      # --custom-params="./specific-deployer-templates/custom-params/app-deployer/custom-params.ini" --os-creds="${OS_CREDS}" --deploy-mode="Rolling Update"

```

### Example of helm-deployer job with common-deploy script

```yaml
app-deployer job:
  <<: *test-case
  script:
    - pip config set global.index-url qubership.org/api/pypi/pypi_python_org.pypi.proxy/simple
    - pip config set global.trusted-host dockerhub.qubership.org
    - python3 -m pip install --upgrade pip
    - pip install --no-cache-dir -r requirements.txt
    - >
      python3 ./scripts/deploy.py -f "./templates-example/helm-deployer-params.yml" --jenkins-url="${JENKINS_URL}" --jenkins-user="${JENKINS_USER}" --jenkins-pass="${JENKINS_PASS}" 
  --cloud-token="${CLOUD_TOKEN}"
      
```

## Parameters

Parameters for running scripts maches the ones in Jenkins job. Also, there are jenkins specific parameters common for all jobs: `JENKINS_USER` and `JENKINS_PASS`. This parameters should be set from GitLab while running pipeline. **Note**, that you can add new parameters and set them from Gitlab.

The rest of parameters you can configure both via flags and yaml file in `./job-params/deployer-name`. You can create several files with different configuration for different jobs.

Custom parameters for deploy should be placed in separate file in `./custom-params/deployer-name`.
### Parameters for helm deployer job

The list of parameters:

* JENKINS_URL
* CLOUD_URL
* CLOUD_NAMESPACE
* DESCRIPTOR_URL
* DEPLOY_MODE
* KUBECTL_VERSION
* HELM_VERSION
* ADDITIONAL_OPTIONS

You can set the as flags or in file. Example can be found in `./specific-deployer-templates/job-params/helm-deployer/job-params`

Custom paramers should be places in yaml file in `./specific-deployer-templates/custom-params/helm-deployer`. Example can be found in `./specific-deployer-templates/custom-params/helm-deployer/custom-params`

### Parameters for deployer job

The list of parameters:

* JENKINS_URL
* PROJECT
* OPENSHIFT_CREDENTIALS
* ARTIFACT_DESCRIPTOR_VERSION
* DEPLOY_MODE

You can set the as flags or in file. Example can be found in `./specific-deployer-templates/job-params/app-deployer/job-params`

Custom paramers should be places in ini file in `./specific-deployer-templates/custom-params/app-deployer`. Example can be found in `./specific-deployer-templates/custom-params/app-deployer/custom-params`

### Parameters for common deployer 

Unlike the previous one, common-deployer script doesn't have the specified list of parameters.
Depending on the job you want to run create yaml file which contains **job-like parameters**: keys are job's filed names and values are their values.
Examples of such file you can find in `./templates-example`. Pass created yaml file to `deploy.py` script using `-f` or `--job-params` flags.
Besides, this file may contain: 
* JENKINS_URL
* JOB_NAME
* TOKEN_NAME
* DESCRIPTOR_NAME
  
`JENKINS_URL` and `JOB_NAME` can be specified both with flags or in file.

Using `TOKEN_NAME` you can specify the field name of Cloud token field and then pass it with `--cloud-token` flag. 
So that you can prevent your private token from displaying in configuration file.

Using `DESCRIPTOR_NAME` you can specify the field name of Service descriptor field and then pass it with `--service-version` flag. 
So that you can cnahge service version without ane changes in config file.



### Pipeline control

Using `when` key you can control job's execution:

* `when:manual` - manual launch of job in Gitlab UI
* `when:on_success` -  execute job only when all jobs from prior stages succeed (or marked allow_failure). Used by default
* `when:on_failure` - execute job only when at least one job from prior stages fails
* `when:always` - job executes in any case regardless of the previous jobs' status
* `when:delayed` - execute job after some delay

More info in [GitLab docs]

Another important setting is `stage`. According to [GitLab docs] **jobs on the same stage run in parallel**, while jobs of the next stage are run after the jobs from the previous stage complete successfully. So **do not deploy** to the same project within same stage without manual control

## Including auto-test

platform-monitoring-tests after monitoring-opearotor deploy
Now, there is a possibility to run platform-monitoring-test after monitoring-operator deploy, which can be deployed by [Helm Deployer] using same `./scripts/deploy_with_helmdeployer.py`. Parameters for auto-tests deploy is placed in `./custom-params/test-params`
 More info about building and deploying you can find in documentation.
