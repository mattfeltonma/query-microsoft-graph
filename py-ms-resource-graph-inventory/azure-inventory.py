import sys
import json
import logging
import adal
import pandas
import azure.mgmt.resourcegraph
from argparse import ArgumentParser
from msrestazure.azure_active_directory import AADTokenCredentials

# Function used to obtain an access token
def obtain_accesstoken(tenantname,scope,appid):
    
    # Obtain acess token using Adal library
    logging.info("Attempting to obtain an access token...")
    result = None
    context = adal.AuthenticationContext(
        authority='https://login.microsoftonline.com/' + tenantname
    )

    code = context.acquire_user_code(
        resource = scope,
        client_id = appid
    )
    print(code['message'])
    token = context.acquire_token_with_device_code(scope, code, appid)
    return token

# Function used to create the request
def resource_request(subscription_ids,query,page_token=None):
    
    logging.info("Creating query option and query request...")
    # Configure query options
    queryoption = azure.mgmt.resourcegraph.models.QueryRequestOptions(
        skip_token = page_token,
        top = 1
    )

    # Configure query request
    queryrequest = azure.mgmt.resourcegraph.models.QueryRequest(
        subscriptions = subscription_ids,
        query = query,
        options = queryoption
    )
    return queryrequest

# Function used to export data
def export_data(data):

    
    # Create a list of column names
    column_names = []
    for column in data.columns:
        column_names.append(column.name)
    
    # Create a DataFrame using the Pandas module and export it as JSON
    dfobj = pandas.DataFrame(data.rows, columns = column_names)
    return dfobj

# Main function
def main():
    try:

        # Configure logging mechanism
        logging.basicConfig(filename='resource_inventory.log',level=logging.INFO,format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Process parameters file
        parser = ArgumentParser()
        parser.add_argument('-parameterfile', type=str, help='JSON file with parameters')
        parser.add_argument('-exportfile', type=str, default='azure_resources.json', help='Name of export file (default: azure_resources.json')
        args = parser.parse_args()

        with open(args.parameterfile) as json_data:
            config = json.load(json_data)

        # Obtain an access token
        token = obtain_accesstoken(tenantname=config['tenantname'],scope=config['scope'],appid=config['appid'])
        credential = AADTokenCredentials(token=token,client_id=None)

        # Setup the Resource Graph connection and issue the query
        client = azure.mgmt.resourcegraph.ResourceGraphClient(credential)

        logging.info("Issuing request to resource graph...")
        result = client.resources(
            query=resource_request(subscription_ids=config['subscription_ids'],query=config['query']),
            )
        df_results = export_data(result.data)

        # Check for paged results
        while result.skip_token != None:
            logging.info("Retrieving " + str(result.count) + " paged records")
            result = client.resources(
                query=resource_request(subscription_ids=config['subscription_ids'],query=config['query'],page_token=result.skip_token)
            )

            # Append new records to DataFrame
            df_results = df_results.append(export_data(result.data))

        df_results.to_json(path_or_buf=args.exportfile,orient='records')

    except Exception as e:
        logging.error("Execution error",exc_info=True)
       
# Run main function
if __name__ == "__main__":
    main()