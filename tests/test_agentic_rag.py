
import os
import subprocess
import sys

from src import agentic_rag


def test_invalid_invoice_number():
    result = agentic_rag.answer_question(
        "What is GST?",
        "invalid-invoice-test-session"
    )

    assert result == "Please provide a valid invoice number."


def test_invoice_not_found(monkeypatch):

    monkeypatch.setattr(
        agentic_rag,
        "load_invoice_json_files",
        lambda folder: []
    )

    result = agentic_rag.answer_question(
        "What is GST for invoice INV-9999?",
        "invoice-not-found-test-session"
    )

    print("ACTUAL RESULT:", result)

    assert "INV-9999" in result
    assert "not found" in result.lower()

def test_successful_invoice_answer(monkeypatch):
    invoice = {
        "company_name": "Larkfield Stationers",
        "invoice_number": "INV-2026-0142",
        "invoice_date": "18 September 2026",
        "subtotal": "14702.00",
        "gst": "2646.36",
        "total_due": "17348.36"
    }

    monkeypatch.setattr(
        agentic_rag,
        "load_invoice_json_files",
        lambda folder: [invoice]
    )

    monkeypatch.setattr(
        agentic_rag,
        "search_by_invoice_number",
        lambda invoices, number: invoice
    )

    monkeypatch.setattr(
        agentic_rag,
        "ask_llm",
        lambda prompt: "GST is 2646.36."
    )

    result = agentic_rag.answer_question(
        "What is GST for invoice INV-2026-0142?",
        "successful-invoice-test-session"
    )

    assert result == "GST is 2646.36."


def test_conversation_memory(monkeypatch):
    invoice = {
        "company_name": "Larkfield Stationers",
        "invoice_number": "INV-2026-0142",
        "invoice_date": "18 September 2026",
        "subtotal": "14702.00",
        "gst": "2646.36",
        "total_due": "17348.36"
    }

    monkeypatch.setattr(
        agentic_rag,
        "load_invoice_json_files",
        lambda folder: [invoice]
    )

    monkeypatch.setattr(
        agentic_rag,
        "search_by_invoice_number",
        lambda invoices, number: invoice
    )

    monkeypatch.setattr(
        agentic_rag,
        "ask_llm",
        lambda prompt: "Answer generated."
    )

    session_id = "conversation-memory-test-session"

    first_result = agentic_rag.answer_question(
        "What is GST for invoice INV-2026-0142?",
        session_id
    )

    second_result = agentic_rag.answer_question(
        "What is its total amount?",
        session_id
    )

    assert first_result == "Answer generated."
    assert second_result == "Answer generated."


def test_separate_conversation_sessions():
    result = agentic_rag.answer_question(
        "What is the total amount?",
        "separate-session-test"
    )

    assert result == "Please provide a valid invoice number."


def test_sqlite_memory_survives_process_restart(tmp_path):

    db_path = tmp_path / "restart_memory.db"

    env = os.environ.copy()
    env["DOCUMIND_MEMORY_DB"] = str(db_path)

    first_process = """
invoice = {
    "company_name": "Larkfield Stationers",
    "invoice_number": "INV-2026-0142",
    "invoice_date": "18 September 2026",
    "subtotal": "14702.00",
    "gst": "2646.36",
    "total_due": "17348.36"
}

import src.agentic_rag as rag

rag.load_invoice_json_files = lambda folder: [invoice]
rag.search_by_invoice_number = lambda invoices, number: invoice
rag.ask_llm = lambda prompt: "GST: 2646.36"

print(rag.answer_question(
    "What is GST for invoice INV-2026-0142?",
    "restart-test-session"
))
"""

    second_process = """
invoice = {
    "company_name": "Larkfield Stationers",
    "invoice_number": "INV-2026-0142",
    "invoice_date": "18 September 2026",
    "subtotal": "14702.00",
    "gst": "2646.36",
    "total_due": "17348.36"
}

import src.agentic_rag as rag

rag.load_invoice_json_files = lambda folder: [invoice]
rag.search_by_invoice_number = lambda invoices, number: invoice
rag.ask_llm = lambda prompt: "Total Due: 17348.36"

print(rag.answer_question(
    "What is its total amount?",
    "restart-test-session"
))
"""

    first = subprocess.run(
        [sys.executable, "-c", first_process],
        capture_output=True,
        text=True,
        env=env
    )

    second = subprocess.run(
        [sys.executable, "-c", second_process],
        capture_output=True,
        text=True,
        env=env
    )

    assert first.returncode == 0, first.stderr
    assert second.returncode == 0, second.stderr

    assert "GST: 2646.36" in first.stdout
    assert "Total Due: 17348.36" in second.stdout
