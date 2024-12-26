import json
import boto3
import botocore
import os
import base64

from jsonschema import validate

SCHEMA_FILE = open('schema.json')
SCHEMA = json.load(SCHEMA_FILE)

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
    client_id = 'sts.amazonaws.com'
    fingerprint_str = params['FINGERPRINT']

    client = boto3.client('eks', region_name=region)
    try:
        cluster = client.describe_cluster(name=cluster_name)
        oidc_issuer_url = cluster['cluster']['identity']['oidc']['issuer']
        print(f'oidc_issuer_url: {oidc_issuer_url}')
    except botocore.exceptions.ClientError as error:
        return {"errorcode": error.response['Error']['Code'],
                "errormessage": error.response['Error']['Message']}
    except Exception as e:
        return {"errorcode": "Something went wrong. Try later or contact the admin. {}".format(e)}

    client = boto3.client('iam', region_name=region)

    # Create open_id_connect_provider
    try:
        response = client.create_open_id_connect_provider(
            ClientIDList=[client_id],
            ThumbprintList=[str(fingerprint_str)],
            Url=oidc_issuer_url
        )
        print(response)
    except botocore.exceptions.ClientError as error:
        return {"errorcode": error.response['Error']['Code'],
                "errormessage": error.response['Error']['Message']}
    except Exception as e:
        return {"errorcode": "Something went wrong during creating OpenIDConnectProvider. {}".format(e)}