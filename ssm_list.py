# The script uses boto3 to create an AWS session and client to access the parameters of the Simple Systems 
# Manager (SSM) service in the 'us-east-1' region and with the 'shared-services' profile.

# Then, the script creates two global variables, envs and secrets, which are instances of the Dict class
# from pysos. It uses the client to get all existing parameters in SSM through the describe_parameters function. 
# For each obtained parameter, it uses the get_parameter function to get the value and type of the parameter. 
# If the type is 'String', it is added to the envs dictionary and if it is 'SecureString' it is added to the 
# secrets dictionary. If the type is not supported, the script exits.
import boto3
import sys
import base64


session = boto3.Session(region_name='us-east-1')
client = session.client('ssm')

def decrypt(session, arn, secret):
    client = session.client('kms')
    plaintext = client.decrypt(
        CiphertextBlob=bytes(base64.b64decode(secret)),
         
    )
    return plaintext["Plaintext"]


p = client.get_paginator('describe_parameters')
paginator = p.paginate().build_full_result()
for page in paginator['Parameters']:
    response = client.get_parameter(Name=page['Name'], WithDecryption=True)
    value = response['Parameter']['Value']
    type = response['Parameter']['Type']
    if type == 'String':
        print(page['Name']+ ",\"" + value+"\"")
    elif type == 'SecureString':        
 
        print(page['Name']+ ",\"" + value+"\"")
    else:
        exit(0)
