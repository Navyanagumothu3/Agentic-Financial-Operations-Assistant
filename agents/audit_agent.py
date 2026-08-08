from typing import Any, Dict
from datetime import datetime, timezone

from services.audit_service import AuditService


def _trace(state: Dict[str, Any], agent: str, summary: str) -> None:
    trace = state.get("agent_trace", [])
    trace.append({"agent": agent, "summary": summary[:200]})
    state["agent_trace"] = trace


class AuditAgent:
    def __init__(self):
        self.audit_service = AuditService()

    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        timestamp = datetime.now(timezone.utc).isoformat()
        entry = {
            "timestamp": timestamp,
            "case_id": state.get("case_id", ""),
            "customer_id": state.get("customer_id", ""),
            "decision": state.get("decision", ""),
            "action": state.get("action", ""),
            "approval_status": state.get("approval_status", ""),
            "self_check": state.get("self_check_result", ""),
            "reason": state.get("reason", ""),
            "message": (
                f"[{timestamp}] Case {state.get('case_id')} | customer={state.get('customer_id')} | "
                f"decision={state.get('decision')} | action={state.get('action')} | "
                f"approval={state.get('approval_status')} | self_check={'PASS' if state.get('self_check_passed') else 'FAIL'} | "
                f"reason={state.get('reason')}"
            ),
        }
        self.audit_service.record([entry])
        state["audit_log"] = [entry]
        _trace(state, "Audit Agent", "Logged to immutable audit trail")
        return state


audit_agent = AuditAgent()
