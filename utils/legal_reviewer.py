import anthropic
import json
import re


SYSTEM_PROMPT = (
    "You are a legal English editor. Review the document for grammar, spelling, "
    "punctuation, clarity, consistency, legal drafting style, and formal legal English. "
    "Do not change the legal meaning unless the user clearly asks you to. Flag any change "
    "that may affect rights, obligations, liability, deadlines, jurisdiction, remedies, "
    "conditions, exceptions, definitions, governing law, dispute resolution, or standards "
    "of proof. For every edit, provide the original text, revised text, issue type, risk "
    "level, and explanation. Preserve the original legal meaning. Do not invent facts. "
    "Do not add new obligations. Do not remove rights, duties, exceptions, conditions, or "
    "deadlines. Use the selected legal style."
)

_FALLBACK = {
    "summary": {
        "total_issues": 0,
        "grammar_issues": 0,
        "style_issues": 0,
        "legal_clarity_issues": 0,
        "high_risk_edits": 0,
    },
    "edits": [],
    "revised_document": "",
}


def _extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    ext = filename.lower().rsplit(".", 1)[-1]

    if ext == "txt":
        return file_bytes.decode("utf-8", errors="replace")

    if ext == "docx":
        import io
        from docx import Document
        doc = Document(io.BytesIO(file_bytes))
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())

    if ext == "pdf":
        import io
        import fitz
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        pages = [page.get_text() for page in doc]
        doc.close()
        return "\n\n".join(pages)

    raise ValueError(f"Unsupported file type: .{ext}")


def _parse_response(raw: str, original_text: str) -> dict:
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw.strip())

    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except Exception:
            pass

    fallback = dict(_FALLBACK)
    fallback["revised_document"] = original_text
    fallback["_parse_error"] = True
    return fallback


class LegalReviewer:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-opus-4-7"

    def review(self, text: str, review_type: str, legal_style: str) -> dict:
        prompt = (
            f"Review Type: {review_type}\n"
            f"Legal Style: {legal_style}\n\n"
            f"Document to review:\n---\n{text}\n---\n\n"
            "Return ONLY valid JSON in this exact format (no markdown, no explanation outside JSON):\n"
            "{\n"
            '  "summary": {\n'
            '    "total_issues": 0,\n'
            '    "grammar_issues": 0,\n'
            '    "style_issues": 0,\n'
            '    "legal_clarity_issues": 0,\n'
            '    "high_risk_edits": 0\n'
            "  },\n"
            '  "edits": [\n'
            "    {\n"
            '      "original_text": "",\n'
            '      "suggested_correction": "",\n'
            '      "issue_type": "grammar | spelling | punctuation | legal_style | clarity | consistency | possible_meaning_change",\n'
            '      "risk_level": "low | medium | high",\n'
            '      "explanation": ""\n'
            "    }\n"
            "  ],\n"
            '  "revised_document": ""\n'
            "}"
        )

        response = self.client.messages.create(
            model=self.model,
            max_tokens=8192,
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[{"role": "user", "content": prompt}],
        )

        raw = next((b.text for b in response.content if b.type == "text"), "{}")
        result = _parse_response(raw, text)

        # Ensure required keys always exist
        result.setdefault("summary", dict(_FALLBACK["summary"]))
        result.setdefault("edits", [])
        result.setdefault("revised_document", text)
        for k in _FALLBACK["summary"]:
            result["summary"].setdefault(k, 0)

        return result
