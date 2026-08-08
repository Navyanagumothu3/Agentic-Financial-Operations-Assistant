from typing import Any, Dict

from services.payment_service import PaymentService
from services.prompt_service import PromptService
from utils.llm import llm_service


def _trace(state: Dict[str, Any], agent: str, summary: str) -> None:
    trace = state.get("agent_trace", [])
    trace.append({"agent": agent, "summary": summary[:200]})
    state["agent_trace"] = trace


class DecisionAgent:
    REFUND_AUTO_LIMIT = 1000
    HIGH_VALUE_LIMIT = 50000
    FRAUD_SCORE_THRESHOLD = 70

    def __init__(self):
        self.prompt_service = PromptService()
        self.payment_service = PaymentService()

    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        amount = float(state.get("amount", 0) or 0)
        request_type = (state.get("request_type") or "support").lower()
        fraud_summary = state.get("fraud_summary", "")
        risk_score = int(state.get("risk_score", 0))
        risk_flags = state.get("risk_flags", [])

        prompt_context = {
            "case_id": state.get("case_id", ""),
            "customer_id": state.get("customer_id", "unknown"),
            "account_id": state.get("account_id", "unknown"),
            "request_type": request_type,
            "amount": amount,
            "description": state.get("description", ""),
            "support_summary": state.get("support_summary", ""),
            "payment_summary": state.get("payment_summary", ""),
            "fraud_summary": fraud_summary,
            "risk_score": risk_score,
        }

        high_risk = (
            "velocity spike" in fraud_summary.lower()
            or risk_score >= self.FRAUD_SCORE_THRESHOLD
            or amount >= self.HIGH_VALUE_LIMIT
            or "unusual beneficiary" in str(risk_flags).lower()
        )

        if high_risk:
            decision = "escalate"
            action = "place fraud hold and initiate manual review"
            approval_required = True
            reason = (
                f"High-risk indicators detected (score {risk_score}/100, amount ₹{amount:,.0f}). "
                "Per RBI guidelines, escalating for human review before any irreversible action."
            )
        elif request_type in ("refund", "dispute"):
            if amount <= self.REFUND_AUTO_LIMIT:
                decision = "approve"
                action = "issue refund automatically"
                approval_required = False
                reason = f"Refund of ₹{amount:,.0f} is within auto-approval limit (≤₹{self.REFUND_AUTO_LIMIT:,})."
            else:
                decision = "approve"
                action = "issue refund pending manager approval"
                approval_required = True
                reason = f"Refund of ₹{amount:,.0f} exceeds ₹{self.REFUND_AUTO_LIMIT:,} threshold — human approval required."
        elif request_type in ("fraud", "suspicious"):
            decision = "escalate"
            action = "freeze account and assign fraud analyst"
            approval_required = True
            reason = "Fraud-related request requires mandatory human-in-the-loop approval."
        else:
            decision = "resolve"
            action = "provide standard support response"
            approval_required = False
            reason = "Routine support case with no high-risk indicators."

        state["decision"] = decision
        state["action"] = action
        state["approval_required"] = approval_required
        state["reason"] = reason

        tier = "reasoning_llm" if approval_required or high_risk else "fast_llm"
        prompt = self.prompt_service.load_prompt("decision")
        prompt_context.update({"decision": decision, "action": action, "reason": reason, "approval_required": approval_required})
        state["explanation"] = llm_service.summarize("decision", prompt, prompt_context, tier=tier, case_id=state.get("case_id", ""))
        _trace(state, "Decision Agent", state["explanation"])
        return state


decision_agent = DecisionAgent()
