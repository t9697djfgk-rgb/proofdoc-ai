import anthropic
import json
import re

SYSTEM_PROMPT = (
    "You are a senior commercial lawyer. Produce clear, accurate summaries of legal contracts. "
    "Extract all key commercial and legal terms. Write in plain English suitable for a client briefing. "
    "Never fabricate details — only summarise what is in the document."
)


def _parse(raw: str) -> dict:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw.strip())
    try:
        return json.loads(raw)
    except Exception:
        m = re.search(r"\{.*\}", raw, re.DOTALL)
        if m:
            try:
                return json.loads(m.group())
            except Exception:
                pass
    return {"_parse_error": True}


class ContractSummarizer:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-opus-4-7"

    def summarize(self, text: str, contract_type: str, perspective: str) -> dict:
        prompt = (
            f"Contract Type: {contract_type}\n"
            f"Client Perspective: {perspective}\n\n"
            f"Contract:\n---\n{text[:14000]}\n---\n\n"
            "Return ONLY valid JSON:\n"
            "{\n"
            '  "executive_summary": "2-3 sentence plain-English overview",\n'
            '  "parties": [{"name": "", "role": ""}],\n'
            '  "key_terms": {\n'
            '    "effective_date": "",\n'
            '    "term_duration": "",\n'
            '    "governing_law": "",\n'
            '    "contract_value": "",\n'
            '    "payment_terms": "",\n'
            '    "termination": "",\n'
            '    "notice_period": "",\n'
            '    "dispute_resolution": ""\n'
            "  },\n"
            '  "key_obligations": [\n'
            '    {"party": "", "obligation": "", "deadline": ""}\n'
            "  ],\n"
            '  "key_rights": ["list of key rights"],\n'
            '  "limitations_and_exclusions": ["list"],\n'
            '  "risk_flags": [\n'
            '    {"issue": "", "severity": "high | medium | low", "recommendation": ""}\n'
            "  ],\n"
            '  "missing_standard_clauses": ["list any absent standard clauses"],\n'
            '  "client_advice": "2-3 sentence advice for the client given their perspective"\n'
            "}"
        )
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=[{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": prompt}],
        )
        raw = next((b.text for b in response.content if b.type == "text"), "{}")
        result = _parse(raw)
        result.setdefault("executive_summary", "")
        result.setdefault("parties", [])
        result.setdefault("key_terms", {})
        result.setdefault("key_obligations", [])
        result.setdefault("key_rights", [])
        result.setdefault("risk_flags", [])
        result.setdefault("missing_standard_clauses", [])
        result.setdefault("client_advice", "")
        return result


class RiskReportGenerator:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-opus-4-7"

    def generate(self, text: str, doc_type: str, reporting_audience: str, jurisdiction: str) -> dict:
        prompt = (
            f"Document Type: {doc_type}\n"
            f"Reporting Audience: {reporting_audience}\n"
            f"Jurisdiction: {jurisdiction}\n\n"
            f"Document(s):\n---\n{text[:14000]}\n---\n\n"
            "Return ONLY valid JSON:\n"
            "{\n"
            '  "overall_risk_rating": "Critical | High | Medium | Low",\n'
            '  "executive_summary": "3-5 sentence board-level overview",\n'
            '  "risk_register": [\n'
            '    {\n'
            '      "risk_id": "R001",\n'
            '      "category": "Legal | Commercial | Regulatory | Operational | Reputational | Financial",\n'
            '      "description": "",\n'
            '      "likelihood": "High | Medium | Low",\n'
            '      "impact": "High | Medium | Low",\n'
            '      "current_mitigation": "",\n'
            '      "recommended_action": "",\n'
            '      "owner": "",\n'
            '      "priority": "Immediate | Short-term | Medium-term | Monitor"\n'
            "    }\n"
            "  ],\n"
            '  "immediate_actions": ["list of actions needed within 30 days"],\n'
            '  "compliance_gaps": ["regulatory or compliance issues identified"],\n'
            '  "conclusion": "concluding risk assessment paragraph"\n'
            "}"
        )
        response = self.client.messages.create(
            model=self.model,
            max_tokens=5120,
            system=[{"type": "text", "text": SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": prompt}],
        )
        raw = next((b.text for b in response.content if b.type == "text"), "{}")
        result = _parse(raw)
        result.setdefault("overall_risk_rating", "Medium")
        result.setdefault("executive_summary", "")
        result.setdefault("risk_register", [])
        result.setdefault("immediate_actions", [])
        result.setdefault("compliance_gaps", [])
        result.setdefault("conclusion", "")
        return result
