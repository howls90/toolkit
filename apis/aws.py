import boto3
import boto
import boto.s3.connection

def createS3(credentials, name):
    conn = boto.connect_s3(
        aws_access_key_id = credentials['Access key ID'],
        aws_secret_access_key = credentials['Secret access key'],
        calling_format = boto.s3.connection.OrdinaryCallingFormat(),
    )
    
    conn.create_bucket(name)

def createCloudfront(credentials,name):
    return False

def createLambda(credentials, name):
    return False

def createRoute53(credentials,name):
    return False