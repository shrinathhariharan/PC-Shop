"""
PDF invoice/receipt generator using fpdf2.
Generates professional digital invoices for completed orders.
"""
import os
from datetime import datetime
from fpdf import FPDF


class InvoicePDF(FPDF):
    """Custom PDF class with header/footer branding."""

    def __init__(self, order: dict):
        super().__init__()
        self.order = order
        self.set_auto_page_break(auto=True, margin=25)

    def header(self):
        # Brand bar
        self.set_fill_color(37, 99, 235)  # Blue #2563EB
        self.rect(0, 0, 210, 12, "F")
        self.set_font("Helvetica", "B", 18)
        self.set_text_color(255, 255, 255)
        self.cell(0, 12, "PC SHOP", align="C", new_x="LMARGIN", new_y="NEXT")
        self.ln(4)

    def footer(self):
        self.set_y(-20)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10,
                  f"Invoice generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}  "
                  f"|  Page {self.page_no()}/{{nb}}",
                  align="C")


def generate_invoice(order: dict, output_dir: str = None) -> str:
    """
    Generate a PDF invoice for the given order dict.

    Parameters
    ----------
    order : dict
        Must contain: order_id, items (list of {name, price, qty}),
        total, date, status.
    output_dir : str, optional
        Directory to save the PDF.  Defaults to ~/Documents.

    Returns
    -------
    str
        Absolute path to the generated PDF.
    """
    if output_dir is None:
        output_dir = os.path.expanduser("~/Documents")
    os.makedirs(output_dir, exist_ok=True)

    pdf = InvoicePDF(order)
    pdf.alias_nb_pages()
    pdf.add_page()

    # ── Invoice title & metadata ──────────────────────────────────────
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(24, 24, 27)
    pdf.cell(0, 10, "INVOICE", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(80, 80, 80)
    pdf.cell(95, 6, f"Order ID:  {order.get('order_id', 'N/A')}")
    pdf.cell(95, 6, f"Date:  {_format_date(order.get('date', ''))}", align="R",
             new_x="LMARGIN", new_y="NEXT")
    pdf.cell(95, 6, f"Status:  {order.get('status', 'N/A')}")
    pdf.cell(95, 6, "", align="R", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    # ── Divider ───────────────────────────────────────────────────────
    pdf.set_draw_color(212, 212, 216)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)

    # ── Table header ──────────────────────────────────────────────────
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(244, 244, 245)
    pdf.set_text_color(24, 24, 27)
    col_widths = [80, 30, 35, 35]
    headers = ["Item", "Qty", "Unit Price", "Subtotal"]
    for w, h in zip(col_widths, headers):
        pdf.cell(w, 8, h, border=0, fill=True, align="C" if h != "Item" else "L")
    pdf.ln()

    # ── Table rows ────────────────────────────────────────────────────
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(50, 50, 50)
    fill = False
    for item in order.get("items", []):
        name = item.get("name", "Unknown")
        qty = item.get("qty", 1)
        price = item.get("price", 0.0)
        subtotal = price * qty

        if fill:
            pdf.set_fill_color(250, 250, 252)
        else:
            pdf.set_fill_color(255, 255, 255)

        # Truncate long names
        display_name = (name[:38] + "..") if len(name) > 40 else name
        pdf.cell(col_widths[0], 7, f"  {display_name}", fill=fill)
        pdf.cell(col_widths[1], 7, str(qty), align="C", fill=fill)
        pdf.cell(col_widths[2], 7, f"${price:,.2f}", align="R", fill=fill)
        pdf.cell(col_widths[3], 7, f"${subtotal:,.2f}", align="R", fill=fill)
        pdf.ln()
        fill = not fill

    # ── Divider ───────────────────────────────────────────────────────
    pdf.ln(2)
    pdf.line(10, pdf.get_y(), 200, pdf.get_y())
    pdf.ln(4)

    # ── Totals ────────────────────────────────────────────────────────
    subtotal = order.get("total", 0.0)
    tax_rate = 0.0825
    tax = round(subtotal * tax_rate, 2)
    grand_total = round(subtotal + tax, 2)

    pdf.set_font("Helvetica", "", 11)
    pdf.cell(145, 7, "Subtotal:", align="R")
    pdf.cell(35, 7, f"${subtotal:,.2f}", align="R", new_x="LMARGIN", new_y="NEXT")

    pdf.cell(145, 7, f"Tax ({tax_rate*100:.2f}%):", align="R")
    pdf.cell(35, 7, f"${tax:,.2f}", align="R", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(1)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(37, 99, 235)
    pdf.cell(145, 9, "TOTAL:", align="R")
    pdf.cell(35, 9, f"${grand_total:,.2f}", align="R", new_x="LMARGIN", new_y="NEXT")

    # ── Thank-you note ────────────────────────────────────────────────
    pdf.ln(12)
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 6, "Thank you for shopping with PC Shop!", align="C",
             new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, "For support, contact support@pcshop.local", align="C")

    # ── Save ──────────────────────────────────────────────────────────
    filename = f"{order.get('order_id', 'invoice')}.pdf"
    filepath = os.path.join(output_dir, filename)
    pdf.output(filepath)
    return filepath


def _format_date(iso_str: str) -> str:
    """Convert ISO date string to human-readable format."""
    try:
        dt = datetime.fromisoformat(iso_str)
        return dt.strftime("%B %d, %Y  %I:%M %p")
    except (ValueError, TypeError):
        return iso_str or "N/A"
