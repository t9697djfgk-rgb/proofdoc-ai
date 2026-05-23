import anthropic
import json
import re

_SYS = (
    "You are a highly experienced legal researcher. Provide accurate, well-structured legal research. "
    "Always note that your response is AI-generated and should be verified against primary sources. "
    "Cite authorities where possible but do not fabricate case names or statutes."
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
    return {**fallback, "_parse_error": True, "_raw": raw[:500]}


def _call(client, prompt: str, max_tokens: int = 4096) -> str:
    response = client.messages.create(
        model="claude-opus-4-7",
        max_tokens=max_tokens,
        system=[{"type": "text", "text": _SYS, "cache_control": {"type": "ephemeral"}}],
        messages=[{"role": "user", "content": prompt}],
    )
    return next((b.text for b in response.content if b.type == "text"), "{}")


class LegalResearchAssistant:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    def research(self, question: str, jurisdiction: str, area_of_law: str) -> dict:
        prompt = (
            f"Legal Question: {question}\n"
            f"Jurisdiction: {jurisdiction}\n"
            f"Area of Law: {area_of_law}\n\n"
            "Return ONLY valid JSON:\n"
            "{\n"
            '  "answer": "structured plain-English answer",\n'
            '  "key_principles": ["list of key legal principles"],\n'
            '  "relevant_authorities": [\n'
            '    {"name": "case or statute name", "citation": "", "relevance": ""}\n'
            "  ],\n"
            '  "practical_implications": ["list of practical points"],\n'
            '  "areas_of_uncertainty": ["unsettled points of law"],\n'
            '  "further_research": ["suggested follow-up research areas"],\n'
            '  "disclaimer": "AI-generated — verify with primary sources"\n'
            "}"
        )
        raw = _call(self.client, prompt)
        result = _parse(raw, {"answer": "", "key_principles": [], "relevant_authorities": [],
                               "practical_implications": [], "areas_of_uncertainty": [],
                               "further_research": []})
        result.setdefault("disclaimer", "AI-generated — verify with primary sources")
        return result


class CaseSummarizer:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    def summarize(self, text: str, jurisdiction: str) -> dict:
        prompt = (
            f"Jurisdiction: {jurisdiction}\n\n"
            f"Case text:\n---\n{text[:12000]}\n---\n\n"
            "Return ONLY valid JSON:\n"
            "{\n"
            '  "case_name": "",\n'
            '  "citation": "",\n'
            '  "court": "",\n'
            '  "date": "",\n'
            '  "judges": "",\n'
            '  "parties": {"claimant": "", "defendant": ""},\n'
            '  "area_of_law": "",\n'
            '  "facts": "concise fact summary",\n'
            '  "issues": ["legal issues decided"],\n'
            '  "held": "decision and outcome",\n'
            '  "ratio_decidendi": "core binding principle",\n'
            '  "obiter_dicta": ["notable obiter statements"],\n'
            '  "key_principles": ["principles extracted"],\n'
            '  "significance": "why this case matters"\n'
            "}"
        )
        raw = _call(self.client, prompt)
        result = _parse(raw, {"case_name": "", "facts": "", "held": "", "ratio_decidendi": "",
                               "key_principles": [], "issues": []})
        return result


class StatuteExplainer:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    def explain(self, text: str, jurisdiction: str, audience: str) -> dict:
        prompt = (
            f"Jurisdiction: {jurisdiction}\nAudience: {audience}\n\n"
            f"Statute/Regulation:\n---\n{text[:12000]}\n---\n\n"
            "Return ONLY valid JSON:\n"
            "{\n"
            '  "title": "name of the legislation",\n'
            '  "purpose": "plain-English purpose statement",\n'
            '  "plain_english_summary": "accessible overview",\n'
            '  "key_provisions": [\n'
            '    {"section": "", "heading": "", "explanation": "", "importance": "high | medium | low"}\n'
            "  ],\n"
            '  "key_obligations": ["who must do what"],\n'
            '  "key_prohibitions": ["what is forbidden"],\n'
            '  "penalties": ["penalties for non-compliance"],\n'
            '  "exemptions": ["notable exemptions"],\n'
            '  "faqs": [\n'
            '    {"question": "", "answer": ""}\n'
            "  ]\n"
            "}"
        )
        raw = _call(self.client, prompt)
        result = _parse(raw, {"title": "", "purpose": "", "plain_english_summary": "",
                               "key_provisions": [], "key_obligations": [], "penalties": []})
        return result


class LegalTermChecker:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)

    def check(self, term: str, jurisdiction: str, area_of_law: str) -> dict:
        prompt = (
            f"Term: {term}\nJurisdiction: {jurisdiction}\nArea of Law: {area_of_law}\n\n"
            "Return ONLY valid JSON:\n"
            "{\n"
            '  "term": "",\n'
            '  "definition": "precise legal definition",\n'
            '  "plain_english": "simple explanation",\n'
            '  "correct_usage": "how to use it in drafting",\n'
            '  "common_mistakes": ["frequent misuses"],\n'
            '  "related_terms": [{"term": "", "relationship": ""}],\n'
            '  "jurisdiction_variations": [\n'
            '    {"jurisdiction": "", "equivalent_term": "", "difference": ""}\n'
            "  ],\n"
            '  "example_clause": "short example clause using the term"\n'
            "}"
        )
        raw = _call(self.client, prompt, max_tokens=2048)
        result = _parse(raw, {"term": term, "definition": "", "plain_english": "",
                               "correct_usage": "", "common_mistakes": [],
                               "related_terms": [], "jurisdiction_variations": []})
        return result
