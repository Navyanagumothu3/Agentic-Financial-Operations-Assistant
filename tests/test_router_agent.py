import unittest

from agents.router_agent import RouterAgent


class RouterAgentTests(unittest.TestCase):
    def setUp(self):
        self.agent = RouterAgent()

    def test_routes_refund_to_payment(self):
        state = {"request_type": "refund", "amount": 7500, "description": "duplicate charge"}
        result = self.agent(state)
        self.assertEqual(result["route"], "payment")
        self.assertEqual(result["router_decision"], "payment")

    def test_routes_fraud_requests_to_fraud(self):
        state = {"request_type": "fraud", "amount": 120000, "description": "suspicious activity"}
        result = self.agent(state)
        self.assertEqual(result["route"], "fraud")
        self.assertEqual(result["router_decision"], "fraud")

    def test_routes_generic_requests_to_support(self):
        state = {"request_type": "support", "amount": 100, "description": "balance inquiry"}
        result = self.agent(state)
        self.assertEqual(result["route"], "support")
        self.assertEqual(result["router_decision"], "support")


if __name__ == "__main__":
    unittest.main()
