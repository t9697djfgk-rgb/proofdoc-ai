import streamlit as st
from utils.shared.sidebar import setup_page
from utils.shared.styles import slim_header, disclaimer, confidentiality_notice, section, placeholder_feature
from utils.shared.document_input import document_input_ui
from utils.shared.export_utils import download_json

api_key = setup_page()
slim_header("🧪", "Evidence & Witnesses", "Analyse witness statements, identify contradictions, and prepare cross-examination")
disclaimer()
confidentiality_notice()

tab1, tab2, tab3 = st.tabs([
    "🧪 Evidence Analyzer",
    "👤 Witness Statement Analyzer",
    "❓ Cross-Examination Questions",
])

# ── 1. Evidence Analyzer (functional) ────────────────────────────
with tab1:
    st.markdown("Analyse witness statements and evidence for strengths, weaknesses, contradictions, and gaps.")
    text1 = document_input_ui("ea", paste_placeholder="Paste witness statement or evidence summary here…")
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    case_type = c1.selectbox("Case Type", [
        "Civil litigation", "Criminal case", "Arbitration", "Employment dispute",
        "Internal investigation", "Anti-corruption investigation", "Other",
    ], key="ea_ct")
    role = c2.selectbox("Your Role / Perspective", [
        "Claimant / Plaintiff", "Defendant", "Prosecutor", "Defence", "Neutral reviewer",
    ], key="ea_role")
    if st.button("🧪 Analyse Evidence", type="primary", disabled=not api_key, key="ea_btn"):
        if not text1:
            st.warning("⚠️ Upload or paste a document first.")
        else:
            from utils.evidence_analyzer import EvidenceAnalyzer
            with st.spinner("Analysing with Claude Opus 4.7…"):
                try:
                    result1 = EvidenceAnalyzer(api_key).analyze(text1, case_type, role)
                    st.session_state.ea_result = result1
                    st.success("✅ Analysis complete!")
                except Exception as exc:
                    st.error(f"Analysis failed: {exc}")
    if st.session_state.get("ea_result"):
        result1 = st.session_state.ea_result
        st.divider()
        m1, m2, m3, m4 = st.columns(4)
        m1.markdown(f'<div class="metric-card"><div class="val">{len(result1.get("key_facts",[]))}</div><div class="lbl">Key Facts</div></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="metric-card"><div class="val" style="color:#16a34a">{len(result1.get("strong_points",[]))}</div><div class="lbl">Strong Points</div></div>', unsafe_allow_html=True)
        m3.markdown(f'<div class="metric-card"><div class="val" style="color:#dc2626">{len(result1.get("weak_points",[]))}</div><div class="lbl">Weak Points</div></div>', unsafe_allow_html=True)
        m4.markdown(f'<div class="metric-card"><div class="val" style="color:#d97706">{len(result1.get("contradictions",[]))}</div><div class="lbl">Contradictions</div></div>', unsafe_allow_html=True)
        ea_tabs = st.tabs([
            "📌 Key Facts", "✅ Strong Points", "⚠️ Weak Points", "🔄 Contradictions",
            "❓ Missing Facts", "💬 Follow-Up", "🔬 Cross-Examination", "📅 Timeline",
        ])
        with ea_tabs[0]:
            for f in result1.get("key_facts",[]): st.markdown(f"- {f}")
        with ea_tabs[1]:
            for s in result1.get("strong_points",[]): st.success(s)
        with ea_tabs[2]:
            for w in result1.get("weak_points",[]): st.warning(w)
        with ea_tabs[3]:
            for c in result1.get("contradictions",[]):
                with st.expander(f"**{c.get('issue','')}**"):
                    for t in c.get("conflicting_texts",[]): st.markdown(f"- `{t}`")
                    st.markdown(f"**Why it matters:** {c.get('why_it_matters','')}")
        with ea_tabs[4]:
            for m in result1.get("missing_facts",[]): st.markdown(f"- {m}")
        with ea_tabs[5]:
            for q in result1.get("follow_up_questions",[]): st.markdown(f"- {q}")
        with ea_tabs[6]:
            for q in result1.get("cross_examination_questions",[]): st.markdown(f"- {q}")
        with ea_tabs[7]:
            for t in result1.get("timeline_facts",[]): st.markdown(f"- {t}")
        st.markdown("<br>", unsafe_allow_html=True)
        c1, _, c3 = st.columns(3)
        with c1: download_json("📥 Download Analysis (.json)", result1, "evidence_analysis.json", key="ea_dl")
        with c3:
            if st.button("🔄 Reset", key="ea_rst", use_container_width=True):
                st.session_state.pop("ea_result", None); st.rerun()

# ── 2. Witness Statement Analyzer (placeholder) ───────────────────
with tab2:
    placeholder_feature(
        "👤", "Witness Statement Analyzer",
        "Deep-analyse individual witness statements against known facts and other statements.",
        ["Upload single witness statement", "Cross-reference against master fact chronology",
         "Identify internal inconsistencies", "Compare with other witnesses' accounts",
         "Score credibility based on consistency"],
        ["Credibility report per witness", "Inconsistencies list with references",
         "Comparison matrix across witnesses", "Deposition preparation notes"],
    )

# ── 3. Cross-Examination Questions (placeholder) ──────────────────
with tab3:
    placeholder_feature(
        "❓", "Cross-Examination Questions",
        "Generate targeted cross-examination questions based on weaknesses, contradictions, and gaps.",
        ["Upload or select witness statement", "AI generates questions targeting key weaknesses",
         "Categorise by topic (credibility, facts, motive)", "Reorder and customise questions"],
        ["Structured cross-examination plan", "Questions grouped by topic",
         "Anticipated answers and follow-ups", "Printable cross-examination outline"],
    )
