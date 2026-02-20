import os
from engine_electricity import extract_text_from_pdf, parse_fields
import openpyxl

def process_folder(folder_path, output_excel):
    import os
    from engine_electricity import extract_text_from_pdf, parse_fields
    import openpyxl

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Invoice Data"

    headers = [
        "Supplier Name",
        "Account No",
        "Site ID",
        "Date of Issue",
        "Due Date",
        "QR Code CU Invoice No",
        "Invoice Number",
        "Total Monthly Bill",
        "V.A.T.",
        "Total Energy",
        "Total Levies and Adjustments",
        "Rounding Adjustments"
    ]
    ws.append(headers)

    for file in os.listdir(folder_path):
        if file.lower().endswith(".pdf"):
            pdf_path = os.path.join(folder_path, file)
            print(f"Processing: {pdf_path}")

            text = extract_text_from_pdf(pdf_path)
            data = parse_fields(text)

            ws.append([
                data["supplier_name"],
                data["account_no"],
                data["site_id"],
                data["date_of_issue"],
                data["due_date"],
                data["qr_code"],
                data["invoice_number"],
                data["total_monthly_bill"],
                data["vat"],
                data["total_energy"],
                data["total_levies"],
                data["rounding_adjustment"]
            ])

    wb.save(output_excel)
    print(f"\nDone! Excel saved at: {output_excel}")
