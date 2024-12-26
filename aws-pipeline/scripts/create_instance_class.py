import argparse
import json
import random
import string
import requests
import time
from aws_requests_auth.aws_auth import AWSRequestsAuth
import urllib3

urllib3.disable_warnings()

headers = {'Content-type': 'application/json'}
aws_get_msk_endpoint_url = '2bzmhh4awzdpokl5yrii3cxdqq0cqozp.lambda-url.us-east-1.on.aws'
aws_get_opensearch_endpoint_url = 'getip6v65rrvjs2xdz5vhbx73m0qzahu.lambda-url.us-east-1.on.aws'


class AWS:

    def __init__(self, configuration, aws_url, aws_access_key, aws_secret_access_key, aws_region, aws_service):
        self.configuration = configuration
        self.aws_url = aws_url
        self.aws_access_key = aws_access_key
        self.aws_secret_access_key = ''
        self.aws_region = aws_region
        self.aws_service = aws_service

    def configure_auth(self, aws_host):
        auth = AWSRequestsAuth(aws_host=aws_host,
                               aws_access_key=self.aws_access_key,
                               aws_secret_access_key=self.aws_secret_access_key,
                               aws_region=self.aws_region,
                               aws_service=self.aws_service)
        return auth

    def make_request(self, aws_url, auth, json_data):
        response = requests.post(aws_url,
                                 headers=headers,
                                 json=json_data,
                                 auth=auth,
                                 verify=False,
                                 timeout=1200)
        return response

    def read_instance_configuration(self):
        file_content = open(self.configuration)
        try:
            json_configuration = json.load(file_content)
            print(f'\033[95mInput json_data:\033[0m \n{json_configuration}')
            return json_configuration
        except:
            print(f'\033[95mInput json_data from file {self.configuration} is incorrect! Please fix it.')

    def create_unique_instance_name(self, json_configuration):
        if 'EngineType' in json_configuration.keys():
            print('\033[92mStart creating\033[0m \033[1mMQ\033[0m \033[92m instance\033[0m')
            broker_name = json_configuration['BrokerName'] + '-' + ''.join(random.choices(string.ascii_lowercase, k=5))
            json_configuration['BrokerName'] = broker_name
        elif 'Provisioned' in json_configuration.keys() and 'KafkaVersion' in json_configuration['Provisioned'].keys():
            print('\033[92mStart creating\033[0m \033[1mMSK\033[0m \033[92m instance\033[0m')
            broker_name = json_configuration['ClusterName'] + '-' + ''.join(random.choices(string.ascii_lowercase, k=5))
            json_configuration['ClusterName'] = broker_name
        elif 'DomainName' in json_configuration.keys():
            print('\033[92mStart creating\033[0m \033[1mOpenSearch\033[0m \033[92m instance\033[0m')
            broker_name = json_configuration['DomainName'] + '-' + ''.join(random.choices(string.ascii_lowercase, k=5))
            json_configuration['DomainName'] = broker_name
        return json_configuration

    def configure_aws_host(self):
        if 'https' in self.aws_url:
            host = self.aws_url.replace('https://', '')
            if host[-1] == '/':
                aws_host = host[0:-1]
            else:
                aws_host = host
        else:
            print(f'\033[91mPlease check aws_url: {self.aws_url}\033[0m')
            exit(1)
        print(f'\033[95mAWS host: {aws_host}\033[0m')
        return aws_host

    def get_mq_endpoint(self, response):
        resp_content = response.json()
        print(f'\033[95mResponse content of creating MQ instance:\033[0m\n {resp_content}')
        connection_url = resp_content['MQWebConsole']
        print(f'\033[92mURL for connection to RABBITMQ:\033[0m \033[1m{connection_url}\033[0m')
        time.sleep(600)
        return connection_url

    def get_msk_endpoint(self, response):
        resp_content = response.json()
        print(f'\033[95mResponse content of creating MSK instance:\033[0m\n {resp_content}')
        msk_arn = resp_content['ClusterArn']
        print(f'\033[92mmsk_arn\033[0m: {msk_arn}')
        time.sleep(1200)
        auth = self.configure_auth(aws_host=aws_get_msk_endpoint_url)
        json_data = {"ClusterArn": msk_arn}
        print(f'\033[95mPerform REST for get Endpoint of MSK instance\033[0m')
        for attempt in range(5):
            resp = self.make_request(f'https://{aws_get_msk_endpoint_url}/', auth, json_data)
            print(f'\033[95mAttempt: {attempt + 1}. Response status_code: {resp.status_code}\033[0m')
            resp_content = resp.json()
            print(f'\033[95mAttempt: {attempt + 1}. Response content2:\033[0m \n {resp_content}')
            if 'Endpoints' in resp_content.keys():
                break
            else:
                time.sleep(300)
        endpoints = resp_content['Endpoints']
        connection_url = f'{endpoints[0][0]}:9094'
        print(f'\033[92mURL for connection to MSK:\033[0m \033[1m{connection_url}\033[0m')
        return connection_url

    def get_opensearch_endpoint(self, response):
        resp_content = response.content.decode("utf-8")
        print(f'\033[95mResponse content of creating OpenSearch instance:\033[0m\n {resp_content}')
        domain_name = resp_content
        auth = self.configure_auth(aws_host=aws_get_opensearch_endpoint_url)
        json_data = {"DomainName": domain_name}
        time.sleep(1200)
        for attempt in range(10):
            response = self.make_request(f'https://{aws_get_opensearch_endpoint_url}/', auth, json_data)
            print(f'\033[95mAttempt: {attempt + 1}. Response status_code: {response.status_code}\033[0m')
            try:
                resp_content = response.json()
                print(f'\033[95mAttempt: {attempt + 1}. Response content3:\033[0m \n {resp_content}')
            except:
                print('OpenSearch endpoints still not available. Trying one more time!')
                resp_content = None
            if resp_content and 'vpc' in resp_content.keys():
                break
            else:
                time.sleep(300)
        connection_url = f"https://{resp_content['vpc']}"
        print(f'\033[92mURL for connection to OPENSEARCH:\033[0m \033[1m{connection_url}\033[0m')
        return connection_url

    def create_env_file(self, connection_url, instance_name, env_file='.env'):
        with open(env_file, 'w') as writer:
            writer.writelines(f'export url="{connection_url}"\n')
            writer.writelines(f'export clusterName="{instance_name}"')


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

    aws_obj = AWS(configuration=args.configuration,
                  aws_url=args.aws_url,
                  aws_access_key=args.aws_access_key,
                  aws_secret_access_key=args.aws_secret_access_key,
                  aws_region=args.aws_region,
                  aws_service=args.aws_service)
    json_configuration = aws_obj.read_instance_configuration()
    configs = aws_obj.create_unique_instance_name(json_configuration)
    aws_host = aws_obj.configure_aws_host()
    auth = aws_obj.configure_auth(aws_host)
    if json_configuration.get('action') == 'start_eks' or json_configuration.get('action') == 'stop_eks':
        response = aws_obj.make_request(aws_url=args.aws_url, auth=auth, json_data={})
        if response.status_code == 200:
            print(f'{response.status_code}, Action for EKS cluster was {json_configuration.get("action")} and performed successfully')
            exit(0)
        else:
            print(f'{response.status_code} Something went wrong')
            exit(1)
    else:
        response = aws_obj.make_request(aws_url=args.aws_url, auth=auth, json_data=configs)
        print(f'RESPONSE: {response.content}')
    if 'EngineType' in configs.keys():
        connection_url = aws_obj.get_mq_endpoint(response)
        aws_obj.create_env_file(connection_url=connection_url, instance_name=configs['BrokerName'], env_file='.env_mq')
    elif 'Provisioned' in configs.keys():
        if 'KafkaVersion' in configs['Provisioned'].keys():
            connection_url = aws_obj.get_msk_endpoint(response)
            aws_obj.create_env_file(connection_url=connection_url, instance_name=configs['ClusterName'], env_file='.env_msk')
    elif 'DomainName' in configs.keys():
        connection_url = aws_obj.get_opensearch_endpoint(response)
        aws_obj.create_env_file(connection_url=connection_url, instance_name=configs['DomainName'], env_file='.env_opensearch')
