from typing import Any, Dict, List

from services.customer_service import CustomerService
from services.prompt_service import PromptService
from utils.llm import llm_service


def _trace(state: Dict[str, Any], agent: str, summary: str) -> None:
    trace = state.get("agent_trace", [])
    trace.append({"agent": agent, "summary": summary[:200]})
    state["agent_trace"] = trace


class SupportAgent:
    def __init__(self):
        self.customer_service = CustomerService()
        self.prompt_service = PromptService()

    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        customer_id = state.get("customer_id", "unknown")
        customer_context = self.customer_service.get_customer_context(customer_id)
        state["customer_tier"] = customer_context.get("tier", "standard")
        state["customer_name"] = customer_context.get("name", "Unknown")
        state["ticket_count"] = customer_context.get("recent_tickets", 0)

        prompt_context = {
            "case_id": state.get("case_id", ""),
            "customer_id": customer_id,
            "customer_name": state["customer_name"],
            "account_id": state.get("account_id", "unknown"),
            "request_type": state.get("request_type", "support"),
            "amount": state.get("amount", 0),
            "description": state.get("description", ""),
            "channel": state.get("channel", "chat"),
            "customer_tier": state["customer_tier"],
            "ticket_count": state["ticket_count"],
            "open_tickets": customer_context.get("open_tickets", 0),
        }
        state["prompt_context"] = prompt_context
        prompt = self.prompt_service.load_prompt("support")
        state["support_summary"] = llm_service.summarize("support", prompt, prompt_context, case_id=state.get("case_id", ""))
        state["reason"] = "Collected support context and customer profile from CRM."
        _trace(state, "Support Agent", state["support_summary"])
        return state


support_agent = SupportAgent()
