import re
from typing import Literal

def detect_language(text: str) -> Literal["khmer", "english"]:
    """
    Detect if the text is in Khmer or English.
    Returns 'khmer' or 'english'.
    """
    if not text:
        return "english"
    
    # Khmer Unicode range: U+1780 to U+17FF
    khmer_pattern = re.compile(r'[\u1780-\u17FF]')
    
    # Count Khmer characters
    khmer_chars = len(khmer_pattern.findall(text))
    
    # If more than 30% of characters are Khmer, consider it Khmer
    if khmer_chars > len(text) * 0.3:
        return "khmer"
    
    return "english"

def should_respond_in_khmer(user_message: str) -> bool:
    """
    Determine if the response should be in Khmer based on user input.
    """
    return detect_language(user_message) == "khmer" 