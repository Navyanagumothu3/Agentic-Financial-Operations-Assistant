from pathlib import Path
from typing import Any, Dict


class PromptService:
    def __init__(self, prompts_dir: str | None = None) -> None:
        base_dir = Path(__file__).resolve().parent.parent
        self.prompts_dir = Path(prompts_dir) if prompts_dir else base_dir / "prompts"

    def load_prompt(self, name: str) -> str:
        prompt_path = self.prompts_dir / f"{name}_prompt.txt"
        if not prompt_path.exists():
            return f"You are assisting with {name} operations."
        return prompt_path.read_text(encoding="utf-8")

    def render(self, name: str, context: Dict[str, Any]) -> str:
        template = self.load_prompt(name)
        safe_context = {
            "customer_id": context.get("customer_id", "unknown"),
            "account_id": context.get("account_id", "unknown"),
            "request_type": context.get("request_type", "support"),
            "amount": context.get("amount", 0),
            "description": context.get("description", ""),
            "channel": context.get("channel", "chat"),
            "customer_tier": context.get("customer_tier", "standard"),
            "ticket_count": context.get("ticket_count", 0),
            "dispute_count": context.get("dispute_count", 0),
            "risk_flags": context.get("risk_flags", []),
            "support_summary": context.get("support_summary", ""),
            "payment_summary": context.get("payment_summary", ""),
            "fraud_summary": context.get("fraud_summary", ""),
        }
        try:
            return template.format(**safe_context)
        except KeyError:
            return template
