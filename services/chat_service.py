"""Conversational orchestrator — parses natural language into structured ops requests."""

import re
from typing import Any, Dict, List, Optional

from graph.workflow import run_workflow
from services.customer_service import CustomerService
from utils.data_loader import load_json


class ChatService:
    GREETING = (
        "Hello! I'm **FinOps Assistant**, your agentic financial operations copilot. "
        "I can help with customer support, payment disputes, fraud investigations, and internal ops.\n\n"
        "Try: *\"Process refund of ₹7500 for customer C1001 — duplicate UPI charge\"* "
        "or *\"Investigate suspicious activity on account A4001\"*"
    )

    DEMO_SCENARIOS = [
        {"label": "Duplicate UPI refund (HITL)", "message": "Customer C1001 was charged twice ₹7500 for electricity. Process refund on account A2001."},
        {"label": "Small auto-refund", "message": "Refund ₹500 to customer C1004 on account A5001 for failed transaction."},
        {"label": "Fraud investigation", "message": "Investigate suspicious IMPS of ₹125000 on account A4001 for customer C1003."},
        {"label": "Support inquiry", "message": "Customer C1002 wants status update on failed NEFT transfer on account A3001."},
    ]

    def __init__(self):
        self.customer_service = CustomerService()
        self._sessions: Dict[str, List[Dict[str, str]]] = {}

    def get_session(self, session_id: str) -> List[Dict[str, str]]:
        return self._sessions.setdefault(session_id, [])

    def chat(self, message: str, session_id: str = "default", customer_id: Optional[str] = None) -> Dict[str, Any]:
        history = self.get_session(session_id)
        history.append({"role": "user", "content": message})

        if self._is_greeting(message):
            reply = self.GREETING
            history.append({"role": "assistant", "content": reply})
            return {"reply": reply, "session_id": session_id, "type": "greeting"}

        parsed = self._parse_intent(message)
        if not parsed.get("customer_id") and customer_id:
            parsed["customer_id"] = customer_id
            if not parsed.get("account_id") or parsed.get("account_id") == "A2001":
                ctx = self.customer_service.get_customer_context(customer_id)
                accounts = ctx.get("account_ids") if isinstance(ctx.get("account_ids"), list) else None
                if accounts:
                    parsed["account_id"] = accounts[0]

        if not parsed.get("customer_id"):
            reply = (
                "I need a customer ID to proceed (e.g., C1001). "
                f"Available customers: {', '.join(c['customer_id'] for c in load_json('customers'))}."
            )
            history.append({"role": "assistant", "content": reply})
            return {"reply": reply, "session_id": session_id, "type": "clarification"}

        result = run_workflow(parsed)
        reply = self._format_response(result)
        history.append({"role": "assistant", "content": reply})

        return {
            "reply": reply,
            "session_id": session_id,
            "type": "operation",
            "case_id": result.get("case_id"),
            "decision": result.get("decision"),
            "action": result.get("action"),
            "approval_required": result.get("approval_required"),
            "approval_status": result.get("approval_status"),
            "explanation": result.get("explanation"),
            "reason": result.get("reason"),
            "agent_trace": result.get("agent_trace", []),
            "self_check_passed": result.get("self_check_passed"),
            "estimated_cost_usd": result.get("estimated_cost_usd"),
            "workflow_result": result,
        }

    def _is_greeting(self, message: str) -> bool:
        lower = message.strip().lower()
        return lower in ("hi", "hello", "hey", "help", "start") or lower.startswith("what can you")

    def _parse_intent(self, message: str) -> Dict[str, Any]:
        lower = message.lower()

        customer_match = re.search(r"\b(C\d{4})\b", message, re.I)
        account_match = re.search(r"\b(A\d{4})\b", message, re.I)
        amount = 0.0
        amount_patterns = [
            r"₹\s*([\d,]+(?:\.\d+)?)",
            r"(?:rs\.?|inr|amount|refund|charge[d]?|transfer|withdraw)\s*(?:of\s*)?₹?\s*([\d,]+(?:\.\d+)?)",
            r"\b([\d,]{4,}(?:\.\d+)?)\b",  # 4+ digit standalone amounts
        ]
        for pattern in amount_patterns:
            amount_match = re.search(pattern, message, re.I)
            if amount_match:
                amount = float(amount_match.group(1).replace(",", ""))
                break

        customer_id = customer_match.group(1).upper() if customer_match else None
        account_id = account_match.group(1).upper() if account_match else None

        if customer_id and not account_id:
            ctx = self.customer_service.get_customer_context(customer_id)
            accounts = ctx.get("account_ids") if isinstance(ctx.get("account_ids"), list) else None
            if accounts:
                account_id = accounts[0]

        if any(w in lower for w in ("fraud", "suspicious", "unauthorized", "hack")):
            request_type = "fraud"
        elif any(w in lower for w in ("refund", "duplicate", "chargeback", "dispute")):
            request_type = "refund"
        elif any(w in lower for w in ("neft", "payment", "transfer", "failed")):
            request_type = "dispute"
        else:
            request_type = "support"

        channel = "chat"
        if "call" in lower:
            channel = "call"
        elif "email" in lower:
            channel = "email"

        return {
            "customer_id": customer_id or "",
            "account_id": account_id or "A2001",
            "request_type": request_type,
            "amount": amount,
            "description": message.strip(),
            "channel": channel,
        }

    def _format_response(self, result: Dict[str, Any]) -> str:
        lines = [
            f"**Case {result.get('case_id')}** — Decision: **{result.get('decision', 'pending').upper()}**",
            "",
            f"**Recommended action:** {result.get('action', 'review')}",
            f"**Reason:** {result.get('reason', 'N/A')}",
            "",
        ]

        if result.get("explanation"):
            lines.append(f"**Explanation:** {result['explanation']}")
            lines.append("")

        status = result.get("approval_status", "unknown")
        if result.get("approval_required"):
            lines.append(f"⚠️ **Human approval required** (status: {status}). An ops manager must approve before execution.")
        else:
            lines.append("✅ Auto-approved — no human intervention needed.")

        lines.append("")
        lines.append(f"**Self-check:** {'PASSED' if result.get('self_check_passed') else 'FAILED — escalated'}")
        lines.append(f"**Est. cost:** ${result.get('estimated_cost_usd', 0):.6f} USD")

        trace = result.get("agent_trace", [])
        if trace:
            lines.append("")
            lines.append("**Agent pipeline:**")
            for step in trace:
                lines.append(f"  • {step['agent']}: {step['summary'][:120]}")

        return "\n".join(lines)


chat_service = ChatService()
