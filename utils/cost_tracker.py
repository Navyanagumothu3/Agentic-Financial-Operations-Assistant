"""Cost tracking for multi-tier model usage (cheap routing vs expensive reasoning)."""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ModelTier:
    name: str
    cost_per_1k_tokens: float
    label: str


MODEL_TIERS = {
    "rule_based": ModelTier("rule_based", 0.0, "Rule-based / Classical"),
    "fast_llm": ModelTier("fast_llm", 0.00015, "Fast LLM (e.g. GPT-4o-mini)"),
    "reasoning_llm": ModelTier("reasoning_llm", 0.003, "Reasoning LLM (e.g. GPT-4o)"),
}


@dataclass
class CostTracker:
    decisions: List[Dict[str, object]] = field(default_factory=list)

    def record(self, agent: str, tier: str, tokens: int = 0, case_id: str = "") -> float:
        model = MODEL_TIERS.get(tier, MODEL_TIERS["rule_based"])
        cost = (tokens / 1000) * model.cost_per_1k_tokens if tokens else 0.001 if tier != "rule_based" else 0.0
        entry = {
            "agent": agent,
            "tier": tier,
            "model_label": model.label,
            "tokens": tokens,
            "cost_usd": round(cost, 6),
            "case_id": case_id,
        }
        self.decisions.append(entry)
        return cost

    def summary(self) -> Dict[str, object]:
        total = sum(d["cost_usd"] for d in self.decisions)
        by_tier: Dict[str, int] = {}
        for d in self.decisions:
            by_tier[d["tier"]] = by_tier.get(d["tier"], 0) + 1
        return {
            "total_decisions": len(self.decisions),
            "total_cost_usd": round(total, 4),
            "avg_cost_per_decision_usd": round(total / len(self.decisions), 6) if self.decisions else 0,
            "by_tier": by_tier,
            "recent": self.decisions[-10:],
        }


cost_tracker = CostTracker()
