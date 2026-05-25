import anthropic
from utils.shared.json_parser import safe_parse

# Call 1: document only — pure text, no parsing needed
_SYSTEM_DRAFT = (
    "You are a senior legal drafting assistant. Generate a professional first draft based only "
    "on the user's facts and instructions. Do not invent facts. Where information is missing, "
    "use [PLACEHOLDER] or list questions. Use precise legal English. "
    "Return ONLY the document text — no JSON, no metadata, no commentary. "
    "Start directly with the document title and body."
)

# Call 2: metadata only — small JSON, always reliable
_SYSTEM_META = (
    "You are a legal assistant. Analyse the draft and return ONLY valid JSON — no other text. "
    "JSON must have exactly these keys: "
    "assumptions (list of strings), "
    "missing_information (list of strings), "
    "risk_warnings (list of strings), "
    "optional_clauses (list of objects with clause_name, clause_text, when_to_use)."
)

_FALLBACK_META = {
    "assumptions": [],
    "missing_information": [],
    "risk_warnings": [],
    "optional_clauses": [],
}


class DraftingAssistant:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-opus-4-7"

    def draft(
        self,
        doc_type: str,
        jurisdiction: str,
        legal_style: str,
        parties: str,
        key_facts: str,
        tone: str,
        additional: str,
    ) -> dict:
        prompt = (
            f"Document Type: {doc_type}\n"
            f"Jurisdiction: {jurisdiction}\n"
            f"Legal Style: {legal_style}\n"
            f"Parties: {parties}\n"
            f"Key Facts: {key_facts}\n"
            f"Tone: {tone}\n"
            f"Additional Instructions: {additional}"
        )

        # ── Call 1: get the full document as plain text ──────────────
        doc_resp = self.client.messages.create(
            model=self.model,
            max_tokens=8192,
            system=[{"type": "text", "text": _SYSTEM_DRAFT,
                     "cache_control": {"type": "ephemeral"}}],
            messages=[{"role": "user", "content": prompt}],
        )
        draft_document = next(
            (b.text for b in doc_resp.content if b.type == "text"), ""
        )

        # Extract title from the first non-empty line
        lines = [ln.lstrip("#").strip() for ln in draft_document.splitlines() if ln.strip()]
        draft_title = lines[0] if lines else doc_type

        # ── Call 2: get metadata as small, simple JSON ───────────────
        meta_prompt = (
            f"Here is a {doc_type} draft (first 3000 chars):\n\n"
            f"{draft_document[:3000]}\n\n"
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
            "draft_title":        draft_title,
            "draft_document":     draft_document,
            "assumptions":        meta.get("assumptions", []),
            "missing_information": meta.get("missing_information", []),
            "risk_warnings":      meta.get("risk_warnings", []),
            "optional_clauses":   meta.get("optional_clauses", []),
        }
