
from src.document_search import (
    search_by_invoice_number,
    search_by_company_name,
    search_by_keyword,
)


# Sample invoice data for testing
invoices = [
    {
        "company_name": "Larkfield Stationers",
        "invoice_number": "INV-2026-0142",
        "invoice_date": "18 September 2026",
        "gst": "2646.36",
        "total_due": "17348.36"
    },
    {
        "company_name": "ABC Traders",
        "invoice_number": "INV-2026-0143",
        "invoice_date": "20 September 2026",
        "gst": "1500.00",
        "total_due": "10000.00"
    }
]


def test_search_by_invoice_number():
    result = search_by_invoice_number(
        invoices,
        "INV-2026-0142"
    )

    assert result is not None
    assert result["company_name"] == "Larkfield Stationers"


def test_search_by_company_name():
    result = search_by_company_name(
        invoices,
        "larkfield"
    )

    assert len(result) == 1
    assert result[0]["company_name"] == "Larkfield Stationers"


def test_search_by_keyword():
    result = search_by_keyword(
        invoices,
        "2646.36"
    )

    assert len(result) == 1
    assert result[0]["invoice_number"] == "INV-2026-0142"


def test_search_by_invalid_invoice_number():
    result = search_by_invoice_number(
        invoices,
        "INV-9999"
    )

    assert result is None


def test_search_by_empty_company_name():
    result = search_by_company_name(
        invoices,
        ""
    )

    assert result == []


def test_search_by_empty_keyword():
    result = search_by_keyword(
        invoices,
        ""
    )

    assert result == []
