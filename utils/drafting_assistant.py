import anthropic
from utils.shared.json_parser import safe_parse

_SYSTEM = (
    "You are a senior legal drafting assistant. Generate a professional first draft based only "
    "on the user's facts and instructions. Do not invent facts. Where information is missing, "
    "use [PLACEHOLDER] or list questions. Use precise legal English. Include assumptions and "
    "risk warnings. Do not present the draft as final legal advice."
)

_FALLBACK = {
    "draft_title": "",
    "draft_document": "",
    "assumptions": [],
    "missing_information": [],
    "risk_warnings": [],
    "optional_clauses": [],
}


class DraftingAssistant:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-opus-4-7"

    def draft(
        self,
        doc_type: str,
        jurisdiction: str,
        legal_style: str,
        parties: str,
        key_facts: str,
        tone: str,
        additional: str,
    ) -> dict:
        prompt = (
            f"Document Type: {doc_type}\nJurisdiction: {jurisdiction}\nLegal Style: {legal_style}\n"
            f"Parties: {parties}\nKey Facts: {key_facts}\nTone: {tone}\n"
            f"Additional Instructions: {additional}\n\n"
            "Return ONLY valid JSON:\n"
            "{\n"
            '  "draft_title": "",\n'
            '  "draft_document": "",\n'
            '  "assumptions": [],\n'
            '  "missing_information": [],\n'
            '  "risk_warnings": [],\n'
            '  "optional_clauses": [\n'
            '    {"clause_name":"","clause_text":"","when_to_use":""}\n'
            "  ]\n"
            "}"
        )
        resp = self.client.messages.create(
            model=self.model, max_tokens=8192,
            system=[{"type": "text", "text": _SYSTEM, "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": prompt}],
        )
        raw = next((b.text for b in resp.content if b.type == "text"), "{}")
        result = safe_parse(raw, _FALLBACK.copy())
        for k, v in _FALLBACK.items():
            result.setdefault(k, v)
        return result
