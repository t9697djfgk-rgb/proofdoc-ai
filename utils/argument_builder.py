import anthropic
import json
import re

_SYS = (
    "You are a specialist appellate and trial barrister. Build precise, well-structured legal arguments "
    "using IRAC (Issue, Rule, Application, Conclusion) and CREAC frameworks. "
    "Anticipate counterarguments. Cite authorities accurately without fabrication."
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


class ArgumentBuilder:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-opus-4-7"

    def build(self, issue: str, facts: str, desired_outcome: str,
              framework: str, jurisdiction: str, case_type: str) -> dict:
        prompt = (
            f"Legal Issue: {issue}\n"
            f"Key Facts: {facts}\n"
            f"Desired Outcome: {desired_outcome}\n"
            f"Argument Framework: {framework}\n"
            f"Jurisdiction: {jurisdiction}\n"
            f"Case Type: {case_type}\n\n"
            "Build a complete legal argument and return ONLY valid JSON:\n"
            "{\n"
            '  "argument_title": "concise title for this argument",\n'
            '  "structured_argument": {\n'
            '    "issue": "precise legal issue statement",\n'
            '    "rule": "applicable legal rule(s) and authorities",\n'
            '    "application": "detailed application of rule to facts",\n'
            '    "conclusion": "clear conclusion"\n'
            "  },\n"
            '  "key_authorities": [\n'
            '    {"name": "", "citation": "", "principle": "", "how_it_helps": ""}\n'
            "  ],\n"
            '  "sub_arguments": [\n'
            '    {"point": "", "rule": "", "application": "", "authority": ""}\n'
            "  ],\n"
            '  "counterarguments": [\n'
            '    {"counterargument": "", "rebuttal": "", "strength": "strong | moderate | weak"}\n'
            "  ],\n"
            '  "weaknesses": ["honest assessment of weaknesses in this argument"],\n'
            '  "oral_advocacy_points": ["key points for oral argument — short, punchy"],\n'
            '  "full_written_argument": "complete submission-ready argument text"\n'
            "}"
        )
        response = self.client.messages.create(
            model=self.model,
            max_tokens=6144,
            system=[{"type": "text", "text": _SYS, "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": prompt}],
        )
        raw = next((b.text for b in response.content if b.type == "text"), "{}")
        result = _parse(raw)
        result.setdefault("argument_title", "Legal Argument")
        result.setdefault("structured_argument", {})
        result.setdefault("key_authorities", [])
        result.setdefault("sub_arguments", [])
        result.setdefault("counterarguments", [])
        result.setdefault("weaknesses", [])
        result.setdefault("oral_advocacy_points", [])
        result.setdefault("full_written_argument", "")
        return result


class FilingChecklist:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-opus-4-7"

    def generate(self, doc_type: str, court: str, jurisdiction: str, matter_summary: str) -> dict:
        prompt = (
            f"Document Type: {doc_type}\n"
            f"Court: {court}\n"
            f"Jurisdiction: {jurisdiction}\n"
            f"Matter Summary: {matter_summary}\n\n"
            "Generate a detailed court filing checklist and return ONLY valid JSON:\n"
            "{\n"
            '  "title": "Filing Checklist title",\n'
            '  "court_overview": "brief overview of the court and relevant rules",\n'
            '  "checklist": [\n'
            '    {\n'
            '      "step": 1,\n'
            '      "category": "Document Preparation | Formatting | Filing | Service | Fee | Timing | Other",\n'
            '      "task": "what to do",\n'
            '      "details": "specific requirements",\n'
            '      "priority": "critical | important | standard",\n'
            '      "timing": "when to complete (e.g. before filing, on filing day)"\n'
            "    }\n"
            "  ],\n"
            '  "required_documents": ["list of required accompanying documents"],\n'
            '  "common_errors": ["frequently made filing errors to avoid"],\n'
            '  "court_fees": "general guidance on applicable fees",\n'
            '  "service_requirements": "how and on whom the document must be served"\n'
            "}"
        )
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=[{"type": "text", "text": _SYS, "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": prompt}],
        )
        raw = next((b.text for b in response.content if b.type == "text"), "{}")
        result = _parse(raw)
        result.setdefault("title", "Filing Checklist")
        result.setdefault("checklist", [])
        result.setdefault("required_documents", [])
        result.setdefault("common_errors", [])
        result.setdefault("court_fees", "")
        result.setdefault("service_requirements", "")
        return result


class HearingPrepGenerator:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-opus-4-7"

    def generate(self, matter_summary: str, key_issues: str, hearing_type: str,
                 judge_notes: str, jurisdiction: str) -> dict:
        prompt = (
            f"Matter Summary: {matter_summary}\n"
            f"Key Issues: {key_issues}\n"
            f"Hearing Type: {hearing_type}\n"
            f"Judge/Tribunal Notes: {judge_notes}\n"
            f"Jurisdiction: {jurisdiction}\n\n"
            "Generate structured hearing preparation notes. Return ONLY valid JSON:\n"
            "{\n"
            '  "hearing_overview": "brief overview of what this hearing is about and what you need to achieve",\n'
            '  "objectives": ["list of objectives for this hearing — ordered by priority"],\n'
            '  "opening_statement": "draft opening remarks (2-3 paragraphs)",\n'
            '  "key_arguments": [\n'
            '    {"argument": "", "supporting_authority": "", "evidence_reference": "", "anticipated_response": ""}\n'
            "  ],\n"
            '  "key_evidence": [\n'
            '    {"item": "", "significance": "", "location_in_bundle": ""}\n'
            "  ],\n"
            '  "anticipated_questions": [\n'
            '    {"question": "", "answer": ""}\n'
            "  ],\n"
            '  "concessions_to_make": ["points you can concede without harm"],\n'
            '  "lines_to_hold": ["points you must not concede"],\n'
            '  "closing_summary": "draft closing remarks",\n'
            '  "logistics_checklist": ["practical preparation items — documents, bundles, tech, etc."]\n'
            "}"
        )
        response = self.client.messages.create(
            model=self.model,
            max_tokens=6144,
            system=[{"type": "text", "text": _SYS, "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": prompt}],
        )
        raw = next((b.text for b in response.content if b.type == "text"), "{}")
        result = _parse(raw)
        result.setdefault("hearing_overview", "")
        result.setdefault("objectives", [])
        result.setdefault("opening_statement", "")
        result.setdefault("key_arguments", [])
        result.setdefault("anticipated_questions", [])
        result.setdefault("closing_summary", "")
        result.setdefault("logistics_checklist", [])
        return result
