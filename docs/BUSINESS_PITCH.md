# Business Pitch — FinOps Assistant

## The Problem

Financial operations teams at banks and NBFCs handle customer support, payment disputes, fraud investigations, and internal process requests — each living in a different system (CRM, payments platform, case management, approval workflows). An ops analyst must manually:

1. Look up customer context across 3–4 systems
2. Decide the right action based on policy
3. Get approval for high-risk actions
4. Execute and document the outcome

This manual orchestration slows routine work by **40–60%** and pulls senior staff away from cases that genuinely need human judgment.

## Our Solution

**FinOps Assistant** — an agentic AI copilot that:

- **Orchestrates 9 specialized agents** (support, payment, fraud, ops, decision, self-check, approval, audit) via LangGraph
- **Talks naturally** — ops staff describe what they need; the assistant handles the rest
- **Keeps humans in the loop** — refunds above ₹1,000, fraud holds, and account actions require manager approval
- **Explains every decision** in plain language with full audit trail
- **Uses tiered AI** — cheap rules for routing, expensive reasoning only for high-stakes cases

## Value Proposition

| Metric | Before | With FinOps Assistant |
|--------|--------|----------------------|
| Avg. case handling time | 12–18 min | 2–4 min |
| Systems to switch between | 4+ | 1 (chat interface) |
| Audit compliance | Manual notes | Automatic immutable log |
| High-risk error rate | Human-dependent | Self-check + HITL gate |
| Cost per routine decision | ₹50–80 (staff time) | ~₹0.01 (AI) |

## Rough Cost per Transaction

- **Routine support/dispute**: ~$0.0001 (rule-based agents)
- **Payment refund with approval**: ~$0.001 (fast LLM + HITL)
- **Fraud investigation**: ~$0.005 (reasoning LLM + HITL)

At 10,000 transactions/day: **~$5–15/day** in AI costs vs. **₹5–8 lakh/month** in manual ops staff time saved.

## What's Next

1. **Production integrations**: Live CRM (Salesforce), payments (Razorpay/Finacle), fraud (Featurespace)
2. **RAG over policy docs**: RBI master directions, internal SOPs for compliance-aware decisions
3. **Voice channel**: Call transcript ingestion for contact center automation
4. **Feedback loop**: Human approval outcomes train a smaller open-source model to reduce LLM dependency
5. **Multi-tenant deployment**: Per-bank configuration with role-based access control

## Demo Scenarios

1. **Duplicate UPI refund (₹7,500)** → Routes through all agents → HITL approval required
2. **Small auto-refund (₹500)** → Auto-approved, no human needed
3. **Fraud investigation (₹1,25,000 IMPS)** → Escalated with fraud hold
4. **Support inquiry (failed NEFT)** → Resolved with standard response
