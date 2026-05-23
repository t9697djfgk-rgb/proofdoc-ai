import streamlit as st
from utils.shared.styles import inject_css, page_header, disclaimer, section
from utils.shared.sidebar import render_sidebar
from utils.shared.export_utils import action_row

st.set_page_config(page_title="Legal Memo Generator · ProofDoc AI", page_icon="📄", layout="wide")
inject_css()
api_key = render_sidebar("Legal Memo Generator")
page_header("📄", "Legal Memo Generator", "Convert facts and research into a structured legal memorandum")
disclaimer()
st.markdown(
    '<div class="notice-box">ℹ️ This tool drafts legal memos from provided facts only. '
    "It will not invent cases or statutes. Verify all cited authorities independently.</div>",
    unsafe_allow_html=True,
)

section("📋 Memo Details")
c1, c2, c3 = st.columns(3)
memo_type = c1.selectbox("Memo Type", [
    "Objective memo", "Persuasive memo", "Internal research memo",
    "Client advice memo", "Academic memo",
])
jurisdiction = c2.selectbox("Jurisdiction", ["International/Neutral", "UK", "US", "EU", "Rwanda", "Other"])
client_position = c3.text_input("Client Position / Party", placeholder="e.g. Claimant, Respondent, Neutral")

legal_issue = st.text_area("Legal Issue / Question *", height=80,
                            placeholder="e.g. Whether the non-compete clause in the employment agreement is enforceable under English law…")
facts = st.text_area("Key Facts *", height=120,
                      placeholder="Describe the relevant facts chronologically…")
research_notes = st.text_area("Relevant Law / Research Notes", height=120,
                               placeholder="List relevant cases, statutes, regulations, or key legal principles you want included…")

submit = st.button("📄 Generate Memo", type="primary", disabled=not api_key)

if submit:
    if not legal_issue.strip() or not facts.strip():
        st.warning("⚠️ Legal issue and facts are required.")
    else:
        from utils.legal_memo import LegalMemoGenerator
        with st.spinner("Drafting memo with Claude Opus 4.7…"):
            try:
                result = LegalMemoGenerator(api_key).generate(
                    legal_issue, facts, jurisdiction, research_notes, client_position, memo_type
                )
                st.session_state.lm_result = result
                st.success("✅ Memo generated!")
            except Exception as exc:
                st.error(f"Generation failed: {exc}")

if st.session_state.get("lm_result"):
    result = st.session_state.lm_result

    st.divider()
    memo_sections = [
        ("⚖️ Issue", "issue"),
        ("💡 Brief Answer", "brief_answer"),
        ("📋 Facts", "facts"),
        ("📚 Applicable Law", "applicable_law"),
        ("🔍 Analysis", "analysis"),
        ("🔄 Counterarguments", "counterarguments"),
        ("🏁 Conclusion", "conclusion"),
    ]

    # Full memo view
    section("📄 Legal Memorandum")
    full_memo = ""
    for label, key in memo_sections:
        content = result.get(key, "")
        if content:
            st.markdown(f"### {label}")
            st.markdown(content)
            st.markdown("")
            full_memo += f"{label}\n{'='*40}\n{content}\n\n"

    risks = result.get("risks", [])
    recs = result.get("recommendations", [])
    if risks:
        st.markdown("### ⚠️ Risks")
        for r in risks: st.warning(r)
        full_memo += "Risks\n" + "\n".join(f"- {r}" for r in risks) + "\n\n"
    if recs:
        st.markdown("### ✅ Recommendations")
        for r in recs: st.markdown(f"- {r}")
        full_memo += "Recommendations\n" + "\n".join(f"- {r}" for r in recs) + "\n\n"

    st.markdown("<br>", unsafe_allow_html=True)
    action_row(
        text_to_download=full_memo,
        base_filename="legal_memo",
        report_data=result,
        reset_keys=["lm_result"],
        key_prefix="lm",
    )
