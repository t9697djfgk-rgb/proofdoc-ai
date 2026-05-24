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
    import io
    from fpdf import FPDF

    def _s(s: str) -> str:
        """Strip characters outside Latin-1; fpdf2 built-in fonts don't support Unicode/emoji."""
        return s.encode("latin-1", errors="replace").decode("latin-1")

    class _PDF(FPDF):
        def header(self):
            if title:
                self.set_font("Helvetica", "B", 13)
                self.cell(0, 10, _s(title), align="C", new_x="LMARGIN", new_y="NEXT")
                self.ln(2)

    pdf = _PDF(orientation="P", unit="mm", format="A4")
    pdf.set_margins(20, 20, 20)
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()
    pdf.set_font("Helvetica", size=10)
    for raw in text.split("\n"):
        line = _s(raw)
        stripped = line.strip()
        if stripped.startswith("---") or stripped.startswith("==="):
            pdf.set_draw_color(200, 168, 76)
            pdf.line(20, pdf.get_y(), 190, pdf.get_y())
            pdf.ln(3)
        elif stripped and stripped == stripped.upper() and len(stripped) > 3 and stripped.replace(" ", "").isalpha():
            pdf.set_font("Helvetica", "B", 10)
            pdf.multi_cell(0, 6, line)
            pdf.set_font("Helvetica", size=10)
        else:
            pdf.multi_cell(0, 5.5, line if line else " ")
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
