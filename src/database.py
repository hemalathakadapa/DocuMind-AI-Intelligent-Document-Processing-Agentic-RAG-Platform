
import sqlite3
from pathlib import Path


# Database file location
DB_PATH = Path("data/documind.db")


def create_database():
    """
    Create SQLite database and invoices table.
    """

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(DB_PATH)

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company_name TEXT,
            invoice_number TEXT UNIQUE,
            invoice_date TEXT,
            subtotal TEXT,
            gst TEXT,
            total_due TEXT
        )
    """)

    connection.commit()
    connection.close()

def search_invoice_by_number(invoice_number):
    """Search invoice using invoice number."""

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    cursor.execute(
        "SELECT * FROM invoices WHERE invoice_number = ?",
        (invoice_number,)
    )

    result = cursor.fetchone()

    connection.close()

    return result
def insert_invoice(invoice):
    """
    Insert invoice details into database.
    """

    connection = sqlite3.connect(DB_PATH)

    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO invoices (
    company_name,
    invoice_number,
    invoice_date,
    subtotal,
    gst,
    total_due
)
VALUES (?, ?, ?, ?, ?, ?)

ON CONFLICT(invoice_number)
DO UPDATE SET
    company_name = excluded.company_name,
    invoice_date = excluded.invoice_date,
    subtotal = excluded.subtotal,
    gst = excluded.gst,
    total_due = excluded.total_due
        
        """, (
            invoice.get("company_name"),
            invoice.get("invoice_number"),
            invoice.get("invoice_date"),
            str(invoice.get("subtotal")) if invoice.get("subtotal") is not None else None,
            str(invoice.get("gst")) if invoice.get("gst") is not None else None,
            str(invoice.get("total_due")) if invoice.get("total_due") is not None else None
        ))

        

        connection.commit()

    finally:
        connection.close()


def get_all_invoices():
    """
    Retrieve all invoice records.
    """

    connection = sqlite3.connect(DB_PATH)

    cursor = connection.cursor()

    cursor.execute("SELECT * FROM invoices")

    records = cursor.fetchall()

    connection.close()

    return records
def search_invoices_by_company(company_name):
    """Search invoices using company name."""

    if not company_name or not company_name.strip():
        return []

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    try:
        cursor.execute("""
            SELECT * FROM invoices
            WHERE company_name LIKE ? COLLATE NOCASE
        """, (f"%{company_name.strip()}%",))

        records = cursor.fetchall()
        return records

    finally:
        connection.close()

def search_invoices_by_filters(
    invoice_number=None,
    company_name=None,
    invoice_date=None,
    subtotal=None,
    gst=None,
    total_due=None
):
    """Search invoices using one or multiple filters."""

    filters = {
        "invoice_number": invoice_number,
        "company_name": company_name,
        "invoice_date": invoice_date,
        "subtotal": subtotal,
        "gst": gst,
        "total_due": total_due
    }

    conditions = []
    values = []

    for column, value in filters.items():
        if value is not None and str(value).strip():
            conditions.append(f"{column} = ?")
            values.append(str(value).strip())

    # No filters means no search
    if not conditions:
        return []

    query = "SELECT * FROM invoices WHERE " + " AND ".join(conditions)

    connection = sqlite3.connect(DB_PATH)
    cursor = connection.cursor()

    try:
        cursor.execute(query, values)
        return cursor.fetchall()

    finally:
        connection.close()

