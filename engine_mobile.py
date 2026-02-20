import pdfplumber
import re

# ---------------------------------------------------------
# Load site mapping
# ---------------------------------------------------------
def load_site_mapping(mapping_path: str) -> dict:
    mapping = {}
    try:
        with open(mapping_path, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 2:
                    subscriber, site_id = parts[0], parts[1]
                    mapping[subscriber] = site_id
    except FileNotFoundError:
        pass
    return mapping


# ---------------------------------------------------------
# Extract text from PDF pages (optimized)
# ---------------------------------------------------------
def extract_page_texts(pdf_path: str, ui_callback=None) -> list[str]:
    texts = []
    start_collecting = False

    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        for idx, page in enumerate(pdf.pages):
            #text = page.extract_text() or ""
            text = page.extract_text_simple() or ""

            if ui_callback:
                percent = int((idx + 1) / total_pages * 50)
                ui_callback(percent)

            # Detect first real invoice page
            if ("Period of Invoice" in text and "Subscriber Number" in text):
                start_collecting = True

            # Collect only invoice pages and everything after
            if start_collecting:
                texts.append(text)

            # Safety limit (optional)
            #if len(texts) > 500:
            #    break
            
    return texts


# ---------------------------------------------------------
# Parse a single invoice page (Page 1 only)
# ---------------------------------------------------------
def parse_mobile_page(text: str, site_mapping: dict | None = None) -> dict | None:
        
    # Reject summary pages
    if "TAX INVOICE SUMMARY" in text:
        return None

    if "Statement Date" in text:
        return None

    # Reject pages without invoice amounts (Page 2 never has these)
    if "Amount Excluding VAT and Excise Duty" not in text:
        return None
   
   # Required markers for Page 1
    required_markers = [
        "Monthly Charge",
        "Total Recurring Charges",
        "Amount Excluding VAT and Excise Duty",
        "EXCISE - 15%",
        "VAT - 16%",
        "Amount Due Ksh"
    ]

    # Reject pages missing any Page‑1 markers (Page 2 never has all of them)
    if not all(marker in text for marker in required_markers):
        return None

    #clean = " ".join(text.split())
    clean = text.replace("\n", " ")
    
    patterns = {
        "invoice_no": r"Invoice Number\s+([A-Z0-9\-]+)",
        "subscriber_no": r"Subscriber Number\s+(\d+)",
        "account_no": r"Customer Number\s+([A-Z0-9]+)",
        "invoice_date": r"Invoice Date\s+(\d{2}/\d{2}/\d{4})",
        "due_date": r"Due Date\s+(\d{2}/\d{2}/\d{4})",
        "amount_excl_tax": r"Amount Excluding VAT and Excise Duty\s+([\d\.]+)",
        "excise_15": r"EXCISE\s*-\s*15%\s+([\d\.]+)",
        "amount_incl_excise": r"Amount Including Excise Duty\s+([\d\.]+)",
        "vat_16": r"VAT\s*-\s*16%\s+([\d\.]+)",
        "total": r"Amount Due Ksh\s+([\d\.]+)",
        "qr_code_date": r"Date:\s*(\d{2}/\d{2}/\d{4})",
        "tis_serial_no": r"TIS Serial No:\s*([A-Z0-9]+)",
        "cu_invoice_no": r"CU Invoice No:\s*([A-Z0-9]+)",
    }

    result = {}

    for key, pattern in patterns.items():
        m = re.search(pattern, clean)
        result[key] = m.group(1) if m else ""

    # Supplier name
    result["supplier_name"] = "Safaricom PLC"

    # Site ID mapping
    subscriber = result.get("subscriber_no", "")
    if site_mapping and subscriber in site_mapping:
        result["site_id"] = site_mapping[subscriber]
    else:
        result["site_id"] = ""

    # If invoice_no missing, skip
    if not result["invoice_no"]:
        return None

    return result


# ---------------------------------------------------------
# Main parser
# ---------------------------------------------------------
def parse_mobile_pdf(pdf_path: str, mapping_path: str | None = None,  ui_callback=None) -> list[dict]:
    #site_mapping = load_site_mapping(mapping_path) if mapping_path else {}
    site_mapping = {}
    texts = extract_page_texts(pdf_path, ui_callback=ui_callback)

    results = []
    total_texts = len(texts)
    for idx, text in enumerate(texts):
        row = parse_mobile_page(text, site_mapping)
        if row:
            results.append(row)

        if ui_callback and total_texts > 0:
            percent = 50 + int((idx + 1) / total_texts * 50)
            ui_callback(percent)


    return results