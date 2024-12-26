import argparse
import json
import random
import string
import requests
import time
from aws_requests_auth.aws_auth import AWSRequestsAuth
import urllib3

urllib3.disable_warnings()


def configure_auth(aws_access_key, aws_secret_access_key, aws_host, aws_region, aws_service):
    auth = AWSRequestsAuth(aws_access_key=aws_access_key,
                           aws_secret_access_key=aws_secret_access_key,
                           aws_host=aws_host,
                           aws_region=aws_region,
                           aws_service=aws_service)
    return auth

def main(args_):
    file_content = open(args_.configuration)
    json_data = json.load(file_content)
    if 'EngineType' in json_data.keys():
        print('\033[92mStart creating\033[0m \033[1mMQ\033[0m \033[92m instance\033[0m')
        broker_name = json_data['BrokerName'] + ''.join(random.choices(string.ascii_lowercase, k=5))
        json_data['BrokerName'] = broker_name
    elif 'Provisioned' in json_data.keys() and 'KafkaVersion' in json_data['Provisioned'].keys():
        print('\033[92mStart creating\033[0m \033[1mMSK\033[0m \033[92m instance\033[0m')
        broker_name = json_data['ClusterName'] + ''.join(random.choices(string.ascii_lowercase, k=5))
        json_data['ClusterName'] = broker_name
    elif 'DomainName' in json_data.keys():
        print('\033[92mStart creating\033[0m \033[1mOpenSearch\033[0m \033[92m instance\033[0m')
        broker_name = json_data['DomainName'] + ''.join(random.choices(string.ascii_lowercase, k=5))
        json_data['DomainName'] = broker_name
    print(f'\033[95mInput json_data:\033[0m \n{json_data}')
    if 'https' in args_.aws_url:
        host = args_.aws_url.replace('https://', '')
        if host[-1] == '/':
            aws_host = host[0:-1]
        else:
            aws_host = host
    else:
        print(f'\033[91mPlease check aws_url: {args_.aws_url}\033[0m')
    print(f'\033[95mAWS host: {aws_host}\033[0m')
    headers = {'Content-type': 'application/json'}
    auth = configure_auth(args_.aws_access_key, args_.aws_secret_access_key, aws_host, args_.aws_region, args_.aws_service)
    response = requests.post(args_.aws_url,
                             headers=headers,
                             json=json_data,
                             auth=auth,
                             verify=False,
                             timeout=1200)
    print(f'\033[95mResponse status_code of creating instance: {response.status_code}\033[0m')
    if 'EngineType' in json_data.keys():
        resp_content = response.json()
        print(f'\033[95mResponse content of creating MQ instance:\033[0m\n {resp_content}')
        connection_url = resp_content['MQWebConsole']
        print(f'\033[92mURL for connection to RABBITMQ:\033[0m \033[1m{connection_url}\033[0m')
    elif 'Provisioned' in json_data.keys():
        if 'KafkaVersion' in json_data['Provisioned'].keys():
            resp_content = response.json()
            print(f'\033[95mResponse content of creating MSK instance:\033[0m\n {resp_content}')
            msk_arn = resp_content['ClusterArn']
            print(f'\033[92mmsk_arn\033[0m: {msk_arn}')
            time.sleep(1200)
            auth = configure_auth(args_.aws_access_key, args_.aws_secret_access_key, '2bzmhh4awzdpokl5yrii3cxdqq0cqozp.lambda-url.us-east-1.on.aws',
                                  args_.aws_region, args_.aws_service)
            json_data = {"ClusterArn": msk_arn}
            print(f'\033[95mPerform REST for get Endpoint of MSK instance\033[0m')
            for attempt in range(5):
                response = requests.post('https://2bzmhh4awzdpokl5yrii3cxdqq0cqozp.lambda-url.us-east-1.on.aws/',
                                         json=json_data,
                                         auth=auth,
                                         verify=False)
                print(f'\033[95mAttempt: {attempt+1}. Response status_code: {response.status_code}\033[0m')
                resp_content = response.json()
                print(f'\033[95mAttempt: {attempt+1}. Response content2:\033[0m \n {resp_content}')
                if 'Endpoints' in resp_content.keys():
                    break
                else:
                    time.sleep(300)
            endpoints = resp_content['Endpoints']
            # connection_url = f'{endpoints[0][0]}:9094,{endpoints[1][0]}:9094'
            connection_url = f'{endpoints[0][0]}:9094'
            print(f'\033[92mURL for connection to MSK:\033[0m \033[1m{connection_url}\033[0m')
    elif 'DomainName' in json_data.keys():
        resp_content = response.content.decode("utf-8")
        print(f'\033[95mResponse content of creating OpenSearch instance:\033[0m\n {resp_content}')
        domain_name = resp_content
        auth = configure_auth(args_.aws_access_key, args_.aws_secret_access_key, 'getip6v65rrvjs2xdz5vhbx73m0qzahu.lambda-url.us-east-1.on.aws',
                              args_.aws_region, args_.aws_service)
        json_data = {"DomainName": domain_name}
        time.sleep(1200)
        for attempt in range(5):
            response = requests.post('https://getip6v65rrvjs2xdz5vhbx73m0qzahu.lambda-url.us-east-1.on.aws/',
                                     json=json_data,
                                     auth=auth,
                                     verify=False)
            print(f'\033[95mAttempt: {attempt+1}. Response status_code: {response.status_code}\033[0m')
            try:
                resp_content = response.json()
                print(f'\033[95mAttempt: {attempt+1}. Response content3:\033[0m \n {resp_content}')
            except:
                print('OpenSearch endpoints still not available. Trying one more time!')
                resp_content = None
            if resp_content and 'vpc' in resp_content.keys():
                break
            else:
                time.sleep(300)
        connection_url = resp_content['vpc']
        print(f'\033[92mURL for connection to OPENSEARCH:\033[0m \033[1m{connection_url}\033[0m')
    with open('.env', 'w') as writer:
        writer.writelines(f'export url="{connection_url}"\n')
        writer.writelines(f'export clusterName="{broker_name}"')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to create instances in AWS')
    parser.add_argument('--configuration', help='Instance configuration')
    parser.add_argument('--aws-url',
                        help='URL to AWS')
    parser.add_argument('--aws-access_key',
                        help='Access key')
    parser.add_argument('--aws-secret-access-key',
                        help='Secret access key')
    parser.add_argument('--aws-region',
                        help='AWS region')
    parser.add_argument('--aws-service',
                        help='AWS service')
    args = parser.parse_args()
    connection_url = main(args)
