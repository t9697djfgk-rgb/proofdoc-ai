import streamlit as st
from utils.shared.styles import inject_css, page_header, disclaimer, confidentiality_notice, section, risk_badge
from utils.shared.sidebar import render_sidebar
from utils.shared.document_input import document_input_ui
from utils.shared.export_utils import action_row, download_json

st.set_page_config(page_title="Citation Checker · ProofDoc AI", page_icon="🔍", layout="wide")
inject_css()
api_key = render_sidebar("Citation Checker")
page_header("🔍", "Citation Checker", "Detect formatting issues, missing details, and citation risks")
disclaimer()
st.markdown(
    '<div class="notice-box">ℹ️ <strong>Note:</strong> This tool checks citation format, internal '
    "consistency, and completeness. It cannot verify that cited authorities exist in external "
    "databases without internet access to legal databases.</div>",
    unsafe_allow_html=True,
)

section("📎 Document Input")
text = document_input_ui("cc", paste_placeholder="Paste your legal brief, memo, or submission here…")

st.markdown("<br>", unsafe_allow_html=True)
c1, c2 = st.columns(2)
citation_style = c1.selectbox("Citation Style", [
    "OSCOLA", "Bluebook", "APA legal", "Chicago legal", "Generic legal citation",
])
jurisdiction = c2.selectbox("Jurisdiction", [
    "UK", "US", "EU", "Rwanda", "International law", "Mixed",
])

submit = st.button("🔍 Check Citations", type="primary", disabled=not api_key)

if submit:
    if not text:
        st.warning("⚠️ Upload a document or paste text first.")
    else:
        from utils.citation_checker import CitationChecker
        with st.spinner("Checking citations with Claude Opus 4.7…"):
            try:
                result = CitationChecker(api_key).check(text, citation_style, jurisdiction)
                st.session_state.cc_result = result
                st.success("✅ Citation check complete!")
            except Exception as exc:
                st.error(f"Check failed: {exc}")

if st.session_state.get("cc_result"):
    result = st.session_state.cc_result
    summary = result.get("summary", {})
    citations = result.get("citations", [])
    recs = result.get("general_recommendations", [])

    st.divider()
    section("📊 Summary")
    cols = st.columns(5)
    for col, (key, lbl) in zip(cols, [
        ("total_citations","Total Citations"), ("formatting_issues","Formatting Issues"),
        ("missing_details","Missing Details"), ("quotation_risks","Quotation Risks"),
        ("possible_invalid_citations","Possible Invalid"),
    ]):
        col.markdown(
            f'<div class="metric-card"><div class="val">{summary.get(key,0)}</div>'
            f'<div class="lbl">{lbl}</div></div>',
            unsafe_allow_html=True,
        )

    if citations:
        st.markdown("<br>", unsafe_allow_html=True)
        section(f"📚 Citations Reviewed ({len(citations)})")
        hdr = st.columns([3, 1.5, 2, 1, 2.5, 2])
        for col, lbl in zip(hdr, ["Citation Text", "Type", "Issue", "Severity", "Suggested Fix", "Explanation"]):
            col.markdown(f"**{lbl}**")
        st.divider()
        for c in citations:
            row = st.columns([3, 1.5, 2, 1, 2.5, 2])
            row[0].markdown(f'`{c.get("citation_text","")}`')
            row[1].markdown(f'<span class="badge-doc">{c.get("citation_type","")}</span>', unsafe_allow_html=True)
            row[2].markdown(c.get("issue", ""))
            row[3].markdown(risk_badge(c.get("severity", "low")), unsafe_allow_html=True)
            row[4].markdown(c.get("suggested_fix", ""))
            row[5].markdown(c.get("explanation", ""))
            st.markdown('<hr style="margin:0.25rem 0;border-color:#f1f5f9">', unsafe_allow_html=True)

    if recs:
        st.markdown("<br>", unsafe_allow_html=True)
        section("💡 General Recommendations")
        for r in recs:
            st.markdown(f"- {r}")

    st.markdown("<br>", unsafe_allow_html=True)
    c1, _, c3 = st.columns(3)
    with c1:
        download_json("📥 Download Report (.json)", result, "citation_report.json", key="cc_dl")
    with c3:
        if st.button("🔄 Reset", use_container_width=True, key="cc_reset"):
            st.session_state.pop("cc_result", None)
            st.rerun()
