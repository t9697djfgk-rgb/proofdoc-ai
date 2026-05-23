import anthropic
from utils.shared.json_parser import safe_parse

_SYSTEM = (
    "You are a legal document comparison expert. Compare the original and revised documents. "
    "Identify additions, deletions, modifications, and changes in legal effect. Focus on rights, "
    "obligations, liability, payment, deadlines, termination, jurisdiction, dispute resolution, "
    "remedies, confidentiality, definitions, and conditions. Do not simply summarize textual "
    "changes; explain legal significance."
)

_FALLBACK = {"executive_summary": "", "changes": []}


class DocumentComparison:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-opus-4-7"

    def compare(self, original: str, revised: str, doc_type: str, client_position: str) -> dict:
        prompt = (
            f"Document Type: {doc_type}\nClient Position: {client_position}\n\n"
            f"ORIGINAL DOCUMENT:\n---\n{original}\n---\n\n"
            f"REVISED DOCUMENT:\n---\n{revised}\n---\n\n"
            "Return ONLY valid JSON:\n"
            "{\n"
            '  "executive_summary": "",\n'
            '  "changes": [\n'
            '    {\n'
            '      "change_type":"added|deleted|modified",\n'
            '      "section":"","original_text":"","revised_text":"",\n'
            '      "legal_significance":"",\n'
            '      "risk_level":"low|medium|high|critical",\n'
            '      "affected_area":[],\n'
            '      "recommended_action":""\n'
            "    }\n"
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
        result.setdefault("executive_summary", "")
        result.setdefault("changes", [])
        return result
