#!/bin/bash

# Asset Valuation 13-Page Template - Deployment Script
# Run this after reviewing all changes

echo "========================================================================"
echo "Asset Valuation 13-Page Template - Deployment"
echo "========================================================================"
echo ""

# Check if we're in the right directory
if [ ! -f "ASSET_VALUATION_13PAGE_UPDATE_COMPLETE.md" ]; then
    echo "❌ Error: Please run this script from the visa project root directory"
    exit 1
fi

echo "📋 Step 1: Reviewing changes..."
echo "----------------------------------------------------------------------"
git status

echo ""
echo "📝 Files that will be committed:"
echo "  - backend/app/templates/asset_valuation_template_13page.html (NEW)"
echo "  - backend/app/services/template_renderer.py (MODIFIED)"
echo "  - backend/app/services/pdf_generator_service.py (MODIFIED)"
echo "  - test_asset_valuation_13page.py (NEW - Optional)"
echo "  - analyze_asset_valuation_template.py (NEW - Optional)"
echo "  - ASSET_VALUATION_13PAGE_UPDATE_COMPLETE.md (NEW - Documentation)"
echo ""

read -p "Do you want to proceed with deployment? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Deployment cancelled"
    exit 0
fi

echo ""
echo "📦 Step 2: Adding files to git..."
echo "----------------------------------------------------------------------"
git add backend/app/templates/asset_valuation_template_13page.html
git add backend/app/services/template_renderer.py
git add backend/app/services/pdf_generator_service.py
git add ASSET_VALUATION_13PAGE_UPDATE_COMPLETE.md

# Optional test files
git add test_asset_valuation_13page.py
git add analyze_asset_valuation_template.py

echo "✅ Files staged for commit"

echo ""
echo "💾 Step 3: Committing changes..."
echo "----------------------------------------------------------------------"
git commit -m "feat: Upgrade Asset Valuation to comprehensive 13-page template

✨ Features:
- Add asset_valuation_template_13page.html with full 13-page structure
- Update template_renderer with 40+ comprehensive data fields
- Enhance pdf_generator_service to collect data from questionnaire
- Add all missing sections: methodology, legal aspects, detailed schedules

🔧 Technical Changes:
- Page 1: Cover page with title and owner info
- Page 2: Company header and report metadata
- Page 3: Synopsis table with all asset valuations
- Page 4-5: Location details for all schedules (A, B, C, D, E)
- Page 6-7: Property descriptions and deed information
- Page 8: Importance of locality for each property
- Page 9: Methodology and basis of valuation
- Page 10-11: Detailed valuations with per-sqft calculations
- Page 12: Legal aspects, observations, and certifications
- Page 13: Signature page

✅ Testing:
- Tested locally: 35.4KB PDF generation successful
- All 13 pages render correctly
- Data fields populate from questionnaire
- Intelligent defaults for missing data
- Backward compatibility maintained (5-page version preserved)

📊 Impact:
- Matches real-world embassy submission format
- Professional quality documentation
- Enhanced data collection from questionnaire
- No database changes required
- No frontend changes required

🎯 Deployment:
- Backend: Auto-deploy via Render (push to trigger)
- Frontend: No changes needed
- Database: No migrations required"

if [ $? -eq 0 ]; then
    echo "✅ Changes committed successfully"
else
    echo "❌ Commit failed. Please check errors above."
    exit 1
fi

echo ""
echo "🚀 Step 4: Pushing to remote repository..."
echo "----------------------------------------------------------------------"
read -p "Push to origin/main to trigger Render deployment? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "⏸️  Push cancelled. You can manually push later with: git push origin main"
    echo ""
    echo "📄 Summary:"
    echo "  - Changes committed locally ✅"
    echo "  - Not pushed to remote ⏸️"
    echo "  - Run 'git push origin main' when ready"
    exit 0
fi

git push origin main

if [ $? -eq 0 ]; then
    echo "✅ Successfully pushed to remote!"
    echo ""
    echo "========================================================================"
    echo "🎉 DEPLOYMENT INITIATED"
    echo "========================================================================"
    echo ""
    echo "Next Steps:"
    echo "  1. Monitor Render deployment at: https://dashboard.render.com"
    echo "  2. Check deployment logs for: '✅ Asset valuation generated with WeasyPrint 13-page template'"
    echo "  3. Wait 3-5 minutes for build to complete"
    echo "  4. Test in production:"
    echo "     - Create new application"
    echo "     - Fill questionnaire"
    echo "     - Generate documents"
    echo "     - Download Asset Valuation Certificate"
    echo "     - Verify 13 pages with correct content"
    echo ""
    echo "📖 Full documentation: ASSET_VALUATION_13PAGE_UPDATE_COMPLETE.md"
    echo ""
    echo "✅ Deployment script completed successfully!"
else
    echo "❌ Push failed. Please check your remote repository access."
    echo ""
    echo "Manual push command: git push origin main"
    exit 1
fi
