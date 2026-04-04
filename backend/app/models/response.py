"""
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
