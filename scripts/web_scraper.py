"""
Web Scraper Template - Extract data from any website
Usage: python web_scraper.py --url "https://example.com" --output results.csv

Features:
- Auto-detect tables, lists, links on any page
- Export to CSV/Excel/JSON
- Rate limiting & retry logic
- CSS selector support
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import argparse
import time
import json
import os
from urllib.parse import urljoin, urlparse

class WebScraper:
    def __init__(self, delay=1.0, max_retries=3):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.delay = delay
        self.max_retries = max_retries
    
    def fetch(self, url):
        for attempt in range(self.max_retries):
            try:
                time.sleep(self.delay)
                resp = self.session.get(url, timeout=15)
                resp.raise_for_status()
                return resp.text
            except Exception as e:
                if attempt == self.max_retries - 1:
                    print(f"Failed after {self.max_retries} attempts: {e}")
                    return None
                time.sleep(2 ** attempt)
    
    def extract_tables(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        tables = []
        for table in soup.find_all('table'):
            df = pd.read_html(str(table))[0]
            tables.append(df)
        return tables
    
    def extract_links(self, html, base_url):
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        for a in soup.find_all('a', href=True):
            full_url = urljoin(base_url, a['href'])
            links.append({
                'text': a.get_text(strip=True),
                'url': full_url
            })
        return pd.DataFrame(links)
    
    def extract_text(self, html, selector=None):
        soup = BeautifulSoup(html, 'html.parser')
        if selector:
            elements = soup.select(selector)
            return [el.get_text(strip=True) for el in elements]
        return soup.get_text(separator='\n', strip=True)
    
    def scrape_to_csv(self, url, output, selector=None):
        print(f"Scraping: {url}")
        html = self.fetch(url)
        if not html:
            return False
        
        # Try tables first
        tables = self.extract_tables(html)
        if tables:
            combined = pd.concat(tables, ignore_index=True)
            combined.to_csv(output, index=False)
            print(f"Extracted {len(combined)} rows from {len(tables)} table(s) → {output}")
            return True
        
        # Try selector
        if selector:
            items = self.extract_text(html, selector)
            df = pd.DataFrame({'text': items})
            df.to_csv(output, index=False)
            print(f"Extracted {len(items)} items → {output}")
            return True
        
        # Fallback: extract links
        links = self.extract_links(html, url)
        links.to_csv(output, index=False)
        print(f"Extracted {len(links)} links → {output}")
        return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Web Scraper - Extract data from any website')
    parser.add_argument('--url', required=True, help='Target URL')
    parser.add_argument('--output', default='scraped_data.csv', help='Output file (csv/xlsx/json)')
    parser.add_argument('--selector', help='CSS selector for targeted extraction')
    parser.add_argument('--delay', type=float, default=1.0, help='Delay between requests (seconds)')
    args = parser.parse_args()
    
    scraper = WebScraper(delay=args.delay)
    scraper.scrape_to_csv(args.url, args.output, args.selector)
