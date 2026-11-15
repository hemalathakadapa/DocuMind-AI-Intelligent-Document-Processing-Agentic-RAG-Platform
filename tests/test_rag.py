
import src.rag_assistant as rag


def test_answer_question_success(monkeypatch):

    # Sample invoice data
    sample_invoice = {
        "company_name": "Larkfield Stationers",
        "invoice_number": "INV-2026-0142",
        "invoice_date": "2026-09-18",
        "subtotal": "14702.00",
        "gst": "2646.36",
        "total_due": "17348.36"
    }

    # Mock invoice loading
    monkeypatch.setattr(
        rag,
        "load_invoice_json_files",
        lambda folder: [sample_invoice]
    )

    # Mock LLM response
    monkeypatch.setattr(
        rag,
        "ask_llm",
        lambda prompt: "The GST is 2646.36."
    )

    answer = rag.answer_question(
        "What is the GST of invoice INV-2026-0142?"
    )

    assert answer == "The GST is 2646.36."


def test_invoice_not_found(monkeypatch):

    monkeypatch.setattr(
        rag,
        "load_invoice_json_files",
        lambda folder: []
    )

    answer = rag.answer_question(
        "Find invoice INV-2026-9999"
    )

    assert "was not found" in answer


def test_invoice_number_missing(monkeypatch):
    monkeypatch.setattr(
    rag,
    "load_invoice_json_files",
    lambda folder: []
)

    answer = rag.answer_question(
        "What is the GST amount?"
    )

    assert answer == "Please provide a valid invoice number."
