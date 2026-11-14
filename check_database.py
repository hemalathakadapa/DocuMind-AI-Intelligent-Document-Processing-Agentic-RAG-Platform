
from src.database import create_database, get_all_invoices

# Create database if it does not exist
create_database()

# Get all invoice records
invoices = get_all_invoices()

print("\n========== DATABASE REPORT ==========")

print("Total invoices in database:", len(invoices))

for invoice in invoices:
    print("\nInvoice ID:", invoice[0])
    print("Company:", invoice[1])
    print("Invoice Number:", invoice[2])
    print("Invoice Date:", invoice[3])
    print("Subtotal:", invoice[4])
    print("GST:", invoice[5])
    print("Total Due:", invoice[6])
