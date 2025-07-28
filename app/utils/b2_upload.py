import os
import boto3
from botocore.client import Config
from botocore.exceptions import ClientError
import logging
import uuid

B2_REGION = os.getenv("B2_REGION")
B2_BUCKET = os.getenv("B2_BUCKET_NAME")
B2_ENDPOINT = f"https://s3.{B2_REGION}.backblazeb2.com"

b2_client = boto3.client(
    's3',
    endpoint_url=B2_ENDPOINT,
    aws_access_key_id=os.getenv("B2_KEY_ID"),
    aws_secret_access_key=os.getenv("B2_APP_KEY"),
    config=Config(signature_version='s3v4'),
    region_name=B2_REGION
)


def upload_file_to_b2(file, filename, content_type, folder="posts"):
    key = f"{folder}/{uuid.uuid4()}-{filename}"
    try:
        b2_client.put_object(
            Bucket=B2_BUCKET,
            Key=key,
            Body=file,
            ContentType=content_type
        )
        print("✅ Upload successful:", key)
    except ClientError as e:
        logging.error(f"❌ Upload failed: {e}")
        raise

    # Генерация signed URL для приватного доступа
    try:
        signed_url = b2_client.generate_presigned_url(
            ClientMethod='get_object',
            Params={'Bucket': B2_BUCKET, 'Key': key},
            ExpiresIn=3600  # 1 час
        )
        return signed_url
    except ClientError as e:
        logging.error("❌ Couldn't generate signed URL:", e)
        return None
