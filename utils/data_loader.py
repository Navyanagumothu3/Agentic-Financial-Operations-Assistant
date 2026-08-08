import json
from pathlib import Path
from typing import Any, Dict, List

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
_cache: Dict[str, List[Dict[str, Any]]] = {}


def load_json(name: str) -> List[Dict[str, Any]]:
    if name not in _cache:
        path = DATA_DIR / f"{name}.json"
        if path.exists():
            _cache[name] = json.loads(path.read_text(encoding="utf-8"))
        else:
            _cache[name] = []
    return _cache[name]


def find_by_field(dataset: str, field: str, value: str) -> Dict[str, Any] | None:
    for item in load_json(dataset):
        if str(item.get(field)) == str(value):
            return item
    return None


def filter_by_field(dataset: str, field: str, value: str) -> List[Dict[str, Any]]:
    return [item for item in load_json(dataset) if str(item.get(field)) == str(value)]
