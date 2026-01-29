import json
from typing import List, Dict

class AIAttackPlanner:
    def __init__(self, llm_client=None):
        self.llm_client = llm_client

    def plan(self, attack_surface: List[Dict]) -> Dict:
        plan = {
            "attacks": [],
            "reasoning": []
        }

        for item in attack_surface:
            path = item.get("path", "")
            params = item.get("parameters", [])

            # ---- IDOR reasoning ----
            id_params = [p for p in params if p.lower() in [
                "id", "user_id", "order_id", "account_id"
            ]]

            if id_params:
                plan["attacks"].append({
                    "type": "IDOR",
                    "endpoint": path,
                    "parameters": id_params
                })
                plan["reasoning"].append(
                    f"Endpoint '{path}' contains object identifier parameters "
                    f"{id_params}, indicating potential IDOR risk."
                )

            # ---- AUTH reasoning ----
            if "api" in path.lower():
                plan["attacks"].append({
                    "type": "AUTH",
                    "endpoint": path,
                })
                plan["reasoning"].append(
                    f"Endpoint '{path}' appears to be an API endpoint and may require authentication."
                )

            # ---- XSS reasoning ----
            if params:
                plan["attacks"].append({
                    "type": "XSS",
                    "endpoint": path,
                })
                plan["reasoning"].append(
                    f"Endpoint '{path}' accepts user-controlled input and may be vulnerable to XSS."
                )

            # ---- DOM-XSS reasoning ----
            if path.endswith(".html") or "/page" in path.lower():
                plan["attacks"].append({
                    "type": "DOM-XSS",
                    "endpoint": path,
                })
                plan["reasoning"].append(
                    f"Page '{path}' may contain client-side JavaScript handling user input, "
                    "making it a candidate for DOM-based XSS."
                )

        if not plan["attacks"]:
            plan["reasoning"].append(
                "No high-risk object-level parameters detected. "
                "Skipping active exploitation."
            )

        return plan
