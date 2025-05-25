#!/usr/bin/env python3
"""
reconstruct_from_fft.py

Reconstructs original image from its stored FFT magnitude and phase spectra.

Usage:
    reconstruct_from_fft.py <magnitude_image> <phase_image> <output_image>
"""

import os
import json
import argparse
import numpy as np

from PIL import Image

def load_magnitude(path: str) -> np.ndarray:
    """
    Load a saved log-magnitude PNG and invert log1p normalization.
    """
    img = Image.open(path).convert("L")
    arr = np.array(img).astype(np.float32) / 255.0  # [0,1]

    # Load min and max magnitude values stored during FFT processing
    meta = json.load(open("data/fft_metadata.json"))
    magnitude = np.expm1(arr * (meta["mag_max"] - meta["mag_min"]) + meta["mag_min"])
    return magnitude

def load_phase(path: str) -> np.ndarray:
    """
    Load a saved phase PNG and map back to [-π, +π].
    """
    img = Image.open(path).convert("L")
    arr = np.array(img).astype(np.float32) / 255.0  # [0,1]
    return arr * 2 * np.pi - np.pi

def reconstruct_image(mag_path: str, phase_path: str, output_path: str):
    # Load magnitude and phase arrays
    magnitude = load_magnitude(mag_path)
    phase     = load_phase(phase_path)

    # Reconstruct complex spectrum
    complex_spectrum = magnitude * np.exp(1j * phase)

    # Inverse FFT shift + inverse FFT
    shifted_back = np.fft.ifftshift(complex_spectrum)
    recon        = np.fft.ifft2(shifted_back)

    # Take real part, normalize to [0,255]
    real_img = np.real(recon)
    real_img -= real_img.min()
    real_img = (255 * real_img / np.ptp(real_img)).astype(np.uint8)

    # 5. Ensure output directory exists
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    Image.fromarray(real_img).save(output_path)
    print(f"Reconstructed image saved to {output_path}")

def main():
    parser = argparse.ArgumentParser(
        description="Reconstruct image from FFT magnitude and phase")
    parser.add_argument("magnitude_image",
                        help="Path to the magnitude spectrum PNG")
    parser.add_argument("phase_image",
                        help="Path to the phase spectrum PNG")
    parser.add_argument("output_image",
                        help="Path to save the reconstructed image")
    args = parser.parse_args()

    reconstruct_image(args.magnitude_image,
                      args.phase_image,
                      args.output_image)

if __name__ == "__main__":
    main()
