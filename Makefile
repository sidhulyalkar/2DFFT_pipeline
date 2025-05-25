# Makefile for 2Dfft-pipeline

VENV_DIR := .venv
PYTHON := $(VENV_DIR)/bin/python
PIP := $(VENV_DIR)/bin/pip

# File paths
INPUT_IMAGE := input_images/forest.png
IMAGE_NAME := forest
MAG_OUTPUT := output_images/${IMAGE_NAME}_output_magnitude.png
PHASE_OUTPUT := output_images/${IMAGE_NAME}_output_phase.png
RECONSTRUCTED := output_images/${IMAGE_NAME}_output_reconstructed.png


## ⚙️ Setup virtual environment
setup:
	python3 -m venv $(VENV_DIR)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt -r dev-requirements.txt

## Check that all required packages are installed
check:
	@.venv/bin/python -c "import numpy, PIL, boto3; print('✅ All required packages are installed.')"

## 🧪 Run FFT on input PNG
fft:
	$(PYTHON) fft_tool/fft_tool.py $(INPUT_IMAGE) $(MAG_OUTPUT) $(PHASE_OUTPUT)

## 🔁 Reconstruct image from magnitude and phase
reconstruct:
	$(PYTHON) fft_tool/reconstruct_from_fft.py $(MAG_OUTPUT) $(PHASE_OUTPUT) $(RECONSTRUCTED)

## 📤 Upload to S3
upload:
	$(PYTHON) scripts/upload_to_s3.py $(INPUT_IMAGE) $(BUCKET) input/$(INPUT_IMAGE)

## 🧹 Clean outputs
clean:
	rm -f output_*.png
	rm -f $(RECONSTRUCTED)

## 📐 Reformat code
format:
	.venv/bin/black .

## 🚨 Lint for errors/style
lint:
	.venv/bin/flake8 fft_tool/ scripts/ tests/

## 🔍 Static type‐check
typecheck:
	.venv/bin/mypy fft_tool/ scripts/ tests/

## 🧪 Run tests
test:
	.venv/bin/pytest --maxfail=1 --disable-warnings -q

