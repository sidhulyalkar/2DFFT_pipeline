import os
import boto3
import json
from fft_tool import compute_fft
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

s3 = boto3.client("s3")


def lambda_handler(event, context):
    logger.info(f"Received event: {event}")
    # Parse bucket & key
    record = event["Records"][0]["s3"]
    bucket = record["bucket"]["name"]
    key = record["object"]["key"]  # e.g. "input/forest.png"
    base = os.path.basename(key)  # "forest.png"
    local_in = f"/tmp/{base}"
    local_mag = f"/tmp/{os.path.splitext(base)[0]}_magnitude.png"
    local_phy = f"/tmp/{os.path.splitext(base)[0]}_phase.png"
    local_meta = f"/tmp/{base}_metadata.json"

    # Download
    s3.download_file(bucket, key, local_in)

    # Compute FFT
    meta = compute_fft(local_in, local_mag, local_phy)

    # Upload
    for fname, suffix in [(local_mag, "_magnitude.png"), (local_phy, "_phase.png")]:
        key = f"output/{base}{suffix}"
        s3.upload_file(
            fname,
            bucket,
            key,
            ExtraArgs={
                "Metadata": {  # S3 object metadata
                    "mag_min": str(meta["mag_min"]),
                    "mag_max": str(meta["mag_max"]),
                }
            },
        )

    # 4. Upload results
    out_prefix = "output/"
    s3.upload_file(local_mag, bucket, out_prefix + os.path.basename(local_mag))
    s3.upload_file(local_phy, bucket, out_prefix + os.path.basename(local_phy))

    return {
        "statusCode": 200,
        "body": f"Processed {key}, wrote {local_mag}, {local_phy}",
    }
