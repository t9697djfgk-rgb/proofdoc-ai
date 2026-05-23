import streamlit as st
import os
import json
from pathlib import Path

st.set_page_config(
    page_title="ProofDoc AI — Legal Grade",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .main-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 2rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    .main-header h1 { margin: 0 0 0.5rem 0; font-size: 2rem; }
    .main-header p  { margin: 0 0 0.25rem 0; opacity: 0.9; }
    .main-header small { opacity: 0.7; font-size: 0.8rem; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="main-header">
        <h1>⚖️ ProofDoc AI — Legal Grade</h1>
        <p>AI-powered document reconstruction · Confidence scoring · Legal formatting preservation</p>
        <small>🔐 Confidentiality-first · Files auto-deleted after session · Powered by Gemini 2.0 Flash</small>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Sidebar ────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configuration")

    api_key = None
    try:
        api_key = st.secrets["GOOGLE_API_KEY"]
        st.success("✅ API key loaded from secrets")
    except Exception:
        api_key = st.text_input(
            "Google API Key", type="password", placeholder="AIza..."
        )
        if api_key:
            st.success("✅ API key set")
        else:
            st.warning("Enter your Google API key to begin")

    st.divider()

    doc_type = st.selectbox(
        "Document Type",
        [
            "legal",
            "contract",
            "court_filing",
            "deed",
            "invoice",
            "report",
            "letter",
            "general",
        ],
        help="Helps Gemini understand the document context for better extraction",
    )

    st.divider()
    st.markdown("**🔐 Privacy Guarantee**")
    st.markdown("- Processed in memory only")
    st.markdown("- Not used for AI training")
    st.markdown("- Auto-deleted after session")
    st.markdown("- No data retained or stored")

# ── Tabs ───────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(
    ["📄 Reconstruct Document", "📚 Merge PDF Bundle", "📋 Audit Trail"]
)

# ── Tab 1 : Reconstruct ────────────────────────────────────────
with tab1:
    col_upload, col_opts = st.columns([1, 1])

    with col_upload:
        st.subheader("Upload Document")
        uploaded_file = st.file_uploader(
            "Drop your scanned document here",
            type=["pdf", "png", "jpg", "jpeg", "tiff", "bmp", "webp"],
            help="Supports scanned PDFs, photographed documents, and image files",
        )
        if uploaded_file:
            st.info(f"📄 **{uploaded_file.name}** ({uploaded_file.size / 1024:.1f} KB)")

    with col_opts:
        st.subheader("Options")
        show_raw = st.checkbox("Show detailed AI analysis", value=False)
        st.markdown("")
        process_btn = st.button(
            "🚀 Reconstruct Document",
            type="primary",
            disabled=not (uploaded_file and api_key),
        )

    if process_btn and uploaded_file and api_key:
        from utils.claude_processor import ClaudeDocumentProcessor
        from utils.document_builder import DocumentBuilder
        from utils.confidentiality import ConfidentialityManager

        conf_mgr = ConfidentialityManager()

        try:
            # Save to secure temp workspace
            temp_input = conf_mgr.secure_path(uploaded_file.name)
            with open(temp_input, "wb") as f:
                f.write(uploaded_file.getbuffer())
            conf_mgr.log_action("UPLOAD", uploaded_file.name)

            progress = st.progress(0, text="Initialising Gemini 2.0 Flash…")

            processor = ClaudeDocumentProcessor(api_key)
            pages_hint = "(multi-page — may take a moment)" if uploaded_file.name.lower().endswith(".pdf") else ""
            progress.progress(20, text=f"Analysing document {pages_hint}…")

            extracted = processor.process_document(temp_input, doc_type)
            conf_mgr.log_action(
                "PROCESS_COMPLETE", uploaded_file.name, extracted.get("avg_confidence")
            )

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

    # ── Results panel ──────────────────────────────────────────
    if st.session_state.get("last_extracted"):
        extracted = st.session_state.last_extracted

        st.divider()
        st.subheader("📊 Reconstruction Report")

        c1, c2, c3, c4 = st.columns(4)
        conf = extracted.get("avg_confidence", 0)
        c1.metric(
            "AI Confidence",
            f"{conf:.1f}%",
            delta="High" if conf >= 85 else "Review needed",
            delta_color="normal" if conf >= 85 else "inverse",
        )
        c2.metric("Pages Processed", extracted.get("total_pages", 0))
        c3.metric("Tables Found", len(extracted.get("tables", [])))
        c4.metric("Signatures", len(extracted.get("signatures", [])))

        legal = {k: v for k, v in extracted.get("legal_elements", {}).items() if v}
        if legal:
            st.subheader("⚖️ Legal Elements Detected")
            n_cols = min(3, len(legal))
            cols = st.columns(n_cols)
            for i, (key, values) in enumerate(legal.items()):
                preview = ", ".join(str(v) for v in values[:5])
                if len(values) > 5:
                    preview += f"… (+{len(values) - 5})"
                cols[i % n_cols].markdown(f"**{key.upper()}**\n\n{preview}")

        if extracted.get("warnings"):
            st.subheader("⚠️ Review Required")
            for w in extracted["warnings"]:
                st.warning(w)

        if show_raw:
            with st.expander("🔍 Full AI Analysis (JSON)"):
                # omit bulky page_results from display
                display = {k: v for k, v in extracted.items() if k != "page_results"}
                st.json(display)

        st.divider()
        output_path = st.session_state.get("last_output_path")
        if output_path and os.path.exists(output_path):
            with open(output_path, "rb") as f:
                st.download_button(
                    label="📥 Download Reconstructed Word Document",
                    data=f.read(),
                    file_name=st.session_state.last_output_name,
                    mime=(
                        "application/vnd.openxmlformats-officedocument"
                        ".wordprocessingml.document"
                    ),
                    type="primary",
                )

# ── Tab 2 : Merge PDFs ─────────────────────────────────────────
with tab2:
    st.subheader("📚 Court-Ready PDF Bundle")
    st.markdown(
        "Merge multiple PDFs into a professional legal bundle with bookmarks and document labels."
    )

    pdfs = st.file_uploader(
        "Upload PDFs to merge",
        type=["pdf"],
        accept_multiple_files=True,
        key="merge_pdfs",
    )

    if pdfs:
        st.info(f"📄 {len(pdfs)} file(s) ready")
        titles = []
        for i, pdf in enumerate(pdfs):
            title = st.text_input(
                f"Title for '{pdf.name}'",
                value=pdf.name.replace(".pdf", ""),
                key=f"merge_title_{i}",
            )
            titles.append(title)

        if len(pdfs) >= 1 and st.button("📚 Create Court Bundle", type="primary"):
            try:
                import PyPDF2
                from utils.confidentiality import ConfidentialityManager

                conf_mgr = ConfidentialityManager()
                merger = PyPDF2.PdfMerger()

                for pdf, title in zip(pdfs, titles):
                    path = conf_mgr.secure_path(pdf.name)
                    with open(path, "wb") as f:
                        f.write(pdf.getbuffer())
                    merger.append(path, outline_item=title)

                out_path = conf_mgr.secure_path("court_bundle.pdf")
                merger.write(out_path)
                merger.close()

                with open(out_path, "rb") as f:
                    st.download_button(
                        "📥 Download Court Bundle",
                        f.read(),
                        "court_bundle.pdf",
                        "application/pdf",
                        type="primary",
                    )
                st.success(f"✅ Bundle ready: {len(pdfs)} document(s) merged")
            except Exception as exc:
                st.error(f"Merge failed: {exc}")
    else:
        st.caption("Upload at least one PDF to start.")

# ── Tab 3 : Audit Trail ────────────────────────────────────────
with tab3:
    st.subheader("📋 Audit Trail")

    audit = st.session_state.get("last_audit")
    if audit:
        st.markdown("Legal-grade audit trail for document processing verification.")

        header = st.columns([2.5, 1.5, 2.5, 1])
        for col, label in zip(header, ["Timestamp", "Action", "File", "Confidence"]):
            col.markdown(f"**{label}**")
        st.divider()

        for entry in audit:
            row = st.columns([2.5, 1.5, 2.5, 1])
            row[0].text(entry.get("timestamp", "")[:19])
            row[1].text(entry.get("action", ""))
            row[2].text(entry.get("file", "")[:35])
            conf_val = entry.get("confidence")
            row[3].text(f"{conf_val:.1f}%" if conf_val else "—")

        st.divider()
        st.download_button(
            "📥 Download Audit Report (JSON)",
            json.dumps(audit, indent=2),
            "proofdoc_audit.json",
            "application/json",
        )
    else:
        st.info("No processing activity in this session yet.")
