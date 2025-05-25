#/usr/bin/env python3
"""
fft_tool.py

Reads a grayscale PNG image and computes its 2D FFT magnitude and phase spectra, 
and writes the results as a pair of PNG images.

Usage:
    fft_tool.py <input_image> <output_magnitude> <output_phase>

"""

import argparse
import numpy as np
import json
import os

from PIL import Image

def compute_fft(image_path: str, output_magnitude_path: str, output_phase_path: str):
    """
    Reads a grayscale PNG image and computes its 2D FFT magnitude and phase spectra,
    and writes the results as a pair of PNG images.

    Args:
        image_path: Path to the input grayscale PNG image.
        output_image_path: Path to the output PNG image containing the magnitude spectrum.
        
    """
    # Read the input image
    image = Image.open(image_path).convert('L')
    image_array = np.array(image)

    # Compute the 2D FFT
    fft_result = np.fft.fft2(image_array)

    # Shift the zero frequency component to the center of the spectrum
    fft_shift = np.fft.fftshift(fft_result)

    # Compute the magnitude spectrum log-scaled for better visibility
    magnitude_spectrum = np.log1p(np.abs(fft_shift))
    
    # Compute the phase spectrum
    phase_spectrum = np.angle(fft_shift)

    # Normalize magntiude spectrum
    magnitude_spectrum_normalized = ((magnitude_spectrum - magnitude_spectrum.min()) / (magnitude_spectrum.max() - magnitude_spectrum.min()) * 255).astype(np.uint8)

    # Normalize phase spectrum 
    phase_spectrum_normalized = ((phase_spectrum - phase_spectrum.min()) / (phase_spectrum.max() - phase_spectrum.min()) * 255).astype(np.uint8)

    # Save magnitude output image
    mag_image = Image.fromarray(magnitude_spectrum_normalized)
    mag_image.save(output_magnitude_path)

    # Save phase output image
    phase_image = Image.fromarray(phase_spectrum_normalized)
    phase_image.save(output_phase_path)

def main():
    parser = argparse.ArgumentParser(description='Compute and save FFT magnitude and phase spectra of a grayscale PNG image.')
    parser.add_argument('input_image', type=str, help='Path to the input grayscale PNG image.')
    parser.add_argument('output_magnitude', type=str, help='Path to the output PNG image containing the magnitude spectrum.')
    parser.add_argument('output_phase', type=str, help='Path to the output PNG image containing the phase spectrum.')

    args = parser.parse_args()

    print(f"FFT complete. Magnitude saved to {args.output_magnitude}")
    if args.output_phase:
        print(f"Phase saved to {args.output_phase}")

if __name__ == '__main__':
    main()