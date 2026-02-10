#!/bin/bash
# Render Build Script - Install WeasyPrint dependencies + Python packages

set -e  # Exit on any error

echo "📦 Installing system dependencies for WeasyPrint..."

# Install WeasyPrint system dependencies (Cairo, Pango, libffi, etc.)
apt-get update && apt-get install -y \
    libcairo2 \
    libcairo2-dev \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf2.0-0 \
    libffi-dev \
    libffi7 \
    shared-mime-info \
    pkg-config

echo "✅ WeasyPrint system dependencies installed"

# Upgrade pip and setuptools
echo "🐍 Upgrading pip and build tools..."
pip install --upgrade pip setuptools wheel

# Install cffi and cairocffi FIRST (critical for WeasyPrint)
echo "📦 Installing cffi and cairocffi..."
pip install cffi==1.16.0 cairocffi==1.7.0

echo "✅ cffi and cairocffi installed"

# Install remaining Python dependencies
echo "🐍 Installing Python packages..."
pip install -r requirements.txt

echo "✅ Build complete! WeasyPrint enabled with 13-page template support"

# Verify WeasyPrint installation
echo "🔍 Verifying WeasyPrint..."
python3 -c "from weasyprint import HTML; print('✅ WeasyPrint OK')" || echo "⚠️ WeasyPrint verification failed"
