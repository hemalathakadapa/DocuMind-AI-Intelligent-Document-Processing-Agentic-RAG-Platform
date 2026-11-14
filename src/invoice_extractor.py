import re
import json

from decimal import Decimal
from datetime import datetime
def normalize_invoice_date(date_text: str) -> str:
    """
    Convert different invoice date formats into YYYY-MM-DD.
    """

    if not date_text:
        return None

    date_text = date_text.strip()

    # Correct common OCR spelling mistake
    date_text = re.sub(
        r"Septemiber",
        "September",
        date_text,
        flags=re.IGNORECASE
    )

    date_formats = [
        "%d %B %Y",
        "%d %b %Y",
        "%d-%b-%y",
        "%d-%B-%Y",
        "%d/%m/%Y",
        "%d-%m-%Y",
    ]

    for date_format in date_formats:
        try:
            parsed_date = datetime.strptime(
                date_text,
                date_format
            )

            return parsed_date.strftime("%Y-%m-%d")

        except ValueError:
            continue

    # If date cannot be parsed, preserve original value
    return date_text
def extract_invoice_fields(text: str) -> dict:
    if not isinstance(text, str):
        raise TypeError("text must be a string")

    fields = {
        "company_name": None,
        "invoice_number": None,
        "invoice_date": None,
        "subtotal": None,
        "gst": None,
        "total_due": None,
    }

    # 1. Extract invoice number
    invoice_match = re.search(
        r"Invoice\s*(?:No\.?|Number)\s*[:#]?\s*"
        r"(?:\n\s*)?([A-Z0-9][A-Z0-9/-]*)",
        text,
        re.IGNORECASE,
    )

    if invoice_match:
        fields["invoice_number"] = invoice_match.group(1).strip()

    # 2. Extract invoice date
             # 2. Extract invoice date
    date_match = re.search(
        r"(?:Invoice\s*date|Dated|Date)\s*:?\s*"
        r"(?:\r?\n\s*)?"
        r"(\d{4}-\d{2}-\d{2}|\d{1,2}[-/ ]+[A-Za-z0-9]+[-/ ]+\d{2,4})",
        text,
        re.IGNORECASE,
    )

    if date_match:
        extracted_date = date_match.group(1).strip()

        fields["invoice_date"] = normalize_invoice_date(
            extracted_date
        )

    # 3. Extract company name
    lines = [line.strip() for line in text.splitlines() if line.strip()]
        # First priority: Extract company name from Company Name label
    company_label_match = re.search(
        r"Company\s+Name\s*:\s*([^\r\n]+)",
        text,
        re.IGNORECASE,
    )

    if company_label_match:
        fields["company_name"] = company_label_match.group(1).strip()

    else:
        company_label_match = re.search(
            r"Company\s+Name\s*:\s*\r?\n\s*([^\r\n]+)",
            text,
            re.IGNORECASE,
        )

        if company_label_match:
            fields["company_name"] = company_label_match.group(1).strip()

    gstin_index = next(
        (
            i for i, line in enumerate(lines)
            if re.search(r"\bGSTIN\b", line, re.IGNORECASE)
        ),
        None,
    )

    if gstin_index is not None:
        for line in reversed(
            lines[max(0, gstin_index - 10):gstin_index]
        ):
            if re.search(
                r"address|road|street|floor|lane|cross|"
                r"state name|contact|phone|email|"
                r"centrix|pin code|code\s*:|gstin",
                line,
                re.IGNORECASE,
            ):
                continue

            if re.search(r"\d{4,}", line):
                continue

            if "invoice" in line.lower():
                continue

            fields["company_name"] = line
            break

        # Fallback company name
    if not fields["company_name"]:
        company_match = re.search(
            r"^\s*(.+?)\s+(?:\d+\s+)?TAX\s+INVOICE\b",
            text,
            re.IGNORECASE | re.MULTILINE,
        )

        if company_match:
            candidate = company_match.group(1).strip()

            # Reject descriptive sentences
            if (
                len(candidate) <= 60
                and not re.search(r"[.!?]", candidate)
                and "computer generated" not in candidate.lower()
                and "fictional" not in candidate.lower()
                and "software testing" not in candidate.lower()
            ):
                fields["company_name"] = candidate

    # 4. Extract subtotal / taxable value

    taxable_match = re.search(
        r"\bTaxable\b[\s\S]{0,300}?"
        r"^\s*\d{6,8}\s+([\s\S]*?)"
        r"(?=^\s*Total\b)",
        text,
        re.MULTILINE | re.IGNORECASE,
    )

    if taxable_match:
        amounts = re.findall(
            r"\d[\d,]*\.\d{2}",
            taxable_match.group(1),
        )

        if amounts:
            fields["subtotal"] = Decimal(
                amounts[-1].replace(",", "")
            )

    # Fallback subtotal extraction
    if fields["subtotal"] is None:
        subtotal_match = re.search(
            r"(?:Sub\s*total|Taxable\s+Value)\s*[:₹%\s]*"
            r"([\d,]+\.\d{2})",
            text,
            re.IGNORECASE,
        )

        if subtotal_match:
            fields["subtotal"] = Decimal(
                subtotal_match.group(1).replace(",", "")
            )

    # 5. Extract GST

    cgst_match = re.search(
        r"CGST(?:\s*@\s*\d+(?:\.\d+)?%?)?\s*[:₹ ]*"
        r"([\d,]+\.\d{2})",
        text,
        re.IGNORECASE,
    )

    sgst_match = re.search(
        r"SGST(?:\s*@\s*\d+(?:\.\d+)?%?)?\s*[:₹ ]*"
        r"([\d,]+\.\d{2})",
        text,
        re.IGNORECASE,
    )

    if cgst_match and sgst_match:
        cgst = Decimal(cgst_match.group(1).replace(",", ""))
        sgst = Decimal(sgst_match.group(1).replace(",", ""))

        fields["gst"] = cgst + sgst

    else:
        gst_match = re.search(
            r"(?<![A-Z])GST(?:\s+at\s+\d+(?:\.\d+)?%)?"
            r"\s*[:₹%\s]*([\d,]+\.\d{2})",
            text,
            re.IGNORECASE,
        )

        if gst_match:
            fields["gst"] = Decimal(
                gst_match.group(1).replace(",", "")
            )

    # 6. Extract total amount

    total_match = re.search(
        r"\b(?:Grand\s+Total|Total\s+due|Total)\b\s*[:₹%\s]*"
        r"([\d,]+\.\d{2})",
        text,
        re.IGNORECASE,
    )

    if total_match:
        fields["total_due"] = Decimal(
            total_match.group(1).replace(",", "")
        )

    return fields


def validate_invoice_totals(
    fields: dict,
    tolerance: Decimal = Decimal("0.01")
) -> bool:

    subtotal = fields.get("subtotal")
    gst = fields.get("gst")
    total_due = fields.get("total_due")

    if subtotal is None or gst is None or total_due is None:
        return False

    if not all(
        isinstance(amount, Decimal)
        for amount in (subtotal, gst, total_due)
    ):
        return False

    if not tolerance.is_finite() or tolerance < 0:
        raise ValueError(
            "tolerance must be a finite, non-negative Decimal"
        )

    calculated_total = subtotal + gst

    return abs(calculated_total - total_due) <= tolerance


def invoice_fields_to_json(fields: dict) -> str:
    json_fields = {
        key: str(value) if isinstance(value, Decimal) else value
        for key, value in fields.items()
    }

    return json.dumps(
        json_fields,
        indent=2,
        ensure_ascii=False,
    )


def save_invoice_json(fields: dict, output_path: str) -> None:
    json_text = invoice_fields_to_json(fields)

    with open(output_path, "w", encoding="utf-8") as file:
        file.write(json_text)
