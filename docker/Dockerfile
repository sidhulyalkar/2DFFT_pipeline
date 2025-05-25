# syntax = docker/dockerfile:1.3
# Multi-Staged Docker Build

# Stage 1: Builder
# Use slim base image for build step 
FROM --platform=linux/amd64 python:3.10-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy in requirements 
COPY requirements.txt .

# Install Python deps into a dedicated dir
RUN pip install \
        --no-cache-dir \
        --upgrade \
        --target=/build/deps \
        -r requirements.txt

# Stage 2: Runtime
FROM --platform=linux/amd64 public.ecr.aws/lambda/python:3.10

# Copy dependencies into Lambda's /opt/python path
COPY --from=builder /build/deps /opt/python

# Copy fft_tool and handler into /var/task (Lambda's working dir)
COPY fft_tool/fft_tool.py   /var/task/fft_tool.py
COPY scripts/handler.py     /var/task/handler.py

# Ensure unbuffered output
ENV PYTHONUNBUFFERED=1

# Labels (still useful)
LABEL maintainer="Sidharth Hulyalkar <sidsoccer21@gmail.com>" \
      description="2D-FFT Lambda for Precision pipeline"

# Tell Lambda which function to invoke
CMD ["handler.lambda_handler"]


