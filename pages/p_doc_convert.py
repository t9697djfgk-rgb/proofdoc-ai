import streamlit as st
import os
import json
from pathlib import Path
from utils.shared.sidebar import setup_page
from utils.shared.styles import slim_header, confidentiality_notice, section

api_key = setup_page()
slim_header("🔄", "Convert & Process", "PDF to Word, Word to PDF, merge PDFs, and document reconstruction")
confidentiality_notice()

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📄 PDF / Image → Word",
    "🔄 Word → PDF",
    "📚 Merge PDFs",
    "✂️ Split PDF",
    "🗜️ Compress PDF",
])


# ── helpers ──────────────────────────────────────────────────────
def _render_doc_preview(extracted: dict) -> str:
    blocks = extracted.get("content_blocks", [])
    if not blocks:
        return "<p style='color:#64748b;font-style:italic'>No content blocks found.</p>"
    html = ""
    for b in blocks:
        text = b.get("text", "").replace("<", "&lt;").replace(">", "&gt;")
        btype = b.get("type", "paragraph")
        fmt = b.get("formatting", "normal")
        align = b.get("alignment", "left")
        lvl = min(b.get("level", 2), 6)
        style = f"text-align:{align};"
        if btype == "heading":
            html += f"<h{lvl} style='{style}color:#1e3a5f'>{text}</h{lvl}>"
        elif btype == "stamp":
            html += f"<div class='stamp'>{text}</div>"
        elif btype == "signature_block":
            html += f"<div class='sig-block'>✍️ {text}</div>"
        elif btype in ("header", "footer"):
            html += f"<div style='{style}font-size:0.8em;color:#94a3b8'>{text}</div>"
        else:
            fw = "bold" if fmt == "bold" else "normal"
            fi = "italic" if fmt == "italic" else "normal"
            html += f"<p style='{style}font-weight:{fw};font-style:{fi};margin:0.3rem 0'>{text}</p>"
    return html


# ── Tab 1: Reconstruct ───────────────────────────────────────────
with tab1:
    st.markdown("Use Claude Opus 4.7 vision to reconstruct scanned PDFs and images into editable Word documents.")
    left, right = st.columns(2, gap="large")

    with left:
        section("Upload Document")
        doc_type = st.selectbox("Document Type", [
            "legal", "contract", "court_filing", "deed", "invoice", "report", "letter", "general",
        ])
        uploaded_file = st.file_uploader(
            "Drop your scanned PDF or image",
            type=["pdf", "png", "jpg", "jpeg", "tiff", "bmp", "webp"],
        )
        if uploaded_file:
            st.info(f"📄 **{uploaded_file.name}** · {uploaded_file.size / 1024:.1f} KB")
        show_raw = st.checkbox("Show raw JSON", value=False)
        process_btn = st.button("🚀 Reconstruct Document", type="primary",
                                disabled=not (uploaded_file and api_key), use_container_width=True)

    with right:
        section("Document Preview")
        preview_ph = st.empty()
        preview_ph.markdown(
            '<div class="doc-preview" style="color:#94a3b8;font-style:italic;text-align:center;padding-top:4rem">'
            '📄 Upload and click Reconstruct to see a preview.</div>',
            unsafe_allow_html=True,
        )

    if process_btn and uploaded_file and api_key:
        from utils.claude_processor import ClaudeDocumentProcessor
        from utils.document_builder import DocumentBuilder
        from utils.confidentiality import ConfidentialityManager
        conf_mgr = ConfidentialityManager()
        try:
            temp_input = conf_mgr.secure_path(uploaded_file.name)
            with open(temp_input, "wb") as f:
                f.write(uploaded_file.getbuffer())
            conf_mgr.log_action("UPLOAD", uploaded_file.name)
            progress = st.progress(0, text="Initialising Claude Opus 4.7…")
            processor = ClaudeDocumentProcessor(api_key)
            progress.progress(20, text="Analysing document…")
            extracted = processor.process_document(temp_input, doc_type)
            conf_mgr.log_action("PROCESS_COMPLETE", uploaded_file.name, extracted.get("avg_confidence"))
            progress.progress(75, text="Building Word document…")
            builder = DocumentBuilder()
            output_name = Path(uploaded_file.name).stem + "_reconstructed.docx"
            output_path = conf_mgr.secure_path(output_name)
            builder.build_word_document(extracted, uploaded_file.name, output_path)
            conf_mgr.log_action("BUILD_WORD", output_name)
            progress.progress(100, text="Done!")
            st.session_state.conv_extracted = extracted
            st.session_state.conv_output_path = output_path
            st.session_state.conv_output_name = output_name
            st.session_state.last_audit = conf_mgr.get_audit_report()
            st.success("✅ Reconstruction complete!")
        except Exception as exc:
            st.error(f"Processing failed: {exc}")

    if st.session_state.get("conv_extracted"):
        extracted = st.session_state.conv_extracted
        preview_ph.markdown(
            f'<div class="doc-preview">{_render_doc_preview(extracted)}</div>',
            unsafe_allow_html=True,
        )
        st.divider()
        conf = extracted.get("avg_confidence", 0)
        m1, m2, m3, m4 = st.columns(4)
        m1.markdown(f'<div class="metric-card"><div class="val">{conf:.0f}%</div><div class="lbl">Confidence</div></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="metric-card"><div class="val">{extracted.get("total_pages", 0)}</div><div class="lbl">Pages</div></div>', unsafe_allow_html=True)
        m3.markdown(f'<div class="metric-card"><div class="val">{len(extracted.get("tables", []))}</div><div class="lbl">Tables</div></div>', unsafe_allow_html=True)
        m4.markdown(f'<div class="metric-card"><div class="val">{len(extracted.get("signatures", []))}</div><div class="lbl">Signatures</div></div>', unsafe_allow_html=True)
        if show_raw:
            with st.expander("🔍 Full JSON"):
                st.json({k: v for k, v in extracted.items() if k != "page_results"})
        st.divider()
        dl1, dl2 = st.columns(2)
        output_path = st.session_state.get("conv_output_path")
        if output_path and os.path.exists(output_path):
            with open(output_path, "rb") as f:
                dl1.download_button("📥 Download Word (.docx)", data=f.read(),
                    file_name=st.session_state.conv_output_name,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True)
            try:
                from utils.word_to_pdf import convert_word_to_pdf
                from utils.confidentiality import ConfidentialityManager as CM
                pdf_name = Path(st.session_state.conv_output_name).stem + ".pdf"
                pdf_out = CM().secure_path(pdf_name)
                convert_word_to_pdf(output_path, pdf_out)
                with open(pdf_out, "rb") as pf:
                    dl2.download_button("📥 Download as PDF", data=pf.read(),
                        file_name=pdf_name, mime="application/pdf", use_container_width=True)
            except Exception:
                pass


# ── Tab 2: Word → PDF ─────────────────────────────────────────────
with tab2:
    section("🔄 Convert Word Document to PDF")
    wl, wr = st.columns(2, gap="large")
    with wl:
        word_file = st.file_uploader("Upload Word Document (.docx)", type=["docx"], key="w2p_up")
        if word_file:
            st.info(f"📝 **{word_file.name}** · {word_file.size / 1024:.1f} KB")
            if st.button("🔄 Convert to PDF", type="primary", use_container_width=True, key="w2p_btn"):
                from utils.word_to_pdf import convert_word_to_pdf
                from utils.confidentiality import ConfidentialityManager
                try:
                    cm = ConfidentialityManager()
                    docx_path = cm.secure_path(word_file.name)
                    with open(docx_path, "wb") as f:
                        f.write(word_file.getbuffer())
                    pdf_name = Path(word_file.name).stem + ".pdf"
                    pdf_path = cm.secure_path(pdf_name)
                    with st.spinner("Converting…"):
                        convert_word_to_pdf(docx_path, pdf_path)
                    st.session_state.w2p_pdf_path = pdf_path
                    st.session_state.w2p_pdf_name = pdf_name
                    st.success("✅ Done!")
                except Exception as exc:
                    st.error(f"Failed: {exc}")
    with wr:
        section("Download")
        if st.session_state.get("w2p_pdf_path") and os.path.exists(st.session_state.w2p_pdf_path):
            with open(st.session_state.w2p_pdf_path, "rb") as f:
                st.download_button("📥 Download PDF", data=f.read(),
                    file_name=st.session_state.w2p_pdf_name, mime="application/pdf",
                    use_container_width=True)
        else:
            st.markdown('<div class="empty-list">Your PDF will appear here after conversion.</div>',
                        unsafe_allow_html=True)


# ── Tab 3: Merge PDFs ─────────────────────────────────────────────
with tab3:
    section("📚 Merge PDFs into a Court Bundle")
    pdfs = st.file_uploader("Upload PDFs to merge", type=["pdf"], accept_multiple_files=True, key="merge_up")
    if pdfs:
        st.info(f"📄 {len(pdfs)} file(s) ready")
        titles = []
        cols = st.columns(2)
        for i, pdf in enumerate(pdfs):
            title = cols[i % 2].text_input(f"Title for '{pdf.name}'",
                value=pdf.name.replace(".pdf", ""), key=f"mt_{i}")
            titles.append(title)
        if st.button("📚 Merge & Download Bundle", type="primary", key="merge_btn"):
            try:
                import PyPDF2
                from utils.confidentiality import ConfidentialityManager
                cm = ConfidentialityManager()
                merger = PyPDF2.PdfMerger()
                for pdf, title in zip(pdfs, titles):
                    path = cm.secure_path(pdf.name)
                    with open(path, "wb") as f:
                        f.write(pdf.getbuffer())
                    merger.append(path, outline_item=title)
                out_path = cm.secure_path("court_bundle.pdf")
                merger.write(out_path)
                merger.close()
                with open(out_path, "rb") as f:
                    st.download_button("📥 Download Court Bundle", f.read(),
                        "court_bundle.pdf", "application/pdf")
                st.success(f"✅ Bundle ready: {len(pdfs)} documents merged")
            except Exception as exc:
                st.error(f"Merge failed: {exc}")
    else:
        st.markdown('<div class="empty-list">Upload at least two PDFs to merge.</div>',
                    unsafe_allow_html=True)


# ── Tab 4: Split PDF (placeholder) ───────────────────────────────
with tab4:
    from utils.shared.styles import placeholder_feature
    placeholder_feature(
        "✂️", "Split PDF",
        "Extract specific pages or ranges from a PDF into separate files.",
        ["Select page ranges to extract", "Split by chapter or bookmark",
         "Batch extract multiple ranges", "Rename output files"],
        ["Individual PDF files per selected range", "Named output files", "Zip archive for bulk splits"],
    )


# ── Tab 5: Compress PDF (placeholder) ────────────────────────────
with tab5:
    from utils.shared.styles import placeholder_feature
    placeholder_feature(
        "🗜️", "Compress PDF",
        "Reduce PDF file size for email, upload, or court filing size limits.",
        ["Select compression level (light, medium, aggressive)",
         "Preview file size before download", "Batch compress multiple files"],
        ["Compressed PDF", "Size reduction report (before vs. after)"],
    )
