from license_manager import save_license_file

def make_license(machine_id: str, license_key: str, expiry: str):
    data = {
        "license_key": license_key,
        "expiry": expiry,          # "YYYY-MM-DD"
        "machine_id": machine_id,
    }
    save_license_file(data)
    print("License file created at:", __import__("license_manager").license_file_path())

if __name__ == "__main__":
    # Fill these from client info
    client_machine_id = "fcc4bcc6-6f68-4499-94f3-48d280010afa"
    license_key = "NAVYA-2025-CLIENT1-AB39X"
    expiry = "2026-02-22"

    make_license(client_machine_id, license_key, expiry)