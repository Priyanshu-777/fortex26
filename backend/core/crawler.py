import requests
import re
from urllib.parse import urljoin, urlparse

class SimpleCrawler:
    def __init__(self, base_url, log_callback=None):
        self.base_url = base_url.rstrip("/")
        self.log_callback = log_callback
        self.visited = set()
        self.to_visit = [self.base_url]
        self.attack_surface = []

    def log(self, message):
        if self.log_callback:
            self.log_callback(message)
        else:
            print(message)

    def is_internal(self, url):
        return url.startswith(self.base_url)

    def crawl(self, limit=20):
        self.log(f"[Crawler] Starting simple crawl on {self.base_url} (limit: {limit} pages)")
        
        count = 0
        while self.to_visit and count < limit:
            url = self.to_visit.pop(0)
            if url in self.visited:
                continue
            
            self.visited.add(url)
            count += 1
            
            try:
                self.log(f"  Crawling: {url}")
                resp = requests.get(url, timeout=5)
                if resp.status_code != 200:
                    continue
                
                # Basic attack surface extraction from this page
                self.extract_from_page(url, resp.text)
                
                # Find more links
                links = re.findall(r'href=["\'](https?://[^"\']+|/[^"\']+)["\']', resp.text)
                for link in links:
                    full_url = urljoin(url, link).split("#")[0].rstrip("/")
                    if self.is_internal(full_url) and full_url not in self.visited:
                        self.to_visit.append(full_url)
                        
            except Exception as e:
                self.log(f"  Error crawling {url}: {e}")

        return self.attack_surface

    def extract_from_page(self, url, html):
        # Add the page itself
        parsed = urlparse(url)
        params = []
        if parsed.query:
            for p in parsed.query.split("&"):
                if "=" in p:
                    params.append(p.split("=")[0])
        
        self.attack_surface.append({
            "method": "GET",
            "path": parsed.path or "/",
            "url": url,
            "parameters": list(set(params)),
            "raw_request": f"GET {url} HTTP/1.1"
        })

        # Find forms (basic)
        forms = re.findall(r'<form[^>]+>(.*?)</form>', html, re.DOTALL | re.IGNORECASE)
        for form_content in forms:
            # Extract inputs
            inputs = re.findall(r'name=["\']([^"\']+)["\']', form_content, re.IGNORECASE)
            if inputs:
                self.attack_surface.append({
                    "method": "POST", # Assume POST for forms
                    "path": parsed.path or "/",
                    "url": url,
                    "parameters": list(set(inputs)),
                    "raw_request": f"POST {url} HTTP/1.1\n\n(Form Inputs: {', '.join(inputs)})"
                })
