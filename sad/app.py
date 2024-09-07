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
dir = '/opt/python'
s3 = boto3.client('s3')


def content_type(file_name):
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
        '.txt': 'text/plain',
        '.svg': 'image/svg+xml',
        '.ttf': 'font/ttf',
        '.woff': 'font/woff',
        '.woff2': 'font/woff2',
        '.pdf': 'application/pdf',
        '.wav': 'audio/wav',
        '.mp4': 'video/mp4',
        '.webm': 'video/webm',
        '.ogg': 'application/ogg',
        '.gif': 'image/gif',
        '.bmp': 'image/bmp',
        '.tiff': 'image/tiff',
        '.jpeg': 'image/jpeg',
        '.png': 'image/png',
    }
    _, ext = os.path.splitext(file_name)
    return mime_types.get(ext, 'application/octet-stream')


def handler(event, context):
    helper(event, context)


def sha256(s):
    return hashlib.sha256(s.encode()).hexdigest()


def upload(event):
    uploaded = []
    props = event['ResourceProperties']
    layer_arn = props['StaticAssetsLayerArn']
    logger.info(f'Layer ARN is {layer_arn}')
    layer_arn_sha256 = sha256(layer_arn)
    bucket_name = props['BucketName']
    cache_control = props.get('CacheControl', 'max-age=31536000, immutable')
    logger.info(f'CacheControl is {cache_control}')

    for local_path, target_path in files():
        logger.info(f'Uploading to {layer_arn_sha256}/{target_path}')
        s3.upload_file(
            local_path,
            bucket_name,
            f'{layer_arn_sha256}/{target_path}',
            ExtraArgs={
                'ContentType': content_type(local_path),
                'CacheControl': cache_control
            }
        )
        uploaded.append(local_path)

    return layer_arn_sha256


def files():
    for root, _, files in os.walk(dir):
        for file in files:
            local_path = os.path.join(root, file)
            target_path = os.path.relpath(local_path, dir)
            yield local_path, target_path


@helper.create
def create(event, context):
    logger.info('Handling create')
    return upload(event)


@helper.update
def update(event, context):
    logger.info('Handling update')
    delete_files(event)
    return upload(event)


def delete_files(event):
    props = event['ResourceProperties']
    layer_arn = props['StaticAssetsLayerArn']
    logger.info(f'Layer ARN is {layer_arn}')
    layer_arn_sha256 = sha256(layer_arn)
    bucket_name = props['BucketName']

    for _, target_path in files():
        key = f'{layer_arn_sha256}/{target_path}'
        logger.info(f'Deleting {key}')
        s3.delete_object(Bucket=bucket_name, Key=key)


@helper.delete
def delete(event, context):
    logger.info('Handling delete')
    delete_files(event)
