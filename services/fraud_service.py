from typing import Dict, List

from utils.data_loader import filter_by_field


class FraudService:
    """Case management integration — fraud history and investigation notes."""

    def get_fraud_context(self, customer_id: str) -> Dict[str, object]:
        cases = filter_by_field("fraud_cases", "customer_id", customer_id)
        active = [c for c in cases if c.get("status") == "under_investigation"]

        all_flags: List[str] = []
        max_score = 0
        for case in cases:
            all_flags.extend(case.get("risk_flags", []))
            max_score = max(max_score, int(case.get("risk_score", 0)))

        unique_flags = list(dict.fromkeys(all_flags))

        return {
            "customer_id": customer_id,
            "prior_cases": len(cases),
            "active_cases": len(active),
            "risk_score": max_score,
            "risk_flags": unique_flags,
            "case_history": [c.get("investigation_notes", "") for c in cases[:3]],
            "cases": cases,
        }
