## Import necessary modules and functions
##

import json
import logging
import boto3

logging.basicConfig(filename='graphapilog.txt', level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

## Retrieve parameter from AWS Parameter Store

def get_parametersParameterStore(parameterName,region):
    try:
        client = boto3.client('ssm', region_name=region)
        response = client.get_parameter(
            Name=parameterName,
            WithDecryption=True
        )
        return response['Parameter']['Value']
    except Exception as e:
        logging.error('Error retrieving parameter: ',e)
        
def put_s3(bucket,prefix,region,filename):
    try:
        s3 = boto3.client('s3', region_name=region)
        s3.upload_file(filename,bucket,prefix + "/" + filename)
    except Exception as e:
        logging.error('Error writing file to S3: ', e)
