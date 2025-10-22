import requests
from ftplib import FTP
import os
import zipfile
import json
import gzip

# ---------------------------
# Config
# ---------------------------
urls = [
    "https://data.fcc.gov/download/pub/uls/complete/l_aircr.zip",
    "ftp://wirelessftp.fcc.gov/pub/uls/complete/l_aircr.zip"
]

script_dir = os.path.dirname(os.path.abspath(__file__))
zip_path = os.path.join(script_dir, "aircr.zip")
json_path = os.path.join(script_dir, "aircr_clean.json")

FIELDS = [
    "record_type", "unique_system_identifier", "uls_file_number", "ebf_number",
    "call_sign", "status_code", "status_date", "name", "first_name",
    "middle_initial", "last_name", "suffix", "phone", "fax", "email",
    "street_address", "city", "state", "zip_code", "po_box", "attn_line",
    "frn", "registration_number", "license_status", "reserved1", "reserved2",
    "reserved3", "reserved4"
]

# ---------------------------
# Download helpers
# ---------------------------
def download_http(url):
    print(f"Trying HTTPS download from {url}")
    r = requests.get(url, stream=True, timeout=60)
    r.raise_for_status()
    with open(zip_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
    print("Download complete")
    return True

def download_ftp(url):
    print(f"Trying FTP download from {url}")
    parts = url.replace("ftp://", "").split("/", 1)
    host = parts[0]
    path = parts[1]
    ftp = FTP(host, timeout=60)
    ftp.login()
    with open(zip_path, "wb") as f:
        ftp.retrbinary(f"RETR {path}", f.write)
    ftp.quit()
    print("Download complete")
    return True

# ---------------------------
# Download file
# ---------------------------
for u in urls:
    try:
        if u.startswith("ftp://"):
            if download_ftp(u):
                break
        else:
            if download_http(u):
                break
    except Exception as e:
        print(f"Failed using {u}: {e}")
        if os.path.exists(zip_path):
            os.remove(zip_path)
else:
    print("All download attempts failed.")
    exit(1)

# ---------------------------
# Extract only EN.dat and delete others
# ---------------------------
with zipfile.ZipFile(zip_path, "r") as z:
    en_file = None
    for f in z.namelist():
        if f.lower().startswith("en") and f.lower().endswith(".dat"):
            en_file = f
            z.extract(f, script_dir)
        else:
            print(f"Skipping {f} from extraction")
os.remove(zip_path)

if not en_file:
    print("No EN.dat file found in ZIP.")
    exit(1)

data_file = os.path.join(script_dir, en_file)
print(f"Using {os.path.basename(data_file)} for processing")

# ---------------------------
# Process Marine dataset with FRN fix
# ---------------------------
calls = {}
with open(data_file, "r", encoding="latin-1") as infile:
    for line in infile:
        parts = [p.strip() for p in line.strip().split("|")]
        if len(parts) < len(FIELDS):
            parts += [""] * (len(FIELDS) - len(parts))
        record = dict(zip(FIELDS, parts))

        call = record.get("call_sign", "")
        if not call:
            continue

        name = record.get("name") or f"{record.get('first_name','')} {record.get('last_name','')}".strip()
        state = record.get("state", "")
        city = record.get("city", "")
        zip_code = record.get("zip_code", "")[:5]

        # FRN fix: skip placeholder '000' if present
        frn_index = FIELDS.index("frn")
        frn = parts[frn_index]
        if frn == "000" and len(parts) > frn_index + 1:
            next_field = parts[frn_index + 1].strip()
            if next_field and next_field != "000":
                frn = next_field

        calls[call] = {
            "call_sign": call,
            "name": name.strip(),
            "street_address": record.get("street_address", "").strip(),
            "city": city.strip(),
            "state": state.strip(),
            "zip": zip_code.strip(),
            "frn": frn
        }

# ---------------------------
# Ask user about compression
# ---------------------------
compress = input("Do you want to gzip-compress the JSON output? (y/n): ").strip().lower()

if compress == "y":
    json_path += ".gz"
    with gzip.open(json_path, "wt", encoding="utf-8") as f:
        for rec in calls.values():
            json.dump(rec, f, ensure_ascii=False, separators=(",", ":"))
            f.write("\n")
else:
    with open(json_path, "w", encoding="utf-8") as f:
        for rec in calls.values():
            json.dump(rec, f, ensure_ascii=False, separators=(",", ":"))
            f.write("\n")

print(f"Processed {len(calls)} unique Marine callsigns saved to {json_path}")
