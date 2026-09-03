import io
from django.core.files.base import ContentFile
from django.utils import timezone
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

class PDFInvoiceGenerator:
    """
    Generates CineVerse branded PDF tax invoices using ReportLab.
    """
    @classmethod
    def generate_pdf(cls, invoice):
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'InvoiceTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#E50914'),
            spaceAfter=6
        )
        body_style = styles['Normal']
        body_style.fontSize = 10
        body_style.leading = 14
        
        elements = []
        
        # 1. Header Banner
        header_data = [
            [Paragraph("<b>CINEVERSE OTT MEDIA INC.</b>", title_style), Paragraph(f"<b>TAX INVOICE</b><br/>#{invoice.invoice_number}", body_style)],
            [Paragraph("100 CineVerse Blvd, Suite 800<br/>Los Angeles, CA 90028<br/>support@cineverse.io", body_style),
             Paragraph(f"<b>Date:</b> {invoice.issued_at.strftime('%B %d, %Y')}<br/><b>Status:</b> PAID<br/><b>Payment Ref:</b> {invoice.transaction.transaction_reference[:16]}", body_style)]
        ]
        header_table = Table(header_data, colWidths=[320, 210])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 20))
        
        # 2. Billed To
        elements.append(Paragraph("<b>BILLED TO:</b>", styles['Heading4']))
        bill_to_text = f"<b>{invoice.billing_name}</b><br/>{invoice.billing_email}<br/>{invoice.billing_address}"
        elements.append(Paragraph(bill_to_text, body_style))
        elements.append(Spacer(1, 25))
        
        # 3. Line Items Table
        sub_name = invoice.transaction.subscription.plan.name if invoice.transaction.subscription else "CineVerse VIP Streaming Plan"
        table_data = [
            [Paragraph("<b>DESCRIPTION</b>", body_style), Paragraph("<b>QTY</b>", body_style), Paragraph("<b>UNIT PRICE</b>", body_style), Paragraph("<b>AMOUNT</b>", body_style)],
            [Paragraph(f"<b>{sub_name}</b><br/>Unlimited 4K HDR Streaming & Downloads", body_style), "1", f"${invoice.subtotal}", f"${invoice.subtotal}"],
            ["", "", Paragraph("<b>Subtotal:</b>", body_style), f"${invoice.subtotal}"],
            ["", "", Paragraph("<b>Tax (0%):</b>", body_style), f"${invoice.tax_amount}"],
            ["", "", Paragraph("<b>TOTAL PAID:</b>", styles['Heading4']), Paragraph(f"<b>${invoice.total_amount} {invoice.currency}</b>", styles['Heading4'])],
        ]
        
        item_table = Table(table_data, colWidths=[280, 50, 100, 100])
        item_table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#161922')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
            ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
            ('GRID', (0,0), (-1,1), 0.5, colors.HexColor('#DDDDDD')),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
            ('TOPPADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(item_table)
        elements.append(Spacer(1, 40))
        
        # 4. Footer Note
        elements.append(Paragraph("Thank you for subscribing to CineVerse. Happy Streaming!", styles['Italic']))
        
        # Build Document
        doc.build(elements)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        
        filename = f"invoice_{invoice.invoice_number}.pdf"
        invoice.pdf_document.save(filename, ContentFile(pdf_bytes), save=True)
        return invoice.pdf_document
