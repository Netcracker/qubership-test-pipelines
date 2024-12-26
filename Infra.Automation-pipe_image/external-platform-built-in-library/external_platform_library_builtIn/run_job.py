import jenkins
import sys
import time
import urllib3
import requests
import logging
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from utils import log

urllib3.disable_warnings()
logger = logging.getLogger(__name__) 

def create_retry_session(retries, backoff_factor, status_forcelist):
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

def run_job(job_name, job_params, jenkins_url, jenkins_user, jenkins_pass, request_type):
    """
        Deploy service with specified job
    """
    retries = 5
    retry_delay = 10
    if not all([job_name, jenkins_url]):
        logger.info(f'Job name or Jenkins url is not specified. Exiting')
        sys.exit(1)
    session = create_retry_session(retries=5, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
    logger.info(f'Running job {job_name}')
    auth_response = session.get(jenkins_url, auth=(jenkins_user, jenkins_pass), timeout=10)
    if auth_response.status_code != 200:
        logger.error(f'Failed to authenticate with Jenkins: {auth_response.status_code} {auth_response.text}')
        sys.exit(1)

    server = jenkins.Jenkins(jenkins_url, username=jenkins_user, password=jenkins_pass)

    if request_type == 'get':
        print(f'Using base approach with build_job method and GET request')
        try:
            queue_n = server.build_job(job_name, job_params)
        except requests.exceptions.RequestException as e:
            logger.error(f"Connection error while fetching build info: {e}! Retry to connect....")
            time.sleep(retry_delay)
    elif request_type == 'post':
        print(f'Using custom approach with method POST request instead build_job method')
        url = server.build_job_url(job_name)
        url = url.replace('build', 'buildWithParameters')
        print(f'URL: {url}')
        response = requests.post(url, auth=(jenkins_user, jenkins_pass), data=job_params)
        print(response.headers)
        location = response.headers['Location']
        if location.endswith('/'):
            location = location[:-1]
        parts = location.split('/')
        queue_n = int(parts[-1])

    build_number = -1
    while build_number == -1:
        logger.info('Waiting for job to start...')
        queue_item_info = server.get_queue_item(queue_n)
        if queue_item_info.get('why') is not None:
            time.sleep(3)
        else:
            build_number = queue_item_info.get('executable', {}).get('number')
    else:
        logger.info(f'Job has build number: {build_number}')
    try:
        job = server.get_build_info(job_name, build_number)
    except requests.exceptions.RequestException as e:
        logger.error(f"Connection error while fetching build info: {e}! Retry to connect....")
        time.sleep(retry_delay)

    logger.info(f'Link to build: {job.get("url")}')

    while job.get('building'):
        logger.info('Waiting job completing...')
        try:
          job = server.get_build_info(job_name, build_number)
        except requests.exceptions.RequestException as e:
          logger.error(f"Connection error while fetching build info: {e}! Retry to connect....")
        time.sleep(30)

    if job.get('result') != 'SUCCESS':
        logger.error(f'\033[91mJob {job_name} failed!\033[0m')
        sys.exit(1)
    else:
        logger.info(f'\033[32m----- Finished: SUCCESS -----\033[0m')
