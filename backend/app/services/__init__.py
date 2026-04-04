"""
Services Package - Document processing and analysis modules.

Extraction Modules:
- pdf_extractor: Extract text from PDF files
- docx_extractor: Extract text from DOCX files
- image_extractor: Extract text from images via OCR
- document_extractor: Central extraction service

Analysis Modules:
- entity_extractor: Extract names, dates, organizations, amounts, locations
- sentiment_analyzer: Analyze sentiment (Positive/Negative/Neutral)
- summarizer: Generate extractive summaries
- document_analyzer: Central analysis orchestrator
"""

from app.services.document_extractor import extract_text, get_extraction_summary
from app.services.document_analyzer import analyze_document_text

__all__ = [
    "extract_text",
    "get_extraction_summary",
    "analyze_document_text",
]
