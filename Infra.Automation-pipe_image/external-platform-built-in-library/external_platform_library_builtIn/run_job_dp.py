import sys
import time
import jenkins
from jenkinsapi.jenkins import Jenkins

from utils import log

def _invoke_job(job_name, job_params, jenkins_url, jenkins_user, jenkins_pass, crumb=False):
    """
       Invoke job using other Jenkins API
    """
    log('Invoking job', 2)
    server = Jenkins(jenkins_url,jenkins_user,jenkins_pass,timeout=60, useCrumb=crumb)
    queue_item = server.get_job(job_name).invoke(build_params=job_params)
    return queue_item.queue_id


def run_job_dp(job_name, job_params, jenkins_url, jenkins_user, jenkins_pass, verbose=False, crumb=False):
    """
        Deploy service with specified job
    """

    if not all([job_name, jenkins_url]):
        log(f'Job name or Jenkins url is not specified. Exiting')
        sys.exit(1)

    log(f'Running job {job_name}')
    server = jenkins.Jenkins(jenkins_url, username=jenkins_user, password=jenkins_pass)
    queue_n = _invoke_job(job_name, job_params, jenkins_url, jenkins_user, jenkins_pass, crumb)

    build_number = -1
    while build_number == -1:
        log('Waiting for job to start...', 2)
        queue_item_info = server.get_queue_item(queue_n)
        if queue_item_info.get('why') is not None:
            time.sleep(3)
        else:
            build_number = queue_item_info.get('executable', {}).get('number')
    else:
        log(f'Job has build number: {build_number}', 2)

    job = server.get_build_info(job_name, build_number)
    log(f'Link to build: {job.get("url")}',2)

    while job.get('building'):
        log('Waiting job completing...', 2)
        job = server.get_build_info(job_name, build_number)
        time.sleep(30)

    if verbose:
        log('Build console logs:',2)
        print(server.get_build_console_output(job_name, build_number))

    build_status = job.get('result')
    log(f'Build finished with status {build_status}',2)
    if build_status != 'SUCCESS':
        sys.exit(1)
