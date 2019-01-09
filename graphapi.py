## Import necessary modules and functions
##

import json
import requests
import logging
import urllib

from adal import AuthenticationContext

log = logging.getLogger(__name__)

## Use Microsoft ADAL module to obtain a bearer token for access to Azure AD and
## create a header to pass in a request

def obtain_accesstoken(tenantname,clientid,clientsecret,resource):
    auth_context = AuthenticationContext('https://login.microsoftonline.com/' +
        tenantname)
    token = auth_context.acquire_token_with_client_credentials(
        resource=resource,client_id=clientid,
        client_secret=clientsecret)
    return token

## Create a valid header using a provided access token and make a request
## of the MS Graph API

def makeapirequest(endpoint,token,q_param=None):
    ## Create a valid header using the provided access token
    ##
        
    headers = {'Content-Type':'application/json', \
    'Authorization':'Bearer {0}'.format(token['accessToken'])}
        
    ## Submit a request to the API and handle OData paged results
    ##
    

    
    ## This section handles a bug with the Python requests module which
    ## encodes blank spaces to plus signs instead of %20.  This will cause
    ## issues with OData filters
    
    if q_param != None:
        response = requests.get(endpoint,headers=headers,params=q_param)
        log.info('Request made to %s...',response.url)
    else:
        response = requests.get(endpoint,headers=headers)
        log.info('Request made to %s...',response.url)
    if response.status_code == 200:
        json_data = json.loads(response.text)
            
        ## This section handles paged results and combines the results 
        ## into a single JSON response.  This may need to be modified
        ## if results are too large

        if '@odata.nextLink' in json_data.keys():
            log.info('Paged result returned...')
            record = makeapirequest(json_data['@odata.nextLink'],token)
            entries = len(record['value'])
            count = 0
            while count < entries:
                json_data['value'].append(record['value'][count])
                count += 1
        return(json_data)
    else:
        raise Exception('Request failed with ',response.status_code,' - ',
            response.text)



