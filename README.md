# 🏦 Agentic Financial Operations Assistant

> An AI-powered banking operations platform that uses **LangGraph Multi-Agent AI**, **FastAPI**, **Spring Boot**, and **React** to automate financial operations while keeping humans in the loop for high-risk actions.

---

## 📌 Overview

Financial operations teams handle customer support, payments, refunds, disputes, fraud investigations, and internal operational requests across multiple systems.

The **Agentic Financial Operations Assistant** automates this workflow using specialized AI agents. The system understands customer requests, determines required agents, calculates risk scores, executes explainable decisions, enforces safety self-checks, routes high-risk actions for human approval, and records immutable audit trails.

---

## 🎯 Key Features

- **Multi-Agent AI Architecture:** Specialized agents for Routing, Support, Payments, Fraud, Internal Ops, Decision-Making, Self-Checking, Approvals, and Auditing.
- **Intelligent Request Routing:** Router agent executes only necessary downstream agents to minimize latency and LLM costs.
- **Deterministic Risk Scoring:** Calculates aggregate risk scores (0–100) using weighted security flags to enforce exact business logic thresholds.
- **Human-in-the-Loop (HITL) Safeguards:** Automatically pauses high-risk transactions and queues them for manager sign-off before execution.
- **Explainable Decisions & Self-Check:** Validates all decisions against safety policies before execution, attaching clear reasoning traces to every action.
- **Immutable Audit Trail:** Comprehensive execution traces stored for full compliance and auditability.

---

## 🏗 System Architecture

```text
React Frontend (Port 5173)
       │
       │ REST API
       ▼
Spring Boot Backend (Port 8080)
       │
       │ HTTP
       ▼
FastAPI AI Layer (Port 8000)
       │
       ▼
 [ Router Agent ]
       │
       ├───────────────────────┬───────────────────────┐
       ▼                       ▼                       ▼
[Support Agent]         [Payment Agent]         [Fraud Agent]
       │                       │                       │
       └───────────────────────┼───────────────────────┘
                                ▼
                     [Internal Ops Agent]
                                │
                                ▼
                         [Decision Agent]
                                │
                                ▼
                        [Self-Check Agent]
                                │
                                ▼
                         [Approval Agent]
                                │
                                ▼
                          [Audit Agent]
```

---

## 📊 Risk Scoring & Handling Protocol

The deterministic risk engine calculates an aggregate score based on contextual security flags:

### Risk Flag Weights

| Flag | Weight |
|---|---|
| Velocity Spike Detected | +30 |
| Unusual / High-Value Beneficiary | +25 |
| New / Untrusted Device | +20 |
| High Transaction Amount Threshold | +20 |
| Failed Login / Security Attempts | +15 |
| Multiple Existing Disputes | +10 |
| Verified / Trusted Device | -15 |

### Operational Risk Tiers

| Aggregate Score | Risk Level | Operational Action & Handling Protocol |
|---|---|---|
| 0 – 20 | Low Risk | Auto-Approve: Executed instantly without manual intervention. |
| 21 – 40 | Moderate Risk | Standard Review: Passed through standard automated validation checks. |
| 41 – 60 | Medium Risk | Manager Review: Flagged and held briefly for operational manager sign-off. |
| 61 – 80 | High Risk | Mandatory HITL: Paused until a manager explicitly approves in the dashboard. |
| 81 – 100 | Critical Risk | Account Freeze: Blocked immediately and escalated to fraud investigators. |

---

## 📂 Repository Structure

```text
AI-BANKING-AGENT/
├── agents/                  # LangGraph specialized agents
│   ├── router_agent.py
│   ├── support_agent.py
│   ├── payment_agent.py
│   ├── fraud_agent.py
│   ├── internal_ops_agent.py
│   ├── decision_agent.py
│   ├── self_check_agent.py
│   ├── approval_agent.py
│   └── audit_agent.py
├── api/                     # API routes
│   └── routes.py
├── Backend/                 # Spring Boot enterprise application
├── data/                    # Data sources (JSON/DB schemas)
├── docs/                    # Documentation and specs
├── frontend/                # React dashboard frontend
├── graph/                   # LangGraph workflow compiler & state schemas
│   └── workflow.py
├── logs/                    # Local audit logs
├── models/                  # Pydantic data models
├── prompts/                 # System prompts for AI agents
├── services/                # Risk engine & business logic services
├── utils/                   # Shared LLM utility functions
│   └── llm.py
├── docker-compose.yml       # Multi-container orchestration setup
├── main.py                  # FastAPI server entrypoint
└── requirements.txt         # Python dependencies
```

---

## 🔌 REST API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Check backend and AI service health status |
| GET | `/ui` | Open the banking operations dashboard UI |
| POST | `/operate` | Submit a financial request and trigger the LangGraph workflow |
| POST | `/approve` | Approve or reject a pending Human-in-the-Loop operation |

### Sample Request (`POST /operate`)

```json
{
  "customer_id": "C1001",
  "account_id": "A2001",
  "request_type": "refund",
  "amount": 7500,
  "description": "Customer was charged twice",
  "channel": "chat"
}
```

### Sample Response

```json
{
  "case_id": "729F9701",
  "decision": "approve",
  "action": "issue refund pending manager approval",
  "approval_required": true,
  "approval_status": "pending",
  "reason": "Refund exceeds automatic approval threshold",
  "agent_trace": [
    "Support Agent",
    "Payment Agent",
    "Fraud Agent",
    "Internal Ops Agent",
    "Decision Agent",
    "Self-Check Agent",
    "Approval Agent",
    "Audit Agent"
  ]
}
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.13+
- Java 17+ & Maven
- Node.js & npm

### 1. AI Layer (FastAPI & LangGraph)

```bash
python -m venv venv
# On Windows: venv\Scripts\activate
# On macOS/Linux: source venv/bin/activate
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### 2. Backend Service (Spring Boot)

```bash
cd Backend
mvn clean install
mvn spring-boot:run
```

### 3. Frontend Dashboard (React)

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser to access the dashboard.

---

## 🛠 Tech Stack

- **Frontend:** React, JavaScript, HTML, CSS
- **Backend:** Java, Spring Boot, REST APIs, Maven
- **AI Service:** Python, FastAPI, LangGraph, LangChain
- **LLM Integration:** Ollama / Cloud Models
