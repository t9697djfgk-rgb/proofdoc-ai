import anthropic
from utils.shared.json_parser import safe_parse

_SYSTEM = (
    "You are a law firm intake assistant. Convert client-provided facts into a structured "
    "lawyer handover note. Do not give final legal advice. Identify key issues, missing "
    "information, documents to request, important dates, urgency, and recommended next steps."
)

_FALLBACK = {
    "client_summary": "",
    "key_legal_issues": [],
    "missing_information": [],
    "documents_to_request": [],
    "important_dates": [],
    "urgency_assessment": "medium",
    "suggested_next_steps": [],
    "lawyer_handover_note": "",
}


class ClientIntakeAssistant:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-opus-4-7"

    def process(
        self,
        matter_type: str,
        client_name: str,
        contact_details: str,
        opposing_party: str,
        key_facts: str,
        important_dates: str,
        docs_available: str,
        desired_outcome: str,
        urgency: str,
        notes: str,
    ) -> dict:
        prompt = (
            f"Matter Type: {matter_type}\nClient Name: {client_name}\n"
            f"Contact Details: {contact_details}\nOpposing Party: {opposing_party}\n"
            f"Key Facts: {key_facts}\nImportant Dates: {important_dates}\n"
            f"Documents Available: {docs_available}\nDesired Outcome: {desired_outcome}\n"
            f"Urgency: {urgency}\nAdditional Notes: {notes}\n\n"
            "Return ONLY valid JSON:\n"
            "{\n"
            '  "client_summary":"","key_legal_issues":[],"missing_information":[],\n'
            '  "documents_to_request":[],"important_dates":[],"urgency_assessment":"low|medium|high|urgent",\n'
            '  "suggested_next_steps":[],"lawyer_handover_note":""\n'
            "}"
        )
        resp = self.client.messages.create(
            model=self.model, max_tokens=4096,
            system=[{"type": "text", "text": _SYSTEM, "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": prompt}],
        )
        raw = next((b.text for b in resp.content if b.type == "text"), "{}")
        result = safe_parse(raw, _FALLBACK.copy())
        for k, v in _FALLBACK.items():
            result.setdefault(k, v)
        return result
