"""
Analyze the Asset Valuation PDF template to understand its structure
"""
import PyPDF2
import sys

def analyze_pdf(pdf_path):
    """Extract and analyze PDF content"""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            num_pages = len(pdf_reader.pages)
            
            print(f"=" * 80)
            print(f"PDF ANALYSIS: Asset Valuation Template")
            print(f"=" * 80)
            print(f"Total Pages: {num_pages}\n")
            
            for page_num in range(num_pages):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                
                print(f"\n{'=' * 80}")
                print(f"PAGE {page_num + 1}")
                print(f"{'=' * 80}")
                print(text)
                print("\n")
                
    except Exception as e:
        print(f"Error analyzing PDF: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    pdf_path = "/media/sayad/Ubuntu-Data/visa/Real Templates/Asset Valuation swapon Sheikh.pdf"
    analyze_pdf(pdf_path)
