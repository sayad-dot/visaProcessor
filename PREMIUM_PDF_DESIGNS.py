# ULTRA-PREMIUM PDF DESIGNS - FOR INTEGRATION

def _generate_visiting_card_reportlab_PREMIUM(self, data: dict, file_path: str):
    """Fallback: Generate ULTRA-PREMIUM luxury visiting card using ReportLab"""
    from reportlab.pdfgen import canvas as pdf_canvas
    from reportlab.lib import colors
    
    c = pdf_canvas.Canvas(file_path, pagesize=(252, 144))
    
    # === LUXURY DESIGN ===
    # Deep charcoal luxury background
    c.setFillColor(colors.HexColor('#1A1A2E'))
    c.rect(0, 0, 252, 144, fill=True, stroke=False)
    
    # Gold top & bottom borders
    c.setFillColor(colors.HexColor('#D4AF37'))
    c.rect(0, 136, 252, 8, fill=True, stroke=False)
    c.rect(0, 0, 252, 8, fill=True, stroke=False)
    
    # LEFT: LUXURY PANEL
    c.setFillColor(colors.HexColor('#0F3460'))
    c.rect(0, 8, 90, 128, fill=True, stroke=False)
    
    # Gold decorative lines
    c.setStrokeColor(colors.HexColor('#D4AF37'))
    c.setLineWidth(1)
    for y_pos in [120, 110, 100]:
        c.line(15, y_pos, 75, y_pos)
    
    # Premium logo circle
    c.setStrokeColor(colors.HexColor('#D4AF37'))
    c.setLineWidth(2.5)
    c.circle(45, 70, 22, fill=False, stroke=True)
    c.setFillColor(colors.HexColor('#D4AF37'))
    c.circle(45, 70, 5, fill=True, stroke=False)
    
    # Corner decorations
    c.setStrokeColor(colors.HexColor('#D4AF37'))
    c.setLineWidth(1.5)
    c.line(10, 130, 30, 130)
    c.line(10, 130, 10, 110)
    c.line(60, 14, 80, 14)
    c.line(80, 14, 80, 34)
    
    # RIGHT: WHITE PANEL with pattern
    c.setFillColor(colors.HexColor('#F8F9FA'))
    c.rect(90, 8, 162, 128, fill=True, stroke=False)
    
    c.setStrokeColor(colors.HexColor('#E8E9EA'))
    c.setLineWidth(0.3)
    for i in range(5):
        c.line(95 + i*30, 136, 95 + i*30, 8)
    
    # NAME - LARGE & BOLD
    c.setFillColor(colors.HexColor('#1A1A2E'))
    c.setFont('Helvetica-Bold', 18)
    c.drawString(100, 108, data['full_name'][:25])
    
    # Designation with gold background
    designation_text = data['designation'][:20].upper()
    c.setFillColor(colors.HexColor('#D4AF37'))
    c.rect(100, 88, len(designation_text) * 5.5, 14, fill=True, stroke=False)
    c.setFillColor(colors.HexColor('#1A1A2E'))
    c.setFont('Helvetica-Bold', 9)
    c.drawString(103, 92, designation_text)
    
    # Dotted separator
    c.setFillColor(colors.HexColor('#D4AF37'))
    for x in range(100, 240, 8):
        c.circle(x, 80, 0.8, fill=True, stroke=False)
    
    # Contact details
    c.setFillColor(colors.HexColor('#D4AF37'))
    c.circle(102, 67, 2, fill=True, stroke=False)
    c.setFillColor(colors.HexColor('#1A1A2E'))
    c.setFont('Helvetica-Bold', 8)
    c.drawString(107, 65, "Phone:")
    c.setFont('Helvetica', 8)
    c.drawString(138, 65, data['phone'][:20])
    
    c.setFillColor(colors.HexColor('#D4AF37'))
    c.circle(102, 54, 2, fill=True, stroke=False)
    c.setFillColor(colors.HexColor('#1A1A2E'))
    c.setFont('Helvetica-Bold', 8)
    c.drawString(107, 52, "Email:")
    c.setFont('Helvetica', 8)
    c.drawString(138, 52, data['email'][:23])
    
    c.setFillColor(colors.HexColor('#D4AF37'))
    c.circle(102, 41, 2, fill=True, stroke=False)
    c.setFillColor(colors.HexColor('#1A1A2E'))
    c.setFont('Helvetica-Bold', 8)
    c.drawString(107, 39, "Web:")
    c.setFont('Helvetica', 8)
    c.drawString(138, 39, data['website'][:25])
    
    # Footer
    c.setFillColor(colors.HexColor('#666666'))
    c.setFont('Helvetica-Oblique', 7)
    c.drawString(100, 18, "Dhaka, Bangladesh  |  Professional Visa Consultancy")
    
    # Corner decoration
    c.setStrokeColor(colors.HexColor('#D4AF37'))
    c.setLineWidth(1.5)
    c.line(240, 14, 240, 34)
    c.line(220, 14, 240, 14)
    
    c.save()
