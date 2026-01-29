"""
PDF Service - Extract text and data from PDF documents with OCR support
"""
import PyPDF2
from typing import Optional, Dict, Any, List
from loguru import logger
import os
from PIL import Image
import io


class PDFService:
    """Service for PDF processing operations"""
    
    def __init__(self):
        """Initialize PDF service"""
        self.ocr_available = self._check_ocr_availability()
    
    def _check_ocr_availability(self) -> bool:
        """Check if OCR libraries are available"""
        try:
            import pytesseract
            from pdf2image import convert_from_path
            logger.info("OCR support available")
            return True
        except ImportError:
            logger.warning("OCR libraries not available. Install with: pip install pytesseract pdf2image")
            return False
    
    def extract_text_from_pdf(self, file_path: str, use_ocr: bool = False) -> str:
        """
        Extract text content from a PDF file
        
        Args:
            file_path: Path to the PDF file
            use_ocr: Whether to use OCR for image-based PDFs
            
        Returns:
            Extracted text as string
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"PDF file not found: {file_path}")
            
            text = ""
            
            # First try standard text extraction
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Extract text from all pages
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    page_text = page.extract_text()
                    text += page_text + "\n"
            
            # If text is minimal and OCR is available, try OCR
            if len(text.strip()) < 100 and use_ocr and self.ocr_available:
                logger.info(f"Text extraction yielded minimal results, trying OCR for {file_path}")
                ocr_text = self.extract_text_with_ocr(file_path)
                if len(ocr_text) > len(text):
                    text = ocr_text
            
            logger.info(f"Successfully extracted {len(text)} characters from PDF: {file_path}")
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text from PDF {file_path}: {str(e)}")
            return ""
    
    def extract_text_with_ocr(self, file_path: str) -> str:
        """
        Extract text from PDF using OCR (for scanned documents)
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Extracted text as string
        """
        if not self.ocr_available:
            logger.warning("OCR not available, returning empty string")
            return ""
        
        try:
            import pytesseract
            from pdf2image import convert_from_path
            
            # Convert PDF to images
            images = convert_from_path(file_path, dpi=300)
            
            text = ""
            for i, image in enumerate(images):
                # Extract text from each page image
                page_text = pytesseract.image_to_string(image, lang='eng')
                text += f"\n--- Page {i+1} ---\n{page_text}"
            
            logger.info(f"OCR extracted {len(text)} characters from {file_path}")
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error performing OCR on {file_path}: {str(e)}")
            return ""
    
    def extract_text_from_image(self, image_path: str) -> str:
        """
        Extract text from image file using OCR
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Extracted text as string
        """
        if not self.ocr_available:
            logger.warning("OCR not available for image extraction")
            return ""
        
        try:
            import pytesseract
            from PIL import Image
            
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image, lang='eng')
            
            logger.info(f"Extracted {len(text)} characters from image: {image_path}")
            return text.strip()
            
        except Exception as e:
            logger.error(f"Error extracting text from image {image_path}: {str(e)}")
            return ""
    
    def get_pdf_metadata(self, file_path: str) -> Dict[str, Any]:
        """
        Extract metadata from a PDF file
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dictionary containing PDF metadata
        """
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                metadata = {
                    'num_pages': len(pdf_reader.pages),
                    'file_size': os.path.getsize(file_path),
                    'file_size_mb': round(os.path.getsize(file_path) / (1024 * 1024), 2),
                    'info': {}
                }
                
                if pdf_reader.metadata:
                    for key, value in pdf_reader.metadata.items():
                        metadata['info'][key] = str(value)
                
                logger.info(f"Extracted metadata from {file_path}: {metadata['num_pages']} pages")
                return metadata
                
        except Exception as e:
            logger.error(f"Error extracting metadata from PDF {file_path}: {str(e)}")
            return {
                'num_pages': 0,
                'file_size': 0,
                'file_size_mb': 0,
                'info': {},
                'error': str(e)
            }
    
    def get_page_count(self, file_path: str) -> int:
        """
        Get the number of pages in a PDF file
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Number of pages
        """
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                page_count = len(pdf_reader.pages)
                logger.info(f"PDF {file_path} has {page_count} pages")
                return page_count
        except Exception as e:
            logger.error(f"Error getting page count from PDF {file_path}: {str(e)}")
            return 0
    
    def validate_pdf(self, file_path: str) -> Dict[str, Any]:
        """
        Validate PDF file and return comprehensive information
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dictionary with validation results and file info
        """
        result = {
            'valid': False,
            'file_exists': False,
            'is_pdf': False,
            'readable': False,
            'num_pages': 0,
            'file_size_mb': 0,
            'has_text': False,
            'text_length': 0,
            'error': None
        }
        
        try:
            # Check file exists
            if not os.path.exists(file_path):
                result['error'] = "File does not exist"
                return result
            result['file_exists'] = True
            
            # Check is PDF
            if not file_path.lower().endswith('.pdf'):
                result['error'] = "Not a PDF file"
                return result
            result['is_pdf'] = True
            
            # Get file size
            result['file_size_mb'] = round(os.path.getsize(file_path) / (1024 * 1024), 2)
            
            # Try to read
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                result['num_pages'] = len(pdf_reader.pages)
                result['readable'] = True
                
                # Check for text content
                text = self.extract_text_from_pdf(file_path)
                result['text_length'] = len(text)
                result['has_text'] = len(text) > 50
                
                result['valid'] = True
                
            logger.info(f"PDF validation successful for {file_path}")
            return result
            
        except Exception as e:
            logger.error(f"Error validating PDF {file_path}: {str(e)}")
            result['error'] = str(e)
            return result
