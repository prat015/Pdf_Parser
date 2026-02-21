import pdfplumber
import re

pdf_path = "Safaricom Ltd July 2025 Part 2.pdf"

invoice_numbers = set()

with pdfplumber.open(pdf_path) as pdf:
    for page_no, page in enumerate(pdf.pages, start=1):

        if page_no < 89:  # since you said TAX Invoice starts at 89
            continue

        text = page.extract_text_simple() or ""

        # Skip summary pages
        if "TAX INVOICE SUMMARY" in text:
            continue

        # Only pages containing Monthly Charge
        if "Monthly Charge" in text:

            match = re.search(r"Invoice Number\s+([A-Z0-9\-]+)", text)
            if match:
                invoice_numbers.add(match.group(1))

print("Unique invoices based on Monthly Charge:", len(invoice_numbers))