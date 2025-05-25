# Use a slim Python image
FROM python:3.10-slim

# Install dependencies
RUN pip install --no-cache-dir numpy pillow

# Copy in the FFT script
WORKDIR /app
COPY ../fft_tool/fft_tool.py .

# Make script executable
RUN chmod +x fft_tool.py

# Default command: allow overriding via `docker run`
ENTRYPOINT ["python", "fft_tool.py"]
