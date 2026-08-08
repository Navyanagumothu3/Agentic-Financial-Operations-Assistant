from typing import Dict, List

from utils.data_loader import filter_by_field, find_by_field


class CustomerService:
    """CRM integration — customer profiles, tickets, and support history."""

    def get_customer_context(self, customer_id: str) -> Dict[str, object]:
        customer = find_by_field("customers", "customer_id", customer_id)
        if not customer:
            return {
                "customer_id": customer_id,
                "name": "Unknown Customer",
                "tier": "standard",
                "risk_band": "medium",
                "recent_tickets": 0,
                "tickets": [],
            }

        tickets = filter_by_field("tickets", "customer_id", customer_id)
        open_tickets = [t for t in tickets if t.get("status") in ("open", "escalated")]

        return {
            "customer_id": customer_id,
            "name": customer.get("name", "Unknown"),
            "email": customer.get("email"),
            "phone": customer.get("phone"),
            "tier": customer.get("tier", "standard"),
            "risk_band": customer.get("risk_band", "medium"),
            "kyc_status": customer.get("kyc_status", "unknown"),
            "region": customer.get("region", "India"),
            "account_ids": customer.get("account_ids", []),
            "recent_tickets": len(tickets),
            "open_tickets": len(open_tickets),
            "tickets": tickets[:5],
        }

    def list_customers(self) -> List[Dict[str, object]]:
        from utils.data_loader import load_json

        return load_json("customers")
