from typing import Any, Dict

from services.payment_service import PaymentService
from services.prompt_service import PromptService
from utils.llm import llm_service


def _trace(state: Dict[str, Any], agent: str, summary: str) -> None:
    trace = state.get("agent_trace", [])
    trace.append({"agent": agent, "summary": summary[:200]})
    state["agent_trace"] = trace


class PaymentAgent:
    def __init__(self):
        self.payment_service = PaymentService()
        self.prompt_service = PromptService()

    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        account_id = state.get("account_id", "unknown")
        payment_context = self.payment_service.get_payment_context(account_id)
        state["dispute_count"] = payment_context.get("dispute_count", 0)

        prompt_context = {
            "case_id": state.get("case_id", ""),
            "customer_id": state.get("customer_id", "unknown"),
            "account_id": account_id,
            "request_type": state.get("request_type", "support"),
            "amount": state.get("amount", 0),
            "description": state.get("description", ""),
            "dispute_count": state["dispute_count"],
            "failed_count": payment_context.get("failed_count", 0),
            "duplicate_charges": payment_context.get("duplicate_charges", 0),
        }
        state["prompt_context"] = {**state.get("prompt_context", {}), **prompt_context}
        prompt = self.prompt_service.load_prompt("payment")
        state["payment_summary"] = llm_service.summarize("payment", prompt, prompt_context, case_id=state.get("case_id", ""))
        state["reason"] = "Reviewed payment history and dispute indicators from payments platform."
        _trace(state, "Payment Agent", state["payment_summary"])
        return state


payment_agent = PaymentAgent()
