from pathlib import Path

from src.invoice_extractor import (
    extract_invoice_fields,
    save_invoice_json,
)

sample_text = """
Invoice no: INV-2026-0142
Invoice date: 18 September 2026
Subtotal: 14702.00
GST at 18%: 2646.36
Total due: 17348.36
"""

fields = extract_invoice_fields(sample_text)

output_path = Path("data/extracted_data/invoice.json")

save_invoice_json(fields, str(output_path))

print("JSON file saved successfully!")
print("File location:", output_path)