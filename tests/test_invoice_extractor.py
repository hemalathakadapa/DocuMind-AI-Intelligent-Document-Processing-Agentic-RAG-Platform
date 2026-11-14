
from decimal import Decimal
import json

from src.invoice_extractor import invoice_fields_to_json
import pytest

from src.invoice_extractor import (
    extract_invoice_fields,
    validate_invoice_totals,
)


SAMPLE_TEXT = """
Invoice no. INV-2026-0142
Invoice date 2026-09-18
Subtotal %14,702.00
GST at 18% %2,646.36
Total due %17,348.36
"""


def test_extract_invoice_fields():
    fields = extract_invoice_fields(SAMPLE_TEXT)

    assert fields["invoice_number"] == "INV-2026-0142"
    assert fields["invoice_date"] == "2026-09-18"
    assert fields["subtotal"] == Decimal("14702.00")
    assert fields["gst"] == Decimal("2646.36")
    assert fields["total_due"] == Decimal("17348.36")


def test_missing_fields_return_none():
    fields = extract_invoice_fields("Invoice no. INV-2026-0142")

    assert fields["invoice_number"] == "INV-2026-0142"
    assert fields["invoice_date"] is None
    assert fields["subtotal"] is None
    assert fields["gst"] is None
    assert fields["total_due"] is None


def test_malformed_amount_is_not_extracted():
    text = """
    Subtotal: invalid
    GST at 18%: 2646.36
    Total due: 17348.36
    """

    fields = extract_invoice_fields(text)

    assert fields["subtotal"] is None
    assert fields["gst"] == Decimal("2646.36")


def test_non_string_input_raises_type_error():
    with pytest.raises(TypeError):
        extract_invoice_fields(123)


def test_valid_invoice_totals():
    fields = {
        "subtotal": Decimal("14702.00"),
        "gst": Decimal("2646.36"),
        "total_due": Decimal("17348.36"),
    }

    assert validate_invoice_totals(fields) is True


def test_invalid_invoice_totals():
    fields = {
        "subtotal": Decimal("100.00"),
        "gst": Decimal("18.00"),
        "total_due": Decimal("150.00"),
    }

    assert validate_invoice_totals(fields) is False


def test_missing_amount_fails_validation():
    fields = {
        "subtotal": Decimal("100.00"),
        "gst": None,
        "total_due": Decimal("118.00"),
    }

    assert validate_invoice_totals(fields) is False


def test_one_paisa_difference_is_allowed():
    fields = {
        "subtotal": Decimal("100.00"),
        "gst": Decimal("18.00"),
        "total_due": Decimal("118.01"),
    }

    assert validate_invoice_totals(fields) is True


def test_negative_tolerance_is_rejected():
    fields = {
        "subtotal": Decimal("100.00"),
        "gst": Decimal("18.00"),
        "total_due": Decimal("118.00"),
    }

    with pytest.raises(ValueError):
        validate_invoice_totals(
            fields,
            tolerance=Decimal("-0.01"),
        )

def test_invoice_fields_to_json():
    fields = {
        "invoice_number": "INV-2026-0142",
        "invoice_date": "2026-09-18",
        "subtotal": Decimal("14702.00"),
        "gst": Decimal("2646.36"),
        "total_due": Decimal("17348.36"),
    }

    result = invoice_fields_to_json(fields)

    parsed = json.loads(result)

    assert parsed["invoice_number"] == "INV-2026-0142"
    assert parsed["invoice_date"] == "2026-09-18"
    assert parsed["subtotal"] == "14702.00"
    assert parsed["gst"] == "2646.36"
    assert parsed["total_due"] == "17348.36"
