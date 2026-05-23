import streamlit as st
import os
import json
from pathlib import Path

st.set_page_config(
    page_title="ProofDoc AI — Legal Platform",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.shared.styles import inject_css, disclaimer, confidentiality_notice, section
inject_css()

# Extra CSS only needed on the home page
st.markdown("""
<style>
.badge-conf-high { background:#dcfce7; color:#166534; border-radius:20px; padding:0.2rem 0.7rem; font-size:0.75rem; font-weight:600; }
.badge-conf-low  { background:#fef9c3; color:#854d0e; border-radius:20px; padding:0.2rem 0.7rem; font-size:0.75rem; font-weight:600; }
.home-tool-card {
    background: white; border: 1px solid #e2e8f0; border-radius: 12px;
    padding: 1rem; text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    margin-bottom: 0.5rem;
}
.home-tool-card .icon { font-size: 1.6rem; margin-bottom: 0.3rem; }
.home-tool-card h5 { margin: 0 0 0.2rem 0; color: #1e3a5f; font-size: 0.82rem; font-weight: 600; }
.home-tool-card p  { margin: 0; color: #64748b; font-size: 0.72rem; }
.suite-header {
    background: linear-gradient(90deg, #1e3a5f, #2d5f8e);
    color: white; border-radius: 10px; padding: 0.75rem 1.25rem;
    margin: 1.5rem 0 1rem 0; font-size: 1rem; font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

# ── Hero ──────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <h1>⚖️ ProofDoc AI</h1>
    <p class="sub">The complete legal AI platform for law firms · Powered by Claude Opus 4.7</p>
    <span class="badge">🔐 Confidentiality-first &nbsp;·&nbsp; 15 Legal AI Tools &nbsp;·&nbsp; Files auto-deleted after session</span>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    api_key = None
    try:
        api_key = st.secrets["ANTHROPIC_API_KEY"]
        st.success("✅ API key loaded")
    except Exception:
        api_key = st.text_input("Anthropic API Key", type="password", placeholder="sk-ant-...")
        if api_key:
            st.success("✅ API key set")
        else:
            st.warning("Enter your API key to begin")

    st.divider()
    doc_type = st.selectbox("Document Type", [
        "legal", "contract", "court_filing", "deed",
        "invoice", "report", "letter", "general",
    ], help="Helps Claude understand the document context (for reconstruction tool)")

    st.divider()
    st.markdown("**🔐 Privacy Guarantee**")
    for line in ["Processed in memory only", "Not used for AI training",
                 "Auto-deleted after session", "No data retained"]:
        st.markdown(f"- {line}")
    st.divider()
    st.caption("⚠️ This platform assists with legal drafting and review. It does not replace qualified legal advice.")

# ── Disclaimer ───────────────────────────────────────────────────
disclaimer()

# ── Legal AI Suite Dashboard ─────────────────────────────────────
st.markdown('<div class="suite-header">🧠 Legal AI Suite — Click any tool to open it</div>', unsafe_allow_html=True)

_tools = [
    ("01_Legal_English_Reviewer", "✍️", "Legal English Reviewer", "Grammar, style & legal clarity"),
    ("02_Contract_Risk_Checker", "⚠️", "Contract Risk Checker", "Identify risks & missing clauses"),
    ("03_Citation_Checker", "📚", "Citation Checker", "Validate legal citations"),
    ("04_Legal_Drafting_Assistant", "📝", "Drafting Assistant", "AI-powered contract drafting"),
    ("05_Clause_Library", "📖", "Clause Library", "Browse & manage standard clauses"),
    ("06_Document_Comparison", "🔍", "Document Comparison", "Track changes between versions"),
    ("07_Due_Diligence_Review", "🏢", "Due Diligence Review", "M&A and transaction review"),
    ("08_Client_Intake_Assistant", "👥", "Client Intake", "Structured matter intake"),
    ("09_Matter_Timeline_Generator", "📅", "Timeline Generator", "Extract chronological facts"),
    ("10_Evidence_Analyzer", "🧪", "Evidence Analyzer", "Analyse witness statements"),
    ("11_Compliance_Policy_Generator", "🛡️", "Policy Generator", "Draft compliance policies"),
    ("12_Legal_Memo_Generator", "📄", "Legal Memo", "Structured legal memoranda"),
    ("13_Court_Document_Checker", "🏛️", "Court Doc Checker", "Pre-filing document review"),
    ("14_Deadline_Obligation_Extractor", "⏰", "Deadline Extractor", "Extract deadlines & duties"),
]

rows = [_tools[i:i+7] for i in range(0, len(_tools), 7)]
for row in rows:
    cols = st.columns(len(row))
    for col, (page_file, icon, name, desc) in zip(cols, row):
        with col:
            st.markdown(
                f'<div class="home-tool-card"><div class="icon">{icon}</div>'
                f'<h5>{name}</h5><p>{desc}</p></div>',
                unsafe_allow_html=True,
            )
            st.page_link(
                f"pages/{page_file}.py",
                label="Open →",
                use_container_width=True,
            )

st.markdown("<br>", unsafe_allow_html=True)

# ── Document Processing Tools ─────────────────────────────────────
st.markdown('<div class="suite-header">📄 Document Processing Tools</div>', unsafe_allow_html=True)

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📄 PDF / Image → Word",
    "🔄 Word → PDF",
    "📚 Merge PDFs",
    "📋 Audit Trail",
    "✍️ Legal English Reviewer",
])


# ── helpers ──────────────────────────────────────────────────────
def render_doc_preview(extracted: dict) -> str:
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
            html += f"<div style='{style}font-size:0.8em;color:#94a3b8;border-top:1px solid #e2e8f0;padding-top:4px'>{text}</div>"
        elif btype == "numbered_list":
            html += f"<li style='{style}'>{text}</li>"
        else:
            fw = "bold" if fmt == "bold" else "normal"
            fi = "italic" if fmt == "italic" else "normal"
            html += f"<p style='{style}font-weight:{fw};font-style:{fi};margin:0.3rem 0'>{text}</p>"
    return html


# ── Tab 1 : Reconstruct ──────────────────────────────────────────
with tab1:
    confidentiality_notice()
    left, right = st.columns([1, 1], gap="large")

    with left:
        section("Upload Document")
        uploaded_file = st.file_uploader(
            "Drop your scanned PDF or image here",
            type=["pdf", "png", "jpg", "jpeg", "tiff", "bmp", "webp"],
            help="Supports scanned PDFs, photographed documents, and image files",
        )
        if uploaded_file:
            st.info(f"📄 **{uploaded_file.name}** &nbsp;·&nbsp; {uploaded_file.size / 1024:.1f} KB")

        show_raw = st.checkbox("Show raw JSON analysis", value=False)
        process_btn = st.button(
            "🚀 Reconstruct Document",
            type="primary",
            disabled=not (uploaded_file and api_key),
            use_container_width=True,
        )

    with right:
        section("Document Preview")
        preview_placeholder = st.empty()
        preview_placeholder.markdown(
            '<div class="doc-preview" style="color:#94a3b8;font-style:italic;text-align:center;padding-top:4rem">'
            '📄 Upload a document and click Reconstruct to see the preview here.'
            '</div>',
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
            pages_hint = "(multi-page)" if uploaded_file.name.lower().endswith(".pdf") else ""
            progress.progress(20, text=f"Analysing document {pages_hint}…")

            extracted = processor.process_document(temp_input, doc_type)
            conf_mgr.log_action("PROCESS_COMPLETE", uploaded_file.name, extracted.get("avg_confidence"))

            progress.progress(75, text="Building Word document…")
            builder = DocumentBuilder()
            output_name = Path(uploaded_file.name).stem + "_reconstructed.docx"
            output_path = conf_mgr.secure_path(output_name)
            builder.build_word_document(extracted, uploaded_file.name, output_path)
            conf_mgr.log_action("BUILD_WORD", output_name)

            progress.progress(100, text="Done!")

            st.session_state.last_extracted = extracted
            st.session_state.last_output_path = output_path
            st.session_state.last_output_name = output_name
            st.session_state.last_audit = conf_mgr.get_audit_report()
            st.success("✅ Reconstruction complete!")

        except Exception as exc:
            st.error(f"Processing failed: {exc}")
            st.exception(exc)

    if st.session_state.get("last_extracted"):
        extracted = st.session_state.last_extracted
        preview_html = render_doc_preview(extracted)
        preview_placeholder.markdown(
            f'<div class="doc-preview">{preview_html}</div>',
            unsafe_allow_html=True,
        )

        st.divider()
        section("📊 Reconstruction Report")

        conf = extracted.get("avg_confidence", 0)
        m1, m2, m3, m4 = st.columns(4)
        m1.markdown(f'<div class="metric-card"><div class="val">{conf:.0f}%</div><div class="lbl">AI Confidence</div></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="metric-card"><div class="val">{extracted.get("total_pages", 0)}</div><div class="lbl">Pages</div></div>', unsafe_allow_html=True)
        m3.markdown(f'<div class="metric-card"><div class="val">{len(extracted.get("tables", []))}</div><div class="lbl">Tables</div></div>', unsafe_allow_html=True)
        m4.markdown(f'<div class="metric-card"><div class="val">{len(extracted.get("signatures", []))}</div><div class="lbl">Signatures</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        dtype = extracted.get("document_type", "unknown")
        st.markdown(f'<span class="badge-doc">📄 {dtype.replace("_", " ").title()}</span>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        legal = {k: v for k, v in extracted.get("legal_elements", {}).items() if v}
        if legal:
            section("⚖️ Legal Elements")
            cols = st.columns(min(3, len(legal)))
            for i, (key, values) in enumerate(legal.items()):
                preview = ", ".join(str(v) for v in values[:4])
                if len(values) > 4:
                    preview += f" (+{len(values)-4})"
                cols[i % 3].markdown(f"**{key.upper()}**\n\n{preview}")

        if extracted.get("warnings"):
            for w in extracted["warnings"]:
                st.warning(w)

        if show_raw:
            with st.expander("🔍 Full JSON Analysis"):
                st.json({k: v for k, v in extracted.items() if k != "page_results"})

        st.divider()
        section("⬇️ Download")
        dl1, dl2 = st.columns(2)

        output_path = st.session_state.get("last_output_path")
        if output_path and os.path.exists(output_path):
            with open(output_path, "rb") as f:
                dl1.download_button(
                    "📥 Download Word Document (.docx)",
                    data=f.read(),
                    file_name=st.session_state.last_output_name,
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                )
            try:
                from utils.word_to_pdf import convert_word_to_pdf
                from utils.confidentiality import ConfidentialityManager
                pdf_name = Path(st.session_state.last_output_name).stem + ".pdf"
                _cm = ConfidentialityManager()
                pdf_out = _cm.secure_path(pdf_name)
                convert_word_to_pdf(output_path, pdf_out)
                with open(pdf_out, "rb") as pf:
                    dl2.download_button(
                        "📥 Download as PDF",
                        data=pf.read(),
                        file_name=pdf_name,
                        mime="application/pdf",
                        use_container_width=True,
                    )
            except Exception:
                pass


# ── Tab 2 : Word → PDF ───────────────────────────────────────────
with tab2:
    section("🔄 Convert Word Document to PDF")
    st.markdown("Upload any `.docx` file and download a clean, formatted PDF instantly.")

    wl, wr = st.columns([1, 1], gap="large")
    with wl:
        word_file = st.file_uploader(
            "Upload Word Document (.docx)",
            type=["docx"],
            key="word_upload",
        )
        if word_file:
            st.info(f"📝 **{word_file.name}** &nbsp;·&nbsp; {word_file.size / 1024:.1f} KB")
            convert_btn = st.button("🔄 Convert to PDF", type="primary", use_container_width=True)
            if convert_btn:
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
                    st.success("✅ Conversion complete!")
                except Exception as exc:
                    st.error(f"Conversion failed: {exc}")

    with wr:
        section("Download")
        if st.session_state.get("w2p_pdf_path") and os.path.exists(st.session_state.w2p_pdf_path):
            with open(st.session_state.w2p_pdf_path, "rb") as f:
                st.download_button(
                    "📥 Download PDF",
                    data=f.read(),
                    file_name=st.session_state.w2p_pdf_name,
                    mime="application/pdf",
                    use_container_width=True,
                )
            st.markdown(f"**File:** {st.session_state.w2p_pdf_name}")
        else:
            st.markdown(
                '<div style="color:#94a3b8;font-style:italic;padding:2rem;text-align:center;'
                'border:1px dashed #e2e8f0;border-radius:12px">'
                '📄 Your converted PDF will appear here.'
                '</div>',
                unsafe_allow_html=True,
            )


# ── Tab 3 : Merge PDFs ───────────────────────────────────────────
with tab3:
    section("📚 Merge PDFs into a Court Bundle")
    st.markdown("Upload multiple PDFs, assign titles, and download a single merged document.")

    pdfs = st.file_uploader(
        "Upload PDFs to merge",
        type=["pdf"],
        accept_multiple_files=True,
        key="merge_pdfs",
    )

    if pdfs:
        st.info(f"📄 {len(pdfs)} file(s) ready to merge")
        titles = []
        cols = st.columns(2)
        for i, pdf in enumerate(pdfs):
            title = cols[i % 2].text_input(
                f"Title for '{pdf.name}'",
                value=pdf.name.replace(".pdf", ""),
                key=f"merge_title_{i}",
            )
            titles.append(title)
        st.markdown("")
        if st.button("📚 Merge & Download Bundle", type="primary", use_container_width=False):
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
                    st.download_button(
                        "📥 Download Court Bundle",
                        f.read(),
                        "court_bundle.pdf",
                        "application/pdf",
                        use_container_width=False,
                    )
                st.success(f"✅ Bundle ready: {len(pdfs)} document(s) merged")
            except Exception as exc:
                st.error(f"Merge failed: {exc}")
    else:
        st.markdown(
            '<div style="color:#94a3b8;font-style:italic;padding:2rem;text-align:center;'
            'border:1px dashed #e2e8f0;border-radius:12px;margin-top:1rem">'
            '📚 Upload at least one PDF to get started.'
            '</div>',
            unsafe_allow_html=True,
        )


# ── Tab 4 : Audit Trail ──────────────────────────────────────────
with tab4:
    section("📋 Audit Trail")
    audit = st.session_state.get("last_audit")
    if audit:
        st.markdown("Legal-grade processing log for verification and compliance.")
        header = st.columns([2.5, 1.5, 2.5, 1])
        for col, lbl in zip(header, ["Timestamp", "Action", "File", "Confidence"]):
            col.markdown(f"**{lbl}**")
        st.divider()
        for entry in audit:
            row = st.columns([2.5, 1.5, 2.5, 1])
            row[0].text(entry.get("timestamp", "")[:19])
            row[1].text(entry.get("action", ""))
            row[2].text(entry.get("file", "")[:35])
            cv = entry.get("confidence")
            row[3].text(f"{cv:.1f}%" if cv else "—")
        st.divider()
        st.download_button(
            "📥 Download Audit Report (JSON)",
            json.dumps(audit, indent=2),
            "proofdoc_audit.json",
            "application/json",
        )
    else:
        st.markdown(
            '<div style="color:#94a3b8;font-style:italic;padding:2rem;text-align:center;'
            'border:1px dashed #e2e8f0;border-radius:12px">'
            '📋 No processing activity in this session yet.'
            '</div>',
            unsafe_allow_html=True,
        )


# ── Tab 5 : Legal English Reviewer ──────────────────────────────
with tab5:
    section("✍️ Legal English Reviewer")
    st.markdown(
        "Upload or paste your legal document. The AI will review grammar, style, "
        "legal clarity, and flag any edits that may affect legal meaning."
    )
    disclaimer()

    inp_left, inp_right = st.columns([1, 1], gap="large")
    with inp_left:
        st.markdown("**📎 Upload Document** (DOCX, PDF, or TXT)")
        review_file = st.file_uploader(
            "Upload a legal document",
            type=["docx", "pdf", "txt"],
            key="review_upload",
            label_visibility="collapsed",
        )
        if review_file:
            st.info(f"📄 **{review_file.name}** · {review_file.size / 1024:.1f} KB")

    with inp_right:
        st.markdown("**✏️ Or Paste Text**")
        pasted_text = st.text_area(
            "Paste legal text here",
            height=180,
            placeholder="Paste your contract, clause, or legal document here…",
            key="review_paste",
            label_visibility="collapsed",
        )

    st.markdown("<br>", unsafe_allow_html=True)
    opt1, opt2 = st.columns(2)
    with opt1:
        review_type = st.selectbox("Review Type", [
            "Legal English polish", "Grammar only", "Contract drafting review",
            "Academic legal writing", "Court submission review", "Plain-English rewrite",
        ])
    with opt2:
        legal_style = st.selectbox("Legal Style", [
            "UK legal English", "US legal English",
            "International legal English", "Academic legal English",
        ])

    review_btn = st.button(
        "🔍 Review Document",
        type="primary",
        disabled=not api_key,
        use_container_width=False,
    )

    if review_btn:
        from utils.legal_reviewer import LegalReviewer, _extract_text_from_file
        input_text = ""
        if review_file:
            try:
                input_text = _extract_text_from_file(review_file.read(), review_file.name)
            except Exception as exc:
                st.error(f"Could not read file: {exc}")
        elif pasted_text.strip():
            input_text = pasted_text.strip()

        if not input_text:
            st.warning("⚠️ Please upload a document or paste text before submitting.")
        elif not api_key:
            st.warning("⚠️ Enter your Anthropic API key in the sidebar.")
        else:
            with st.spinner("Reviewing document with Claude Opus 4.7…"):
                try:
                    reviewer = LegalReviewer(api_key)
                    result = reviewer.review(input_text, review_type, legal_style)
                    st.session_state.review_result = result
                    st.session_state.review_input_text = input_text
                    if result.get("_parse_error"):
                        st.warning("⚠️ AI response could not be fully parsed. Showing partial results.")
                    else:
                        st.success("✅ Review complete!")
                except Exception as exc:
                    st.error(f"Review failed: {exc}")
                    st.exception(exc)

    if st.session_state.get("review_result"):
        result = st.session_state.review_result
        summary = result.get("summary", {})
        edits = result.get("edits", [])
        revised = result.get("revised_document", "")

        st.divider()
        section("📊 Review Summary")

        s1, s2, s3, s4, s5 = st.columns(5)
        s1.markdown(f'<div class="metric-card"><div class="val">{summary.get("total_issues", 0)}</div><div class="lbl">Total Issues</div></div>', unsafe_allow_html=True)
        s2.markdown(f'<div class="metric-card"><div class="val">{summary.get("grammar_issues", 0)}</div><div class="lbl">Grammar</div></div>', unsafe_allow_html=True)
        s3.markdown(f'<div class="metric-card"><div class="val">{summary.get("style_issues", 0)}</div><div class="lbl">Style</div></div>', unsafe_allow_html=True)
        s4.markdown(f'<div class="metric-card"><div class="val">{summary.get("legal_clarity_issues", 0)}</div><div class="lbl">Legal Clarity</div></div>', unsafe_allow_html=True)
        s5.markdown(f'<div class="metric-card"><div class="val" style="color:#dc2626">{summary.get("high_risk_edits", 0)}</div><div class="lbl">High Risk Edits</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        if edits:
            section("📝 Suggested Edits")
            hcols = st.columns([2.5, 2.5, 1.5, 1, 3])
            for col, lbl in zip(hcols, ["Original Text", "Suggested Correction", "Issue Type", "Risk", "Explanation"]):
                col.markdown(f"**{lbl}**")
            st.divider()
            for edit in edits:
                risk = edit.get("risk_level", "low").lower()
                risk_cls = {"high": "risk-high", "medium": "risk-medium"}.get(risk, "risk-low")
                issue = edit.get("issue_type", "").replace("_", " ").title()
                row = st.columns([2.5, 2.5, 1.5, 1, 3])
                row[0].markdown(f'<span style="color:#64748b">{edit.get("original_text", "")}</span>', unsafe_allow_html=True)
                row[1].markdown(f'**{edit.get("suggested_correction", "")}**')
                row[2].markdown(f'<span class="issue-badge">{issue}</span>', unsafe_allow_html=True)
                row[3].markdown(f'<span class="{risk_cls}">{risk.title()}</span>', unsafe_allow_html=True)
                row[4].markdown(edit.get("explanation", ""))
                st.markdown('<hr style="margin:0.3rem 0;border-color:#f1f5f9">', unsafe_allow_html=True)
        else:
            st.info("No specific edits suggested — the document looks good!")

        if revised:
            st.markdown("<br>", unsafe_allow_html=True)
            section("📄 Clean Revised Version")
            st.markdown(
                f'<div class="revised-doc">{revised.replace(chr(10), "<br>")}</div>',
                unsafe_allow_html=True,
            )

            st.markdown("<br>", unsafe_allow_html=True)
            dl1, dl2, dl3, dl4 = st.columns(4)

            dl1.download_button(
                "📥 Download Revised (.txt)",
                data=revised,
                file_name="revised_document.txt",
                mime="text/plain",
                use_container_width=True,
            )

            issue_report = {
                "review_type": review_type,
                "legal_style": legal_style,
                "summary": summary,
                "edits": edits,
            }
            dl2.download_button(
                "📊 Export Issue Report (.json)",
                data=json.dumps(issue_report, indent=2),
                file_name="legal_review_report.json",
                mime="application/json",
                use_container_width=True,
            )

            try:
                import tempfile, os as _os
                from docx import Document as _Doc
                _tmp = tempfile.NamedTemporaryFile(suffix=".docx", delete=False)
                _tmp.close()
                _doc = _Doc()
                for line in revised.split("\n"):
                    _doc.add_paragraph(line)
                _doc.save(_tmp.name)
                with open(_tmp.name, "rb") as _f:
                    dl3.download_button(
                        "📝 Download as Word (.docx)",
                        data=_f.read(),
                        file_name="revised_document.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        use_container_width=True,
                    )
                _os.unlink(_tmp.name)
            except Exception:
                pass

            if dl4.button("🔄 Reset Review", use_container_width=True):
                for key in ("review_result", "review_input_text"):
                    st.session_state.pop(key, None)
                st.rerun()
