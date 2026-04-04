"""
Document Analyzer - Central Analysis Orchestrator
==================================================
Coordinates all analysis operations:
- Entity extraction
- Sentiment analysis
- Summarization

This module ties together the full analysis pipeline.
"""

from typing import Dict, List, Any

from app.services.entity_extractor import extract_entities
from app.services.sentiment_analyzer import analyze_sentiment
from app.services.summarizer import summarize_text


def analyze_document_text(text: str) -> Dict[str, Any]:
    """
    Performs full analysis on extracted document text.
    
    This is the main entry point for document analysis.
    It calls all three analyzers and returns combined results.
    
    Args:
        text: The extracted text from a document
    
    Returns:
        Dict with keys: summary, entities, sentiment
    """
    # Handle empty or very short text
    if not text or len(text.strip()) < 10:
        return {
            "summary": "Document contains insufficient text for analysis.",
            "entities": {
                "names": [],
                "dates": [],
                "organizations": [],
                "amounts": [],
                "locations": []
            },
            "sentiment": "Neutral"
        }
    
    # Step 1: Generate summary
    summary = _safe_summarize(text)
    
    # Step 2: Extract entities
    entities = _safe_extract_entities(text)
    
    # Step 3: Analyze sentiment
    sentiment = _safe_analyze_sentiment(text)
    
    return {
        "summary": summary,
        "entities": entities,
        "sentiment": sentiment
    }


def _safe_summarize(text: str) -> str:
    """Safely generates summary with error handling."""
    try:
        summary = summarize_text(text, num_sentences=3)
        
        # Ensure summary is not empty
        if not summary or len(summary.strip()) < 10:
            # Fallback: use first 200 characters
            summary = text[:200].strip()
            if len(text) > 200:
                summary += "..."
        
        return summary
        
    except Exception as e:
        # Fallback on any error
        fallback = text[:200].strip()
        if len(text) > 200:
            fallback += "..."
        return fallback


def _safe_extract_entities(text: str) -> Dict[str, List[str]]:
    """Safely extracts entities with error handling."""
    try:
        entities = extract_entities(text)
        return entities
        
    except Exception as e:
        # Return empty entities on error
        return {
            "names": [],
            "dates": [],
            "organizations": [],
            "amounts": [],
            "locations": []
        }


def _safe_analyze_sentiment(text: str) -> str:
    """Safely analyzes sentiment with error handling."""
    try:
        sentiment = analyze_sentiment(text)
        
        # Validate response
        if sentiment not in ["Positive", "Negative", "Neutral"]:
            return "Neutral"
        
        return sentiment
        
    except Exception as e:
        # Default to Neutral on error
        return "Neutral"


def get_analysis_stats(text: str, analysis_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Returns additional statistics about the analysis.
    
    Useful for debugging and understanding results.
    
    Args:
        text: Original text
        analysis_result: Result from analyze_document_text()
    
    Returns:
        Dict with analysis statistics
    """
    entities = analysis_result.get("entities", {})
    
    total_entities = (
        len(entities.get("names", [])) +
        len(entities.get("dates", [])) +
        len(entities.get("organizations", [])) +
        len(entities.get("amounts", [])) +
        len(entities.get("locations", []))
    )
    
    return {
        "text_length": len(text),
        "word_count": len(text.split()),
        "summary_length": len(analysis_result.get("summary", "")),
        "total_entities_found": total_entities,
        "entity_breakdown": {
            "names": len(entities.get("names", [])),
            "dates": len(entities.get("dates", [])),
            "organizations": len(entities.get("organizations", [])),
            "amounts": len(entities.get("amounts", [])),
            "locations": len(entities.get("locations", [])),
        },
        "sentiment": analysis_result.get("sentiment", "Neutral")
    }
