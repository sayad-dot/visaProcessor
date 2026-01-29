"""
Document Generator Service - Generate PDFs for missing documents
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from typing import Dict, Any
from datetime import datetime
from loguru import logger
import os


class DocumentGenerator:
    """Service for generating PDF documents"""
    
    def __init__(self, output_folder: str):
        """
        Initialize document generator
        
        Args:
            output_folder: Path to folder where generated documents will be saved
        """
        self.output_folder = output_folder
        os.makedirs(output_folder, exist_ok=True)
    
    def generate_cover_letter(
        self,
        content: str,
        user_data: Dict[str, Any],
        filename: str
    ) -> str:
        """
        Generate a cover letter PDF
        
        Args:
            content: Generated content from AI
            user_data: User information
            filename: Output filename
            
        Returns:
            Path to generated PDF file
        """
        try:
            output_path = os.path.join(self.output_folder, filename)
            
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            story = []
            styles = getSampleStyleSheet()
            
            # Add applicant info header
            header_style = ParagraphStyle(
                'CustomHeader',
                parent=styles['Normal'],
                fontSize=10,
                alignment=TA_RIGHT
            )
            
            applicant_name = user_data.get('name', 'Applicant Name')
            applicant_address = user_data.get('address', 'Address')
            
            story.append(Paragraph(applicant_name, header_style))
            story.append(Paragraph(applicant_address, header_style))
            story.append(Spacer(1, 0.3*inch))
            
            # Date
            date_str = datetime.now().strftime("%B %d, %Y")
            story.append(Paragraph(date_str, styles['Normal']))
            story.append(Spacer(1, 0.3*inch))
            
            # Recipient
            story.append(Paragraph("To,", styles['Normal']))
            story.append(Paragraph("The Visa Officer", styles['Normal']))
            story.append(Paragraph("Embassy of Iceland", styles['Normal']))
            story.append(Spacer(1, 0.3*inch))
            
            # Subject
            subject_style = ParagraphStyle(
                'Subject',
                parent=styles['Normal'],
                fontSize=11,
                fontName='Helvetica-Bold'
            )
            story.append(Paragraph("Subject: Application for Iceland Tourist Visa", subject_style))
            story.append(Spacer(1, 0.2*inch))
            
            # Content
            content_paragraphs = content.split('\n\n')
            for para in content_paragraphs:
                if para.strip():
                    story.append(Paragraph(para, styles['Normal']))
                    story.append(Spacer(1, 0.1*inch))
            
            # Signature
            story.append(Spacer(1, 0.3*inch))
            story.append(Paragraph("Sincerely,", styles['Normal']))
            story.append(Spacer(1, 0.5*inch))
            story.append(Paragraph(applicant_name, styles['Normal']))
            
            # Build PDF
            doc.build(story)
            
            logger.info(f"Generated cover letter: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating cover letter: {str(e)}")
            raise
    
    def generate_travel_itinerary(
        self,
        itinerary_data: Dict[str, Any],
        filename: str
    ) -> str:
        """
        Generate a travel itinerary PDF
        
        Args:
            itinerary_data: Itinerary information
            filename: Output filename
            
        Returns:
            Path to generated PDF file
        """
        try:
            output_path = os.path.join(self.output_folder, filename)
            
            doc = SimpleDocTemplate(output_path, pagesize=A4)
            story = []
            styles = getSampleStyleSheet()
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                textColor=colors.HexColor('#1a1a1a'),
                alignment=TA_CENTER,
                spaceAfter=20
            )
            story.append(Paragraph("TRAVEL ITINERARY", title_style))
            story.append(Spacer(1, 0.3*inch))
            
            # TODO: Add itinerary details
            # This will be implemented in Phase 4 with actual data structure
            
            # Build PDF
            doc.build(story)
            
            logger.info(f"Generated travel itinerary: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating travel itinerary: {str(e)}")
            raise
    
    def generate_visiting_card(
        self,
        user_data: Dict[str, Any],
        filename: str
    ) -> str:
        """
        Generate a professional visiting card PDF
        
        Args:
            user_data: User information for the card
            filename: Output filename
            
        Returns:
            Path to generated PDF file
        """
        try:
            output_path = os.path.join(self.output_folder, filename)
            
            # TODO: Implement beautiful visiting card design
            # This will be implemented in Phase 4
            
            logger.info(f"Generated visiting card: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating visiting card: {str(e)}")
            raise
    
    def compress_pdf(self, input_path: str, max_size_mb: int = 4) -> str:
        """
        Compress PDF to be under specified size
        
        Args:
            input_path: Path to input PDF
            max_size_mb: Maximum size in MB
            
        Returns:
            Path to compressed PDF
        """
        # TODO: Implement PDF compression in Phase 5
        # For now, just return original path
        return input_path
