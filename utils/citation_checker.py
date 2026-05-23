import anthropic
from utils.shared.json_parser import safe_parse

_SYSTEM = (
    "You are a legal citation and authority checker. Extract all cases, statutes, regulations, "
    "treaties, articles, books, and footnotes. Check citation format, internal consistency, "
    "missing court/year/page/pinpoint details, suspicious or incomplete references, "
    "quotation-risk issues, and whether the cited authority appears to support the nearby "
    "proposition based only on the text available. Do not invent authorities. "
    "Do not claim a source exists unless verified. Clearly state you cannot verify external "
    "existence of authorities, only format and consistency."
)

_FALLBACK = {
    "summary": {"total_citations": 0, "formatting_issues": 0, "missing_details": 0,
                "quotation_risks": 0, "possible_invalid_citations": 0},
    "citations": [],
    "general_recommendations": [],
}


class CitationChecker:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-opus-4-7"

    def check(self, text: str, citation_style: str, jurisdiction: str) -> dict:
        prompt = (
            f"Citation Style: {citation_style}\nJurisdiction: {jurisdiction}\n\n"
            f"Document:\n---\n{text}\n---\n\n"
            "Return ONLY valid JSON:\n"
            "{\n"
            '  "summary": {"total_citations":0,"formatting_issues":0,"missing_details":0,"quotation_risks":0,"possible_invalid_citations":0},\n'
            '  "citations": [\n'
            '    {"citation_text":"","citation_type":"case|statute|regulation|treaty|article|book|other","issue":"","severity":"low|medium|high","suggested_fix":"","explanation":""}\n'
            "  ],\n"
            '  "general_recommendations": []\n'
            "}"
        )
        resp = self.client.messages.create(
            model=self.model, max_tokens=6144,
            system=[{"type": "text", "text": _SYSTEM, "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": prompt}],
        )
        raw = next((b.text for b in resp.content if b.type == "text"), "{}")
        result = safe_parse(raw, _FALLBACK.copy())
        result.setdefault("summary", _FALLBACK["summary"].copy())
        result.setdefault("citations", [])
        result.setdefault("general_recommendations", [])
        return result
