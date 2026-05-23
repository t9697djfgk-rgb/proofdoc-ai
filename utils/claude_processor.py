import anthropic
import base64
import json
import re
import io
from PIL import Image


SYSTEM_PROMPT = """You are an expert legal document reconstruction specialist. \
Analyze scanned or photographed legal and business documents with extreme precision. \
Extract ALL content with exact formatting preserved. Identify legal structure, tables, \
signature blocks, and stamps. Always respond with valid JSON only — no markdown code fences, \
no explanation text outside the JSON object."""


class ClaudeDocumentProcessor:
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-opus-4-7"

    def _image_to_base64(self, image: Image.Image) -> str:
        if image.mode in ("RGBA", "LA", "P"):
            image = image.convert("RGB")
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG", quality=95)
        return base64.standard_b64encode(buffer.getvalue()).decode()

    def _extract_images(self, file_path: str) -> list:
        ext = file_path.lower().rsplit(".", 1)[-1]
        if ext == "pdf":
            import fitz  # PyMuPDF
            doc = fitz.open(file_path)
            images = []
            for page in doc:
                mat = fitz.Matrix(200 / 72, 200 / 72)
                pix = page.get_pixmap(matrix=mat)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                images.append(img)
            doc.close()
            return images
        return [Image.open(file_path)]

    def _analyze_page(
        self, image: Image.Image, page_num: int, total_pages: int, doc_type: str
    ) -> dict:
        img_b64 = self._image_to_base64(image)

        prompt = f"""Analyze page {page_num} of {total_pages} of this {doc_type} document.
Extract ALL content precisely and return ONLY this JSON (no other text):
{{
  "page_number": {page_num},
  "document_type": "contract|court_filing|deed|agreement|invoice|report|letter|other",
  "content_blocks": [
    {{
      "type": "heading|paragraph|table|signature_block|stamp|numbered_list|footer|header|address",
      "level": 1,
      "text": "exact text content",
      "formatting": "bold|italic|underline|normal",
      "alignment": "left|center|right|justify"
    }}
  ],
  "legal_elements": {{
    "articles": [],
    "sections": [],
    "clauses": [],
    "exhibits": [],
    "parties": [],
    "dates": [],
    "case_numbers": [],
    "reference_numbers": []
  }},
  "tables": [
    {{
      "headers": ["col1", "col2"],
      "rows": [["data1", "data2"]]
    }}
  ],
  "signature_blocks": [
    {{
      "position": "bottom|middle|top",
      "signatories": ["party names"],
      "has_stamp": false,
      "has_date_line": false
    }}
  ],
  "ocr_confidence": 85,
  "warnings": []
}}"""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=6144,
            system=[
                {
                    "type": "text",
                    "text": SYSTEM_PROMPT,
                    "cache_control": {"type": "ephemeral"},
                }
            ],
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": img_b64,
                            },
                        },
                        {"type": "text", "text": prompt},
                    ],
                }
            ],
        )

        text = next((b.text for b in response.content if b.type == "text"), "{}")

        try:
            text = text.strip()
            if text.startswith("```"):
                text = re.sub(r"^```(?:json)?\s*", "", text)
                text = re.sub(r"\s*```$", "", text)
            return json.loads(text)
        except json.JSONDecodeError:
            json_match = re.search(r"\{.*\}", text, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except Exception:
                    pass

        return {
            "page_number": page_num,
            "content_blocks": [
                {
                    "type": "paragraph",
                    "text": text,
                    "formatting": "normal",
                    "alignment": "left",
                    "level": 1,
                }
            ],
            "legal_elements": {},
            "tables": [],
            "signature_blocks": [],
            "ocr_confidence": 50,
            "warnings": ["JSON parse failed — raw text extracted"],
        }

    def process_document(self, file_path: str, doc_type: str = "legal") -> dict:
        images = self._extract_images(file_path)
        results = [
            self._analyze_page(img, i + 1, len(images), doc_type)
            for i, img in enumerate(images)
        ]
        return self._consolidate(results)

    def _consolidate(self, page_results: list) -> dict:
        all_blocks, all_tables, all_signatures = [], [], []
        all_legal: dict = {
            "articles": [], "sections": [], "clauses": [],
            "exhibits": [], "parties": [], "dates": [],
            "case_numbers": [], "reference_numbers": [],
        }
        warnings, doc_types, confidences = [], [], []

        for r in page_results:
            all_blocks.extend(r.get("content_blocks", []))
            all_tables.extend(r.get("tables", []))
            all_signatures.extend(r.get("signature_blocks", []))
            for key in all_legal:
                all_legal[key].extend(r.get("legal_elements", {}).get(key, []))
            warnings.extend(r.get("warnings", []))
            if r.get("document_type"):
                doc_types.append(r["document_type"])
            if r.get("ocr_confidence"):
                confidences.append(r["ocr_confidence"])

        for key in all_legal:
            all_legal[key] = list(dict.fromkeys(all_legal[key]))

        return {
            "total_pages": len(page_results),
            "document_type": doc_types[0] if doc_types else "unknown",
            "content_blocks": all_blocks,
            "tables": all_tables,
            "signatures": all_signatures,
            "legal_elements": all_legal,
            "avg_confidence": sum(confidences) / len(confidences) if confidences else 0,
            "warnings": list(dict.fromkeys(warnings)),
            "page_results": page_results,
        }
