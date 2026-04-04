"""
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
