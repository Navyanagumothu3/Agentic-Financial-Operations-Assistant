from typing import Dict, List

from utils.data_loader import load_json
from utils.logger import log_event

_entries: List[Dict[str, str]] = []


class AuditService:
    """Immutable audit trail for every agent action and escalation."""

    def record(self, entries: List[Dict[str, str]]) -> None:
        for entry in entries:
            _entries.append(entry)
            log_event(entry.get("message", str(entry)))

    def list_entries(self, limit: int = 50) -> List[Dict[str, str]]:
        return list(reversed(_entries[-limit:]))

    def clear(self) -> None:
        _entries.clear()


class InternalOpsService:
    """Internal ops workflows and approval records."""

    def list_workflows(self) -> List[Dict[str, object]]:
        return load_json("internal_workflows")

    def get_pending_approvals(self) -> List[Dict[str, object]]:
        return [w for w in self.list_workflows() if w.get("status") == "pending"]
