## Import necessary modules and functions
##

import json
import requests
import logging
import time
import graphapi
import awsintegration

## SIGN IN LOGS ONLY
## import re

from argparse import ArgumentParser



## Setup Python logging module to create a logging instance for this module and
## to write log entries to a file with INFO log level
    
logging.basicConfig(filename='msapiquery.log', level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

## Process parameters file and retrieve data
##

parser = ArgumentParser()
parser.add_argument('sourcefile', type=str, help='JSON file with parameters')
parser.add_argument('--s3', help='Write results to S3 bucket',action='store_true')
args = parser.parse_args()

try:
    with open(args.sourcefile) as json_data:
        d = json.load(json_data)
        tenantname = d['parameters']['tenantname']
        resource = d['parameters']['resource']
        endpoint = d['parameters']['endpoint']
        filename = d['parameters']['filename']
        aws_region = d['parameters']['aws_region']
        q_param = d['parameters']['q_param']
        clientid_param = d['parameters']['clientid_param']
        clientsecret_param = d['parameters']['clientsecret_param']
        if args.s3:
            bucket = d['parameters']['bucket']
            prefix = d['parameters']['prefix']

## Retrieve Azure AD application credentials from Parameter Store
##
    logging.info('Attempting to contact Parameter Store...')
    clientid = awsintegration.get_parametersParameterStore(clientid_param,aws_region)
    clientsecret = awsintegration.get_parametersParameterStore(clientsecret_param,aws_region)

## Obtain access token from Azure AD
##
    logging.info('Attempting to obtain an access token...')
    token = graphapi.obtain_accesstoken(tenantname,clientid,clientsecret,resource)

## Query MS Graph API Endpoint
##

    data = graphapi.makeapirequest(endpoint,token,q_param)

## SIGN IN LOGS ONLY
##  for record in data['value']:
##      record['createdDateTime'] = re.sub('[TZ]',' ', record['createdDateTime'])

## Write results to a file
##
    logging.info('Attempting to write results to a file...')
    timestr = time.strftime("%Y-%m-%d")
    filename = timestr + '-' + filename
    with open(filename,'w') as f:
        
        ## If the data was paged remove the @odata.nextLink key
        ## to clean up the data before writing it to a file

        if '@odata.nextLink' in data.keys():
            del data['@odata.nextLink']
        f.write(json.dumps(data))

## Send the file to S3 if the user has set the bucket switch 
##
    
    if args.s3:
        logging.info('Attempting to write results to %s S3 bucket...',bucket)
        awsintegration.put_s3(bucket,prefix,aws_region,filename)
except Exception as e:
    logging.error('Exception thrown: %s',e)
    print('Error running script.  Review the log file for more details')


