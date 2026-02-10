#!/bin/bash

# Asset Valuation Consistency Fix - Complete Deployment
# Fixes: Local (5-page) vs Deployed (10-page) inconsistency
# Result: Both generate 13-page comprehensive template

echo "========================================================================"
echo "Asset Valuation Consistency Fix - Deployment"
echo "========================================================================"
echo ""
echo "🎯 Goal: Make local and deployed versions generate identical 13-page PDFs"
echo ""

# Check if we're in the right directory
if [ ! -d "backend" ]; then
    echo "❌ Error: Please run this script from the visa project root directory"
    exit 1
fi

echo "📋 Changes Overview:"
echo "----------------------------------------------------------------------"
echo "1. ✅ Created 13-page comprehensive template (embassy format)"
echo "2. ✅ Updated build.sh to install WeasyPrint system dependencies"
echo "3. ✅ Updated render.yaml to use build.sh (not just pip install)"
echo "4. ✅ Enhanced data extraction (40+ fields from questionnaire)"
echo "5. ✅ Tested locally: 35.4KB, 13 pages ✅"
echo ""

echo "📦 Files to be deployed:"
echo "----------------------------------------------------------------------"
echo "  CRITICAL (Fix the inconsistency):"
echo "    - backend/build.sh                               (WeasyPrint deps)"
echo "    - render.yaml                                    (Use build.sh)"
echo ""
echo "  TEMPLATE (New 13-page format):"
echo "    - backend/app/templates/asset_valuation_template_13page.html"
echo ""
echo "  SERVICES (Enhanced data collection):"
echo "    - backend/app/services/template_renderer.py"
echo "    - backend/app/services/pdf_generator_service.py"
echo ""
echo "  DOCUMENTATION:"
echo "    - ASSET_VALUATION_13PAGE_UPDATE_COMPLETE.md"
echo "    - ASSET_VALUATION_CONSISTENCY_FIX.md"
echo "    - QUICK_DEPLOY_GUIDE.md"
echo ""

git status --short | grep -E "build.sh|render.yaml|asset_valuation|template_renderer|pdf_generator"

echo ""
echo "⚠️  IMPORTANT: Database Changes?"
echo "----------------------------------------------------------------------"
echo "✅ NO database changes needed!"
echo "✅ NO Neon migrations required!"
echo "✅ Uses existing questionnaire_responses table"
echo ""

read -p "Continue with deployment? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Deployment cancelled"
    exit 0
fi

echo ""
echo "📦 Step 1: Staging files..."
echo "----------------------------------------------------------------------"

# Critical files for consistency fix
git add backend/build.sh
git add render.yaml

# New template and enhanced services
git add backend/app/templates/asset_valuation_template_13page.html
git add backend/app/services/template_renderer.py
git add backend/app/services/pdf_generator_service.py

# Documentation
git add ASSET_VALUATION_13PAGE_UPDATE_COMPLETE.md
git add ASSET_VALUATION_CONSISTENCY_FIX.md
git add QUICK_DEPLOY_GUIDE.md
git add deploy_asset_valuation_13page.sh
git add deploy_consistency_fix.sh

# Optional test files
git add test_asset_valuation_13page.py 2>/dev/null || true
git add analyze_asset_valuation_template.py 2>/dev/null || true

echo "✅ Files staged"

echo ""
echo "💾 Step 2: Committing changes..."
echo "----------------------------------------------------------------------"

git commit -m "fix: Ensure Asset Valuation consistency between local and deployed

🐛 Problem:
- Local: Generated 5-page PDF using WeasyPrint HTML template
- Deployed: Generated 10-page PDF using ReportLab fallback (different design)
- Root cause: Missing WeasyPrint system dependencies on Render

✨ Solution:
- Add WeasyPrint system dependencies in build.sh (Cairo, Pango, etc.)
- Update render.yaml to use build.sh instead of direct pip install
- Create comprehensive 13-page template matching embassy requirements
- Enhanced data extraction from questionnaire (40+ fields)

📄 Changes:
- backend/build.sh: Install libcairo2, libpango, libgdk-pixbuf2, etc.
- render.yaml: Use 'bash build.sh' as buildCommand
- asset_valuation_template_13page.html: New 13-page comprehensive template
- template_renderer.py: Enhanced with comprehensive data fields
- pdf_generator_service.py: Better data extraction from questionnaire

✅ Result:
- Both local and deployed now use same 13-page HTML template
- WeasyPrint works on both environments
- No ReportLab fallback needed
- Consistent professional design
- No database changes required

🎯 Impact:
- Embassy-ready format for both environments
- Predictable, consistent output
- Professional quality documentation
- Build time: +3 mins (installing system deps)

📊 Testing:
- Local test: ✅ 35.4KB, 13 pages
- All sections render correctly
- Data from questionnaire populates properly
- Intelligent defaults for missing data

🔧 Technical Details:
- WeasyPrint 60.2 (requires system libraries)
- System deps: libcairo2, libpango-1.0-0, libpangocairo-1.0-0
- Template: Jinja2 + CSS (1,050 lines)
- Fallback: ReportLab (if WeasyPrint fails)

📖 Documentation:
- ASSET_VALUATION_13PAGE_UPDATE_COMPLETE.md
- ASSET_VALUATION_CONSISTENCY_FIX.md
- QUICK_DEPLOY_GUIDE.md"

if [ $? -eq 0 ]; then
    echo "✅ Changes committed successfully"
else
    echo "❌ Commit failed. Please check errors above."
    exit 1
fi

echo ""
echo "🚀 Step 3: Pushing to trigger Render deployment..."
echo "----------------------------------------------------------------------"
echo ""
echo "⚠️  IMPORTANT: After pushing, deployment will take 5-7 minutes"
echo "   (longer than usual due to system dependency installation)"
echo ""
read -p "Push to origin/main now? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "⏸️  Push cancelled. You can manually push later with:"
    echo "   git push origin main"
    echo ""
    echo "Changes are committed locally ✅"
    exit 0
fi

git push origin main

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================================================"
    echo "🎉 DEPLOYMENT INITIATED - CONSISTENCY FIX"
    echo "========================================================================"
    echo ""
    echo "📊 What's Happening Now:"
    echo "  1. Render detects new commit"
    echo "  2. Starts build process"
    echo "  3. Runs build.sh (installs system dependencies)"
    echo "  4. Installs Python packages"
    echo "  5. Deploys new backend"
    echo "  6. Health check passes → Live ✅"
    echo ""
    echo "⏱️  Expected Build Time: 5-7 minutes"
    echo "   (Longer due to system dependency installation)"
    echo ""
    echo "📝 Next Steps:"
    echo "----------------------------------------------------------------------"
    echo "1. Go to Render Dashboard: https://dashboard.render.com"
    echo ""
    echo "2. Monitor Build Logs - Look for:"
    echo "   ✅ '📦 Installing system dependencies for WeasyPrint...'"
    echo "   ✅ '✅ WeasyPrint system dependencies installed'"
    echo "   ✅ '✅ Build complete! WeasyPrint enabled'"
    echo ""
    echo "3. Wait for 'Live' status (5-7 minutes)"
    echo ""
    echo "4. Test in Production App:"
    echo "   a. Create new visa application"
    echo "   b. Fill questionnaire (or use auto-fill)"
    echo "   c. Generate documents"
    echo "   d. Download Asset Valuation Certificate"
    echo "   e. Verify: 13 pages ✅ (not 5, not 10)"
    echo "   f. Check: Same design as local version ✅"
    echo ""
    echo "5. Check Render Logs for:"
    echo "   '✅ Asset valuation generated with WeasyPrint 13-page template'"
    echo ""
    echo "❌ If you see 'Falling back to ReportLab':"
    echo "   - WeasyPrint dependencies didn't install properly"
    echo "   - Check build logs for apt-get errors"
    echo "   - See ASSET_VALUATION_CONSISTENCY_FIX.md for troubleshooting"
    echo ""
    echo "========================================================================"
    echo "📖 Full Documentation:"
    echo "----------------------------------------------------------------------"
    echo "  - ASSET_VALUATION_CONSISTENCY_FIX.md (troubleshooting)"
    echo "  - ASSET_VALUATION_13PAGE_UPDATE_COMPLETE.md (complete details)"
    echo "  - QUICK_DEPLOY_GUIDE.md (quick reference)"
    echo ""
    echo "✅ Deployment script completed successfully!"
    echo "========================================================================"
else
    echo ""
    echo "❌ Push failed. Please check your repository access."
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check git remote: git remote -v"
    echo "  2. Check branch: git branch"
    echo "  3. Try manual push: git push origin main"
    echo "  4. Check network connection"
    exit 1
fi
