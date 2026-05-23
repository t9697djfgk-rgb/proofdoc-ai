import streamlit as st
from utils.shared.styles import inject_css, page_header, disclaimer, section
from utils.shared.sidebar import render_sidebar
from utils.shared.export_utils import action_row

st.set_page_config(page_title="Compliance Policy Generator · ProofDoc AI", page_icon="🛡️", layout="wide")
inject_css()
api_key = render_sidebar("Compliance Policy Generator")
page_header("🛡️", "Compliance Policy Generator", "Draft compliance policies tailored to your organization")
disclaimer()
st.markdown(
    '<div class="notice-box">ℹ️ Generated policies are first drafts. Have a qualified lawyer review before adoption.</div>',
    unsafe_allow_html=True,
)

section("📋 Policy Details")
c1, c2 = st.columns(2)
policy_type = c1.selectbox("Policy Type", [
    "Anti-bribery and corruption policy", "AML policy", "Sanctions policy",
    "Whistleblowing policy", "Gifts and hospitality policy", "Conflict of interest policy",
    "Data protection policy", "Code of conduct", "Third-party due diligence policy",
    "Procurement integrity policy",
])
risk_level = c2.selectbox("Risk Level", ["Low", "Medium", "High"])

d1, d2, d3 = st.columns(3)
org_name = d1.text_input("Organization Name *")
industry = d2.text_input("Industry *", placeholder="e.g. Financial services, Construction, NGO")
jurisdiction = d3.selectbox("Primary Jurisdiction", ["International/Neutral", "UK", "US", "EU", "Rwanda", "Other"])

employees = st.text_input("Number of Employees", placeholder="e.g. 50, 500, 10,000+")
additional = st.text_area("Additional Instructions", height=80,
                           placeholder="Any specific risks, operations, existing policies, or regulatory requirements to include…")

submit = st.button("🛡️ Generate Policy", type="primary", disabled=not api_key)

if submit:
    if not org_name.strip() or not industry.strip():
        st.warning("⚠️ Organization name and industry are required.")
    else:
        from utils.compliance_policy import CompliancePolicyGenerator
        with st.spinner("Drafting policy with Claude Opus 4.7…"):
            try:
                result = CompliancePolicyGenerator(api_key).generate(
                    policy_type, org_name, industry, jurisdiction, employees, risk_level, additional
                )
                st.session_state.cp_result = result
                st.success("✅ Policy generated!")
            except Exception as exc:
                st.error(f"Generation failed: {exc}")

if st.session_state.get("cp_result"):
    result = st.session_state.cp_result
    policy_doc = result.get("policy_document", "")
    title = result.get("policy_title", policy_type if "policy_type" in dir() else "Policy")

    st.divider()
    section(f"📄 {title}")
    st.markdown(f'<div class="revised-doc">{policy_doc.replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)

    tabs = st.tabs(["✅ Implementation Checklist", "🎓 Training", "📞 Reporting Channels",
                    "⚖️ Disciplinary Measures", "🗓️ Review Schedule", "⚠️ Risk Warnings"])
    with tabs[0]:
        for item in result.get("implementation_checklist",[]): st.markdown(f"- {item}")
    with tabs[1]:
        for t in result.get("training_recommendations",[]): st.markdown(f"- {t}")
    with tabs[2]:
        for r in result.get("reporting_channels",[]): st.markdown(f"- {r}")
    with tabs[3]:
        st.markdown(result.get("disciplinary_measures",""))
    with tabs[4]:
        st.markdown(result.get("review_schedule",""))
    with tabs[5]:
        for w in result.get("risk_warnings",[]): st.error(w)

    st.markdown("<br>", unsafe_allow_html=True)
    action_row(
        text_to_download=policy_doc,
        base_filename="compliance_policy",
        report_data=result,
        reset_keys=["cp_result"],
        key_prefix="cp",
    )
