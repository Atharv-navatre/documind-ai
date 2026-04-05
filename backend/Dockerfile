# DocuMind AI - Dockerfile for Render Deployment
# ================================================

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies (including Tesseract OCR)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy English model
RUN python -m spacy download en_core_web_sm

# Copy application code
COPY app/ ./app/

# Expose port
EXPOSE 8000

# Start command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
