import boto3
import botocore
from botocore import client
from django.conf import settings

def save_file_s3(dir,file_id,file_obj):
    s3 = boto3.client(
            "s3",
            config=client.Config(signature_version="s3v4"),
            region_name=settings.AWS_S3_REGION_NAME,
        )
    s3.upload_fileobj(
                file_obj,
                settings.AWS_STORAGE_BUCKET_NAME,
                f'{dir}/{file_id}-{file_obj.name}'
    )

    signed_url = s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': f'{dir}/{file_id}-{file_obj.name}'},
                ExpiresIn=604800
            )
    return signed_url
