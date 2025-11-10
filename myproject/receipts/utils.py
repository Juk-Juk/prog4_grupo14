from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.enums import TA_CENTER
from io import BytesIO
from datetime import datetime

def generate_cart_receipt(cart, user):
    """Generate a PDF receipt for the shopping cart"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    # Container for elements
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    header_style = ParagraphStyle(
        'CustomHeader',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.grey,
        alignment=TA_CENTER,
        spaceAfter=20
    )
    
    # Title
    title = Paragraph("Resumen de Carrito", title_style)
    elements.append(title)
    
    # Header info
    header_text = f"""
    <b>Mi Mercado</b><br/>
    Usuario: {user.username}<br/>
    Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}<br/>
    Email: {user.email if user.email else 'No proporcionado'}
    """
    header = Paragraph(header_text, header_style)
    elements.append(header)
    elements.append(Spacer(1, 0.3*inch))
    
    # Cart items table
    cart_items = cart.items.all()
    
    if cart_items:
        # Table data
        data = [['Producto', 'Precio', 'Cantidad', 'Subtotal']]
        
        for item in cart_items:
            data.append([
                Paragraph(item.product.title[:40], styles['Normal']),
                f'${item.product.price}',
                str(item.quantity),
                f'${item.subtotal()}'
            ])
        
        # Add total row
        data.append(['', '', 'TOTAL:', f'${cart.total()}'])
        
        # Create table
        table = Table(data, colWidths=[3.5*inch, 1.2*inch, 1*inch, 1.2*inch])
        table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            
            # Data rows
            ('BACKGROUND', (0, 1), (-1, -2), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('ALIGN', (1, 1), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -2), 10),
            ('TOPPADDING', (0, 1), (-1, -2), 6),
            ('BOTTOMPADDING', (0, 1), (-1, -2), 6),
            
            # Total row
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#2ecc71')),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.whitesmoke),
            ('ALIGN', (0, -1), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, -1), (-1, -1), 12),
            ('TOPPADDING', (0, -1), (-1, -1), 12),
            ('BOTTOMPADDING', (0, -1), (-1, -1), 12),
            
            # Grid
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 0.5*inch))
        
        # Footer notes
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.grey,
            alignment=TA_CENTER
        )
        
        footer_text = """
        <b>Nota:</b> Este es un resumen informativo de tu carrito.<br/>
        No constituye una factura ni un comprobante de compra.<br/>
        Para completar tu compra, procede al pago en la plataforma.
        """
        footer = Paragraph(footer_text, footer_style)
        elements.append(footer)
    else:
        # Empty cart message
        empty_msg = Paragraph("Tu carrito está vacío", styles['Normal'])
        elements.append(empty_msg)
    
    # Build PDF
    doc.build(elements)
    
    # Get PDF from buffer
    pdf = buffer.getvalue()
    buffer.close()
    
    return pdf