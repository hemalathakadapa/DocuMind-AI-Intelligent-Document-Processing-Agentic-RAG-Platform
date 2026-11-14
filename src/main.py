
import json

from src.batch_processor import process_invoice_folder
from src.database import create_database, get_all_invoices


def main():

    # Step 1: Create database and table
    create_database()

    input_folder = "data/sample_documents"
    output_folder = "data/extracted_data"

    # Step 2: Process all PDF invoices
    results = process_invoice_folder(
        input_folder,
        output_folder,
    )

    print("\n========== BATCH PROCESSING REPORT ==========")

    for result in results:
        print(f"\nFile: {result['file']}")
        print(f"Status: {result['status']}")

        if result["status"] == "Success":
            print(f"Invoice Valid: {result['valid']}")

            # Read extracted invoice details from JSON
            with open(
                result["output"],
                "r",
                encoding="utf-8",
            ) as file:
                invoice_data = json.load(file)

            # Display extracted invoice information
            print(f"Company Name: {invoice_data.get('company_name')}")
            print(f"Invoice Number: {invoice_data.get('invoice_number')}")
            print(f"Invoice Date: {invoice_data.get('invoice_date')}")
            print(f"Subtotal: {invoice_data.get('subtotal')}")
            print(f"GST: {invoice_data.get('gst')}")
            print(f"Total Due: {invoice_data.get('total_due')}")

            print(f"JSON Output: {result['output']}")

        else:
            print(f"Error: {result['error']}")

    # Step 3: Display database records
        # Step 3: Display database records
    invoices = get_all_invoices()

    print("\n========== DATABASE REPORT ==========")
    print("Total invoices in database:", len(invoices))

    for invoice in invoices:
        (
            invoice_id,
            company_name,
            invoice_number,
            invoice_date,
            subtotal,
            gst,
            total_due
        ) = invoice

        print("\n------------------------------")
        print("Company Name:", company_name)
        print("Invoice Number:", invoice_number)
        print("Invoice Date:", invoice_date)
        print("Subtotal:", subtotal)
        print("GST:", gst)
        print("Total Due:", total_due)

    print("\n========== PROCESSING SUMMARY ==========")
    print("Total PDF files:", len(results))
    print(
        "Successful:",
        sum(r["status"] == "Success" for r in results)
    )
    print(
        "Failed:",
        sum(r["status"] == "Failed" for r in results)
    )


if __name__ == "__main__":
    main()
