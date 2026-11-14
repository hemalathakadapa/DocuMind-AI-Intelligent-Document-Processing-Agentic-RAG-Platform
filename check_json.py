
import json
from pathlib import Path

files = [
    "data/extracted_data/invoice2.json",
    "data/extracted_data/sample-scanned-invoice.json"
]

for file in files:
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("\nFile:", file)
    print("Company:", data.get("company_name"))
    print("Invoice Number:", data.get("invoice_number"))
    print("Total Due:", data.get("total_due"))

import json
from pathlib import Path

folder = Path("data/extracted_data")

for file in folder.glob("*.json"):
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)

    print("\nFile:", file.name)
    print("Company:", data.get("company_name"))
    print("Invoice Number:", data.get("invoice_number"))
    print("Invoice Date:", data.get("invoice_date"))
    print("Subtotal:", data.get("subtotal"))
    print("GST:", data.get("gst"))
    print("Total Due:", data.get("total_due"))
