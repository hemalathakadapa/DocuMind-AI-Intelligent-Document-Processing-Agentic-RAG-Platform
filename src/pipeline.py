
from pathlib import Path

from src.document_loader import load_document
from src.text_cleaner import clean_text
from src.invoice_extractor import (
    extract_invoice_fields,
    validate_invoice_totals,
    save_invoice_json,
)
from src.database import insert_invoice


def process_invoice(
    input_path: str,
    output_path: str,
) -> dict:
    """Extract, validate, and save invoice information."""

    # Step 1: Read PDF and extract text
    extracted_text = load_document(input_path)

    # Step 2: Clean extracted text
    cleaned_text = clean_text(extracted_text)

    # Step 3: Extract invoice fields
    invoice_fields = extract_invoice_fields(cleaned_text)

    # Step 4: Validate invoice totals
    is_valid = validate_invoice_totals(invoice_fields)

    # Step 5: Save invoice details as JSON
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    save_invoice_json(invoice_fields, str(output_file))

    # Step 6: Save valid invoice into database
    database_saved = False

    if is_valid and invoice_fields.get("invoice_number"):
        insert_invoice(invoice_fields)
        database_saved = True

    return {
        "invoice_fields": invoice_fields,
        "is_valid": is_valid,
        "output_path": str(output_file),
        "database_saved": database_saved,
    }
