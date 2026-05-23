import anthropic
from utils.shared.json_parser import safe_parse

_SYSTEM = (
    "You are a senior litigation drafting reviewer. Review the court document for structure, "
    "clarity, persuasiveness, procedural completeness, unsupported assertions, missing relief, "
    "citation issues, tone, and legal argument quality. Do not invent law or facts. "
    "Flag issues that require lawyer review."
)

_FALLBACK = {
    "filing_readiness_score": 0,
    "executive_summary": "",
    "structural_issues": [],
    "missing_elements": [],
    "weak_arguments": [],
    "unsupported_factual_claims": [],
    "citation_issues": [],
    "tone_issues": [],
    "relief_clarity_issues": [],
    "suggested_improvements": [],
}


class CourtDocumentChecker:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-opus-4-7"

    def check(self, text: str, doc_type: str, court_jurisdiction: str, party: str) -> dict:
        prompt = (
            f"Document Type: {doc_type}\nCourt/Jurisdiction: {court_jurisdiction}\n"
            f"Party Represented: {party}\n\n"
            f"Document:\n---\n{text}\n---\n\n"
            "Return ONLY valid JSON:\n"
            "{\n"
            '  "filing_readiness_score": 0,\n'
            '  "executive_summary":"",\n'
            '  "structural_issues":[],"missing_elements":[],"weak_arguments":[],\n'
            '  "unsupported_factual_claims":[],"citation_issues":[],"tone_issues":[],\n'
            '  "relief_clarity_issues":[],"suggested_improvements":[]\n'
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
