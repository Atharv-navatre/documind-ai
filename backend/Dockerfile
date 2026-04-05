FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (including Tesseract OCR)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Download spaCy English model
RUN python -m spacy download en_core_web_sm

# Copy app files
COPY . .

# Expose port
EXPOSE 10000

# Start app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "10000"]