import requests
import urllib.parse
import copy

class XSSTester:
    def __init__(self, headers=None, proxies=None):
        self.headers = headers or {}
        self.proxies = proxies or {}
        self.payloads = [
            "<script>alert(1)</script>",
            "\" onmouseover=\"alert(1)",
            "javascript:alert(1)",
        ]

    def test_endpoint(self, endpoint):
        if isinstance(endpoint, dict):
            url = endpoint.get("url") or endpoint.get("path")
        else:
            url = endpoint

        if not url:
            return None

        print(f"[XSS] Testing {url}")
        
        parsed = urllib.parse.urlparse(url)
        query_params = urllib.parse.parse_qs(parsed.query)
        
        if not query_params:
            return []

        findings = []

        for param, values in query_params.items():
            for payload in self.payloads:
                new_query = copy.deepcopy(query_params)
                new_query[param] = [payload]
                new_query_string = urllib.parse.urlencode(new_query, doseq=True)
                new_url = urllib.parse.urlunparse(parsed._replace(query=new_query_string))

                try:
                    resp = requests.get(new_url, headers=self.headers, timeout=5, proxies=self.proxies)
                    if payload in resp.text:
                        findings.append({
                            "vulnerability": "Reflected XSS",
                            "endpoint": url,
                            "parameter": param,
                            "payload": payload,
                            "impact": "Script injection possible via reflection",
                            "severity": "High"
                        })
                        break
                except requests.RequestException:
                    pass
        
        return findings

    def run(self, endpoints):
        all_findings = []
        for ep in endpoints:
            results = self.test_endpoint(ep)
            if results:
                all_findings.extend(results)
        return all_findings
