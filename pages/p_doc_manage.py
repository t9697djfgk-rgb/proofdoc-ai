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

# ── Export Center ─────────────────────────────────────────────────
with tab_export:
    from utils.shared.styles import group_header, section
    import io as _io
    import zipfile as _zf
    import json as _json

    group_header("Export Center")
    st.markdown("Collect AI outputs and documents from this session and export them together.")

    # Collect all session AI results
    _RESULT_LABELS = {
        "ler_result":  ("✍️", "Legal English Review",        "ler_review"),
        "crc_result":  ("⚠️", "Contract Risk Check",         "contract_risk"),
        "cc_result":   ("📚", "Citation Check",              "citation_check"),
        "de_result":   ("⏰", "Deadline Extraction",         "deadlines"),
        "is_result":   ("🔍", "Legal Issue Spotter",         "issue_spotter"),
        "dda_result":  ("🏢", "Due Diligence Review",        "due_diligence"),
        "dca_result":  ("🔍", "Document Comparison",        "doc_comparison"),
        "cs_result":   ("📋", "Contract Summary",           "contract_summary"),
        "rr_result":   ("🚨", "Risk Report",                "risk_report"),
        "da_result":   ("📝", "Legal Draft",                "legal_draft"),
        "lm_result":   ("📄", "Legal Memo",                 "legal_memo"),
        "cp_result":   ("🛡️", "Compliance Policy",          "compliance_policy"),
        "cdc_result":  ("🏛️", "Court Document Check",       "court_doc_check"),
        "tg_result":   ("📅", "Matter Timeline",            "timeline"),
        "ea_result":   ("🧪", "Evidence Analysis",          "evidence_analysis"),
        "wa_result":   ("👤", "Witness Analysis",           "witness_analysis"),
        "ce_result":   ("❓", "Cross-Examination Plan",     "cross_examination"),
        "fc_result":   ("📋", "Filing Checklist",           "filing_checklist"),
        "ab_result":   ("💬", "Legal Argument",             "argument"),
        "hp_result":   ("📝", "Hearing Prep Notes",         "hearing_prep"),
        "lr_result":   ("🔬", "Legal Research",             "research"),
        "csum_result": ("📑", "Case Summary",               "case_summary"),
        "se_result":   ("📖", "Statute Explanation",        "statute_explanation"),
    }

    available = {k: v for k, v in _RESULT_LABELS.items() if st.session_state.get(k)}

    if not available:
        st.markdown(
            '<div class="empty-list">📭 No AI results in this session yet.<br>'
            '<small>Run any AI tool then return here to export.</small></div>',
            unsafe_allow_html=True,
        )
        st.page_link("pages/p_ai_review.py", label="Go to AI Review Tools →")
    else:
        section(f"📦 Available Exports ({len(available)} results)")
        selected_keys = []
        for k, (icon, label, _) in available.items():
            if st.checkbox(f"{icon} {label}", value=True, key=f"exp_{k}"):
                selected_keys.append(k)

        st.markdown("<br>", unsafe_allow_html=True)
        matter_ref = st.text_input("Matter Reference (for filename prefix)",
                                   placeholder="e.g. MAT-2026-0001", key="exp_ref")
        export_format = st.radio("Export Format", ["Individual JSON files (ZIP)",
                                                    "Single combined JSON"], horizontal=True)

        prefix = f"{matter_ref}_" if matter_ref.strip() else ""

        if st.button("📤 Export Selected", type="primary", disabled=not selected_keys, key="exp_btn"):
            if export_format == "Single combined JSON":
                combined = {}
                for k in selected_keys:
                    _, label, slug = _RESULT_LABELS[k]
                    combined[slug] = {"label": label, "data": st.session_state[k]}
                buf = _io.BytesIO(_json.dumps(combined, indent=2).encode())
                fname = f"{prefix}proofdoc_export.json"
                st.download_button("📥 Download Combined JSON", buf.getvalue(),
                                   fname, "application/json", key="exp_dl_combined")
                st.success(f"✅ {len(selected_keys)} results combined into {fname}")
            else:
                zip_buf = _io.BytesIO()
                with _zf.ZipFile(zip_buf, "w", _zf.ZIP_DEFLATED) as zf:
                    for k in selected_keys:
                        _, label, slug = _RESULT_LABELS[k]
                        data = _json.dumps(st.session_state[k], indent=2)
                        zf.writestr(f"{prefix}{slug}.json", data)
                fname = f"{prefix}proofdoc_export.zip"
                st.download_button("📥 Download ZIP", zip_buf.getvalue(),
                                   fname, "application/zip", key="exp_dl_zip")
                st.success(f"✅ {len(selected_keys)} files bundled into {fname}")

        # Audit log export
        audit = st.session_state.get("last_audit", [])
        if audit:
            st.divider()
            section("📋 Session Audit Log")
            st.caption(f"{len(audit)} entries — documents processed this session")
            audit_buf = _io.BytesIO(_json.dumps(audit, indent=2).encode())
            st.download_button("📥 Export Audit Log (.json)", audit_buf.getvalue(),
                               f"{prefix}audit_log.json", "application/json", key="exp_audit")
