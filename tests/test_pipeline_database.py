
from decimal import Decimal

import pytest

import src.database as database
import src.pipeline as pipeline


@pytest.fixture
def setup_pipeline_database(tmp_path, monkeypatch):

    test_db_path = tmp_path / "test_pipeline.db"
    monkeypatch.setattr(database, "DB_PATH", test_db_path)

    database.create_database()

    sample_invoice = {
        "company_name": "Larkfield Stationers",
        "invoice_number": "INV-2026-0142",
        "invoice_date": "18 September 2026",
        "subtotal": Decimal("14702.00"),
        "gst": Decimal("2646.36"),
        "total_due": Decimal("17348.36"),
    }

    monkeypatch.setattr(
        pipeline, "load_document",
        lambda path: "Sample invoice text"
    )

    monkeypatch.setattr(
        pipeline, "clean_text",
        lambda text: text
    )

    monkeypatch.setattr(
        pipeline, "extract_invoice_fields",
        lambda text: sample_invoice
    )

    monkeypatch.setattr(
        pipeline, "validate_invoice_totals",
        lambda invoice: True
    )

    monkeypatch.setattr(
        pipeline, "save_invoice_json",
        lambda invoice, path: None
    )

    return sample_invoice, tmp_path


def test_valid_invoice_saved_to_database(setup_pipeline_database):

    sample_invoice, tmp_path = setup_pipeline_database

    result = pipeline.process_invoice(
        "invoice.pdf",
        str(tmp_path / "invoice.json")
    )

    records = database.get_all_invoices()

    assert result["is_valid"] is True
    assert result["database_saved"] is True
    assert len(records) == 1
    assert records[0][2] == sample_invoice["invoice_number"]


def test_duplicate_invoice_not_inserted_twice(setup_pipeline_database):

    sample_invoice, tmp_path = setup_pipeline_database

    pipeline.process_invoice(
        "invoice1.pdf",
        str(tmp_path / "invoice1.json")
    )

    pipeline.process_invoice(
        "invoice2.pdf",
        str(tmp_path / "invoice2.json")
    )

    records = database.get_all_invoices()

    assert len(records) == 1


def test_invalid_invoice_not_saved_to_database(
    setup_pipeline_database, monkeypatch
):

    sample_invoice, tmp_path = setup_pipeline_database

    monkeypatch.setattr(
        pipeline, "validate_invoice_totals",
        lambda invoice: False
    )

    result = pipeline.process_invoice(
        "invalid_invoice.pdf",
        str(tmp_path / "invalid_invoice.json")
    )

    records = database.get_all_invoices()

    assert result["is_valid"] is False
    assert result["database_saved"] is False
    assert len(records) == 0
