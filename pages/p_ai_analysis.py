import streamlit as st
from utils.shared.sidebar import setup_page
from utils.shared.styles import slim_header, disclaimer, section, risk_badge, placeholder_feature
from utils.shared.document_input import document_input_ui, two_document_input_ui
from utils.shared.export_utils import download_json

api_key = setup_page()
slim_header("📊", "Analysis", "Contract summaries, due diligence, risk reports, and document comparison")
disclaimer()

tab1, tab2, tab3, tab4 = st.tabs([
    "🏢 Due Diligence Review",
    "🔍 Document Comparison",
    "📋 Contract Summary",
    "🚨 Risk Report Generator",
])

# ── 1. Due Diligence Review ───────────────────────────────────────
with tab1:
    from utils.shared.styles import confidentiality_notice
    confidentiality_notice()
    text1 = document_input_ui("dda", paste_placeholder="Paste due diligence document, SPA, or disclosure letter here…")
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    matter_type = c1.selectbox("Matter Type", [
        "M&A / Acquisition", "Joint venture", "Investment / Fundraising",
        "Real estate transaction", "Banking / Finance", "Commercial agreement", "Other",
    ], key="dda_mt")
    client_perspective = c2.selectbox("Client Perspective", [
        "Buyer / Investor", "Seller / Target", "Lender", "Borrower", "Neutral review",
    ], key="dda_cp")
    key_concerns = c3.text_input("Key Concerns", placeholder="e.g. IP, litigation, regulatory", key="dda_kc")
    if st.button("🏢 Run Due Diligence Review", type="primary", disabled=not api_key, key="dda_btn"):
        if not text1:
            st.warning("⚠️ Upload or paste a document first.")
        else:
            from utils.due_diligence import DueDiligenceReview
            with st.spinner("Reviewing with Claude Opus 4.7…"):
                try:
                    result1 = DueDiligenceReview(api_key).review(text1, matter_type, client_perspective, key_concerns)
                    st.session_state.dda_result = result1
                    st.success("✅ Review complete!")
                except Exception as exc:
                    st.error(f"Review failed: {exc}")
    if st.session_state.get("dda_result"):
        result1 = st.session_state.dda_result
        red_flags = result1.get("red_flags", [])
        mat = result1.get("matters_for_attention", [])
        st.divider()
        m1, m2, m3 = st.columns(3)
        m1.markdown(f'<div class="metric-card"><div class="val" style="color:#dc2626">{len(red_flags)}</div><div class="lbl">Red Flags</div></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="metric-card"><div class="val" style="color:#d97706">{len(mat)}</div><div class="lbl">Matters for Attention</div></div>', unsafe_allow_html=True)
        m3.markdown(f'<div class="metric-card"><div class="val">{result1.get("overall_risk","—")}</div><div class="lbl">Overall Risk</div></div>', unsafe_allow_html=True)
        st.markdown(f"**Executive Summary:** {result1.get('executive_summary','')}")
        if red_flags:
            st.markdown("<br>", unsafe_allow_html=True)
            section(f"🚨 Red Flags ({len(red_flags)})")
            for rf in red_flags:
                row = st.columns([1.5, 3, 2, 1.5, 1])
                row[0].markdown(rf.get("category",""))
                row[1].markdown(rf.get("issue",""))
                row[2].markdown(rf.get("implication",""))
                row[3].markdown(rf.get("recommendation",""))
                row[4].markdown(risk_badge(rf.get("severity","medium")), unsafe_allow_html=True)
                st.markdown('<hr style="margin:0.25rem 0;border-color:#f1f5f9">', unsafe_allow_html=True)
        for m in mat: st.warning(m)
        st.markdown("<br>", unsafe_allow_html=True)
        c1, _, c3 = st.columns(3)
        with c1: download_json("📥 Download DD Report (.json)", result1, "due_diligence.json", key="dda_dl")
        with c3:
            if st.button("🔄 Reset", key="dda_rst", use_container_width=True):
                st.session_state.pop("dda_result", None); st.rerun()

# ── 2. Document Comparison ────────────────────────────────────────
with tab2:
    orig_text, rev_text = two_document_input_ui("dca")
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    doc_type2 = c1.selectbox("Document Type", [
        "Contract", "NDA", "Shareholder agreement", "Employment agreement",
        "Settlement", "Court pleading", "Policy", "Other",
    ], key="dca_dt")
    client_pos2 = c2.selectbox("Client Position", [
        "Neutral review", "Buyer / Investor", "Seller / Target", "Claimant", "Defendant",
    ], key="dca_cp")
    if st.button("🔍 Compare Documents", type="primary", disabled=not api_key, key="dca_btn"):
        if not orig_text or not rev_text:
            st.warning("⚠️ Both documents are required.")
        else:
            from utils.document_comparison import DocumentComparison
            with st.spinner("Comparing with Claude Opus 4.7…"):
                try:
                    result2 = DocumentComparison(api_key).compare(orig_text, rev_text, doc_type2, client_pos2)
                    st.session_state.dca_result = result2
                    st.success("✅ Comparison complete!")
                except Exception as exc:
                    st.error(f"Comparison failed: {exc}")
    if st.session_state.get("dca_result"):
        result2 = st.session_state.dca_result
        changes = result2.get("changes", [])
        st.divider()
        m1, m2, m3 = st.columns(3)
        m1.markdown(f'<div class="metric-card"><div class="val">{len(changes)}</div><div class="lbl">Changes</div></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="metric-card"><div class="val" style="color:#dc2626">{len(result2.get("significant_changes",[]))}</div><div class="lbl">High-Impact</div></div>', unsafe_allow_html=True)
        m3.markdown(f'<div class="metric-card"><div class="val">{result2.get("net_effect","—")}</div><div class="lbl">Net Effect</div></div>', unsafe_allow_html=True)
        st.markdown(f"**Summary:** {result2.get('summary','')}")
        if changes:
            st.markdown("<br>", unsafe_allow_html=True)
            section(f"📋 Changes ({len(changes)})")
            for ch in changes:
                row = st.columns([1, 3, 3, 2, 1])
                row[0].markdown(f"`{ch.get('change_type','')}`")
                row[1].markdown(f'<span style="color:#dc2626">{ch.get("original_text","")}</span>', unsafe_allow_html=True)
                row[2].markdown(f'<span style="color:#16a34a">{ch.get("revised_text","")}</span>', unsafe_allow_html=True)
                row[3].markdown(ch.get("legal_significance",""))
                row[4].markdown(risk_badge(ch.get("impact_level","low")), unsafe_allow_html=True)
                st.markdown('<hr style="margin:0.25rem 0;border-color:#f1f5f9">', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        c1, _, c3 = st.columns(3)
        with c1: download_json("📥 Download Report (.json)", result2, "comparison.json", key="dca_dl")
        with c3:
            if st.button("🔄 Reset", key="dca_rst", use_container_width=True):
                st.session_state.pop("dca_result", None); st.rerun()

# ── 3. Contract Summary (placeholder) ────────────────────────────
with tab3:
    placeholder_feature(
        "📋", "Contract Summary",
        "Generate a concise plain-English summary of any contract, highlighting key commercial terms.",
        ["Upload any contract in PDF or Word format", "Receive structured summary with key terms table",
         "Identify parties, dates, payment, termination, and key obligations",
         "Export one-page summary for client or internal use"],
        ["One-page contract summary", "Key terms table (parties, value, term, governing law)",
         "Risk flags highlighted", "Word/PDF export"],
    )

# ── 4. Risk Report Generator (placeholder) ───────────────────────
with tab4:
    placeholder_feature(
        "🚨", "Risk Report Generator",
        "Generate a comprehensive risk report across multiple documents for board or client reporting.",
        ["Upload multiple documents for batch risk analysis",
         "Receive consolidated risk register across all documents",
         "Prioritise risks by severity and likelihood",
         "Export board-ready risk report"],
        ["Consolidated risk register", "Risk matrix (severity × likelihood)",
         "Board-ready risk report (PDF)", "Risk summary per document"],
    )
