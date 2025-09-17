import requests
import random
import time
import json
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
import trafilatura
from typing import Dict, List, Optional
import threading
from urllib.parse import urljoin, urlparse

class AntiDetectionScraper:
    """
    Advanced web scraping engine with anti-detection features for bypassing bot prevention
    """
    
    def __init__(self):
        self.user_agent = UserAgent()
        self.session = requests.Session()
        self.proxies = []  # Will be populated with proxy rotation
        self.current_proxy_index = 0
        self.rate_limit = 2  # Minimum seconds between requests
        self.max_retries = 3
        
    def get_random_headers(self) -> Dict[str, str]:
        """Generate random headers to mimic real browser requests"""
        headers = {
            'User-Agent': self.user_agent.random,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': random.choice([
                'en-US,en;q=0.9',
                'en-GB,en;q=0.9',
                'es-ES,es;q=0.8,en;q=0.7',
                'fr-FR,fr;q=0.8,en;q=0.7'
            ]),
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        }
        
        # Randomly add some additional headers
        if random.choice([True, False]):
            headers['Referer'] = random.choice([
                'https://www.google.com/',
                'https://www.bing.com/',
                'https://duckduckgo.com/'
            ])
            
        return headers
    
    def add_proxies(self, proxy_list: List[str]):
        """Add proxy servers for rotation"""
        self.proxies = proxy_list
        
    def get_next_proxy(self) -> Optional[Dict[str, str]]:
        """Get next proxy in rotation"""
        if not self.proxies:
            return None
            
        proxy = self.proxies[self.current_proxy_index]
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)
        
        return {
            'http': proxy,
            'https': proxy
        }
    
    def human_delay(self):
        """Add human-like delay between requests"""
        delay = self.rate_limit + random.uniform(0.5, 3.0)
        time.sleep(delay)
    
    def scrape_url(self, url: str, use_trafilatura: bool = False) -> Optional[Dict]:
        """
        Scrape a single URL with anti-detection measures
        """
        for attempt in range(self.max_retries):
            try:
                # Get random headers and proxy
                headers = self.get_random_headers()
                proxies = self.get_next_proxy()
                
                # Make request with session
                response = self.session.get(
                    url,
                    headers=headers,
                    proxies=proxies,
                    timeout=30,
                    verify=True
                )
                
                if response.status_code == 200:
                    if use_trafilatura:
                        # Use trafilatura for clean text extraction
                        text_content = trafilatura.extract(response.text)
                        return {
                            'url': url,
                            'status': 'success',
                            'content': text_content,
                            'method': 'trafilatura'
                        }
                    else:
                        # Use BeautifulSoup for HTML parsing
                        soup = BeautifulSoup(response.text, 'html.parser')
                        return {
                            'url': url,
                            'status': 'success',
                            'content': response.text,
                            'title': soup.title.string if soup.title else '',
                            'method': 'beautifulsoup'
                        }
                        
                elif response.status_code == 429:
                    # Rate limited - wait longer
                    print(f"Rate limited for {url}, waiting...")
                    time.sleep(random.uniform(10, 20))
                    continue
                    
                else:
                    print(f"HTTP {response.status_code} for {url}")
                    
            except requests.exceptions.RequestException as e:
                print(f"Request error for {url} (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(random.uniform(5, 10))
                    continue
                    
            # Add delay between attempts
            if attempt < self.max_retries - 1:
                self.human_delay()
        
        return {
            'url': url,
            'status': 'failed',
            'content': None,
            'method': None
        }
    
    def bulk_scrape(self, urls: List[str], use_trafilatura: bool = False) -> List[Dict]:
        """
        Scrape multiple URLs with delays and anti-detection
        """
        results = []
        
        for i, url in enumerate(urls):
            print(f"Scraping {i+1}/{len(urls)}: {url}")
            result = self.scrape_url(url, use_trafilatura)
            results.append(result)
            
            # Add human-like delay between requests
            if i < len(urls) - 1:  # Don't delay after the last request
                self.human_delay()
        
        return results

class GoogleMapsScraper(AntiDetectionScraper):
    """
    Specialized scraper for Google Maps data extraction
    """
    
    def extract_business_info(self, search_query: str, location: str = "") -> List[Dict]:
        """
        Extract business information from Google Maps search
        """
        # Construct Google Maps search URL
        base_url = "https://www.google.com/maps/search/"
        query = f"{search_query} {location}".strip()
        search_url = f"{base_url}{query.replace(' ', '+')}"
        
        print(f"Searching Google Maps for: {query}")
        result = self.scrape_url(search_url)
        
        businesses = []
        
        if result and result['status'] == 'success' and 'soup' in result:
            soup = result['soup']
            
            # Extract business listings (this is a simplified example)
            # Google Maps uses complex JS-rendered content, this is a basic approach
            business_elements = soup.find_all('div', attrs={'data-cid': True})
            
            for element in business_elements[:10]:  # Limit to first 10 results
                try:
                    name = element.find('span', class_='fontHeadlineSmall')
                    name = name.text.strip() if name else "Unknown"
                    
                    rating_element = element.find('span', attrs={'aria-label': True})
                    rating = rating_element.get('aria-label', '') if rating_element else ""
                    
                    address_element = element.find('div', class_='fontBodyMedium')
                    address = address_element.text.strip() if address_element else ""
                    
                    business_info = {
                        'name': name,
                        'rating': rating,
                        'address': address,
                        'search_query': query,
                        'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    businesses.append(business_info)
                    
                except Exception as e:
                    print(f"Error extracting business info: {e}")
                    continue
        
        return businesses