import anthropic
import json
import re

SYSTEM_PROMPT = (
    "You are an expert legal analyst. Identify and categorise all potential legal issues, "
    "ambiguities, and drafting problems in the document provided. For each issue give: "
    "category, clause reference (if any), description, severity (critical/high/medium/low), "
    "and recommended remedy. Be thorough but precise — flag real problems, not hypotheticals."
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
    return {"issues": [], "summary": "", "_parse_error": True}


class IssueSpotter:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-opus-4-7"

    def spot(self, text: str, doc_type: str, jurisdiction: str, perspective: str) -> dict:
        prompt = (
            f"Document Type: {doc_type}\n"
            f"Jurisdiction: {jurisdiction}\n"
            f"Perspective: {perspective}\n\n"
            f"Document:\n---\n{text[:12000]}\n---\n\n"
            "Return ONLY valid JSON:\n"
            "{\n"
            '  "summary": "overall assessment in 2-3 sentences",\n'
            '  "risk_level": "critical | high | medium | low",\n'
            '  "issue_count": 0,\n'
            '  "issues": [\n'
            '    {\n'
            '      "category": "Ambiguity | Missing clause | Inconsistency | Enforceability | Drafting error | Commercial risk | Compliance | Other",\n'
            '      "clause_reference": "e.g. Clause 4.2 or N/A",\n'
            '      "description": "clear description of the issue",\n'
            '      "severity": "critical | high | medium | low",\n'
            '      "remedy": "specific recommended fix"\n'
            "    }\n"
            "  ],\n"
            '  "priority_actions": ["top 3-5 most urgent fixes"]\n'
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
        result.setdefault("issues", [])
        result.setdefault("summary", "")
        result.setdefault("risk_level", "medium")
        result.setdefault("priority_actions", [])
        result["issue_count"] = len(result["issues"])
        return result
