"""
File Utilities - Base64 decoding, temp file handling, and file helpers.
"""

import base64
import tempfile
import os
from typing import Tuple


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
    return file_bytes[:4] == b'PK\x03\x04'


def get_file_extension(file_type: str) -> str:
    """
    Returns the appropriate file extension for a given file type.
    
    Args:
        file_type: One of 'pdf', 'docx', or 'image'
    
    Returns:
        File extension with dot (e.g., '.pdf')
    """
    extensions = {
        "pdf": ".pdf",
        "docx": ".docx",
        "image": ".png"  # Default to PNG for images
    }
    return extensions.get(file_type, ".bin")


def save_temp_file(file_bytes: bytes, file_type: str) -> str:
    """
    Saves bytes to a temporary file and returns the file path.
    
    The temp file is created with delete=False so it persists until
    we explicitly delete it after processing.
    
    Args:
        file_bytes: The file content as bytes
        file_type: Type of file ('pdf', 'docx', 'image')
    
    Returns:
        str: Path to the temporary file
    
    Raises:
        IOError: If file cannot be written
    """
    extension = get_file_extension(file_type)
    
    try:
        # Create temp file with appropriate extension
        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=extension,
            prefix="documind_"
        )
        temp_file.write(file_bytes)
        temp_file.close()
        
        return temp_file.name
        
    except Exception as e:
        raise IOError(f"Failed to create temporary file: {e}")


def cleanup_temp_file(file_path: str) -> None:
    """
    Safely deletes a temporary file.
    
    Args:
        file_path: Path to the file to delete
    """
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
    except Exception:
        # Silently ignore cleanup errors
        pass


def detect_image_format(file_bytes: bytes) -> str:
    """
    Detects image format from magic bytes.
    
    Args:
        file_bytes: The file content
    
    Returns:
        str: Image format ('png', 'jpg', 'gif', etc.) or 'unknown'
    """
    # PNG
    if file_bytes[:8] == b'\x89PNG\r\n\x1a\n':
        return "png"
    # JPEG
    elif file_bytes[:2] == b'\xff\xd8':
        return "jpg"
    # GIF
    elif file_bytes[:6] in (b'GIF87a', b'GIF89a'):
        return "gif"
    # BMP
    elif file_bytes[:2] == b'BM':
        return "bmp"
    # WebP
    elif file_bytes[:4] == b'RIFF' and file_bytes[8:12] == b'WEBP':
        return "webp"
    # TIFF
    elif file_bytes[:4] in (b'II*\x00', b'MM\x00*'):
        return "tiff"
    else:
        return "unknown"
