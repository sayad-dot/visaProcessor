#!/bin/bash

# Create required directories
mkdir -p /tmp/uploads
mkdir -p /tmp/generated
mkdir -p /tmp/logs

# Start the application
uvicorn main:app --host 0.0.0.0 --port $PORT
