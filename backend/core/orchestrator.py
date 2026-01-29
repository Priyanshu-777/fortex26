import os
from dotenv import load_dotenv
from ai.planner import AIAttackPlanner
from ai.severity import SeverityScorer


from zap.zap_client import ZAPClient
from zap.adapter import zap_surface_to_endpoints
from attacks.idor import IDORTester
from attacks.auth import AuthTester
from attacks.xss import XSSTester
from attacks.dom_xss import DOMXSSTester
from reporting.report_generator import ReportGenerator

class Orchestrator:
    def __init__(self, target_url=None, log_callback=None):
        load_dotenv()

        self.zap_proxy = os.getenv("ZAP_PROXY")
        self.zap_api_key = os.getenv("ZAP_API_KEY")
        
        # Accept target_url as parameter or fall back to .env
        self.target_url = target_url or os.getenv("TARGET_URL")
        self.log_callback = log_callback

        if not self.zap_proxy or not self.target_url:
            raise RuntimeError("ZAP_PROXY or TARGET_URL missing")

        self.zap = ZAPClient(
            zap_proxy=self.zap_proxy,
            api_key=self.zap_api_key,
        )
    
    def log(self, message, log_type="info"):
        """Log message to console and callback if provided"""
        print(message)
        if self.log_callback:
            self.log_callback(message, log_type)

    def run(self):
        self.log("[+] Orchestrator started")
        self.log(f"[+] Target: {self.target_url}")
        
        findings = []

        # -----------------------------
        # ZAP Recon
        # -----------------------------
        self.log("[Step 3] Resetting ZAP session", "step")
        self.zap.reset_session()

        self.log("[Step 4] Running spider to discover pages", "step")
        self.zap.spider(self.target_url)

        self.log("[Step 4b] Running AJAX spider", "step")
        self.zap.ajax_spider(self.target_url)

        self.log("[Step 5] Waiting for passive scan", "step")
        self.zap.wait_for_passive_scan()

        # -----------------------------
        # Extract Attack Surface
        # -----------------------------
        self.log("[Step 6] Extracting attack surface", "step")
        attack_surface = self.zap.extract_attack_surface()
        self.log(f"[+] Found {len(attack_surface)} request patterns")

        if not attack_surface:
            self.log("[-] No attack surface found", "error")
            return {
                "findings": [],
                "attack_surface": [],
                "attack_plan": {},
                "risk_level": "LOW"
            }

        # -----------------------------
        # AI Attack Planning
        # -----------------------------
        self.log("[Step 7] Running AI attack planner", "step")
        planner = AIAttackPlanner()
        attack_plan = planner.plan(attack_surface)

        self.log("[AI] Attack Plan generated")
        for r in attack_plan["reasoning"]:
            self.log(f" - {r}")

        # -----------------------------
        # Prepare IDOR Targets
        # -----------------------------
        self.log("[Step 8] Preparing IDOR endpoints", "step")
        idor_targets = zap_surface_to_endpoints(
            attack_surface=attack_surface,
            base_url=self.target_url.rstrip("/"),
        )
        
        # Only proceed if AI planned IDOR
        if not any(a["type"] == "IDOR" for a in attack_plan["attacks"]):
            self.log("[AI] No IDOR attacks planned")
            # We continue to allow other tests to run

        self.log(f"[+] {len(idor_targets)} endpoints ready for testing")

        proxies = {
            "http": self.zap_proxy,
            "https": self.zap_proxy,
        }

        # -----------------------------
        # Run IDOR Attacks
        # -----------------------------
        if any(a["type"] == "IDOR" for a in attack_plan["attacks"]):
            self.log("[Step 9] Running IDOR tests", "step")
            idor = IDORTester(
                base_url=self.target_url,
                headers={
                    # Add auth if needed
                    # "Authorization": "Bearer YOUR_TOKEN"
                },
                proxies=proxies,
            )

            findings.extend(idor.run(idor_targets))

        # -----------------------------
        # Run AUTH Tests
        # -----------------------------
        if any(a["type"] == "AUTH" for a in attack_plan["attacks"]):
            self.log("[Step 10] Running authentication checks", "step")

            auth = AuthTester(
                headers={
                    # Example
                },
                proxies=proxies,
            )

            findings.extend(auth.run(idor_targets))

        # -----------------------------
        # Run XSS Tests
        # -----------------------------
        if any(a["type"] == "XSS" for a in attack_plan["attacks"]):
            self.log("[Step 11] Running XSS tests", "step")

            xss = XSSTester(
                headers={
                    # Add auth header if required
                },
                proxies=proxies,
            )

            findings.extend(xss.run(idor_targets))

        # -----------------------------
        # Run DOM-XSS Tests
        # -----------------------------
        if any(a["type"] == "DOM-XSS" for a in attack_plan["attacks"]):
            self.log("[Step 12] Running DOM-XSS analysis", "step")

            dom_xss = DOMXSSTester(
                headers={
                    # Optional auth
                },
                proxies=proxies,
            )

            findings.extend(dom_xss.run(idor_targets))

        # -----------------------------
        # Severity Scoring
        # -----------------------------
        if findings:
            self.log("[Step 13] Scoring vulnerability severity", "step")
            scorer = SeverityScorer()

            for f in findings:
                scorer.score(f)

        # -----------------------------
        # Reporting
        # -----------------------------
        self.log("========== SCAN RESULTS ==========")

        if findings:
            for i, f in enumerate(findings, 1):
                self.log(f"[{i}] {f['vulnerability']} ({f['severity']})")
                self.log(f"    Endpoint: {f.get('endpoint')}")
                self.log(f"    Impact: {f.get('impact')}")

            self.log("[Step 14] Generating report", "step")
            report = ReportGenerator(
                target=self.target_url,
                findings=findings,
                attack_surface=attack_surface,
                attack_plan=attack_plan
            )
            path = report.save()
            self.log(f"[+] Report saved at: {path}", "success")
        else:
            self.log("[+] No vulnerabilities found", "success")
            
            # Always generate report
            self.log("[Step 14] Generating report", "step")
            report = ReportGenerator(
                target=self.target_url,
                findings=[],
                attack_surface=attack_surface,
                attack_plan=attack_plan
            )
            path = report.save()
            self.log(f"[+] Report saved at: {path}", "success")

        self.log("[+] Orchestrator finished", "success")
        
        return {
            "findings": findings,
            "attack_surface": attack_surface,
            "attack_plan": attack_plan,
            "risk_level": "HIGH" if findings else "LOW" # Simple logic for now
        }
