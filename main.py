## Import necessary modules and functions
##

import json
import requests
import logging
import graphapi
import awsintegration
from argparse import ArgumentParser

## Setup Python logging module to create a logging instance for this module and
## to write log entries to a file with INFO log level

logging.basicConfig(filename='graphapilog.txt', level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


## Process parameters file and retrieve data
##

parser = ArgumentParser()
parser.add_argument('sourcefile', type=str, help='JSON file with parameters')
parser.add_argument('--bucket', help='Write results to S3 bucket',action='store_true')
args = parser.parse_args()

try:
    with open(args.sourcefile) as json_data:
        d = json.load(json_data)
        tenantname = d['parameters']['tenantname']
        resource = d['parameters']['resource']
        endpoint = d['parameters']['endpoint']
        filename = d['parameters']['filename']
        aws_region = d['parameters']['aws_region']
        clientid_param = d['parameters']['clientid_param']
        clientsecret_param = d['parameters']['clientsecret_param']
        if args.bucket:
            bucket = d['parameters']['bucket']
            prefix = d['parameters']['prefix']
            
except Exception as e:
    print('Error reading parameter file: ',e)

## Retrieve Azure AD application credentials from Parameter Store
##

clientid = awsintegration.get_parametersParameterStore(clientid_param,aws_region)
clientsecret = awsintegration.get_parametersParameterStore(clientsecret_param,aws_region)

## Obtain access token from Azure AD
##

token = graphapi.obtain_accesstoken(tenantname,clientid,clientsecret,resource)

## Query MS Graph API Endpoint
##

data = graphapi.makeapirequest(endpoint,token)

try:
    with open(filename,'w') as f:
        
        ## If the data was paged remove the @odata.nextLink key
        ## to clean up the data before writing it to a file

        if '@odata.nextLink' in data.keys():
            del data['@odata.nextLink']
        f.write(json.dumps(data))
except Exception as e:
    logging.error('Error writing to file: ', e)


if args.bucket:
    awsintegration.put_s3(bucket,prefix,aws_region,filename)


