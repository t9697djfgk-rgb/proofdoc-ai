import anthropic
import json
import re

_SYS = (
    "You are an expert legal translator with deep knowledge of legal terminology across multiple legal systems. "
    "Translate accurately preserving all legal meaning and technical terms. "
    "Note any terms that are difficult to translate directly."
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


class LegalTranslator:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-opus-4-7"

    def translate(self, text: str, source_lang: str, target_lang: str,
                  doc_type: str, formality: str) -> dict:
        prompt = (
            f"Source Language: {source_lang}\n"
            f"Target Language: {target_lang}\n"
            f"Document Type: {doc_type}\n"
            f"Formality: {formality}\n\n"
            f"Document to translate:\n---\n{text[:10000]}\n---\n\n"
            "Return ONLY valid JSON:\n"
            "{\n"
            '  "translated_text": "full translation",\n'
            '  "translator_notes": [\n'
            '    {"original_term": "", "translated_term": "", "note": "why this translation was chosen"}\n'
            "  ],\n"
            '  "untranslatable_terms": [\n'
            '    {"term": "", "explanation": "", "closest_equivalent": ""}\n'
            "  ],\n"
            '  "legal_system_differences": ["key differences between the two legal systems that affect the translation"]\n'
            "}"
        )
        response = self.client.messages.create(
            model=self.model,
            max_tokens=8192,
            system=[{"type": "text", "text": _SYS, "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": prompt}],
        )
        raw = next((b.text for b in response.content if b.type == "text"), "{}")
        result = _parse(raw, {"translated_text": "", "translator_notes": [],
                               "untranslatable_terms": [], "legal_system_differences": []})
        return result


class BilingualReviewer:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-opus-4-7"

    def review(self, original: str, translation: str, source_lang: str, target_lang: str) -> dict:
        prompt = (
            f"Source Language: {source_lang}\nTarget Language: {target_lang}\n\n"
            f"Original:\n---\n{original[:6000]}\n---\n\n"
            f"Translation:\n---\n{translation[:6000]}\n---\n\n"
            "Return ONLY valid JSON:\n"
            "{\n"
            '  "overall_accuracy": "Excellent | Good | Acceptable | Poor",\n'
            '  "summary": "overall assessment",\n'
            '  "discrepancies": [\n'
            '    {\n'
            '      "original_text": "",\n'
            '      "translated_text": "",\n'
            '      "issue": "description of the discrepancy",\n'
            '      "severity": "critical | high | medium | low",\n'
            '      "suggested_correction": ""\n'
            "    }\n"
            "  ],\n"
            '  "missing_content": ["content in original not present in translation"],\n'
            '  "added_content": ["content in translation not in original"]\n'
            "}"
        )
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            system=[{"type": "text", "text": _SYS, "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": prompt}],
        )
        raw = next((b.text for b in response.content if b.type == "text"), "{}")
        result = _parse(raw, {"overall_accuracy": "—", "summary": "", "discrepancies": [],
                               "missing_content": [], "added_content": []})
        return result
