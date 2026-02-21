import os
import re
import pdfplumber
import pandas as pd

PDF_FOLDER = "pdf_folder"      # change if needed
OUTPUT_EXCEL = "output.xlsx"   # overwrite each run


def extract_text_from_pdf(pdf_path):
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text() or ""
            text += "\n" + page_text
    return text


def extract_fields(text):
    # Extract dates
    dates = re.findall(r"\b(\d{2}/\d{2}/\d{4})\b", text)
    date_of_issue = dates[0] if len(dates) > 0 else ""
    date_due = dates[1] if len(dates) > 1 else ""

    # Extract account number (first 9-digit number)
    acc = re.search(r"\b(\d{9})\b", text)
    account_number = acc.group(1) if acc else ""

    # Extract customer name (two consecutive uppercase lines)
    name_match = re.search(
        r"([A-Z0-9&\s\(\)\.-]+)\n([A-Z0-9&\s\(\)\.-]+)", text
    )
    if name_match:
        customer_name = (name_match.group(1) + " " + name_match.group(2)).strip()
    else:
        customer_name = ""

    # VAT formula
    vat_formula = re.search(r"V\.A\.T\.\s*([\d\.]+\s*x\s*[\d\.]+)", text)
    vat_formula = vat_formula.group(1) if vat_formula else ""

    # VAT amount
    vat_amount = re.search(r"V\.A\.T\.[\s\S]*?([0-9,]+\.\d{2})", text)
    vat_amount = vat_amount.group(1).replace(",", "") if vat_amount else ""

    # Monthly bill
    monthly_bill = re.search(r"Total Monthly Bill[\s\S]*?([0-9,]+\.\d{2})", text)
    monthly_bill_amount = monthly_bill.group(1).replace(",", "") if monthly_bill else ""

    return {
        "account_number": account_number,
        "date_of_issue": date_of_issue,
        "date_due": date_due,
        "customer_name": customer_name,
        "vat_formula": vat_formula,
        "vat_amount": vat_amount,
        "monthly_bill_amount": monthly_bill_amount,
    }

def process_pdfs(pdf_folder, output_excel):
    rows = []

    for filename in os.listdir(pdf_folder):
        if not filename.lower().endswith(".pdf"):
            continue

        pdf_path = os.path.join(pdf_folder, filename)
        print(f"Processing: {filename}")

        text = extract_text_from_pdf(pdf_path)

        with open("debug_output.txt", "w", encoding="utf-8") as f:
            f.write(text)

        fields = extract_fields(text)
        fields["source_file"] = filename  # optional, useful for traceability
        rows.append(fields)
        
      

    if not rows:
        print("No PDFs found or no data extracted.")
        return

    df = pd.DataFrame(rows)
    df.to_excel(output_excel, index=False)
    print(f"Done. Written {len(rows)} rows to {output_excel}")


if __name__ == "__main__":
    process_pdfs(PDF_FOLDER, OUTPUT_EXCEL)