import anthropic
from utils.shared.json_parser import safe_parse

_SYSTEM = (
    "You are a senior contract lawyer. Review the contract for legal risk, commercial risk, "
    "ambiguity, missing clauses, one-sided terms, inconsistent definitions, unclear obligations, "
    "liability exposure, weak remedies, problematic termination rights, governing law problems, "
    "dispute resolution problems, confidentiality gaps, anti-corruption gaps, data protection gaps, "
    "and enforcement risks. Do not provide final legal advice. Flag risks clearly and preserve the user's position."
)

_FALLBACK = {
    "overall_risk": "unknown",
    "executive_summary": "",
    "risks": [],
    "missing_clauses": [],
    "negotiation_points": [],
}


class ContractRiskChecker:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-opus-4-7"

    def check(self, text: str, contract_type: str, client_position: str, jurisdiction: str) -> dict:
        prompt = (
            f"Contract Type: {contract_type}\n"
            f"Client Position: {client_position}\n"
            f"Jurisdiction: {jurisdiction}\n\n"
            f"Contract text:\n---\n{text}\n---\n\n"
            "Return ONLY valid JSON:\n"
            "{\n"
            '  "overall_risk": "low | medium | high | critical",\n'
            '  "executive_summary": "",\n'
            '  "risks": [\n'
            '    {"clause":"","risk_identified":"","why_it_matters":"","risk_level":"low|medium|high|critical","suggested_revision":""}\n'
            "  ],\n"
            '  "missing_clauses": [\n'
            '    {"clause_name":"","why_needed":"","sample_clause":""}\n'
            "  ],\n"
            '  "negotiation_points": [\n'
            '    {"point":"","recommended_position":""}\n'
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
        result.setdefault("overall_risk", "unknown")
        result.setdefault("executive_summary", "")
        result.setdefault("risks", [])
        result.setdefault("missing_clauses", [])
        result.setdefault("negotiation_points", [])
        return result
