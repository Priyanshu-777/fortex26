import requests

class AuthTester:
    def __init__(self, headers=None, proxies=None):
        self.auth_headers = headers or {}
        self.proxies = proxies or {}

    def test_endpoint(self, endpoint):
        url = endpoint.get("url")
        if not url:
            return None

        print(f"[AUTH] Testing authentication on {url}")

        try:
            auth_resp = requests.get(url, headers=self.auth_headers, timeout=10, proxies=self.proxies)
            noauth_resp = requests.get(url, headers={}, timeout=10, proxies=self.proxies)

        except requests.RequestException:
            return None

        if auth_resp.status_code == 200 and noauth_resp.status_code == 200 and auth_resp.text == noauth_resp.text:
            return {
                "vulnerability": "Missing Authentication",
                "endpoint": url,
                "impact": "Protected endpoint accessible without authentication",
            }

        if auth_resp.status_code == 200 and noauth_resp.status_code == 200 and auth_resp.text != noauth_resp.text:
            return {
                "vulnerability": "Broken Access Control",
                "endpoint": url,
                "impact": "Endpoint leaks data without proper authorization",
            }

        return None

    def run(self, endpoints):
        findings = []
        for ep in endpoints:
            result = self.test_endpoint(ep)
            if result:
                findings.append(result)
        return findings
