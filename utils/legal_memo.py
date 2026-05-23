import anthropic
from utils.shared.json_parser import safe_parse

_SYSTEM = (
    "You are a senior legal research and memo-writing assistant. Write a structured legal "
    "memorandum based only on the facts and legal materials provided. Do not invent cases, "
    "statutes, or authorities. If legal authority is missing, say so. Separate law from "
    "analysis. Include counterarguments and risks."
)

_FALLBACK = {
    "issue": "",
    "brief_answer": "",
    "facts": "",
    "applicable_law": "",
    "analysis": "",
    "counterarguments": "",
    "risks": [],
    "recommendations": [],
    "conclusion": "",
}


class LegalMemoGenerator:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-opus-4-7"

    def generate(
        self,
        legal_issue: str,
        facts: str,
        jurisdiction: str,
        research_notes: str,
        client_position: str,
        memo_type: str,
    ) -> dict:
        prompt = (
            f"Memo Type: {memo_type}\nJurisdiction: {jurisdiction}\nClient Position: {client_position}\n"
            f"Legal Issue/Question: {legal_issue}\nFacts: {facts}\n"
            f"Relevant Law/Research Notes: {research_notes}\n\n"
            "Return ONLY valid JSON:\n"
            "{\n"
            '  "issue":"","brief_answer":"","facts":"","applicable_law":"",\n'
            '  "analysis":"","counterarguments":"","risks":[],"recommendations":[],"conclusion":""\n'
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
