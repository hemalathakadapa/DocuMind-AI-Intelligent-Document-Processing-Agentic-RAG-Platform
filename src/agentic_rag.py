
import re
from typing import TypedDict, Any
import os
from langgraph.graph import StateGraph, START, END
import sqlite3
from pathlib import Path
from langgraph.checkpoint.sqlite import SqliteSaver

from src.document_search import (
    load_invoice_json_files,
    search_by_invoice_number
)

from src.llm_client import ask_llm


INVOICE_FOLDER = "data/extracted_data"

# Persistent conversation memory database
MEMORY_DB_PATH = Path(
    os.getenv(
        "DOCUMIND_MEMORY_DB",
        "data/documind_memory.db"
    )
)

MEMORY_DB_PATH.parent.mkdir(parents=True, exist_ok=True)

connection = sqlite3.connect(
    str(MEMORY_DB_PATH),
    check_same_thread=False
)

memory = SqliteSaver(connection)
memory.setup()
# 1. Define the workflow state
class AgenticRAGState(TypedDict, total=False):
    question: str
    invoice_number: str
    invoice: dict[str, Any]
    status: str
    answer: str


def extract_invoice_node(state: AgenticRAGState):

    question = state["question"]

    match = re.search(
        r"\b[A-Z0-9]+(?:[-/][A-Z0-9]+)+\b",
        question.upper()
    )

    if match:
        return {
            "invoice_number": match.group(0),
            "status": "valid"
        }

    # Use previous invoice number from conversation memory
    previous_invoice = state.get("invoice_number")

    if previous_invoice:
        return {
            "invoice_number": previous_invoice,
            "status": "valid"
        }

    return {
        "status": "invalid",
        "answer": "Please provide a valid invoice number."
    }


# 3. Node: Retrieve invoice
def retrieve_invoice_node(state: AgenticRAGState):

    invoices = load_invoice_json_files(INVOICE_FOLDER)

    invoice = search_by_invoice_number(
        invoices,
        state["invoice_number"]
    )

    if invoice is None:
        return {
            "status": "not_found",
            "answer": (
                f"Invoice {state['invoice_number']} was not found."
            )
        }

    return {
        "invoice": invoice,
        "status": "found"
    }


# 4. Node: Generate answer using Qwen
def generate_answer_node(state: AgenticRAGState):

    invoice = state["invoice"]

    context = f"""
    Company Name: {invoice.get('company_name')}
    Invoice Number: {invoice.get('invoice_number')}
    Invoice Date: {invoice.get('invoice_date')}
    Subtotal: {invoice.get('subtotal')}
    GST: {invoice.get('gst')}
    Total Due: {invoice.get('total_due')}
    """

    prompt = f"""
    You are an invoice assistant.

    Answer using ONLY the invoice information below.
    Do not invent any values.

    Invoice Information:
    {context}

    User Question:
    {state['question']}

    Answer:
    """

    answer = ask_llm(prompt)

    return {
        "answer": answer,
        "status": "completed"
    }


# 5. Conditional routing after invoice extraction
def check_invoice_number(state: AgenticRAGState):

    if state["status"] == "valid":
        return "retrieve"

    return "finish"


# 6. Conditional routing after retrieval
def check_retrieval(state: AgenticRAGState):

    if state["status"] == "found":
        return "generate"

    return "finish"


# 7. Build LangGraph workflow
def build_agentic_rag():

    workflow = StateGraph(AgenticRAGState)

    workflow.add_node(
        "extract_invoice",
        extract_invoice_node
    )

    workflow.add_node(
        "retrieve_invoice",
        retrieve_invoice_node
    )

    workflow.add_node(
        "generate_answer",
        generate_answer_node
    )

    workflow.add_edge(START, "extract_invoice")

    workflow.add_conditional_edges(
        "extract_invoice",
        check_invoice_number,
        {
            "retrieve": "retrieve_invoice",
            "finish": END
        }
    )

    workflow.add_conditional_edges(
        "retrieve_invoice",
        check_retrieval,
        {
            "generate": "generate_answer",
            "finish": END
        }
    )

    workflow.add_edge("generate_answer", END)

    return workflow.compile(checkpointer=memory)

# 8. Public function to ask questions
agentic_rag = build_agentic_rag()


def answer_question(question: str, session_id: str = "default"):

    result = agentic_rag.invoke(
        {"question": question},
        config={
            "configurable": {
                "thread_id": session_id
            }
        }
    )

    return result["answer"]