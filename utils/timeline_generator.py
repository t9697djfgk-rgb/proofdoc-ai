import anthropic
from utils.shared.json_parser import safe_parse

_SYSTEM = (
    "You are a legal chronology assistant. Extract dated and undated events from the provided "
    "text. Create a chronological timeline. Identify people/entities involved, source references, "
    "legal relevance, uncertain dates, conflicting dates, and missing chronology questions. "
    "Do not invent dates. If exact date is unavailable, mark it as approximate or unknown."
)

_FALLBACK = {
    "timeline": [],
    "undated_events": [],
    "conflicting_dates": [],
    "missing_questions": [],
}


class TimelineGenerator:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-opus-4-7"

    def generate(self, text: str, matter_type: str, date_format: str) -> dict:
        prompt = (
            f"Matter Type: {matter_type}\nPreferred Date Format: {date_format}\n\n"
            f"Document/text:\n---\n{text}\n---\n\n"
            "Return ONLY valid JSON:\n"
            "{\n"
            '  "timeline":[\n'
            '    {"date":"","event":"","source_reference":"","people_or_entities":[],"legal_relevance":"","confidence":"low|medium|high"}\n'
            "  ],\n"
            '  "undated_events":[],"conflicting_dates":[],"missing_questions":[]\n'
            "}"
        )
        resp = self.client.messages.create(
            model=self.model, max_tokens=6144,
            system=[{"type": "text", "text": _SYSTEM, "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": prompt}],
        )
        raw = next((b.text for b in resp.content if b.type == "text"), "{}")
        result = safe_parse(raw, _FALLBACK.copy())
        for k, v in _FALLBACK.items():
            result.setdefault(k, v)
        return result
