"""
Validate that URLs correspond to the correct scheme names
"""

import json
import re
from urllib.parse import urlparse

def extract_scheme_name_from_url(url: str) -> str:
    """
    Extract scheme name from URL by analyzing the URL path
    """
    parsed = urlparse(url)
    path = parsed.path.lower()
    
    # SBI MF URLs
    if 'sbimf.com' in url.lower():
        # Extract from path like: /sbimf-scheme-details/sbi-large-cap-fund-...
        if 'scheme-details' in path:
            # Get the scheme name part
            parts = path.split('/')
            for part in parts:
                if 'scheme-details' in part:
                    idx = parts.index(part)
                    if idx + 1 < len(parts):
                        scheme_part = parts[idx + 1]
                        # Clean up: remove numbers, parentheses, etc.
                        scheme_name = re.sub(r'-\d+$', '', scheme_part)  # Remove trailing numbers
                        scheme_name = re.sub(r'\([^)]+\)', '', scheme_name)  # Remove parentheses
                        scheme_name = scheme_name.replace('-', ' ').strip()
                        return scheme_name
    
    # Groww URLs
    elif 'groww.in' in url.lower():
        # Extract from path like: /mutual-funds/sbi-large-cap-fund-direct-growth
        if 'mutual-funds' in path:
            parts = path.split('/')
            for part in parts:
                if 'mutual-funds' in part:
                    idx = parts.index(part)
                    if idx + 1 < len(parts):
                        scheme_part = parts[idx + 1]
                        # Remove suffixes like -direct-growth
                        scheme_name = re.sub(r'-(direct|regular|growth|dividend).*$', '', scheme_part)
                        scheme_name = scheme_name.replace('-', ' ').strip()
                        return scheme_name
    
    return None


def normalize_scheme_name(name: str) -> str:
    """
    Normalize scheme name for comparison
    """
    if not name:
        return ""
    
    # Convert to lowercase
    name = name.lower()
    
    # Remove common suffixes
    name = re.sub(r'\s*(direct|regular|growth|dividend|fund).*$', '', name)
    
    # Remove extra spaces
    name = ' '.join(name.split())
    
    # Common name variations
    replacements = {
        'sbi': '',
        'formerly known as': '',
        'bluechip': 'large cap',
        'nifty midcap 150 index': 'nifty midcap 150',
        'nifty smallcap 250 index': 'nifty smallcap 250',
    }
    
    for old, new in replacements.items():
        name = name.replace(old, new)
    
    name = ' '.join(name.split())  # Clean up spaces
    return name.strip()


def validate_scheme_url_mapping(urls_mapping: dict) -> dict:
    """
    Validate that URLs correspond to correct scheme names
    
    Args:
        urls_mapping: Dictionary mapping scheme names to lists of URLs
        
    Returns:
        Dictionary with validation results
    """
    validation_results = {
        'correct': [],
        'mismatched': [],
        'warnings': []
    }
    
    for expected_scheme, urls in urls_mapping.items():
        normalized_expected = normalize_scheme_name(expected_scheme)
        
        for url in urls:
            extracted_scheme = extract_scheme_name_from_url(url)
            normalized_extracted = normalize_scheme_name(extracted_scheme) if extracted_scheme else ""
            
            # Check if they match
            match_score = calculate_match_score(normalized_expected, normalized_extracted)
            
            if match_score >= 0.7:  # 70% match threshold
                validation_results['correct'].append({
                    'url': url,
                    'expected_scheme': expected_scheme,
                    'extracted_scheme': extracted_scheme,
                    'match_score': match_score
                })
            elif match_score >= 0.3:  # Partial match - warning
                validation_results['warnings'].append({
                    'url': url,
                    'expected_scheme': expected_scheme,
                    'extracted_scheme': extracted_scheme,
                    'match_score': match_score
                })
            else:  # Mismatch
                validation_results['mismatched'].append({
                    'url': url,
                    'expected_scheme': expected_scheme,
                    'extracted_scheme': extracted_scheme,
                    'match_score': match_score
                })
    
    return validation_results


def calculate_match_score(expected: str, extracted: str) -> float:
    """
    Calculate similarity score between expected and extracted scheme names
    """
    if not expected or not extracted:
        return 0.0
    
    expected_words = set(expected.split())
    extracted_words = set(extracted.split())
    
    if not expected_words or not extracted_words:
        return 0.0
    
    # Calculate Jaccard similarity
    intersection = expected_words & extracted_words
    union = expected_words | extracted_words
    
    if not union:
        return 0.0
    
    jaccard = len(intersection) / len(union)
    
    # Bonus for key words matching
    key_words = ['large', 'cap', 'multicap', 'small', 'nifty', 'index', 'hybrid', 'equity']
    key_matches = sum(1 for word in key_words if word in expected and word in extracted)
    key_bonus = key_matches * 0.1
    
    return min(1.0, jaccard + key_bonus)


def main():
    # Load the scheme-URL mapping
    # Note: Groww links removed for Large Cap, Small Cap, and Nifty Index Fund 
    # due to categorization differences
    SCHEME_URLS = {
        "SBI Large Cap Fund": [
            "https://www.sbimf.com/sbimf-scheme-details/sbi-large-cap-fund-(formerly-known-as-sbi-bluechip-fund)-43"
        ],
        "SBI Multicap Fund": [
            "https://www.sbimf.com/sbimf-scheme-details/sbi-multicap-fund-609",
            "https://groww.in/mutual-funds/sbi-multicap-fund-direct-growth"
        ],
        "SBI Nifty Index Fund": [
            "https://www.sbimf.com/sbimf-scheme-details/sbi-nifty-index-fund-13"
        ],
        "SBI Small Cap Fund": [
            "https://www.sbimf.com/sbimf-scheme-details/sbi-small-cap-fund-329"
        ],
        "SBI Equity Hybrid Fund": [
            "https://www.sbimf.com/sbimf-scheme-details/sbi-equity-hybrid-fund-5"
        ]
    }
    
    print("="*70)
    print("SCHEME-URL VALIDATION")
    print("="*70)
    
    # Validate mappings
    results = validate_scheme_url_mapping(SCHEME_URLS)
    
    print(f"\n[OK] CORRECT MAPPINGS: {len(results['correct'])}")
    for item in results['correct']:
        print(f"  - {item['expected_scheme']}")
        print(f"    URL: {item['url']}")
        print(f"    Extracted: {item['extracted_scheme']} (Match: {item['match_score']:.2%})")
        print()
    
    if results['warnings']:
        print(f"\n[WARNING] PARTIAL MATCHES: {len(results['warnings'])}")
        for item in results['warnings']:
            print(f"  - Expected: {item['expected_scheme']}")
            print(f"    URL: {item['url']}")
            print(f"    Extracted: {item['extracted_scheme']} (Match: {item['match_score']:.2%})")
            print()
    
    if results['mismatched']:
        print(f"\n[ERROR] MISMATCHED URLS: {len(results['mismatched'])}")
        for item in results['mismatched']:
            print(f"  - Expected Scheme: {item['expected_scheme']}")
            print(f"    URL: {item['url']}")
            print(f"    Extracted Scheme: {item['extracted_scheme']} (Match: {item['match_score']:.2%})")
            print(f"    WARNING: URL does not match expected scheme!")
            print()
    
    # Summary
    print("="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Total URLs: {len(results['correct']) + len(results['warnings']) + len(results['mismatched'])}")
    print(f"Correct: {len(results['correct'])}")
    print(f"Warnings: {len(results['warnings'])}")
    print(f"Mismatched: {len(results['mismatched'])}")
    
    if results['mismatched']:
        print("\n[ACTION REQUIRED] Please correct the mismatched URLs before proceeding!")
        return False
    
    return True


if __name__ == "__main__":
    main()

