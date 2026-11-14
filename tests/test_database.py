
import sqlite3

import src.database as database


def setup_test_database(tmp_path, monkeypatch):
    test_db_path = tmp_path / "test_documind.db"

    monkeypatch.setattr(database, "DB_PATH", test_db_path)

    database.create_database()

    return test_db_path


def test_create_database(tmp_path, monkeypatch):
    test_db_path = setup_test_database(tmp_path, monkeypatch)

    assert test_db_path.exists()

    connection = sqlite3.connect(test_db_path)
    cursor = connection.cursor()

    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
        AND name = 'invoices'
    """)

    result = cursor.fetchone()
    connection.close()

    assert result is not None


def test_insert_and_get_all_invoices(tmp_path, monkeypatch):
    setup_test_database(tmp_path, monkeypatch)

    invoice = {
        "company_name": "Larkfield Stationers",
        "invoice_number": "INV-TEST-001",
        "invoice_date": "18 September 2026",
        "subtotal": "14702.00",
        "gst": "2646.36",
        "total_due": "17348.36"
    }

    database.insert_invoice(invoice)

    records = database.get_all_invoices()

    assert len(records) == 1
    assert records[0][2] == "INV-TEST-001"


def test_duplicate_invoice_number_is_ignored(
    tmp_path, monkeypatch
):
    setup_test_database(tmp_path, monkeypatch)

    invoice = {
        "company_name": "Larkfield Stationers",
        "invoice_number": "INV-TEST-002",
        "invoice_date": "18 September 2026",
        "subtotal": "1000.00",
        "gst": "180.00",
        "total_due": "1180.00"
    }

    database.insert_invoice(invoice)
    database.insert_invoice(invoice)

    records = database.get_all_invoices()

    assert len(records) == 1


def test_search_invoice_by_number_found(
    tmp_path, monkeypatch
):
    setup_test_database(tmp_path, monkeypatch)

    invoice = {
        "company_name": "Larkfield Stationers",
        "invoice_number": "INV-TEST-003",
        "invoice_date": "18 September 2026",
        "subtotal": "1000.00",
        "gst": "180.00",
        "total_due": "1180.00"
    }

    database.insert_invoice(invoice)

    result = database.search_invoice_by_number(
        "INV-TEST-003"
    )

    assert result is not None
    assert result[2] == "INV-TEST-003"


def test_search_invoice_by_number_not_found(
    tmp_path, monkeypatch
):
    setup_test_database(tmp_path, monkeypatch)

    result = database.search_invoice_by_number(
        "INV-UNKNOWN"
    )

    assert result is None
def test_search_invoices_by_company_partial_name(
    tmp_path, monkeypatch
):
    setup_test_database(tmp_path, monkeypatch)

    invoice = {
        "company_name": "Larkfield Stationers",
        "invoice_number": "INV-TEST-004",
        "invoice_date": "18 September 2026",
        "subtotal": "1000.00",
        "gst": "180.00",
        "total_due": "1180.00"
    }

    database.insert_invoice(invoice)

    results = database.search_invoices_by_company("Larkfield")

    assert len(results) == 1
    assert results[0][1] == "Larkfield Stationers"


def test_search_invoices_by_company_full_name(
    tmp_path, monkeypatch
):
    setup_test_database(tmp_path, monkeypatch)

    invoice = {
        "company_name": "Larkfield Stationers",
        "invoice_number": "INV-TEST-005",
        "invoice_date": "18 September 2026",
        "subtotal": "1000.00",
        "gst": "180.00",
        "total_due": "1180.00"
    }

    database.insert_invoice(invoice)

    results = database.search_invoices_by_company(
        "Larkfield Stationers"
    )

    assert len(results) == 1


def test_search_invoices_by_company_not_found(
    tmp_path, monkeypatch
):
    setup_test_database(tmp_path, monkeypatch)

    results = database.search_invoices_by_company(
        "Unknown Company"
    )

    assert results == []

import pytest
import src.database as database


@pytest.fixture
def filter_test_database(tmp_path, monkeypatch):
    """Create a temporary database with one sample invoice."""

    test_db_path = tmp_path / "test_filters.db"
    monkeypatch.setattr(database, "DB_PATH", test_db_path)

    database.create_database()

    sample_invoice = {
        "company_name": "Larkfield Stationers",
        "invoice_number": "INV-2026-0142",
        "invoice_date": "18 September 2026",
        "subtotal": "14702.00",
        "gst": "2646.36",
        "total_due": "17348.36"
    }

    database.insert_invoice(sample_invoice)

    return sample_invoice


def test_search_by_invoice_date(filter_test_database):
    result = database.search_invoices_by_filters(
        invoice_date="18 September 2026"
    )
    assert len(result) == 1


def test_search_by_gst(filter_test_database):
    result = database.search_invoices_by_filters(
        gst="2646.36"
    )
    assert len(result) == 1


def test_search_by_total_due(filter_test_database):
    result = database.search_invoices_by_filters(
        total_due="17348.36"
    )
    assert len(result) == 1


def test_search_using_multiple_filters(filter_test_database):
    result = database.search_invoices_by_filters(
        invoice_date="18 September 2026",
        gst="2646.36",
        total_due="17348.36"
    )
    assert len(result) == 1


def test_search_with_wrong_filter_values(filter_test_database):
    result = database.search_invoices_by_filters(
        gst="9999.99"
    )
    assert result == []


def test_search_without_filters(filter_test_database):
    result = database.search_invoices_by_filters()
    assert result == []
