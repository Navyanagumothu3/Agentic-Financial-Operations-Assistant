from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime
import random

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from graph.workflow import run_workflow
from services.audit_service import AuditService
from services.chat_service import chat_service
from services.customer_service import CustomerService
from utils.cost_tracker import cost_tracker
from utils.data_loader import filter_by_field, load_json

app = FastAPI(
    title="Agentic Financial Operations Assistant",
    description="Multi-agent banking ops copilot with HITL, audit trail, and explainability",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

audit_service = AuditService()
customer_service = CustomerService()
case_store: List[dict] = []

ACCOUNTS_STORE = {
    "A2001": {"account_id": "A2001", "customer_id": "C1001", "account_type": "Current", "balance": 125000.0, "currency": "INR"},
    "A2002": {"account_id": "A2002", "customer_id": "C1001", "account_type": "Savings", "balance": 480000.0, "currency": "INR"},
    "A3001": {"account_id": "A3001", "customer_id": "C1002", "account_type": "Current", "balance": 95000.0, "currency": "INR"},
    "A4001": {"account_id": "A4001", "customer_id": "C1003", "account_type": "Current", "balance": 310000.0, "currency": "INR"},
    "A5001": {"account_id": "A5001", "customer_id": "C1004", "account_type": "Savings", "balance": 75000.0, "currency": "INR"},
}

TRANSACTIONS_STORE: List[dict] = list(load_json("transactions"))


class OperationRequest(BaseModel):
    customer_id: str = Field(min_length=1)
    account_id: str = Field(min_length=1)
    request_type: str = Field(default="support")
    amount: float = Field(default=0.0, ge=0)
    description: str = Field(default="")
    channel: str = Field(default="chat")


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    session_id: str = Field(default="default")
    customer_id: Optional[str] = Field(default=None)


class ApprovalRequest(BaseModel):
    case_id: str = Field(min_length=1)
    approved: bool
    reviewer: str = Field(min_length=1)


class TransferRequest(BaseModel):
    customer_id: str = Field(min_length=1)
    from_account: str = Field(min_length=1)
    to_account: str = Field(min_length=1)
    amount: float = Field(gt=0)
    description: str = Field(default="")


class WithdrawRequest(BaseModel):
    account_id: str = Field(min_length=1)
    amount: float = Field(gt=0)
    customer_id: str = Field(default="C1001")


class LoginRequest(BaseModel):
    customer_id: str = Field(min_length=1)
    password: str = Field(min_length=1)


def _store_case(payload: OperationRequest, result: dict) -> dict:
    case_record = {
        "case_id": result.get("case_id"),
        "customer_id": payload.customer_id,
        "account_id": payload.account_id,
        "request_type": payload.request_type,
        "amount": payload.amount,
        "description": payload.description,
        "channel": payload.channel,
        "decision": result.get("decision"),
        "action": result.get("action"),
        "approval_required": result.get("approval_required"),
        "approval_status": result.get("approval_status"),
        "reason": result.get("reason"),
        "explanation": result.get("explanation"),
        "self_check_passed": result.get("self_check_passed"),
        "agent_trace": result.get("agent_trace", []),
        "estimated_cost_usd": result.get("estimated_cost_usd"),
    }
    case_store.append(case_record)
    return case_record


@app.get("/")
def health():
    return {
        "status": "ok",
        "service": "Agentic Financial Operations Assistant",
        "agents": ["router", "support", "payment", "fraud", "internal_ops", "decision", "self_check", "approval", "audit"],
        "guardrails": ["human_in_the_loop", "auditability", "explainability", "data_privacy"],
    }


@app.get("/ui", response_class=HTMLResponse)
def ui_page():
    html_path = Path(__file__).resolve().parent.parent / "static" / "index.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))


@app.post("/login")
def login(payload: LoginRequest):
    cid = payload.customer_id.upper().strip()
    pwd = payload.password.strip()
    if cid in ("M1001", "MANAGER", "ADMIN") and pwd in ("admin123", "manager123", "bank123"):
        return {
            "authenticated": True,
            "role": "manager",
            "user": {
                "id": "M1001",
                "name": "Ops Compliance Manager",
                "role": "manager",
                "email": "ops.manager@bank.com",
                "region": "Headquarters"
            }
        }
    customer = customer_service.get_customer_context(payload.customer_id)
    if customer.get("name") == "Unknown Customer" or payload.password != "bank123":
        raise HTTPException(status_code=401, detail="Invalid customer credentials")
    return {"authenticated": True, "role": "customer", "customer": customer}


@app.get("/customers")
def customers():
    return customer_service.list_customers()


@app.get("/customers/{customer_id}")
def get_customer(customer_id: str):
    ctx = customer_service.get_customer_context(customer_id)
    if ctx.get("name") == "Unknown Customer":
        raise HTTPException(status_code=404, detail="Customer not found")
    return ctx


@app.get("/customers/{customer_id}/accounts")
def customer_accounts(customer_id: str):
    ctx = customer_service.get_customer_context(customer_id)
    account_ids = ctx.get("account_ids", [])
    result = []
    for aid in account_ids:
        if aid in ACCOUNTS_STORE:
            result.append(ACCOUNTS_STORE[aid])
        else:
            result.append({
                "account_id": aid,
                "customer_id": customer_id,
                "account_type": "Current",
                "balance": 100000.0,
                "currency": "INR",
            })
    return result


@app.get("/accounts/{account_id}")
def get_account(account_id: str):
    if account_id in ACCOUNTS_STORE:
        return ACCOUNTS_STORE[account_id]
    return {
        "account_id": account_id,
        "account_type": "Current" if account_id.startswith("A2") else "Savings",
        "balance": 125000.0 if account_id.endswith("1") else 50000.0,
        "currency": "INR",
        "status": "active",
    }


@app.get("/customers/{customer_id}/transactions")
def customer_transactions(customer_id: str):
    txns = [t for t in TRANSACTIONS_STORE if t.get("customer_id") == customer_id]
    return sorted(txns, key=lambda x: x.get("timestamp", ""), reverse=True)


@app.post("/operate")
def operate(payload: OperationRequest):
    result = run_workflow(payload.model_dump())
    case_record = _store_case(payload, result)
    return result | {"case_record": case_record}


@app.post("/chat")
def chat(payload: ChatRequest):
    response = chat_service.chat(payload.message, payload.session_id, payload.customer_id)
    if response.get("type") == "operation" and response.get("workflow_result"):
        wf = response["workflow_result"]
        case_record = {
            "case_id": wf.get("case_id"),
            "customer_id": wf.get("customer_id"),
            "account_id": wf.get("account_id"),
            "request_type": wf.get("request_type"),
            "amount": wf.get("amount"),
            "description": wf.get("description"),
            "channel": wf.get("channel"),
            "decision": wf.get("decision"),
            "action": wf.get("action"),
            "approval_required": wf.get("approval_required"),
            "approval_status": wf.get("approval_status"),
            "reason": wf.get("reason"),
            "explanation": wf.get("explanation"),
            "self_check_passed": wf.get("self_check_passed"),
            "agent_trace": wf.get("agent_trace", []),
            "estimated_cost_usd": wf.get("estimated_cost_usd"),
        }
        case_store.append(case_record)
        response["case_record"] = case_record
    return response


@app.get("/chat/scenarios")
def chat_scenarios():
    return chat_service.DEMO_SCENARIOS


@app.post("/transfer")
def transfer(payload: TransferRequest):
    if payload.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    result = run_workflow({
        "customer_id": payload.customer_id,
        "account_id": payload.from_account,
        "request_type": "transfer",
        "amount": payload.amount,
        "description": payload.description or f"Transfer ₹{payload.amount} from {payload.from_account} to {payload.to_account}",
        "channel": "internal",
    })

    if payload.from_account in ACCOUNTS_STORE:
        ACCOUNTS_STORE[payload.from_account]["balance"] -= payload.amount
    if payload.to_account in ACCOUNTS_STORE:
        ACCOUNTS_STORE[payload.to_account]["balance"] += payload.amount

    txn_num = random.randint(100, 999)
    new_txn = {
        "txn_id": f"TXN-{txn_num}",
        "account_id": payload.from_account,
        "customer_id": payload.customer_id,
        "amount": payload.amount,
        "type": "TRANSFER",
        "status": "completed",
        "merchant": f"Transfer to {payload.to_account}",
        "timestamp": datetime.now().isoformat()[:19],
        "reference": f"TRF-REF-{txn_num}"
    }
    TRANSACTIONS_STORE.insert(0, new_txn)

    case_record = {
        "case_id": result.get("case_id"),
        "customer_id": payload.customer_id,
        "account_id": payload.from_account,
        "request_type": "transfer",
        "amount": payload.amount,
        "description": payload.description,
        "decision": result.get("decision"),
        "action": result.get("action"),
        "approval_required": result.get("approval_required"),
        "approval_status": result.get("approval_status"),
        "reason": result.get("reason"),
        "agent_trace": result.get("agent_trace", []),
    }
    case_store.append(case_record)

    return {
        "status": "success",
        "message": f"Transfer of ₹{payload.amount:,.2f} from {payload.from_account} to {payload.to_account} processed successfully.",
        "customer_id": payload.customer_id,
        "from_account": payload.from_account,
        "to_account": payload.to_account,
        "amount": payload.amount,
        "decision": result.get("decision"),
        "approval_required": result.get("approval_required"),
        "approval_status": result.get("approval_status"),
        "reason": result.get("reason"),
        "agent_trace": result.get("agent_trace", []),
        "case_id": result.get("case_id"),
        "case_record": case_record,
    }


@app.post("/withdraw")
def withdraw(payload: WithdrawRequest):
    if payload.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    result = run_workflow({
        "customer_id": payload.customer_id,
        "account_id": payload.account_id,
        "request_type": "withdraw",
        "amount": payload.amount,
        "description": f"Withdrawal of ₹{payload.amount} from {payload.account_id}",
        "channel": "internal",
    })

    if payload.account_id in ACCOUNTS_STORE:
        ACCOUNTS_STORE[payload.account_id]["balance"] -= payload.amount

    txn_num = random.randint(100, 999)
    new_txn = {
        "txn_id": f"TXN-{txn_num}",
        "account_id": payload.account_id,
        "customer_id": payload.customer_id,
        "amount": payload.amount,
        "type": "WITHDRAWAL",
        "status": "completed",
        "merchant": "ATM / Cash Withdrawal",
        "timestamp": datetime.now().isoformat()[:19],
        "reference": f"WTH-REF-{txn_num}"
    }
    TRANSACTIONS_STORE.insert(0, new_txn)

    case_record = {
        "case_id": result.get("case_id"),
        "customer_id": payload.customer_id,
        "account_id": payload.account_id,
        "request_type": "withdraw",
        "amount": payload.amount,
        "decision": result.get("decision"),
        "action": result.get("action"),
        "approval_required": result.get("approval_required"),
        "approval_status": result.get("approval_status"),
        "agent_trace": result.get("agent_trace", []),
    }
    case_store.append(case_record)

    return {
        "status": "success",
        "message": f"Withdrawal of ₹{payload.amount:,.2f} from account {payload.account_id} processed successfully.",
        "amount": payload.amount,
        "account_id": payload.account_id,
        "decision": result.get("decision"),
        "approval_required": result.get("approval_required"),
        "approval_status": result.get("approval_status"),
        "reason": result.get("reason"),
        "agent_trace": result.get("agent_trace", []),
        "case_id": result.get("case_id"),
        "case_record": case_record,
    }


@app.post("/approve")
def approve(payload: ApprovalRequest):
    case = next((item for item in case_store if item["case_id"] == payload.case_id), None)
    if case is None:
        raise HTTPException(status_code=404, detail="Case not found")

    case["approved"] = payload.approved
    case["reviewer"] = payload.reviewer
    case["approval_status"] = "approved" if payload.approved else "rejected"

    audit_service.record([{
        "message": (
            f"Human approval: case={payload.case_id} approved={payload.approved} "
            f"reviewer={payload.reviewer}"
        )
    }])

    return {
        "case_id": payload.case_id,
        "approved": payload.approved,
        "reviewer": payload.reviewer,
        "status": case["approval_status"],
        "case": case,
    }


@app.get("/cases", response_model=List[dict])
def list_cases():
    return list(reversed(case_store))


@app.get("/cases/pending-approval")
def pending_approvals():
    return [item for item in reversed(case_store) if item.get("approval_required") and item.get("approval_status") == "pending"]


@app.get("/analytics/{customer_id}")
def analytics(customer_id: str):
    txns = [t for t in TRANSACTIONS_STORE if t.get("customer_id") == customer_id]
    duplicate_count = sum(1 for t in txns if t.get("note") == "Possible duplicate")
    high_value = sum(1 for t in txns if float(t.get("amount", 0)) >= 50000)
    return {
        "customer_id": customer_id,
        "transaction_count": len(txns),
        "duplicate_count": duplicate_count,
        "high_value_transactions": high_value,
        "risk_summary": "High value activity detected" if high_value else "Normal activity",
    }


@app.get("/metrics")
def metrics():
    cases = case_store
    return {
        "total_cases": len(cases),
        "pending_approval": len([c for c in cases if c.get("approval_status") == "pending"]),
        "auto_approved": len([c for c in cases if c.get("approval_status") == "auto_approved" or (c.get("decision") == "approve" and not c.get("approval_required"))]),
        "escalated": len([c for c in cases if c.get("decision") == "escalate"]),
        "cost": cost_tracker.summary(),
    }


@app.get("/audit")
def audit(limit: int = 50):
    entries = []
    for item in reversed(case_store[:limit]):
        entries.append({
            "case_id": item.get("case_id"),
            "decision": item.get("decision"),
            "approval_status": item.get("approval_status"),
            "reason": item.get("reason"),
        })
    return entries
