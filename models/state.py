from typing import Any, Dict, List, Optional, TypedDict


class OperationState(TypedDict, total=False):
    case_id: str
    customer_id: str
    account_id: str
    request_type: str
    amount: float
    description: str
    channel: str
    route: str
    router_decision: str
    customer_tier: str
    customer_name: str
    ticket_count: int
    dispute_count: int
    risk_flags: List[str]
    risk_score: int
    support_summary: str
    payment_summary: str
    fraud_summary: str
    internal_ops_summary: str
    decision: str
    action: str
    approval_required: bool
    approval_status: str
    reason: str
    explanation: str
    self_check_result: str
    self_check_passed: bool
    audit_log: List[Dict[str, Any]]
    approved: Optional[bool]
    reviewer: Optional[str]
    prompt_context: Dict[str, Any]
    agent_trace: List[Dict[str, str]]
    estimated_cost_usd: float
