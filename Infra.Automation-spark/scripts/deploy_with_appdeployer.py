import argparse
import os
import sys
from jenkins import JenkinsException
from jenkinsapi.custom_exceptions import JenkinsAPIException
from requests.exceptions import HTTPError
from run_job import run_job
from utils import log
from utils import parse_yml


def main(args_):

    deploy_params = parse_yml(args_.job_params)
    log(f'PARAMS: {deploy_params}')

    job_name = args_.job_name or deploy_params.get('JOB_NAME', '')
    jenkins_url = args_.jenkins_url or deploy_params.get('JENKINS_URL', '')

    job_params = {
        'PROJECT': args_.project or deploy_params.get('PROJECT', ''),
        'OPENSHIFT_CREDENTIALS': args_.os_creds or deploy_params.get('OPENSHIFT_CREDENTIALS', ''),
        'ARTIFACT_DESCRIPTOR_VERSION': args_.artifact or deploy_params.get('ARTIFACT_DESCRIPTOR_VERSION', ''),
        'CUSTOM_PARAMS': deploy_params.get('CUSTOM_PARAMS', ''),
        'DEPLOY_MODE': args_.deploy_mode or deploy_params.get('DEPLOY_MODE', '')
    }

    try:
        run_job(
            jenkins_url=jenkins_url,
            job_name=job_name,
            job_params=job_params,
            jenkins_user=args_.jenkins_user,
            jenkins_pass=args_.jenkins_pass
        )
    except JenkinsException as e:
        log(f'Error! Some Jenkins exception occurred: {e}')
        sys.exit(1)
    except JenkinsAPIException as e:
        log(f'Error! Some Jenkins exception occurred while invoking job: {e}')
        sys.exit(1)
    except HTTPError as e:
        log(f'Error! Some HTTP exception occurred: {e}')
        sys.exit(1)
    except Exception as e:
        log(f'Error! Some exception occurred: {e}')
        sys.exit(1)


if __name__ == '__main__':

    log(f'Running script "{os.path.basename(__file__)}"...', 0)
    log('Parse command line arguments...')

    parser = argparse.ArgumentParser(description='Script to deploy service with Deployer job')

    parser.add_argument('-f', '--job-params',
                        help='Deploy parameters of the job',
                        default='./job-params/app-deployer/job-params.yml')
    parser.add_argument('--job-name',
                        help='Jenkins job name')
    parser.add_argument('--jenkins-user',
                        default='admin',
                        help='Jenkins user')
    parser.add_argument('--jenkins-pass',
                        default='admin',
                        help='Jenkins password')
    parser.add_argument('--jenkins-url',
                        help='Jenkins url')
    parser.add_argument('--project',
                        help='Project name')
    parser.add_argument('--os-creds',
                        help='Opensheft credentials')
    parser.add_argument('--artifact',
                        help='Artifact description version')
    parser.add_argument('--deploy-mode',
                        help='Job deployment mode')
    args = parser.parse_args()

    main(args)
