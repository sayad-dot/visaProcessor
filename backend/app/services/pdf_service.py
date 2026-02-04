"""
PDF Service - Enhanced version with complete OCR, image support, and better text extraction
"""
import PyPDF2
from typing import Optional, Dict, Any, List
from loguru import logger
import os
from PIL import Image
import io


class PDFService:
    """Enhanced service for PDF processing with automatic OCR and image support"""
    
    def __init__(self):
        """Initialize PDF service with OCR capabilities"""
        self.ocr_available = self._check_ocr_availability()
        self._configure_tesseract()
    
    def _check_ocr_availability(self) -> bool:
        """Check if OCR libraries are available"""
        try:
            import pytesseract
            from pdf2image import convert_from_path
            logger.info("✅ OCR support available (pytesseract + pdf2image)")
            return True
        except ImportError as e:
            logger.warning(f"⚠️ OCR libraries not available: {str(e)}")
            logger.warning("Install with: pip install pytesseract pdf2image Pillow")
            logger.warning("Also install system packages: sudo apt-get install tesseract-ocr tesseract-ocr-ben")
            return False
    
    def _configure_tesseract(self):
        """Configure Tesseract for better accuracy"""
        if not self.ocr_available:
            return
        
        try:
            import pytesseract
            # Try to find tesseract executable (adjust path based on system)
            possible_paths = [
                '/usr/bin/tesseract',
                '/usr/local/bin/tesseract',
                'C:\\Program Files\\Tesseract-OCR\\tesseract.exe',  # Windows
                '/opt/homebrew/bin/tesseract'  # Mac M1
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    logger.info(f"✅ Tesseract configured at: {path}")
                    break
        except Exception as e:
            logger.warning(f"Could not configure Tesseract path: {str(e)}")
    
    def extract_text_from_file(self, file_path: str) -> str:
        """
        Smart extraction that handles PDFs and images automatically
        
        Args:
            file_path: Path to the file (PDF, JPG, PNG, etc.)
            
        Returns:
            Extracted text as string
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Determine file type
            file_extension = file_path.lower().split('.')[-1]
            
            # Handle images directly
            if file_extension in ['jpg', 'jpeg', 'png', 'bmp', 'tiff', 'webp']:
                logger.info(f"📄 Detected image file: {file_extension}")
                return self.extract_text_from_image(file_path)
            
            # Handle PDFs with smart OCR
            elif file_extension == 'pdf':
                logger.info("📄 Detected PDF file")
                return self.extract_text_from_pdf(file_path, use_ocr=True, auto_detect=True)
            
            else:
                logger.warning(f"⚠️ Unsupported file type: {file_extension}")
                return ""
                
        except Exception as e:
            logger.error(f"❌ Error extracting text from file {file_path}: {str(e)}")
            return ""
    
    def extract_text_from_pdf(
        self, 
        file_path: str, 
        use_ocr: bool = True, 
        auto_detect: bool = True
    ) -> str:
        """
        Enhanced PDF text extraction with automatic OCR detection
        
        Args:
            file_path: Path to the PDF file
            use_ocr: Whether to use OCR if needed
            auto_detect: Automatically detect if OCR is needed
            
        Returns:
            Extracted text as string
        """
        try:
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"PDF file not found: {file_path}")
            
            text = ""
            
            # Step 1: Try standard text extraction
            logger.info(f"📖 Attempting standard PDF text extraction: {os.path.basename(file_path)}")
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                
                logger.info(f"📄 PDF has {num_pages} page(s)")
                
                # Extract text from all pages
                for page_num in range(num_pages):
                    try:
                        page = pdf_reader.pages[page_num]
                        page_text = page.extract_text()
                        text += page_text + "\n"
                    except Exception as e:
                        logger.warning(f"⚠️ Error extracting text from page {page_num + 1}: {str(e)}")
                        continue
            
            # Clean and measure quality
            text_clean = text.strip()
            text_length = len(text_clean)
            words = len(text_clean.split())
            
            logger.info(f"📊 Standard extraction: {text_length} chars, {words} words")
            
            # Step 2: Auto-detect if OCR is needed
            needs_ocr = False
            
            if auto_detect:
                # Criteria for triggering OCR:
                # 1. Very little text extracted (< 100 chars)
                # 2. Very few words (< 20 words)
                # 3. Low character-to-word ratio (might be garbled)
                
                if text_length < 100:
                    logger.info("🔍 Very little text found, will use OCR")
                    needs_ocr = True
                elif words < 20:
                    logger.info("🔍 Too few words, will use OCR")
                    needs_ocr = True
                elif words > 0 and (text_length / words) < 3:
                    logger.info("🔍 Poor text quality detected, will use OCR")
                    needs_ocr = True
            
            # Step 3: OCR DISABLED - Not needed for this system
            # All data comes from questionnaire, OCR was optional feature
            if needs_ocr:
                logger.info("ℹ️ OCR disabled (not needed - questionnaire provides all data)")
            
            logger.info(f"✅ Final extraction: {len(text_clean)} characters from {os.path.basename(file_path)}")
            return text_clean
            
        except Exception as e:
            logger.error(f"❌ Error extracting text from PDF {file_path}: {str(e)}")
            
            # OCR disabled - not needed for this application
            logger.info("ℹ️ OCR disabled - questionnaire system handles all data collection")
            
            return ""
    
    def extract_text_with_ocr(self, file_path: str) -> str:
        """
        OCR DISABLED - Not needed since all data comes from questionnaire
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Empty string (OCR disabled)
        """
        logger.info("ℹ️ OCR disabled - all data collected via questionnaire")
        return ""  # OCR completely disabled to save memory
        
        try:
            import pytesseract
            from pdf2image import convert_from_path
            
            logger.info(f"🤖 Starting high-quality OCR on: {os.path.basename(file_path)}")
            
            # Check file size first
            file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
            logger.info(f"📦 PDF file size: {file_size_mb:.2f} MB")
            
            # ULTRA-CONSERVATIVE limits for free tier (512MB RAM)
            MAX_FILE_SIZE_MB = 2  # Only 2MB files for OCR (was 5MB)
            if file_size_mb > MAX_FILE_SIZE_MB:
                logger.warning(f"⚠️ File too large for OCR ({file_size_mb:.2f} MB > {MAX_FILE_SIZE_MB} MB). Using basic text extraction only.")
                logger.warning(f"💡 For better OCR support, upgrade to paid plan or use smaller files.")
                return f"[File too large for OCR: {file_size_mb:.2f} MB. Basic text extraction used. For OCR, use files <{MAX_FILE_SIZE_MB}MB or upgrade plan.]"
            
            # Get page count first without loading all pages
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                total_pages = len(pdf_reader.pages)
            
            # STRICT page limit for free tier
            MAX_PAGES = 3  # Only 3 pages max (was 10)
            if total_pages > MAX_PAGES:
                logger.warning(f"⚠️ PDF has {total_pages} pages. Processing only first {MAX_PAGES} pages (free tier limit).")
                logger.warning(f"💡 Upgrade to paid plan for unlimited page processing.")
                total_pages = MAX_PAGES
            
            logger.info(f"🤖 Starting memory-efficient OCR on {total_pages} page(s)")
            
            text = ""
            
            # Process pages ONE AT A TIME to manage memory
            for page_num in range(total_pages):
                try:
                    logger.info(f"🔍 OCR processing page {page_num+1}/{total_pages}...")
                    
                    # Convert SINGLE page to image (ultra memory efficient)
                    images = convert_from_path(
                        file_path,
                        first_page=page_num + 1,
                        last_page=page_num + 1,
                        dpi=150,  # MINIMAL DPI for free tier (90% less memory than 400)
                        fmt='jpeg',
                        grayscale=True
                    )
                    
                    if not images:
                        logger.warning(f"⚠️ No image generated for page {page_num+1}")
                        continue
                    
                    image = images[0]
            
                    # OCR the single page
                    try:
                        # Use English only for better reliability
                        # --psm 3 = Automatic page segmentation (more reliable than psm 1)
                        # --oem 3 = Default OCR Engine
                        page_text = pytesseract.image_to_string(
                            image,
                            lang='eng',  # English only (more stable than eng+ben)
                            config='--psm 3 --oem 3'
                        )
                        
                        text += f"\n--- Page {page_num+1} ---\n{page_text}"
                        logger.info(f"📝 Page {page_num+1}: Extracted {len(page_text)} characters")
                        
                    except Exception as ocr_error:
                        logger.error(f"❌ OCR error on page {page_num+1}: {str(ocr_error)}")
                        text += f"\n--- Page {page_num+1} ---\n[OCR failed: {str(ocr_error)}]\n"
                    
                    # Clean up memory after each page
                    del images
                    del image
                    
                except Exception as page_error:
                    logger.error(f"❌ Error processing page {page_num+1}: {str(page_error)}")
                    continue
            
            text_clean = text.strip()
            logger.info(f"✅ OCR completed: {len(text_clean)} total characters extracted")
            
            if len(text_clean) < 50:
                logger.warning(f"⚠️ OCR extracted very little text ({len(text_clean)} chars). Document may be blank or very low quality.")
            
            return text_clean
            
        except Exception as e:
            logger.error(f"❌ Error performing OCR on {file_path}: {str(e)}", exc_info=True)
            return ""
    
    def extract_text_from_image(self, image_path: str) -> str:
        """
        Enhanced image text extraction with advanced preprocessing
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Extracted text as string
        """
        if not self.ocr_available:
            logger.warning("⚠️ OCR not available for image extraction")
            return ""
        
        try:
            import pytesseract
            from PIL import Image, ImageEnhance, ImageFilter
            
            logger.info(f"📸 Starting enhanced OCR on image: {os.path.basename(image_path)}")
            
            # Load image
            image = Image.open(image_path)
            original_mode = image.mode
            logger.info(f"📷 Image mode: {original_mode}, Size: {image.size}")
            
            # Convert to RGB if needed
            if image.mode not in ['RGB', 'L']:
                image = image.convert('RGB')
                logger.info(f"Converted to RGB from {original_mode}")
            
            # ===== Enhanced preprocessing for better OCR =====
            
            # 1. Increase contrast significantly
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)  # ← INCREASED from 1.5 to 2.0
            logger.info("✓ Contrast enhanced")
            
            # 2. Increase sharpness
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(2.0)  # ← ADDED sharpness enhancement
            logger.info("✓ Sharpness enhanced")
            
            # 3. Increase brightness slightly
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(1.2)
            logger.info("✓ Brightness adjusted")
            
            # 4. Convert to grayscale for better OCR
            image = image.convert('L')
            logger.info("✓ Converted to grayscale")
            
            # 5. Apply threshold to make text clearer
            # Convert to binary (black and white only)
            threshold = 128
            image = image.point(lambda x: 255 if x > threshold else 0)
            logger.info("✓ Applied binary threshold")
            
            # 6. Apply additional sharpening filter
            image = image.filter(ImageFilter.SHARPEN)
            logger.info("✓ Applied sharpening filter")
            
            # ===== Perform OCR with optimal settings =====
            text = pytesseract.image_to_string(
                image,
                lang='eng+ben',  # English + Bengali
                config='--psm 1 --oem 3'  # ← CHANGED from psm 3 to psm 1 for better results
            )
            
            text_clean = text.strip()
            logger.info(f"✅ Extracted {len(text_clean)} characters from image: {os.path.basename(image_path)}")
            
            if len(text_clean) < 50:
                logger.warning(f"⚠️ Very little text extracted ({len(text_clean)} chars). Image may be low quality or contain minimal text.")
            
            return text_clean
            
        except Exception as e:
            logger.error(f"❌ Error extracting text from image {image_path}: {str(e)}", exc_info=True)
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
                
                logger.info(f"📊 Extracted metadata from {file_path}: {metadata['num_pages']} pages")
                return metadata
                
        except Exception as e:
            logger.error(f"❌ Error extracting metadata from PDF {file_path}: {str(e)}")
            return {
                'num_pages': 0,
                'file_size': 0,
                'file_size_mb': 0,
                'info': {},
                'error': str(e)
            }
    
    def get_page_count(self, file_path: str) -> int:
        """Get the number of pages in a PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                page_count = len(pdf_reader.pages)
                logger.info(f"📄 PDF {file_path} has {page_count} pages")
                return page_count
        except Exception as e:
            logger.error(f"❌ Error getting page count from PDF {file_path}: {str(e)}")
            return 0
    
    def validate_pdf(self, file_path: str) -> Dict[str, Any]:
        """
        Enhanced PDF validation with text quality assessment
        
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
            'text_quality': 'unknown',  # 'good', 'poor', 'scanned'
            'needs_ocr': False,
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
                
                # Extract text to assess quality
                text = self.extract_text_from_pdf(file_path, use_ocr=False)
                result['text_length'] = len(text)
                result['has_text'] = len(text) > 50
                
                # Assess text quality
                if len(text) < 50:
                    result['text_quality'] = 'scanned'
                    result['needs_ocr'] = True
                elif len(text.split()) < 20:
                    result['text_quality'] = 'poor'
                    result['needs_ocr'] = True
                else:
                    result['text_quality'] = 'good'
                    result['needs_ocr'] = False
                
                result['valid'] = True
                
            logger.info(f"✅ PDF validation successful: {file_path} - Quality: {result['text_quality']}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Error validating PDF {file_path}: {str(e)}")
            result['error'] = str(e)
            return result