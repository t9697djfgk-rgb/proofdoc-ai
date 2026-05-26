import streamlit as st
from utils.shared.sidebar import setup_page
from utils.shared.styles import slim_header, disclaimer, confidentiality_notice, section
from utils.shared.document_input import document_input_ui
from utils.shared.export_utils import download_json, download_docx_from_dict, save_to_matter_ui, dict_to_markdown

from utils.auth import require_lawyer
api_key = setup_page()
require_lawyer()
slim_header("🧪", "Evidence & Witnesses", "Analyse witness statements, identify contradictions, and prepare cross-examination")
disclaimer()
confidentiality_notice()

tab1, tab2, tab3 = st.tabs([
    "🧪 Evidence Analyzer",
    "👤 Witness Statement Analyzer",
    "❓ Cross-Examination Questions",
])

# ── 1. Evidence Analyzer ─────────────────────────────────────────
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

        # Metric cards
        m1, m2, m3, m4 = st.columns(4)
        metrics = [
            (m1, len(result1.get("key_facts", [])),       "Key Facts",       "#1a2744", "#f0f4ff"),
            (m2, len(result1.get("strong_points", [])),   "Strong Points",   "#16a34a", "#f0fdf4"),
            (m3, len(result1.get("weak_points", [])),     "Weak Points",     "#dc2626", "#fef2f2"),
            (m4, len(result1.get("contradictions", [])),  "Contradictions",  "#d97706", "#fffbeb"),
        ]
        for col, val, label, fg, bg in metrics:
            col.markdown(
                f'<div style="background:{bg};border-radius:10px;padding:.8rem;text-align:center;'
                f'border-top:3px solid {fg}">'
                f'<div style="font-size:1.6rem;font-weight:700;color:{fg}">{val}</div>'
                f'<div style="font-size:.72rem;color:#64748b;text-transform:uppercase;letter-spacing:.05em">{label}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        ea_tabs = st.tabs([
            "📌 Key Facts", "✅ Strong Points", "⚠️ Weak Points", "🔄 Contradictions",
            "❓ Missing Facts", "💬 Follow-Up", "🔬 Cross-Examination", "📅 Timeline",
        ])
        with ea_tabs[0]:
            for i, f in enumerate(result1.get("key_facts", []), 1):
                st.markdown(
                    f'<div style="background:#f0f4ff;border-radius:8px;padding:.5rem .9rem;'
                    f'margin-bottom:.3rem;display:flex;gap:.8rem;align-items:flex-start">'
                    f'<span style="font-weight:700;color:#1a2744;flex-shrink:0">{i}.</span>'
                    f'<span style="color:#334155">{f}</span></div>',
                    unsafe_allow_html=True,
                )
        with ea_tabs[1]:
            for s in result1.get("strong_points", []):
                st.success(s)
        with ea_tabs[2]:
            for w in result1.get("weak_points", []):
                st.warning(w)
        with ea_tabs[3]:
            for c in result1.get("contradictions", []):
                with st.expander(f"**{c.get('issue', '')}**"):
                    for t in c.get("conflicting_texts", []):
                        st.markdown(f"- `{t}`")
                    st.markdown(f"**Why it matters:** {c.get('why_it_matters', '')}")
        with ea_tabs[4]:
            for m in result1.get("missing_facts", []):
                st.markdown(f"- {m}")
        with ea_tabs[5]:
            for q in result1.get("follow_up_questions", []):
                st.markdown(f"- {q}")
        with ea_tabs[6]:
            for q in result1.get("cross_examination_questions", []):
                st.markdown(
                    f'<div style="background:#f8fafc;border-radius:8px;padding:.55rem .9rem;'
                    f'margin-bottom:.3rem;border-left:3px solid #1a2744;font-size:.88rem;color:#1e293b">'
                    f'❓ {q}</div>',
                    unsafe_allow_html=True,
                )
        with ea_tabs[7]:
            for t in result1.get("timeline_facts", []):
                st.markdown(f"- {t}")

        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            download_json("📥 Export (.json)", result1, "evidence_analysis.json", key="ea_dl")
        with c2:
            download_docx_from_dict("📝 Download (.docx)", result1, "evidence_analysis.docx",
                                    title="Evidence Analysis", key="ea_dl_docx")
        with c4:
            if st.button("🔄 Reset", key="ea_rst", use_container_width=True):
                st.session_state.pop("ea_result", None)
                st.rerun()
        save_to_matter_ui(dict_to_markdown(result1, title="Evidence Analysis"),
                          "Evidence Analysis", "ea")

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

        score  = r.get("credibility_score", 0)
        rating = r.get("credibility_rating", "—")
        CRED_CFG = {
            "High":   ("#16a34a", "#f0fdf4"),
            "Medium": ("#d97706", "#fffbeb"),
            "Low":    ("#dc2626", "#fef2f2"),
        }
        score_fg, score_bg = CRED_CFG.get(rating, ("#64748b", "#f1f5f9"))

        m1, m2, m3, m4 = st.columns(4)
        wa_metrics = [
            (m1, rating,                                            "Credibility",    score_fg, score_bg),
            (m2, len(r.get("inconsistent_with_facts", [])),        "Contradictions", "#dc2626", "#fef2f2"),
            (m3, len(r.get("internal_inconsistencies", [])),       "Internal Issues","#d97706", "#fffbeb"),
            (m4, len(r.get("gaps_and_omissions", [])),             "Gaps",           "#64748b", "#f1f5f9"),
        ]
        for col, val, label, fg, bg in wa_metrics:
            col.markdown(
                f'<div style="background:{bg};border-radius:10px;padding:.8rem;text-align:center;'
                f'border-top:3px solid {fg}">'
                f'<div style="font-size:1.4rem;font-weight:700;color:{fg}">{val}</div>'
                f'<div style="font-size:.72rem;color:#64748b;text-transform:uppercase;letter-spacing:.05em">{label}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.markdown(f"<br>**Credibility Assessment:** {r.get('credibility_assessment', '')}", unsafe_allow_html=True)

        wa_tabs = st.tabs(["📋 Key Claims", "⚠️ Contradictions", "🔄 Internal Issues",
                            "❓ Gaps", "💡 Motives", "✅ Strong Points", "📝 Deposition Notes"])
        with wa_tabs[0]:
            for c in r.get("key_claims", []):
                st.markdown(f"- {c}")
        with wa_tabs[1]:
            for i in r.get("inconsistent_with_facts", []):
                sev = i.get("significance", "medium")
                fn = st.error if sev == "high" else st.warning
                fn(f"**Claim:** {i.get('claim', '')}  |  **Contradiction:** {i.get('contradiction', '')}")
        with wa_tabs[2]:
            for i in r.get("internal_inconsistencies", []):
                with st.expander(f"Internal conflict: {i.get('issue', '')}"):
                    st.markdown(f"*Text 1:* {i.get('text_1', '')}")
                    st.markdown(f"*Text 2:* {i.get('text_2', '')}")
        with wa_tabs[3]:
            for g in r.get("gaps_and_omissions", []):
                st.warning(g)
        with wa_tabs[4]:
            for m in r.get("possible_motives", []):
                st.info(m)
        with wa_tabs[5]:
            for s in r.get("strong_points", []):
                st.success(s)
        with wa_tabs[6]:
            for n in r.get("deposition_notes", []):
                st.markdown(f"- {n}")

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            download_json("📥 Export (.json)", r, "witness_analysis.json", key="wa_dl")
        with c2:
            download_docx_from_dict("📝 Download (.docx)", r, "witness_analysis.docx",
                                    title="Witness Statement Analysis", key="wa_dl_docx")
        with c4:
            if st.button("🔄 Reset", key="wa_rst", use_container_width=True):
                st.session_state.pop("wa_result", None)
                st.rerun()
        save_to_matter_ui(dict_to_markdown(r, title="Witness Statement Analysis"),
                          "Witness Statement Analysis", "wa")

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

        # Strategy overview card
        st.markdown(
            f'<div style="background:#f0f4ff;border-radius:10px;padding:1rem 1.2rem;'
            f'border-left:4px solid #1a2744;margin-bottom:1rem">'
            f'<div style="font-size:.72rem;font-weight:700;color:#64748b;text-transform:uppercase;'
            f'letter-spacing:.05em;margin-bottom:.4rem">Strategy Overview</div>'
            f'<div style="color:#1a2744">{r.get("strategy_overview", "")}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

        col_o, col_c = st.columns(2)
        col_o.info(f"**Opening:** _{r.get('opening_question', '')}_")
        col_c.success(f"**Closing:** _{r.get('closing_question', '')}_")

        question_sets = r.get("question_sets", [])
        st.markdown("<br>", unsafe_allow_html=True)
        section(f"❓ Question Sets ({len(question_sets)} topics)")

        Q_BADGE = {"leading": ("🔵", "#dbeafe"), "open": ("🟢", "#dcfce7"),
                   "clarification": ("🟡", "#fef9c3"), "challenge": ("🔴", "#fee2e2")}
        for qs in question_sets:
            with st.expander(f"📌 **{qs.get('topic', '')}** — {qs.get('objective', '')}"):
                for i, q in enumerate(qs.get("questions", []), 1):
                    icon, qbg = Q_BADGE.get(q.get("type", ""), ("⚪", "#f1f5f9"))
                    st.markdown(
                        f'<div style="background:{qbg};border-radius:8px;padding:.55rem .9rem;'
                        f'margin-bottom:.4rem">'
                        f'<div style="font-size:.88rem;font-weight:600;color:#1a2744">'
                        f'Q{i} {icon} {q.get("question", "")}</div>'
                        f'<div style="font-size:.76rem;color:#64748b;margin-top:.25rem">'
                        f'Expected: {q.get("expected_answer", "")} · Follow-up: {q.get("follow_up", "")}</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

        if r.get("points_to_establish"):
            section("🎯 Points to Establish")
            for p in r["points_to_establish"]:
                st.markdown(f"- {p}")
        if r.get("traps_to_avoid"):
            section("⚠️ Traps to Avoid")
            for t in r["traps_to_avoid"]:
                st.warning(t)

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            download_json("📥 Export (.json)", r, "cross_examination.json", key="ce_dl")
        with c2:
            download_docx_from_dict("📝 Download (.docx)", r, "cross_examination.docx",
                                    title="Cross-Examination Plan", key="ce_dl_docx")
        with c4:
            if st.button("🔄 Reset", key="ce_rst", use_container_width=True):
                st.session_state.pop("ce_result", None)
                st.rerun()
        save_to_matter_ui(dict_to_markdown(r, title="Cross-Examination Plan"),
                          "Cross-Examination Plan", "ce")
