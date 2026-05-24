"""Export / download utilities for legal tool results."""
from __future__ import annotations
import json
import streamlit as st


def download_txt(label: str, text: str, filename: str, key: str | None = None) -> None:
    st.download_button(
        label=label,
        data=text,
        file_name=filename,
        mime="text/plain",
        use_container_width=True,
        key=key,
    )


def download_json(label: str, data: dict | list, filename: str, key: str | None = None) -> None:
    st.download_button(
        label=label,
        data=json.dumps(data, indent=2, ensure_ascii=False),
        file_name=filename,
        mime="application/json",
        use_container_width=True,
        key=key,
    )


def download_md(label: str, text: str, filename: str, key: str | None = None) -> None:
    st.download_button(
        label=label,
        data=text,
        file_name=filename,
        mime="text/markdown",
        use_container_width=True,
        key=key,
    )


def download_docx(label: str, text: str, filename: str, key: str | None = None) -> None:
    """Create a minimal Word doc from plain text and offer it as a download."""
    import io
    from docx import Document
    doc = Document()
    for line in text.split("\n"):
        doc.add_paragraph(line)
    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    st.download_button(
        label=label,
        data=buf.read(),
        file_name=filename,
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        use_container_width=True,
        key=key,
    )


def download_pdf(label: str, text: str, filename: str, title: str = "", key: str | None = None) -> None:
    """Render plain text as a PDF using fpdf2 and offer it as a download."""
    import io, textwrap
    from fpdf import FPDF

    def _s(s: str) -> str:
        # fpdf2 built-in fonts only cover Latin-1; replace anything outside that range
        return s.encode("latin-1", errors="replace").decode("latin-1")

    _title = _s(title)

    class _PDF(FPDF):
        def header(self):
            if _title:
                self.set_font("Helvetica", "B", 13)
                self.cell(self.epw, 10, _title, align="C", new_x="LMARGIN", new_y="NEXT")
                self.ln(2)

    pdf = _PDF(orientation="P", unit="mm", format="A4")
    pdf.set_margins(20, 20, 20)
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    pdf.set_font("Helvetica", size=10)
    w = pdf.epw  # effective width: paper - left margin - right margin (170 mm for A4)

    for raw in text.split("\n"):
        line = _s(raw)
        stripped = line.strip()
        # Pre-wrap very long lines so a single token can never exceed the cell width
        chunks = textwrap.wrap(line, width=120) if len(line) > 120 else [line]
        for chunk in (chunks or [""]):
            try:
                if stripped.startswith("---") or stripped.startswith("==="):
                    pdf.set_draw_color(200, 168, 76)
                    pdf.line(pdf.l_margin, pdf.get_y(), pdf.l_margin + w, pdf.get_y())
                    pdf.ln(3)
                    break  # only draw the rule once per original line
                elif (stripped and stripped == stripped.upper()
                      and len(stripped) > 3
                      and all(c.isalpha() or c.isspace() for c in stripped)):
                    pdf.set_font("Helvetica", "B", 10)
                    pdf.multi_cell(w, 6, chunk)
                    pdf.set_font("Helvetica", size=10)
                else:
                    pdf.multi_cell(w, 5.5, chunk if chunk else " ")
            except Exception:
                pdf.ln(5.5)  # skip unrenderable chunk, preserve spacing

    buf = io.BytesIO(pdf.output())
    st.download_button(
        label=label,
        data=buf.read(),
        file_name=filename,
        mime="application/pdf",
        use_container_width=True,
        key=key,
    )


def action_row(
    text_to_download: str,
    base_filename: str,
    report_data: dict | list | None = None,
    reset_keys: list[str] | None = None,
    key_prefix: str = "",
) -> None:
    """
    Renders a standard 4-button action row:
    Download .txt | Export report .json | Download .docx | Reset
    """
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        download_txt("📥 Download (.txt)", text_to_download,
                     f"{base_filename}.txt", key=f"{key_prefix}_dl_txt")
    with c2:
        if report_data is not None:
            download_json("📊 Export Report (.json)", report_data,
                          f"{base_filename}_report.json", key=f"{key_prefix}_dl_json")
    with c3:
        download_docx("📝 Download (.docx)", text_to_download,
                      f"{base_filename}.docx", key=f"{key_prefix}_dl_docx")
    with c4:
        if st.button("🔄 Reset", use_container_width=True, key=f"{key_prefix}_reset"):
            if reset_keys:
                for k in reset_keys:
                    st.session_state.pop(k, None)
            st.rerun()
