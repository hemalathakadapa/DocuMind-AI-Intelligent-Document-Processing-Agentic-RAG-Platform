
import json
from pathlib import Path

def load_invoice_json_files(folder_path):
    """
    Load all JSON invoice files from a folder.
    """
    folder = Path(folder_path)

    if not folder.exists():
        raise FileNotFoundError(f"Folder not found: {folder_path}")

    invoice_records = []

    for file_path in folder.glob("*.json"):
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                invoice_data = json.load(file)

            invoice_records.append(invoice_data)

        except (json.JSONDecodeError, OSError) as error:
            print(f"Could not read {file_path.name}: {error}")

    return invoice_records

def search_by_invoice_number(invoice_records, invoice_number):
    """
    Search an invoice using its invoice number.
    """
    for invoice in invoice_records:
        if invoice.get("invoice_number", "").strip().lower() == invoice_number.strip().lower():
            return invoice

    return None
def search_by_company_name(invoice_records, company_name):
    """
    Search invoices using company name.
    """
    company_name = company_name.strip().lower()

    if not company_name:
        return []

    matching_invoices = []

    for invoice in invoice_records:
        saved_name = invoice.get("company_name")

        if isinstance(saved_name, str) and company_name in saved_name.lower():
            matching_invoices.append(invoice)

    return matching_invoices
def search_by_keyword(invoice_records, keyword):
    """
    Search invoices using any keyword.
    """
    keyword = keyword.strip().lower()

    if not keyword:
        return []

    matching_invoices = []

    for invoice in invoice_records:
        invoice_text = json.dumps(invoice).lower()

        if keyword in invoice_text:
            matching_invoices.append(invoice)

    return matching_invoices
def display_invoice_details(invoice_records):
    """
    Display important invoice details.
    """

    if not invoice_records:
        print("No matching invoices found.")
        return

    for invoice in invoice_records:
        print("\n---------- INVOICE DETAILS ----------")
        print("Company Name:", invoice.get("company_name", "Not Available"))
        print("Invoice Number:", invoice.get("invoice_number", "Not Available"))
        print("Invoice Date:", invoice.get("invoice_date", "Not Available"))
        print("GST:", invoice.get("gst", "Not Available"))
        print("Total Due:", invoice.get("total_due", "Not Available"))