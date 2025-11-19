"""
Script to scrape custom URLs provided by user
Scrapes only the specified URLs and saves them with scheme names
"""

import sys
import os

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from scrape_urls import scrape_urls_list
import json
from datetime import datetime

# URLs organized by scheme name
SCHEME_URLS = {
    "SBI Large Cap Fund": [
        "https://coin.zerodha.com/mf/fund/INF200K01QX4/sbi-large-cap-fund-direct-growth",
        # PDF URL removed - skipping PDF files
        "https://www.angelone.in/mutual-funds/mf-schemes/sbi-blue-chip-fund-direct-plan-growth"
    ],
    "SBI Multicap Fund": [
        "https://www.indmoney.com/mutual-funds/sbi-multicap-fund-direct-growth-1040584",
        "https://coin.zerodha.com/mf/fund/INF200KA18E2/sbi-multicap-fund-direct-growth",
        "https://www.paytmmoney.com/mutual-funds/scheme/sbi-multicap-fund-direct-growth/inf200ka18e2"
    ],
    "SBI Nifty Index Fund": [
        "https://coin.zerodha.com/mf/fund/INF200K01TE8/sbi-nifty-index-fund-direct-growth",
        "https://groww.in/mutual-funds/sbi-nifty-index-fund-direct-growth",
        "https://www.indmoney.com/mutual-funds/sbi-nifty-index-fund-direct-growth-5583",
        "https://www.angelone.in/mutual-funds/mf-schemes/sbi-nifty-index-fund-direct-plan-growth"
    ],
    "SBI Small Cap Fund": [
        "https://groww.in/mutual-funds/sbi-small-midcap-fund-direct-growth",
        "https://coin.zerodha.com/mf/fund/INF200K01T51/sbi-small-cap-fund-direct-growth",
        "https://www.paytmmoney.com/mutual-funds/scheme/sbi-small-cap-fund-direct-growth/inf200k01t51"
    ],
    "SBI Equity Hybrid Fund": [
        "https://groww.in/mutual-funds/sbi-magnum-balanced-fund-direct-growth",
        "https://www.paytmmoney.com/mutual-funds/scheme/sbi-equity-hybrid-fund-direct-plan-growth/inf200k01ry0",
        "https://coin.zerodha.com/mf/fund/INF200K01RY0/sbi-equity-hybrid-fund-direct-growth"
    ]
}

def determine_document_type(url: str) -> str:
    """
    Determine document type based on URL domain
    """
    if 'sbimf.com' in url:
        if '.pdf' in url:
            return 'factsheet'
        return 'scheme_details'
    elif 'groww.in' in url:
        return 'groww_listing'
    elif 'zerodha.com' in url or 'coin.zerodha.com' in url:
        return 'zerodha_listing'
    elif 'indmoney.com' in url:
        return 'indmoney_listing'
    elif 'paytmmoney.com' in url:
        return 'paytm_listing'
    elif 'angelone.in' in url:
        return 'angelone_listing'
    else:
        return 'other'

def main():
    print("="*70)
    print("CUSTOM URL SCRAPING")
    print("="*70)
    
    # Collect all URLs with scheme mapping
    all_urls = []
    scheme_mapping = {}  # Map URL to scheme name
    
    for scheme_name, urls in SCHEME_URLS.items():
        for url in urls:
            all_urls.append(url)
            scheme_mapping[url] = scheme_name
    
    print(f"\nTotal URLs to scrape: {len(all_urls)}")
    print(f"Schemes: {len(SCHEME_URLS)}")
    print("\nBreakdown by scheme:")
    for scheme_name, urls in SCHEME_URLS.items():
        print(f"  - {scheme_name}: {len(urls)} URL(s)")
        for url in urls:
            print(f"    • {url}")
    
    # Scrape all URLs
    print("\n" + "="*70)
    print("STEP 1: SCRAPING URLs")
    print("="*70)
    
    # Use a temporary output file
    temp_output = "data/raw/custom_scraped_data.json"
    
    stats = scrape_urls_list(
        all_urls, 
        output_file=temp_output,
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
    
    # Update scraped data with scheme names and document types
    print("\n" + "="*70)
    print("STEP 2: PROCESSING SCRAPED DATA")
    print("="*70)
    
    try:
        with open(temp_output, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Update each document with scheme name and document type
        processed_data = []
        for doc in data:
            url = doc.get('url', '')
            scheme_name = scheme_mapping.get(url, None)
            
            if scheme_name:
                doc['scheme_name'] = scheme_name
                doc['document_type'] = determine_document_type(url)
                processed_data.append(doc)
                print(f"[OK] {scheme_name} - {url}")
            else:
                print(f"[WARNING] URL not in mapping: {url}")
        
        # Save processed data
        output_file = "data/raw/scraped_data.json"
        
        # Check if existing scraped_data.json exists and merge
        existing_data = []
        if os.path.exists(output_file):
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                print(f"\nFound existing data with {len(existing_data)} documents")
            except Exception as e:
                print(f"\nWarning: Could not read existing data: {e}")
        
        # Merge: add new data, avoiding duplicates by URL
        existing_urls = {doc.get('url') for doc in existing_data}
        new_docs = [doc for doc in processed_data if doc.get('url') not in existing_urls]
        
        if new_docs:
            merged_data = existing_data + new_docs
            print(f"\nAdding {len(new_docs)} new documents")
            print(f"Total documents after merge: {len(merged_data)}")
        else:
            merged_data = existing_data
            print(f"\nNo new documents to add (all URLs already exist)")
        
        # Save merged data
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, indent=2, ensure_ascii=False)
        
        print(f"\nData saved to: {output_file}")
        
        # Display summary of extracted factual data
        print("\n" + "="*70)
        print("EXTRACTED FACTUAL DATA SUMMARY")
        print("="*70)
        
        for doc in processed_data:
            scheme = doc.get('scheme_name', 'Unknown')
            url = doc.get('url', '')
            doc_type = doc.get('document_type', 'Unknown')
            factual = doc.get('factual_data', {})
            
            print(f"\n{scheme} ({doc_type})")
            print(f"URL: {url}")
            print(f"  Expense Ratio Regular: {factual.get('expense_ratio_regular', 'Not found')}%")
            print(f"  Expense Ratio Direct: {factual.get('expense_ratio_direct', 'Not found')}%")
            print(f"  Exit Load: {factual.get('exit_load', 'Not found')}%")
            print(f"  Minimum SIP: Rs. {factual.get('minimum_sip', 'Not found')}")
            print(f"  Minimum Lumpsum: Rs. {factual.get('minimum_lumpsum', 'Not found')}")
            print(f"  Lock-in Period: {factual.get('lock_in_period', 'Not found')}")
            print(f"  Riskometer: {factual.get('riskometer', 'Not found')}")
            print(f"  Benchmark: {factual.get('benchmark', 'Not found')}")
            print("-" * 70)
        
        print(f"\nTotal new documents processed: {len(processed_data)}")
        print(f"Total documents in database: {len(merged_data)}")
        
    except Exception as e:
        print(f"Error processing scraped data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

