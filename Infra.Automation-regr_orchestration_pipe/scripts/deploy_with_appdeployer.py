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

    try:
        deploy_params = parse_yml(args_.job_params)
        log(f'PARAMS: {deploy_params}')
    except:
        deploy_params = None
        custom_params = ''
        log('There is no deploy_params file!')

    job_name = args_.job_name or os.getenv('JOB_NAME')
    jenkins_url = args_.jenkins_url or os.getenv('JENKINS_URL')
    jenkins_user = args_.jenkins_user or os.getenv('JOB_USER')
    jenkins_pass = args_.jenkins_pass or os.getenv('JOB_TOKEN')
    request_type = args_.request_type or os.getenv('REQUEST_TYPE')
    if deploy_params:
        custom_params = deploy_params.get('CUSTOM_PARAMS', '')
    job_params = {
        'PROJECT': args_.project or os.getenv("PROJECT"),
        'OPENSHIFT_CREDENTIALS': args_.os_creds or os.getenv("OPENSHIFT_CREDENTIALS"),
        'ARTIFACT_DESCRIPTOR_VERSION': args_.artifact or os.getenv("ARTIFACT_DESCRIPTOR_VERSION", ''),
        'CUSTOM_PARAMS': custom_params,
        'DEPLOY_MODE': args_.deploy_mode or os.getenv("DEPLOY_MODE", ''),
        #'DEPLOY_TIMEOUT': args_.deploy_timeout or os.getenv("DEPLOY_TIMEOUT", '1')
    }
    timeout = args_.deploy_timeout or os.getenv("DEPLOY_TIMEOUT", '')
    if timeout:
        job_params['DEPLOY_TIMEOUT']=timeout
    log(f'job_params: {job_params}')


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
    parser.add_argument('--deploy-timeout',
                        help='Job deploy timeout')
    parser.add_argument('--request-type',
                        help='Type of request: get or post',
                        default='get')
    args = parser.parse_args()

    main(args)
