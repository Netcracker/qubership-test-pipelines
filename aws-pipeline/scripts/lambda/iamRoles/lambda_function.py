import json
import boto3
import botocore
import os
import time

from jsonschema import validate

SCHEMA_FILE = open('schema.json')
SCHEMA = json.load(SCHEMA_FILE)

def update_oidc_id(input_dict, oidc_id, region, aws_account_id):
    for key, value in input_dict.items():
        if isinstance(value, dict):
            update_oidc_id(value, oidc_id, region, aws_account_id)
        elif isinstance(value, list):
            for item in value:
                update_oidc_id(item, oidc_id, region, aws_account_id)
        elif isinstance(value, str):
            input_dict[key] = value.replace('<oidc_id>', oidc_id).replace('<aws_region>', region).replace('<aws_account_id>', aws_account_id)

def update_string_equals_keys(input_dict, oidc_id, region):
    for statement in input_dict["Statement"]:
        if "Condition" in statement and "StringEquals" in statement["Condition"]:
            string_equals_dict = statement["Condition"]["StringEquals"]
            updated_string_equals_dict = {}
            for key, value in string_equals_dict.items():
                updated_key = key.replace('<oidc_id>', oidc_id).replace('<aws_region>', region)
                updated_string_equals_dict[updated_key] = value
            statement["Condition"]["StringEquals"] = updated_string_equals_dict

def prepare_trust_policy(policy_file, oidc_id, region, aws_account_id):
    with open(policy_file) as file:
        input_dict = json.load(file)
    update_oidc_id(input_dict, oidc_id, region, aws_account_id)
    update_string_equals_keys(input_dict, oidc_id, region)
    str_trust_policy = str(input_dict).replace(' ', '').replace('\'', '"')
    print(f'Updated trust_policy: {str_trust_policy}')
    return str_trust_policy

def lambda_handler(event, context):
    s1 = json.dumps(event)
    params = json.loads(s1)

    print("Received params: \n{}".format(params))
    print("Validating received params for schema compliance...")
    try:
        validate(instance=event, schema=SCHEMA)
    except:
        print("Params doesn't match target schema!")
        return

    region = os.environ['REGION']
    cluster_name = params['CLUSTER_NAME']
    aws_account_id = params['AWS_ACCOUNT_ID']

    client = boto3.client('eks', region_name=region)
    try:
        cluster = client.describe_cluster(name=cluster_name)
        oidc_issuer = cluster['cluster']['identity']['oidc']['issuer']
        oidc_id = oidc_issuer.split('/')[-1]
        print(f'oidc_id: {oidc_id} for cluster: {cluster_name}')
    except botocore.exceptions.ClientError as error:
        return {"errorcode": error.response['Error']['Code'],
                "errormessage": error.response['Error']['Message']}
    except Exception as e:
        return {"errorcode": "Something went wrong. Try later or contact the admin. {}".format(e)}

    load_balancer_policy_str = prepare_trust_policy('load-balancer-role-trust-policy.json', oidc_id, region, aws_account_id)
    # persistent_storage_policy_str = prepare_trust_policy('persistent-storage-role-trust-policy.json', oidc_id, region, aws_account_id)

    # Delete existing (old) Roles for cluster
    client = boto3.client('iam', region_name=region)
    response = client.list_roles()
    for role in response['Roles']:
        if role['RoleName'] == f'EKSLoadBalancerRoleLambda-{cluster_name}':
            print(f'Role: {role["RoleName"]} will be deleted!')
            client.detach_role_policy(
                RoleName=role['RoleName'],
                PolicyArn=f'arn:aws:iam::{aws_account_id}:policy/AWSLoadBalancerControllerIAMPolicy')
            client.delete_role(RoleName=role['RoleName'])
        # elif role['RoleName'] == f'EKS_EFS_CSI_RoleLambda-{cluster_name}':
        #     print(f'Role: {role["RoleName"]} will be deleted!')
        #     client.detach_role_policy(
        #         RoleName=role['RoleName'],
        #         PolicyArn=f'arn:aws:iam::{aws_account_id}:policy/AmazonEKS_EFS_CSI_Driver_Policy')
        #     client.delete_role(RoleName=role['RoleName'])

    time.sleep(30)

    # Create roles
    role_arns = {}
    response = client.create_role(
        AssumeRolePolicyDocument=load_balancer_policy_str,
        Path='/',
        RoleName=f'EKSLoadBalancerRoleLambda-{cluster_name}'
    )
    print(f'Response of creating AmazonEKSLoadBalancerControllerRoleQALambda-{cluster_name} role: {response}')
    role_arns['arnloadbalancer'] = response['Role'].get('Arn')

    # response = client.create_role(
    #     AssumeRolePolicyDocument=persistent_storage_policy_str,
    #     Path='/',
    #     RoleName=f'EKS_EFS_CSI_RoleLambda-{cluster_name}'
    # )
    # print(f'Response of creating AmazonEKS_EFS_CSI_DriverRoleQALambda-{cluster_name} role: {response}')
    # role_arns['arnekscsi'] = response['Role'].get('Arn')

    # Attach Policies
    response = client.attach_role_policy(
        PolicyArn=f'arn:aws:iam::{aws_account_id}:policy/AWSLoadBalancerControllerIAMPolicy',
        RoleName=f'EKSLoadBalancerRoleLambda-{cluster_name}'
    )
    print(f'Response of attaching AWSLoadBalancerControllerIAMPolicy role_policy: {response}')
    # response = client.attach_role_policy(
    #     PolicyArn=f'arn:aws:iam::{aws_account_id}:policy/AmazonEKS_EFS_CSI_Driver_Policy',
    #     RoleName=f'EKS_EFS_CSI_RoleLambda-{cluster_name}'
    # )
    # print(f'Response of attaching AmazonEKS_EFS_CSI_Driver_Policy role_policy: {response}')

    print(f'Arns for roles: {role_arns}')
    return role_arns
