import streamlit as st
from utils.shared.styles import inject_css, page_header, disclaimer, confidentiality_notice, section
from utils.shared.sidebar import render_sidebar
from utils.shared.document_input import document_input_ui
from utils.shared.export_utils import download_json

st.set_page_config(page_title="Evidence Analyzer · ProofDoc AI", page_icon="🧪", layout="wide")
inject_css()
api_key = render_sidebar("Evidence Analyzer")
page_header("🧪", "Evidence Analyzer", "Analyze witness statements and evidence for strengths, weaknesses, and contradictions")
disclaimer()
confidentiality_notice()

section("📎 Evidence / Statement Input")
text = document_input_ui("ea", paste_placeholder="Paste witness statement or evidence summary here…")

st.markdown("<br>", unsafe_allow_html=True)
c1, c2 = st.columns(2)
case_type = c1.selectbox("Case Type", [
    "Civil litigation", "Criminal case", "Arbitration", "Employment dispute",
    "Internal investigation", "Anti-corruption investigation", "Other",
])
role = c2.selectbox("Your Role / Perspective", [
    "Claimant/Plaintiff", "Defendant", "Prosecutor", "Defence", "Neutral reviewer",
])

submit = st.button("🧪 Analyze Evidence", type="primary", disabled=not api_key)

if submit:
    if not text:
        st.warning("⚠️ Upload a document or paste text first.")
    else:
        from utils.evidence_analyzer import EvidenceAnalyzer
        with st.spinner("Analysing with Claude Opus 4.7…"):
            try:
                result = EvidenceAnalyzer(api_key).analyze(text, case_type, role)
                st.session_state.ea_result = result
                st.success("✅ Analysis complete!")
            except Exception as exc:
                st.error(f"Analysis failed: {exc}")

if st.session_state.get("ea_result"):
    result = st.session_state.ea_result

    st.divider()
    m1, m2, m3, m4 = st.columns(4)
    m1.markdown(f'<div class="metric-card"><div class="val">{len(result.get("key_facts",[]))}</div><div class="lbl">Key Facts</div></div>', unsafe_allow_html=True)
    m2.markdown(f'<div class="metric-card"><div class="val" style="color:#16a34a">{len(result.get("strong_points",[]))}</div><div class="lbl">Strong Points</div></div>', unsafe_allow_html=True)
    m3.markdown(f'<div class="metric-card"><div class="val" style="color:#dc2626">{len(result.get("weak_points",[]))}</div><div class="lbl">Weak Points</div></div>', unsafe_allow_html=True)
    m4.markdown(f'<div class="metric-card"><div class="val" style="color:#d97706">{len(result.get("contradictions",[]))}</div><div class="lbl">Contradictions</div></div>', unsafe_allow_html=True)

    tab_labels = ["📌 Key Facts", "✅ Strong Points", "⚠️ Weak Points", "🔄 Contradictions",
                  "❓ Missing Facts", "💬 Follow-Up", "🔬 Cross-Examination", "📅 Timeline Facts"]
    tabs = st.tabs(tab_labels)

    with tabs[0]:
        for f in result.get("key_facts",[]): st.markdown(f"- {f}")
    with tabs[1]:
        for s in result.get("strong_points",[]): st.success(s)
    with tabs[2]:
        for w in result.get("weak_points",[]): st.warning(w)
    with tabs[3]:
        for c in result.get("contradictions",[]):
            with st.expander(f"**{c.get('issue','')}**"):
                for t in c.get("conflicting_texts",[]): st.markdown(f"- `{t}`")
                st.markdown(f"**Why it matters:** {c.get('why_it_matters','')}")
    with tabs[4]:
        for m in result.get("missing_facts",[]): st.markdown(f"- {m}")
    with tabs[5]:
        for q in result.get("follow_up_questions",[]): st.markdown(f"- {q}")
    with tabs[6]:
        for q in result.get("cross_examination_questions",[]): st.markdown(f"- {q}")
    with tabs[7]:
        for t in result.get("timeline_facts",[]): st.markdown(f"- {t}")

    st.markdown("<br>", unsafe_allow_html=True)
    c1, _, c3 = st.columns(3)
    with c1:
        download_json("📥 Download Analysis Report (.json)", result, "evidence_analysis.json", key="ea_dl")
    with c3:
        if st.button("🔄 Reset", use_container_width=True, key="ea_reset"):
            st.session_state.pop("ea_result", None)
            st.rerun()
