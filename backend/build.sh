#!/bin/bash
# Render Build Script - Install WeasyPrint dependencies + Python packages

echo "📦 Installing system dependencies for WeasyPrint..."

# Install WeasyPrint system dependencies (Cairo, Pango, etc.)
apt-get update && apt-get install -y \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    shared-mime-info

echo "✅ WeasyPrint system dependencies installed"

# Install Python dependencies
echo "🐍 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Build complete! WeasyPrint enabled with 13-page template support"
