import streamlit as st
from utils.shared.styles import inject_css, page_header, disclaimer, confidentiality_notice, privilege_warning, section, risk_badge
from utils.shared.sidebar import render_sidebar
from utils.shared.document_input import two_document_input_ui
from utils.shared.export_utils import download_json

st.set_page_config(page_title="Document Comparison · ProofDoc AI", page_icon="📊", layout="wide")
inject_css()
api_key = render_sidebar("Document Comparison")
page_header("📊", "Document Comparison", "Identify legally significant differences between two documents")
disclaimer()
confidentiality_notice()
privilege_warning()

section("📎 Document Input")
original, revised = two_document_input_ui("dc")

st.markdown("<br>", unsafe_allow_html=True)
c1, c2 = st.columns(2)
doc_type = c1.selectbox("Document Type", ["Contract", "Court submission", "Legal opinion", "Policy", "Other"])
client_position = c2.selectbox("Client Position", ["Party A", "Party B", "Neutral"])

submit = st.button("📊 Compare Documents", type="primary", disabled=not api_key)

if submit:
    if not original or not revised:
        st.warning("⚠️ Both original and revised documents are required.")
    else:
        from utils.document_comparison import DocumentComparison
        with st.spinner("Comparing with Claude Opus 4.7…"):
            try:
                result = DocumentComparison(api_key).compare(original, revised, doc_type, client_position)
                st.session_state.dc_result = result
                st.success("✅ Comparison complete!")
            except Exception as exc:
                st.error(f"Comparison failed: {exc}")

if st.session_state.get("dc_result"):
    result = st.session_state.dc_result
    changes = result.get("changes", [])

    st.divider()
    section("📋 Executive Summary")
    st.markdown(result.get("executive_summary", ""))

    added   = [c for c in changes if c.get("change_type") == "added"]
    deleted = [c for c in changes if c.get("change_type") == "deleted"]
    modified = [c for c in changes if c.get("change_type") == "modified"]

    m1, m2, m3, m4 = st.columns(4)
    m1.markdown(f'<div class="metric-card"><div class="val">{len(changes)}</div><div class="lbl">Total Changes</div></div>', unsafe_allow_html=True)
    m2.markdown(f'<div class="metric-card"><div class="val" style="color:#16a34a">{len(added)}</div><div class="lbl">Added</div></div>', unsafe_allow_html=True)
    m3.markdown(f'<div class="metric-card"><div class="val" style="color:#dc2626">{len(deleted)}</div><div class="lbl">Deleted</div></div>', unsafe_allow_html=True)
    m4.markdown(f'<div class="metric-card"><div class="val" style="color:#d97706">{len(modified)}</div><div class="lbl">Modified</div></div>', unsafe_allow_html=True)

    if changes:
        st.markdown("<br>", unsafe_allow_html=True)
        section(f"🔍 Change Details ({len(changes)})")

        type_icons = {"added": "🟢", "deleted": "🔴", "modified": "🟡"}
        for ch in changes:
            ct = ch.get("change_type", "modified")
            icon = type_icons.get(ct, "🔵")
            with st.expander(f"{icon} **{ct.title()}** · {ch.get('section','')} · {risk_badge(ch.get('risk_level','low'))}", expanded=False):
                cols = st.columns(2)
                if ch.get("original_text"):
                    cols[0].markdown("**Original:**")
                    cols[0].markdown(f'<div class="revised-doc" style="max-height:150px;background:#fef2f2">{ch["original_text"]}</div>', unsafe_allow_html=True)
                if ch.get("revised_text"):
                    cols[1].markdown("**Revised:**")
                    cols[1].markdown(f'<div class="revised-doc" style="max-height:150px;background:#f0fdf4">{ch["revised_text"]}</div>', unsafe_allow_html=True)
                st.markdown(f"**Legal Significance:** {ch.get('legal_significance','')}")
                if ch.get("affected_area"):
                    st.markdown(f"**Affected:** {', '.join(ch['affected_area'])}")
                if ch.get("recommended_action"):
                    st.info(f"💡 **Recommended:** {ch['recommended_action']}")

    st.markdown("<br>", unsafe_allow_html=True)
    c1, _, c3 = st.columns(3)
    with c1:
        download_json("📥 Download Comparison Report (.json)", result, "comparison_report.json", key="dc_dl")
    with c3:
        if st.button("🔄 Reset", use_container_width=True, key="dc_reset"):
            st.session_state.pop("dc_result", None)
            st.rerun()
