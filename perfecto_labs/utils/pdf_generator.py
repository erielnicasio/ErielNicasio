"""
Generador de facturas en PDF para Perfecto Labs.
Soporta formato estandar y formato para impresora termica 80mm.
"""

import os
from datetime import datetime

from fpdf import FPDF


class InvoicePDF(FPDF):
    """PDF de factura estandar tamano carta."""

    def __init__(self, empresa="Perfecto Labs"):
        super().__init__()
        self.empresa = empresa

    def header(self):
        self.set_font("Helvetica", "B", 16)
        self.cell(0, 10, self.empresa, ln=True, align="C")
        self.set_font("Helvetica", "", 9)
        self.cell(0, 5, "Sistema de Gestion Educativa", ln=True, align="C")
        self.cell(0, 5, "Tel: (809) 555-0100 | info@perfectolabs.edu.do", ln=True, align="C")
        self.line(10, self.get_y() + 3, 200, self.get_y() + 3)
        self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Pagina {self.page_no()}/{{nb}}", align="C")


class ThermalPDF(FPDF):
    """PDF para impresora termica de 80mm (ancho ~72mm util)."""

    def __init__(self, empresa="Perfecto Labs"):
        super().__init__(format=(80, 200))
        self.empresa = empresa

    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 5, self.empresa, ln=True, align="C")
        self.set_font("Helvetica", "", 7)
        self.cell(0, 4, "Tel: (809) 555-0100", ln=True, align="C")
        self.line(3, self.get_y() + 1, 77, self.get_y() + 1)
        self.ln(3)


def generate_invoice_pdf(pedido, items, output_dir=None, thermal=False):
    """
    Genera un PDF de factura.

    Args:
        pedido: dict con datos del pedido.
        items: lista de dicts con items del pedido.
        output_dir: directorio donde guardar el PDF.
        thermal: True para formato 80mm, False para carta.

    Returns:
        Ruta completa del archivo PDF generado.
    """
    if output_dir is None:
        output_dir = os.path.join(os.path.expanduser("~"), "PerfectoLabs_Facturas")
    os.makedirs(output_dir, exist_ok=True)

    numero = pedido.get("numero_pedido", "SN")
    fecha = pedido.get("fecha_creacion", datetime.now().strftime("%Y-%m-%d %H:%M"))
    if hasattr(fecha, "strftime"):
        fecha = fecha.strftime("%Y-%m-%d %H:%M")
    cliente = pedido.get("cliente_nombre", "Cliente General")

    if thermal:
        pdf = ThermalPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=False)

        pdf.set_font("Helvetica", "B", 8)
        pdf.cell(0, 4, f"Factura: {numero}", ln=True)
        pdf.set_font("Helvetica", "", 7)
        pdf.cell(0, 4, f"Fecha: {fecha}", ln=True)
        pdf.cell(0, 4, f"Cliente: {cliente}", ln=True)
        pdf.ln(2)

        pdf.line(3, pdf.get_y(), 77, pdf.get_y())
        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 7)
        pdf.cell(30, 4, "Articulo", border=0)
        pdf.cell(10, 4, "Cant", border=0, align="C")
        pdf.cell(15, 4, "Precio", border=0, align="R")
        pdf.cell(15, 4, "Subtot", border=0, align="R")
        pdf.ln()
        pdf.line(3, pdf.get_y(), 77, pdf.get_y())
        pdf.ln(1)

        pdf.set_font("Helvetica", "", 7)
        for item in items:
            desc = item.get("descripcion", "")[:20]
            cant = item.get("cantidad", 1)
            precio = item.get("precio_unitario", 0)
            sub = item.get("subtotal", 0)
            pdf.cell(30, 4, desc, border=0)
            pdf.cell(10, 4, str(cant), border=0, align="C")
            pdf.cell(15, 4, f"${precio:.2f}", border=0, align="R")
            pdf.cell(15, 4, f"${sub:.2f}", border=0, align="R")
            pdf.ln()

        pdf.ln(2)
        pdf.line(3, pdf.get_y(), 77, pdf.get_y())
        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 8)
        pdf.cell(40, 4, "Subtotal:", border=0)
        pdf.cell(30, 4, f"${pedido.get('subtotal', 0):.2f}", border=0, align="R")
        pdf.ln()
        pdf.cell(40, 4, "ITBIS (18%):", border=0)
        pdf.cell(30, 4, f"${pedido.get('impuesto', 0):.2f}", border=0, align="R")
        pdf.ln()
        pdf.set_font("Helvetica", "B", 9)
        pdf.cell(40, 5, "TOTAL:", border=0)
        pdf.cell(30, 5, f"${pedido.get('total', 0):.2f}", border=0, align="R")
        pdf.ln(4)

        pdf.set_font("Helvetica", "", 7)
        pdf.cell(0, 4, "Gracias por su compra!", ln=True, align="C")
        pdf.cell(0, 4, "Perfecto Labs", ln=True, align="C")
    else:
        pdf = InvoicePDF()
        pdf.alias_nb_pages()
        pdf.add_page()

        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(95, 7, f"Factura No: {numero}")
        pdf.cell(95, 7, f"Fecha: {fecha}", align="R", ln=True)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(0, 7, f"Cliente: {cliente}", ln=True)
        metodo = pedido.get("metodo_pago", "N/A")
        pdf.cell(0, 7, f"Metodo de Pago: {metodo}", ln=True)
        pdf.ln(5)

        pdf.set_fill_color(30, 41, 59)
        pdf.set_text_color(255, 255, 255)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(80, 8, " Descripcion", border=1, fill=True)
        pdf.cell(25, 8, "Cantidad", border=1, fill=True, align="C")
        pdf.cell(35, 8, "Precio Unit.", border=1, fill=True, align="C")
        pdf.cell(35, 8, "Subtotal", border=1, fill=True, align="C")
        pdf.ln()
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Helvetica", "", 10)

        for i, item in enumerate(items):
            fill = i % 2 == 0
            if fill:
                pdf.set_fill_color(241, 245, 249)
            desc = item.get("descripcion", "")
            cant = item.get("cantidad", 1)
            precio = item.get("precio_unitario", 0)
            sub = item.get("subtotal", 0)
            pdf.cell(80, 7, f" {desc}", border=1, fill=fill)
            pdf.cell(25, 7, str(cant), border=1, fill=fill, align="C")
            pdf.cell(35, 7, f"RD${precio:,.2f}", border=1, fill=fill, align="C")
            pdf.cell(35, 7, f"RD${sub:,.2f}", border=1, fill=fill, align="C")
            pdf.ln()

        pdf.ln(3)
        x_label = 120
        x_val = 155
        w_label = 35
        w_val = 35
        pdf.set_x(x_label)
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(w_label, 7, "Subtotal:", border=0, align="R")
        pdf.cell(w_val, 7, f"RD${pedido.get('subtotal', 0):,.2f}", border=0, align="R")
        pdf.ln()
        pdf.set_x(x_label)
        pdf.cell(w_label, 7, "ITBIS (18%):", border=0, align="R")
        pdf.cell(w_val, 7, f"RD${pedido.get('impuesto', 0):,.2f}", border=0, align="R")
        pdf.ln()
        pdf.set_x(x_label)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(w_label, 8, "TOTAL:", border="T", align="R")
        pdf.cell(w_val, 8, f"RD${pedido.get('total', 0):,.2f}", border="T", align="R")

    filename = f"Factura_{numero}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
    filepath = os.path.join(output_dir, filename)
    pdf.output(filepath)
    return filepath
