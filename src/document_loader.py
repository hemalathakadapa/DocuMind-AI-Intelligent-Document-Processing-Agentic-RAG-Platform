


import io
from pathlib import Path

import pymupdf
import pytesseract
from docx import Document
from PIL import Image

import shutil

tesseract_path = shutil.which("tesseract")

if tesseract_path:
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
elif Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe").exists():
    pytesseract.pytesseract.tesseract_cmd = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt"}


def get_file_extension(file_path: str) -> str:
    """Return the extension of a file in lowercase."""
    return Path(file_path).suffix.lower()



def is_supported_file(file_path: str) -> bool:
    """Return True if the file has a supported extension."""
    return get_file_extension(file_path) in SUPPORTED_EXTENSIONS




def extract_txt_text(file_path: str) -> str:
    """Extract text from a TXT file."""
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if path.suffix.lower() != ".txt":
        raise ValueError("Only TXT files are supported by this function.")

    return path.read_text(encoding="utf-8")


import pymupdf




def extract_pdf_text(file_path: str) -> str:
    """Extract text from a PDF, using OCR if selectable text is absent."""
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError("Only PDF files are supported by this function.")

    with pymupdf.open(path) as document:
        pages_text = []

        for page in document:
            text = page.get_text().strip()

            if not text:
                pix = page.get_pixmap(dpi=200)
                image = Image.open(
                    io.BytesIO(pix.tobytes("png"))
                )

                text = pytesseract.image_to_string(image).strip()

            pages_text.append(text)

    return "\n".join(pages_text)

def extract_docx_text(file_path: str) -> str:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if path.suffix.lower() != ".docx":
        raise ValueError("Only DOCX files are supported by this function.")

    document = Document(path)

    text_parts = []

    # Extract paragraph text
    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            text_parts.append(paragraph.text)

    # Extract table text
    for table in document.tables:
        for row in table.rows:
            row_text = " | ".join(
                cell.text.strip() for cell in row.cells
            )
            text_parts.append(row_text)

    return "\n".join(text_parts)


def load_document(file_path: str) -> str:
    """Load a supported document and return its extracted text."""

    extension = get_file_extension(file_path)

    if not is_supported_file(file_path):
        raise ValueError(f"Unsupported file type: {extension}")

    if extension == ".txt":
        return extract_txt_text(file_path)

    if extension == ".pdf":
        return extract_pdf_text(file_path)

    if extension == ".docx":
        return extract_docx_text(file_path)

    raise ValueError(f"Unsupported file type: {extension}")
def needs_ocr(extracted_text: str) -> bool:
    """Return True when extracted PDF text is empty."""
    return not extracted_text.strip()