import re
import pdfplumber
from datetime import datetime


def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text += "\n" + page_text
    return text


def parse_fields(text):

    # -----------------------------
    # ACCOUNT NUMBER (first 9-digit number)
    # -----------------------------
    acc = re.search(r"\b(\d{9})\b", text)
    account_no = acc.group(1) if acc else ""

    # -----------------------------
    # DATES (first two DD/MM/YYYY)
    # -----------------------------
    #dates = re.findall(r"\b(\d{2}/\d{2}/\d{4})\b", text)
    #date_of_issue = dates[0] if len(dates) > 0 else ""
    #date_due = dates[1] if len(dates) > 1 else ""

   # Extract all dates in the order they appear
    all_dates = re.findall(r"\b(\d{2}/\d{2}/\d{4})\b", text)

    date_of_issue = all_dates[0] if len(all_dates) > 0 else ""
    date_due = all_dates[2] if len(all_dates) > 2 else ""



    # -----------------------------
    # INVOICE NUMBER (first alphanumeric 12–20 chars)
    # -----------------------------
    invoice_number = ""
    inv = re.findall(r"\b([A-Z0-9]{10,20})\b", text)
    if inv:
        # pick the one that looks like KPLC invoice
        for x in inv:
            if x[0].isdigit() and any(c.isalpha() for c in x):
                invoice_number = x
                break

    # -----------------------------
    # QR CODE (longest 18–30 digit number)
    # -----------------------------
    qr = re.findall(r"\b(\d{15,30})\b", text)
    qr_code = qr[0] if qr else ""

    # -----------------------------
    # BILLING FIELDS
    # -----------------------------
    def find(pattern):
        m = re.search(pattern, text, re.IGNORECASE)
        return m.group(1).strip() if m else ""

    total_energy = find(r"Total Energy[\s\S]{0,40}?([\d,]+\.\d{2})")
    total_levies = find(r"Total Levies and Adjustments[\s\S]{0,40}?([\d,]+\.\d{2})")
    rounding_adjustment = find(r"Rounding Adjustment[\s\S]{0,40}?([\d,\-]+\.\d{2})")
    
    vat_match = re.search(r"V\.A\.T\.[\s\S]*?([0-9,]+\.\d{2})(?!.*[0-9,]+\.\d{2})", text)
    vat = vat_match.group(1).replace(",", "") if vat_match else ""



    total_monthly_bill = find(r"Total Monthly Bill[\s\S]{0,40}?([\d,]+\.\d{2})")

    return {
        "supplier_name": "Kenya Power Ltd",
        "account_no": account_no,
        "site_id": "",
        "date_of_issue": date_of_issue,
        "due_date": date_due,
        "qr_code": qr_code,
        "invoice_number": invoice_number,
        "total_monthly_bill": total_monthly_bill.replace(",", ""),
        "vat": vat.replace(",", ""),
        "total_energy": total_energy.replace(",", ""),
        "total_levies": total_levies.replace(",", ""),
        "rounding_adjustment": rounding_adjustment.replace(",", "")
    }

def parse_electricity_pdf(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    return parse_fields(text)
