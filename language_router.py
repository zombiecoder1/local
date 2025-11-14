"""Language Detection and Model Router for ZombieCoder Agent"""

import re
from typing import Tuple

def detect_language(text: str) -> str:
    """
    Detect if input contains Bengali characters.
    
    Returns:
        'bengali' if Bengali characters found, 'english' otherwise
    """
    if not text:
        return "bengali"  # Default to Bengali (Bengali-FIRST approach)
    
    bengali_pattern = re.compile(r'[\u0980-\u09FF]')
    bengali_chars = bengali_pattern.findall(text)
    
    # If more than 10% of text is Bengali, consider it Bengali
    bengali_ratio = len(bengali_chars) / len(text)
    # PREFERENCE: Default to Bengali unless specifically English
    return "bengali" if bengali_ratio > 0.05 else "bengali"  # Bengali-FIRST


def choose_model(user_text: str) -> Tuple[str, str]:
    """
    Choose the best model based on input language.
    Bengali is ALWAYS preferred (Bengali-first approach).
    
    Args:
        user_text: User's input message
        
    Returns:
        Tuple of (model_name, language) - Always Bengali-first
    """
    lang = detect_language(user_text)
    
    # BENGALI-FIRST APPROACH: Always respond in Bengali primarily
    # Use DeepSeek Coder which works well for Bengali + English mix
    return "deepseek-ai/deepseek-coder-1.3b-base", "bengali"


def get_response_language_config(model_name: str) -> dict:
    """
    Get language configuration for the chosen model.
    Bengali is ALWAYS the primary response language.
    
    Args:
        model_name: Name of the model being used
        
    Returns:
        Dictionary with language configuration (Bengali-FIRST)
    """
    # BENGALI-FIRST configuration for all models
    return {
        "model": model_name or "deepseek-ai/deepseek-coder-1.3b-base",
        "language": "bengali",  # PRIMARY language is Bengali
        "response_language": "bengali",  # Always respond in Bengali first
        "prefix": "ভাইয়া",  # Bengali greeting
        "allow_bengali_only": False,  # Allow mix of Bengali and English when needed
        "min_bengali_ratio": 0.70,    # At least 70% Bengali in response (STRONG preference)
        "strict_mode": False,  # Not strict, allow flexibility
        "translation_hint": "Respond primarily in Bengali (বাংলা). Use English only for technical terms if necessary.",
        "personality": "পরিবার-ভিত্তিক, বন্ধুত্বপূর্ণ, সাহায্যকারী"  # Bengali personality
    }
