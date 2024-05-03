import os
import logging
import hashlib

import crhelper
import boto3

logger = logging.getLogger(__name__)
helper = crhelper.CfnResource(
    json_logging=False,
    log_level='INFO',
    boto_level='CRITICAL',
)
s3 = boto3.client('s3')
dir = '/opt/python'
cache_control = os.getenv('CACHE_CONTROL', 'max-age=31536000, immutable')

def _content_type(file_name):
    """
    Returns the content type for the given file name.

    :param file_name: The file name.
    :return: The content type.
    """
    mime_types = {
        '.ico': 'image/x-icon',
        '.jpg': 'image/jpeg',
        '.html': 'text/html',
        '.css': 'text/css',
        '.js': 'application/javascript',
        '.xml': 'application/xml',
        '.png': 'image/png',
    }
    _, ext = os.path.splitext(file_name)
    return mime_types.get(ext, 'binary/octet-stream')


def handler(event, context):
    helper(event, context)


def _upload(event):
    uploaded = []
    dirs = os.listdir(dir)
    logger.info(dirs)
    bucket_name = event['ResourceProperties']['BucketName']
    for local_path, target_path in _files():
        logger.info(f'Uploading to {target_path}')
        s3.upload_file(
            local_path,
            bucket_name,
            target_path,
            ExtraArgs={
                'ContentType': _content_type(local_path),
                'CacheControl': cache_control
            }
        )
        uploaded.append(local_path)

    concatenated_names = ''.join(uploaded)
    hashed_names = hashlib.md5(concatenated_names.encode()).hexdigest()
    physical_resource_id = f"{bucket_name}/{hashed_names}"
    return physical_resource_id


def _files():
    for root, _, files in os.walk(dir):
        for file in files:
            local_path = os.path.join(root, file)
            target_path = os.path.relpath(local_path, dir)
            yield local_path, target_path


@helper.create
def create(event, context):
    logger.info('Handling create')
    return _upload(event)


@helper.update
def update(event, context):
    logger.info('Handling update')
    return _upload(event)


@helper.delete
def delete(event, context):
    logger.info('Handling delete')
    bucket_name = event['ResourceProperties']['BucketName']
    for local_path, target_path in _files():
        logger.info(f'Deleting {target_path}')
        s3.delete_object(Bucket=bucket_name, Key=target_path)
