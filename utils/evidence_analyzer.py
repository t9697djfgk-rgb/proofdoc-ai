import anthropic
from utils.shared.json_parser import safe_parse

_SYSTEM = (
    "You are a litigation and evidence analysis assistant. Analyze the evidence or witness "
    "statement. Identify key facts, admissions, contradictions, inconsistencies, missing facts, "
    "weaknesses, strengths, follow-up questions, and possible cross-examination questions. "
    "Do not fabricate facts. Separate facts from inferences."
)

_FALLBACK = {
    "key_facts": [],
    "key_admissions": [],
    "contradictions": [],
    "missing_facts": [],
    "strong_points": [],
    "weak_points": [],
    "follow_up_questions": [],
    "cross_examination_questions": [],
    "timeline_facts": [],
}


class EvidenceAnalyzer:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-opus-4-7"

    def analyze(self, text: str, case_type: str, role: str) -> dict:
        prompt = (
            f"Case Type: {case_type}\nRole/Perspective: {role}\n\n"
            f"Evidence/Statement:\n---\n{text}\n---\n\n"
            "Return ONLY valid JSON:\n"
            "{\n"
            '  "key_facts":[],"key_admissions":[],\n'
            '  "contradictions":[{"issue":"","conflicting_texts":[],"why_it_matters":""}],\n'
            '  "missing_facts":[],"strong_points":[],"weak_points":[],\n'
            '  "follow_up_questions":[],"cross_examination_questions":[],"timeline_facts":[]\n'
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
