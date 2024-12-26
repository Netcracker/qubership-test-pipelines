import argparse
import os
import sys
import yaml
from jenkins import JenkinsException
from run_job import run_job
from utils import log
from utils import parse_yml


def main(args_):

    job_params = parse_yml(args_.job_params)
    job_name = args_.job_name or job_params.get('JOB_NAME', '')
    job_params[job_params['TOKEN_NAME']] = args_.cloud_token
    job_params[job_params['DESCRIPTOR_NAME']] = args_.service_version
    job_params['PROJECT'] = args_.namespace_name

    # Specify cloud token filed name
    # if 'TOKEN_NAME' in job_params:
    #     job_params[job_params['TOKEN_NAME']] = args_.cloud_token
    # Specify service descriptor name
    # if 'DESCRIPTOR_NAME' in job_params:
    #     job_params[job_params['DESCRIPTOR_NAME']] = args_.service_version

    try:
        run_job(
            job_name=job_name,
            job_params=job_params,
            jenkins_url=args_.jenkins_url or job_params.get('JENKINS_URL', ''),
            jenkins_user=args_.jenkins_user,
            jenkins_pass=args_.jenkins_pass
        )
    except JenkinsException as e:
        log(f'Error! Some exception occurred: {e}')
        sys.exit(1)


if __name__ == '__main__':

    log(f'Running script "{os.path.basename(__file__)}"...', 0)
    log('Parse command line arguments...')

    parser = argparse.ArgumentParser(description='Script to run Jenkins job with specified parameters')

    parser.add_argument('-f', '--job-params',
                        help='Deploy parameters of the job')
    parser.add_argument('--job-name',
                        help='Jenkins job name')
    parser.add_argument('--jenkins-user',
                        help='Jenkins user')
    parser.add_argument('--jenkins-pass',
                        help='Jenkins password')
    parser.add_argument('--jenkins-url',
                        help='Jenkins url')
    parser.add_argument('--cloud-token',
                        help='Cloud token')
    parser.add_argument('--service-version',
                        help='Version or descriptor of deploying service')
    parser.add_argument('--namespace-name',
                        help='Namespace for deploy')
    parser.add_argument('--job_name',
                        help='Namespace for deploy')
    parser.add_argument('--jenkins_url',
                        help='Namespace for deploy')
    args = parser.parse_args()
    main(args)
