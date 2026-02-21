from engine_electricity import extract_text_from_pdf

pdf_path = r"C:\My Projects\Pdf_Parser\pdf_folder\electricityBill_12 - December 2025_account_169964295.pdf"   # put ONE PDF here

text = extract_text_from_pdf(pdf_path)

print(text)
