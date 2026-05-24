import streamlit as st
from utils.shared.sidebar import setup_page
from utils.shared.styles import slim_header, disclaimer, section
from utils.shared.export_utils import action_row

from utils.auth import require_lawyer
api_key = setup_page()
require_lawyer()
slim_header("👤", "Client Intake", "Convert client facts into a structured lawyer handover note")
disclaimer()

st.markdown(
    '<div class="notice-box">ℹ️ Complete the form below. The AI will produce a structured '
    "intake summary and handover note ready for the responsible lawyer to review.</div>",
    unsafe_allow_html=True,
)

section("📋 Matter Details")
c1, c2, c3 = st.columns(3)
matter_type = c1.selectbox("Matter Type", [
    "Commercial dispute", "Employment matter", "Corporate transaction",
    "Property matter", "Criminal case", "Family law", "Regulatory", "Other",
])
client_name = c2.text_input("Client Name *", placeholder="e.g. Acme Ltd / John Smith")
contact = c3.text_input("Contact / Relationship", placeholder="e.g. CEO, Self")

d1, d2 = st.columns(2)
opposing = d1.text_input("Opposing Party / Counterparty", placeholder="e.g. XYZ Corp")
referred_by = d2.text_input("Referred By", placeholder="e.g. Existing client / Google Search")

key_facts = st.text_area(
    "Key Facts *", height=150,
    placeholder="Describe the situation in chronological order. Include dates, amounts, and key events…",
)
client_objectives = st.text_area(
    "Client Objectives", height=80,
    placeholder="What does the client want to achieve? e.g. Recover €500k, retain employment, avoid prosecution…",
)
urgency = st.selectbox("Urgency", ["Standard (7+ days)", "Urgent (2–6 days)", "Critical (within 24 hours)"])
additional = st.text_area(
    "Additional Notes", height=60,
    placeholder="Any documents provided, prior legal advice, limitation concerns, sensitivity flags…",
)

submit = st.button("👤 Generate Intake Summary", type="primary", disabled=not api_key)

if submit:
    if not client_name.strip() or not key_facts.strip():
        st.warning("⚠️ Client name and key facts are required.")
    else:
        from utils.client_intake import ClientIntakeAssistant
        with st.spinner("Building intake summary with Claude Opus 4.7…"):
            try:
                result = ClientIntakeAssistant(api_key).process(
                    matter_type, client_name, contact, opposing,
                    key_facts, client_objectives, urgency, referred_by, additional,
                )
                st.session_state.ci_result = result
                st.success("✅ Intake summary generated!")
            except Exception as exc:
                st.error(f"Generation failed: {exc}")

if st.session_state.get("ci_result"):
    result = st.session_state.ci_result

    st.divider()
    section("📄 Client Intake Summary")

    handover = result.get("handover_note", "")
    if handover:
        st.markdown(
            f'<div class="revised-doc">{handover.replace(chr(10), "<br>")}</div>',
            unsafe_allow_html=True,
        )

    tabs = st.tabs(["⚠️ Immediate Actions", "📋 Key Issues", "🕐 Limitation Concerns",
                    "📌 Recommended Next Steps", "💼 Matter Classification"])
    with tabs[0]:
        for a in result.get("immediate_actions", []): st.warning(a)
    with tabs[1]:
        for i in result.get("key_issues", []): st.markdown(f"- {i}")
    with tabs[2]:
        for l in result.get("limitation_concerns", []): st.error(l)
    with tabs[3]:
        for n in result.get("next_steps", []): st.markdown(f"- {n}")
    with tabs[4]:
        st.markdown(f"**Matter Type:** {result.get('matter_classification', matter_type)}")
        st.markdown(f"**Complexity:** {result.get('complexity', '—')}")
        st.markdown(f"**Estimated Timeline:** {result.get('estimated_timeline', '—')}")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Create matter directly from intake ────────────────────────
    section("➕ Create Matter from this Intake")
    ci1, ci2, ci3 = st.columns(3)
    ci_title = ci1.text_input("Matter Title *",
                               value=f"{client_name} — {matter_type}",
                               key="ci_m_title")
    ci_jur   = ci2.selectbox("Jurisdiction",
                              ["Rwanda", "UK", "US", "EU", "International", "Other"],
                              key="ci_m_jur")
    ci_pri   = ci3.selectbox("Priority", ["high", "medium", "low"], index=1, key="ci_m_pri")
    if st.button("➕ Create Matter in System", type="primary",
                 use_container_width=True, key="ci_create_matter"):
        if not ci_title.strip():
            st.warning("⚠️ Matter title is required.")
        else:
            import utils.database as db
            import datetime as _dt
            existing = db.list_matters()
            ref = f"MAT-{_dt.date.today().year}-{len(existing)+1:04d}"
            m = db.create_matter(
                ref=ref,
                title=ci_title.strip(),
                matter_type=result.get("matter_classification", matter_type),
                jurisdiction=ci_jur,
                description=handover[:1000] if handover else "",
                opposing_party=opposing.strip() if opposing else None,
                priority=ci_pri,
            )
            if m:
                st.success(f"✅ Matter **{ref}** created! Go to Matters to open it.")
                st.session_state.selected_matter_id = m["id"]
            else:
                st.error("Failed to create matter — make sure you are logged in.")

    st.markdown("<br>", unsafe_allow_html=True)
    action_row(
        text_to_download=handover,
        base_filename="client_intake",
        report_data=result,
        reset_keys=["ci_result"],
        key_prefix="ci",
    )
