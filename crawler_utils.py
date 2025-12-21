"""
Utility Functions for IZU Web Crawler
Text processing, validation, and helper functions
"""

import re
import hashlib
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import unicodedata


def calculate_content_hash(text: str) -> str:
    """
    Calculate MD5 hash of content for deduplication
    
    Args:
        text: Content to hash
        
    Returns:
        MD5 hash string
    """
    return hashlib.md5(text.encode('utf-8')).hexdigest()


def clean_turkish_text(text: str) -> str:
    """
    Clean and normalize Turkish text
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Normalize unicode
    text = unicodedata.normalize('NFKC', text)
    
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    
    # Remove zero-width spaces and other invisible characters
    text = re.sub(r'[\u200b\u200c\u200d\ufeff]', '', text)
    
    # Trim
    text = text.strip()
    
    return text


def detect_language(text: str) -> str:
    """
    Simple language detection for Turkish vs English
    
    Args:
        text: Text to analyze
        
    Returns:
        'turkish', 'english', or 'unknown'
    """
    if not text or len(text) < 20:
        return 'unknown'
    
    # Count Turkish-specific characters
    turkish_chars = ['ğ', 'ü', 'ş', 'ı', 'ö', 'ç', 'Ğ', 'Ü', 'Ş', 'İ', 'Ö', 'Ç']
    turkish_count = sum(text.count(char) for char in turkish_chars)
    
    # Turkish-specific words
    turkish_words = ['ve', 'ile', 'için', 'bir', 'bu', 'olan', 'ancak', 'hakkında', 'üzerinde']
    turkish_word_count = sum(1 for word in turkish_words if word in text.lower())
    
    # English-specific words
    english_words = ['the', 'and', 'for', 'with', 'this', 'that', 'about', 'from']
    english_word_count = sum(1 for word in english_words if f' {word} ' in f' {text.lower()} ')
    
    if turkish_chars or turkish_word_count > 2:
        return 'turkish'
    elif english_word_count > 2:
        return 'english'
    
    return 'unknown'


def extract_dates(text: str) -> List[str]:
    """
    Extract dates from text in various formats
    
    Args:
        text: Text to search for dates
        
    Returns:
        List of date strings found
    """
    dates = []
    
    # DD.MM.YYYY or DD/MM/YYYY
    pattern1 = r'\b(\d{1,2}[./]\d{1,2}[./]\d{4})\b'
    dates.extend(re.findall(pattern1, text))
    
    # YYYY-MM-DD
    pattern2 = r'\b(\d{4}-\d{2}-\d{2})\b'
    dates.extend(re.findall(pattern2, text))
    
    # Month name formats (Turkish and English)
    pattern3 = r'\b(\d{1,2}\s+(?:Ocak|Şubat|Mart|Nisan|Mayıs|Haziran|Temmuz|Ağustos|Eylül|Ekim|Kasım|Aralık|January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})\b'
    dates.extend(re.findall(pattern3, text, re.IGNORECASE))
    
    return dates


def extract_emails(text: str) -> List[str]:
    """
    Extract email addresses from text
    
    Args:
        text: Text to search for emails
        
    Returns:
        List of unique email addresses
    """
    pattern = r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
    emails = re.findall(pattern, text)
    return list(set(emails))


def extract_phones(text: str) -> List[str]:
    """
    Extract phone numbers from text (Turkish format)
    
    Args:
        text: Text to search for phone numbers
        
    Returns:
        List of unique phone numbers
    """
    phones = []
    
    # International format: +90 XXX XXX XX XX
    pattern1 = r'\+90\s*\d{3}\s*\d{3}\s*\d{2}\s*\d{2}'
    phones.extend(re.findall(pattern1, text))
    
    # Parentheses format: (0XXX) XXX XX XX
    pattern2 = r'\(0\d{3}\)\s*\d{3}\s*\d{2}\s*\d{2}'
    phones.extend(re.findall(pattern2, text))
    
    # Simple format: 0XXX XXX XX XX
    pattern3 = r'0\d{3}\s*\d{3}\s*\d{2}\s*\d{2}'
    phones.extend(re.findall(pattern3, text))
    
    return list(set(phones))


def validate_email(email: str) -> bool:
    """
    Validate email address format
    
    Args:
        email: Email to validate
        
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_phone(phone: str) -> bool:
    """
    Validate Turkish phone number format
    
    Args:
        phone: Phone number to validate
        
    Returns:
        True if valid, False otherwise
    """
    # Remove spaces and dashes
    clean_phone = re.sub(r'[\s\-()]', '', phone)
    
    # Check if it matches Turkish phone patterns
    patterns = [
        r'^\+90\d{10}$',  # +90XXXXXXXXXX
        r'^0\d{10}$',     # 0XXXXXXXXXX
    ]
    
    return any(re.match(pattern, clean_phone) for pattern in patterns)


def extract_price(text: str) -> Optional[Dict[str, str]]:
    """
    Extract price/fee information from text
    
    Args:
        text: Text to search for prices
        
    Returns:
        Dictionary with amount and currency, or None
    """
    # Turkish Lira patterns
    tl_patterns = [
        r'(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)\s*(?:TL|₺|TRY)',
        r'(?:TL|₺|TRY)\s*(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)',
    ]
    
    for pattern in tl_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return {'amount': match.group(1), 'currency': 'TRY'}
    
    # USD patterns
    usd_patterns = [
        r'\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
        r'(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)\s*(?:USD|Dolar)',
    ]
    
    for pattern in usd_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return {'amount': match.group(1), 'currency': 'USD'}
    
    # Euro patterns
    eur_patterns = [
        r'€\s*(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)',
        r'(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)\s*(?:EUR|Euro)',
    ]
    
    for pattern in eur_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return {'amount': match.group(1), 'currency': 'EUR'}
    
    return None


def clean_html_text(text: str) -> str:
    """
    Clean text extracted from HTML
    
    Args:
        text: Text to clean
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove HTML entities
    text = re.sub(r'&[a-zA-Z]+;', ' ', text)
    text = re.sub(r'&#\d+;', ' ', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    return text


def extract_program_info(text: str) -> Dict[str, Optional[str]]:
    """
    Extract program-specific information from text
    
    Args:
        text: Text to analyze
        
    Returns:
        Dictionary with program info
    """
    info = {
        'degree_type': None,
        'duration': None,
        'language': None,
    }
    
    # Degree type
    degree_patterns = {
        'bachelor': r'\b(?:lisans|bachelor|undergraduate|ön lisans|önlisans)\b',
        'master': r'\b(?:yüksek lisans|master|graduate)\b',
        'phd': r'\b(?:doktora|phd|doctorate)\b',
        'associate': r'\b(?:ön lisans|associate)\b',
    }
    
    text_lower = text.lower()
    for degree, pattern in degree_patterns.items():
        if re.search(pattern, text_lower):
            info['degree_type'] = degree
            break
    
    # Duration
    duration_pattern = r'(\d+)\s*(?:yıl|year|sene)'
    match = re.search(duration_pattern, text_lower)
    if match:
        info['duration'] = match.group(1)
    
    # Language
    if re.search(r'\b(?:%100|100%|tamamen|fully|completely)\s*(?:ingilizce|english)\b', text_lower):
        info['language'] = 'english'
    elif re.search(r'\bingilizce\b', text_lower) and re.search(r'\btürkçe\b', text_lower):
        info['language'] = 'bilingual'
    elif re.search(r'\bingilizce\b', text_lower):
        info['language'] = 'english'
    elif re.search(r'\btürkçe\b', text_lower):
        info['language'] = 'turkish'
    
    return info


def similarity_ratio(text1: str, text2: str) -> float:
    """
    Calculate simple similarity ratio between two texts
    
    Args:
        text1: First text
        text2: Second text
        
    Returns:
        Similarity ratio (0.0 to 1.0)
    """
    if not text1 or not text2:
        return 0.0
    
    # Simple word-based similarity
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union) if union else 0.0


def truncate_text(text: str, max_length: int = 500, suffix: str = "...") -> str:
    """
    Truncate text to maximum length
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def extract_year(text: str) -> Optional[str]:
    """
    Extract year (4 digits) from text
    
    Args:
        text: Text to search
        
    Returns:
        Year string or None
    """
    match = re.search(r'\b(20\d{2}|19\d{2})\b', text)
    return match.group(1) if match else None
