"""
Sentiment Analyzer (Improved)
=============================
Analyzes sentiment using VADER + keyword-based override for business documents.

Key improvement: Detects negative business contexts (breaches, fraud, incidents)
that VADER often misclassifies as neutral or positive.

Returns one of: Positive, Negative, Neutral
"""

from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re


# Initialize analyzer once (reused across calls)
_analyzer = None


def get_analyzer() -> SentimentIntensityAnalyzer:
    """Returns cached VADER analyzer instance."""
    global _analyzer
    if _analyzer is None:
        _analyzer = SentimentIntensityAnalyzer()
    return _analyzer


# =============================================================================
# KEYWORD LISTS for context-aware sentiment override
# =============================================================================

# Strong negative indicators (override to Negative)
STRONG_NEGATIVE_KEYWORDS = [
    # Security & Incidents
    'breach', 'breached', 'breaches', 'hacked', 'hacking', 'hack',
    'cyber attack', 'cyberattack', 'ransomware', 'malware', 'phishing',
    'data leak', 'data breach', 'security incident', 'security breach',
    'unauthorized access', 'compromised', 'vulnerability', 'exploit',
    'intrusion', 'infiltration', 'attack vector',
    
    # Fraud & Crime
    'fraud', 'fraudulent', 'scam', 'theft', 'stolen', 'embezzlement',
    'money laundering', 'identity theft', 'criminal', 'illegal',
    'misconduct', 'violation', 'forgery', 'counterfeit',
    
    # Legal & Compliance
    'lawsuit', 'litigation', 'sued', 'penalty', 'penalties', 'fine',
    'fines', 'sanction', 'sanctions', 'violation', 'non-compliance',
    'regulatory action', 'legal action', 'court order', 'injunction',
    'class action', 'settlement', 'damages awarded',
    
    # Business Negative
    'bankruptcy', 'bankrupt', 'insolvency', 'liquidation', 'shutdown',
    'layoffs', 'downsizing', 'restructuring', 'loss', 'losses',
    'deficit', 'decline', 'downturn', 'recession', 'failure', 'failed',
    'terminated', 'termination', 'cancelled', 'cancellation',
    
    # Crisis & Emergency
    'crisis', 'emergency', 'disaster', 'catastrophe', 'accident',
    'fatality', 'fatalities', 'injury', 'injuries', 'death', 'deaths',
    'victim', 'victims', 'casualty', 'casualties',
    
    # Negative Outcomes
    'damage', 'damages', 'destroyed', 'destruction', 'harm', 'harmful',
    'risk', 'threat', 'danger', 'dangerous', 'warning', 'alert',
    'concern', 'concerning', 'problem', 'issue', 'trouble',
]

# Strong positive indicators (override to Positive)
STRONG_POSITIVE_KEYWORDS = [
    # Achievement & Success
    'achievement', 'achieved', 'success', 'successful', 'successfully',
    'accomplishment', 'accomplished', 'milestone', 'breakthrough',
    'award', 'awarded', 'recognition', 'honored', 'excellence',
    'outstanding', 'exceptional', 'remarkable',
    
    # Growth & Improvement
    'growth', 'growing', 'increase', 'increased', 'improvement',
    'improved', 'progress', 'advancement', 'innovation', 'innovative',
    'expansion', 'expanded', 'profit', 'profitable', 'revenue growth',
    'record high', 'all-time high', 'best ever',
    
    # Positive Actions
    'launched', 'launch', 'introducing', 'introduced', 'partnership',
    'collaboration', 'acquisition', 'merger', 'investment', 'funding',
    'raised', 'secured', 'won', 'winning', 'victory',
    
    # Positive Qualities
    'excellent', 'amazing', 'fantastic', 'wonderful', 'great',
    'impressive', 'incredible', 'superior', 'premium', 'world-class',
    'leading', 'best-in-class', 'top-rated', 'highly rated',
]

# Neutral indicators (professional/resume-style content)
NEUTRAL_INDICATORS = [
    # Resume/CV language
    'responsibilities include', 'responsible for', 'managed', 'managed team',
    'worked with', 'collaborated with', 'developed', 'implemented',
    'maintained', 'coordinated', 'supported', 'assisted',
    'experience in', 'skilled in', 'proficient in', 'knowledge of',
    'bachelor', 'master', 'degree', 'certified', 'certification',
    'professional experience', 'work experience', 'employment history',
    
    # Formal/Report language
    'pursuant to', 'in accordance with', 'as per', 'regarding',
    'attached please find', 'please note', 'for your reference',
    'outlined below', 'described above', 'as follows',
]


def analyze_sentiment(text: str) -> str:
    """
    Analyzes the overall sentiment of the text.
    
    Uses a hybrid approach:
    1. Keyword-based override for strong indicators
    2. VADER analysis for general sentiment
    3. Context-aware classification
    
    Args:
        text: The text to analyze
    
    Returns:
        str: "Positive", "Negative", or "Neutral"
    """
    if not text or not text.strip():
        return "Neutral"
    
    text_lower = text.lower()
    
    # Step 1: Check for strong negative indicators FIRST
    # This fixes the "breach classified as positive" problem
    negative_score = _count_keyword_matches(text_lower, STRONG_NEGATIVE_KEYWORDS)
    positive_score = _count_keyword_matches(text_lower, STRONG_POSITIVE_KEYWORDS)
    neutral_score = _count_keyword_matches(text_lower, NEUTRAL_INDICATORS)
    
    # Strong negative override (security breaches, fraud, etc.)
    if negative_score >= 3 or (negative_score >= 2 and negative_score > positive_score * 2):
        return "Negative"
    
    # Strong positive override (achievements, growth, etc.)
    if positive_score >= 3 and positive_score > negative_score * 2:
        return "Positive"
    
    # Neutral override for resume/professional content
    if neutral_score >= 3 and negative_score < 2 and positive_score < 2:
        return "Neutral"
    
    # Step 2: Use VADER for general cases
    analyzer = get_analyzer()
    
    if len(text) > 5000:
        vader_result = _analyze_long_text(text, analyzer)
    else:
        scores = analyzer.polarity_scores(text)
        vader_result = _classify_score(scores["compound"])
    
    # Step 3: Apply keyword adjustment to VADER result
    # If VADER says positive but we have negative keywords, reconsider
    if vader_result == "Positive" and negative_score > positive_score:
        return "Negative" if negative_score >= 2 else "Neutral"
    
    # If VADER says negative but we have more positive keywords
    if vader_result == "Negative" and positive_score > negative_score + 2:
        return "Positive"
    
    return vader_result


def _count_keyword_matches(text: str, keywords: list) -> int:
    """Counts how many keywords are present in text."""
    count = 0
    for keyword in keywords:
        # Use word boundary for single words, simple contains for phrases
        if ' ' in keyword:
            if keyword in text:
                count += 1
        else:
            if re.search(r'\b' + re.escape(keyword) + r'\b', text):
                count += 1
    return count


def _analyze_long_text(text: str, analyzer: SentimentIntensityAnalyzer) -> str:
    """Analyzes long text by breaking into paragraphs and averaging scores."""
    paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
    
    if not paragraphs:
        paragraphs = [text[:5000]]
    
    compound_scores = []
    
    for para in paragraphs[:20]:
        if len(para) > 50:
            scores = analyzer.polarity_scores(para)
            compound_scores.append(scores["compound"])
    
    if not compound_scores:
        return "Neutral"
    
    avg_compound = sum(compound_scores) / len(compound_scores)
    
    return _classify_score(avg_compound)


def _classify_score(compound: float) -> str:
    """
    Classifies compound score into sentiment label.
    
    Using slightly adjusted thresholds for business documents:
    - Positive: compound >= 0.1 (stricter than default 0.05)
    - Negative: compound <= -0.1 (stricter than default -0.05)
    - Neutral: everything in between
    
    This helps avoid false positives for formal/professional text.
    """
    if compound >= 0.1:
        return "Positive"
    elif compound <= -0.1:
        return "Negative"
    else:
        return "Neutral"


def get_detailed_sentiment(text: str) -> dict:
    """
    Returns detailed sentiment scores (for debugging/advanced use).
    """
    if not text or not text.strip():
        return {
            "label": "Neutral",
            "compound": 0.0,
            "positive": 0.0,
            "negative": 0.0,
            "neutral": 1.0,
            "keyword_negative": 0,
            "keyword_positive": 0
        }
    
    analyzer = get_analyzer()
    scores = analyzer.polarity_scores(text[:5000])
    
    text_lower = text.lower()
    neg_keywords = _count_keyword_matches(text_lower, STRONG_NEGATIVE_KEYWORDS)
    pos_keywords = _count_keyword_matches(text_lower, STRONG_POSITIVE_KEYWORDS)
    
    return {
        "label": analyze_sentiment(text),
        "compound": round(scores["compound"], 4),
        "positive": round(scores["pos"], 4),
        "negative": round(scores["neg"], 4),
        "neutral": round(scores["neu"], 4),
        "keyword_negative": neg_keywords,
        "keyword_positive": pos_keywords
    }
