
from PIL import Image
from src.document_loader import get_file_extension, is_supported_file
from src.document_loader import (
    get_file_extension,
    is_supported_file,
    extract_txt_text,
)
from docx import Document
from src.document_loader import extract_docx_text
from src.document_loader import needs_ocr
def test_pdf_extension():
    assert get_file_extension("invoice.pdf") == ".pdf"


def test_uppercase_extension():
    assert get_file_extension("INVOICE.PDF") == ".pdf"


def test_docx_extension():
    assert get_file_extension("report.docx") == ".docx"


def test_supported_pdf():
    assert is_supported_file("invoice.pdf") is True


def test_supported_txt():
    assert is_supported_file("notes.txt") is True


def test_unsupported_jpg():
    assert is_supported_file("photo.jpg") is False


def test_extract_txt_text(tmp_path):
    sample_file = tmp_path / "sample.txt"
    sample_file.write_text(
        "Hello DocuMind AI!",
        encoding="utf-8",
    )

    result = extract_txt_text(str(sample_file))

    assert result == "Hello DocuMind AI!"

import pytest


def test_missing_txt_file():
    with pytest.raises(FileNotFoundError):
        extract_txt_text("data/does_not_exist.txt")


def test_extract_txt_from_pdf_is_rejected(tmp_path):
    fake_pdf = tmp_path / "sample.pdf"
    fake_pdf.write_text("not a real PDF", encoding="utf-8")

    with pytest.raises(ValueError):
        extract_txt_text(str(fake_pdf))


import pymupdf
import pytest

from src.document_loader import extract_pdf_text


def test_extract_pdf_text(tmp_path):
    pdf_path = tmp_path / "sample.pdf"

    with pymupdf.open() as document:
        page = document.new_page()
        page.insert_text((72, 72), "Hello DocuMind AI")
        document.save(pdf_path)

    extracted_text = extract_pdf_text(str(pdf_path))

    assert "Hello DocuMind AI" in extracted_text


def test_missing_pdf_file(tmp_path):
    pdf_path = tmp_path / "missing.pdf"

    with pytest.raises(FileNotFoundError):
        extract_pdf_text(str(pdf_path))


def test_extract_pdf_from_txt_is_rejected(tmp_path):
    txt_path = tmp_path / "sample.txt"
    txt_path.write_text("This is a text file", encoding="utf-8")

    with pytest.raises(ValueError):
        extract_pdf_text(str(txt_path))


def test_extract_docx_text(tmp_path):
    docx_path = tmp_path / "sample.docx"

    document = Document()
    document.add_paragraph("Hello DocuMind AI!")
    document.add_paragraph("Document extraction is working.")
    document.save(docx_path)

    result = extract_docx_text(str(docx_path))

    assert "Hello DocuMind AI!" in result
    assert "Document extraction is working." in result


def test_missing_docx_file(tmp_path):
    docx_path = tmp_path / "missing.docx"

    with pytest.raises(FileNotFoundError):
        extract_docx_text(str(docx_path))
from src.document_loader import load_document


def test_load_document_txt(tmp_path):
    file_path = tmp_path / "sample.txt"
    file_path.write_text("Hello DocuMind AI", encoding="utf-8")

    result = load_document(str(file_path))

    assert result == "Hello DocuMind AI"


def test_load_document_unsupported_file(tmp_path):
    file_path = tmp_path / "sample.jpg"
    file_path.write_text("sample image placeholder", encoding="utf-8")

    try:
        load_document(str(file_path))
        assert False, "Expected ValueError for unsupported file"
    except ValueError as error:
        assert "Unsupported file type" in str(error)
        
def test_load_document_pdf(tmp_path):
    pdf_path = tmp_path / "sample.pdf"

    with pymupdf.open() as document:
        page = document.new_page()
        page.insert_text((72, 72), "PDF routing works")
        document.save(pdf_path)

    result = load_document(str(pdf_path))

    assert "PDF routing works" in result


def test_load_document_docx(tmp_path):
    docx_path = tmp_path / "sample.docx"

    document = Document()
    document.add_paragraph("DOCX routing works")
    document.save(docx_path)

    result = load_document(str(docx_path))

    assert "DOCX routing works" in result
def test_extract_docx_table_text(tmp_path):
    docx_path = tmp_path / "table_sample.docx"

    document = Document()
    table = document.add_table(rows=2, cols=2)

    table.cell(0, 0).text = "Item"
    table.cell(0, 1).text = "Amount"
    table.cell(1, 0).text = "Laptop"
    table.cell(1, 1).text = "50000"

    document.save(docx_path)

    result = extract_docx_text(str(docx_path))

    assert "Item" in result
    assert "Laptop" in result
    assert "50000" in result

def test_extract_pdf_text_from_scanned_pdf(tmp_path):
    pdf_path = tmp_path / "scanned.pdf"

    with pymupdf.open() as document:
        document.new_page()
        document.save(pdf_path)

    result = extract_pdf_text(str(pdf_path))

    assert result.strip() == ""
def test_needs_ocr_when_text_is_empty():
    assert needs_ocr("") is True


def test_needs_ocr_when_text_contains_content():
    assert needs_ocr("Invoice Total: 5000") is False


def test_needs_ocr_when_text_has_only_whitespace():
    assert needs_ocr("   \n  ") is True

def test_extract_pdf_text_using_ocr(tmp_path):
    image_path = tmp_path / "invoice.png"
    pdf_path = tmp_path / "scanned_invoice.pdf"

    image = Image.new("RGB", (1200, 300), "white")
    from PIL import ImageDraw

    draw = ImageDraw.Draw(image)
    draw.text((50, 100), "INVOICE TOTAL 5000", fill="black")
    image.save(image_path)

    with pymupdf.open() as document:
        page = document.new_page(width=600, height=150)
        page.insert_image(page.rect, filename=str(image_path))
        document.save(pdf_path)

    result = extract_pdf_text(str(pdf_path))

    assert "INVOICE" in result.upper()
    assert "5000" in result