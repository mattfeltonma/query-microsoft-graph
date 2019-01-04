## Import necessary modules and functions
##

import json
import requests
import logging
from adal import AuthenticationContext

## Setup Python logging module to create a logging instance for this module and
## to write log entries to a file with INFO log level

logging.basicConfig(filename='graphapilog.txt', level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def obtain_accesstoken(tenantname,clientid,clientsecret,resource):
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
    return headers

def makeapirequest(endpoint,headers):
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


