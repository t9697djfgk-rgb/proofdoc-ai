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

# ── 2. Witness Statement Analyzer ────────────────────────────────
with tab2:
    st.markdown("Deep-analyse a witness statement for credibility, inconsistencies, and areas for challenge.")
    text2 = document_input_ui("wa", paste_placeholder="Paste the witness statement to analyse…")
    c1, c2 = st.columns(2)
    wa_case_type = c1.selectbox("Case Type", [
        "Civil litigation", "Criminal case", "Arbitration", "Employment dispute",
        "Internal investigation", "Anti-corruption", "Other",
    ], key="wa_ct")
    wa_persp = c2.selectbox("Your Role", [
        "Claimant / Plaintiff", "Defendant", "Prosecutor", "Defence", "Neutral reviewer",
    ], key="wa_persp")
    wa_facts = st.text_area("Known Facts (for cross-referencing)", height=80,
                             placeholder="List key facts you already know to be true…", key="wa_facts")
    wa_other = st.text_area("Other Witness Statements (optional)", height=60,
                             placeholder="Paste summaries of other witnesses for cross-comparison…", key="wa_other")
    if st.button("👤 Analyse Statement", type="primary", disabled=not api_key, key="wa_btn"):
        if not text2:
            st.warning("⚠️ Upload or paste a witness statement first.")
        else:
            from utils.witness_analyzer import WitnessStatementAnalyzer
            with st.spinner("Analysing with Claude Opus 4.7…"):
                try:
                    result2 = WitnessStatementAnalyzer(api_key).analyze(
                        text2, wa_facts, wa_case_type, wa_persp, wa_other)
                    st.session_state.wa_result = result2
                    st.success("✅ Analysis complete!")
                except Exception as exc:
                    st.error(f"Analysis failed: {exc}")
    if st.session_state.get("wa_result"):
        r = st.session_state.wa_result
        st.divider()
        score = r.get("credibility_score", 0)
        rating = r.get("credibility_rating", "—")
        score_color = {"High": "#16a34a", "Medium": "#d97706", "Low": "#dc2626"}.get(rating, "#64748b")
        m1, m2, m3, m4 = st.columns(4)
        m1.markdown(f'<div class="metric-card"><div class="val" style="color:{score_color}">{rating}</div><div class="lbl">Credibility</div></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="metric-card"><div class="val" style="color:#dc2626">{len(r.get("inconsistent_with_facts",[]))}</div><div class="lbl">Contradictions</div></div>', unsafe_allow_html=True)
        m3.markdown(f'<div class="metric-card"><div class="val" style="color:#d97706">{len(r.get("internal_inconsistencies",[]))}</div><div class="lbl">Internal Issues</div></div>', unsafe_allow_html=True)
        m4.markdown(f'<div class="metric-card"><div class="val">{len(r.get("gaps_and_omissions",[]))}</div><div class="lbl">Gaps</div></div>', unsafe_allow_html=True)
        st.markdown(f"**Credibility Assessment:** {r.get('credibility_assessment','')}")
        wa_tabs = st.tabs(["📋 Key Claims", "⚠️ Contradictions", "🔄 Internal Issues",
                            "❓ Gaps", "💡 Motives", "✅ Strong Points", "📝 Deposition Notes"])
        with wa_tabs[0]:
            for c in r.get("key_claims",[]): st.markdown(f"- {c}")
        with wa_tabs[1]:
            for i in r.get("inconsistent_with_facts",[]):
                sev = i.get("significance","medium")
                fn = st.error if sev == "high" else st.warning
                fn(f"**Claim:** {i.get('claim','')}  |  **Contradiction:** {i.get('contradiction','')}")
        with wa_tabs[2]:
            for i in r.get("internal_inconsistencies",[]):
                with st.expander(f"Internal conflict: {i.get('issue','')}"):
                    st.markdown(f"*Text 1:* {i.get('text_1','')}")
                    st.markdown(f"*Text 2:* {i.get('text_2','')}")
        with wa_tabs[3]:
            for g in r.get("gaps_and_omissions",[]): st.warning(g)
        with wa_tabs[4]:
            for m in r.get("possible_motives",[]): st.info(m)
        with wa_tabs[5]:
            for s in r.get("strong_points",[]): st.success(s)
        with wa_tabs[6]:
            for n in r.get("deposition_notes",[]): st.markdown(f"- {n}")
        c1, _, c3 = st.columns(3)
        with c1: download_json("📥 Download Analysis (.json)", r, "witness_analysis.json", key="wa_dl")
        with c3:
            if st.button("🔄 Reset", key="wa_rst", use_container_width=True):
                st.session_state.pop("wa_result", None); st.rerun()

# ── 3. Cross-Examination Questions ───────────────────────────────
with tab3:
    st.markdown("Generate a structured cross-examination plan targeting weaknesses, contradictions, and credibility.")
    text3 = document_input_ui("ce", paste_placeholder="Paste the witness statement to cross-examine on…")
    c1, c2 = st.columns(2)
    ce_objectives = c1.text_area("Objectives for this Cross-Examination", height=80,
                                   placeholder="e.g. (1) Establish motive to lie, (2) Contradict para 3 of statement", key="ce_obj")
    ce_weaknesses = c2.text_area("Known Weaknesses / Inconsistencies", height=80,
                                   placeholder="Key inconsistencies or lies you have evidence of…", key="ce_weak")
    c3, c4 = st.columns(2)
    ce_case_type = c3.selectbox("Case Type", [
        "Civil litigation", "Criminal case", "Arbitration", "Employment", "Other",
    ], key="ce_ct")
    ce_persp = c4.selectbox("Your Role", [
        "Claimant / Plaintiff counsel", "Defence counsel", "Prosecutor",
        "Defendant counsel", "Neutral / Arbitration",
    ], key="ce_persp")
    if st.button("❓ Generate Cross-Examination Questions", type="primary", disabled=not api_key, key="ce_btn"):
        if not text3:
            st.warning("⚠️ Upload or paste a witness statement first.")
        else:
            from utils.witness_analyzer import CrossExamGenerator
            with st.spinner("Generating with Claude Opus 4.7…"):
                try:
                    result3 = CrossExamGenerator(api_key).generate(
                        text3, ce_weaknesses, ce_objectives, ce_case_type, ce_persp)
                    st.session_state.ce_result = result3
                    st.success("✅ Cross-examination plan ready!")
                except Exception as exc:
                    st.error(f"Generation failed: {exc}")
    if st.session_state.get("ce_result"):
        r = st.session_state.ce_result
        st.divider()
        st.markdown(f"**Strategy:** {r.get('strategy_overview','')}")
        st.markdown(f"**Opening Question:** _{r.get('opening_question','')}_")
        st.markdown(f"**Closing Question:** _{r.get('closing_question','')}_")
        question_sets = r.get("question_sets", [])
        for qs in question_sets:
            with st.expander(f"📌 **{qs.get('topic','')}** — {qs.get('objective','')}"):
                for i, q in enumerate(qs.get("questions", []), 1):
                    q_type_badge = {"leading": "🔵", "open": "🟢", "clarification": "🟡", "challenge": "🔴"}.get(q.get("type",""), "⚪")
                    st.markdown(f"**Q{i}:** {q_type_badge} {q.get('question','')}")
                    st.caption(f"Expected: {q.get('expected_answer','')}  |  Follow-up: {q.get('follow_up','')}")
                    st.markdown("---")
        if r.get("points_to_establish"):
            section("🎯 Points to Establish")
            for p in r["points_to_establish"]: st.markdown(f"- {p}")
        if r.get("traps_to_avoid"):
            section("⚠️ Traps to Avoid")
            for t in r["traps_to_avoid"]: st.warning(t)
        c1, _, c3 = st.columns(3)
        with c1: download_json("📥 Export Cross-Exam Plan (.json)", r, "cross_examination.json", key="ce_dl")
        with c3:
            if st.button("🔄 Reset", key="ce_rst", use_container_width=True):
                st.session_state.pop("ce_result", None); st.rerun()
