import streamlit as st
from utils.shared.styles import inject_css, page_header, disclaimer, section
from utils.shared.sidebar import render_sidebar
from utils.shared.export_utils import action_row

st.set_page_config(page_title="Legal Drafting Assistant · ProofDoc AI", page_icon="📝", layout="wide")
inject_css()
api_key = render_sidebar("Legal Drafting Assistant")
page_header("📝", "Legal Drafting Assistant", "Generate professional first drafts of legal documents")
disclaimer()

section("📋 Document Details")
c1, c2, c3 = st.columns(3)
doc_type = c1.selectbox("Document Type", [
    "NDA", "Service Agreement", "Employment Contract", "Consultancy Agreement",
    "Demand Letter", "Legal Opinion", "Legal Memo", "Board Resolution",
    "Shareholder Resolution", "Anti-Bribery Policy", "Whistleblowing Policy",
    "Court Submission", "Affidavit/Witness Statement", "Settlement Agreement",
])
jurisdiction = c2.selectbox("Jurisdiction", ["International/Neutral", "UK", "US", "EU", "Rwanda", "Other"])
legal_style = c3.selectbox("Legal Style", [
    "UK legal English", "US legal English", "International legal English",
])

c4, c5 = st.columns(2)
tone = c4.selectbox("Tone", ["Formal", "Firm", "Neutral", "Persuasive", "Simple"])
parties = c5.text_input("Party Names", placeholder="e.g. ABC Ltd (the Company) and John Smith (the Employee)")

key_facts = st.text_area("Key Facts / Instructions", height=140,
                          placeholder="Describe the key facts, terms, dates, and obligations to include…")
additional = st.text_area("Additional Instructions (optional)", height=80,
                           placeholder="Any specific clauses, exclusions, or requirements…")

submit = st.button("📝 Generate Draft", type="primary", disabled=not api_key)

if submit:
    if not key_facts.strip():
        st.warning("⚠️ Enter the key facts before generating.")
    else:
        from utils.drafting_assistant import DraftingAssistant
        with st.spinner("Drafting with Claude Opus 4.7…"):
            try:
                result = DraftingAssistant(api_key).draft(
                    doc_type, jurisdiction, legal_style, parties, key_facts, tone, additional
                )
                st.session_state.da_result = result
                st.success("✅ Draft generated!")
            except Exception as exc:
                st.error(f"Drafting failed: {exc}")

if st.session_state.get("da_result"):
    result = st.session_state.da_result
    draft = result.get("draft_document", "")
    title = result.get("draft_title", doc_type if "doc_type" in dir() else "Draft Document")

    st.divider()
    section(f"📄 {title}")
    st.markdown(
        f'<div class="revised-doc">{draft.replace(chr(10), "<br>")}</div>',
        unsafe_allow_html=True,
    )

    tabs = st.tabs(["🔍 Assumptions", "❓ Missing Information", "⚠️ Risk Warnings", "➕ Optional Clauses"])
    with tabs[0]:
        items = result.get("assumptions", [])
        if items:
            for a in items: st.markdown(f"- {a}")
        else:
            st.caption("No assumptions flagged.")
    with tabs[1]:
        items = result.get("missing_information", [])
        if items:
            for m in items: st.warning(m)
        else:
            st.caption("No missing information flagged.")
    with tabs[2]:
        items = result.get("risk_warnings", [])
        if items:
            for w in items: st.error(w)
        else:
            st.caption("No risk warnings.")
    with tabs[3]:
        for oc in result.get("optional_clauses", []):
            with st.expander(f"**{oc.get('clause_name','')}** — {oc.get('when_to_use','')}"):
                st.code(oc.get("clause_text", ""), language=None)

    st.markdown("<br>", unsafe_allow_html=True)
    action_row(
        text_to_download=draft,
        base_filename="draft_document",
        report_data=result,
        reset_keys=["da_result"],
        key_prefix="da",
    )
    if st.button("🔁 Improve Draft", key="da_improve"):
        st.info("To improve the draft, update your instructions above and click 'Generate Draft' again.")
