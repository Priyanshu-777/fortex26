import requests

class DOMXSSTester:
    def __init__(self, headers=None, proxies=None):
        self.headers = headers or {}
        self.proxies = proxies or {}
        self.sinks = [
            "document.write",
            "innerHTML",
            "outerHTML",
            "location.hash",
            "window.name"
        ]

    def test_endpoint(self, endpoint):
        if isinstance(endpoint, dict):
            url = endpoint.get("url") or endpoint.get("path")
        else:
            url = endpoint

        if not url:
            return None
            
        print(f"[DOM-XSS] Analyzing {url}")
        
        try:
            resp = requests.get(url, headers=self.headers, timeout=5, proxies=self.proxies)
            content = resp.text
            
            found_sinks = []
            for sink in self.sinks:
                if sink in content:
                    found_sinks.append(sink)
            
            if found_sinks:
                return {
                    "vulnerability": "Potential DOM XSS",
                    "endpoint": url,
                    "sinks_found": found_sinks,
                    "impact": "Client-side script execution via DOM manipulation",
                    "severity": "Medium"
                }

        except requests.RequestException:
            pass
            
        return None

    def run(self, endpoints):
        all_findings = []
        for ep in endpoints:
            result = self.test_endpoint(ep)
            if result:
                all_findings.append(result)
        return all_findings
