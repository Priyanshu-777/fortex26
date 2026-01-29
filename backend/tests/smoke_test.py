import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.orchestrator import Orchestrator

class TestOrchestrator(unittest.TestCase):
    @patch("core.orchestrator.ZAPClient")
    @patch("core.orchestrator.AIAttackPlanner")
    @patch("core.orchestrator.os.getenv")
    @patch("core.orchestrator.SeverityScorer")
    @patch("core.orchestrator.ReportGenerator")
    def test_orchestrator_flow(self, mock_report, mock_scorer, mock_getenv, mock_planner, mock_zap_client):
        # Setup Mocks
        mock_getenv.side_effect = lambda k: {
            "ZAP_PROXY": "http://127.0.0.1:8080",
            "ZAP_API_KEY": "test_key",
            "TARGET_URL": "http://example.com"
        }.get(k)

        # Mock ZAP behavior
        mock_zap_instance = mock_zap_client.return_value
        mock_zap_instance.extract_attack_surface.return_value = [
            {"path": "/page.html", "parameters": [], "url": "http://example.com/page.html"},
            {"path": "/api/user", "parameters": ["id"], "url": "http://example.com/api/user?id=1"}
        ]

        # Mock Planner behavior
        mock_planner_instance = mock_planner.return_value
        mock_planner_instance.plan.return_value = {
            "attacks": [
                {"type": "IDOR", "endpoint": "/api/user", "parameters": ["id"]},
                {"type": "XSS", "endpoint": "/api/user"},
                {"type": "DOM-XSS", "endpoint": "/page.html"}
            ],
            "reasoning": ["Testing logic"]
        }
        
        # Mock Attacks (We need to patch specific imports in orchestrator)
        with patch("core.orchestrator.IDORTester") as MockIDOR, \
             patch("core.orchestrator.XSSTester") as MockXSS, \
             patch("core.orchestrator.DOMXSSTester") as MockDOM:
            
            MockIDOR.return_value.run.return_value = [{"vulnerability": "IDOR", "severity": "High"}]
            MockXSS.return_value.run.return_value = []
            MockDOM.return_value.run.return_value = []

            # Initialize and Run
            orchestrator = Orchestrator()
            findings = orchestrator.run()

            # Assertions
            mock_zap_instance.spider.assert_called_once()
            mock_planner_instance.plan.assert_called_once()
            MockIDOR.return_value.run.assert_called_once()
            
            # Verify findings were aggregated
            self.assertEqual(len(findings), 1)
            self.assertEqual(findings[0]["vulnerability"], "IDOR")
            
            print("\n[+] Smoke test passed: Orchestrator logic flow verified.")

if __name__ == "__main__":
    unittest.main()
