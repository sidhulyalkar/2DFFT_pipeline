#!/usr/bin/env python3
"""
reconstruct_from_fft.py

Reconstructs the original image from its stored FFT magnitude and phase spectra in S3,
using object metadata for exact log1p min/max recovery.

Usage:
    reconstruct_from_fft.py \
      --bucket BUCKET_NAME \
      --key-magnitude PATH/TO/magnitude.png \
      --key-phase PATH/TO/phase.png \
      --output LOCAL_OUTPUT_IMAGE
"""
import argparse
import os
import tempfile

import numpy as np
from PIL import Image
import boto3


def download_and_get_metadata(s3, bucket: str, key: str, local_path: str) -> dict:
    """
    Download object from S3 to local_path and return its Metadata dict (mag_min, mag_max).
    """
    head = s3.head_object(Bucket=bucket, Key=key)
    metadata = head.get("Metadata", {})
    s3.download_file(bucket, key, local_path)
    return metadata


def load_image(path: str) -> np.ndarray:
    """
    Load a grayscale PNG image into float32 numpy array.
    """
    img = Image.open(path).convert("L")
    return np.array(img).astype(np.float32)


def reconstruct_image(bucket: str, key_mag: str, key_phase: str, output_path: str):
    s3 = boto3.client("s3")

    # Create temp files for downloads
    tmp_mag = tempfile.NamedTemporaryFile(suffix=".png", delete=False).name
    tmp_phase = tempfile.NamedTemporaryFile(suffix=".png", delete=False).name

    # Download and get metadata for magnitude
    metadata = download_and_get_metadata(s3, bucket, key_mag, tmp_mag)
    mag_min = float(metadata.get("mag_min", 0.0))
    mag_max = float(metadata.get("mag_max", 0.0))

    # Download phase (metadata not needed)
    download_and_get_metadata(s3, bucket, key_phase, tmp_phase)

    # Load arrays
    mag_arr = load_image(tmp_mag)
    phase_arr = load_image(tmp_phase)

    # Invert normalization: log1p_mag = norm * (mag_max - mag_min) + mag_min
    norm_mag = mag_arr / 255.0
    log1p_mag = norm_mag * (mag_max - mag_min) + mag_min
    magnitude = np.expm1(log1p_mag)

    # Convert phase [0,255] → [-π, +π]
    norm_phase = phase_arr / 255.0
    phase = norm_phase * 2 * np.pi - np.pi

    # Reconstruct complex spectrum and inverse FFT
    complex_spec = magnitude * np.exp(1j * phase)
    recon = np.fft.ifft2(np.fft.ifftshift(complex_spec))

    # Real part, normalize to [0,255]
    real_img = np.real(recon)
    real_img -= real_img.min()
    real_img = (255 * real_img / np.ptp(real_img)).astype(np.uint8)

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    Image.fromarray(real_img).save(output_path)
    print(f"Reconstructed image saved to {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Reconstruct original image from FFT outputs stored in S3."
    )
    parser.add_argument("--bucket", required=True, help="Name of the S3 bucket")
    parser.add_argument(
        "--key-magnitude", required=True, help="S3 key for the magnitude PNG"
    )
    parser.add_argument("--key-phase", required=True, help="S3 key for the phase PNG")
    parser.add_argument(
        "--output", required=True, help="Local path to save the reconstructed image"
    )
    args = parser.parse_args()

    reconstruct_image(args.bucket, args.key_magnitude, args.key_phase, args.output)


if __name__ == "__main__":
    main()
