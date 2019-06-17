# Microsoft Azure Resource Graph Query
This Python script is used to interact with the [Microsot Graph](https://docs.microsoft.com/en-us/graph/overview) service and provides integration with Amazon Web Services services for credential and data storage. 

## What problem does this solve?
The script demonstrates how services from multiple public clouds can be strung together to formulate a solution to effieciently and securely pull data from an API.  This example uses Python to pull data from the Microsoft Graph API and stores it in Amazon S3 storage.  The credentials used to interact with the Microsoft Graph are stored securely in AWS KMS.

## Requirements

* [Python 3.6](https://www.python.org/downloads/release/python-360/)
* [AWS Boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html?id=docs_gateway)
* [Microsoft Azure Active Directory Authentication Library ADAL](https://docs.microsoft.com/en-us/azure/active-directory/develop/active-directory-authentication-libraries)

## Setup
Clone the repository.

Prior to running the script you will need to create the Azure Active Directory security principal that the script will use.  The script uses the [OAuth Client Credentials Grant Flow](https://oauth.net/2/grant-types/client-credentials/) to acquire a OAuth token to access the Microsoft Graph.  The security principal needs to be granted the appropriate permissions to access the resources you wish to pull information for.

The script keeps a log file of its activities in a file named msapiquery.log which is stored in the directory the script is executed from.  The log file can be used to track the scripts activities and for debugging any errors.

The results of the query are written to text file which is written to an S3 bucket.

## Execution
A sample parameters file is included.
