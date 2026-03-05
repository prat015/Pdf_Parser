import os
import json
import base64
import datetime
import winreg

# ---------- CONFIG ----------
SECRET_KEY = "NAVYA2025"  # keep private, don't share with client

DEVELOPER_WHITELIST = {
    # Put YOUR machine ID here after step 4
     "1e52778e-075c-47fd-ae4c-cf751dad4b90",
}

APP_FOLDER_NAME = "BillCore"   # or your app name
LICENSE_FILE_NAME = "license.dat"
# ----------------------------


def get_machine_id():
    try:
        registry_path = r"SOFTWARE\Microsoft\Cryptography"
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path)
        value, _ = winreg.QueryValueEx(key, "MachineGuid")
        return value
    except Exception as e:
        print("Error reading MachineGuid:", e)
        return None


def license_file_path():
    folder = os.path.join(os.getenv("LOCALAPPDATA"), APP_FOLDER_NAME)
    os.makedirs(folder, exist_ok=True)
    print("License folder:", folder)
    return os.path.join(folder, LICENSE_FILE_NAME)


def encrypt(text: str) -> str:
    xored = "".join(
        chr(ord(c) ^ ord(SECRET_KEY[i % len(SECRET_KEY)]))
        for i, c in enumerate(text)
    )
    return base64.b64encode(xored.encode()).decode()


def decrypt(encoded: str) -> str:
    decoded = base64.b64decode(encoded).decode()
    return "".join(
        chr(ord(c) ^ ord(SECRET_KEY[i % len(SECRET_KEY)]))
        for i, c in enumerate(decoded)
    )


def save_license_file(license_data: dict):
    encrypted = encrypt(json.dumps(license_data))
    with open(license_file_path(), "w") as f:
        f.write(encrypted)


def load_license_file() -> dict | None:
    try:
        with open(license_file_path(), "r") as f:
            decrypted = decrypt(f.read())
            return json.loads(decrypted)
    except Exception:
        return None


def validate_license() -> tuple[bool, str]:
    machine_id = get_machine_id()

    # Developer bypass
    if machine_id in DEVELOPER_WHITELIST:
        return True, "Developer Mode"

    lic = load_license_file()
    if not lic:
        return False, "License file missing"

    # Machine binding
    if lic.get("machine_id") != machine_id:
        return False, "License not valid for this machine"

    # Expiry check
    try:
        today = datetime.date.today()
        expiry = datetime.date.fromisoformat(lic["expiry"])
    except Exception:
        return False, "Invalid license data"

    if today > expiry:
        return False, "License expired"

    return True, "OK"