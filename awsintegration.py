## Import necessary modules and functions
##

import json
import boto3
import logging

log = logging.getLogger(__name__)

## Retrieve parameter from AWS Parameter Store

def get_parametersParameterStore(parameterName,region):
    log.info('Request %s from Parameter Store',parameterName)
    client = boto3.client('ssm', region_name=region)
    response = client.get_parameter(
        Name=parameterName,
        WithDecryption=True
    )
    return response['Parameter']['Value']
        
def put_s3(bucket,prefix,region,filename):
    s3 = boto3.client('s3', region_name=region)
    s3.upload_file(filename,bucket,prefix + "/" + filename)
