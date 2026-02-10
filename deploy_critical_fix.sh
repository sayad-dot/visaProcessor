#!/bin/bash
# Critical WeasyPrint + Empty ZIP Fix Deployment

echo "🚨 CRITICAL FIX: WeasyPrint Dependencies + Empty ZIP Logging"
echo "============================================================"
echo ""

# Stage all changes
echo "📦 Staging changes..."
git add backend/build.sh
git add backend/requirements.txt
git add backend/app/services/template_renderer.py
git add backend/app/api/endpoints/generate.py
git add CRITICAL_WEASYPRINT_FIX.md

# Commit
echo "💾 Committing fixes..."
git commit -m "CRITICAL FIX: WeasyPrint cffi cairocffi + ZIP logging

Fixes:
1. WeasyPrint PDF.__init__() error - install cffi/cairocffi first
2. Empty ZIP downloads - enhanced logging to debug
3. Missing system dependencies - libcairo2-dev, libffi7, pkg-config

Changes:
- backend/build.sh: Install cffi+cairocffi before weasyprint
- backend/requirements.txt: Explicit cffi==1.16.0 cairocffi==1.7.0
- template_renderer.py: Enhanced error handling with tracebacks
- generate.py: ZIP logging - files added, missing files, ZIP size

Build time: Now 8-10 min (compiling cffi from source)
"

# Push to GitHub (triggers Render deployment)
echo "🚀 Pushing to GitHub..."
git push origin main

echo ""
echo "✅ DEPLOYMENT INITIATED!"
echo ""
echo "⏱️  Render Build Time: ~8-10 minutes (compiling cffi)"
echo ""
echo "📋 What to watch for in Render logs:"
echo ""
echo "   SUCCESS INDICATORS:"
echo "   ✅ WeasyPrint system dependencies installed"
echo "   ✅ cffi and cairocffi installed"
echo "   ✅ Build complete! WeasyPrint enabled"
echo "   ✅ WeasyPrint OK"
echo ""
echo "   After deployment, application logs:"
echo "   ✅ Visiting card generated with WeasyPrint template"
echo "   ✅ Asset valuation generated with WeasyPrint 13-page template"
echo "   📦 ZIP created: XX files, XXXXX bytes"
echo ""
echo "   FAILURE INDICATORS (should NOT see):"
echo "   ❌ WeasyPrint failed: PDF.__init__() error"
echo "   ❌ ZIP is empty! No files were added"
echo "   ⚠️  Missing generated file:"
echo ""
echo "🧪 Test after deployment:"
echo "   1. Create new application"
echo "   2. Upload documents"
echo "   3. Generate documents"
echo "   4. Download ZIP - should be 1-2 MB"
echo "   5. Verify Asset Valuation = 13 pages"
echo ""
echo "🔗 Monitor deployment:"
echo "   https://dashboard.render.com/web/visaProcessor"
echo ""
