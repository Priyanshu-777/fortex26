from datetime import datetime
import json
import os

class ReportGenerator:
    def __init__(self, target, findings, attack_surface=None, attack_plan=None):
        self.target = target
        self.findings = findings
        self.attack_surface = attack_surface or []
        self.attack_plan = attack_plan or {}
        self.timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")

    def executive_summary(self):
        if not self.findings:
            return f"Security Scan Report for {self.target}\n\nScan Time: {self.timestamp}\n\nNo critical security issues were discovered.\n"
        return f"Security Scan Report for {self.target}\n\nScan Time: {self.timestamp}\n\nTotal Vulnerabilities Found: {len(self.findings)}\nRisk Level: HIGH\n\nImmediate remediation is strongly recommended.\n"

    def vulnerability_details(self):
        content = ""
        for idx, f in enumerate(self.findings, 1):
            content += f"### {idx}. {f.get('vulnerability')} — {f.get('severity')}\n\n"
            content += f"**Severity Score:** {f.get('severity_score')}/9\n\n"
            content += f"**Endpoint:** {f.get('endpoint')}\n\n"
            content += f"**Affected Parameter:** `{f.get('parameter')}`\n\n"
            content += f"**Impact:** {f.get('impact')}\n\n"
            content += "---\n\n"
        return content

    def scan_scope(self):
        content = f"## 🔍 Scan Scope\n\n**Total Unique Endpoints Discovered:** {len(self.attack_surface)}\n\n"
        if self.attack_surface:
            content += "| Method | URL |\n|---|---|\n"
            # Limit to top 20 to avoid huge reports
            for item in self.attack_surface[:20]:
                content += f"| {item.get('method')} | `{item.get('url')}` |\n"
            
            if len(self.attack_surface) > 20:
                content += f"\n*(...and {len(self.attack_surface) - 20} more)*\n"
        else:
            content += "_No endpoints were discovered during the crawl phase._\n"
        return content + "\n"

    def methodology(self):
        content = "## 🧪 Methodology\n\n"
        
        # Tools Used
        content += "### Tools & Techniques\n"
        content += "- **ZAP Spider**: Standard crawling for static links.\n"
        content += "- **ZAP AJAX Spider**: Dynamic crawling for SPA/JS-heavy content.\n"
        content += "- **AI Planner**: Context-aware attack strategy.\n\n"

        # AI Plan
        if self.attack_plan:
            content += "### Planned Attacks (AI Driven)\n"
            content += "Based on the attack surface, the AI agent planned the following tests:\n\n"
            if "reasoning" in self.attack_plan:
                for reason in self.attack_plan["reasoning"]:
                    content += f"- {reason}\n"
        
        return content + "\n---\n\n"

    def generate_markdown(self):
        report = "# 🛡️ Security Assessment Report\n\n"
        report += self.executive_summary()
        report += "\n---\n\n"
        
        # New Sections
        report += self.methodology()
        report += self.scan_scope()
        report += "\n---\n\n"
        
        report += "## Vulnerability Details\n\n"
        if self.findings:
            report += self.vulnerability_details()
        else:
            report += "_No vulnerabilities were identified during this scan._\n"
            
        return report

    def save(self, output_dir="reports"):
        os.makedirs(output_dir, exist_ok=True)
        filename = f"security_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.md"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(self.generate_markdown())
        return filepath
