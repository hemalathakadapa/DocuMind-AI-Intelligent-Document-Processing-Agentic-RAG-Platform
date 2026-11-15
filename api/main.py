
from pathlib import Path
import shutil
import uuid

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field

from src.pipeline import process_invoice
from src.agentic_rag import answer_question


# Project folders
BASE_DIR = Path(__file__).resolve().parent.parent

UPLOAD_DIR = BASE_DIR / "data" / "uploads"
OUTPUT_DIR = BASE_DIR / "data" / "extracted_data"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# FastAPI application
app = FastAPI(
    title="DocuMind AI",
    description="Intelligent Document Processing and Agentic RAG Platform",
    version="1.0.0"
)


# Request model for AI questions
class QuestionRequest(BaseModel):
    question: str = Field(min_length=1)
    session_id: str = Field(min_length=1)


@app.get("/")
def home():
    return {
        "message": "Welcome to DocuMind AI API",
        "status": "Running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "application": "DocuMind AI"
    }


@app.post("/upload-invoice", summary="Upload and process an invoice PDF")
def upload_invoice(file: UploadFile = File(...)):

    if not file.filename or Path(file.filename).suffix.lower() != ".pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported."
        )

    unique_id = uuid.uuid4().hex

    input_path = UPLOAD_DIR / f"{unique_id}.pdf"
    output_path = OUTPUT_DIR / f"{unique_id}.json"

    try:
        with input_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        result = process_invoice(
            input_path=str(input_path),
            output_path=str(output_path)
        )

        return jsonable_encoder({
            "message": "Invoice processed successfully",
            "filename": file.filename,
            **result
        })

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Invoice processing failed: {str(exc)}"
        )

    finally:
        file.file.close()


@app.post("/ask", summary="Ask questions about an invoice")
def ask_invoice_question(request: QuestionRequest):

    try:
        answer = answer_question(
            question=request.question,
            session_id=request.session_id
        )

        return {
            "question": request.question,
            "session_id": request.session_id,
            "answer": answer
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Question answering failed: {str(exc)}"
        )
