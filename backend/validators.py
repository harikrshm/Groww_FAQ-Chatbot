"""
Response validation module for LLM-generated responses
Validates responses for source citations, no advice, facts-only, and response length
"""

import re
import sys
import os
import logging
from typing import Dict, List, Optional, Tuple

# Add parent directory to path for config import
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    OPINION_WORDS, FACTUAL_INDICATORS, ADVICE_KEYWORDS,
    DEFAULT_FALLBACK_URL
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Source citation patterns
SOURCE_CITATION_PATTERNS = [
    r"last updated from sources?",
    r"source[s]?:",
    r"from (?:the )?source[s]?",
    r"according to (?:the )?source[s]?",
    r"per (?:the )?source[s]?",
]

# URL pattern for detecting source URLs in response
URL_PATTERN = r'https?://[^\s<>"{}|\\^`\[\]]+[^\s<>"{}|\\^`\[\].,;:!?]'


class ValidationResult:
    """Container for validation results"""
    
    def __init__(self):
        self.is_valid = True
        self.errors = []
        self.warnings = []
        self.fixes_applied = []
    
    def add_error(self, error: str):
        """Add a validation error"""
        self.is_valid = False
        self.errors.append(error)
        logger.warning(f"Validation error: {error}")
    
    def add_warning(self, warning: str):
        """Add a validation warning"""
        self.warnings.append(warning)
        logger.info(f"Validation warning: {warning}")
    
    def add_fix(self, fix: str):
        """Record a fix that was applied"""
        self.fixes_applied.append(fix)
        logger.info(f"Fix applied: {fix}")
    
    def to_dict(self) -> Dict:
        """Convert validation result to dictionary"""
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "fixes_applied": self.fixes_applied
        }


def validate_source_citation(response: str) -> Tuple[bool, Optional[str]]:
    """
    Validate that response includes source citation
    
    Args:
        response: Response text to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    response_lower = response.lower()
    
    # Check for citation patterns
    for pattern in SOURCE_CITATION_PATTERNS:
        if re.search(pattern, response_lower):
            return True, None
    
    # Check for URL in response
    if re.search(URL_PATTERN, response):
        return True, None
    
    return False, "Response missing source citation (should end with 'Last updated from sources.')"


def validate_no_advice(response: str) -> Tuple[bool, Optional[str], List[str]]:
    """
    Validate that response doesn't contain investment advice or opinion words
    
    Args:
        response: Response text to validate
        
    Returns:
        Tuple of (is_valid, error_message, detected_advice_words)
    """
    response_lower = response.lower()
    detected_words = []
    
    # Check for advice keywords
    for keyword in ADVICE_KEYWORDS:
        if keyword.lower() in response_lower:
            detected_words.append(keyword)
    
    # Check for opinion words
    for word in OPINION_WORDS:
        # Use word boundaries to avoid partial matches
        pattern = r'\b' + re.escape(word.lower()) + r'\b'
        if re.search(pattern, response_lower):
            detected_words.append(word)
    
    if detected_words:
        return False, f"Response contains advice/opinion words: {', '.join(detected_words)}", detected_words
    
    return True, None, []


def validate_facts_only(response: str) -> Tuple[bool, Optional[str]]:
    """
    Validate that response contains factual indicators and is factual in nature
    
    Args:
        response: Response text to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    response_lower = response.lower()
    
    # Check for at least one factual indicator
    has_factual_indicator = False
    for indicator in FACTUAL_INDICATORS:
        if indicator.lower() in response_lower:
            has_factual_indicator = True
            break
    
    # Also check for numbers/percentages (common in factual responses)
    if re.search(r'\d+', response):
        has_factual_indicator = True
    
    if not has_factual_indicator:
        return False, "Response lacks factual indicators (numbers, percentages, factual terms)"
    
    return True, None


def validate_response_length(response: str, max_sentences: int = 3) -> Tuple[bool, Optional[str], int]:
    """
    Validate that response is within length limit (≤3 sentences)
    
    Args:
        response: Response text to validate
        max_sentences: Maximum number of sentences allowed (default: 3)
        
    Returns:
        Tuple of (is_valid, error_message, sentence_count)
    """
    # Split by sentence endings (. ! ?)
    sentences = re.split(r'[.!?]+', response)
    # Filter out empty strings
    sentences = [s.strip() for s in sentences if s.strip()]
    
    sentence_count = len(sentences)
    
    if sentence_count > max_sentences:
        return False, f"Response too long ({sentence_count} sentences, max {max_sentences})", sentence_count
    
    return True, None, sentence_count


def count_sentences(text: str) -> int:
    """
    Count number of sentences in text
    
    Args:
        text: Text to count sentences in
        
    Returns:
        Number of sentences
    """
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    return len(sentences)


def fix_source_citation(response: str, source_url: Optional[str] = None) -> str:
    """
    Add source citation to response if missing
    
    Args:
        response: Response text to fix
        source_url: Optional source URL to include
        
    Returns:
        Fixed response with source citation
    """
    response_lower = response.lower()
    
    # Check if citation already exists
    has_citation = False
    for pattern in SOURCE_CITATION_PATTERNS:
        if re.search(pattern, response_lower):
            has_citation = True
            break
    
    if has_citation:
        return response
    
    # Add citation
    citation = " Last updated from sources."
    if source_url:
        citation = f" Last updated from sources. For more information, visit {source_url}."
    
    # Ensure response ends with proper punctuation
    response = response.rstrip('.!?')
    response += citation
    
    return response


def fix_advice_words(response: str, detected_words: List[str]) -> str:
    """
    Remove or replace advice/opinion words from response
    
    Args:
        response: Response text to fix
        detected_words: List of detected advice/opinion words
        
    Returns:
        Fixed response with advice words removed/replaced
    """
    fixed_response = response
    
    # Replace common advice patterns
    replacements = {
        r'\bshould\b': 'can',
        r'\brecommend\b': 'provide information about',
        r'\bsuggest\b': 'provide information about',
        r'\bgood\b': 'suitable',
        r'\bbad\b': 'not suitable',
        r'\bbest\b': 'one option',
        r'\bworst\b': 'another option',
    }
    
    for pattern, replacement in replacements.items():
        fixed_response = re.sub(pattern, replacement, fixed_response, flags=re.IGNORECASE)
    
    # If still contains advice words, add disclaimer
    response_lower = fixed_response.lower()
    still_has_advice = any(word.lower() in response_lower for word in detected_words)
    
    if still_has_advice:
        disclaimer = " Note: This is factual information only, not personalized guidance."
        if not fixed_response.endswith('.'):
            fixed_response += '.'
        fixed_response += disclaimer
    
    return fixed_response


def truncate_response(response: str, max_sentences: int = 3) -> str:
    """
    Truncate response to maximum number of sentences
    
    Args:
        response: Response text to truncate
        max_sentences: Maximum number of sentences to keep
        
    Returns:
        Truncated response
    """
    sentences = re.split(r'([.!?]+)', response)
    
    # Reconstruct sentences with their punctuation
    reconstructed = []
    sentence_count = 0
    i = 0
    
    while i < len(sentences) and sentence_count < max_sentences:
        part = sentences[i].strip()
        if part:
            if i + 1 < len(sentences) and re.match(r'^[.!?]+$', sentences[i + 1]):
                # Sentence with punctuation
                reconstructed.append(part + sentences[i + 1])
                sentence_count += 1
                i += 2
            elif i == len(sentences) - 1 or (i + 1 < len(sentences) and not sentences[i + 1].strip()):
                # Last part or followed by empty
                if part:
                    reconstructed.append(part)
                    if re.search(r'[.!?]$', part):
                        sentence_count += 1
                i += 1
            else:
                reconstructed.append(part)
                i += 1
        else:
            i += 1
    
    truncated = ' '.join(reconstructed)
    
    # Ensure it ends with proper punctuation
    if not re.search(r'[.!?]$', truncated):
        truncated += '.'
    
    return truncated


def fix_response(
    response: str,
    source_url: Optional[str] = None,
    max_sentences: int = 3,
    remove_advice: bool = True
) -> Tuple[str, List[str]]:
    """
    Apply all fixes to response to make it compliant
    
    Args:
        response: Response text to fix
        source_url: Optional source URL for citation
        max_sentences: Maximum number of sentences allowed
        remove_advice: Whether to remove advice words
        
    Returns:
        Tuple of (fixed_response, fixes_applied)
    """
    fixes_applied = []
    fixed_response = response
    
    # Fix 1: Add source citation if missing
    is_valid, _ = validate_source_citation(fixed_response)
    if not is_valid:
        fixed_response = fix_source_citation(fixed_response, source_url)
        fixes_applied.append("Added source citation")
    
    # Fix 2: Remove advice words if requested
    if remove_advice:
        is_valid, _, detected_words = validate_no_advice(fixed_response)
        if not is_valid:
            fixed_response = fix_advice_words(fixed_response, detected_words)
            fixes_applied.append(f"Removed/replaced advice words: {', '.join(detected_words[:3])}")
    
    # Fix 3: Truncate if too long
    is_valid, _, sentence_count = validate_response_length(fixed_response, max_sentences)
    if not is_valid:
        fixed_response = truncate_response(fixed_response, max_sentences)
        fixes_applied.append(f"Truncated from {sentence_count} to {max_sentences} sentences")
    
    return fixed_response, fixes_applied


def validate_response(
    response: str,
    source_url: Optional[str] = None,
    max_sentences: int = 3,
    strict: bool = False
) -> ValidationResult:
    """
    Comprehensive response validation
    
    Args:
        response: Response text to validate
        source_url: Optional source URL for citation validation
        max_sentences: Maximum number of sentences allowed
        strict: If True, warnings are treated as errors
        
    Returns:
        ValidationResult object with validation status and details
    """
    result = ValidationResult()
    
    # Validation 1: Source citation
    is_valid, error = validate_source_citation(response)
    if not is_valid:
        result.add_error(error)
    
    # Validation 2: No advice
    is_valid, error, detected_words = validate_no_advice(response)
    if not is_valid:
        if strict:
            result.add_error(error)
        else:
            result.add_warning(error)
    
    # Validation 3: Facts only
    is_valid, error = validate_facts_only(response)
    if not is_valid:
        result.add_warning(error)  # This is a warning, not an error
    
    # Validation 4: Response length
    is_valid, error, sentence_count = validate_response_length(response, max_sentences)
    if not is_valid:
        result.add_error(error)
    
    return result


def validate_and_fix_response(
    response: str,
    source_url: Optional[str] = None,
    max_sentences: int = 3,
    remove_advice: bool = True,
    max_fix_attempts: int = 1
) -> Tuple[str, ValidationResult]:
    """
    Validate response and apply fixes if needed
    
    Args:
        response: Response text to validate and fix
        source_url: Optional source URL for citation
        max_sentences: Maximum number of sentences allowed
        remove_advice: Whether to remove advice words
        max_fix_attempts: Maximum number of fix attempts
        
    Returns:
        Tuple of (fixed_response, validation_result)
    """
    # Initial validation
    result = validate_response(response, source_url, max_sentences, strict=False)
    
    # If valid, return as-is
    if result.is_valid and not result.warnings:
        return response, result
    
    # Apply fixes
    fixed_response = response
    for attempt in range(max_fix_attempts):
        fixed_response, fixes = fix_response(
            fixed_response,
            source_url,
            max_sentences,
            remove_advice
        )
        result.fixes_applied.extend(fixes)
        
        # Re-validate after fixes
        new_result = validate_response(fixed_response, source_url, max_sentences, strict=False)
        
        # If now valid, return
        if new_result.is_valid and not new_result.warnings:
            result = new_result
            break
        
        # Update result with new errors/warnings
        result.errors = new_result.errors
        result.warnings = new_result.warnings
        result.is_valid = new_result.is_valid
    
    return fixed_response, result


if __name__ == "__main__":
    # Test validation functions
    print("="*80)
    print("TESTING RESPONSE VALIDATORS")
    print("="*80)
    
    test_responses = [
        "The expense ratio is 1.48%. Last updated from sources.",
        "This fund is good for investment. You should buy it.",
        "The minimum SIP is Rs. 500. The fund has low risk. The returns are high. The expense ratio is low.",
        "The exit load is 1% for redemptions within 12 months.",
    ]
    
    for i, response in enumerate(test_responses, 1):
        print(f"\n{'='*80}")
        print(f"TEST {i}: {response[:60]}...")
        print("="*80)
        
        result = validate_response(response)
        print(f"Valid: {result.is_valid}")
        if result.errors:
            print(f"Errors: {result.errors}")
        if result.warnings:
            print(f"Warnings: {result.warnings}")
        
        if not result.is_valid or result.warnings:
            fixed, fixes = fix_response(response)
            print(f"\nFixed: {fixed}")
            print(f"Fixes applied: {fixes}")

