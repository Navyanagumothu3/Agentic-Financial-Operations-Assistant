from typing import Any, Dict


class RouterAgent:
    """Route a banking request to the appropriate specialist agent."""

    def __init__(self) -> None:
        self._route_map = {
            "refund": "payment",
            "payment": "payment",
            "dispute": "payment",
            "fraud": "fraud",
            "suspicious": "fraud",
            "support": "support",
            "inquiry": "support",
            "complaint": "support",
        }

    def _normalize_request_type(self, request_type: str | None) -> str:
        if not request_type:
            return "support"
        return str(request_type).strip().lower()

    def _infer_route(self, state: Dict[str, Any]) -> str:
        request_type = self._normalize_request_type(state.get("request_type"))
        description = str(state.get("description", "")).strip().lower()
        amount = float(state.get("amount", 0) or 0)

        if request_type in {"refund", "payment", "dispute"}:
            return "payment"

        if request_type in {"fraud", "suspicious"} or "fraud" in description or amount >= 100000:
            return "fraud"

        if request_type in {"support", "inquiry", "complaint"}:
            return "support"

        if any(keyword in description for keyword in ["refund", "charge", "payment", "dispute"]):
            return "payment"

        return "support"

    def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        route = self._infer_route(state)
        state["route"] = route
        state["router_decision"] = route
        state["reason"] = f"Routed request to {route} specialist."
        return state


router_agent = RouterAgent()
