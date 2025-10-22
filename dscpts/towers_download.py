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
    "https://data.fcc.gov/download/pub/uls/complete/r_tower.zip",
    "ftp://wirelessftp.fcc.gov/pub/uls/complete/r_tower.zip"
]

script_dir = os.path.dirname(os.path.abspath(__file__))
zip_path = os.path.join(script_dir, "tower.zip")
json_path = os.path.join(script_dir, "tower_clean.json")

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
# Download the ZIP
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
# Extract EN.dat only
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
    print("No EN.dat found in ZIP.")
    exit(1)

data_file = os.path.join(script_dir, en_file)
print(f"Processing {os.path.basename(data_file)}")

# ---------------------------
# Parse EN.dat with proper field alignment
# ---------------------------
records = []

with open(data_file, "r", encoding="latin-1") as f:
    for line in f:
        parts = [p.strip() for p in line.strip().split("|")]

        record = {
            "record_type": parts[0] if len(parts) > 0 else "",
            "registration_type": parts[1] if len(parts) > 1 else "",
            "registration_number": parts[2] if len(parts) > 2 else "",
            "ebf_number": parts[3] if len(parts) > 3 else "",
            "unique_id": parts[4] if len(parts) > 4 else "",
            "status_code": parts[5] if len(parts) > 5 else "",
            "company_name": parts[10] if len(parts) > 10 else "",
            "phone": parts[14] if len(parts) > 14 else "",
            "street_address": parts[17] if len(parts) > 17 else "",
            "city": parts[20] if len(parts) > 20 else "",
            "state": parts[21] if len(parts) > 21 else "",
            "zip_code": parts[22] if len(parts) > 22 else "",
            "contact_name": parts[23] if len(parts) > 23 else ""
        }

        records.append(record)

# ---------------------------
# Ask about compression
# ---------------------------
compress = input("Do you want to gzip-compress the JSON output? (y/n): ").strip().lower()

if compress == "y":
    json_path += ".gz"
    with gzip.open(json_path, "wt", encoding="utf-8") as f:
        for rec in records:
            json.dump(rec, f, ensure_ascii=False, separators=(",", ":"))
            f.write("\n")
else:
    with open(json_path, "w", encoding="utf-8") as f:
        for rec in records:
            json.dump(rec, f, ensure_ascii=False, separators=(",", ":"))
            f.write("\n")

print(f"Processed {len(records)} tower records saved to {json_path}")
