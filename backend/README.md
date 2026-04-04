# DocuMind AI - Backend

AI-Powered Document Analysis & Extraction API

## Quick Start

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
copy .env.example .env

# Edit .env and set your API_KEY

# Run the server
uvicorn app.main:app --reload
```

## API Endpoints

- `GET /` - API info
- `GET /health` - Health check
- `POST /api/document-analyze` - Analyze document (requires x-api-key header)

## Test

Open http://localhost:8000/docs for Swagger UI
