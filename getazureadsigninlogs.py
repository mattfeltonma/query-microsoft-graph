## Import necessary modules and functions
##

import json
import requests
import logging
import boto3
from pathlib import Path
from adal import AuthenticationContext
from argparse import ArgumentParser

## Setup Python logging module to create a logging instance for this module and
## to write log entries to a file with INFO log level

logging.basicConfig(filename='graphapilog.txt', level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

## Get parameters from AWS System Manager Parameter store if parameterStore option
## was used

def get_parameters(parameterClientID,parameterClientSecret):
    try:
        client = boto3.client('ssm', region_name=region)
        parresponse = client.get_parameters(
            Names=[
                parameterClientID,
                parameterClientSecret],
            WithDecryption=True
        )
        credentials = dict();
        credentials['clientid'] = parresponse['Parameters'][0]['Value']
        credentials['secret'] = parresponse['Parameters'][1]['Value']
        return credentials
    except Exception as e:
        print ('Error getting information from AWS Parameter Store: ',e)


## Process parameters file
##

parser = ArgumentParser()
parser.add_argument('sourcefile', type=str, help='JSON file with parameters')
parser.add_argument('--parameterStore', help='Use AWS Systems Manager Parameter Store',action='store_true')
parser.add_argument('--bucket', help='Write results to S3 bucket',action='store_true')
args = parser.parse_args()

try:
    with open(args.sourcefile) as json_data:
        d = json.load(json_data)
            
        tenantname = d['parameters']['tenantname']
        resource = d['parameters']['resource']
        endpoint = d['parameters']['endpoint']
        filename = d['parameters']['filepath']
        bucket = d['parameters']['bucket']
                
        ## Get parameters from AWS Systems Manager if parameterStore option was used
        ##

        if args.parameterStore:
            region = d['parameters']['region']
            parameterClientID = d['parameters']['clientIdParam']
            parameterClientSecret = d['parameters']['clientSecParam']
            credentials = get_parameters(parameterClientID,parameterClientSecret)
            clientid = credentials['clientid']
            clientsecret = credentials['secret']
        else:
            clientid = d['parameters']['clientid']
            clientsecret = d['parameters']['clientsecret']

        if args.bucket:
            region = d['parameters']['region']
            bucket = d['parameters']['bucket']

except Exception as e:
    print('Error reading parameter file: ',e)


## Use Python Requests module to make requests of Microsoft Graph API
## and additionally handle paged responses

def makeAPIRequest(endpoint,headers):
    try:
        response = requests.get(endpoint,headers=headers)
        if response.status_code == 200:
            logging.info('HTTP GET: ' + endpoint)
            json_data = json.loads(response.text)
            
            ## This section handles paged results and combines the results 
            ## into a single JSON response.  This may need to be modified
            ## if results are too large

            if '@odata.nextLink' in json_data.keys():
                record = makeAPIRequest(json_data['@odata.nextLink'],headers)
                entries = len(record['value'])
                count = 0
                while count < entries:
                    json_data['value'].append(record['value'][count])
                    count += 1
            return(json_data)
        else:
            logging.error('Request failed: ', response.status_code, ' - ', response.text)
    except Exception as e:
        logging.error('Error querying Microsoft Graph API: ', e)


## Use Python Microsoft ADAL module to obtain an access token for Azure AD
## API and create header for requests

try:
    auth_context = AuthenticationContext('https://login.microsoftonline.com/' +
        tenantname)
    token = auth_context.acquire_token_with_client_credentials(
        resource=resource,client_id=clientid,
        client_secret=clientsecret)
except Exception as e:
    logging.error('Error obtaining access token: ', e)

headers = {'Content-Type':'application/json', \
    'Authorization':'Bearer {0}'.format(token['accessToken'])}

## Use Python Requests module to make requests from Azure API checking for OData
## paging

data = makeAPIRequest(endpoint,headers=headers)
try:
    my_file = Path(filename)
    with open(filename,'w') as f:
        
        ## If the data was paged remove the @odata.nextLink key
        ## to clean up the data before writing it to a file

        if '@odata.nextLink' in data.keys():
            del data['@odata.nextLink']
        f.write(json.dumps(data))
except Exception as e:
    logging.error('Error writing to file: ', e)

try:
    if args.bucket:
        s3 = boto3.client('s3', region_name=region)
        s3.upload_file(filename,bucket,"graphapi/" + filename)
except Exception as e:
    logging.error('Request to write to s3 failed: ', e)


