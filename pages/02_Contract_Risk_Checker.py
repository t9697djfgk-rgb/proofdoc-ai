import streamlit as st
from utils.shared.styles import inject_css, page_header, disclaimer, confidentiality_notice, privilege_warning, section, risk_badge
from utils.shared.sidebar import render_sidebar
from utils.shared.document_input import document_input_ui
from utils.shared.export_utils import action_row, download_json

st.set_page_config(page_title="Contract Risk Checker · ProofDoc AI", page_icon="📋", layout="wide")
inject_css()
api_key = render_sidebar("Contract Risk Checker")
page_header("📋", "Contract Risk Checker", "Identify legal, commercial, and drafting risks in contracts")
disclaimer()
confidentiality_notice()
privilege_warning()

section("📎 Contract Input")
text = document_input_ui("crc", paste_placeholder="Paste your contract text here…")

st.markdown("<br>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
contract_type = c1.selectbox("Contract Type", [
    "General Contract", "NDA", "Service Agreement", "Employment Contract",
    "Consultancy Agreement", "Sales Agreement", "Lease Agreement",
    "Shareholder Agreement", "Loan Agreement",
])
client_position = c2.selectbox("Client Position", [
    "Neutral Review", "Buyer", "Seller", "Employer", "Employee",
    "Service Provider", "Client/Customer", "Lender", "Borrower",
])
jurisdiction = c3.selectbox("Jurisdiction", ["International/Neutral", "UK", "US", "EU", "Rwanda"])

submit = st.button("🔍 Analyse Contract Risk", type="primary", disabled=not api_key)

if submit:
    if not text:
        st.warning("⚠️ Upload a contract or paste text first.")
    else:
        from utils.contract_risk import ContractRiskChecker
        with st.spinner("Analysing with Claude Opus 4.7…"):
            try:
                result = ContractRiskChecker(api_key).check(text, contract_type, client_position, jurisdiction)
                st.session_state.crc_result = result
                st.success("✅ Analysis complete!")
            except Exception as exc:
                st.error(f"Analysis failed: {exc}")

if st.session_state.get("crc_result"):
    result = st.session_state.crc_result
    risks = result.get("risks", [])
    missing = result.get("missing_clauses", [])
    neg_points = result.get("negotiation_points", [])

    st.divider()
    overall = result.get("overall_risk", "unknown")
    section("📊 Overall Risk")
    oc1, oc2 = st.columns([1, 3])
    oc1.markdown(
        f'<div class="metric-card" style="margin-top:0.5rem"><div class="val">'
        f'{risk_badge(overall)}</div><div class="lbl">Overall Risk</div></div>',
        unsafe_allow_html=True,
    )
    oc2.markdown(f"**Executive Summary**\n\n{result.get('executive_summary','')}")

    if risks:
        st.markdown("<br>", unsafe_allow_html=True)
        section(f"⚠️ Risks Identified ({len(risks)})")
        hdr = st.columns([1.5, 2.5, 2, 1, 2.5])
        for col, lbl in zip(hdr, ["Clause/Section", "Risk Identified", "Why It Matters", "Level", "Suggested Revision"]):
            col.markdown(f"**{lbl}**")
        st.divider()
        for r in risks:
            row = st.columns([1.5, 2.5, 2, 1, 2.5])
            row[0].markdown(r.get("clause", ""))
            row[1].markdown(r.get("risk_identified", ""))
            row[2].markdown(r.get("why_it_matters", ""))
            row[3].markdown(risk_badge(r.get("risk_level", "medium")), unsafe_allow_html=True)
            row[4].markdown(r.get("suggested_revision", ""))
            st.markdown('<hr style="margin:0.25rem 0;border-color:#f1f5f9">', unsafe_allow_html=True)

    if missing:
        st.markdown("<br>", unsafe_allow_html=True)
        section(f"❌ Missing Clauses ({len(missing)})")
        for m in missing:
            with st.expander(f"**{m.get('clause_name','')}** — {m.get('why_needed','')}"):
                if m.get("sample_clause"):
                    st.code(m["sample_clause"], language=None)

    if neg_points:
        st.markdown("<br>", unsafe_allow_html=True)
        section(f"🤝 Negotiation Points ({len(neg_points)})")
        for n in neg_points:
            st.markdown(f"- **{n.get('point','')}** → {n.get('recommended_position','')}")

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        download_json("📥 Download Risk Report (.json)", result, "contract_risk_report.json", key="crc_dl_json")
    with c3:
        if st.button("🔄 Reset", use_container_width=True, key="crc_reset"):
            st.session_state.pop("crc_result", None)
            st.rerun()
