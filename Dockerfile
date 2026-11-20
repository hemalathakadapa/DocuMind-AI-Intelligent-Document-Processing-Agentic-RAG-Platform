
# 1. Use Python 3.12 as the base image
FROM python:3.12-slim

# 2. Set working directory inside container
WORKDIR /app

# 3. Install Tesseract OCR
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# 4. Copy requirements file
COPY requirements.txt .

# 5. Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy project files
COPY src/ ./src/
COPY api/ ./api/
COPY ui/ ./ui/
COPY scripts/ ./scripts/

# 7. Create required data folders
RUN mkdir -p data/uploads data/extracted_data

# 8. Expose FastAPI port

EXPOSE 8000 8501

# 9. Start FastAPI server
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
