import streamlit as st
from utils.shared.sidebar import setup_page
from utils.shared.styles import (
    slim_header, disclaimer, section, risk_badge, placeholder_feature,
)
from utils.shared.document_input import document_input_ui
from utils.shared.export_utils import action_row, download_json, download_txt

api_key = setup_page()
slim_header("🔍", "Review", "AI-powered legal document review — grammar, risk, citations, and deadlines")
disclaimer()

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "✍️ Legal English Reviewer",
    "⚠️ Contract Risk Checker",
    "📚 Citation Checker",
    "⏰ Deadline Extractor",
    "🔍 Issue Spotter",
])

# ── 1. Legal English Reviewer ────────────────────────────────────
with tab1:
    st.markdown("Review grammar, style, and legal clarity. Get risk-flagged edit suggestions and a clean revised version.")
    text = document_input_ui("ler", paste_placeholder="Paste your legal document, clause, or submission here…")
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    review_type = c1.selectbox("Review Type", [
        "Legal English polish", "Grammar only", "Contract drafting review",
        "Academic legal writing", "Court submission review", "Plain-English rewrite",
    ], key="ler_rt")
    legal_style = c2.selectbox("Legal Style", [
        "UK legal English", "US legal English",
        "International legal English", "Academic legal English",
    ], key="ler_ls")
    if st.button("✍️ Review Document", type="primary", disabled=not api_key, key="ler_btn"):
        if not text:
            st.warning("⚠️ Upload or paste a document first.")
        else:
            from utils.legal_reviewer import LegalReviewer
            with st.spinner("Reviewing with Claude Opus 4.7…"):
                try:
                    result = LegalReviewer(api_key).review(text, review_type, legal_style)
                    st.session_state.ler_result = result
                    st.success("✅ Review complete!")
                except Exception as exc:
                    st.error(f"Review failed: {exc}")
    if st.session_state.get("ler_result"):
        result = st.session_state.ler_result
        summary = result.get("summary", {})
        edits = result.get("edits", [])
        revised = result.get("revised_document", "")
        st.divider()
        s1, s2, s3, s4, s5 = st.columns(5)
        s1.markdown(f'<div class="metric-card"><div class="val">{summary.get("total_issues",0)}</div><div class="lbl">Total Issues</div></div>', unsafe_allow_html=True)
        s2.markdown(f'<div class="metric-card"><div class="val">{summary.get("grammar_issues",0)}</div><div class="lbl">Grammar</div></div>', unsafe_allow_html=True)
        s3.markdown(f'<div class="metric-card"><div class="val">{summary.get("style_issues",0)}</div><div class="lbl">Style</div></div>', unsafe_allow_html=True)
        s4.markdown(f'<div class="metric-card"><div class="val">{summary.get("legal_clarity_issues",0)}</div><div class="lbl">Legal Clarity</div></div>', unsafe_allow_html=True)
        s5.markdown(f'<div class="metric-card"><div class="val" style="color:#dc2626">{summary.get("high_risk_edits",0)}</div><div class="lbl">High Risk</div></div>', unsafe_allow_html=True)
        if edits:
            st.markdown("<br>", unsafe_allow_html=True)
            section(f"📝 Suggested Edits ({len(edits)})")
            hdr = st.columns([2.5, 2.5, 1.5, 1, 3])
            for col, lbl in zip(hdr, ["Original", "Correction", "Issue Type", "Risk", "Explanation"]):
                col.markdown(f"**{lbl}**")
            st.divider()
            for edit in edits:
                risk = edit.get("risk_level", "low").lower()
                risk_cls = {"high": "risk-high", "medium": "risk-medium"}.get(risk, "risk-low")
                issue = edit.get("issue_type", "").replace("_", " ").title()
                row = st.columns([2.5, 2.5, 1.5, 1, 3])
                row[0].markdown(f'<span style="color:#64748b">{edit.get("original_text","")}</span>', unsafe_allow_html=True)
                row[1].markdown(f'**{edit.get("suggested_correction","")}**')
                row[2].markdown(f'<span class="issue-badge">{issue}</span>', unsafe_allow_html=True)
                row[3].markdown(f'<span class="{risk_cls}">{risk.title()}</span>', unsafe_allow_html=True)
                row[4].markdown(edit.get("explanation", ""))
                st.markdown('<hr style="margin:0.25rem 0;border-color:#f1f5f9">', unsafe_allow_html=True)
        if revised:
            st.markdown("<br>", unsafe_allow_html=True)
            section("📄 Clean Revised Version")
            st.markdown(f'<div class="revised-doc">{revised.replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            action_row(text_to_download=revised, base_filename="legal_review",
                       report_data=result, reset_keys=["ler_result"], key_prefix="ler")

# ── 2. Contract Risk Checker ──────────────────────────────────────
with tab2:
    st.markdown("Identify legal and commercial risks, missing clauses, and negotiation points in any contract.")
    text2 = document_input_ui("crc", paste_placeholder="Paste the contract text here…")
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    contract_type = c1.selectbox("Contract Type", [
        "Service agreement", "NDA", "Employment contract", "SPA",
        "Shareholder agreement", "Loan agreement", "Lease", "Other",
    ], key="crc_ct")
    client_pos = c2.selectbox("Client Position", [
        "Buyer", "Seller", "Service provider", "Client/Customer",
        "Employer", "Employee", "Lender", "Borrower", "Neutral",
    ], key="crc_cp")
    jurisdiction = c3.text_input("Jurisdiction", placeholder="e.g. English law, Rwandan law", key="crc_jur")
    if st.button("⚠️ Check Contract Risks", type="primary", disabled=not api_key, key="crc_btn"):
        if not text2:
            st.warning("⚠️ Upload or paste a contract first.")
        else:
            from utils.contract_risk import ContractRiskChecker
            with st.spinner("Analysing with Claude Opus 4.7…"):
                try:
                    result2 = ContractRiskChecker(api_key).check(text2, contract_type, client_pos, jurisdiction)
                    st.session_state.crc_result = result2
                    st.success("✅ Risk check complete!")
                except Exception as exc:
                    st.error(f"Check failed: {exc}")
    if st.session_state.get("crc_result"):
        result2 = st.session_state.crc_result
        risks = result2.get("risks", [])
        missing = result2.get("missing_clauses", [])
        nego = result2.get("negotiation_points", [])
        st.divider()
        m1, m2, m3, m4 = st.columns(4)
        m1.markdown(f'<div class="metric-card"><div class="val">{result2.get("overall_risk","—")}</div><div class="lbl">Overall Risk</div></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="metric-card"><div class="val" style="color:#dc2626">{len(risks)}</div><div class="lbl">Risks Found</div></div>', unsafe_allow_html=True)
        m3.markdown(f'<div class="metric-card"><div class="val" style="color:#d97706">{len(missing)}</div><div class="lbl">Missing Clauses</div></div>', unsafe_allow_html=True)
        m4.markdown(f'<div class="metric-card"><div class="val">{len(nego)}</div><div class="lbl">Negotiation Points</div></div>', unsafe_allow_html=True)
        tabs_r = st.tabs(["🚨 Risks", "❌ Missing Clauses", "💬 Negotiation Points", "✅ Strengths"])
        with tabs_r[0]:
            if risks:
                for r in risks:
                    row = st.columns([2, 4, 2, 1])
                    row[0].markdown(f"**{r.get('clause','')}**")
                    row[1].markdown(r.get("risk",""))
                    row[2].markdown(r.get("recommendation",""))
                    row[3].markdown(risk_badge(r.get("severity","medium")), unsafe_allow_html=True)
                    st.markdown('<hr style="margin:0.25rem 0;border-color:#f1f5f9">', unsafe_allow_html=True)
            else:
                st.success("No significant risks found.")
        with tabs_r[1]:
            for m in missing: st.warning(m)
        with tabs_r[2]:
            for n in nego: st.markdown(f"- {n}")
        with tabs_r[3]:
            for s in result2.get("strengths", []): st.success(s)
        st.markdown("<br>", unsafe_allow_html=True)
        c1, _, c3 = st.columns(3)
        with c1: download_json("📥 Download Report (.json)", result2, "contract_risk.json", key="crc_dl")
        with c3:
            if st.button("🔄 Reset", key="crc_rst", use_container_width=True):
                st.session_state.pop("crc_result", None); st.rerun()

# ── 3. Citation Checker ───────────────────────────────────────────
with tab3:
    st.markdown("Validate citation format, consistency, and completeness against OSCOLA, Bluebook, or APA.")
    text3 = document_input_ui("cc", paste_placeholder="Paste legal text containing citations…")
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    cite_style = c1.selectbox("Citation Style", ["OSCOLA", "Bluebook", "APA", "AGLC", "Other"], key="cc_cs")
    jur3 = c2.text_input("Jurisdiction", placeholder="e.g. UK, US, Australia", key="cc_jur")
    if st.button("📚 Check Citations", type="primary", disabled=not api_key, key="cc_btn"):
        if not text3:
            st.warning("⚠️ Upload or paste a document first.")
        else:
            from utils.citation_checker import CitationChecker
            with st.spinner("Checking with Claude Opus 4.7…"):
                try:
                    result3 = CitationChecker(api_key).check(text3, cite_style, jur3)
                    st.session_state.cc_result = result3
                    st.success("✅ Citation check complete!")
                except Exception as exc:
                    st.error(f"Check failed: {exc}")
    if st.session_state.get("cc_result"):
        result3 = st.session_state.cc_result
        issues = result3.get("issues", [])
        summ3 = result3.get("summary", {})
        st.divider()
        m1, m2, m3 = st.columns(3)
        m1.markdown(f'<div class="metric-card"><div class="val">{summ3.get("total_citations",0)}</div><div class="lbl">Citations Found</div></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="metric-card"><div class="val" style="color:#dc2626">{summ3.get("errors",0)}</div><div class="lbl">Errors</div></div>', unsafe_allow_html=True)
        m3.markdown(f'<div class="metric-card"><div class="val" style="color:#d97706">{summ3.get("warnings",0)}</div><div class="lbl">Warnings</div></div>', unsafe_allow_html=True)
        if issues:
            st.markdown("<br>", unsafe_allow_html=True)
            section(f"📋 Citation Issues ({len(issues)})")
            for issue in issues:
                sev = issue.get("severity", "warning")
                fn = st.error if sev == "error" else st.warning
                fn(f"**{issue.get('citation','')}** — {issue.get('issue','')} · *Fix:* {issue.get('correction','')}")
        else:
            st.success("All citations look correct!")
        st.markdown("<br>", unsafe_allow_html=True)
        c1, _, c3 = st.columns(3)
        with c1: download_json("📥 Download Report (.json)", result3, "citation_report.json", key="cc_dl")
        with c3:
            if st.button("🔄 Reset", key="cc_rst", use_container_width=True):
                st.session_state.pop("cc_result", None); st.rerun()

# ── 4. Deadline & Obligation Extractor ───────────────────────────
with tab4:
    st.markdown("Extract all obligations, deadlines, and compliance duties from contracts, court orders, and regulations.")
    text4 = document_input_ui("de", paste_placeholder="Paste your contract, court order, or regulation here…")
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    doc_type4 = c1.selectbox("Document Type", [
        "Contract", "Court order", "Regulation", "Policy",
        "Legal letter", "Settlement agreement", "Other",
    ], key="de_dt")
    party4 = c2.text_input("Party Perspective", placeholder="e.g. Service Provider, Buyer, Defendant", key="de_pp")
    if st.button("⏰ Extract Obligations & Deadlines", type="primary", disabled=not api_key, key="de_btn"):
        if not text4:
            st.warning("⚠️ Upload or paste a document first.")
        else:
            from utils.deadline_extractor import DeadlineExtractor
            with st.spinner("Extracting with Claude Opus 4.7…"):
                try:
                    result4 = DeadlineExtractor(api_key).extract(text4, doc_type4, party4)
                    st.session_state.de_result = result4
                    st.success("✅ Extraction complete!")
                except Exception as exc:
                    st.error(f"Extraction failed: {exc}")
    if st.session_state.get("de_result"):
        result4 = st.session_state.de_result
        obligations = result4.get("obligations", [])
        deadlines = result4.get("deadlines", [])
        unclear = result4.get("unclear_deadlines", [])
        st.divider()
        m1, m2, m3 = st.columns(3)
        m1.markdown(f'<div class="metric-card"><div class="val">{len(obligations)}</div><div class="lbl">Obligations</div></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="metric-card"><div class="val">{len(deadlines)}</div><div class="lbl">Deadlines</div></div>', unsafe_allow_html=True)
        m3.markdown(f'<div class="metric-card"><div class="val" style="color:#d97706">{len(unclear)}</div><div class="lbl">Unclear</div></div>', unsafe_allow_html=True)
        if obligations:
            st.markdown("<br>", unsafe_allow_html=True)
            section(f"⚖️ Obligations ({len(obligations)})")
            hdr = st.columns([1.5, 3, 2, 1.5, 2, 1])
            for col, lbl in zip(hdr, ["Party", "Obligation", "Trigger", "Deadline", "Consequence", "Priority"]):
                col.markdown(f"**{lbl}**")
            st.divider()
            for ob in obligations:
                row = st.columns([1.5, 3, 2, 1.5, 2, 1])
                row[0].markdown(ob.get("responsible_party",""))
                row[1].markdown(ob.get("obligation",""))
                row[2].markdown(ob.get("trigger_event",""))
                row[3].markdown(f"**{ob.get('deadline_or_date','')}**")
                row[4].markdown(ob.get("consequence",""))
                row[5].markdown(risk_badge(ob.get("priority","medium")), unsafe_allow_html=True)
                st.markdown('<hr style="margin:0.25rem 0;border-color:#f1f5f9">', unsafe_allow_html=True)
        if deadlines:
            st.markdown("<br>", unsafe_allow_html=True)
            section(f"📅 Deadlines ({len(deadlines)})")
            hdr2 = st.columns([2, 3, 2, 1])
            for col, lbl in zip(hdr2, ["Date / Period", "Action Required", "Party", "Priority"]):
                col.markdown(f"**{lbl}**")
            st.divider()
            for dl in deadlines:
                row = st.columns([2, 3, 2, 1])
                row[0].markdown(f"**{dl.get('date_or_period','')}**")
                row[1].markdown(dl.get("action_required",""))
                row[2].markdown(dl.get("responsible_party",""))
                row[3].markdown(risk_badge(dl.get("priority","medium")), unsafe_allow_html=True)
                st.markdown('<hr style="margin:0.25rem 0;border-color:#f1f5f9">', unsafe_allow_html=True)
        if unclear:
            st.markdown("<br>", unsafe_allow_html=True)
            section("⚠️ Unclear / Conditional")
            for u in unclear: st.warning(u)
        dl_text = "\n".join(
            f"{dl.get('date_or_period','?')} — {dl.get('action_required','')} [{dl.get('responsible_party','')}]"
            for dl in deadlines
        )
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, _, c4 = st.columns(4)
        with c1: download_txt("📥 Export Deadlines (.txt)", dl_text, "deadlines.txt", key="de_txt")
        with c2: download_json("📊 Export Full Report (.json)", result4, "obligations_report.json", key="de_json")
        with c4:
            if st.button("🔄 Reset", use_container_width=True, key="de_rst"):
                st.session_state.pop("de_result", None); st.rerun()

# ── 5. Legal Issue Spotter ────────────────────────────────────────
with tab5:
    st.markdown("Automatically identify and categorise all legal issues, ambiguities, and drafting problems in any document.")
    text5 = document_input_ui("is", paste_placeholder="Paste any legal document, contract, or submission here…")
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    is_doc_type = c1.selectbox("Document Type", [
        "Contract", "Court pleading", "Legislation / Policy", "Legal letter",
        "Shareholder agreement", "Employment document", "Property document", "Other",
    ], key="is_dt")
    is_jur = c2.text_input("Jurisdiction", placeholder="e.g. UK, Rwandan law", key="is_jur")
    is_persp = c3.selectbox("Perspective", [
        "Neutral review", "Claimant / Buyer", "Defendant / Seller",
        "Employer", "Employee", "Lender", "Borrower",
    ], key="is_persp")
    if st.button("🔍 Spot Legal Issues", type="primary", disabled=not api_key, key="is_btn"):
        if not text5:
            st.warning("⚠️ Upload or paste a document first.")
        else:
            from utils.issue_spotter import IssueSpotter
            with st.spinner("Analysing with Claude Opus 4.7…"):
                try:
                    result5 = IssueSpotter(api_key).spot(text5, is_doc_type, is_jur, is_persp)
                    st.session_state.is_result = result5
                    st.success("✅ Analysis complete!")
                except Exception as exc:
                    st.error(f"Analysis failed: {exc}")
    if st.session_state.get("is_result"):
        result5 = st.session_state.is_result
        issues = result5.get("issues", [])
        st.divider()
        risk_color = {"critical": "#dc2626", "high": "#d97706", "medium": "#2563eb", "low": "#16a34a"}
        m1, m2, m3, m4 = st.columns(4)
        m1.markdown(f'<div class="metric-card"><div class="val">{len(issues)}</div><div class="lbl">Issues Found</div></div>', unsafe_allow_html=True)
        critical = len([i for i in issues if i.get("severity") == "critical"])
        high = len([i for i in issues if i.get("severity") == "high"])
        m2.markdown(f'<div class="metric-card"><div class="val" style="color:#dc2626">{critical}</div><div class="lbl">Critical</div></div>', unsafe_allow_html=True)
        m3.markdown(f'<div class="metric-card"><div class="val" style="color:#d97706">{high}</div><div class="lbl">High</div></div>', unsafe_allow_html=True)
        m4.markdown(f'<div class="metric-card"><div class="val">{result5.get("risk_level","—").title()}</div><div class="lbl">Overall Risk</div></div>', unsafe_allow_html=True)
        st.markdown(f"**Assessment:** {result5.get('summary','')}")
        if result5.get("priority_actions"):
            st.markdown("<br>", unsafe_allow_html=True)
            section("🚨 Priority Actions")
            for a in result5["priority_actions"]: st.error(f"→ {a}")
        if issues:
            st.markdown("<br>", unsafe_allow_html=True)
            section(f"📋 Issues Register ({len(issues)})")
            hdr = st.columns([1.5, 1.5, 3, 3, 1])
            for col, lbl in zip(hdr, ["Category", "Clause", "Issue", "Remedy", "Severity"]):
                col.markdown(f"**{lbl}**")
            st.divider()
            for issue in issues:
                sev = issue.get("severity", "medium").lower()
                row = st.columns([1.5, 1.5, 3, 3, 1])
                row[0].markdown(issue.get("category", ""))
                row[1].markdown(f'<span style="color:#64748b;font-size:0.85rem">{issue.get("clause_reference","N/A")}</span>', unsafe_allow_html=True)
                row[2].markdown(issue.get("description", ""))
                row[3].markdown(issue.get("remedy", ""))
                row[4].markdown(risk_badge(sev), unsafe_allow_html=True)
                st.markdown('<hr style="margin:0.25rem 0;border-color:#f1f5f9">', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        c1, _, c3 = st.columns(3)
        with c1: download_json("📥 Download Issues Report (.json)", result5, "legal_issues.json", key="is_dl")
        with c3:
            if st.button("🔄 Reset", key="is_rst", use_container_width=True):
                st.session_state.pop("is_result", None); st.rerun()
