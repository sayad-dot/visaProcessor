#!/bin/bash
# Quick verification script for memory fixes

echo "🔍 Verifying Memory Fix Implementation..."
echo ""

# Check if pdf_service.py has the fixes
echo "1. Checking OCR DPI reduction..."
if grep -q "dpi=200" /media/sayad/Ubuntu-Data/visa/backend/app/services/pdf_service.py; then
    echo "   ✅ DPI reduced to 200 (was 400)"
else
    echo "   ❌ DPI still at 400 or not found"
fi

# Check page limit
echo "2. Checking page processing limit..."
if grep -q "MAX_PAGES = 10" /media/sayad/Ubuntu-Data/visa/backend/app/services/pdf_service.py; then
    echo "   ✅ Page limit set to 10"
else
    echo "   ❌ No page limit found"
fi

# Check file size limit
echo "3. Checking file size limit..."
if grep -q "MAX_FILE_SIZE_MB = 5" /media/sayad/Ubuntu-Data/visa/backend/app/services/pdf_service.py; then
    echo "   ✅ File size limit: 5MB"
else
    echo "   ❌ No file size limit found"
fi

# Check build script
echo "4. Checking build script..."
if [ -f "/media/sayad/Ubuntu-Data/visa/backend/build.sh" ]; then
    echo "   ✅ build.sh exists"
    if grep -q "tesseract-ocr" /media/sayad/Ubuntu-Data/visa/backend/build.sh; then
        echo "   ✅ Tesseract installation included"
    fi
else
    echo "   ❌ build.sh not found"
fi

# Check render config
echo "5. Checking Render configuration..."
if grep -q "bash build.sh" /media/sayad/Ubuntu-Data/visa/render-blueprint.yaml; then
    echo "   ✅ Build command updated"
else
    echo "   ❌ Build command not updated"
fi

if grep -q "plan: starter" /media/sayad/Ubuntu-Data/visa/render-blueprint.yaml; then
    echo "   ✅ Instance upgraded to Starter (2GB RAM)"
else
    echo "   ⚠️  Instance still on Free plan (manual upgrade needed)"
fi

echo ""
echo "📋 Next Steps:"
echo "   1. Commit all changes: git add . && git commit -m 'Fix memory issues'"
echo "   2. Push to GitHub: git push origin main"
echo "   3. Upgrade Render instance manually to Starter plan"
echo "   4. Monitor deployment logs for success messages"
echo ""
echo "📖 Full guide: docs/MEMORY_FIX_GUIDE.md"
