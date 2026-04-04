# 🚀 DocuMind AI

### AI-Powered Document Analysis & Extraction API

Built for **GUVI Hackathon 2026 – Intern Hiring Challenge**

---

## 📌 Overview

**DocuMind AI** is a production-ready backend API that intelligently processes and analyzes documents across multiple formats.

It accepts **PDF**, **DOCX**, and **image-based documents**, extracts textual content, and returns structured AI-powered insights such as:

* concise summaries
* key entities
* sentiment classification

The system is designed specifically for **robust API evaluation**, making it suitable for automated testing environments like the GUVI hackathon endpoint tester.

---

## 🎯 Problem Statement

**AI-Powered Document Analysis & Extraction**

Build an intelligent document processing system that can:

* support multiple document formats
* extract readable text
* summarize content
* identify important entities
* analyze overall sentiment

---

## ✨ Key Features

### 📄 Multi-Format Document Support

Supports:

* **PDF**
* **DOCX**
* **Image files (OCR)**

---

### 🔍 Intelligent Text Extraction

Automatically extracts text from uploaded documents using format-specific parsing and OCR.

* **PDF text extraction**
* **Word document parsing**
* **Image OCR using Tesseract**

---

### 🧠 AI-Powered Analysis

Each processed document returns:

* **Summary** → concise explanation of document content
* **Entities** → extraction of:

  * Names
  * Dates
  * Organizations
  * Monetary Amounts
  * Locations
* **Sentiment** → classification as:

  * Positive
  * Negative
  * Neutral

---

### 🔐 Secure API Access

The API uses **`x-api-key` authentication** to protect access and match the hackathon’s endpoint testing requirements.

---

### ⚙️ Robust Validation & Error Handling

The system safely handles:

* invalid API keys
* unsupported file types
* malformed base64 input
* empty payloads
* processing failures

---

## 🏗️ System Architecture

The backend is designed with a clean modular architecture:

```text
Client Request
   ↓
FastAPI Endpoint
   ↓
Authentication + Validation
   ↓
Document Extraction Layer
   ├── PDF Extractor
   ├── DOCX Extractor
   └── Image OCR Extractor
   ↓
Analysis Layer
   ├── Summarizer
   ├── Entity Extractor
   └── Sentiment Analyzer
   ↓
Structured JSON Response
```

---

## 🧠 Tech Stack

### Backend

* **FastAPI**
* **Python**

### Document Processing

* **PyMuPDF** → PDF extraction
* **python-docx** → DOCX extraction
* **Pillow** → image handling
* **Tesseract OCR** → text extraction from images

### NLP / AI Processing

* **Regex + heuristics** → structured entity extraction
* **VADER Sentiment Analysis** → document sentiment classification
* **Extractive summarization logic** → concise content summary

### Deployment

* **Render / Railway compatible**

---

## 📂 Project Structure

```text
documind-ai/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── models/
│   │   ├── services/
│   │   ├── utils/
│   │   ├── config.py
│   │   └── main.py
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
│
├── test_files/
├── test_api.py
├── .gitignore
└── README.md
```

---

## 🔌 API Specification

### Endpoint

```http
POST /api/document-analyze
```

---

### Required Headers

```http
x-api-key: YOUR_API_KEY
Content-Type: application/json
```

---

### Request Body

```json
{
  "fileName": "sample.pdf",
  "fileType": "pdf",
  "fileBase64": "BASE64_ENCODED_FILE"
}
```

---

### Supported File Types

| File Type | Value   |
| --------- | ------- |
| PDF       | `pdf`   |
| DOCX      | `docx`  |
| Image     | `image` |

---

## 📤 Example Success Response

```json
{
  "status": "success",
  "fileName": "sample.pdf",
  "summary": "This document discusses recent developments in artificial intelligence and its impact on industry growth.",
  "entities": {
    "names": ["Nina Lane"],
    "dates": ["June 2020"],
    "organizations": ["Acme Corporation"],
    "amounts": ["$2,500.00"],
    "locations": ["New York, NY"]
  },
  "sentiment": "Positive"
}
```

---

## ❌ Example Error Response

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

## 🧪 Local Development Setup

### 1) Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/documind-ai.git
cd documind-ai
```

---

### 2) Create virtual environment

```bash
cd backend
python -m venv venv
```

#### Windows

```bash
venv\Scripts\activate
```

#### macOS / Linux

```bash
source venv/bin/activate
```

---

### 3) Install dependencies

```bash
pip install -r requirements.txt
```

---

### 4) Configure environment variables

Create a `.env` file inside `backend/`:

```env
API_KEY=documind123
```

You can also use the provided:

```text
.env.example
```

---

### 5) Run the backend server

```bash
uvicorn app.main:app --reload
```

Then open:

```text
http://127.0.0.1:8000/docs
```

This opens the interactive **Swagger UI** for testing the API.

---

## 🧪 Automated Testing

A simple automated API test script is included:

```bash
python test_api.py
```

This verifies:

* PDF analysis
* DOCX analysis
* image OCR analysis
* invalid API key handling
* unsupported file type validation
* empty file validation
* malformed base64 validation

---

## 🔑 API Key for Evaluation

For hackathon evaluation, use:

```text
x-api-key: documind123
```

> This key is provided for testing/demo purposes only.

---

## 🎥 Demo Video

**Demo Video Link:**
*Add your YouTube or Google Drive demo link here*

---

## 🌐 Live Deployment

**Live API URL:**
*Add your deployed backend URL here*

**Swagger Docs:**
*Add your `/docs` link here*

Example:

```text
https://your-app.onrender.com/docs
```

---

## 🤖 AI Tools Used

As required by the hackathon rules, the following AI tools were used during development:

* **ChatGPT** → project planning, debugging, architecture guidance
* **Claude** → implementation support and refinement
* **GitHub Copilot** → code completion and development assistance

---

## ⚠️ Known Limitations

* OCR accuracy depends on image quality and text clarity
* Entity extraction is heuristic-based and may include occasional noisy outputs
* Complex document layouts may reduce extraction accuracy
* This project is optimized for hackathon evaluation and production-style robustness within limited build time

---

## 🚀 Future Improvements

Potential enhancements include:

* better layout-aware OCR
* stronger named entity recognition models
* confidence scores for extracted entities
* batch document processing
* frontend upload dashboard
* async background task processing

---

## 🏆 Hackathon Submission Focus

This project was designed to maximize performance for the **GUVI Hackathon 2026 API Endpoint Tester** by prioritizing:

* API stability
* clean request/response handling
* multi-format support
* modular backend design
* automated validation readiness

---

## 👨‍💻 Author

**Atharv Navatre**

Built as part of **GUVI Hackathon 2026 – Intern Hiring Challenge**

---

## 📜 License

This project is developed for educational and hackathon submission purposes.
