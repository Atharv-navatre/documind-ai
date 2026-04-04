"""
Document Extractor - Central Extraction Service
================================================
Routes documents to the appropriate extractor based on file type.
"""

from typing import Tuple

from app.utils.file_utils import save_temp_file, cleanup_temp_file
from app.services.pdf_extractor import extract_text_from_pdf
from app.services.docx_extractor import extract_text_from_docx
from app.services.image_extractor import extract_text_from_image


def extract_text(file_bytes: bytes, file_type: str) -> Tuple[str, int]:
    """
    Extracts text from a document based on its type.
    
    This is the main entry point for document extraction.
    It saves the file temporarily, calls the appropriate extractor,
    and cleans up afterward.
    
    Args:
        file_bytes: The file content as bytes
        file_type: Type of file ('pdf', 'docx', 'image')
    
    Returns:
        Tuple[str, int]: (extracted_text, character_count)
    
    Raises:
        ValueError: If file type is not supported or extraction fails
    """
    temp_file_path = None
    
    try:
        # Step 1: Save to temporary file
        temp_file_path = save_temp_file(file_bytes, file_type)
        
        # Step 2: Extract text based on file type
        if file_type == "pdf":
            text = extract_text_from_pdf(temp_file_path)
        elif file_type == "docx":
            text = extract_text_from_docx(temp_file_path)
        elif file_type == "image":
            text = extract_text_from_image(temp_file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_type}")
        
        # Step 3: Return text and character count
        char_count = len(text)
        
        return text, char_count
        
    finally:
        # Step 4: Always clean up temp file
        if temp_file_path:
            cleanup_temp_file(temp_file_path)


def get_extraction_summary(text: str, file_type: str) -> str:
    """
    Generates a brief summary of the extraction result.
    
    Args:
        text: The extracted text
        file_type: Type of file that was processed
    
    Returns:
        str: A summary message
    """
    char_count = len(text)
    word_count = len(text.split())
    
    # Get first 100 characters as preview
    preview = text[:100].replace('\n', ' ').strip()
    if len(text) > 100:
        preview += "..."
    
    return (
        f"Successfully extracted {char_count:,} characters ({word_count:,} words) "
        f"from {file_type.upper()} document."
    )
