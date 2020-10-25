# from settings import keys
from settings import *
import boto3



# build aws s3 client
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)


# example usage: s3_operation('upload', 'iii-tutorial-v2', 'student99/<filename>')
def s3_operation(operator, bucket, key, filename=None):
    if operator == 'upload':
        # upload object with aws s3 client
        s3_client.upload_file(Bucket=bucket, Key=key, Filename=filename)
    elif operator == 'download':
        # download object with aws s3 client
        s3_client.download_file(Bucket=bucket, Key=key, Filename=filename)
    elif operator == 'delete':
        # delete object with aws s3 client
        s3_client.delete_object(Bucket=bucket, Key=key)
    else:
        print('operator missing or wrong typing')
