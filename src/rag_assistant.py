
import re

from src.document_search import (
    load_invoice_json_files,
    search_by_invoice_number
)

from src.llm_client import ask_llm


INVOICE_FOLDER = "data/extracted_data"


def answer_question(question):
    """
    Retrieve invoice information and generate
    an answer using the local Qwen LLM.
    """

    # Step 1: Load invoice JSON files
    invoices = load_invoice_json_files(INVOICE_FOLDER)

    # Step 2: Find invoice number in the question
    match = re.search(
        r"\b[A-Z0-9]+(?:[-/][A-Z0-9]+)+\b",
        question.upper()
    )

    if not match:
        return "Please provide a valid invoice number."

    invoice_number = match.group(0)

    # Step 3: Retrieve the relevant invoice
    invoice = search_by_invoice_number(
        invoices,
        invoice_number
    )

    if invoice is None:
        return f"Invoice {invoice_number} was not found."

    # Step 4: Prepare retrieved information
    context = f"""
    Company Name: {invoice.get('company_name')}
    Invoice Number: {invoice.get('invoice_number')}
    Invoice Date: {invoice.get('invoice_date')}
    Subtotal: {invoice.get('subtotal')}
    GST: {invoice.get('gst')}
    Total Due: {invoice.get('total_due')}
    """

    # Step 5: Send context and question to Qwen
    prompt = f"""
    You are an invoice assistant.

    Answer the question using ONLY the invoice information below.

    If the information is not available, say so.
    Do not invent any values.

    Invoice Information:
    {context}

    User Question:
    {question}

    Answer:
    """

    return ask_llm(prompt)
