import copy
import requests
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

COMMON_ID_PARAMS = ["id", "user_id", "account_id", "order_id", "profile_id"]

class IDORTester:
    def __init__(self, base_url, headers=None, proxies=None):
        self.base_url = base_url.rstrip("/")
        self.headers = headers or {}
        self.proxies = proxies or {}

    def _find_id_param(self, params):
        for p in params:
            if p.lower() in COMMON_ID_PARAMS:
                return p
        return None

    def _increment_id(self, value):
        try:
            return str(int(value) + 1)
        except Exception:
            return value

    def test_endpoint(self, endpoint):
        url = endpoint.get("url")
        if not url:
            return None

        parsed = urlparse(url)
        query = parse_qs(parsed.query)

        id_param = self._find_id_param(query)
        if not id_param:
            return None

        original_value = query[id_param][0]
        tampered_value = self._increment_id(original_value)

        tampered_query = copy.deepcopy(query)
        tampered_query[id_param] = [tampered_value]

        tampered_url = urlunparse(parsed._replace(query=urlencode(tampered_query, doseq=True)))

        print(f"[IDOR] Testing {tampered_url}")

        try:
            original_resp = requests.get(url, headers=self.headers, timeout=10, proxies=self.proxies)
            tampered_resp = requests.get(tampered_url, headers=self.headers, timeout=10, proxies=self.proxies)
        except requests.RequestException:
            return None

        if (original_resp.status_code == 200 and tampered_resp.status_code == 200 and original_resp.text != tampered_resp.text):
            return {
                "vulnerability": "IDOR",
                "endpoint": url,
                "parameter": id_param,
                "original_id": original_value,
                "tampered_id": tampered_value,
                "impact": "Unauthorized access to another user's data",
            }
        return None

    def run(self, endpoints):
        findings = []
        for ep in endpoints:
            result = self.test_endpoint(ep)
            if result:
                findings.append(result)
        return findings
