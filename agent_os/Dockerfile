# Dockerfile for Agent OS Cloud Deployment
FROM python:3.12-slim

# Install system dependencies (curl for healthchecks, git for vault sync, build-essential for C-extensions)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all application files
COPY . .

# Default server execution port (Cloud Run injects PORT environment variable)
ENV PORT=8080
EXPOSE 8080

# Run the python backend server with unbuffered stdout to capture real-time logging
CMD ["python", "-u", "server.py"]
