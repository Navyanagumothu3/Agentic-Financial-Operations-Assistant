from typing import Any, Dict

from services.fraud_service import FraudService
from services.prompt_service import PromptService
from utils.llm import llm_service


def _trace(state: Dict[str, Any], agent: str, summary: str) -> None:
    trace = state.get("agent_trace", [])
    trace.append({"agent": agent, "summary": summary[:200]})
    state["agent_trace"] = trace


class FraudAgent:
    def __init__(self):
        self.fraud_service = FraudService()
        self.prompt_service = PromptService()

    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        customer_id = state.get("customer_id", "unknown")
        fraud_context = self.fraud_service.get_fraud_context(customer_id)
        state["risk_flags"] = fraud_context.get("risk_flags", [])
        state["risk_score"] = fraud_context.get("risk_score", 0)

        prompt_context = {
            "case_id": state.get("case_id", ""),
            "customer_id": customer_id,
            "account_id": state.get("account_id", "unknown"),
            "request_type": state.get("request_type", "support"),
            "amount": state.get("amount", 0),
            "description": state.get("description", ""),
            "risk_flags": state["risk_flags"],
            "risk_score": state["risk_score"],
            "active_cases": fraud_context.get("active_cases", 0),
        }
        state["prompt_context"] = {**state.get("prompt_context", {}), **prompt_context}
        prompt = self.prompt_service.load_prompt("fraud")
        tier = "reasoning_llm" if state["risk_score"] >= 70 else "fast_llm"
        state["fraud_summary"] = llm_service.summarize(
            "fraud", prompt, prompt_context, tier=tier, case_id=state.get("case_id", "")
        )
        state["reason"] = "Checked fraud history and behavioral risk signals from case management."
        _trace(state, "Fraud Agent", state["fraud_summary"])
        return state


fraud_agent = FraudAgent()
