import unittest

from fastapi.testclient import TestClient

from api.routes import app


class AgentRouteTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_transfer_runs_agent_workflow(self):
        response = self.client.post(
            "/transfer",
            json={
                "customer_id": "C1001",
                "from_account": "A2001",
                "to_account": "A2002",
                "amount": 1500,
                "description": "Transfer to savings",
            },
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("decision", payload)
        self.assertIn("agent_trace", payload)
        self.assertIn("approval_status", payload)
        self.assertEqual(payload["customer_id"], "C1001")

    def test_withdraw_runs_agent_workflow(self):
        response = self.client.post(
            "/withdraw",
            json={"account_id": "A2001", "amount": 2500},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("decision", payload)
        self.assertIn("agent_trace", payload)
        self.assertEqual(payload["amount"], 2500.0)

    def test_chat_uses_agent_pipeline(self):
        response = self.client.post(
            "/chat",
            json={"message": "Customer C1001 needs a refund of ₹7500 for duplicate charge", "session_id": "tests"},
        )

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("agent_trace", payload)
        self.assertTrue(payload["agent_trace"])
        self.assertIn("Support Agent", payload["agent_trace"][0]["agent"])
        self.assertIn("**Case", payload["reply"])


if __name__ == "__main__":
    unittest.main()
