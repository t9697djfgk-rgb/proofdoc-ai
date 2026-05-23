"""Clause library management — JSON file backed, in-memory cached."""
from __future__ import annotations
import json
import os
import secrets
from datetime import datetime

_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "clause_library.json")

CATEGORIES = [
    "Confidentiality", "Governing law", "Dispute resolution", "Arbitration",
    "Termination", "Limitation of liability", "Indemnity", "Force majeure",
    "Anti-corruption", "Sanctions", "Data protection", "Payment",
    "Intellectual property", "Non-compete", "Non-solicitation", "Other",
]

JURISDICTIONS = [
    "International/Neutral", "UK", "US", "EU", "Rwanda", "Other",
]


def _load() -> list[dict]:
    try:
        with open(_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def _save(clauses: list[dict]) -> None:
    os.makedirs(os.path.dirname(_PATH), exist_ok=True)
    with open(_PATH, "w", encoding="utf-8") as f:
        json.dump(clauses, f, indent=2, ensure_ascii=False)


def get_all() -> list[dict]:
    return _load()


def search(query: str = "", category: str = "", jurisdiction: str = "") -> list[dict]:
    clauses = _load()
    q = query.lower()
    result = []
    for c in clauses:
        if category and c.get("category") != category:
            continue
        if jurisdiction and c.get("jurisdiction") != jurisdiction:
            continue
        if q and q not in c.get("title", "").lower() and q not in c.get("clause_text", "").lower():
            continue
        result.append(c)
    return result


def get_by_id(clause_id: str) -> dict | None:
    for c in _load():
        if c.get("id") == clause_id:
            return c
    return None


def add_clause(
    title: str,
    category: str,
    jurisdiction: str,
    clause_text: str,
    notes: str = "",
    risk_level: str = "medium",
    approved: bool = False,
) -> dict:
    clauses = _load()
    now = datetime.now().isoformat()
    new_clause = {
        "id": f"cl_{secrets.token_hex(4)}",
        "title": title,
        "category": category,
        "jurisdiction": jurisdiction,
        "clause_text": clause_text,
        "notes": notes,
        "risk_level": risk_level,
        "approved": approved,
        "created_at": now,
        "updated_at": now,
    }
    clauses.append(new_clause)
    _save(clauses)
    return new_clause


def update_clause(clause_id: str, **kwargs) -> bool:
    clauses = _load()
    for i, c in enumerate(clauses):
        if c.get("id") == clause_id:
            clauses[i].update(kwargs)
            clauses[i]["updated_at"] = datetime.now().isoformat()
            _save(clauses)
            return True
    return False


def delete_clause(clause_id: str) -> bool:
    clauses = _load()
    new_clauses = [c for c in clauses if c.get("id") != clause_id]
    if len(new_clauses) < len(clauses):
        _save(new_clauses)
        return True
    return False
