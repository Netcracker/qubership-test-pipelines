import argparse
import os
import sys
from jenkins import JenkinsException
from jenkinsapi.custom_exceptions import JenkinsAPIException
from requests.exceptions import HTTPError
from run_job_dp import run_job_dp
from utils import log
from utils import parse_yml


def main(args_):
    job_params = parse_yml(args_.job_params)
    job_params = {
        'CLOUD_URL': args_.cloud_url,
        'CLOUD_NAMESPACE': args_.cloud_ns,
        'CLOUD_TOKEN': args_.cloud_token,
        'DESCRIPTOR_URL': args_.artifact,
        'DEPLOYMENT_PARAMETERS': job_params.get('CUSTOM_PARAMS', ''),
        'DEPLOY_MODE': args_.deploy_mode,
        'KUBECTL_VERSION': '1.20.5',
        'HELM_VERSION': '3.5.3',
        'ADDITIONAL_OPTIONS': ['--skip-crds']
    }
    job_name = args_.job_name

    try:
        run_job_dp(
            job_name=job_name,
            job_params=job_params,
            jenkins_url=args_.jenkins_url,
            jenkins_user=args_.jenkins_user,
            jenkins_pass=args_.jenkins_pass
        )
    except JenkinsException as e:
        log(f'Error! Some Jenkins exception occurred: {e}')
        sys.exit(1)
    except JenkinsAPIException as e:
        log(f'Error! Some Jenkins exception occurred while invoking job {e}')
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

    parser = argparse.ArgumentParser(description='Script to run Jenkins job with specified parameters')

    parser.add_argument('-f', '--job-params',
                        help='Deploy parameters of the job')
    parser.add_argument('--cloud-url',
                        help='URL to cloud')
    parser.add_argument('--cloud-ns',
                        help='Cloud namespace')
    parser.add_argument('--cloud-token',
                        help='Cloud token')
    parser.add_argument('--artifact',
                        help='Version or descriptor of deploying service')
    parser.add_argument('--deploy-mode',
                        help='Deploy Mode')
    parser.add_argument('--job-name')
    parser.add_argument('--jenkins-url')
    parser.add_argument('--jenkins-user')
    parser.add_argument('--jenkins-pass')
    args = parser.parse_args()

    main(args)
