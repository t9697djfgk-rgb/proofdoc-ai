import streamlit as st
from utils.shared.sidebar import setup_page
from utils.shared.styles import slim_header, disclaimer, section, placeholder_feature, group_header
from utils.shared.document_input import document_input_ui
from utils.shared.export_utils import download_json

api_key = setup_page()
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
        s1, s2 = st.columns([1, 3])
        s1.markdown(
            f'<div class="metric-card"><div class="val" style="color:{score_color}">{score}/100</div>'
            f'<div class="lbl">Filing Readiness</div></div>',
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
        c1, _, c3 = st.columns(3)
        with c1: download_json("📥 Download Review Report (.json)", result1, "court_doc_review.json", key="cdc_dl")
        with c3:
            if st.button("🔄 Reset", key="cdc_rst", use_container_width=True):
                st.session_state.pop("cdc_result", None); st.rerun()

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
            hdr = st.columns([2, 4, 2, 2])
            for col, lbl in zip(hdr, ["Date", "Event", "Significance", "Source"]):
                col.markdown(f"**{lbl}**")
            st.divider()
            for ev in events:
                row = st.columns([2, 4, 2, 2])
                row[0].markdown(f"**{ev.get('date','')}**")
                row[1].markdown(ev.get("event",""))
                row[2].markdown(ev.get("significance",""))
                row[3].markdown(f'<span style="color:#94a3b8;font-size:0.8rem">{ev.get("source","")}</span>', unsafe_allow_html=True)
                st.markdown('<hr style="margin:0.25rem 0;border-color:#f1f5f9">', unsafe_allow_html=True)
        if conflicts:
            st.markdown("<br>", unsafe_allow_html=True)
            section("⚠️ Date Conflicts")
            for c in conflicts: st.error(c)
        if undated:
            st.markdown("<br>", unsafe_allow_html=True)
            section("📌 Undated Events")
            for u in undated: st.markdown(f"- {u}")
        st.markdown("<br>", unsafe_allow_html=True)
        c1, _, c3 = st.columns(3)
        with c1: download_json("📥 Download Timeline (.json)", result2, "matter_timeline.json", key="tg_dl")
        with c3:
            if st.button("🔄 Reset", key="tg_rst", use_container_width=True):
                st.session_state.pop("tg_result", None); st.rerun()

# ── 3. Filing Checklist (placeholder) ────────────────────────────
with tab3:
    placeholder_feature(
        "📋", "Court Filing Checklist",
        "Generate a jurisdiction-specific filing checklist for any court document or application.",
        ["Select court and document type", "Receive step-by-step filing checklist",
         "Attach required supporting documents", "Track completion and sign off"],
        ["Itemised filing checklist", "Required attachments list",
         "Court fees schedule", "Filing confirmation log"],
    )

# ── 4. Argument Builder (placeholder) ────────────────────────────
with tab4:
    placeholder_feature(
        "💬", "Argument Builder",
        "Structure legal arguments for submissions, memos, or oral advocacy using IRAC and CREAC frameworks.",
        ["Enter issue, rule, and facts", "AI structures argument in IRAC / CREAC format",
         "Anticipate counterarguments and rebuttals", "Export as submission-ready section"],
        ["Structured legal argument", "Counterarguments and rebuttals",
         "Authority references per point", "Argument outline for oral advocacy"],
    )

# ── 5. Hearing Prep Notes (placeholder) ─────────────────────────
with tab5:
    placeholder_feature(
        "📝", "Hearing Preparation Notes",
        "Prepare structured hearing notes covering key arguments, evidence, and anticipated questions.",
        ["Enter matter summary and key issues", "AI drafts structured hearing notes",
         "Include key authorities and evidential references", "Add judge/arbitrator background notes"],
        ["Hearing prep document", "Key argument one-pagers", "Anticipated questions list",
         "Evidence reference index"],
    )
