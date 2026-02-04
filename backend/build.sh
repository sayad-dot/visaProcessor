#!/bin/bash
# Render Build Script - Install system dependencies for OCR
# This ensures tesseract-ocr and poppler-utils are installed

echo "📦 Installing system dependencies..."

# Update package list
apt-get update -qq

# Install Tesseract OCR (for text extraction from images)
echo "🔍 Installing Tesseract OCR..."
apt-get install -y tesseract-ocr

# Install Poppler (for pdf2image library)
echo "📄 Installing Poppler utilities..."
apt-get install -y poppler-utils

echo "✅ System dependencies installed successfully"

# Install Python dependencies
echo "🐍 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Build complete!"
