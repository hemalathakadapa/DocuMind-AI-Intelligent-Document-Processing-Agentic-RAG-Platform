import os
import uuid

import requests
import streamlit as st


# FastAPI backend address
API_URL = os.getenv(
    "API_URL",
    "http://127.0.0.1:8000"
)

# Page configuration
st.set_page_config(
    page_title="DocuMind AI",
    page_icon="📄",
    layout="wide"
)


# Initialize session state
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "invoice_result" not in st.session_state:
    st.session_state.invoice_result = None

if "messages" not in st.session_state:
    st.session_state.messages = []


# Application heading
st.title("📄 DocuMind AI")
st.subheader("Intelligent Document Processing & Agentic RAG Platform")

st.caption("Upload invoices, extract information, validate totals, and ask AI questions.")

st.divider()


# Backend connection check
try:
    health_response = requests.get(
        f"{API_URL}/health",
        timeout=5
    )
    api_status = health_response.status_code == 200
except requests.RequestException:
    api_status = False


if api_status:
    st.success("Backend API Connected")
else:
    st.error("Backend API is not running. Please start FastAPI first.")


# Two-column dashboard
upload_col, chat_col = st.columns(2)


# -----------------------------------
# LEFT SIDE: Invoice Upload
# -----------------------------------

with upload_col:

    st.header("📤 Upload Invoice")

    uploaded_file = st.file_uploader(
        "Choose a PDF invoice",
        type=["pdf"]
    )

    if st.button(
        "Process Invoice",
        disabled=uploaded_file is None or not api_status
    ):

        try:
            with st.spinner("Processing invoice..."):

                response = requests.post(
                    f"{API_URL}/upload-invoice",
                    files={
                        "file": (
                            uploaded_file.name,
                            uploaded_file.getvalue(),
                            "application/pdf"
                        )
                    },
                    timeout=180
                )

            if response.status_code == 200:

                st.session_state.invoice_result = response.json()

                st.success("Invoice processed successfully!")

            else:
                st.error(f"Upload failed: {response.text}")

        except requests.RequestException as error:
            st.error(f"API connection error: {error}")


    # Display invoice details
    if st.session_state.invoice_result:

        result = st.session_state.invoice_result
        invoice = result["invoice_fields"]

        st.subheader("Extracted Invoice Details")

        st.write("**Company:**", invoice.get("company_name"))
        st.write("**Invoice Number:**", invoice.get("invoice_number"))
        st.write("**Invoice Date:**", invoice.get("invoice_date"))

        st.metric(
            "Subtotal",
            f"₹{invoice.get('subtotal', 0)}"
        )

        st.metric(
            "GST",
            f"₹{invoice.get('gst', 0)}"
        )

        st.metric(
            "Total Due",
            f"₹{invoice.get('total_due', 0)}"
        )

        if result.get("is_valid"):
            st.success("Invoice Validation: Valid")
        else:
            st.warning("Invoice Validation: Invalid")

        if result.get("database_saved"):
            st.success("Invoice saved to database.")
        else:
            st.info("Invoice was not saved to database.")


# -----------------------------------
# RIGHT SIDE: AI Chat
# -----------------------------------

with chat_col:

    st.header("🤖 Ask DocuMind AI")

    st.caption(
        "Ask questions about your uploaded invoice."
    )

    # Display previous conversation
    for message in st.session_state.messages:

        with st.chat_message(message["role"]):
            st.markdown(message["content"])


    # User question
    question = st.chat_input(
        "Ask a question about your invoice..."
    )

    if question:

        st.session_state.messages.append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):

            with st.spinner("AI is thinking..."):

                try:

                    response = requests.post(
                        f"{API_URL}/ask",
                        json={
                            "question": question,
                            "session_id": st.session_state.session_id
                        },
                        timeout=180
                    )

                    if response.status_code == 200:

                        answer = response.json()["answer"]

                    else:

                        answer = f"API Error: {response.text}"

                except requests.RequestException as error:

                    answer = f"Connection error: {error}"

                st.markdown(answer)

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer
        })
