import json
import yaml
import argparse

def main(args):
    print(f'Got DD: {args.dd}')
    json_dd = json.loads(args.dd)
    services_images = {}
    component = json_dd['metadata']['component']
    components = ['opensearch-service', 'zookeeper-service', 'rabbitmq', 'mistral', 'kafka', 'kafka-services',
                  'streaming-service', 'consul-service', 'vault-operator', 'jaeger']
    for service in json_dd['services']:
        services_images[service['service_name']] = service['full_image_name']
        if component in components or 'RabbitMQ' in component or 'Streaming_zookeeper-service' in component:
            if 'deploy_param' in service:
                services_images[service['deploy_param']] = service['full_image_name']
            else:
                if component == 'opensearch-service':
                    services_images['opensearchOperator'] = service['full_image_name']
                elif component == 'zookeeper-service' or 'Streaming_zookeeper-service' in component:
                    services_images['zooKeeperOperator'] = service['full_image_name']
                elif component == 'rabbitmq' or 'RabbitMQ' in component:
                    services_images['operator'] = service['full_image_name']
                elif component == 'mistral':
                    services_images['mistralOperator'] = service['full_image_name']
                elif component == 'kafka':
                    services_images['kafkaOperator'] = service['full_image_name']
                elif component == 'kafka-services':
                    services_images['kafkaServiceOperator'] = service['full_image_name']
                    services_images['kafka-service'] = service['full_image_name']
                elif component == 'streaming-service':
                    services_images['streamingOperator'] = service['full_image_name']
                    services_images['streaming-service'] = service['full_image_name']
                elif component == 'consul-service':
                    services_images['consulIntegrationTests'] = service['full_image_name']
                elif component == 'vault-operator':
                    services_images['vault_operator'] = service['full_image_name']
    with open(args.parameters_file, "r") as stream:
        data = yaml.safe_load(stream)
        new_data = {'dD': {key: {'image': value} for key, value in services_images.items()}}
        data.update(new_data)
        if component == 'MONITORING' or component == 'thirdparty.services_airflow' or component == 'thirdparty.services_spark-operator-gcp':
            new_data = {'global': {'dD': {key: {'image': value} for key, value in services_images.items()}}}
            data.update(new_data)

    with open(args.parameters_file, 'w') as file:
        yaml.dump(data, file, default_flow_style=False)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to prepare namespaces in cloud')
    parser.add_argument('--dd',
                        help='Json of DD for service')
    parser.add_argument('--parameters-file',
                        help='Path to file with service parameters')
    args = parser.parse_args()
    main(args)
