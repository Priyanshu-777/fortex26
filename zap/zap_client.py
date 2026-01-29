import time
from zapv2 import ZAPv2

class ZAPClient:
    def __init__(self, zap_proxy="http://127.0.0.1:8080", api_key=None, timeout=60):
        self.zap = ZAPv2(
            apikey=api_key,
            proxies={"http": zap_proxy, "https": zap_proxy},
        )
        self.timeout = timeout

    def spider(self, target_url):
        print(f"[+] Starting spider on {target_url}")
        scan_id = self.zap.spider.scan(target_url)
        while int(self.zap.spider.status(scan_id)) < 100:
            print(f"    Spider progress: {self.zap.spider.status(scan_id)}%")
            time.sleep(2)
        print("[+] Spider completed")

    def ajax_spider(self, target_url):
        print(f"[+] Starting AJAX spider on {target_url}")
        self.zap.ajaxSpider.scan(target_url)
        
        timeout_loops = 0
        while self.zap.ajaxSpider.status == 'running':
            if timeout_loops > 60: # ~2 minutes max for demo
                self.zap.ajaxSpider.stop()
                print("    AJAX Spider timed out")
                break
            print("    AJAX Spider running...")
            time.sleep(2)
            timeout_loops += 1
            
        print("[+] AJAX Spider completed")

    def wait_for_passive_scan(self):
        print("[+] Waiting for passive scan to finish")
        while int(self.zap.pscan.records_to_scan) > 0:
            print(f"    Records left: {self.zap.pscan.records_to_scan}")
            time.sleep(2)
        print("[+] Passive scan completed")

    def get_urls(self):
        return list(set(self.zap.core.urls()))

    def get_http_messages(self):
        return self.zap.core.messages()

    def extract_attack_surface(self):
        attack_surface = []
        messages = self.get_http_messages()

        for msg in messages:
            request_header = msg.get("requestHeader", "")
            request_body = msg.get("requestBody", "")
            
            # Extract URL Line
            url_line = request_header.split("\n")[0]
            try:
                method, full_path_with_query_maybe, _ = url_line.split(" ")
            except ValueError:
                continue

            params = []
            
            # Logic to handle relative vs absolute URL in request line
            # ZAP usually stores absolute URL in history if proxied, or relative if spidered?
            # We'll trust ZAP's 'name' or 'url' fields if available? 
            # msg object has 'requestUrl' usually?
            # But the original code relied on parsing requestHeader.
            # I will improve it: use 'method' 'name' if available. 
            # But adhering to original structure + Fix:
            
            path_only = full_path_with_query_maybe.split("?")[0]
            
            if "?" in full_path_with_query_maybe:
                query = full_path_with_query_maybe.split("?")[1]
                for p in query.split("&"):
                    if "=" in p:
                        params.append(p.split("=")[0])
            
            attack_surface.append({
                "method": method,
                "path": path_only,
                "url": full_path_with_query_maybe, # ADDED THIS FIELD
                "parameters": list(set(params)),
                "raw_request": request_header + "\n" + request_body,
            })

        return attack_surface

    def reset_session(self):
        print("[+] Resetting ZAP session")
        self.zap.core.new_session(overwrite=True)
