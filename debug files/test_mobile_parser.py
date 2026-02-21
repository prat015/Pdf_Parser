from engine_mobile import parse_mobile_pdf

PDF_PATH = r"C:\My Projects\Pdf_Parser\Pdf_folder\Safaricom Ltd July 2025 Part 2.pdf"
MAPPING_PATH = None   # or "site_mapping.txt"

def main():
    print("=== TEST: Starting mobile parser ===")

    rows = parse_mobile_pdf(PDF_PATH, mapping_path=MAPPING_PATH)

    print(f"\n=== PARSER OUTPUT ===")
    print(f"Total rows parsed: {len(rows)}\n")

    for i, row in enumerate(rows[:5], start=1):
        print(f"--- Row {i} ---")
        for k, v in row.items():
            print(f"{k}: {v}")
        print()

if __name__ == "__main__":
    main()