import streamlit as st
from utils.shared.sidebar import setup_page
from utils.shared.styles import slim_header, disclaimer, section, group_header
from utils.shared.document_input import document_input_ui
from utils.shared.export_utils import download_json, download_docx_from_dict, save_to_matter_ui, dict_to_markdown

from utils.auth import require_lawyer
api_key = setup_page()
require_lawyer()
slim_header("🏛️", "Trial Workspace", "Court document review, filing checklists, timelines, and argument preparation")
disclaimer()

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏛️ Court Document Checker",
    "📅 Matter Timeline",
    "📋 Filing Checklist",
    "💬 Argument Builder",
    "📝 Hearing Prep Notes",
])

# ── 1. Court Document Checker ─────────────────────────────────────
with tab1:
    st.markdown("Review pleadings and submissions for structural issues, missing elements, and weak arguments before filing.")

    from utils.shared.styles import confidentiality_notice
    confidentiality_notice()

    text1 = document_input_ui("cdc", paste_placeholder="Paste your court document here…")
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    doc_type1 = c1.selectbox("Document Type", [
        "Written submissions", "Statement of claim", "Defence", "Affidavit",
        "Witness statement", "Motion / Application", "Appeal brief", "Other",
    ], key="cdc_dt")
    court_jur = c2.text_input("Court / Jurisdiction", placeholder="e.g. High Court, Commercial Court", key="cdc_cj")
    party1 = c3.selectbox("Party Represented", [
        "Claimant / Plaintiff", "Defendant", "Appellant", "Respondent",
        "Prosecutor", "Defence",
    ], key="cdc_pr")
    if st.button("🏛️ Check Document", type="primary", disabled=not api_key, key="cdc_btn"):
        if not text1:
            st.warning("⚠️ Upload or paste a document first.")
        else:
            from utils.court_checker import CourtDocumentChecker
            with st.spinner("Reviewing with Claude Opus 4.7…"):
                try:
                    result1 = CourtDocumentChecker(api_key).check(text1, doc_type1, court_jur, party1)
                    st.session_state.cdc_result = result1
                    st.success("✅ Review complete!")
                except Exception as exc:
                    st.error(f"Review failed: {exc}")
    if st.session_state.get("cdc_result"):
        result1 = st.session_state.cdc_result
        score = result1.get("filing_readiness_score", 0)
        st.divider()
        score_color = "#16a34a" if score >= 80 else "#d97706" if score >= 60 else "#dc2626"
        score_bg    = "#f0fdf4" if score >= 80 else "#fffbeb" if score >= 60 else "#fef2f2"
        s1, s2 = st.columns([1, 3])
        s1.markdown(
            f'<div style="background:{score_bg};border-radius:12px;padding:1.2rem;text-align:center;'
            f'border-top:4px solid {score_color}">'
            f'<div style="font-size:2rem;font-weight:700;color:{score_color}">{score}</div>'
            f'<div style="font-size:.65rem;color:#64748b;text-transform:uppercase;letter-spacing:.06em">out of 100</div>'
            f'<div style="font-size:.75rem;color:{score_color};font-weight:600;margin-top:.3rem">Filing Readiness</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
        s2.markdown(f"**Summary:** {result1.get('executive_summary','')}")
        issue_tabs = st.tabs([
            "🏗️ Structure", "❌ Missing", "⚠️ Weak Arguments",
            "🔍 Unsupported Claims", "📚 Citations", "🗣️ Tone",
            "⚖️ Relief Clarity", "💡 Improvements",
        ])
        for tab, key in zip(issue_tabs, [
            "structural_issues", "missing_elements", "weak_arguments",
            "unsupported_factual_claims", "citation_issues", "tone_issues",
            "relief_clarity_issues", "suggested_improvements",
        ]):
            with tab:
                items = result1.get(key, [])
                if items:
                    for item in items: st.markdown(f"- {item}")
                else:
                    st.success("No issues in this category.")
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        with c1: download_json("📥 Export (.json)", result1, "court_doc_review.json", key="cdc_dl")
        with c2: download_docx_from_dict("📝 Download (.docx)", result1, "court_doc_review.docx",
                                          title="Court Document Review", key="cdc_dl_docx")
        with c4:
            if st.button("🔄 Reset", key="cdc_rst", use_container_width=True):
                st.session_state.pop("cdc_result", None); st.rerun()
        save_to_matter_ui(dict_to_markdown(result1, title="Court Document Review"),
                          "Court Document Review", "cdc")

# ── 2. Matter Timeline ────────────────────────────────────────────
with tab2:
    st.markdown("Extract and organise chronological events from legal documents to build a matter timeline.")
    text2 = document_input_ui("tg", paste_placeholder="Paste statements, correspondence, contracts, or case summaries…")
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    matter_type2 = c1.selectbox("Matter Type", [
        "Civil litigation", "Criminal case", "Arbitration", "Employment dispute",
        "Corporate transaction", "Property matter", "Other",
    ], key="tg_mt")
    date_format2 = c2.selectbox("Date Format", ["DD/MM/YYYY", "MM/DD/YYYY", "YYYY-MM-DD"], key="tg_df")
    if st.button("📅 Generate Timeline", type="primary", disabled=not api_key, key="tg_btn"):
        if not text2:
            st.warning("⚠️ Upload or paste a document first.")
        else:
            from utils.timeline_generator import TimelineGenerator
            with st.spinner("Generating with Claude Opus 4.7…"):
                try:
                    result2 = TimelineGenerator(api_key).generate(text2, matter_type2, date_format2)
                    st.session_state.tg_result = result2
                    st.success("✅ Timeline generated!")
                except Exception as exc:
                    st.error(f"Generation failed: {exc}")
    if st.session_state.get("tg_result"):
        result2 = st.session_state.tg_result
        events = result2.get("timeline", [])
        undated = result2.get("undated_events", [])
        conflicts = result2.get("conflicts", [])
        st.divider()
        m1, m2, m3 = st.columns(3)
        m1.markdown(f'<div class="metric-card"><div class="val">{len(events)}</div><div class="lbl">Dated Events</div></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="metric-card"><div class="val" style="color:#d97706">{len(undated)}</div><div class="lbl">Undated Events</div></div>', unsafe_allow_html=True)
        m3.markdown(f'<div class="metric-card"><div class="val" style="color:#dc2626">{len(conflicts)}</div><div class="lbl">Conflicts</div></div>', unsafe_allow_html=True)
        if events:
            st.markdown("<br>", unsafe_allow_html=True)
            section(f"📅 Timeline ({len(events)} events)")
            SIG_COLORS = {
                "critical":  ("#dc2626", "#fef2f2"),
                "high":      ("#d97706", "#fffbeb"),
                "medium":    ("#2563eb", "#eff6ff"),
                "low":       ("#16a34a", "#f0fdf4"),
            }
            for ev in events:
                sig = (ev.get("significance") or "medium").lower()
                fg, bg = SIG_COLORS.get(sig, ("#64748b", "#f1f5f9"))
                st.markdown(
                    f"""<div style="background:white;border:1px solid #e2e8f0;border-radius:10px;
                                  padding:.75rem 1rem;margin-bottom:.4rem;
                                  display:flex;align-items:flex-start;gap:1rem;flex-wrap:wrap">
                      <div style="min-width:90px;flex-shrink:0">
                        <div style="font-size:.78rem;font-weight:700;color:#1a2744">{ev.get('date','')}</div>
                        <span style="font-size:.68rem;font-weight:700;color:{fg};background:{bg};
                                     padding:.1rem .45rem;border-radius:20px;border:1px solid {fg}30">{sig.title()}</span>
                      </div>
                      <div style="flex:1;min-width:0">
                        <div style="font-size:.88rem;color:#1e293b;font-weight:500">{ev.get('event','')}</div>
                        {f'<div style="font-size:.75rem;color:#94a3b8;margin-top:.2rem">Source: {ev.get("source","")}</div>' if ev.get('source') else ''}
                      </div>
                    </div>""",
                    unsafe_allow_html=True,
                )
        if conflicts:
            st.markdown("<br>", unsafe_allow_html=True)
            section("⚠️ Date Conflicts")
            for c in conflicts: st.error(c)
        if undated:
            st.markdown("<br>", unsafe_allow_html=True)
            section("📌 Undated Events")
            for u in undated: st.markdown(f"- {u}")
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3, c4 = st.columns(4)
        with c1: download_json("📥 Export (.json)", result2, "matter_timeline.json", key="tg_dl")
        with c2: download_docx_from_dict("📝 Download (.docx)", result2, "matter_timeline.docx",
                                          title="Matter Timeline", key="tg_dl_docx")
        with c4:
            if st.button("🔄 Reset", key="tg_rst", use_container_width=True):
                st.session_state.pop("tg_result", None); st.rerun()
        save_to_matter_ui(dict_to_markdown(result2, title="Matter Timeline"),
                          "Matter Timeline", "tg")

# ── 3. Filing Checklist ───────────────────────────────────────────
with tab3:
    st.markdown("Generate a step-by-step court filing checklist for any document type and jurisdiction.")
    c1, c2, c3 = st.columns(3)
    fc_doc_type = c1.selectbox("Document Type", [
        "Claim form", "Defence", "Reply", "Summary judgment application",
        "Injunction application", "Appeal notice", "Witness statement",
        "Skeleton argument", "Expert report", "Court bundle", "Other",
    ], key="fc_dt")
    fc_court    = c2.text_input("Court / Tribunal", placeholder="e.g. High Court, Commercial Court", key="fc_court")
    fc_jur      = c3.selectbox("Jurisdiction", ["England & Wales", "Scotland", "Rwanda",
                                                  "United States", "International / Other"], key="fc_jur")
    fc_summary  = st.text_area("Brief Matter Summary", height=60,
                                placeholder="2-3 sentences about the matter and stage of proceedings", key="fc_sum")
    if st.button("📋 Generate Checklist", type="primary", disabled=not api_key, key="fc_btn"):
        from utils.argument_builder import FilingChecklist
        with st.spinner("Generating with Claude Opus 4.7…"):
            try:
                result3 = FilingChecklist(api_key).generate(fc_doc_type, fc_court, fc_jur, fc_summary)
                st.session_state.fc_result = result3
                st.success("✅ Checklist ready!")
            except Exception as exc:
                st.error(f"Generation failed: {exc}")
    if st.session_state.get("fc_result"):
        r = st.session_state.fc_result
        st.divider()
        st.markdown(f"### {r.get('title','Filing Checklist')}")
        st.markdown(r.get("court_overview",""))
        checklist = r.get("checklist", [])
        if checklist:
            if "fc_completed" not in st.session_state:
                st.session_state.fc_completed = set()

            # Count completed from rendered checkboxes
            completed_count = sum(
                1 for item in checklist
                if st.session_state.get(f"fc_chk_{item.get('step', 0)}", False)
            )
            progress_pct = completed_count / len(checklist) if checklist else 0
            prog_color = "#16a34a" if progress_pct == 1 else "#2563eb" if progress_pct >= 0.5 else "#d97706"

            st.markdown(
                f'<div style="background:#f8fafc;border-radius:10px;padding:.8rem 1rem;margin-bottom:.8rem">'
                f'<div style="display:flex;justify-content:space-between;margin-bottom:.4rem">'
                f'<span style="font-size:.82rem;font-weight:600;color:#1a2744">Checklist Progress</span>'
                f'<span style="font-size:.82rem;color:{prog_color};font-weight:700">{completed_count}/{len(checklist)} steps</span>'
                f'</div>'
                f'<div style="background:#e2e8f0;border-radius:20px;height:8px">'
                f'<div style="background:{prog_color};height:8px;border-radius:20px;width:{progress_pct*100:.0f}%"></div>'
                f'</div></div>',
                unsafe_allow_html=True,
            )

            section(f"✅ Filing Checklist ({len(checklist)} steps)")
            for item in checklist:
                step = item.get("step", 0)
                pri_icon = {"critical": "🔴", "important": "🟡", "standard": "🟢"}.get(item.get("priority",""), "⚪")
                checked = st.checkbox(
                    f"{pri_icon} **Step {step}: {item.get('task','')}**  ·  _{item.get('timing','')}_",
                    key=f"fc_chk_{step}",
                )
                if checked:
                    st.session_state.fc_completed.add(step)
                if item.get("details"):
                    st.caption(f"  {item['details']}")
        if r.get("required_documents"):
            section("📄 Required Documents")
            for d in r["required_documents"]: st.markdown(f"- {d}")
        if r.get("common_errors"):
            section("⚠️ Common Errors to Avoid")
            for e in r["common_errors"]: st.warning(e)
        if r.get("court_fees"):
            section("💷 Court Fees")
            st.markdown(r["court_fees"])
        if r.get("service_requirements"):
            section("📮 Service Requirements")
            st.markdown(r["service_requirements"])
        c1, c2, c3, c4 = st.columns(4)
        with c1: download_json("📥 Export (.json)", r, "filing_checklist.json", key="fc_dl")
        with c2: download_docx_from_dict("📝 Download (.docx)", r, "filing_checklist.docx",
                                          title="Filing Checklist", key="fc_dl_docx")
        with c4:
            if st.button("🔄 Reset", key="fc_rst", use_container_width=True):
                st.session_state.pop("fc_result", None)
                st.session_state.pop("fc_completed", None)
                st.rerun()
        save_to_matter_ui(dict_to_markdown(r, title="Filing Checklist"),
                          f"Filing Checklist — {fc_doc_type}", "fc")

# ── 4. Argument Builder ───────────────────────────────────────────
with tab4:
    st.markdown("Build structured legal arguments using IRAC / CREAC frameworks with counterarguments and authorities.")
    ab_issue    = st.text_area("Legal Issue *", height=60,
                                placeholder="e.g. Whether a binding contract was formed at the meeting on 1 June 2025")
    c1, c2 = st.columns(2)
    ab_outcome  = c1.text_input("Desired Outcome", placeholder="e.g. Establish that a contract was formed")
    ab_framework= c2.selectbox("Argument Framework", ["IRAC", "CREAC", "IRAC with sub-arguments"], key="ab_fw")
    ab_facts    = st.text_area("Key Facts", height=80, placeholder="Relevant facts supporting your argument…")
    c3, c4, c5 = st.columns(3)
    ab_jur      = c3.text_input("Jurisdiction", placeholder="e.g. English law", key="ab_jur")
    ab_type     = c4.selectbox("Case Type", [
        "Civil litigation", "Commercial dispute", "Employment",
        "Criminal", "Administrative / Judicial review", "Arbitration",
    ], key="ab_type")
    if st.button("💬 Build Argument", type="primary", disabled=not api_key, key="ab_btn"):
        if not ab_issue.strip():
            st.warning("⚠️ Enter the legal issue first.")
        else:
            from utils.argument_builder import ArgumentBuilder
            with st.spinner("Building with Claude Opus 4.7…"):
                try:
                    result4 = ArgumentBuilder(api_key).build(
                        ab_issue, ab_facts, ab_outcome, ab_framework, ab_jur, ab_type)
                    st.session_state.ab_result = result4
                    st.success("✅ Argument built!")
                except Exception as exc:
                    st.error(f"Build failed: {exc}")
    if st.session_state.get("ab_result"):
        r = st.session_state.ab_result
        st.divider()
        st.markdown(f"## {r.get('argument_title','')}")
        arg = r.get("structured_argument", {})
        ab_tabs = st.tabs(["🏗️ Structure", "📚 Authorities", "🔄 Sub-Arguments",
                            "⚔️ Counterarguments", "⚠️ Weaknesses", "🗣️ Oral Points", "📄 Full Text"])
        with ab_tabs[0]:
            for label, key in [("Issue", "issue"), ("Rule", "rule"),
                                ("Application", "application"), ("Conclusion", "conclusion")]:
                st.markdown(f"**{label}:**")
                st.markdown(arg.get(key, ""))
                st.markdown("---")
        with ab_tabs[1]:
            for a in r.get("key_authorities", []):
                with st.expander(f"**{a.get('name','')}** `{a.get('citation','')}`"):
                    st.markdown(f"**Principle:** {a.get('principle','')}")
                    st.markdown(f"**How it helps:** {a.get('how_it_helps','')}")
        with ab_tabs[2]:
            for s in r.get("sub_arguments", []):
                with st.expander(f"📌 {s.get('point','')}"):
                    st.markdown(f"**Rule:** {s.get('rule','')}")
                    st.markdown(f"**Application:** {s.get('application','')}")
                    st.markdown(f"**Authority:** _{s.get('authority','')}_")
        with ab_tabs[3]:
            for ca in r.get("counterarguments", []):
                with st.expander(f"⚔️ {ca.get('counterargument','')} ({ca.get('strength','')})"):
                    st.markdown(f"**Rebuttal:** {ca.get('rebuttal','')}")
        with ab_tabs[4]:
            for w in r.get("weaknesses", []): st.warning(w)
        with ab_tabs[5]:
            for p in r.get("oral_advocacy_points", []):
                st.markdown(f"→ {p}")
        with ab_tabs[6]:
            st.markdown(r.get("full_written_argument",""))
        c1, c2, c3, c4 = st.columns(4)
        with c1: download_json("📥 Export (.json)", r, "legal_argument.json", key="ab_dl")
        with c2: download_docx_from_dict("📝 Download (.docx)", r, "legal_argument.docx",
                                          title="Legal Argument", key="ab_dl_docx")
        with c4:
            if st.button("🔄 Reset", key="ab_rst", use_container_width=True):
                st.session_state.pop("ab_result", None); st.rerun()
        save_to_matter_ui(dict_to_markdown(r, title="Legal Argument"),
                          f"Legal Argument — {ab_issue[:50]}", "ab")

# ── 5. Hearing Prep Notes ─────────────────────────────────────────
with tab5:
    st.markdown("Generate structured hearing preparation notes including opening, key arguments, and anticipated questions.")
    hp_summary = st.text_area("Matter Summary *", height=80,
                               placeholder="Brief overview of the case, stage, and what this hearing decides")
    hp_issues  = st.text_area("Key Issues for This Hearing", height=60,
                               placeholder="e.g. (1) Whether injunction should be granted, (2) Costs")
    c1, c2, c3 = st.columns(3)
    hp_type    = c1.selectbox("Hearing Type", [
        "Case management hearing", "Injunction application", "Summary judgment",
        "Trial", "Appeal hearing", "Arbitration hearing", "Costs hearing", "Other",
    ], key="hp_type")
    hp_jur     = c2.text_input("Jurisdiction", placeholder="e.g. High Court, England", key="hp_jur")
    hp_judge   = c3.text_input("Judge / Tribunal Notes", placeholder="e.g. Known to be strict on costs", key="hp_judge")
    if st.button("📝 Generate Hearing Prep Notes", type="primary", disabled=not api_key, key="hp_btn"):
        if not hp_summary.strip():
            st.warning("⚠️ Enter a matter summary first.")
        else:
            from utils.argument_builder import HearingPrepGenerator
            with st.spinner("Generating with Claude Opus 4.7…"):
                try:
                    result5 = HearingPrepGenerator(api_key).generate(
                        hp_summary, hp_issues, hp_type, hp_judge, hp_jur)
                    st.session_state.hp_result = result5
                    st.success("✅ Hearing notes ready!")
                except Exception as exc:
                    st.error(f"Generation failed: {exc}")
    if st.session_state.get("hp_result"):
        r = st.session_state.hp_result
        st.divider()
        st.markdown(f"**Hearing Overview:** {r.get('hearing_overview','')}")
        hp_tabs = st.tabs(["🎯 Objectives", "🗣️ Opening", "⚖️ Arguments", "❓ Questions",
                            "📜 Closing", "✅ Logistics"])
        with hp_tabs[0]:
            for i, obj in enumerate(r.get("objectives",[]), 1):
                st.markdown(f"**{i}.** {obj}")
        with hp_tabs[1]:
            st.markdown(r.get("opening_statement",""))
        with hp_tabs[2]:
            for arg in r.get("key_arguments", []):
                with st.expander(f"📌 {arg.get('argument','')}"):
                    st.markdown(f"**Authority:** {arg.get('supporting_authority','')}")
                    st.markdown(f"**Evidence:** {arg.get('evidence_reference','')}")
                    st.markdown(f"**Anticipated Response:** {arg.get('anticipated_response','')}")
        with hp_tabs[3]:
            for q in r.get("anticipated_questions", []):
                with st.expander(f"❓ {q.get('question','')}"):
                    st.markdown(q.get("answer",""))
            if r.get("concessions_to_make"):
                section("✅ Safe Concessions")
                for c in r["concessions_to_make"]: st.info(c)
            if r.get("lines_to_hold"):
                section("🛑 Lines to Hold")
                for l in r["lines_to_hold"]: st.error(l)
        with hp_tabs[4]:
            st.markdown(r.get("closing_summary",""))
        with hp_tabs[5]:
            for item in r.get("logistics_checklist",[]): st.checkbox(item, key=f"hp_log_{item[:20]}")
        c1, c2, c3, c4 = st.columns(4)
        with c1: download_json("📥 Export (.json)", r, "hearing_prep.json", key="hp_dl")
        with c2: download_docx_from_dict("📝 Download (.docx)", r, "hearing_prep.docx",
                                          title="Hearing Preparation Notes", key="hp_dl_docx")
        with c4:
            if st.button("🔄 Reset", key="hp_rst", use_container_width=True):
                st.session_state.pop("hp_result", None); st.rerun()
        save_to_matter_ui(dict_to_markdown(r, title="Hearing Preparation Notes"),
                          f"Hearing Prep — {hp_type}", "hp")
