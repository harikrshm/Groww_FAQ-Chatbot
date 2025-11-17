"""
Web scraper for collecting official mutual fund documents
Uses Selenium for JavaScript-rendered pages and BeautifulSoup for parsing
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
import time
import json
import logging
import os
import re
from typing import List, Dict, Optional
from datetime import datetime

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# User agent for requests
USER_AGENT = "Mozilla/5.0 (compatible; FAQBot/1.0; +https://github.com/your-repo)"

# Rate limiting delay (seconds between requests)
RATE_LIMIT_DELAY = 1.5

# Selenium configuration
PAGE_LOAD_TIMEOUT = 30  # seconds
IMPLICIT_WAIT = 10  # seconds
EXPLICIT_WAIT = 20  # seconds for specific elements


def validate_url(url: str) -> bool:
    """
    Validate if URL is properly formatted and accessible
    
    Args:
        url: URL string to validate
        
    Returns:
        bool: True if URL is valid, False otherwise
    """
    try:
        parsed = urlparse(url)
        # Check if URL has scheme and netloc
        if not parsed.scheme or not parsed.netloc:
            logger.warning(f"Invalid URL format: {url}")
            return False
        
        # Check if scheme is http or https
        if parsed.scheme not in ['http', 'https']:
            logger.warning(f"Unsupported URL scheme: {url}")
            return False
        
        return True
    except Exception as e:
        logger.error(f"Error validating URL {url}: {e}")
        return False


def check_robots_txt(url: str) -> bool:
    """
    Check if URL is allowed by robots.txt
    
    Args:
        url: URL to check
        
    Returns:
        bool: True if allowed, False if disallowed or error
    """
    try:
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        
        rp = RobotFileParser()
        rp.set_url(robots_url)
        rp.read()
        
        # Check if our user agent can fetch the URL
        can_fetch = rp.can_fetch(USER_AGENT, url)
        
        if not can_fetch:
            logger.warning(f"URL disallowed by robots.txt: {url}")
        
        return can_fetch
    except Exception as e:
        # If robots.txt check fails, assume allowed (fail gracefully)
        logger.warning(f"Could not check robots.txt for {url}: {e}. Proceeding anyway.")
        return True


def init_webdriver(headless: bool = True) -> Optional[webdriver.Chrome]:
    """
    Initialize Chrome WebDriver with appropriate options
    
    Args:
        headless: Whether to run browser in headless mode
        
    Returns:
        Chrome WebDriver instance or None if failed
    """
    try:
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument(f'--user-agent={USER_AGENT}')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # Use webdriver-manager to automatically handle ChromeDriver
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
        driver.implicitly_wait(IMPLICIT_WAIT)
        
        return driver
    except Exception as e:
        logger.error(f"Error initializing WebDriver: {e}")
        return None


def get_page_content_selenium(url: str, driver: webdriver.Chrome) -> Optional[Dict]:
    """
    Fetch page content using Selenium for JavaScript-rendered pages
    
    Args:
        url: URL to fetch
        driver: Selenium WebDriver instance
        
    Returns:
        Dictionary with 'html' and 'soup' keys, or None if failed
    """
    try:
        logger.info(f"Loading page with Selenium: {url}")
        driver.get(url)
        
        # Wait for page to load - wait for body or main content
        try:
            WebDriverWait(driver, EXPLICIT_WAIT).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
        except TimeoutException:
            logger.warning(f"Timeout waiting for body element on {url}")
        
        # Additional wait for JavaScript to render content
        # Wait for common content indicators
        time.sleep(3)  # Give extra time for dynamic content
        
        # Get page source after JavaScript execution
        html_content = driver.page_source
        
        # Parse with BeautifulSoup
        soup = BeautifulSoup(html_content, 'lxml')
        
        return {
            'html': html_content,
            'soup': soup
        }
    except TimeoutException:
        logger.error(f"Timeout error loading page: {url}")
        return None
    except WebDriverException as e:
        logger.error(f"WebDriver error for URL {url}: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error fetching {url}: {e}")
        return None


def extract_main_content(soup: BeautifulSoup, url: str) -> str:
    """
    Extract main content from HTML, removing navigation, footer, ads
    
    Args:
        soup: BeautifulSoup object
        url: Source URL for context
        
    Returns:
        str: Extracted text content
    """
    # Remove script and style elements
    for script in soup(["script", "style", "noscript"]):
        script.decompose()
    
    # Remove common non-content elements
    for element in soup.find_all(['nav', 'header', 'footer', 'aside', 'advertisement']):
        element.decompose()
    
    # Try to find main content area
    main_content = None
    
    # Common main content selectors
    main_selectors = [
        'main',
        'article',
        '[role="main"]',
        '.main-content',
        '.content',
        '#content',
        '.post-content',
        '.article-content'
    ]
    
    for selector in main_selectors:
        main_content = soup.select_one(selector)
        if main_content:
            break
    
    # If no main content found, use body
    if not main_content:
        main_content = soup.find('body')
    
    if main_content:
        # Get text content
        text = main_content.get_text(separator='\n', strip=True)
    else:
        # Fallback to entire soup
        text = soup.get_text(separator='\n', strip=True)
    
    # Clean up excessive whitespace
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    cleaned_text = '\n'.join(lines)
    
    return cleaned_text


def extract_tables(soup: BeautifulSoup) -> List[Dict]:
    """
    Extract tables from HTML and convert to structured format
    
    Args:
        soup: BeautifulSoup object
        
    Returns:
        List of dictionaries containing table data
    """
    tables = []
    for table in soup.find_all('table'):
        table_data = []
        rows = table.find_all('tr')
        
        for row in rows:
            cells = row.find_all(['td', 'th'])
            row_data = [cell.get_text(strip=True) for cell in cells]
            if row_data:
                table_data.append(row_data)
        
        if table_data:
            tables.append({
                'headers': table_data[0] if table_data else [],
                'rows': table_data[1:] if len(table_data) > 1 else []
            })
    
    return tables


def extract_factual_data(soup: BeautifulSoup, content: str) -> Dict:
    """
    Extract structured factual data from page content
    Looks for expense ratio, exit load, minimum SIP, lock-in, riskometer, benchmark, etc.
    
    Args:
        soup: BeautifulSoup object
        content: Extracted text content
        
    Returns:
        Dictionary with extracted factual data
    """
    factual_data = {
        'expense_ratio_regular': None,
        'expense_ratio_direct': None,
        'exit_load': None,
        'minimum_sip': None,
        'minimum_lumpsum': None,
        'lock_in_period': None,
        'riskometer': None,
        'benchmark': None,
    }
    
    content_lower = content.lower()
    
    # Extract expense ratio (Regular and Direct)
    # Look for patterns like "Expense Ratio Regular" or "Regular Expense Ratio"
    
    # Pattern for expense ratio regular: "Expense Ratio Regular in % (as on ...) is 1.48"
    # More flexible patterns to handle various formats
    er_regular_patterns = [
        r'expense\s+ratio\s+regular\s+in\s*%\s*\([^)]+\)\s+is\s+(\d+\.?\d*)',
        r'expense\s+ratio\s+regular[^\d]*(\d+\.?\d*)\s*%',
        r'regular\s+expense\s+ratio[^\d]*(\d+\.?\d*)\s*%',
        r'expense\s+ratio.*regular.*?(\d+\.?\d*)\s*%',
        r'regular[^\d]*(\d+\.?\d*)\s*%',  # Fallback: just "regular" followed by percentage
    ]
    
    # Search in both lowercase and original case (for better matching)
    for pattern in er_regular_patterns:
        match = re.search(pattern, content_lower, re.IGNORECASE)
        if match:
            factual_data['expense_ratio_regular'] = match.group(1)
            break
    
    # Pattern for expense ratio direct: "Expense Ratio Direct in % (as on ...) is 0.81"
    er_direct_patterns = [
        r'expense\s+ratio\s+direct\s+in\s*%\s*\([^)]+\)\s+is\s+(\d+\.?\d*)',
        r'expense\s+ratio\s+direct[^\d]*(\d+\.?\d*)\s*%',
        r'direct\s+expense\s+ratio[^\d]*(\d+\.?\d*)\s*%',
        r'expense\s+ratio.*direct.*?(\d+\.?\d*)\s*%',
        r'direct[^\d]*(\d+\.?\d*)\s*%',  # Fallback: just "direct" followed by percentage
    ]
    
    for pattern in er_direct_patterns:
        match = re.search(pattern, content_lower, re.IGNORECASE)
        if match:
            factual_data['expense_ratio_direct'] = match.group(1)
            break
    
    # Extract exit load
    exit_load_patterns = [
        r'exit\s+load[^\d]*(\d+\.?\d*)\s*%',
        r'redemption\s+charge[^\d]*(\d+\.?\d*)\s*%',
        r'exit\s+load.*?(\d+\.?\d*)\s*%',
    ]
    
    for pattern in exit_load_patterns:
        match = re.search(pattern, content_lower, re.IGNORECASE)
        if match:
            factual_data['exit_load'] = match.group(1)
            break
    
    # Extract minimum SIP
    sip_patterns = [
        r'minimum\s+sip[^\d]*₹?\s*(\d+(?:,\d+)*)',
        r'sip\s+minimum[^\d]*₹?\s*(\d+(?:,\d+)*)',
        r'minimum\s+investment.*sip[^\d]*₹?\s*(\d+(?:,\d+)*)',
    ]
    
    for pattern in sip_patterns:
        match = re.search(pattern, content_lower, re.IGNORECASE)
        if match:
            factual_data['minimum_sip'] = match.group(1).replace(',', '')
            break
    
    # Extract minimum lumpsum
    lumpsum_patterns = [
        r'minimum\s+(?:lump\s+sum|lumpsum|investment)[^\d]*₹?\s*(\d+(?:,\d+)*)',
        r'lump\s+sum\s+minimum[^\d]*₹?\s*(\d+(?:,\d+)*)',
    ]
    
    for pattern in lumpsum_patterns:
        match = re.search(pattern, content_lower, re.IGNORECASE)
        if match:
            factual_data['minimum_lumpsum'] = match.group(1).replace(',', '')
            break
    
    # Extract lock-in period
    lockin_patterns = [
        r'lock[-\s]?in\s+period[^\d]*(\d+)\s*(?:year|yr|month|months)',
        r'lock[-\s]?in[^\d]*(\d+)\s*(?:year|yr|month|months)',
        r'minimum\s+holding\s+period[^\d]*(\d+)\s*(?:year|yr|month|months)',
    ]
    
    for pattern in lockin_patterns:
        match = re.search(pattern, content_lower, re.IGNORECASE)
        if match:
            factual_data['lock_in_period'] = match.group(1)
            break
    
    # Extract riskometer (look for risk level descriptions)
    riskometer_patterns = [
        r'riskometer[^\d]*(\d+)',
        r'risk\s+level[^\d]*(\d+)',
        r'riskometer\s+rating[^\d]*(\d+)',
    ]
    
    for pattern in riskometer_patterns:
        match = re.search(pattern, content_lower, re.IGNORECASE)
        if match:
            factual_data['riskometer'] = match.group(1)
            break
    
    # Extract benchmark (look for benchmark index names)
    benchmark_patterns = [
        r'benchmark[:\s]+([A-Z0-9\s]+(?:index|indices?))',
        r'benchmark\s+index[:\s]+([A-Z0-9\s]+)',
    ]
    
    for pattern in benchmark_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            factual_data['benchmark'] = match.group(1).strip()
            break
    
    return factual_data


def extract_metadata(soup: BeautifulSoup, url: str) -> Dict:
    """
    Extract metadata from HTML page
    
    Args:
        soup: BeautifulSoup object
        url: Source URL
        
    Returns:
        Dictionary with metadata
    """
    metadata = {
        'url': url,
        'title': '',
        'last_modified': None,
        'breadcrumbs': []
    }
    
    # Extract title
    title_tag = soup.find('title')
    if title_tag:
        metadata['title'] = title_tag.get_text(strip=True)
    
    # Try to find last modified date (various formats)
    # Check meta tags
    meta_date = soup.find('meta', {'property': 'article:modified_time'}) or \
                soup.find('meta', {'name': 'last-modified'}) or \
                soup.find('meta', {'name': 'date'})
    
    if meta_date:
        metadata['last_modified'] = meta_date.get('content', '').strip()
    
    # Extract breadcrumbs if available
    breadcrumb_nav = soup.find('nav', {'aria-label': 'breadcrumb'}) or \
                     soup.find(class_='breadcrumb') or \
                     soup.find(id='breadcrumb')
    
    if breadcrumb_nav:
        breadcrumb_links = breadcrumb_nav.find_all('a')
        metadata['breadcrumbs'] = [link.get_text(strip=True) for link in breadcrumb_links]
    
    return metadata


def scrape_url(url: str, driver: Optional[webdriver.Chrome] = None, 
                check_robots: bool = True, use_selenium: bool = True) -> Optional[Dict]:
    """
    Scrape a single URL and extract content
    
    Args:
        url: URL to scrape
        driver: Selenium WebDriver instance (created if None and use_selenium=True)
        check_robots: Whether to check robots.txt
        use_selenium: Whether to use Selenium for JavaScript-rendered pages
        
    Returns:
        Dictionary with scraped data or None if failed
    """
    # Validate URL
    if not validate_url(url):
        return None
    
    # Check robots.txt
    if check_robots:
        if not check_robots_txt(url):
            return None
    
    # Rate limiting
    time.sleep(RATE_LIMIT_DELAY)
    
    # Initialize driver if needed
    driver_created = False
    if use_selenium:
        if driver is None:
            driver = init_webdriver(headless=True)
            if driver is None:
                logger.error("Failed to initialize WebDriver")
                return None
            driver_created = True
    
    try:
        # Fetch page
        logger.info(f"Scraping: {url}")
        
        if use_selenium and driver:
            # Use Selenium for JavaScript-rendered pages
            page_data = get_page_content_selenium(url, driver)
            if not page_data:
                return None
            
            soup = page_data['soup']
            raw_html = page_data['html']
        else:
            # Fallback to requests (for non-JS pages)
            import requests
            response = requests.get(url, headers={'User-Agent': USER_AGENT}, timeout=10)
            response.raise_for_status()
            raw_html = response.text
            soup = BeautifulSoup(response.content, 'lxml')
        
        # Extract content
        content = extract_main_content(soup, url)
        
        # Look for data in script tags
        script_content = ""
        for script in soup.find_all('script'):
            if script.string:
                script_content += script.string + "\n"
        
        # Combine content sources for pattern matching
        full_content = content + "\n" + script_content + "\n" + raw_html
        
        tables = extract_tables(soup)
        metadata = extract_metadata(soup, url)
        factual_data = extract_factual_data(soup, full_content)
        
        # Prepare scraped data structure
        scraped_data = {
            'url': url,
            'title': metadata['title'],
            'content': content,
            'tables': tables,
            'metadata': metadata,
            'factual_data': factual_data,  # Structured factual data
            'scraped_date': datetime.now().isoformat(),
            'scheme_name': None,  # To be filled manually or via URL analysis
            'document_type': None  # To be filled manually or via URL analysis
        }
        
        logger.info(f"Successfully scraped: {url} ({len(content)} characters)")
        
        return scraped_data
    
    except Exception as e:
        logger.error(f"Error scraping {url}: {e}")
        return None
    
    finally:
        # Close driver if we created it
        if driver_created and driver:
            driver.quit()


def scrape_urls_list(urls: List[str], output_file: str = "data/raw/scraped_data.json", 
                     check_robots: bool = True, use_selenium: bool = True) -> Dict:
    """
    Scrape multiple URLs and save results to JSON file
    
    Args:
        urls: List of URLs to scrape
        output_file: Path to output JSON file
        check_robots: Whether to check robots.txt
        use_selenium: Whether to use Selenium for JavaScript-rendered pages
        
    Returns:
        Dictionary with scraping statistics
    """
    results = []
    failed_urls = []
    successful_count = 0
    
    # Initialize driver once for all URLs (more efficient)
    driver = None
    if use_selenium:
        driver = init_webdriver(headless=True)
        if driver is None:
            logger.error("Failed to initialize WebDriver. Falling back to requests.")
            use_selenium = False
    
    try:
        logger.info(f"Starting to scrape {len(urls)} URLs")
        
        for i, url in enumerate(urls, 1):
            logger.info(f"Processing URL {i}/{len(urls)}: {url}")
            
            scraped_data = scrape_url(url, driver=driver, check_robots=check_robots, 
                                     use_selenium=use_selenium)
            
            if scraped_data:
                results.append(scraped_data)
                successful_count += 1
            else:
                failed_urls.append(url)
                logger.warning(f"Failed to scrape: {url}")
    
    finally:
        # Close driver when done
        if driver:
            driver.quit()
    
    # Save results to JSON file
    try:
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(results)} scraped documents to {output_file}")
    except Exception as e:
        logger.error(f"Error saving to {output_file}: {e}")
        raise
    
    # Return statistics
    stats = {
        'total_urls': len(urls),
        'successful': successful_count,
        'failed': len(failed_urls),
        'failed_urls': failed_urls,
        'output_file': output_file
    }
    
    logger.info(f"Scraping complete: {successful_count}/{len(urls)} successful")
    
    return stats


if __name__ == "__main__":
    # Test with SBI Large Cap Fund URL
    test_urls = [
        "https://www.sbimf.com/sbimf-scheme-details/sbi-large-cap-fund-(formerly-known-as-sbi-bluechip-fund)-43",
    ]
    
    print("Testing scraper with Selenium for JavaScript-rendered pages...")
    print("Testing with SBI Large Cap Fund URL...")
    stats = scrape_urls_list(test_urls, output_file="data/raw/test_scraped_data.json", 
                            use_selenium=True)
    
    print(f"\nScraping Statistics:")
    print(f"Total URLs: {stats['total_urls']}")
    print(f"Successful: {stats['successful']}")
    print(f"Failed: {stats['failed']}")
    if stats['failed_urls']:
        print(f"Failed URLs: {stats['failed_urls']}")
    
    # Display extracted factual data
    if stats['successful'] > 0:
        import json
        try:
            with open("data/raw/test_scraped_data.json", 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data:
                    print("\n" + "="*50)
                    print("EXTRACTED FACTUAL DATA:")
                    print("="*50)
                    factual = data[0].get('factual_data', {})
                    print(f"Expense Ratio Regular: {factual.get('expense_ratio_regular', 'Not found')}%")
                    print(f"Expense Ratio Direct: {factual.get('expense_ratio_direct', 'Not found')}%")
                    print(f"Exit Load: {factual.get('exit_load', 'Not found')}%")
                    min_sip = factual.get('minimum_sip', 'Not found')
                    min_lumpsum = factual.get('minimum_lumpsum', 'Not found')
                    print(f"Minimum SIP: Rs. {min_sip if min_sip != 'Not found' else min_sip}")
                    print(f"Minimum Lumpsum: Rs. {min_lumpsum if min_lumpsum != 'Not found' else min_lumpsum}")
                    print(f"Lock-in Period: {factual.get('lock_in_period', 'Not found')}")
                    print(f"Riskometer: {factual.get('riskometer', 'Not found')}")
                    print(f"Benchmark: {factual.get('benchmark', 'Not found')}")
                    print("="*50)
                    
                    # Validation
                    print("\nVALIDATION:")
                    expected_regular = "1.48"
                    expected_direct = "0.81"
                    actual_regular = factual.get('expense_ratio_regular')
                    actual_direct = factual.get('expense_ratio_direct')
                    
                    if actual_regular == expected_regular:
                        print(f"[OK] Expense Ratio Regular: CORRECT ({actual_regular}%)")
                    else:
                        print(f"[X] Expense Ratio Regular: EXPECTED {expected_regular}%, GOT {actual_regular}")
                    
                    if actual_direct == expected_direct:
                        print(f"[OK] Expense Ratio Direct: CORRECT ({actual_direct}%)")
                    else:
                        print(f"[X] Expense Ratio Direct: EXPECTED {expected_direct}%, GOT {actual_direct}")
                    
                    # Debug: Show sample of content searched
                    print("\nDEBUG: Sample of content searched (first 500 chars):")
                    content_sample = data[0].get('content', '')[:500]
                    print(content_sample)
                    print("\nNote: If expense ratios are not found, the page may be JavaScript-rendered.")
                    print("Consider using Selenium for dynamic content or checking for API endpoints.")
        except Exception as e:
            print(f"Error reading test data: {e}")

