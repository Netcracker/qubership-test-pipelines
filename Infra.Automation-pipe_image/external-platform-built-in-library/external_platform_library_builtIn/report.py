import requests
import logging
import sys
import argparse
import os
from tabulate import tabulate
from bs4 import BeautifulSoup
from datetime import datetime
from requests_toolbelt.multipart.encoder import MultipartEncoder


def fetch_pipeline_jobs(gl_url, project_id, pipeline_id, token):
    response = requests.get(
        f"{gl_url}/api/v4/projects/{project_id}/pipelines/{pipeline_id}/jobs?page=1&per_page=100",
        headers={'PRIVATE-TOKEN': token})
    if response.status_code == 200:
        jobs = response.json()
        sorted_jobs = sorted(jobs, key=lambda x: x['id'])
        return sorted_jobs
    else:
        logging.error(f"Failed to fetch pipeline jobs. Status code: {response.status_code}")

def convert_seconds_in_time_format(duration):
    minutes = duration // 60
    seconds = duration % 60
    seconds = str(seconds).split('.')[0]
    time = f"{int(minutes)}m {seconds}s"
    return time

def prepare_jobs_table(sorted_jobs):
    table = []
    total_duration = 0
    for job in sorted_jobs:
        if job['created_at'] and job['name'] and job['name'] != 'Report':
            job_info = collect_job_info(job)
            if job_info['job_status'] == 'success':
                status = f"\033[92m{job_info['job_status']}\033[0m"
            elif job_info['job_status'] == 'failed':
                status = f"\033[91m{job_info['job_status']}\033[0m"
            else:
                status = f"\033[37m{job_info['job_status']}\033[0m"
            table.append([job_info['job_name'], status, job_info['job_duration_in_min'], job_info['job_web_url']])
            if job_info['job_duration']:
                total_duration += job_info['job_duration']
    print(tabulate(table, ['Job Name', 'Status', 'Duration', 'Web Url'], "grid"))
    return table, total_duration

def prepare_result_table(table, total_duration):
    result_table = []
    elapsed_time, success, fail, not_run = 0, 0, 0, 0
    for job in table:
        if 'success' in job[1]:
            success +=1
        elif 'failed' in job[1]:
            fail += 1
        else:
            not_run +=1
    time = convert_seconds_in_time_format(total_duration)
    total = success + fail + not_run
    result_table.append([total, success, fail, not_run, time])
    print(tabulate(result_table, ['Total Jobs', 'Number Of Successful Jobs', 'Number Of Failed Jobs', 'Number Of Not Started Jobs', 'Total Elapsed Time'], "grid"))

# ---------------------------------------- HTML -----------------------------------------------------------------------#
def collect_job_info(job_json):
    job_name = job_json['name']
    job_status = job_json['status']
    job_duration = job_json['duration']
    if job_duration:
        job_duration_in_min = convert_seconds_in_time_format(job_duration)
    else:
        job_duration_in_min = ''
    job_web_url = job_json['web_url']
    job_html_web_url = f'<a href="{job_web_url}">{job_name}</a>'
    job_info = {'job_name': job_name, 'job_status': job_status, 'job_duration': job_duration,
                'job_duration_in_min': job_duration_in_min, 'job_web_url': job_web_url, 'job_html_web_url': job_html_web_url}
    return job_info

# Add hyperlinks to `Job names` + bootstrap classes to table + red background for failed jobs
def modify_jobs_status_table(jobs_status_table_html, web_url_list):
    soup = BeautifulSoup(jobs_status_table_html, 'html.parser')
    table_tag = soup.find('table')
    # Add bootstrap classes for customize table
    table_tag['class'] = ['table', 'table-hover', 'table-bordered', 'table-responsive-md', 'mx-auto', 'table-sm']
    # Add hyperlinks
    for i, row in enumerate(soup.find_all('tr')):
        if i == 0:
            row.attrs['class'] = ['table-primary']
            continue
        cells = row.find_all('td')
        job_name_cell = cells[0]
        job_name_cell.clear()
        job_name_cell.append(BeautifulSoup(web_url_list[i - 1], 'html.parser').a)
        # Make color row depends on job status for failed jobs
        status_cell = cells[1].get_text().strip().lower()
        if status_cell == 'failed':
            row.attrs['class'] = ['table-danger']
        elif status_cell == 'canceled' or status_cell == 'manual':
            row.attrs['class'] = ['table-secondary']
    return str(soup.table)

# Create HTML table with jobs statuses
def prepare_jobs_status_table(sorted_jobs):
    html_table = []
    web_url_list = []
    headers = ['Job Name', 'Status', 'Duration']
    for job in sorted_jobs:
        if job['created_at'] and job['name'] != 'Report':
            job_info = collect_job_info(job)
            html_table.append([job_info['job_name'], job_info['job_status'], job_info['job_duration_in_min']])
            web_url_list.append(job_info['job_html_web_url'])
    jobs_status_table_html = tabulate(html_table, headers=headers, tablefmt="html")
    return modify_jobs_status_table(jobs_status_table_html, web_url_list)

def modify_job_names_with_releases(html_content, releases_name):
    try:
        for key, value in releases_name.items():
            value = releases_name[key].replace('"', '')
            key = key.replace('_name', '')
            html_content = html_content.replace(f'[{key}]', f'[{value}]')
        return html_content
    except:
        print('Not possible to perform modify_job_names_with_releases')
        return html_content

# Collect pipeline information
def collect_pipeline_basis_info(sorted_jobs, total_duration):
    pipeline_username = f"{sorted_jobs[0]['user']['username']} ({sorted_jobs[0]['user']['name']})"
    pipeline_link = sorted_jobs[0]['pipeline']['web_url']
    pipeline_date = sorted_jobs[0]['pipeline']['created_at'].split('.')[0]
    pipeline_ref = sorted_jobs[0]['pipeline']['ref']
    successful_jobs, failed_jobs, not_run_jobs = 0, 0, 0
    for job in sorted_jobs:
        if job['name'] != 'Report':
            if 'success' in job['status']:
                successful_jobs +=1
            elif 'failed' in job['status']:
                failed_jobs += 1
            else:
                not_run_jobs +=1
    pipeline_duration = convert_seconds_in_time_format(total_duration)
    pipeline_total_jobs = successful_jobs + failed_jobs + not_run_jobs
    pipeline_info = {'pipeline_username': pipeline_username, 'pipeline_link': pipeline_link, 'pipeline_date': pipeline_date,
                     'successful_jobs': successful_jobs, 'failed_jobs': failed_jobs, 'not_run_jobs': not_run_jobs,
                     'pipeline_duration': pipeline_duration, 'pipeline_total_jobs': pipeline_total_jobs,
                     'pipeline_ref': pipeline_ref}
    return pipeline_info

# Update data in basic info table + change data in diagram
def prepare_basic_info_table(html_content, pipeline_info):
    html_content = html_content.replace('var_total_jobs', str(pipeline_info['pipeline_total_jobs']))
    pass_rate = pipeline_info['successful_jobs'] / pipeline_info['pipeline_total_jobs'] * 100
    html_content = html_content.replace('var_pass_rate', f'{int(pass_rate)}%')
    html_content = html_content.replace('var_elapsed_time', pipeline_info['pipeline_duration'])
    html_content = html_content.replace('var_pipeline_link', pipeline_info['pipeline_link'])
    html_content = html_content.replace('var_author', pipeline_info['pipeline_username'])
    html_content = html_content.replace('var_date', pipeline_info['pipeline_date'])
    html_content = html_content.replace('successJobs = 0;', f'successJobs = {pipeline_info["successful_jobs"]};')
    html_content = html_content.replace('failedJobs = 0;', f'failedJobs = {pipeline_info["failed_jobs"]};')
    html_content = html_content.replace('notRunJobs = 0;', f'notRunJobs = {pipeline_info["not_run_jobs"]};')
    return html_content

# Remove timestamp part from version
def remove_timestamp_part_from_version(string):
    result = None
    last_dash_index = string.rfind("-")
    second_last_dash_index = string.rfind("-", 0, last_dash_index)
    if second_last_dash_index != -1:
        result = string[:second_last_dash_index]
    if result:
        return result
    else:
        return string

def version_split(text):
    parts = text.strip().split('=')
    if len(parts) == 2:
        key = parts[0].strip().replace('export ', '')
        value = parts[1].strip()
        return key, value

# Possible formats: .cci_file with all releases versions/.cci_file with main versions/.cci_file with list of services/gl variables
def create_versions_dict(versions):
    result_dict = {}
    file_path = '.env_cci'
    if os.path.isfile(file_path):
        with open(file_path, 'r') as file:
            for line in file:
                key, value = version_split(line)
                result_dict[key] = value
    elif versions:
        versions_list = versions.split(',')
        for version in versions_list:
            key, value = version.split('=')
            result_dict[key] = value
    else:
        logging.error('There are no specified versions for report job, also no .env_cci file was found. Exit...')
        return None
    return result_dict

# Create versions table
def prepare_version_table(versions_dict):
    versions_table = []
    releases_name = {}
    headers = None
    for key, value in versions_dict.items():
        if 'cv_' in key or 'psv_' in key or 'n1r_' in key or 'n2r_' in key: ''
            if not headers:
                headers = ['Type', 'Release/Branch', 'Version']
            if '_name' not in key: ''
                release_branch_name = versions_dict[f'{key}_name'].replace('"', '')
                versions_table.append([key, release_branch_name, versions_dict[key]])
            elif '_name' in key: ''
                releases_name[key] = value
        else:
            versions_table.append([key, value])
            if not headers:
                headers = ['Service Name', 'Version']

    versions_table_html = tabulate(versions_table, headers=headers, tablefmt="html")
    soup = BeautifulSoup(versions_table_html, 'html.parser')
    versions_table_tag = soup.find('table')
    versions_table_tag['class'] = ['table', 'table-hover', 'table-bordered', 'table-responsive-md', 'mx-auto', 'table-sm']
    versions_table = str(soup.table)
    return versions_table, releases_name

def add_content_to_div_by_id(html_content, content_to_add, div_id):
    insert_position = html_content.find(div_id)
    modified_content = (html_content[:insert_position] + div_id + f'\n {content_to_add}\n' + html_content[insert_position+len(div_id):])
    return modified_content

# Generate final html file
def create_final_html_file(content, ref):
    current_datetime = datetime.now()
    dt_string = current_datetime.strftime('%d_%m_%Y_%H_%M')
    output_filename = f"report_{ref}_{dt_string}.html"
    with open(output_filename, "w") as file:
        file.write(content)
    return output_filename

def send_report_to_webex(file_name, room_id, token):
    m = MultipartEncoder({'roomId': room_id,
                          'text': f'CI pipeline execution: {file_name}',
                          'files': (f'{file_name}', open(file_name, 'rb'))})
    proxy_url = "http://***.***.***.***:3128"
    proxies = {
        'http': proxy_url,
        'https': proxy_url
    }
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': m.content_type}
    try:
        requests.post('https://webexapis.com/v1/messages', data=m, headers=headers, proxies=proxies)
        logging.info(f'Report was successfully sent to Webex group: {room_id}')
    except requests.exceptions.HTTPError as err:
        logging.error(f'Failed to send HTML file to Webex. HTTP error occurred: {err}')
    except requests.exceptions.RequestException as err:
        logging.error(f'Failed to send HTML file to Webex. Request exception occurred: {err}')
# -------------------------------------------------------------------------------------------------------------------- #

class PrintErrorParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)-5s[%(name)s] - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    parser = PrintErrorParser(description='Script for creating final report based on executed jobs')
    parser.add_argument('--gl_host', default='https://git.qubership.org', help='Gitlab host')
    parser.add_argument('--project_id', default='20633', help='Gitlab project ID')
    parser.add_argument('--pipeline_id', required=True, help='ID of pipeline')
    parser.add_argument('--token', required=True, help='Gitlab Access token')
    parser.add_argument('--versions', required=False, default=None,
                        help='String with installation versions separated by comma')
    parser.add_argument('--webex-room-id', required=False, default=None,  help='Room ID in Webex')
    parser.add_argument('--webex-token', required=False, default=None,  help='Token from Webex Bot')
    args = parser.parse_args()

    jobs = fetch_pipeline_jobs(args.gl_host, args.project_id, args.pipeline_id, args.token)
    table, total_duration = prepare_jobs_table(jobs)
    prepare_result_table(table, total_duration)

    # HTML
    with open('/scripts/external_platform_library_builtIn/report.html', "r") as file:
        html_content = file.read()
    pipeline_info = collect_pipeline_basis_info(jobs, total_duration)
    html_content = prepare_basic_info_table(html_content, pipeline_info)
    versions_dict = create_versions_dict(args.versions)
    versions_table, releases_name = prepare_version_table(versions_dict)
    jobs_status_table = prepare_jobs_status_table(jobs)
    html_content = add_content_to_div_by_id(html_content, jobs_status_table, 'id="status_table">')
    html_content = add_content_to_div_by_id(html_content, versions_table, 'id="versions_table">')
    html_content = modify_job_names_with_releases(html_content, releases_name)
    output_filename = create_final_html_file(html_content, pipeline_info['pipeline_ref'])
    if args.webex_room_id and args.webex_token:
        send_report_to_webex(output_filename, args.webex_room_id, args.webex_token)
