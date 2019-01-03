## Import necessary modules and functions
##

import json
import requests
import logging
from awsintegration import get_parametersParameterStore,put_s3
from adal import AuthenticationContext
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

clientid = get_parametersParameterStore(clientid_param,aws_region)
clientsecret = get_parametersParameterStore(clientsecret_param,aws_region)

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
    with open(filename,'w') as f:
        
        ## If the data was paged remove the @odata.nextLink key
        ## to clean up the data before writing it to a file

        if '@odata.nextLink' in data.keys():
            del data['@odata.nextLink']
        f.write(json.dumps(data))
except Exception as e:
    logging.error('Error writing to file: ', e)


if args.bucket:
    put_s3(bucket,prefix,region)


