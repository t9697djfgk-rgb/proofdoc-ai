import anthropic
from utils.shared.json_parser import safe_parse

_SYSTEM = (
    "You are a legal due diligence assistant. Review the provided documents from the selected "
    "matter perspective. Identify red flags, missing documents, obligations, deadlines, liabilities, "
    "disputes, compliance issues, financial obligations, change-of-control issues, termination risks, "
    "and unusual clauses. Do not invent facts. Cite the relevant document section where possible."
)

_FALLBACK = {
    "executive_summary": "",
    "document_inventory": [],
    "red_flags": [],
    "key_obligations": [],
    "key_deadlines": [],
    "missing_documents": [],
    "follow_up_questions": [],
}


class DueDiligenceReview:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-opus-4-7"

    def review(self, text: str, matter_type: str, client_perspective: str, key_concerns: str) -> dict:
        prompt = (
            f"Matter Type: {matter_type}\nClient Perspective: {client_perspective}\n"
            f"Key Concerns: {key_concerns}\n\n"
            f"Documents:\n---\n{text}\n---\n\n"
            "Return ONLY valid JSON:\n"
            "{\n"
            '  "executive_summary":"",\n'
            '  "document_inventory":[{"document_name":"","document_type":"","brief_summary":""}],\n'
            '  "red_flags":[{"issue":"","document":"","section_or_reference":"","risk_level":"low|medium|high|critical","why_it_matters":"","recommended_action":""}],\n'
            '  "key_obligations":[],\n'
            '  "key_deadlines":[],\n'
            '  "missing_documents":[],\n'
            '  "follow_up_questions":[]\n'
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
