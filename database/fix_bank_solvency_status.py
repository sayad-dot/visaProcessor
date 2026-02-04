"""
Fix bank_solvency status from REQUIRED to SUGGESTED
Updates existing database records
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent / "backend"))

from app.database import SessionLocal, engine
from app.models import RequiredDocument, DocumentType

def fix_bank_solvency_status():
    """Update bank_solvency from mandatory to suggested"""
    db = SessionLocal()
    try:
        print("🔧 Fixing bank_solvency status...")
        
        # Find bank_solvency document
        bank_solvency_docs = db.query(RequiredDocument).filter(
            RequiredDocument.document_type == DocumentType.BANK_SOLVENCY
        ).all()
        
        if not bank_solvency_docs:
            print("❌ No bank_solvency documents found in database!")
            return
        
        updated_count = 0
        for doc in bank_solvency_docs:
            print(f"  Found: {doc.document_type} - is_mandatory={doc.is_mandatory}")
            
            if doc.is_mandatory:
                doc.is_mandatory = False
                doc.description = "Bank solvency certificate - SUGGESTED (Upload if available, or system will use questionnaire data)"
                updated_count += 1
                print(f"  ✅ Updated to: is_mandatory=False")
        
        db.commit()
        print(f"\n✅ Successfully updated {updated_count} bank_solvency records!")
        print("   Bank solvency is now SUGGESTED (not required)")
        
        # Verify the change
        print("\n📋 Verification:")
        for doc in bank_solvency_docs:
            db.refresh(doc)
            print(f"  {doc.document_type}: is_mandatory={doc.is_mandatory}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("=" * 60)
    print("Bank Solvency Status Fix")
    print("=" * 60)
    fix_bank_solvency_status()
    print("\n✨ Done! Restart your backend server to see changes.")
    print("=" * 60)
