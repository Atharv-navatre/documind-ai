"""
PDF Text Extractor
==================
Extracts text from PDF files using PyMuPDF (fitz).
"""

import fitz  # PyMuPDF


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extracts text from all pages of a PDF file.
    
    Args:
        file_path: Path to the PDF file
    
    Returns:
        str: Combined text from all pages
    
    Raises:
        ValueError: If PDF cannot be opened or read
    """
    try:
        # Open the PDF
        doc = fitz.open(file_path)
        
        # Extract text from each page
        text_parts = []
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_text = page.get_text()
            
            if page_text.strip():
                text_parts.append(page_text)
        
        # Close the document
        doc.close()
        
        # Combine all text
        full_text = "\n\n".join(text_parts)
        
        # Clean up the text
        full_text = clean_extracted_text(full_text)
        
        if not full_text.strip():
            raise ValueError("PDF appears to be empty or contains only images (no extractable text)")
        
        return full_text
        
    except fitz.FileDataError as e:
        raise ValueError(f"Invalid or corrupted PDF file: {e}")
    except Exception as e:
        raise ValueError(f"Failed to extract text from PDF: {e}")


def clean_extracted_text(text: str) -> str:
    """
    Cleans extracted text by removing excessive whitespace.
    
    Args:
        text: Raw extracted text
    
    Returns:
        str: Cleaned text
    """
    # Replace multiple newlines with double newline
    import re
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Replace multiple spaces with single space
    text = re.sub(r' {2,}', ' ', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text
