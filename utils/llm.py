"""LLM abstraction — uses OpenAI when configured, otherwise rule-based summaries."""

import os
import re
from typing import Any, Dict, Optional

from utils.cost_tracker import cost_tracker


class LLMService:
    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY", "").strip()
        self.model_fast = os.getenv("OPENAI_MODEL_FAST", "gpt-4o-mini")
        self.model_reasoning = os.getenv("OPENAI_MODEL_REASONING", "gpt-4o")

    @property
    def is_live(self) -> bool:
        return bool(self.api_key)

    def summarize(self, agent: str, prompt: str, context: Dict[str, Any], *, tier: str = "fast_llm", case_id: str = "") -> str:
        if self.is_live:
            return self._call_openai(agent, prompt, context, tier, case_id)
        return self._rule_based_summary(agent, context)

    def _call_openai(self, agent: str, prompt: str, context: Dict[str, Any], tier: str, case_id: str) -> str:
        try:
            from openai import OpenAI

            client = OpenAI(api_key=self.api_key)
            model = self.model_reasoning if tier == "reasoning_llm" else self.model_fast
            user_content = f"{prompt}\n\nContext:\n{context}"
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a financial operations AI agent. Be concise, explainable, and RBI-compliant. Never expose full PAN/Aadhaar."},
                    {"role": "user", "content": user_content},
                ],
                max_tokens=300,
                temperature=0.2,
            )
            text = response.choices[0].message.content or ""
            tokens = response.usage.total_tokens if response.usage else 200
            cost_tracker.record(agent, tier, tokens, case_id)
            return text.strip()
        except Exception:
            return self._rule_based_summary(agent, context)

    def _rule_based_summary(self, agent: str, context: Dict[str, Any]) -> str:
        cost_tracker.record(agent, "rule_based", 0, context.get("case_id", ""))

        if agent == "support":
            tier = context.get("customer_tier", "standard")
            tickets = context.get("ticket_count", 0)
            name = context.get("customer_name", context.get("customer_id", "customer"))
            return (
                f"Support context for {name} ({tier} tier): "
                f"{tickets} recent ticket(s). Request via {context.get('channel', 'chat')}: "
                f"'{context.get('description', 'no description')}'."
            )
        if agent == "payment":
            disputes = context.get("dispute_count", 0)
            failed = context.get("failed_count", 0)
            dupes = context.get("duplicate_charges", 0)
            amount = context.get("amount", 0)
            parts = []
            if dupes:
                parts.append(f"{dupes} possible duplicate charge(s)")
            if disputes:
                parts.append(f"{disputes} dispute indicator(s)")
            if failed:
                parts.append(f"{failed} failed payment(s)")
            detail = ", ".join(parts) if parts else "no payment anomalies"
            return f"Payment review for ₹{amount:,.0f}: {detail}. Account {context.get('account_id', 'unknown')}."
        if agent == "fraud":
            flags = context.get("risk_flags", [])
            score = context.get("risk_score", 0)
            if flags:
                return f"Fraud assessment: risk score {score}/100. Flags: {', '.join(flags)}."
            return f"Fraud assessment: risk score {score}/100. No active fraud flags."
        if agent == "decision":
            return self._decision_explanation(context)
        if agent == "self_check":
            return self._self_check(context)
        return f"{agent} analysis complete for case {context.get('case_id', 'unknown')}."

    def _decision_explanation(self, ctx: Dict[str, Any]) -> str:
        decision = ctx.get("decision", "pending")
        action = ctx.get("action", "review")
        reason = ctx.get("reason", "")
        return f"Decision: {decision}. Recommended action: {action}. Reason: {reason}"

    def _self_check(self, ctx: Dict[str, Any]) -> str:
        issues = []
        if ctx.get("approval_required") and ctx.get("decision") == "approve":
            if float(ctx.get("amount", 0)) > 1000:
                issues.append("High-value approval flagged correctly")
        if "velocity spike" in str(ctx.get("fraud_summary", "")) and ctx.get("decision") != "escalate":
            issues.append("WARNING: fraud signal may need escalation")
        if not ctx.get("reason"):
            issues.append("WARNING: missing explainability")
        if not issues:
            return "Self-check passed: decision aligns with business goals and guardrails."
        return "Self-check: " + "; ".join(issues)


llm_service = LLMService()
