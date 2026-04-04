"""
Document Analysis Routes
Endpoint: POST /api/document-analyze
"""

from fastapi import APIRouter, Depends, HTTPException, status
from app.models.request import DocumentAnalyzeRequest
from app.models.response import DocumentAnalyzeResponse, Entities, ErrorResponse
from app.api.dependencies import verify_api_key
from app.utils.file_utils import decode_base64_file, get_file_size_mb
from app.services.document_extractor import extract_text
from app.services.document_analyzer import analyze_document_text
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
    """
    Main document analysis endpoint.
    
    Pipeline:
    1. Validate file type
    2. Decode base64
    3. Check file size
    4. Extract text (PDF/DOCX/Image)
    5. Analyze text (summary, entities, sentiment)
    6. Return structured response
    """
    settings = get_settings()
    
    # Step 1: Validate file type
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
    
    # Step 2: Decode base64
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
    
    # Step 3: Check file size
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
    
    # Step 4: Extract text from document
    try:
        extracted_text, char_count = extract_text(file_bytes, request.fileType)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status": "error",
                "error": {
                    "code": "EXTRACTION_FAILED",
                    "message": str(e)
                }
            }
        )
    
    # Step 5: Analyze the extracted text
    try:
        analysis_result = analyze_document_text(extracted_text)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "status": "error",
                "error": {
                    "code": "ANALYSIS_FAILED",
                    "message": f"Failed to analyze document: {str(e)}"
                }
            }
        )
    
    # Step 6: Build and return response
    return DocumentAnalyzeResponse(
        status="success",
        fileName=request.fileName,
        summary=analysis_result["summary"],
        entities=Entities(
            names=analysis_result["entities"]["names"],
            dates=analysis_result["entities"]["dates"],
            organizations=analysis_result["entities"]["organizations"],
            amounts=analysis_result["entities"]["amounts"],
            locations=analysis_result["entities"]["locations"]
        ),
        sentiment=analysis_result["sentiment"]
    )
