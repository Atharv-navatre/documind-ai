"""
Image OCR Extractor
===================
Extracts text from images using Tesseract OCR via pytesseract.
"""

import pytesseract
from PIL import Image


def extract_text_from_image(file_path: str) -> str:
    """
    Extracts text from an image file using OCR.
    
    Args:
        file_path: Path to the image file
    
    Returns:
        str: Extracted text from the image
    
    Raises:
        ValueError: If image cannot be opened or OCR fails
    """
    try:
        # Open image with Pillow
        image = Image.open(file_path)
        
        # Convert to RGB if necessary (handles PNG with alpha, etc.)
        if image.mode in ('RGBA', 'LA', 'P'):
            # Create white background
            background = Image.new('RGB', image.size, (255, 255, 255))
            if image.mode == 'P':
                image = image.convert('RGBA')
            background.paste(image, mask=image.split()[-1] if 'A' in image.mode else None)
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Perform OCR
        text = pytesseract.image_to_string(image)
        
        # Clean up
        text = clean_extracted_text(text)
        
        if not text.strip():
            raise ValueError("No text could be extracted from image (image may be empty or unreadable)")
        
        return text
        
    except pytesseract.TesseractNotFoundError:
        raise ValueError(
            "Tesseract OCR is not installed or not in PATH. "
            "Please install Tesseract: https://github.com/tesseract-ocr/tesseract"
        )
    except Exception as e:
        if "cannot identify image" in str(e).lower():
            raise ValueError(f"Invalid or corrupted image file: {e}")
        raise ValueError(f"Failed to extract text from image: {e}")


def clean_extracted_text(text: str) -> str:
    """
    Cleans OCR-extracted text by removing excessive whitespace.
    
    Args:
        text: Raw OCR text
    
    Returns:
        str: Cleaned text
    """
    import re
    
    # Replace multiple newlines with double newline
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Replace multiple spaces with single space
    text = re.sub(r' {2,}', ' ', text)
    
    # Strip leading/trailing whitespace
    text = text.strip()
    
    return text
