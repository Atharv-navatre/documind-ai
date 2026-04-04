"""
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
