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

    # Normalize the magnitude spectrum to the range 0-255
    magnitude_spectrum_normalized = normalize_spectrum(magnitude_spectrum)

    # Normalize the phase spectrum to the range 0-255
    phase_spectrum_normalized = normalize_spectrum(phase_spectrum)

    # Create the output magnitude image
    create_and_save_image(magnitude_spectrum_normalized, output_magnitude_path)

    # Create the output phase image
    create_and_save_image(phase_spectrum_normalized, output_phase_path)

def normalize_spectrum(spectrum: np.ndarray) -> np.ndarray:
    """
    Normalizes a spectrum to the range 0-255.`
    """
    return ((spectrum - spectrum.min()) / (spectrum.max() - spectrum.min()) * 255).astype(np.uint8)

def create_and_save_image(image: np.ndarray, path: str):
    """
    Creates an image from a numpy array and saves it to a file.
    """
    image = Image.fromarray(image)
    image.save(path)

def main():
    parser = argparse.ArgumentParser(description='Compute and save FFT magnitude and phase spectra of a grayscale PNG image.')
    parser.add_argument('input_image', type=str, help='Path to the input grayscale PNG image.')
    parser.add_argument('output_magnitude', type=str, help='Path to the output PNG image containing the magnitude spectrum.')
    parser.add_argument('output_phase', type=str, help='Path to the output PNG image containing the phase spectrum.')
    parser.add_argument("--metadata", dest="metadata_path", help="If provided, writable path to dump log-magnitude min/max JSON",)
    args = parser.parse_args()
    
    compute_fft(args.input_png, args.output_magnitude, args.output_phase)

    print(f"FFT complete. Magnitude saved to {args.output_magnitude}")
    if args.output_phase:
        print(f"Phase saved to {args.output_phase}")

if __name__ == '__main__':
    main()
    
    
    

    
    