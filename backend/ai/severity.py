class SeverityScorer:
    def __init__(self):
        self.scores = {
            "IDOR": 8,
            "Broken Access Control": 8,
            "Reflected XSS": 7,
            "DOM XSS": 6,
            "Potential DOM XSS": 5,
            "Missing Authentication": 9,
        }

    def score(self, finding):
        vuln_type = finding.get("vulnerability", "Unknown")
        base_score = self.scores.get(vuln_type, 5)
        
        impact = finding.get("impact", "").lower()
        if "admin" in impact or "root" in impact:
            base_score += 1
        
        final_score = min(base_score, 10)
        
        finding["severity_score"] = final_score
        
        if final_score >= 9:
            finding["severity"] = "Critical"
        elif final_score >= 7:
            finding["severity"] = "High"
        elif final_score >= 4:
            finding["severity"] = "Medium"
        else:
            finding["severity"] = "Low"
            
        return finding
