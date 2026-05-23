import anthropic
import json
import re

_SYS = (
    "You are an experienced trial lawyer and forensic interviewer. Analyse witness statements critically. "
    "Identify inconsistencies, credibility issues, and areas for challenge. "
    "Generate targeted cross-examination questions that expose weaknesses."
)


def _parse(raw: str, fallback: dict) -> dict:
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
    return {**fallback, "_parse_error": True}


class WitnessStatementAnalyzer:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-opus-4-7"

    def analyze(self, statement: str, known_facts: str, case_type: str,
                 perspective: str, other_statements: str = "") -> dict:
        context = f"\nOther witness statements for comparison:\n{other_statements}" if other_statements.strip() else ""
        prompt = (
            f"Case Type: {case_type}\nPerspective: {perspective}\n\n"
            f"Witness Statement:\n---\n{statement[:8000]}\n---\n\n"
            f"Known Facts:\n{known_facts}{context}\n\n"
            "Return ONLY valid JSON:\n"
            "{\n"
            '  "witness_summary": "who this witness is and what they claim",\n'
            '  "credibility_score": 0,\n'
            '  "credibility_rating": "High | Medium | Low",\n'
            '  "credibility_assessment": "overall credibility analysis",\n'
            '  "key_claims": ["list of key factual claims made"],\n'
            '  "supported_by_facts": ["claims consistent with known facts"],\n'
            '  "inconsistent_with_facts": [\n'
            '    {"claim": "", "contradiction": "", "significance": "high | medium | low"}\n'
            "  ],\n"
            '  "internal_inconsistencies": [\n'
            '    {"text_1": "", "text_2": "", "issue": ""}\n'
            "  ],\n"
            '  "cross_statement_conflicts": [\n'
            '    {"this_statement": "", "other_statement": "", "conflict": ""}\n'
            "  ],\n"
            '  "gaps_and_omissions": ["notable absences from the statement"],\n'
            '  "possible_motives": ["potential motives affecting credibility"],\n'
            '  "strong_points": ["credible elements of the statement"],\n'
            '  "deposition_notes": ["key points to explore in deposition"]\n'
            "}"
        )
        response = self.client.messages.create(
            model=self.model,
            max_tokens=5120,
            system=[{"type": "text", "text": _SYS, "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": prompt}],
        )
        raw = next((b.text for b in response.content if b.type == "text"), "{}")
        fallback = {"witness_summary": "", "credibility_score": 0, "credibility_rating": "—",
                    "credibility_assessment": "", "key_claims": [], "inconsistent_with_facts": [],
                    "internal_inconsistencies": [], "gaps_and_omissions": [], "strong_points": []}
        return _parse(raw, fallback)


class CrossExamGenerator:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-opus-4-7"

    def generate(self, statement: str, weaknesses: str, objectives: str,
                 case_type: str, perspective: str) -> dict:
        prompt = (
            f"Case Type: {case_type}\nYour Role: {perspective}\n"
            f"Objectives: {objectives}\nKnown Weaknesses: {weaknesses}\n\n"
            f"Witness Statement:\n---\n{statement[:8000]}\n---\n\n"
            "Return ONLY valid JSON:\n"
            "{\n"
            '  "strategy_overview": "overall cross-examination strategy",\n'
            '  "question_sets": [\n'
            '    {\n'
            '      "topic": "topic heading (e.g. Credibility, Fact X, Motive)",\n'
            '      "objective": "what you aim to establish",\n'
            '      "questions": [\n'
            '        {\n'
            '          "question": "exact question text",\n'
            '          "type": "leading | open | clarification | challenge",\n'
            '          "expected_answer": "what you expect the witness to say",\n'
            '          "follow_up": "follow-up if they deny or deflect",\n'
            '          "purpose": "why this question matters"\n'
            "        }\n"
            "      ]\n"
            "    }\n"
            "  ],\n"
            '  "opening_question": "first question to set the tone",\n'
            '  "closing_question": "final question to end on",\n'
            '  "points_to_establish": ["key concessions or admissions to extract"],\n'
            '  "traps_to_avoid": ["common errors to avoid with this witness"]\n'
            "}"
        )
        response = self.client.messages.create(
            model=self.model,
            max_tokens=5120,
            system=[{"type": "text", "text": _SYS, "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": prompt}],
        )
        raw = next((b.text for b in response.content if b.type == "text"), "{}")
        fallback = {"strategy_overview": "", "question_sets": [], "opening_question": "",
                    "closing_question": "", "points_to_establish": [], "traps_to_avoid": []}
        return _parse(raw, fallback)
