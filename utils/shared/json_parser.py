"""Safe JSON parsing for AI responses."""
from __future__ import annotations
import json
import re


def safe_parse(raw: str, fallback: dict | None = None) -> dict:
    """
    Parse JSON from an AI response string.
    Handles markdown code fences, leading/trailing text, and partial JSON.
    Returns fallback dict on failure (or empty dict if fallback is None).
    """
    if fallback is None:
        fallback = {}

    if not raw or not raw.strip():
        return {**fallback, "_parse_error": True, "_raw": ""}

    text = raw.strip()

    # Strip markdown code fences
    if "```" in text:
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text.strip())

    # Direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to extract the first {...} block
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # Return fallback with error flag
    return {**fallback, "_parse_error": True, "_raw": raw[:500]}
