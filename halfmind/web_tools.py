import os
import re
import json
import hashlib
from pathlib import Path
from urllib.parse import urlparse, urljoin


class WebTools:
    """Tools for web scraping, HTTP requests, and URL manipulation"""
    
    ALLOWED_SCHEMES = {'http', 'https'}
    MAX_RESPONSE_SIZE = 50 * 1024 * 1024
    
    def __init__(self, timeout=30, max_retries=3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = None
    
    def _validate_url(self, url):
        """Validates URL for security"""
        parsed = urlparse(url)
        if parsed.scheme not in self.ALLOWED_SCHEMES:
            raise ValueError(f"Invalid URL scheme: {parsed.scheme}")
        if not parsed.netloc:
            raise ValueError("Invalid URL: missing hostname")
        return url
    
    def _get_session(self):
        """Returns or creates a requests session"""
        import requests
        if self.session is None:
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'HalfMind WebTools/1.0'
            })
        return self.session
    
    def fetch_url(self, url, headers=None, params=None):
        """Fetches content from a URL"""
        import requests
        validated_url = self._validate_url(url)
        session = self._get_session()
        if headers:
            session.headers.update(headers)
        response = session.get(
            validated_url,
            params=params,
            timeout=self.timeout,
            stream=True
        )
        response.raise_for_status()
        content = response.content[:self.MAX_RESPONSE_SIZE]
        return {
            'status_code': response.status_code,
            'headers': dict(response.headers),
            'content': content,
            'text': response.text[:self.MAX_RESPONSE_SIZE],
            'url': response.url
        }
    
    def download_file(self, url, output_path, chunk_size=8192):
        """Downloads a file from a URL"""
        import requests
        validated_url = self._validate_url(url)
        session = self._get_session()
        response = session.get(validated_url, stream=True, timeout=self.timeout)
        response.raise_for_status()
        total_size = 0
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)
                    total_size += len(chunk)
                    if total_size > self.MAX_RESPONSE_SIZE:
                        raise ValueError("Download exceeds maximum file size")
        return {
            'file_path': output_path,
            'file_size': total_size,
            'content_type': response.headers.get('content-type', '')
        }
    
    def post_data(self, url, data=None, json_data=None, headers=None):
        """Sends POST request with data or JSON"""
        import requests
        validated_url = self._validate_url(url)
        session = self._get_session()
        response = session.post(
            validated_url,
            data=data,
            json=json_data,
            headers=headers,
            timeout=self.timeout
        )
        response.raise_for_status()
        return {
            'status_code': response.status_code,
            'headers': dict(response.headers),
            'text': response.text,
            'json': response.json() if response.headers.get('content-type', '').startswith('application/json') else None
        }
    
    def put_data(self, url, data=None, json_data=None, headers=None):
        """Sends PUT request"""
        import requests
        validated_url = self._validate_url(url)
        session = self._get_session()
        response = session.put(
            validated_url,
            data=data,
            json=json_data,
            headers=headers,
            timeout=self.timeout
        )
        response.raise_for_status()
        return {
            'status_code': response.status_code,
            'text': response.text
        }
    
    def delete_resource(self, url, headers=None):
        """Sends DELETE request"""
        import requests
        validated_url = self._validate_url(url)
        session = self._get_session()
        response = session.delete(validated_url, headers=headers, timeout=self.timeout)
        response.raise_for_status()
        return {
            'status_code': response.status_code,
            'text': response.text
        }
    
    def scrape_html(self, url, selector=None):
        """Scrapes HTML content from a URL, optionally extracting by CSS selector"""
        from bs4 import BeautifulSoup
        import requests
        validated_url = self._validate_url(url)
        session = self._get_session()
        response = session.get(validated_url, timeout=self.timeout)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        if selector:
            elements = soup.select(selector)
            return [elem.get_text(strip=True) for elem in elements]
        return soup.get_text(strip=True)
    
    def extract_links(self, url, base_url=None):
        """Extracts all links from a webpage"""
        from bs4 import BeautifulSoup
        import requests
        validated_url = self._validate_url(url)
        session = self._get_session()
        response = session.get(validated_url, timeout=self.timeout)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        links = []
        for anchor in soup.find_all('a', href=True):
            href = anchor['href']
            if base_url:
                href = urljoin(base_url, href)
            links.append({
                'url': href,
                'text': anchor.get_text(strip=True),
                'title': anchor.get('title', '')
            })
        return links
    
    def extract_images(self, url, base_url=None):
        """Extracts all image URLs from a webpage"""
        from bs4 import BeautifulSoup
        import requests
        validated_url = self._validate_url(url)
        session = self._get_session()
        response = session.get(validated_url, timeout=self.timeout)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        images = []
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if base_url and src:
                src = urljoin(base_url, src)
            images.append({
                'src': src,
                'alt': img.get('alt', ''),
                'title': img.get('title', '')
            })
        return images
    
    def extract_metadata(self, url):
        """Extracts metadata from a webpage"""
        from bs4 import BeautifulSoup
        import requests
        validated_url = self._validate_url(url)
        session = self._get_session()
        response = session.get(validated_url, timeout=self.timeout)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        metadata = {
            'title': '',
            'description': '',
            'keywords': [],
            'og_data': {},
            'twitter_data': {}
        }
        title_tag = soup.find('title')
        if title_tag:
            metadata['title'] = title_tag.get_text(strip=True)
        for meta in soup.find_all('meta'):
            name = meta.get('name', '').lower()
            property_attr = meta.get('property', '').lower()
            content = meta.get('content', '')
            if name == 'description':
                metadata['description'] = content
            elif name == 'keywords':
                metadata['keywords'] = [k.strip() for k in content.split(',')]
            elif property_attr.startswith('og:'):
                metadata['og_data'][property_attr[3:]] = content
            elif name.startswith('twitter:'):
                metadata['twitter_data'][name[8:]] = content
        return metadata
    
    def check_url_status(self, url):
        """Checks if a URL is accessible and returns status"""
        import requests
        validated_url = self._validate_url(url)
        try:
            session = self._get_session()
            response = session.head(validated_url, timeout=self.timeout, allow_redirects=True)
            return {
                'url': url,
                'status_code': response.status_code,
                'accessible': response.status_code < 400,
                'final_url': response.url,
                'content_type': response.headers.get('content-type', '')
            }
        except requests.RequestException as e:
            return {
                'url': url,
                'status_code': None,
                'accessible': False,
                'error': str(e)
            }
    
    def get_page_speed(self, url):
        """Measures page load time"""
        import requests
        import time
        validated_url = self._validate_url(url)
        session = self._get_session()
        start_time = time.time()
        response = session.get(validated_url, timeout=self.timeout)
        end_time = time.time()
        return {
            'url': url,
            'load_time': round(end_time - start_time, 3),
            'status_code': response.status_code,
            'content_length': len(response.content),
            'headers': dict(response.headers)
        }
    
    def parse_sitemap(self, sitemap_url):
        """Parses XML sitemap and returns URLs"""
        import requests
        from bs4 import BeautifulSoup
        validated_url = self._validate_url(sitemap_url)
        session = self._get_session()
        response = session.get(validated_url, timeout=self.timeout)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'xml')
        urls = []
        for url_tag in soup.find_all('url'):
            loc = url_tag.find('loc')
            if loc:
                urls.append({
                    'url': loc.get_text(strip=True),
                    'lastmod': url_tag.find('lastmod').get_text(strip=True) if url_tag.find('lastmod') else '',
                    'changefreq': url_tag.find('changefreq').get_text(strip=True) if url_tag.find('changefreq') else '',
                    'priority': url_tag.find('priority').get_text(strip=True) if url_tag.find('priority') else ''
                })
        return urls
    
    def validate_html(self, url):
        """Basic HTML validation check"""
        from bs4 import BeautifulSoup
        import requests
        validated_url = self._validate_url(url)
        session = self._get_session()
        response = session.get(validated_url, timeout=self.timeout)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        issues = []
        if not soup.find('html'):
            issues.append("Missing <html> tag")
        if not soup.find('head'):
            issues.append("Missing <head> tag")
        if not soup.find('title'):
            issues.append("Missing <title> tag")
        if not soup.find('body'):
            issues.append("Missing <body> tag")
        for img in soup.find_all('img'):
            if not img.get('alt'):
                issues.append(f"Image missing alt attribute: {img.get('src', 'unknown')}")
        return {
            'valid': len(issues) == 0,
            'issues': issues
        }
    
    def create_url_hash(self, url):
        """Creates a hash of a URL for caching purposes"""
        return hashlib.md5(url.encode()).hexdigest()
    
    def normalize_url(self, url):
        """Normalizes a URL by removing fragments and standardizing"""
        parsed = urlparse(url)
        normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        if parsed.query:
            normalized += f"?{parsed.query}"
        return normalized.lower().rstrip('/')