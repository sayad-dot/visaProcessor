#!/bin/bash
set -e

# Create required directories
mkdir -p /tmp/uploads
mkdir -p /tmp/generated  
mkdir -p /tmp/logs

# Print diagnostic info
echo "Starting Visa Backend Service..."
echo "Working directory: $(pwd)"
echo "Python version: $(python --version)"

# Start the application
exec uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}
