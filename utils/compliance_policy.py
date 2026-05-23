import anthropic
from utils.shared.json_parser import safe_parse

_SYSTEM = (
    "You are a compliance lawyer and policy drafting assistant. Draft a practical compliance "
    "policy tailored to the organization, industry, jurisdiction, and risk level. Use clear, "
    "professional legal English. Do not invent specific laws unless provided or verified. "
    "Include implementation steps, reporting channels, responsibilities, training, monitoring, "
    "and review procedures."
)

_FALLBACK = {
    "policy_title": "",
    "policy_document": "",
    "implementation_checklist": [],
    "training_recommendations": [],
    "reporting_channels": [],
    "disciplinary_measures": "",
    "review_schedule": "",
    "risk_warnings": [],
}


class CompliancePolicyGenerator:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-opus-4-7"

    def generate(
        self,
        policy_type: str,
        org_name: str,
        industry: str,
        jurisdiction: str,
        employees: str,
        risk_level: str,
        additional: str,
    ) -> dict:
        prompt = (
            f"Policy Type: {policy_type}\nOrganization: {org_name}\nIndustry: {industry}\n"
            f"Jurisdiction: {jurisdiction}\nEmployees: {employees}\nRisk Level: {risk_level}\n"
            f"Additional Instructions: {additional}\n\n"
            "Return ONLY valid JSON:\n"
            "{\n"
            '  "policy_title":"","policy_document":"","implementation_checklist":[],\n'
            '  "training_recommendations":[],"reporting_channels":[],\n'
            '  "disciplinary_measures":"","review_schedule":"","risk_warnings":[]\n'
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
