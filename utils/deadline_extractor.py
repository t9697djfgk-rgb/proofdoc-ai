import anthropic
from utils.shared.json_parser import safe_parse

_SYSTEM = (
    "You are a legal obligation and deadline extraction assistant. Extract all obligations, "
    "deadlines, notice periods, payment dates, renewal dates, reporting duties, filing dates, "
    "and compliance requirements. Identify responsible party, trigger, deadline, consequence, "
    "source clause, and priority. Do not invent dates. Flag unclear or conditional deadlines."
)

_FALLBACK = {"obligations": [], "deadlines": [], "unclear_deadlines": []}


class DeadlineExtractor:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-opus-4-7"

    def extract(self, text: str, doc_type: str, party_perspective: str) -> dict:
        prompt = (
            f"Document Type: {doc_type}\nParty Perspective: {party_perspective}\n\n"
            f"Document:\n---\n{text}\n---\n\n"
            "Return ONLY valid JSON:\n"
            "{\n"
            '  "obligations":[\n'
            '    {"responsible_party":"","obligation":"","trigger_event":"","deadline_or_date":"","consequence":"","source_clause":"","priority":"low|medium|high"}\n'
            "  ],\n"
            '  "deadlines":[\n'
            '    {"date_or_period":"","action_required":"","responsible_party":"","source_clause":"","priority":"low|medium|high"}\n'
            "  ],\n"
            '  "unclear_deadlines":[]\n'
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
