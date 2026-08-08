from typing import Dict, List

from utils.data_loader import filter_by_field


class PaymentService:
    """Payments platform integration — transactions, disputes, and failure records."""

    REFUND_THRESHOLD_INR = 1000
    HIGH_VALUE_THRESHOLD_INR = 50000

    def get_payment_context(self, account_id: str) -> Dict[str, object]:
        transactions = filter_by_field("transactions", "account_id", account_id)
        disputes = [
            t for t in transactions
            if t.get("note") or t.get("status") == "failed"
        ]
        failed = [t for t in transactions if t.get("status") == "failed"]
        duplicates = [t for t in transactions if "duplicate" in str(t.get("note", "")).lower()]

        return {
            "account_id": account_id,
            "recent_payments": transactions[:10],
            "transaction_count": len(transactions),
            "dispute_count": len(disputes),
            "failed_count": len(failed),
            "duplicate_charges": len(duplicates),
            "total_volume": sum(float(t.get("amount", 0)) for t in transactions),
        }

    def get_transaction(self, txn_id: str) -> Dict[str, object] | None:
        from utils.data_loader import find_by_field

        return find_by_field("transactions", "txn_id", txn_id)
