from typing import Any, Dict

from services.audit_service import InternalOpsService
from utils.llm import llm_service


def _trace(state: Dict[str, Any], agent: str, summary: str) -> None:
    trace = state.get("agent_trace", [])
    trace.append({"agent": agent, "summary": summary[:200]})
    state["agent_trace"] = trace


class InternalOpsAgent:
    """Handles internal workflow context — limit changes, holds, escalations."""

    def __init__(self):
        self.ops_service = InternalOpsService()

    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        pending = self.ops_service.get_pending_approvals()
        prompt_context = {
            "case_id": state.get("case_id", ""),
            "pending_workflows": len(pending),
            "workflow_types": [w.get("type") for w in pending[:3]],
        }
        if pending:
            summary = f"Internal ops: {len(pending)} pending approval workflow(s) — {', '.join(w.get('title', '') for w in pending[:2])}."
        else:
            summary = "Internal ops: no pending workflow bottlenecks."
        state["internal_ops_summary"] = summary
        llm_service.summarize("internal_ops", summary, prompt_context, case_id=state.get("case_id", ""))
        _trace(state, "Internal Ops Agent", summary)
        return state


internal_ops_agent = InternalOpsAgent()
