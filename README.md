# 🚀 DocuMind AI

## AI-Powered Document Analysis & Extraction API

Built for **GUVI Hackathon 2026 – Intern Hiring Challenge**

---

## 📌 Overview

**DocuMind AI** is a production-ready backend API that processes and analyzes documents across multiple formats.

It supports **PDF, DOCX, and image files**, extracts text, and returns structured insights:

* Concise summaries
* Key entity extraction
* Sentiment classification

Designed for **robust API evaluation**, making it ideal for automated testing environments.

---

## 🎯 Problem Statement

Build an intelligent system that can:

* Support multiple document formats
* Extract readable text
* Summarize content
* Identify important entities
* Analyze sentiment

---

## 🧠 Solution

DocuMind AI transforms **unstructured documents into structured insights** via a single API.

Applicable across:

* Business operations
* Legal workflows
* Finance
* HR
* Education
* Automation systems

---

## ✨ Core Features

### 📄 Multi-Format Support

* PDF
* DOCX
* Images (OCR)

### 🔍 Intelligent Extraction

* PDF → PyMuPDF
* DOCX → python-docx
* Images → Tesseract OCR

### 🧠 AI Analysis

* Summary
* Entity extraction:

  * Names
  * Dates
  * Organizations
  * Amounts
  * Locations
* Sentiment:

  * Positive / Negative / Neutral

### 🔐 Secure API

* `x-api-key` authentication

### ⚙️ Robust Validation

Handles:

* Invalid API keys
* Unsupported file types
* Malformed base64
* Empty payloads
* Extraction failures

---

## 🏗️ System Architecture

### 🔄 Flow

```
Client
  ↓
FastAPI Layer
  ↓
Auth + Validation
  ↓
Document Processing
  ├── PDF
  ├── DOCX
  └── OCR
  ↓
AI Analysis
  ├── Summary
  ├── Entities
  └── Sentiment
  ↓
JSON Response
```

---

### 🧩 Internal Structure

```
app/
├── api/
├── models/
├── services/
│   ├── extractors
│   ├── analyzer
│   ├── summarizer
│   ├── entity extractor
│   └── sentiment analyzer
├── utils/
├── config.py
└── main.py
```

---

## 🔄 Request Flow

### 1. Validation

* Headers
* API key
* Schema
* File type
* Base64

### 2. Extraction

* PDF → PyMuPDF
* DOCX → python-docx
* Image → Tesseract

### 3. Analysis

* Summary
* Entities
* Sentiment

### 4. Response

* Structured JSON

---

## 🧠 Tech Stack

### Backend

* FastAPI
* Python

### Processing

* PyMuPDF
* python-docx
* Pillow
* Tesseract OCR

### AI / NLP

* Regex + heuristics
* VADER sentiment
* Extractive summarization

### DevOps

* Docker
* Render
* GitHub

---

## 📂 Project Structure

```
documind-ai/
├── backend/
├── test_files/
├── test_api.py
├── render.yaml
└── README.md
```

---

## 🌐 Deployment

### Base URL

```
https://documind-ai-2s72.onrender.com
```

### Docs

```
/docs
```

### Health

```
/health
```

### Endpoint

```
POST /api/document-analyze
```

---

## 🔌 API Spec

### Headers

```
x-api-key: documind123
Content-Type: application/json
```

### Request

```json
{
  "fileName": "sample.pdf",
  "fileType": "pdf",
  "fileBase64": "BASE64_STRING"
}
```

### File Types

| Type  | Value |
| ----- | ----- |
| PDF   | pdf   |
| DOCX  | docx  |
| Image | image |

---

## 📥 Example Request

```bash
curl -X POST ".../api/document-analyze" \
-H "x-api-key: documind123" \
-H "Content-Type: application/json" \
-d '{ ... }'
```

---

## 📤 Success Response

```json
{
  "status": "success",
  "fileName": "invoice.pdf",
  "summary": "...",
  "entities": {
    "names": [],
    "dates": [],
    "organizations": [],
    "amounts": [],
    "locations": []
  },
  "sentiment": "Positive"
}
```

---

## ❌ Error Response

```json
{
  "status": "error",
  "error": {
    "code": "INVALID_BASE64",
    "message": "Invalid base64 encoding"
  }
}
```

---

## 🧪 Testing

### Manual

* Swagger
* Postman
* cURL

### Automated

```
python test_api.py
```

Covers:

* All formats
* Errors
* Validation

---

## 💻 Local Setup

### 1. Clone

```bash
git clone <repo>
cd documind-ai/backend
```

### 2. Env

```bash
python -m venv venv
```

### 3. Install

```bash
pip install -r requirements.txt
```

### 4. Config

```
API_KEY=documind123
```

### 5. Run

```bash
uvicorn app.main:app --reload
```

---

## 🔑 Evaluation

* Header: `x-api-key: documind123`
* Endpoint: `/api/document-analyze`

---

## 🏆 Highlights

* Clean modular architecture
* Multi-format + OCR support
* Structured AI pipeline
* Strong validation
* Deployment-ready
* Hackathon-optimized

---

## ⚠️ Limitations

* OCR depends on image quality
* Heuristic entity extraction
* Complex layouts may affect accuracy

---

## 🚀 Future Improvements

* Advanced OCR
* Better NER models
* Confidence scores
* Batch processing
* Async jobs
* Dashboard UI

---

## 👨‍💻 Author

**Atharv Navatre**
GUVI Hackathon 2026

---

## 📜 License

Educational / portfolio use
