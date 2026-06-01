# Use slim Python 3.11 base image
FROM python:3.11-slim

# Ensure Python outputs logs straight to terminal
ENV PYTHONUNBUFFERED=1 

WORKDIR /app

# System deps (keep minimal; add build deps if any package needs compilation)
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies first for better Docker layer caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /app

# FastAPI/Uvicorn runs on this port (matches render.yaml)
EXPOSE 10000

# Default command
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "10000"]

