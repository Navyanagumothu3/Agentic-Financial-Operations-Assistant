from __future__ import annotations

from typing import Any, Dict
from uuid import uuid4

from langgraph.graph import END, START, StateGraph

from agents.approval_agent import approval_agent
from agents.audit_agent import audit_agent
from agents.decision_agent import decision_agent
from agents.fraud_agent import fraud_agent
from agents.internal_ops_agent import internal_ops_agent
from agents.payment_agent import payment_agent
from agents.router_agent import router_agent
from agents.self_check_agent import self_check_agent
from agents.support_agent import support_agent
from models.state import OperationState
from utils.cost_tracker import cost_tracker


def build_workflow():
    workflow = StateGraph(OperationState)

    workflow.add_node("router", router_agent)
    workflow.add_node("support", support_agent)
    workflow.add_node("payment", payment_agent)
    workflow.add_node("fraud", fraud_agent)
    workflow.add_node("internal_ops", internal_ops_agent)
    workflow.add_node("decision", decision_agent)
    workflow.add_node("self_check", self_check_agent)
    workflow.add_node("approval", approval_agent)
    workflow.add_node("audit", audit_agent)

    workflow.add_edge(START, "router")
    workflow.add_edge("router", "support")
    workflow.add_edge("support", "payment")
    workflow.add_edge("payment", "fraud")
    workflow.add_edge("fraud", "internal_ops")
    workflow.add_edge("internal_ops", "decision")
    workflow.add_edge("decision", "self_check")
    workflow.add_edge("self_check", "approval")
    workflow.add_edge("approval", "audit")
    workflow.add_edge("audit", END)

    return workflow.compile()


def run_workflow(state: Dict[str, Any]) -> Dict[str, Any]:
    workflow = build_workflow()
    if not state.get("case_id"):
        state["case_id"] = uuid4().hex[:8].upper()
    state.setdefault("agent_trace", [])
    result = workflow.invoke(state)
    summary = cost_tracker.summary()
    result["estimated_cost_usd"] = summary.get("avg_cost_per_decision_usd", 0)
    result["cost_summary"] = summary
    return result
