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
    def __init__(self):
        load_dotenv()

        self.zap_proxy = os.getenv("ZAP_PROXY")
        self.zap_api_key = os.getenv("ZAP_API_KEY")
        self.target_url = os.getenv("TARGET_URL")

        if not self.zap_proxy or not self.target_url:
            raise RuntimeError("ZAP_PROXY or TARGET_URL missing in .env")

        self.zap = ZAPClient(
            zap_proxy=self.zap_proxy,
            api_key=self.zap_api_key,
        )

    def run(self):
        print("\n[+] Orchestrator started")
        print("[+] Target:", self.target_url)
        
        findings = []

        # -----------------------------
        # ZAP Recon
        # -----------------------------
        print("\n[+] Resetting ZAP session")
        self.zap.reset_session()

        print("[+] Running spider")
        self.zap.spider(self.target_url)

        print("[+] Running AJAX spider")
        self.zap.ajax_spider(self.target_url)

        print("[+] Waiting for passive scan")
        self.zap.wait_for_passive_scan()

        # -----------------------------
        # Extract Attack Surface
        # -----------------------------
        print("\n[+] Extracting attack surface")
        attack_surface = self.zap.extract_attack_surface()
        print(f"[+] Found {len(attack_surface)} request patterns")

        if not attack_surface:
            print("[-] No attack surface found")
            return findings

        # -----------------------------
        # AI Attack Planning
        # -----------------------------
        print("\n[+] Running AI attack planner")
        planner = AIAttackPlanner()
        attack_plan = planner.plan(attack_surface)

        print("\n[AI] Attack Plan:")
        for r in attack_plan["reasoning"]:
            print(" -", r)

        # -----------------------------
        # Prepare IDOR Targets
        # -----------------------------
        print("\n[+] Preparing IDOR endpoints")
        idor_targets = zap_surface_to_endpoints(
            attack_surface=attack_surface,
            base_url=self.target_url.rstrip("/"),
        )
        
        # Only proceed if AI planned IDOR
        if not any(a["type"] == "IDOR" for a in attack_plan["attacks"]):
            print("[AI] No IDOR attacks planned. Exiting.")
            # We continue to allow other tests to run

        print(f"[+] {len(idor_targets)} endpoints ready for IDOR testing")

        if not idor_targets:
            print("[-] No ID-based endpoints discovered")
            return findings

        proxies = {
            "http": self.zap_proxy,
            "https": self.zap_proxy,
        }

        # -----------------------------
        # Run IDOR Attacks
        # -----------------------------
        if any(a["type"] == "IDOR" for a in attack_plan["attacks"]):
            print("\n[+] Running IDOR tests")
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
            print("\n[+] Running authentication checks")

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
            print("\n[+] Running XSS tests")

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
            print("\n[+] Running DOM-XSS analysis")

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
            print("\n[+] Scoring vulnerability severity")
            scorer = SeverityScorer()

            for f in findings:
                scorer.score(f)

        # -----------------------------
        # Reporting
        # -----------------------------
        print("\n========== SCAN RESULTS ==========")

        if findings:
            for i, f in enumerate(findings, 1):
                print(f"\n[{i}] {f['vulnerability']} ({f['severity']})")
                print("    Endpoint :", f.get("endpoint"))
                print("    Impact   :", f.get("impact"))

            print("\n[+] Generating report")
            report = ReportGenerator(
                target=self.target_url,
                findings=findings,
                attack_surface=attack_surface,
                attack_plan=attack_plan
            )
            path = report.save()
            print(f"[+] Report saved at: {path}")
        else:
            print("[+] No IDOR vulnerabilities found")
            
            # Always generate report
            print("\n[+] Generating report")
            report = ReportGenerator(
                target=self.target_url,
                findings=[],
                attack_surface=attack_surface,
                attack_plan=attack_plan
            )
            path = report.save()
            print(f"[+] Report saved at: {path}")

        print("\n[+] Orchestrator finished\n")
        return findings
