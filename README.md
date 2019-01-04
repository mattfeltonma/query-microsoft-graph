# azuregraphpython
This project contains three separate modules.  The graphapi.py module contains a function to obtain a token from Azure AD for use with the MS Graph API and a function to request data from the MS Graph API which handles OData paged results.  The awsintegration module contains a function to retrieve a secure parameter from AWS Systems Parameter Store and a function to write to an S3 bucket.  The main.py is an example of how to use the two modules together.

Log files for all module are written to a file named graphapilogs.

A sample parameters file is included.
