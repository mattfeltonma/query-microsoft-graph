# Microsoft Azure Resource Graph Query
This Python script is used to interact with the [Microsoft Azure Resource Graph](https://docs.microsoft.com/en-us/azure/governance/resource-graph/) service to query [Azure Resource Manager](https://docs.microsoft.com/en-us/azure/azure-resource-manager/resource-group-overview) for information on Azure resources.  It is written using Python 3.7.

## What problem does this solve?
Retrieving information about Azure resources typically involves creating separate resource queries to each [resource provider](https://docs.microsoft.com/en-us/azure/azure-resource-manager/resource-manager-supported-services) such as storage, network, and compute.  By using the Microsoft Azure Resource Graph queries for properties of resources can be performed without having to make them individually to each resource provider.  The service also supports complex queries using the [Resource Graph query language].(https://docs.microsoft.com/en-us/azure/governance/resource-graph/concepts/query-language)

## Requirements

* [Python 3.7](https://www.python.org/downloads/release/python-370/)
* [Microsoft Azure Python SDK](https://github.com/Azure/azure-sdk-for-python/tree/master/sdk)
* [Microsoft Azure Active Directory Authentication Library ADAL](https://docs.microsoft.com/en-us/azure/active-directory/develop/active-directory-authentication-libraries)
* [Pandas](https://pandas.pydata.org/)

### Setup
Clone the repository.

Prior to running the script you will need to create the Azure Active Directory security principal that the script will use.  The script uses the [OAuth Device Grant flow](https://oauth.net/2/device-flow/) to acquire a OAuth token to access the Resource Graph with the delegated rights of the user running the script.  The security principal needs to be granted the permission to access the Azure Service Management API as the user.  The user executing the script and authorizing the script needs to have the appropriate permissions to the Azure subscription.  See the following [Microsoft documentation](https://docs.microsoft.com/en-us/azure/active-directory/develop/quickstart-register-app) for instructions.

The script keeps a log file of its activities in a file named resource_inventory.log which is stored in the directory the script is executed from.  The log file can be used to track the scripts activities and for debugging any errors.

The results of the query are stored in JSON format in a file with a filename specified by the user at runtime.  This can be imported into a business intelligence tool such as PowerBI for further analysis.  The query must use the Resource Graph query language.

The Resource Graph is configured to page results if more than 100 records are returned.  The script is configured to handle these paged records and will write the records to the file after all of the returned records have been retrieved.

### Execution
The script requires a parameters file and a filename for the export file be provided as arguments at runtime.  A sample parameters file is included in the repository.

Example: python3 azure-inventory.py -parameterfile parameters.json -exportfile resources.json


