import jenkins
import sys
import time
import urllib3

from utils import log

urllib3.disable_warnings()

def run_job(job_name, job_params, jenkins_url, jenkins_user, jenkins_pass):
    """
        Deploy service with specified job
    """

    if not all([job_name, jenkins_url]):
        log(f'Job name or Jenkins url is not specified. Exiting')
        sys.exit(1)

    log(f'Running job {job_name}')
    server = jenkins.Jenkins(jenkins_url, username=jenkins_user, password=jenkins_pass)
    queue_n = server.build_job(job_name, job_params)

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
    log(f'Link to build: {job.get("url")}')

    while job.get('building'):
        log('Waiting job completing...', 2)
        job = server.get_build_info(job_name, build_number)
        time.sleep(30)

    if job.get('result') != 'SUCCESS':
        log(f'Job {job_name} failed!', 2)
        sys.exit(1)
