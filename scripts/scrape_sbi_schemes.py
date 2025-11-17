"""
Script to scrape SBI Mutual Fund scheme URLs
Validates that URLs correspond to correct scheme names before storing
"""

from scrape_urls import scrape_urls_list
from validate_scheme_urls import validate_scheme_url_mapping, extract_scheme_name_from_url, normalize_scheme_name, calculate_match_score
import json

# URLs for 5 SBI Mutual Fund schemes
# Note: Groww links removed for Large Cap, Small Cap, and Nifty Index Fund 
# due to categorization differences that cause confusion
SCHEME_URLS = {
    "SBI Large Cap Fund": [
        "https://www.sbimf.com/sbimf-scheme-details/sbi-large-cap-fund-(formerly-known-as-sbi-bluechip-fund)-43"
        # Groww URL removed - categorization mismatch
    ],
    "SBI Multicap Fund": [
        "https://www.sbimf.com/sbimf-scheme-details/sbi-multicap-fund-609",
        "https://groww.in/mutual-funds/sbi-multicap-fund-direct-growth"
    ],
    "SBI Nifty Index Fund": [
        "https://www.sbimf.com/sbimf-scheme-details/sbi-nifty-index-fund-13"
        # Groww URL removed - categorization mismatch
    ],
    "SBI Small Cap Fund": [
        "https://www.sbimf.com/sbimf-scheme-details/sbi-small-cap-fund-329"
        # Groww URL removed - categorization mismatch
    ],
    "SBI Equity Hybrid Fund": [
        "https://www.sbimf.com/sbimf-scheme-details/sbi-equity-hybrid-fund-5"
    ]
}

def main():
    # STEP 1: Validate URLs before scraping
    print("="*70)
    print("STEP 1: VALIDATING SCHEME-URL MAPPINGS")
    print("="*70)
    
    validation_results = validate_scheme_url_mapping(SCHEME_URLS)
    
    if validation_results['mismatched']:
        print("\n[ERROR] Found mismatched URLs. Please correct them:")
        for item in validation_results['mismatched']:
            print(f"  Expected: {item['expected_scheme']}")
            print(f"  URL: {item['url']}")
            print(f"  Extracted: {item['extracted_scheme']}")
            print()
        print("Aborting scraping. Please fix the URLs and try again.")
        return
    
    if validation_results['warnings']:
        print("\n[WARNING] Found URLs with partial matches:")
        for item in validation_results['warnings']:
            print(f"  Expected: {item['expected_scheme']}")
            print(f"  URL: {item['url']}")
            print(f"  Extracted: {item['extracted_scheme']} (Match: {item['match_score']:.2%})")
            print()
        print("Continuing with warnings...")
    
    print("\n[OK] All URLs validated successfully!")
    
    # STEP 2: Scrape URLs
    print("\n" + "="*70)
    print("STEP 2: SCRAPING URLs")
    print("="*70)
    
    # Collect all URLs
    all_urls = []
    scheme_mapping = {}  # Map URL to scheme name
    
    for scheme_name, urls in SCHEME_URLS.items():
        for url in urls:
            all_urls.append(url)
            scheme_mapping[url] = scheme_name
    
    print(f"Scraping {len(all_urls)} URLs for {len(SCHEME_URLS)} schemes...")
    print("\nSchemes:")
    for scheme_name, urls in SCHEME_URLS.items():
        print(f"  - {scheme_name}: {len(urls)} URL(s)")
    
    # Scrape all URLs
    stats = scrape_urls_list(
        all_urls, 
        output_file="data/raw/scraped_data.json",
        check_robots=True,
        use_selenium=True
    )
    
    print(f"\n{'='*60}")
    print("SCRAPING COMPLETE")
    print(f"{'='*60}")
    print(f"Total URLs: {stats['total_urls']}")
    print(f"Successful: {stats['successful']}")
    print(f"Failed: {stats['failed']}")
    
    if stats['failed_urls']:
        print(f"\nFailed URLs:")
        for url in stats['failed_urls']:
            print(f"  - {url}")
    
    # Update scraped data with scheme names
    try:
        with open("data/raw/scraped_data.json", 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # STEP 3: Validate and update scraped data with scheme names
        print("\n" + "="*70)
        print("STEP 3: VALIDATING SCRAPED DATA")
        print("="*70)
        
        validated_data = []
        validation_errors = []
        
        for doc in data:
            url = doc.get('url', '')
            expected_scheme = scheme_mapping.get(url, None)
            
            if expected_scheme:
                # Extract scheme name from URL
                extracted_scheme = extract_scheme_name_from_url(url)
                normalized_expected = normalize_scheme_name(expected_scheme)
                normalized_extracted = normalize_scheme_name(extracted_scheme) if extracted_scheme else ""
                
                # Calculate match score
                match_score = calculate_match_score(normalized_expected, normalized_extracted)
                
                if match_score >= 0.7:  # Good match
                    doc['scheme_name'] = expected_scheme
                    doc['scheme_name_validated'] = True
                    doc['match_score'] = match_score
                    validated_data.append(doc)
                else:  # Mismatch - don't store
                    validation_errors.append({
                        'url': url,
                        'expected_scheme': expected_scheme,
                        'extracted_scheme': extracted_scheme,
                        'match_score': match_score
                    })
                    print(f"[SKIPPED] URL mismatch:")
                    print(f"  URL: {url}")
                    print(f"  Expected: {expected_scheme}")
                    print(f"  Extracted: {extracted_scheme} (Match: {match_score:.2%})")
                    print()
            else:
                # URL not in mapping - skip
                validation_errors.append({
                    'url': url,
                    'error': 'URL not in scheme mapping'
                })
                print(f"[SKIPPED] URL not in mapping: {url}")
        
        if validation_errors:
            print(f"\n[WARNING] {len(validation_errors)} URLs were skipped due to validation failures.")
        
        # Try to determine document type
        for doc in validated_data:
            url = doc.get('url', '')
            if 'sbimf.com' in url:
                doc['document_type'] = 'scheme_details'
            elif 'groww.in' in url:
                doc['document_type'] = 'groww_listing'
        
        # Save only validated data
        data = validated_data
        
        # Save validated data
        with open("data/raw/scraped_data.json", 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*60}")
        print("EXTRACTED FACTUAL DATA SUMMARY")
        print(f"{'='*60}")
        
        for doc in data:
            scheme = doc.get('scheme_name', 'Unknown')
            url = doc.get('url', '')
            factual = doc.get('factual_data', {})
            
            print(f"\n{scheme}")
            print(f"URL: {url}")
            print(f"  Expense Ratio Regular: {factual.get('expense_ratio_regular', 'Not found')}%")
            print(f"  Expense Ratio Direct: {factual.get('expense_ratio_direct', 'Not found')}%")
            print(f"  Exit Load: {factual.get('exit_load', 'Not found')}%")
            print(f"  Minimum SIP: Rs. {factual.get('minimum_sip', 'Not found')}")
            print(f"  Minimum Lumpsum: Rs. {factual.get('minimum_lumpsum', 'Not found')}")
            print(f"  Lock-in Period: {factual.get('lock_in_period', 'Not found')}")
            print(f"  Riskometer: {factual.get('riskometer', 'Not found')}")
            print(f"  Benchmark: {factual.get('benchmark', 'Not found')}")
            print("-" * 60)
        
        print(f"\nData saved to: data/raw/scraped_data.json")
        print(f"Total documents scraped: {len(data)}")
        
    except Exception as e:
        print(f"Error processing scraped data: {e}")

if __name__ == "__main__":
    main()

