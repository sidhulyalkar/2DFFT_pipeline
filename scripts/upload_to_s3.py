#!/usr/bin/env python
"""
upload_to_s3.py

Uploads a local PNG image to a specified S3 bucket and key (path).
"""

import argparse
import boto3
import os
from botocore.exceptions import NoCredentialsError, ClientError


def upload_png_to_s3(file_path, bucket_name, key):
    # Validate the file
    if not os.path.isfile(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    if not file_path.lower().endswith(".png"):
        raise ValueError("Only .png files are supported.")

    # Initialize S3 client
    s3 = boto3.client("s3")

    try:
        s3.upload_file(file_path, bucket_name, key)
        print(f"✅ Uploaded '{file_path}' to 's3://{bucket_name}/{key}'")
    except NoCredentialsError:
        print("❌ AWS credentials not found. Did you run `aws configure`?")
    except ClientError as e:
        print(f"❌ Failed to upload: {e}")


def main():
    parser = argparse.ArgumentParser(description="Upload a PNG file to S3")
    parser.add_argument("file_path", help="Path to the local PNG file")
    parser.add_argument("bucket_name", help="Target S3 bucket name")
    parser.add_argument("s3_key", help="S3 key (e.g., 'input/my_image.png')")
    args = parser.parse_args()

    upload_png_to_s3(args.file_path, args.bucket_name, args.s3_key)


if __name__ == "__main__":
    main()
