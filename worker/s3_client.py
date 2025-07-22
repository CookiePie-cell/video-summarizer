import os

import boto3
from botocore.client import Config

s3 = boto3.client(
    's3',
    endpoint_url=os.environ.get('MINIO_ENDPOINT'),
    aws_access_key_id=os.environ.get('MINIO_ACCESS_KEY'),
    aws_secret_access_key=os.environ.get('MINIO_SECRET_KEY'),
    config=Config(signature_version='s3v4'),
    region_name=os.environ.get('MINIO_REGION')
)

