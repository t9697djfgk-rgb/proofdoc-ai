import streamlit as st
from utils.shared.styles import inject_css, page_header, disclaimer, section, risk_badge
from utils.shared.sidebar import render_sidebar
from utils.shared.export_utils import action_row

st.set_page_config(page_title="Client Intake · ProofDoc AI", page_icon="👤", layout="wide")
inject_css()
api_key = render_sidebar("Client Intake Assistant")
page_header("👤", "Client Intake Assistant", "Convert client facts into a structured lawyer handover note")
disclaimer()
st.markdown(
    '<div class="notice-box">ℹ️ This tool generates an intake summary for the lawyer. '
    "It does not provide legal advice.</div>",
    unsafe_allow_html=True,
)

section("📋 Client Information")
c1, c2 = st.columns(2)
matter_type = c1.selectbox("Matter Type", [
    "Contract dispute", "Employment issue", "Criminal matter", "Corporate matter",
    "Immigration matter", "Family matter", "Real estate matter",
    "Debt recovery", "Personal injury", "Compliance issue", "Other",
])
urgency = c2.selectbox("Urgency", ["Low", "Medium", "High", "Urgent"])

d1, d2 = st.columns(2)
client_name = d1.text_input("Client Name *")
contact_details = d2.text_input("Contact Details", placeholder="Email / phone / address")

opposing_party = st.text_input("Opposing Party / Respondent", placeholder="Name and role if known")
key_facts = st.text_area("Key Facts *", height=130,
                          placeholder="Describe what happened, when, and who was involved…")
important_dates = st.text_area("Important Dates", height=70,
                                placeholder="e.g. Contract signed 1 Jan 2024, dispute arose 15 March 2025…")
docs_available = st.text_input("Documents Available", placeholder="e.g. Contract, emails, invoices")
desired_outcome = st.text_area("Desired Outcome", height=70,
                                placeholder="What does the client want to achieve?")
notes = st.text_area("Additional Notes", height=70)

submit = st.button("📋 Generate Intake Summary", type="primary", disabled=not api_key)

if submit:
    if not client_name.strip() or not key_facts.strip():
        st.warning("⚠️ Client name and key facts are required.")
    else:
        from utils.client_intake import ClientIntakeAssistant
        with st.spinner("Generating intake summary…"):
            try:
                result = ClientIntakeAssistant(api_key).process(
                    matter_type, client_name, contact_details, opposing_party,
                    key_facts, important_dates, docs_available, desired_outcome, urgency, notes
                )
                st.session_state.ci_result = result
                st.success("✅ Intake summary generated!")
            except Exception as exc:
                st.error(f"Failed: {exc}")

if st.session_state.get("ci_result"):
    result = st.session_state.ci_result
    urgency_val = result.get("urgency_assessment", "medium")

    st.divider()
    section("📋 Intake Summary")
    u1, u2 = st.columns([3, 1])
    u1.markdown(f"**Client Summary:** {result.get('client_summary','')}")
    u2.markdown(f"**Urgency:** {risk_badge(urgency_val)}", unsafe_allow_html=True)

    tabs = st.tabs(["⚖️ Legal Issues", "❓ Missing Info", "📂 Documents Needed", "📅 Dates", "➡️ Next Steps", "📝 Handover Note"])

    with tabs[0]:
        for i in result.get("key_legal_issues", []): st.markdown(f"- {i}")
    with tabs[1]:
        for m in result.get("missing_information", []): st.warning(m)
    with tabs[2]:
        for d in result.get("documents_to_request", []): st.markdown(f"- {d}")
    with tabs[3]:
        for d in result.get("important_dates", []): st.markdown(f"- {d}")
    with tabs[4]:
        for s in result.get("suggested_next_steps", []): st.markdown(f"- {s}")
    with tabs[5]:
        handover = result.get("lawyer_handover_note", "")
        st.markdown(f'<div class="revised-doc">{handover.replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    handover_text = result.get("lawyer_handover_note", "")
    action_row(
        text_to_download=handover_text,
        base_filename="client_intake",
        report_data=result,
        reset_keys=["ci_result"],
        key_prefix="ci",
    )
