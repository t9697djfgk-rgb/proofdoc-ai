import streamlit as st
import json
from utils.shared.styles import inject_css, page_header, disclaimer, confidentiality_notice, section, risk_badge
from utils.shared.sidebar import render_sidebar
from utils.shared.document_input import document_input_ui
from utils.shared.export_utils import action_row

st.set_page_config(page_title="Legal English Reviewer · ProofDoc AI", page_icon="✍️", layout="wide")
inject_css()
api_key = render_sidebar("Legal English Reviewer")
page_header("✍️", "Legal English Reviewer", "Grammar · Style · Legal Clarity · Risk Flags")
disclaimer()
confidentiality_notice()

section("📎 Document Input")
text = document_input_ui("ler", paste_placeholder="Paste your contract, clause, or legal document here…")

st.markdown("<br>", unsafe_allow_html=True)
c1, c2 = st.columns(2)
review_type = c1.selectbox("Review Type", [
    "Legal English polish", "Grammar only", "Contract drafting review",
    "Academic legal writing", "Court submission review", "Plain-English rewrite",
])
legal_style = c2.selectbox("Legal Style", [
    "UK legal English", "US legal English", "International legal English", "Academic legal English",
])

submit = st.button("🔍 Review Document", type="primary", disabled=not api_key)

if submit:
    if not text:
        st.warning("⚠️ Upload a document or paste text first.")
    else:
        from utils.legal_reviewer import LegalReviewer
        with st.spinner("Reviewing with Claude Opus 4.7…"):
            try:
                result = LegalReviewer(api_key).review(text, review_type, legal_style)
                st.session_state.ler_result = result
                if result.get("_parse_error"):
                    st.warning("⚠️ Response partially parsed.")
                else:
                    st.success("✅ Review complete!")
            except Exception as exc:
                st.error(f"Review failed: {exc}")

if st.session_state.get("ler_result"):
    result = st.session_state.ler_result
    summary = result.get("summary", {})
    edits = result.get("edits", [])
    revised = result.get("revised_document", "")

    st.divider()
    section("📊 Summary")
    cols = st.columns(5)
    for col, (key, lbl) in zip(cols, [
        ("total_issues", "Total Issues"), ("grammar_issues", "Grammar"),
        ("style_issues", "Style"), ("legal_clarity_issues", "Legal Clarity"),
        ("high_risk_edits", "High Risk"),
    ]):
        color = 'color:#dc2626' if key == "high_risk_edits" and summary.get(key, 0) > 0 else ''
        col.markdown(
            f'<div class="metric-card"><div class="val" style="{color}">{summary.get(key, 0)}</div>'
            f'<div class="lbl">{lbl}</div></div>',
            unsafe_allow_html=True,
        )

    if edits:
        st.markdown("<br>", unsafe_allow_html=True)
        section("📝 Suggested Edits")
        hdr = st.columns([2.5, 2.5, 1.5, 1, 3])
        for col, lbl in zip(hdr, ["Original Text", "Suggested Correction", "Issue Type", "Risk", "Explanation"]):
            col.markdown(f"**{lbl}**")
        st.divider()
        for edit in edits:
            risk = edit.get("risk_level", "low")
            row = st.columns([2.5, 2.5, 1.5, 1, 3])
            row[0].markdown(f'<span style="color:#64748b">{edit.get("original_text","")}</span>', unsafe_allow_html=True)
            row[1].markdown(f'**{edit.get("suggested_correction","")}**')
            row[2].markdown(f'<span class="issue-badge">{edit.get("issue_type","").replace("_"," ").title()}</span>', unsafe_allow_html=True)
            row[3].markdown(risk_badge(risk), unsafe_allow_html=True)
            row[4].markdown(edit.get("explanation", ""))
            st.markdown('<hr style="margin:0.25rem 0;border-color:#f1f5f9">', unsafe_allow_html=True)
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
        action_row(
            text_to_download=revised,
            base_filename="revised_document",
            report_data={"review_type": review_type, "legal_style": legal_style, "summary": summary, "edits": edits},
            reset_keys=["ler_result"],
            key_prefix="ler",
        )
