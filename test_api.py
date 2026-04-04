import requests
import base64
import os
from pathlib import Path

BASE_URL = "http://127.0.0.1:8000/api/document-analyze"
API_KEY = "documind123"

HEADERS = {
    "x-api-key": API_KEY,
    "Content-Type": "application/json"
}

def encode_file(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def find_first_file(folder, extensions):
    for file in os.listdir(folder):
        if file.lower().endswith(extensions):
            return os.path.join(folder, file)
    return None

def print_response(response):
    try:
        data = response.json()
    except Exception:
        print("❌ Could not parse JSON response")
        print("Raw response:", response.text)
        return

    print("Status Code:", response.status_code)
    print("Response:")
    print(data)

def test_case(name, payload, headers=HEADERS):
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"{'='*60}")
    try:
        response = requests.post(BASE_URL, json=payload, headers=headers, timeout=60)
        print_response(response)
    except Exception as e:
        print("❌ Error:", str(e))

# Project paths
BASE_DIR = Path(__file__).resolve().parent
TEST_DIR = BASE_DIR / "test_files"

if not TEST_DIR.exists():
    print(f"❌ test_files folder not found: {TEST_DIR}")
    exit()

# Auto-detect files
pdf_path = find_first_file(TEST_DIR, (".pdf",))
docx_path = find_first_file(TEST_DIR, (".docx",))
img_path = find_first_file(TEST_DIR, (".jpg", ".jpeg", ".png"))

print("\n📂 Detected Test Files:")
print("PDF :", pdf_path if pdf_path else "❌ Not found")
print("DOCX:", docx_path if docx_path else "❌ Not found")
print("IMG :", img_path if img_path else "❌ Not found")

# Encode files safely
pdf_b64 = encode_file(pdf_path) if pdf_path else None
docx_b64 = encode_file(docx_path) if docx_path else None
img_b64 = encode_file(img_path) if img_path else None

# ✅ TEST 1 — PDF
if pdf_b64:
    test_case("PDF ANALYSIS", {
        "fileName": os.path.basename(pdf_path),
        "fileType": "pdf",
        "fileBase64": pdf_b64
    })
else:
    print("\n⚠️ Skipping PDF test (no PDF file found)")

# ✅ TEST 2 — DOCX
if docx_b64:
    test_case("DOCX ANALYSIS", {
        "fileName": os.path.basename(docx_path),
        "fileType": "docx",
        "fileBase64": docx_b64
    })
else:
    print("\n⚠️ Skipping DOCX test (no DOCX file found)")

# ✅ TEST 3 — IMAGE
if img_b64:
    test_case("IMAGE ANALYSIS", {
        "fileName": os.path.basename(img_path),
        "fileType": "image",
        "fileBase64": img_b64
    })
else:
    print("\n⚠️ Skipping IMAGE test (no image file found)")

# ❌ TEST 4 — WRONG API KEY
if pdf_b64:
    test_case("INVALID API KEY", {
        "fileName": os.path.basename(pdf_path),
        "fileType": "pdf",
        "fileBase64": pdf_b64
    }, headers={
        "x-api-key": "wrongkey",
        "Content-Type": "application/json"
    })

# ❌ TEST 5 — UNSUPPORTED TYPE
test_case("UNSUPPORTED FILE TYPE", {
    "fileName": "file.txt",
    "fileType": "txt",
    "fileBase64": "dGVzdA=="
})

# ❌ TEST 6 — EMPTY BASE64
test_case("EMPTY FILE", {
    "fileName": "empty.pdf",
    "fileType": "pdf",
    "fileBase64": ""
})

# ❌ TEST 7 — INVALID BASE64
test_case("BROKEN BASE64", {
    "fileName": "broken.pdf",
    "fileType": "pdf",
    "fileBase64": "not-base64"
})

print("\n✅ API verification test run completed.")