import streamlit as st
from utils.shared.sidebar import setup_page
from utils.shared.styles import slim_header, disclaimer, section, risk_badge, placeholder_feature
from utils.shared.document_input import two_document_input_ui
from utils.shared.export_utils import download_json

api_key = setup_page()
slim_header("🗂️", "Manage & Compare", "Document comparison, version history, e-signature, and export")

tab_compare, tab_version, tab_esig, tab_export = st.tabs([
    "🔍 Document Comparison",
    "📂 Version History",
    "✍️ E-Signature",
    "📤 Export Center",
])

# ── Document Comparison (functional) ─────────────────────────────
with tab_compare:
    disclaimer()
    st.markdown("Upload two versions of a document. The AI will identify legally significant changes.")

    orig_text, rev_text = two_document_input_ui("dc")

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    doc_type = c1.selectbox("Document Type", [
        "Contract", "NDA", "Shareholder agreement", "Employment agreement",
        "Settlement", "Court pleading", "Policy document", "Other",
    ])
    client_position = c2.selectbox("Your Client's Position", [
        "Neutral review", "Buyer / Investor", "Seller / Target",
        "Claimant / Plaintiff", "Defendant",
    ])

    submit = st.button("🔍 Compare Documents", type="primary", disabled=not api_key)

    if submit:
        if not orig_text or not rev_text:
            st.warning("⚠️ Both documents are required for comparison.")
        else:
            from utils.document_comparison import DocumentComparison
            with st.spinner("Comparing with Claude Opus 4.7…"):
                try:
                    result = DocumentComparison(api_key).compare(orig_text, rev_text, doc_type, client_position)
                    st.session_state.dc_result = result
                    st.success("✅ Comparison complete!")
                except Exception as exc:
                    st.error(f"Comparison failed: {exc}")

    if st.session_state.get("dc_result"):
        result = st.session_state.dc_result
        changes = result.get("changes", [])
        significant = result.get("significant_changes", [])

        st.divider()
        m1, m2, m3 = st.columns(3)
        m1.markdown(f'<div class="metric-card"><div class="val">{len(changes)}</div><div class="lbl">Total Changes</div></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="metric-card"><div class="val" style="color:#dc2626">{len(significant)}</div><div class="lbl">High-Impact Changes</div></div>', unsafe_allow_html=True)
        m3.markdown(f'<div class="metric-card"><div class="val">{result.get("net_effect","—")}</div><div class="lbl">Net Effect</div></div>', unsafe_allow_html=True)

        st.markdown(f"<br>**Summary:** {result.get('summary','')}", unsafe_allow_html=True)

        if changes:
            st.markdown("<br>", unsafe_allow_html=True)
            section(f"📋 Changes ({len(changes)})")
            hdr = st.columns([1, 3, 3, 2, 1])
            for col, lbl in zip(hdr, ["Type", "Original", "Revised", "Legal Significance", "Impact"]):
                col.markdown(f"**{lbl}**")
            st.divider()
            for ch in changes:
                row = st.columns([1, 3, 3, 2, 1])
                row[0].markdown(f"`{ch.get('change_type','')}`")
                row[1].markdown(f'<span style="color:#dc2626">{ch.get("original_text","")}</span>', unsafe_allow_html=True)
                row[2].markdown(f'<span style="color:#16a34a">{ch.get("revised_text","")}</span>', unsafe_allow_html=True)
                row[3].markdown(ch.get("legal_significance", ""))
                row[4].markdown(risk_badge(ch.get("impact_level", "low")), unsafe_allow_html=True)
                st.markdown('<hr style="margin:0.25rem 0;border-color:#f1f5f9">', unsafe_allow_html=True)

        if significant:
            st.markdown("<br>", unsafe_allow_html=True)
            section("🚨 High-Impact Changes")
            for s in significant:
                st.error(s)

        st.markdown("<br>", unsafe_allow_html=True)
        c1, _, c3 = st.columns(3)
        with c1:
            download_json("📥 Download Comparison Report (.json)", result, "comparison_report.json", key="dc_dl")
        with c3:
            if st.button("🔄 Reset", use_container_width=True, key="dc_reset"):
                st.session_state.pop("dc_result", None)
                st.rerun()

# ── Version History (placeholder) ────────────────────────────────
with tab_version:
    placeholder_feature(
        "📂", "Version History",
        "Track all versions of a document with timestamps, author info, and change summaries.",
        ["View full version timeline", "Compare any two versions side-by-side",
         "Restore an earlier version", "Tag versions (draft, reviewed, final, executed)"],
        ["Version timeline per document", "Side-by-side diff view", "Restored version download"],
    )

# ── E-Signature (placeholder) ────────────────────────────────────
with tab_esig:
    placeholder_feature(
        "✍️", "E-Signature",
        "Send documents for legally binding electronic signature from within ProofDoc AI.",
        ["Upload document and add signature fields", "Send to one or multiple signatories",
         "Track signature status in real time", "Download fully signed and certified copy"],
        ["Signature-ready document", "Email notification to signatories",
         "Signed PDF with certificate", "Audit trail of signing events"],
    )

# ── Export Center (placeholder) ───────────────────────────────────
with tab_export:
    placeholder_feature(
        "📤", "Export Center",
        "Bulk export documents in multiple formats with custom naming and folder structure.",
        ["Batch export documents to PDF, Word, or ZIP",
         "Apply consistent naming convention", "Export with matter reference prefixes",
         "Schedule recurring exports"],
        ["Bulk download ZIP", "Export manifest (list of files)", "Custom naming applied"],
    )
