"""
Entity Extractor (Improved)
===========================
Extracts named entities using hybrid approach:
- spaCy NER (when available)
- Strong regex patterns for dates, amounts, locations
- Heuristic name detection for OCR/document text

Entities extracted:
- names: Person names
- dates: Date references  
- organizations: Company/org names
- amounts: Monetary values
- locations: Places/addresses
"""

import re
from typing import Dict, List, Set


# =============================================================================
# REGEX PATTERNS - Improved for better coverage
# =============================================================================

# Date patterns (comprehensive)
DATE_PATTERNS = [
    # ISO format: 2024-03-15
    r'\b\d{4}-\d{2}-\d{2}\b',
    # US format: 03/15/2024, 3/15/24
    r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',
    # European format: 15-03-2024, 15.03.2024
    r'\b\d{1,2}[-./]\d{1,2}[-./]\d{2,4}\b',
    # Full month names: March 15, 2024 or 15 March 2024
    r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}\b',
    r'\b\d{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December),?\s+\d{4}\b',
    # Short month: Mar 15, 2024 or Mar 2024
    r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}\b',
    # Month Year only: June 2020, March 2024
    r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b',
    r'\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}\b',
    # Year ranges: 2020-2024, 2020 - 2024
    r'\b\d{4}\s*[-–—]\s*\d{4}\b',
    # Quarter references: Q1 2024, Q2 2023
    r'\b[Qq][1-4]\s+\d{4}\b',
]

# Monetary amount patterns (improved)
AMOUNT_PATTERNS = [
    # Dollar amounts: $1,234.56 or $1234 or $ 1,234
    r'\$\s*[\d,]+(?:\.\d{1,2})?',
    # Euro amounts: €1,234.56
    r'€\s*[\d,]+(?:\.\d{1,2})?',
    # Pound amounts: £1,234.56
    r'£\s*[\d,]+(?:\.\d{1,2})?',
    # Indian Rupee: ₹1,23,456 or Rs. 1,234 or Rs 1234 or INR 1234
    r'₹\s*[\d,]+(?:\.\d{1,2})?',
    r'\bRs\.?\s*[\d,]+(?:\.\d{1,2})?',
    r'\bINR\.?\s*[\d,]+(?:\.\d{1,2})?',
    # Written currency codes: USD 1,234.56, EUR 500
    r'\b(?:USD|EUR|GBP|INR|AUD|CAD|JPY)\s*[\d,]+(?:\.\d{1,2})?',
    # Numbers with currency words: 1,234.56 dollars, 500 rupees
    r'\b[\d,]+(?:\.\d{1,2})?\s*(?:dollars?|euros?|pounds?|rupees?|USD|EUR|GBP)\b',
    # Large amounts: 2.5 million, 10 billion
    r'\$?\s*[\d.]+\s*(?:million|billion|trillion|lakh|crore|lakhs|crores)\b',
]

# Location patterns (cities, states, countries)
LOCATION_PATTERNS = [
    # City, State format: New York, NY or San Francisco, CA
    r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s*[A-Z]{2}\b',
    # City, State full: New York, New York
    r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*,\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',
]

# Common US states
US_STATES = {
    'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado',
    'Connecticut', 'Delaware', 'Florida', 'Georgia', 'Hawaii', 'Idaho',
    'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky', 'Louisiana',
    'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota',
    'Mississippi', 'Missouri', 'Montana', 'Nebraska', 'Nevada',
    'New Hampshire', 'New Jersey', 'New Mexico', 'New York',
    'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon',
    'Pennsylvania', 'Rhode Island', 'South Carolina', 'South Dakota',
    'Tennessee', 'Texas', 'Utah', 'Vermont', 'Virginia', 'Washington',
    'West Virginia', 'Wisconsin', 'Wyoming'
}

# Major cities
MAJOR_CITIES = {
    'New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix', 'Philadelphia',
    'San Antonio', 'San Diego', 'Dallas', 'San Jose', 'Austin', 'Jacksonville',
    'San Francisco', 'Seattle', 'Denver', 'Boston', 'Nashville', 'Baltimore',
    'London', 'Paris', 'Tokyo', 'Mumbai', 'Delhi', 'Bangalore', 'Hyderabad',
    'Chennai', 'Kolkata', 'Singapore', 'Hong Kong', 'Sydney', 'Melbourne',
    'Toronto', 'Vancouver', 'Dubai', 'Berlin', 'Munich', 'Amsterdam'
}

# Countries
COUNTRIES = {
    'United States', 'USA', 'U.S.A.', 'United Kingdom', 'UK', 'U.K.',
    'Canada', 'Australia', 'India', 'Germany', 'France', 'Japan', 'China',
    'Singapore', 'Netherlands', 'Switzerland', 'Ireland', 'Sweden', 'Norway'
}

# Organization suffixes/patterns
ORG_SUFFIXES = [
    r'\b\w+(?:\s+\w+)*\s+(?:Inc\.?|Corp\.?|Corporation|LLC|Ltd\.?|Limited|Co\.?|Company|Group|Holdings|Partners|Associates|Technologies|Solutions|Services|Systems|Consulting|International|Global|Enterprise|Enterprises)\b',
    r'\b(?:The\s+)?[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\s+(?:Bank|University|College|Institute|Foundation|Association|Organization|Agency|Department|Ministry|Commission|Board|Council|Committee)\b',
]

# Name patterns (for detecting names in document text)
NAME_PATTERNS = [
    # Title + Name: Mr. John Smith, Dr. Jane Doe, Prof. Smith
    r'\b(?:Mr\.?|Mrs\.?|Ms\.?|Dr\.?|Prof\.?)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b',
    # Common name pattern: First Last (capitalized words)
    r'\b[A-Z][a-z]{2,15}\s+[A-Z][a-z]{2,15}\b',
    # Three word names: John David Smith
    r'\b[A-Z][a-z]{2,15}\s+[A-Z][a-z]{2,15}\s+[A-Z][a-z]{2,15}\b',
]

# Common first names for validation
COMMON_FIRST_NAMES = {
    'james', 'john', 'robert', 'michael', 'william', 'david', 'richard', 'joseph',
    'thomas', 'charles', 'christopher', 'daniel', 'matthew', 'anthony', 'mark',
    'donald', 'steven', 'paul', 'andrew', 'joshua', 'mary', 'patricia', 'jennifer',
    'linda', 'elizabeth', 'barbara', 'susan', 'jessica', 'sarah', 'karen', 'nancy',
    'lisa', 'betty', 'margaret', 'sandra', 'ashley', 'dorothy', 'kimberly', 'emily',
    'donna', 'michelle', 'nina', 'anna', 'emma', 'olivia', 'ava', 'sophia', 'isabella',
    'alex', 'sam', 'taylor', 'jordan', 'casey', 'riley', 'jamie', 'morgan', 'charlie'
}

# Words that look like names but aren't
FALSE_NAME_POSITIVES = {
    'the', 'this', 'that', 'these', 'those', 'here', 'there', 'where', 'when',
    'what', 'which', 'who', 'how', 'why', 'can', 'could', 'would', 'should',
    'new york', 'los angeles', 'san francisco', 'las vegas', 'data breach',
    'cyber security', 'machine learning', 'artificial intelligence', 'project manager',
    'senior developer', 'software engineer', 'data scientist', 'product manager',
    'dear sir', 'dear madam', 'good morning', 'good afternoon', 'best regards',
    'kind regards', 'yours truly', 'thank you', 'please note', 'attached please',
    'invoice number', 'order number', 'reference number', 'account number',
    'total amount', 'grand total', 'sub total', 'net amount', 'gross amount'
}


def extract_entities(text: str) -> Dict[str, List[str]]:
    """
    Extracts named entities from text using hybrid approach.
    
    Combines spaCy NER with strong regex patterns for better coverage.
    """
    if not text or not text.strip():
        return _empty_entities()
    
    # Normalize text for better matching
    clean_text = _preprocess_text(text)
    
    # Initialize result containers
    names: Set[str] = set()
    dates: Set[str] = set()
    organizations: Set[str] = set()
    amounts: Set[str] = set()
    locations: Set[str] = set()
    
    # Step 1: Try spaCy NER
    try:
        spacy_entities = _extract_with_spacy(clean_text)
        names.update(spacy_entities.get("names", []))
        dates.update(spacy_entities.get("dates", []))
        organizations.update(spacy_entities.get("organizations", []))
        locations.update(spacy_entities.get("locations", []))
    except Exception:
        pass
    
    # Step 2: Regex-based extraction (catches what spaCy misses)
    regex_dates = _extract_dates_regex(clean_text)
    dates.update(regex_dates)
    
    regex_amounts = _extract_amounts_regex(clean_text)
    amounts.update(regex_amounts)
    
    regex_locations = _extract_locations_regex(clean_text)
    locations.update(regex_locations)
    
    regex_orgs = _extract_organizations_regex(clean_text)
    organizations.update(regex_orgs)
    
    regex_names = _extract_names_regex(clean_text)
    names.update(regex_names)
    
    # Step 3: Apply post-processing cleanup filters
    cleaned_names = _filter_names(names)
    cleaned_orgs = _filter_organizations(organizations)
    cleaned_locations = _filter_locations(locations)
    cleaned_dates = _filter_dates(dates)
    cleaned_amounts = _filter_amounts(amounts)
    
    # Step 4: Return cleaned results (max 8 per category)
    return {
        "names": cleaned_names[:8],
        "dates": cleaned_dates[:8],
        "organizations": cleaned_orgs[:8],
        "amounts": cleaned_amounts[:8],
        "locations": cleaned_locations[:8],
    }


def _preprocess_text(text: str) -> str:
    """Cleans text for better extraction."""
    # Fix common OCR issues
    text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
    text = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', text)  # Split camelCase
    return text


def _extract_with_spacy(text: str) -> Dict[str, List[str]]:
    """Extracts entities using spaCy NER model."""
    import spacy
    
    try:
        nlp = spacy.load("en_core_web_sm")
    except OSError:
        return _empty_entities()
    
    # Process text (limit for performance)
    doc = nlp(text[:100000])
    
    names = []
    dates = []
    organizations = []
    locations = []
    
    for ent in doc.ents:
        entity_text = ent.text.strip()
        
        if len(entity_text) < 2 or len(entity_text) > 100:
            continue
        
        if ent.label_ == "PERSON":
            names.append(entity_text)
        elif ent.label_ == "DATE":
            dates.append(entity_text)
        elif ent.label_ == "ORG":
            organizations.append(entity_text)
        elif ent.label_ in ("GPE", "LOC", "FAC"):
            locations.append(entity_text)
        elif ent.label_ == "MONEY":
            pass  # We use regex for amounts
    
    return {
        "names": names,
        "dates": dates,
        "organizations": organizations,
        "locations": locations,
    }


def _extract_dates_regex(text: str) -> List[str]:
    """Extracts dates using comprehensive regex patterns."""
    dates = []
    
    for pattern in DATE_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        dates.extend(matches)
    
    return [d.strip() for d in dates if d.strip()]


def _extract_amounts_regex(text: str) -> List[str]:
    """Extracts monetary amounts using regex patterns."""
    amounts = []
    
    for pattern in AMOUNT_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        amounts.extend(matches)
    
    return [a.strip() for a in amounts if a.strip()]


def _extract_locations_regex(text: str) -> List[str]:
    """Extracts locations using regex and known location lists."""
    locations = []
    
    # Pattern-based extraction
    for pattern in LOCATION_PATTERNS:
        matches = re.findall(pattern, text)
        locations.extend(matches)
    
    # Check for known cities
    for city in MAJOR_CITIES:
        if re.search(r'\b' + re.escape(city) + r'\b', text, re.IGNORECASE):
            locations.append(city)
    
    # Check for US states
    for state in US_STATES:
        if re.search(r'\b' + re.escape(state) + r'\b', text, re.IGNORECASE):
            locations.append(state)
    
    # Check for countries
    for country in COUNTRIES:
        if re.search(r'\b' + re.escape(country) + r'\b', text, re.IGNORECASE):
            locations.append(country)
    
    return [loc.strip() for loc in locations if loc.strip()]


def _extract_organizations_regex(text: str) -> List[str]:
    """Extracts organization names using patterns."""
    orgs = []
    
    for pattern in ORG_SUFFIXES:
        matches = re.findall(pattern, text, re.IGNORECASE)
        orgs.extend(matches)
    
    return [o.strip() for o in orgs if o.strip()]


def _extract_names_regex(text: str) -> List[str]:
    """Extracts person names using patterns and heuristics."""
    names = []
    
    for pattern in NAME_PATTERNS:
        matches = re.findall(pattern, text)
        for match in matches:
            # Validate it looks like a name
            if _is_likely_name(match):
                names.append(match)
    
    return names


def _is_likely_name(text: str) -> bool:
    """Checks if text is likely a person's name."""
    text_lower = text.lower().strip()
    
    # Skip if in false positives
    if text_lower in FALSE_NAME_POSITIVES:
        return False
    
    # Skip single words
    words = text.split()
    if len(words) < 2:
        return False
    
    # Check if first word could be a first name
    first_word = words[0].lower()
    if first_word in COMMON_FIRST_NAMES:
        return True
    
    # Check if matches Title Name pattern
    if first_word in {'mr', 'mrs', 'ms', 'dr', 'prof'}:
        return True
    
    # Additional heuristic: both words should be title case
    if all(w[0].isupper() and w[1:].islower() for w in words if len(w) > 1):
        # Not a common phrase
        if len(words) == 2 and len(words[0]) > 2 and len(words[1]) > 2:
            return True
    
    return False


def _clean_entity_list(entities: Set[str], min_len: int = 2, max_len: int = 100) -> List[str]:
    """Cleans and deduplicates entity list."""
    cleaned = set()
    
    for entity in entities:
        entity = entity.strip()
        
        # Length check
        if len(entity) < min_len or len(entity) > max_len:
            continue
        
        # Skip pure numbers or punctuation
        if not any(c.isalpha() for c in entity):
            continue
        
        cleaned.add(entity)
    
    return sorted(list(cleaned))


def _clean_amounts_list(amounts: Set[str]) -> List[str]:
    """Cleans and validates monetary amounts."""
    cleaned = set()
    
    for amount in amounts:
        amount = amount.strip()
        
        # Must have at least one digit
        if not any(c.isdigit() for c in amount):
            continue
        
        # Skip if too short (e.g., just "rs,")
        digits = re.findall(r'\d', amount)
        if len(digits) < 1:
            continue
        
        # Skip malformed entries
        if amount.lower() in {'rs,', 'rs.', 'rs', '$', '€', '£', '₹'}:
            continue
        
        cleaned.add(amount)
    
    return sorted(list(cleaned))


def _empty_entities() -> Dict[str, List[str]]:
    """Returns empty entity structure."""
    return {
        "names": [],
        "dates": [],
        "organizations": [],
        "amounts": [],
        "locations": [],
    }


# =============================================================================
# POST-PROCESSING CLEANUP FILTERS
# =============================================================================

# Words that are NOT person names (common false positives)
NAME_BLACKLIST = {
    # Generic business words
    'innovation', 'industry', 'incident', 'report', 'technology', 'security',
    'management', 'development', 'engineering', 'analysis', 'intelligence',
    'research', 'summary', 'overview', 'introduction', 'conclusion',
    'background', 'experience', 'education', 'skills', 'reference',
    'objective', 'professional', 'personal', 'contact', 'information',
    # Document terms
    'appendix', 'attachment', 'document', 'section', 'chapter', 'page',
    'table', 'figure', 'exhibit', 'schedule', 'item', 'note', 'revision',
    # Common misclassifications
    'data breach', 'cyber security', 'machine learning', 'cloud computing',
    'project manager', 'software engineer', 'data scientist', 'team lead',
    'dear sir', 'dear madam', 'best regards', 'kind regards', 'sincerely',
    # Invoice/business document false positives
    'consulting', 'fee', 'services', 'rendered', 'total', 'due', 'amount',
    'tax', 'invoice', 'payment', 'balance', 'subtotal', 'price', 'cost',
    'location', 'address', 'phone', 'email', 'fax', 'website', 'date',
    'number', 'quantity', 'description', 'unit', 'rate', 'discount',
    'credit', 'debit', 'account', 'billing', 'shipping', 'order',
}

# Full phrases that should NEVER be names
NAME_PHRASE_BLACKLIST = {
    'consulting fee', 'services rendered', 'total due', 'grand total',
    'amount due', 'balance due', 'payment due', 'invoice number',
    'order number', 'reference number', 'account number', 'phone number',
    'new york', 'los angeles', 'san francisco', 'las vegas', 'hong kong',
    'data breach', 'cyber security', 'machine learning', 'cloud computing',
    'project manager', 'software engineer', 'data scientist', 'team lead',
    'acme corporation', 'thank you',  # Orgs should not be names
}

# Organization indicators (must contain one of these to be valid)
ORG_INDICATORS = {
    'inc', 'inc.', 'corp', 'corp.', 'corporation', 'ltd', 'ltd.', 'limited',
    'llc', 'llp', 'co', 'co.', 'company', 'group', 'holdings', 'partners',
    'associates', 'bank', 'university', 'college', 'institute', 'foundation',
    'agency', 'department', 'ministry', 'commission', 'authority', 'council',
    'technologies', 'solutions', 'services', 'systems', 'consulting', 'labs',
    'enterprises', 'international', 'global', 'worldwide', 'industries',
}

# Generic words to filter from locations
LOCATION_BLACKLIST = {
    'the', 'this', 'that', 'here', 'there', 'where', 'our', 'their', 'your',
    'company', 'office', 'department', 'team', 'organization', 'location',
    'address', 'contact', 'information', 'details', 'based', 'located',
}


def _filter_names(names: Set[str]) -> List[str]:
    """
    Filters names to keep only likely person names.
    
    Rules:
    - Keep 2-3 word names only
    - Must be properly capitalized
    - Remove blacklisted words and phrases
    - Remove entries that look like titles/business terms
    - Require first word to look like a first name OR title
    """
    filtered = []
    
    for name in names:
        name = name.strip()
        
        # Skip empty
        if not name:
            continue
        
        # Word count check (2-3 words for names)
        words = name.split()
        if len(words) < 2 or len(words) > 3:
            continue
        
        # Length check
        if len(name) < 4 or len(name) > 35:
            continue
        
        name_lower = name.lower()
        
        # Check against phrase blacklist FIRST (exact match)
        if name_lower in NAME_PHRASE_BLACKLIST:
            continue
        
        # Check if ANY blacklisted word appears in the name
        name_words_lower = [w.lower() for w in words]
        if any(bl_word in name_words_lower for bl_word in NAME_BLACKLIST):
            continue
        
        # All words should start with capital letter
        if not all(w[0].isupper() for w in words if len(w) > 0):
            continue
        
        # Skip if any word is all caps (likely acronym/header)
        if any(w.isupper() and len(w) > 2 for w in words):
            continue
        
        # Skip if contains numbers
        if any(c.isdigit() for c in name):
            continue
        
        # Each word should be reasonable length (2-15 chars)
        if not all(2 <= len(w) <= 15 for w in words):
            continue
        
        # CRITICAL: First word must look like a real first name or title
        first_word_lower = words[0].lower()
        is_title = first_word_lower in {'mr', 'mrs', 'ms', 'dr', 'prof', 'sir', 'lady'}
        is_common_name = first_word_lower in COMMON_FIRST_NAMES
        
        # If neither title nor common name, apply stricter validation
        if not (is_title or is_common_name):
            # Reject if the name contains any organization indicator
            if any(ind in name_lower for ind in ORG_INDICATORS):
                continue
            # Reject names ending with common business suffixes
            last_word_lower = words[-1].lower()
            if last_word_lower in {'inc', 'corp', 'corporation', 'ltd', 'llc', 'company', 'group', 'services', 'consulting', 'fee', 'due', 'rendered', 'location'}:
                continue
        
        filtered.append(name)
    
    # Remove duplicates and sort
    return sorted(list(set(filtered)))


def _filter_organizations(organizations: Set[str]) -> List[str]:
    """
    Filters organizations to keep only valid company/org names.
    
    Rules:
    - Must contain org indicator (Inc, Corp, Ltd, etc.) OR be known pattern
    - Max 4 words
    - Remove sentence-like entries
    - Remove entries with random document text mixed in
    """
    filtered = []
    
    for org in organizations:
        org = org.strip()
        
        # Skip empty
        if not org:
            continue
        
        # Word count check (max 4 words - stricter)
        words = org.split()
        if len(words) > 4:
            continue
        
        # Length check (stricter max)
        if len(org) < 3 or len(org) > 45:
            continue
        
        org_lower = org.lower()
        
        # CRITICAL: Reject orgs that contain obvious noise words
        noise_words = {'services rendered', 'consulting fee', 'rendered consulting', 
                       'total due', 'amount due', 'thank you', 'dear sir', 'dear madam'}
        if any(noise in org_lower for noise in noise_words):
            continue
        
        # Reject if org contains state abbreviations mixed with noise
        # e.g., "NY Services Rendered Consulting"
        if re.search(r'\b[A-Z]{2}\s+(?:services|rendered|consulting|fee)', org, re.IGNORECASE):
            continue
        
        # Must contain an org indicator
        has_indicator = any(ind in org_lower.split() for ind in ORG_INDICATORS)
        
        # Also check for indicator at end with punctuation
        if not has_indicator:
            has_indicator = bool(re.search(r'\b(?:Inc|Corp|Ltd|LLC|Co)\b\.?$', org, re.IGNORECASE))
        
        if not has_indicator:
            continue
        
        # Skip if looks like a sentence (has common verbs/articles mid-string)
        sentence_indicators = [' is ', ' was ', ' are ', ' were ', ' the ', ' for ', ' with ', ' and the ', ' or the ']
        if any(ind in org_lower for ind in sentence_indicators):
            continue
        
        filtered.append(org)
    
    # Remove near-duplicates (keep shorter/cleaner version)
    final = []
    filtered_sorted = sorted(filtered, key=len)  # Shorter first
    for org in filtered_sorted:
        # Check if this is a substring of something already added
        is_duplicate = False
        for existing in final:
            if org.lower() in existing.lower() or existing.lower() in org.lower():
                is_duplicate = True
                break
        if not is_duplicate:
            final.append(org)
    
    return sorted(final)


def _filter_locations(locations: Set[str]) -> List[str]:
    """
    Filters locations to keep only valid places.
    
    Rules:
    - "City, State" format is preferred
    - Known cities/states/countries are good
    - Remove generic words
    - Deduplicate ("New York" vs "New York, NY" → keep the more specific one)
    """
    filtered = []
    
    for loc in locations:
        loc = loc.strip()
        
        # Skip empty
        if not loc:
            continue
        
        # Length check
        if len(loc) < 2 or len(loc) > 40:
            continue
        
        # Skip if in blacklist
        loc_lower = loc.lower()
        if loc_lower in LOCATION_BLACKLIST:
            continue
        
        # Word count check (max 4 words for locations)
        words = loc.split()
        if len(words) > 4:
            continue
        
        # Skip if contains business noise
        noise_words = {'services', 'rendered', 'consulting', 'fee', 'due', 'invoice', 'payment'}
        if any(w.lower() in noise_words for w in words):
            continue
        
        # Good patterns:
        # 1. "City, State" format
        if ',' in loc:
            filtered.append(loc)
            continue
        
        # 2. Known in our location sets
        if loc in MAJOR_CITIES or loc in US_STATES or loc in COUNTRIES:
            filtered.append(loc)
            continue
        
        # 3. Starts with capital, max 2 words (stricter)
        if loc[0].isupper() and len(words) <= 2:
            # Additional validation: looks like a place name
            if all(w[0].isupper() for w in words if len(w) > 0):
                filtered.append(loc)
                continue
    
    # Smart deduplication: prefer more specific entries
    # e.g., "New York, NY" over "New York"
    final = []
    seen_bases = set()
    
    # Sort by length descending (prefer more specific)
    filtered_sorted = sorted(set(filtered), key=len, reverse=True)
    
    for loc in filtered_sorted:
        # Extract base location name (before comma if present)
        base = loc.split(',')[0].strip().lower()
        
        # If we haven't seen this base, add it
        if base not in seen_bases:
            final.append(loc)
            seen_bases.add(base)
    
    return sorted(final)


def _filter_dates(dates: Set[str]) -> List[str]:
    """
    Filters dates to keep only valid date formats.
    
    Rules:
    - Must contain actual date components (month name, day, year pattern)
    - Remove noise like "#1001 Date:"
    """
    filtered = []
    
    # Valid date patterns
    date_validators = [
        # Full/abbreviated month names with optional day and year
        re.compile(r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2}(?:st|nd|rd|th)?,?\s*\d{4}\b', re.IGNORECASE),
        # Month Year: June 2020
        re.compile(r'\b(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}\b', re.IGNORECASE),
        # Numeric: 2024-03-15, 03/15/2024, 15-03-2024
        re.compile(r'\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b'),
        re.compile(r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b'),
        # Quarter: Q1 2024
        re.compile(r'\b[Qq][1-4]\s+\d{4}\b'),
        # Year range: 2020-2024
        re.compile(r'\b\d{4}\s*[-–—]\s*\d{4}\b'),
    ]
    
    for date in dates:
        date = date.strip()
        
        # Skip empty
        if not date:
            continue
        
        # Skip if starts with # (invoice/order numbers)
        if date.startswith('#'):
            continue
        
        # Skip if contains "Date:" (label not value)
        if 'date:' in date.lower():
            continue
        
        # Length check
        if len(date) < 4 or len(date) > 25:
            continue
        
        # Must have numbers
        if not any(c.isdigit() for c in date):
            continue
        
        # Skip if too many words (>4)
        words = date.split()
        if len(words) > 4:
            continue
        
        # Validate against known good patterns
        is_valid_date = any(pattern.search(date) for pattern in date_validators)
        if not is_valid_date:
            continue
        
        filtered.append(date)
    
    return sorted(list(set(filtered)))


def _filter_amounts(amounts: Set[str]) -> List[str]:
    """
    Filters amounts to keep only valid currency formats.
    
    Rules:
    - Must have digits
    - Must have currency symbol or word
    - Remove malformed entries
    """
    filtered = []
    
    for amount in amounts:
        amount = amount.strip()
        
        # Skip empty
        if not amount:
            continue
        
        # Must have at least one digit
        digits = re.findall(r'\d', amount)
        if len(digits) < 1:
            continue
        
        # Skip very short malformed entries
        if len(amount) < 2:
            continue
        
        # Skip known bad patterns
        bad_patterns = {'rs,', 'rs.', 'rs', '$', '€', '£', '₹', 'usd', 'inr', 'eur', 'gbp'}
        if amount.lower() in bad_patterns:
            continue
        
        # Must have currency indicator
        has_currency = bool(re.search(r'[\$€£₹]|Rs\.?|USD|EUR|GBP|INR|dollar|rupee|euro|pound', amount, re.IGNORECASE))
        has_large_unit = bool(re.search(r'million|billion|lakh|crore', amount, re.IGNORECASE))
        
        if not (has_currency or has_large_unit):
            continue
        
        filtered.append(amount)
    
    return sorted(list(set(filtered)))
