import streamlit as st
from utils.shared.styles import inject_css, page_header, disclaimer, confidentiality_notice, section, risk_badge
from utils.shared.sidebar import render_sidebar
from utils.shared.document_input import document_input_ui
from utils.shared.export_utils import download_json

st.set_page_config(page_title="Court Document Checker · ProofDoc AI", page_icon="🏛️", layout="wide")
inject_css()
api_key = render_sidebar("Court Document Checker")
page_header("🏛️", "Court Document Checker", "Review pleadings and submissions before filing")
disclaimer()
confidentiality_notice()

section("📎 Document Input")
text = document_input_ui("cdc", paste_placeholder="Paste your court document here…")

st.markdown("<br>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
doc_type = c1.selectbox("Document Type", [
    "Written submissions", "Statement of claim", "Defence", "Affidavit",
    "Witness statement", "Motion/Application", "Appeal brief", "Other",
])
court_jurisdiction = c2.text_input("Court / Jurisdiction", placeholder="e.g. High Court of Rwanda, English Commercial Court")
party = c3.selectbox("Party Represented", [
    "Claimant/Plaintiff", "Defendant", "Appellant", "Respondent", "Prosecutor", "Defence",
])

submit = st.button("🏛️ Check Document", type="primary", disabled=not api_key)

if submit:
    if not text:
        st.warning("⚠️ Upload a document or paste text first.")
    else:
        from utils.court_checker import CourtDocumentChecker
        with st.spinner("Reviewing with Claude Opus 4.7…"):
            try:
                result = CourtDocumentChecker(api_key).check(text, doc_type, court_jurisdiction, party)
                st.session_state.cdc_result = result
                st.success("✅ Review complete!")
            except Exception as exc:
                st.error(f"Review failed: {exc}")

if st.session_state.get("cdc_result"):
    result = st.session_state.cdc_result
    score = result.get("filing_readiness_score", 0)

    st.divider()
    score_color = "#16a34a" if score >= 80 else "#d97706" if score >= 60 else "#dc2626"
    s1, s2 = st.columns([1, 3])
    s1.markdown(
        f'<div class="metric-card"><div class="val" style="color:{score_color}">{score}/100</div>'
        f'<div class="lbl">Filing Readiness</div></div>',
        unsafe_allow_html=True,
    )
    s2.markdown(f"**Summary:** {result.get('executive_summary','')}")

    issue_tabs = [
        ("🏗️ Structural Issues", "structural_issues"),
        ("❌ Missing Elements", "missing_elements"),
        ("⚠️ Weak Arguments", "weak_arguments"),
        ("🔍 Unsupported Claims", "unsupported_factual_claims"),
        ("📚 Citation Issues", "citation_issues"),
        ("🗣️ Tone Issues", "tone_issues"),
        ("⚖️ Relief Clarity", "relief_clarity_issues"),
        ("💡 Improvements", "suggested_improvements"),
    ]
    tabs = st.tabs([t[0] for t in issue_tabs])
    for tab, (_, key) in zip(tabs, issue_tabs):
        with tab:
            items = result.get(key, [])
            if items:
                for item in items: st.markdown(f"- {item}")
            else:
                st.success("No issues in this category.")

    st.markdown("<br>", unsafe_allow_html=True)
    c1, _, c3 = st.columns(3)
    with c1:
        download_json("📥 Download Review Report (.json)", result, "court_document_review.json", key="cdc_dl")
    with c3:
        if st.button("🔄 Reset", use_container_width=True, key="cdc_reset"):
            st.session_state.pop("cdc_result", None)
            st.rerun()
