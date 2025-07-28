import os
import boto3
from botocore.client import Config

B2_REGION = os.getenv("B2_REGION")
B2_ENDPOINT = f"https://s3.{B2_REGION}.backblazeb2.com"

b2_client = boto3.client(
    's3',
    endpoint_url=B2_ENDPOINT,
    aws_access_key_id=os.getenv("B2_KEY_ID"),
    aws_secret_access_key=os.getenv("B2_APP_KEY"),
    config=Config(signature_version='s3v4'),
    region_name=B2_REGION
)
