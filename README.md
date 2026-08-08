# Agentic Financial Operations Assistant

> **AI Build 2026** · Multi-agent banking ops copilot with Human-in-the-Loop (HITL), audit trail, data privacy, and explainability.

FinOps Assistant autonomously handles operational tasks across **customer support**, **payments**, **fraud investigations**, and **internal ops** by orchestrating 9 specialized agents — while strictly respecting RBI regulations and keeping humans in the loop for high-risk actions.

---

## 🛡️ Enterprise Guardrails Implementation

The system rigorously implements the four mandatory guardrails required for financial AI governance:

### 1. 🤝 Human-in-the-Loop (HITL)
- **Policy Thresholds**: Any high-risk or irreversible action (such as refunds exceeding ₹1,000, risk score $\ge$ 70, velocity spikes, or account holds) is automatically gated by the `ApprovalAgent`.
- **Workflow Pipeline**: When `approval_required = True`, the system sets `approval_status = "pending"` and routes the case to the **Manager HITL Hub** (`/cases/pending-approval`).
- **Role-Based Access Control (RBAC)**: Separates Customer capabilities (`C1001` / `bank123`) from Manager Governance (`M1001` / `admin123`). Only authenticated Ops Managers can review, approve, or reject pending cases via the dedicated Manager Hub.

### 2. 📜 Auditability
- **Immutable Logging**: Every single autonomous decision, auto-approval, and escalation is logged by the `AuditAgent` in plain, human-readable language.
- **Log Data Schema**: Every audit record captures the UTC timestamp, `case_id`, `customer_id`, decision (`approve`, `resolve`, `escalate`), recommended action, self-check verification result, approval reviewer metadata, and exact policy reason.
- **Access**: Accessible live via `GET /audit` and the Manager Audit Dashboard (`/audit`).

### 3. 🔒 Data Privacy (RBI & Indian DPDPA Guidelines)
- **PII / Secret Masking**: System prompts explicitly enforce privacy boundaries: *"Never expose full PAN, Aadhaar, CVV, or full card numbers in outputs or trace summaries."*
- **Role-Based Data Scoping**: Customers can only view their own account context and transactions. Internal manager queues and audit logs are restricted to authenticated compliance staff (`M1001`).
- **RBI Compliance**: Adheres to RBI guidelines for digital lending, dispute resolution, and payment system fraud reporting.

### 4. 🧠 Explainability
- **Plain-Language Reasons**: Every decision returns a human-understandable `reason` (e.g. *"Refund of ₹7,500 exceeds ₹1,000 threshold — human approval required"*).
- **Customer & Manager Explanations**: `DecisionAgent` generates structured, policy-aligned explanations explaining *why* an action was taken or recommended.
- **Agent Pipeline Transparency**: The frontend displays a live **Agent Pipeline Trace** badge list showing the step-by-step contributions of all 9 specialized agents (`Support` → `Payment` → `Fraud` → `Internal Ops` → `Decision` → `Self-Check` → `Approval` → `Audit`).

---

## 🤖 9 Cooperating Specialized Agents

| Agent | Responsibility | Model Tier | Guardrail / Role |
| :--- | :--- | :--- | :--- |
| **Router Agent** | Classifies incoming inquiry into domain | Rule-Based | Fast intent classification |
| **Support Agent** | Fetches customer profile, tier, and open tickets | Fast LLM / Rules | CRM Context Integration |
| **Payment Agent** | Analyzes UPI/NEFT/IMPS logs & dispute notes | Fast LLM / Rules | Payment Anomaly Detection |
| **Fraud Agent** | Assesses behavioral risk scores & velocity flags | Reasoning LLM | Risk Assessment ($\ge 70$ threshold) |
| **Internal Ops Agent** | Checks active workflow bottlenecks & pending cases | Rule-Based | Internal Operations Integration |
| **Decision Agent** | Synthesizes context & recommends action | Reasoning / Fast LLM | Policy & Threshold Evaluation |
| **Self-Check Agent** | Audits output against business guardrails | Rule-Based | Output Validation & Quality Gate |
| **Approval Agent** | Gates high-risk actions for HITL approval | Rule-Based | Human-in-the-Loop Queueing |
| **Audit Agent** | Writes immutable log entry with plain reason | Rule-Based | Audit Trail Compliance |

---

## ⚡ Quick Start

### 1. Backend Setup

```powershell
cd C:\AI-Banking-Agent
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```
- **Backend API**: `http://localhost:8000`
- **Interactive Swagger Docs**: `http://localhost:8000/docs`

### 2. Frontend Setup

```powershell
cd C:\AI-Banking-Agent\frontend
npm install
npm run dev
```
- **Web App UI**: `http://localhost:5173`

---

## 🔑 Login Credentials

| Role | User / Customer ID | Password | Available Features |
| :--- | :--- | :--- | :--- |
| **Customer** | `C1001` | `bank123` | Dashboard, Transfers & Cash Withdrawal, Transactions, Floating AI Copilot |
| **Ops Manager** | `M1001` | `admin123` | Manager HITL Queue, Audit Trail, System Metrics, Customer Directory |

---

## 🧪 Testing & Verification

Run the full automated test suite (8 integration and unit tests):
```powershell
python -m pytest
```

---

## 📂 Documentation

- [Architecture & AI Workflow](docs/ARCHITECTURE.md)
- [Guardrails & RBI Compliance Specification](docs/GUARDRAILS_AND_COMPLIANCE.md)
- [Business Pitch & Cost Analysis](docs/BUSINESS_PITCH.md)

---

## 📄 License

MIT — Built for AI Build 2026 Hackathon.
