from typing import Any, Dict


def _trace(state: Dict[str, Any], agent: str, summary: str) -> None:
    trace = state.get("agent_trace", [])
    trace.append({"agent": agent, "summary": summary[:200]})
    state["agent_trace"] = trace


class ApprovalAgent:
    """Human-in-the-loop gate for high-risk / irreversible actions."""

    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        approval_required = bool(state.get("approval_required", False))
        if approval_required:
            state["approval_status"] = "pending"
            state["approved"] = None
            state["reviewer"] = None
            state["reason"] = (
                f"High-risk action '{state.get('action')}' requires human approval before execution. "
                f"Assigned to ops manager queue."
            )
            _trace(state, "Approval Agent", "Queued for human approval (HITL)")
        else:
            state["approval_status"] = "auto_approved"
            state["approved"] = True
            state["reviewer"] = "system"
            state["reason"] = "Routine action auto-approved — no HITL required."
            _trace(state, "Approval Agent", "Auto-approved (low risk)")
        return state


approval_agent = ApprovalAgent()
