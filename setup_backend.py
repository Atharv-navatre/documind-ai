"""
DocuMind AI - Backend Setup Script
===================================
Run this script to create the entire backend structure.
Usage: python setup_backend.py
"""

import os

# Base path - CHANGE THIS IF NEEDED
BASE_PATH = r"D:\Hackathon Projects\documind-ai"

# All files with their contents
FILES = {
    # ==========================================================================
    # requirements.txt
    # ==========================================================================
    "backend/requirements.txt": """# DocuMind AI - Backend Dependencies

# FastAPI & Server
fastapi==0.109.0
uvicorn[standard]==0.27.0
python-multipart==0.0.6

# Environment & Configuration
python-dotenv==1.0.0
pydantic==2.5.3
pydantic-settings==2.1.0

# Document Processing (for next phase)
PyMuPDF==1.23.8
python-docx==1.1.0
pytesseract==0.3.10
Pillow==10.2.0

# NLP & Analysis (for next phase)
spacy==3.7.2
vaderSentiment==3.3.2
sumy==0.11.0
nltk==3.8.1

# Utilities
httpx==0.26.0
""",

    # ==========================================================================
    # .env.example
    # ==========================================================================
    "backend/.env.example": """# DocuMind AI - Environment Variables
# Copy this file to .env and update the values

# API Security (REQUIRED - change this!)
API_KEY=your-secure-api-key-here

# Environment
ENVIRONMENT=development

# File Processing Limits
MAX_FILE_SIZE_MB=10
""",

    # ==========================================================================
    # .gitignore
    # ==========================================================================
    "backend/.gitignore": """# Environment
.env
.env.local
.env.*.local

# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
.venv/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Testing
.pytest_cache/
htmlcov/
.coverage

# Temp files
*.tmp
*.temp
temp/

# OS
.DS_Store
Thumbs.db
""",

    # ==========================================================================
    # README.md
    # ==========================================================================
    "backend/README.md": """# DocuMind AI - Backend

AI-Powered Document Analysis & Extraction API

## Quick Start

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\\Scripts\\activate

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
""",

    # ==========================================================================
    # app/__init__.py
    # ==========================================================================
    "backend/app/__init__.py": '''"""
DocuMind AI - Backend Application
GUVI Hackathon 2026
"""

__version__ = "1.0.0"
''',

    # ==========================================================================
    # app/config.py
    # ==========================================================================
    "backend/app/config.py": '''"""
Configuration settings loaded from environment variables.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from .env file."""
    
    # API Security
    api_key: str = "default-dev-key-change-me"
    
    # Environment
    environment: str = "development"
    
    # File Processing Limits
    max_file_size_mb: int = 10
    
    # App Info
    app_name: str = "DocuMind AI"
    app_version: str = "1.0.0"
    app_description: str = "AI-Powered Document Analysis & Extraction API"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Returns cached settings instance."""
    return Settings()
''',

    # ==========================================================================
    # app/main.py
    # ==========================================================================
    "backend/app/main.py": '''"""
DocuMind AI - FastAPI Application Entry Point
Run with: uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.api.routes import document

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    description=settings.app_description,
    version=settings.app_version,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(document.router)


@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - API info."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "environment": settings.environment}
''',

    # ==========================================================================
    # app/api/__init__.py
    # ==========================================================================
    "backend/app/api/__init__.py": '''"""API package."""
''',

    # ==========================================================================
    # app/api/dependencies.py
    # ==========================================================================
    "backend/app/api/dependencies.py": '''"""
API Dependencies - API key validation.
"""

from fastapi import Header, HTTPException, status
from app.config import get_settings


async def verify_api_key(
    x_api_key: str = Header(..., description="API Key for authentication")
) -> str:
    """Validates the x-api-key header."""
    settings = get_settings()
    
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "status": "error",
                "error": {
                    "code": "MISSING_API_KEY",
                    "message": "x-api-key header is required"
                }
            }
        )
    
    if x_api_key != settings.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "status": "error",
                "error": {
                    "code": "INVALID_API_KEY",
                    "message": "Invalid API key provided"
                }
            }
        )
    
    return x_api_key
''',

    # ==========================================================================
    # app/api/routes/__init__.py
    # ==========================================================================
    "backend/app/api/routes/__init__.py": '''"""Routes package."""
''',

    # ==========================================================================
    # app/api/routes/document.py
    # ==========================================================================
    "backend/app/api/routes/document.py": '''"""
Document Analysis Routes
Endpoint: POST /api/document-analyze
"""

from fastapi import APIRouter, Depends, HTTPException, status
from app.models.request import DocumentAnalyzeRequest
from app.models.response import DocumentAnalyzeResponse, Entities, ErrorResponse
from app.api.dependencies import verify_api_key
from app.utils.file_utils import decode_base64_file, get_file_size_mb
from app.config import get_settings

router = APIRouter(prefix="/api", tags=["Document Analysis"])


@router.post(
    "/document-analyze",
    response_model=DocumentAnalyzeResponse,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
    },
    summary="Analyze a document",
    description="Extract text, summarize, extract entities, and analyze sentiment from PDF, DOCX, or image files."
)
async def analyze_document(
    request: DocumentAnalyzeRequest,
    api_key: str = Depends(verify_api_key)
) -> DocumentAnalyzeResponse:
    """Main document analysis endpoint."""
    settings = get_settings()
    
    # Validate file type
    valid_types = ["pdf", "docx", "image"]
    if request.fileType not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status": "error",
                "error": {
                    "code": "INVALID_FILE_TYPE",
                    "message": f"File type '{request.fileType}' not supported. Use: {', '.join(valid_types)}"
                }
            }
        )
    
    # Decode base64
    try:
        file_bytes = decode_base64_file(request.fileBase64)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status": "error",
                "error": {"code": "INVALID_BASE64", "message": str(e)}
            }
        )
    
    # Check file size
    file_size_mb = get_file_size_mb(file_bytes)
    if file_size_mb > settings.max_file_size_mb:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={
                "status": "error",
                "error": {
                    "code": "FILE_TOO_LARGE",
                    "message": f"File size ({file_size_mb:.2f} MB) exceeds limit ({settings.max_file_size_mb} MB)"
                }
            }
        )
    
    # PLACEHOLDER - Real processing in next phase
    return DocumentAnalyzeResponse(
        status="success",
        fileName=request.fileName,
        summary=f"Document '{request.fileName}' received successfully. Size: {file_size_mb:.2f} MB. Full analysis coming in next phase.",
        entities=Entities(),
        sentiment="Neutral"
    )
''',

    # ==========================================================================
    # app/models/__init__.py
    # ==========================================================================
    "backend/app/models/__init__.py": '''"""Models package - Pydantic schemas."""
''',

    # ==========================================================================
    # app/models/request.py
    # ==========================================================================
    "backend/app/models/request.py": '''"""
Request Models - What the API accepts.
"""

from pydantic import BaseModel, Field, field_validator
from typing import Literal


class DocumentAnalyzeRequest(BaseModel):
    """
    Request body for POST /api/document-analyze
    
    Example:
    {
        "fileName": "invoice.pdf",
        "fileType": "pdf",
        "fileBase64": "JVBERi0xLjQK..."
    }
    """
    
    fileName: str = Field(
        ...,
        description="Name of the uploaded file",
        min_length=1,
        max_length=255
    )
    
    fileType: Literal["pdf", "docx", "image"] = Field(
        ...,
        description="Type of file: pdf, docx, or image"
    )
    
    fileBase64: str = Field(
        ...,
        description="Base64 encoded file content",
        min_length=1
    )
    
    @field_validator("fileName")
    @classmethod
    def validate_filename(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("fileName cannot be empty")
        return v
    
    @field_validator("fileBase64")
    @classmethod
    def validate_base64(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("fileBase64 cannot be empty")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "fileName": "sample.pdf",
                "fileType": "pdf",
                "fileBase64": "JVBERi0xLjQKJeLjz9MK..."
            }
        }
''',

    # ==========================================================================
    # app/models/response.py
    # ==========================================================================
    "backend/app/models/response.py": '''"""
Response Models - What the API returns.
"""

from pydantic import BaseModel, Field
from typing import List, Literal


class Entities(BaseModel):
    """Extracted entities from document."""
    names: List[str] = Field(default_factory=list, description="Person names")
    dates: List[str] = Field(default_factory=list, description="Dates found")
    organizations: List[str] = Field(default_factory=list, description="Organizations")
    amounts: List[str] = Field(default_factory=list, description="Monetary amounts")
    locations: List[str] = Field(default_factory=list, description="Locations")


class DocumentAnalyzeResponse(BaseModel):
    """
    Successful response for POST /api/document-analyze
    
    Matches GUVI Hackathon required format.
    """
    status: Literal["success"] = "success"
    fileName: str = Field(..., description="Original file name")
    summary: str = Field(..., description="Document summary")
    entities: Entities = Field(..., description="Extracted entities")
    sentiment: str = Field(..., description="Sentiment: Positive, Negative, or Neutral")


class ErrorDetail(BaseModel):
    """Error detail structure."""
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")


class ErrorResponse(BaseModel):
    """Error response structure."""
    status: Literal["error"] = "error"
    error: ErrorDetail
''',

    # ==========================================================================
    # app/services/__init__.py
    # ==========================================================================
    "backend/app/services/__init__.py": '''"""
Services Package - Business logic modules.
Will contain: document_processor, extractors, analyzers
"""
''',

    # ==========================================================================
    # app/utils/__init__.py
    # ==========================================================================
    "backend/app/utils/__init__.py": '''"""Utils package."""
''',

    # ==========================================================================
    # app/utils/file_utils.py
    # ==========================================================================
    "backend/app/utils/file_utils.py": '''"""
File Utilities - Base64 decoding and file helpers.
"""

import base64


def decode_base64_file(base64_string: str) -> bytes:
    """
    Decodes base64 string to bytes.
    Handles both plain base64 and data URL format.
    """
    try:
        base64_string = base64_string.strip()
        
        # Handle data URL format (e.g., "data:application/pdf;base64,...")
        if base64_string.startswith("data:"):
            parts = base64_string.split(",", 1)
            if len(parts) == 2:
                base64_string = parts[1]
        
        file_bytes = base64.b64decode(base64_string)
        
        if not file_bytes:
            raise ValueError("Decoded file is empty")
        
        return file_bytes
        
    except base64.binascii.Error as e:
        raise ValueError(f"Invalid base64 encoding: {e}")
    except Exception as e:
        raise ValueError(f"Failed to decode base64: {e}")


def get_file_size_mb(file_bytes: bytes) -> float:
    """Returns file size in megabytes."""
    return round(len(file_bytes) / (1024 * 1024), 2)


def validate_pdf_header(file_bytes: bytes) -> bool:
    """Checks if file starts with PDF magic number."""
    return file_bytes[:4] == b'%PDF'


def validate_docx_header(file_bytes: bytes) -> bool:
    """Checks if file starts with DOCX/ZIP magic number."""
    return file_bytes[:4] == b'PK\\x03\\x04'
''',
}


def main():
    print("=" * 60)
    print("DocuMind AI - Backend Setup")
    print("=" * 60)
    
    # Create all files
    for relative_path, content in FILES.items():
        full_path = os.path.join(BASE_PATH, relative_path)
        
        # Create directory if needed
        dir_path = os.path.dirname(full_path)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
            print(f"[DIR]  Created: {dir_path}")
        
        # Write file
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content.strip() + "\n")
        print(f"[FILE] Created: {relative_path}")
    
    print("=" * 60)
    print("SUCCESS! All files created.")
    print("=" * 60)
    print()
    print("Next steps:")
    print(f"  1. cd \"{os.path.join(BASE_PATH, 'backend')}\"")
    print("  2. python -m venv venv")
    print("  3. venv\\Scripts\\activate")
    print("  4. pip install -r requirements.txt")
    print("  5. copy .env.example .env")
    print("  6. Edit .env and set your API_KEY")
    print("  7. uvicorn app.main:app --reload")
    print()
    print("Then open: http://localhost:8000/docs")
    print("=" * 60)


if __name__ == "__main__":
    main()
