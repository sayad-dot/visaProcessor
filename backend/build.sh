#!/bin/bash
# Render Build Script - OCR dependencies removed (not needed)

echo "📦 Installing Python dependencies only..."

# Install Python dependencies
echo "🐍 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

echo "✅ Build complete! (OCR disabled - using questionnaire data only)"
