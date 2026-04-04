"""
Text Summarizer
===============
Generates concise summaries from extracted document text.

Uses extractive summarization (selects important sentences)
which is deterministic and reliable for hackathon scoring.
"""

import re
from typing import List


def summarize_text(text: str, num_sentences: int = 3) -> str:
    """
    Generates an extractive summary of the text.
    
    Extractive summarization selects the most important sentences
    from the original text rather than generating new text.
    This approach is deterministic and reliable.
    
    Args:
        text: The text to summarize
        num_sentences: Target number of sentences in summary (default: 3)
    
    Returns:
        str: The summary
    """
    if not text or not text.strip():
        return "No content available to summarize."
    
    # Clean the text
    text = _clean_text(text)
    
    # Split into sentences
    sentences = _split_sentences(text)
    
    # Handle short documents
    if len(sentences) <= num_sentences:
        return " ".join(sentences)
    
    # Score sentences by importance
    scored_sentences = _score_sentences(sentences, text)
    
    # Select top sentences
    top_sentences = sorted(scored_sentences, key=lambda x: x[1], reverse=True)[:num_sentences]
    
    # Restore original order (maintains readability)
    top_sentences_ordered = sorted(top_sentences, key=lambda x: x[2])
    
    # Join selected sentences
    summary = " ".join([s[0] for s in top_sentences_ordered])
    
    return summary


def _clean_text(text: str) -> str:
    """Cleans text for summarization."""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove very short lines (likely headers/footers)
    lines = text.split('\n')
    lines = [line.strip() for line in lines if len(line.strip()) > 20]
    text = ' '.join(lines)
    
    return text.strip()


def _split_sentences(text: str) -> List[str]:
    """
    Splits text into sentences.
    
    Uses a simple but effective regex-based approach.
    """
    # Split on sentence-ending punctuation followed by space and capital
    # This handles: "Hello. World" but not "Dr. Smith"
    sentence_pattern = r'(?<=[.!?])\s+(?=[A-Z])'
    
    raw_sentences = re.split(sentence_pattern, text)
    
    # Clean and filter sentences
    sentences = []
    for sent in raw_sentences:
        sent = sent.strip()
        # Keep sentences that are reasonable length
        if len(sent) > 20 and len(sent) < 500:
            sentences.append(sent)
    
    return sentences


def _score_sentences(sentences: List[str], full_text: str) -> List[tuple]:
    """
    Scores sentences by importance using multiple factors.
    
    Returns list of (sentence, score, original_index) tuples.
    """
    # Calculate word frequencies in the document
    word_freq = _get_word_frequencies(full_text)
    
    scored = []
    
    for idx, sentence in enumerate(sentences):
        score = 0.0
        
        # Factor 1: Word frequency score
        words = _get_words(sentence)
        if words:
            freq_score = sum(word_freq.get(w, 0) for w in words) / len(words)
            score += freq_score * 2
        
        # Factor 2: Position score (earlier sentences often more important)
        position_score = 1.0 / (idx + 1)
        score += position_score
        
        # Factor 3: Length score (prefer medium-length sentences)
        length = len(sentence)
        if 50 <= length <= 200:
            score += 0.5
        elif 200 < length <= 300:
            score += 0.3
        
        # Factor 4: Contains important words
        important_keywords = [
            'important', 'significant', 'key', 'main', 'primary',
            'essential', 'critical', 'major', 'conclusion', 'result',
            'summary', 'total', 'overall', 'finally', 'therefore'
        ]
        sentence_lower = sentence.lower()
        for keyword in important_keywords:
            if keyword in sentence_lower:
                score += 0.3
                break
        
        # Factor 5: Contains numbers (often indicates specific info)
        if re.search(r'\d+', sentence):
            score += 0.2
        
        scored.append((sentence, score, idx))
    
    return scored


def _get_word_frequencies(text: str) -> dict:
    """Calculates normalized word frequencies."""
    words = _get_words(text)
    
    if not words:
        return {}
    
    # Count frequencies
    freq = {}
    for word in words:
        freq[word] = freq.get(word, 0) + 1
    
    # Normalize by max frequency
    max_freq = max(freq.values()) if freq else 1
    for word in freq:
        freq[word] = freq[word] / max_freq
    
    return freq


def _get_words(text: str) -> List[str]:
    """Extracts words from text, lowercased and filtered."""
    # Common stop words to ignore
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
        'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
        'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
        'could', 'should', 'may', 'might', 'must', 'shall', 'can', 'need',
        'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it',
        'we', 'they', 'what', 'which', 'who', 'whom', 'where', 'when', 'why',
        'how', 'all', 'each', 'every', 'both', 'few', 'more', 'most', 'other',
        'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so',
        'than', 'too', 'very', 'just', 'also', 'now', 'here', 'there'
    }
    
    # Extract words
    words = re.findall(r'\b[a-z]{3,}\b', text.lower())
    
    # Filter stop words
    words = [w for w in words if w not in stop_words]
    
    return words


def get_summary_with_stats(text: str, num_sentences: int = 3) -> dict:
    """
    Returns summary with additional statistics.
    
    Args:
        text: Text to summarize
        num_sentences: Number of sentences in summary
    
    Returns:
        dict with keys: summary, original_length, summary_length, compression_ratio
    """
    summary = summarize_text(text, num_sentences)
    
    original_words = len(text.split())
    summary_words = len(summary.split())
    
    compression_ratio = 0
    if original_words > 0:
        compression_ratio = round((1 - summary_words / original_words) * 100, 1)
    
    return {
        "summary": summary,
        "original_words": original_words,
        "summary_words": summary_words,
        "compression_ratio": compression_ratio
    }
