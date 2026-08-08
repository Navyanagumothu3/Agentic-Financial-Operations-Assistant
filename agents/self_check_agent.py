from typing import Any, Dict


def _trace(state: Dict[str, Any], agent: str, summary: str) -> None:
    trace = state.get("agent_trace", [])
    trace.append({"agent": agent, "summary": summary[:200]})
    state["agent_trace"] = trace


class SelfCheckAgent:
    """Reviews the agent pipeline output against business goals before finalizing."""

    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        issues = []
        passed = True

        if state.get("approval_required") and state.get("decision") == "approve":
            if float(state.get("amount", 0)) > 1000 and state.get("approval_status") == "not_required":
                issues.append("High-value action should require approval")
                passed = False

        fraud_summary = str(state.get("fraud_summary", "")).lower()
        if ("velocity spike" in fraud_summary or state.get("risk_score", 0) >= 70) and state.get("decision") == "resolve":
            issues.append("Fraud signals present but decision is resolve — should escalate")
            passed = False

        if not state.get("reason"):
            issues.append("Missing plain-language reason for audit trail")
            passed = False

        if not state.get("explanation"):
            issues.append("Missing customer-facing explanation")
            passed = False

        if passed:
            result = "Self-check PASSED: decision aligns with guardrails (HITL, auditability, explainability)."
        else:
            result = "Self-check FAILED: " + "; ".join(issues) + ". Flagging for review."
            if state.get("decision") == "resolve":
                state["decision"] = "escalate"
                state["approval_required"] = True
                state["approval_status"] = "pending"
                state["action"] = "escalate after self-check failure"
                state["reason"] = "Self-check detected policy gap — escalating for human review."

        state["self_check_result"] = result
        state["self_check_passed"] = passed
        _trace(state, "Self-Check Agent", result)
        return state


self_check_agent = SelfCheckAgent()
