import anthropic
from utils.shared.json_parser import safe_parse

_SYSTEM_DRAFT = (
    "You are a compliance lawyer and policy drafting assistant. Draft a practical compliance "
    "policy tailored to the organization, industry, jurisdiction, and risk level. Use clear, "
    "professional legal English. Do not invent specific laws unless provided or verified. "
    "Include implementation steps, reporting channels, responsibilities, training, monitoring, "
    "and review procedures. "
    "Return ONLY the policy document text — no JSON, no metadata, no commentary."
)

_SYSTEM_META = (
    "You are a compliance assistant. Analyse the policy draft and return ONLY valid JSON — "
    "no other text. JSON must have exactly these keys: "
    "implementation_checklist (list of strings), "
    "training_recommendations (list of strings), "
    "reporting_channels (list of strings), "
    "disciplinary_measures (string), "
    "review_schedule (string), "
    "risk_warnings (list of strings)."
)

_FALLBACK_META = {
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
            f"Policy Type: {policy_type}\n"
            f"Organization: {org_name}\n"
            f"Industry: {industry}\n"
            f"Jurisdiction: {jurisdiction}\n"
            f"Employees: {employees}\n"
            f"Risk Level: {risk_level}\n"
            f"Additional Instructions: {additional}"
        )

        # ── Call 1: full policy document as plain text ───────────────
        doc_resp = self.client.messages.create(
            model=self.model,
            max_tokens=8192,
            system=[{"type": "text", "text": _SYSTEM_DRAFT,
                     "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": prompt}],
        )
        policy_document = next(
            (b.text for b in doc_resp.content if b.type == "text"), ""
        )

        lines = [ln.lstrip("#").strip() for ln in policy_document.splitlines() if ln.strip()]
        policy_title = lines[0] if lines else policy_type

        # ── Call 2: small metadata JSON ──────────────────────────────
        meta_prompt = (
            f"Here is a {policy_type} (first 3000 chars):\n\n"
            f"{policy_document[:3000]}\n\n"
            "Return ONLY the JSON metadata object described in your instructions."
        )
        meta_resp = self.client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=1024,
            system=_SYSTEM_META,
            messages=[{"role": "user", "content": meta_prompt}],
        )
        meta_raw = next(
            (b.text for b in meta_resp.content if b.type == "text"), "{}"
        )
        meta = safe_parse(meta_raw, _FALLBACK_META.copy())

        return {
            "policy_title":             policy_title,
            "policy_document":          policy_document,
            "implementation_checklist": meta.get("implementation_checklist", []),
            "training_recommendations": meta.get("training_recommendations", []),
            "reporting_channels":       meta.get("reporting_channels", []),
            "disciplinary_measures":    meta.get("disciplinary_measures", ""),
            "review_schedule":          meta.get("review_schedule", ""),
            "risk_warnings":            meta.get("risk_warnings", []),
        }
