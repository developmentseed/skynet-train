import os
import boto3
from datetime import datetime


def get_client(bucket):
    s3 = boto3.resource('s3')
    region_name = s3.meta.client.get_bucket_location(Bucket=bucket)['LocationConstraint']
    if region_name is None:
        region_name = 'us-east-1'
    return boto3.client('s3', region_name=region_name)


# based on http://stackoverflow.com/a/33350380
def download_dir(prefix, local='/tmp', bucket='your_bucket', client=None, base=None):
    print('downloading %s from %s to %s' % (prefix, bucket, local))
    if client is None:
        client = get_client(bucket)
    if base is None:
        base = prefix
    paginator = client.get_paginator('list_objects')
    for result in paginator.paginate(Bucket=bucket, Delimiter='/', Prefix=prefix):
        if result.get('CommonPrefixes') is not None:
            for subdir in result.get('CommonPrefixes'):
                download_dir(subdir.get('Prefix'), local, bucket=bucket, client=client, base=base)
        if result.get('Contents') is not None:
            for file in result.get('Contents'):
                relative_path = os.path.relpath(file.get('Key'), base)
                download_path = os.path.join(local, relative_path)
                if not os.path.exists(os.path.dirname(download_path)):
                    os.makedirs(os.path.dirname(download_path))
                print('downloading %s to %s' % (file.get('Key'), download_path))
                client.download_file(bucket, file.get('Key'), download_path)


def upload_dir(local, prefix, bucket):
    client = get_client(bucket)
    for root, dirs, files in os.walk(local):
        for filename in files:
            full_path = os.path.join(root, filename)
            mtime = datetime.fromtimestamp(os.path.getmtime(full_path))
            relative_path = os.path.relpath(full_path, local)
            key = os.path.join(prefix, relative_path)
            try:
                client.head_object(Bucket=bucket, Key=key, IfUnmodifiedSince=mtime)
            except:
                print('Uploading %s' % key)
                client.upload_file(full_path, bucket, key)
