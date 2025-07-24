from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from datetime import datetime
import qrcode
import io
import os

def format_currency(amount):
    return f"Ksh. {amount:,.2f}"

def add_paid_watermark(canvas, doc):
    canvas.saveState()
    canvas.setFont('Helvetica-Bold', 100)
    canvas.setFillColorRGB(0.85, 0.85, 0.85, alpha=0.2)
    canvas.translate(300, 400)
    canvas.rotate(45)
    canvas.drawCentredString(0, 0, "PAID")
    canvas.restoreState()

def generate_qr_code(data):
    qr = qrcode.QRCode(box_size=4, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf

def add_company_header(elements, styles, branch_info=None, doc_type="Document", doc_number=None):
    logo_path = os.path.join(os.getcwd(), "logo.png")
    if os.path.exists(logo_path):
        img = Image(logo_path, width=3.5*cm, height=3.5*cm)
    else:
        img = Paragraph("", styles['Normal'])

    header_right = []
    header_right.append(Paragraph("<b>Magen Fuel Enterprise</b>", styles['Title']))

    if branch_info:
        header_right.append(Paragraph(branch_info["name"], styles['Normal']))
        header_right.append(Paragraph(branch_info["address"], styles['Normal']))
        header_right.append(Paragraph(branch_info["contacts"], styles['Normal']))
    else:
        header_right.append(Paragraph("P.O Box 12345-00100, Nairobi, Kenya", styles['Normal']))
        header_right.append(Paragraph("Tel: +254 700 123456 | Email: info@magenfuel.co.ke", styles['Normal']))

    header_table = Table(
        [[img, header_right]],
        colWidths=[4.5*cm, 11.5*cm]
    )

    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (1, 0), (-1, -1), 'LEFT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 1),
        ('RIGHTPADDING', (0, 0), (-1, -1), 1),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
    ]))

    elements.append(header_table)
    elements.append(Spacer(1, 12))

def generate_invoice_pdf_document(invoice_number, sale_data, filename, paid=False, branch_info=None, qr_data=None, include_t_and_c=False):
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    if qr_data is None:
        qr_data = f"{invoice_number}-{sale_data['customer_name']}-{sale_data['date']}"

    add_company_header(elements, styles, branch_info, "Invoice", invoice_number)

    elements.append(Paragraph(f"<b>Customer:</b> {sale_data['customer_name']}", styles['Normal']))
    elements.append(Paragraph(f"<b>Transaction Date:</b> {sale_data['date']}", styles['Normal']))
    elements.append(Spacer(1, 12))

    data = [
        ["Product", "Quantity (Litres)", "Price per Unit", "Total"],
        [
            sale_data['product'],
            str(sale_data['quantity']),
            format_currency(float(sale_data['price'])),
            format_currency(float(sale_data['total']))
        ]
    ]

    table = Table(data, colWidths=[140, 100, 120, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#0A4D68")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 24))

    signature_style = ParagraphStyle(name="Signature", fontSize=12, spaceAfter=20)
    elements.append(Paragraph("Customer Signature: ___________________________", signature_style))
    elements.append(Paragraph("Authorized Signature: ___________________________", signature_style))
    elements.append(Spacer(1, 12))

    if qr_data:
        qr_buf = generate_qr_code(qr_data)
        qr_img = Image(qr_buf, width=4*cm, height=4*cm)
        qr_img.hAlign = 'RIGHT'
        elements.append(qr_img)
        elements.append(Spacer(1, 12))

    footer_style = ParagraphStyle(name="Footer", alignment=1, fontSize=10, textColor=colors.grey)
    elements.append(Paragraph("Thank you for your business.", footer_style))
    elements.append(Paragraph("Magen Fuel Enterprise | Reliable. Efficient. Affordable.", footer_style))

    if paid:
        doc.build(elements, onFirstPage=add_paid_watermark)
    else:
        doc.build(elements)

    if include_t_and_c:
        t_and_c_doc = SimpleDocTemplate(filename.replace(".pdf", "_TnC.pdf"), pagesize=A4)
        t_and_c_elements = []
        t_and_c_elements.append(PageBreak())
        t_and_c_elements.append(Paragraph("Terms and Conditions", styles['Title']))
        t_and_c_elements.append(Spacer(1, 12))
        t_and_c_text = """
        1. Payment is due within 7 days unless otherwise agreed.
        2. Goods once delivered are non-refundable unless defective.
        3. Magen Fuel Enterprise is not liable for delays caused by circumstances beyond control.
        4. Disputes should be reported within 48 hours of delivery.
        5. For support, contact info@magenfuel.co.ke.
        """
        for line in t_and_c_text.strip().split("\n"):
            t_and_c_elements.append(Paragraph(line.strip(), styles['Normal']))
            t_and_c_elements.append(Spacer(1, 6))
        t_and_c_doc.build(t_and_c_elements)

def generate_delivery_note_pdf_document(delivery_note_number, sale_data, filename, branch_info=None, qr_data=None):
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    if qr_data is None:
        qr_data = f"{delivery_note_number}-{sale_data['customer_name']}-{sale_data['date']}"

    add_company_header(elements, styles, branch_info, "Delivery Note", delivery_note_number)

    elements.append(Paragraph(f"<b>Customer:</b> {sale_data['customer_name']}", styles['Normal']))
    elements.append(Paragraph(f"<b>Transaction Date:</b> {sale_data['date']}", styles['Normal']))
    elements.append(Spacer(1, 12))

    data = [
        ["Product", "Quantity (Litres)"],
        [sale_data['product'], str(sale_data['quantity'])]
    ]

    table = Table(data, colWidths=[250, 250])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#14532d")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 24))

    signature_style = ParagraphStyle(name="Signature", fontSize=12, spaceAfter=20)
    elements.append(Paragraph("Customer Signature: ___________________________", signature_style))
    elements.append(Paragraph("Driver Signature: ___________________________", signature_style))
    elements.append(Spacer(1, 12))

    if qr_data:
        qr_buf = generate_qr_code(qr_data)
        qr_img = Image(qr_buf, width=4*cm, height=4*cm)
        qr_img.hAlign = 'RIGHT'
        elements.append(qr_img)
        elements.append(Spacer(1, 12))

    footer_style = ParagraphStyle(name="Footer", alignment=1, fontSize=10, textColor=colors.grey)
    elements.append(Paragraph("Goods delivered in good condition.", footer_style))
    elements.append(Paragraph("Magen Fuel Enterprise | Reliable. Efficient. Affordable.", footer_style))

    doc.build(elements)

# New: Generate LPO PDF document
def generate_lpo_pdf_document(lpo_number, lpo_data, filename, branch_info=None, qr_data=None):
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    if qr_data is None:
        qr_data = f"{lpo_number}-{lpo_data['customer_name']}-{lpo_data['date']}"

    add_company_header(elements, styles, branch_info, "Local Purchase Order", lpo_number)

    elements.append(Paragraph(f"<b>Customer:</b> {lpo_data['customer_name']}", styles['Normal']))
    elements.append(Paragraph(f"<b>Transaction Date:</b> {lpo_data['date']}", styles['Normal']))
    elements.append(Spacer(1, 12))

    data = [["Product", "Quantity (Litres)", "Price per Unit", "Total"]]
    for item in lpo_data['items']:
        data.append([
            item['product'],
            str(item['quantity']),
            format_currency(float(item['price'])),
            format_currency(float(item['total']))
        ])

    table = Table(data, colWidths=[140, 100, 120, 100])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#5B21B6")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 24))

    signature_style = ParagraphStyle(name="Signature", fontSize=12, spaceAfter=20)
    elements.append(Paragraph("Authorized Signature: ___________________________", signature_style))
    elements.append(Paragraph("Customer Signature: ___________________________", signature_style))
    elements.append(Spacer(1, 12))

    if qr_data:
        qr_buf = generate_qr_code(qr_data)
        qr_img = Image(qr_buf, width=4*cm, height=4*cm)
        qr_img.hAlign = 'RIGHT'
        elements.append(qr_img)
        elements.append(Spacer(1, 12))

    footer_style = ParagraphStyle(name="Footer", alignment=1, fontSize=10, textColor=colors.grey)
    elements.append(Paragraph("Thank you for your business.", footer_style))
    elements.append(Paragraph("Magen Fuel Enterprise | Reliable. Efficient. Affordable.", footer_style))

    doc.build(elements)
