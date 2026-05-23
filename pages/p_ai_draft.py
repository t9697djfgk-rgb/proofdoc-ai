import streamlit as st
from utils.shared.sidebar import setup_page
from utils.shared.styles import slim_header, disclaimer, section, placeholder_feature
from utils.shared.export_utils import action_row, download_json

from utils.auth import require_lawyer
api_key = setup_page()
require_lawyer()
slim_header("📝", "Draft", "AI-assisted legal drafting — documents, memos, clauses, and policies")
disclaimer()

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📝 Drafting Assistant",
    "📄 Legal Memo",
    "📖 Clause Library",
    "🛡️ Compliance Policy",
    "🏛️ Court Document Drafting",
    "🔧 Template Builder",
])

# ── 1. Legal Drafting Assistant ───────────────────────────────────
with tab1:
    st.markdown(
        '<div class="notice-box">ℹ️ This tool drafts from the facts you provide. '
        "Verify all cited law and review before sending.</div>",
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns(3)
    doc_type = c1.selectbox("Document Type", [
        "NDA / Confidentiality agreement", "Service agreement", "Employment contract",
        "Shareholder agreement", "Loan agreement", "Settlement agreement",
        "Legal letter / Demand letter", "Terms and conditions", "Other",
    ], key="da_dt")
    jurisdiction = c2.selectbox("Jurisdiction", [
        "International / Neutral", "UK", "US", "EU", "Rwanda", "Other",
    ], key="da_jur")
    legal_style = c3.selectbox("Legal Style", [
        "Plain English", "Formal commercial", "Formal litigation", "Academic",
    ], key="da_ls")
    parties = st.text_area("Parties", height=60,
        placeholder="e.g. Party A: ABC Ltd (service provider); Party B: XYZ Corp (client)", key="da_p")
    key_facts = st.text_area("Key Facts / Instructions *", height=120,
        placeholder="Describe the deal, relationship, key terms, and any special conditions…", key="da_kf")
    c1b, c2b = st.columns(2)
    tone = c1b.selectbox("Tone", ["Formal", "Balanced", "Protective / Conservative"], key="da_tone")
    additional = c2b.text_area("Additional Instructions", height=60,
        placeholder="Any clauses to include/exclude, specific language requirements…", key="da_add")
    if st.button("📝 Generate Draft", type="primary", disabled=not api_key, key="da_btn"):
        if not key_facts.strip():
            st.warning("⚠️ Key facts are required.")
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
        doc_text = result.get("document", "")
        st.divider()
        section(f"📄 {result.get('title', doc_type)}")
        if doc_text:
            st.markdown(f'<div class="revised-doc">{doc_text.replace(chr(10),"<br>")}</div>',
                        unsafe_allow_html=True)
        tabs_d = st.tabs(["💡 Assumptions Made", "❓ Missing Info", "⚠️ Risk Notes", "📌 Optional Clauses"])
        with tabs_d[0]:
            for a in result.get("assumptions", []): st.markdown(f"- {a}")
        with tabs_d[1]:
            for m in result.get("missing_info", []): st.warning(m)
        with tabs_d[2]:
            for r in result.get("risk_notes", []): st.error(r)
        with tabs_d[3]:
            for o in result.get("optional_clauses", []): st.markdown(f"- {o}")
        st.markdown("<br>", unsafe_allow_html=True)
        action_row(text_to_download=doc_text, base_filename="legal_draft",
                   report_data=result, reset_keys=["da_result"], key_prefix="da")

# ── 2. Legal Memo Generator ───────────────────────────────────────
with tab2:
    st.markdown(
        '<div class="notice-box">ℹ️ This tool drafts legal memos from the facts provided. '
        "Verify all cited authorities independently.</div>",
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns(3)
    memo_type = c1.selectbox("Memo Type", [
        "Objective memo", "Persuasive memo", "Internal research memo",
        "Client advice memo", "Academic memo",
    ], key="lm_mt")
    jur_m = c2.selectbox("Jurisdiction", [
        "International / Neutral", "UK", "US", "EU", "Rwanda", "Other",
    ], key="lm_jur")
    client_pos_m = c3.text_input("Client Position / Party", placeholder="e.g. Claimant, Respondent", key="lm_cp")
    legal_issue = st.text_area("Legal Issue / Question *", height=80,
        placeholder="e.g. Whether the non-compete clause is enforceable under English law…", key="lm_li")
    facts = st.text_area("Key Facts *", height=120,
        placeholder="Describe the relevant facts chronologically…", key="lm_f")
    research_notes = st.text_area("Relevant Law / Research Notes", height=100,
        placeholder="List relevant cases, statutes, and key legal principles…", key="lm_rn")
    if st.button("📄 Generate Memo", type="primary", disabled=not api_key, key="lm_btn"):
        if not legal_issue.strip() or not facts.strip():
            st.warning("⚠️ Legal issue and facts are required.")
        else:
            from utils.legal_memo import LegalMemoGenerator
            with st.spinner("Drafting memo with Claude Opus 4.7…"):
                try:
                    result_m = LegalMemoGenerator(api_key).generate(
                        legal_issue, facts, jur_m, research_notes, client_pos_m, memo_type
                    )
                    st.session_state.lm_result = result_m
                    st.success("✅ Memo generated!")
                except Exception as exc:
                    st.error(f"Generation failed: {exc}")
    if st.session_state.get("lm_result"):
        result_m = st.session_state.lm_result
        st.divider()
        section("📄 Legal Memorandum")
        full_memo = ""
        for label, key in [
            ("⚖️ Issue", "issue"), ("💡 Brief Answer", "brief_answer"),
            ("📋 Facts", "facts"), ("📚 Applicable Law", "applicable_law"),
            ("🔍 Analysis", "analysis"), ("🔄 Counterarguments", "counterarguments"),
            ("🏁 Conclusion", "conclusion"),
        ]:
            content = result_m.get(key, "")
            if content:
                st.markdown(f"### {label}")
                st.markdown(content)
                full_memo += f"{label}\n{'='*40}\n{content}\n\n"
        for r in result_m.get("risks", []): st.warning(r)
        for r in result_m.get("recommendations", []): st.markdown(f"- {r}")
        st.markdown("<br>", unsafe_allow_html=True)
        action_row(text_to_download=full_memo, base_filename="legal_memo",
                   report_data=result_m, reset_keys=["lm_result"], key_prefix="lm")

# ── 3. Clause Library ─────────────────────────────────────────────
with tab3:
    from utils.clause_library import (
        CATEGORIES, JURISDICTIONS, get_all, search, add_clause, update_clause, delete_clause,
    )
    cl_search, cl_add = st.tabs(["🔍 Browse & Search", "➕ Add Clause"])

    with cl_search:
        sc1, sc2, sc3 = st.columns(3)
        search_q = sc1.text_input("Search clauses", placeholder="e.g. force majeure, termination", key="cl_sq")
        cat_filter = sc2.selectbox("Category", ["All"] + CATEGORIES, key="cl_cf")
        jur_filter = sc3.selectbox("Jurisdiction", ["All"] + JURISDICTIONS, key="cl_jf")
        clauses = (
            search(search_q, None if cat_filter == "All" else cat_filter,
                   None if jur_filter == "All" else jur_filter)
            if search_q else get_all(None if cat_filter == "All" else cat_filter,
                                     None if jur_filter == "All" else jur_filter)
        )
        st.caption(f"{len(clauses)} clause(s) found")
        for cl in clauses:
            with st.expander(f"**{cl.get('name','')}** · {cl.get('category','')} · {cl.get('jurisdiction','')}"):
                st.markdown(f'<div class="revised-doc">{cl.get("text","")}</div>', unsafe_allow_html=True)
                if cl.get("notes"): st.caption(f"📝 Notes: {cl['notes']}")
                approved = cl.get("approved", False)
                st.markdown(
                    f'<span class="badge-available">✅ Approved</span>' if approved
                    else '<span class="badge-soon">◌ Not reviewed</span>',
                    unsafe_allow_html=True,
                )
                c1x, c2x = st.columns(2)
                note_edit = c1x.text_input("Update notes", value=cl.get("notes",""), key=f"note_{cl['id']}")
                if c1x.button("💾 Save Note", key=f"save_{cl['id']}"):
                    update_clause(cl["id"], notes=note_edit, approved=approved)
                    st.rerun()
                if c2x.button("🔄 Toggle Approved", key=f"appr_{cl['id']}"):
                    update_clause(cl["id"], notes=cl.get("notes",""), approved=not approved)
                    st.rerun()
                if c2x.button("🗑️ Delete", key=f"del_{cl['id']}"):
                    delete_clause(cl["id"]); st.rerun()

    with cl_add:
        na = st.text_input("Clause Name *", key="cl_an")
        ca = st.selectbox("Category *", CATEGORIES, key="cl_ac")
        ja = st.selectbox("Jurisdiction", JURISDICTIONS, key="cl_aj")
        ta = st.text_area("Clause Text *", height=160, key="cl_at")
        no = st.text_area("Notes", height=60, key="cl_ano")
        if st.button("➕ Add Clause", type="primary", key="cl_abtn"):
            if na.strip() and ta.strip():
                add_clause(name=na, category=ca, jurisdiction=ja, text=ta, notes=no)
                st.success("✅ Clause added!")
            else:
                st.warning("⚠️ Name and text are required.")

# ── 4. Compliance Policy Generator ───────────────────────────────
with tab4:
    st.markdown(
        '<div class="notice-box">ℹ️ Generated policies are first drafts. '
        "Have a qualified lawyer review before adoption.</div>",
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns(2)
    policy_type = c1.selectbox("Policy Type", [
        "Anti-bribery and corruption policy", "AML policy", "Sanctions policy",
        "Whistleblowing policy", "Gifts and hospitality policy", "Conflict of interest policy",
        "Data protection policy", "Code of conduct", "Third-party due diligence policy",
        "Procurement integrity policy",
    ], key="cp_pt")
    risk_level = c2.selectbox("Risk Level", ["Low", "Medium", "High"], key="cp_rl")
    d1, d2, d3 = st.columns(3)
    org_name = d1.text_input("Organisation Name *", key="cp_on")
    industry = d2.text_input("Industry *", placeholder="e.g. Financial services, NGO", key="cp_ind")
    jur_cp = d3.selectbox("Jurisdiction", [
        "International / Neutral", "UK", "US", "EU", "Rwanda", "Other",
    ], key="cp_jur")
    employees = st.text_input("Number of Employees", placeholder="e.g. 50, 500, 10,000+", key="cp_emp")
    additional_cp = st.text_area("Additional Instructions", height=60,
        placeholder="Specific risks, existing policies, or regulatory requirements…", key="cp_add")
    if st.button("🛡️ Generate Policy", type="primary", disabled=not api_key, key="cp_btn"):
        if not org_name.strip() or not industry.strip():
            st.warning("⚠️ Organisation name and industry are required.")
        else:
            from utils.compliance_policy import CompliancePolicyGenerator
            with st.spinner("Drafting policy with Claude Opus 4.7…"):
                try:
                    result_cp = CompliancePolicyGenerator(api_key).generate(
                        policy_type, org_name, industry, jur_cp, employees, risk_level, additional_cp
                    )
                    st.session_state.cp_result = result_cp
                    st.success("✅ Policy generated!")
                except Exception as exc:
                    st.error(f"Generation failed: {exc}")
    if st.session_state.get("cp_result"):
        result_cp = st.session_state.cp_result
        policy_doc = result_cp.get("policy_document", "")
        title = result_cp.get("policy_title", policy_type)
        st.divider()
        section(f"📄 {title}")
        st.markdown(f'<div class="revised-doc">{policy_doc.replace(chr(10),"<br>")}</div>', unsafe_allow_html=True)
        cp_tabs = st.tabs(["✅ Implementation Checklist", "🎓 Training", "📞 Reporting",
                           "⚖️ Disciplinary", "🗓️ Review Schedule"])
        with cp_tabs[0]:
            for item in result_cp.get("implementation_checklist",[]): st.markdown(f"- {item}")
        with cp_tabs[1]:
            for t in result_cp.get("training_recommendations",[]): st.markdown(f"- {t}")
        with cp_tabs[2]:
            for r in result_cp.get("reporting_channels",[]): st.markdown(f"- {r}")
        with cp_tabs[3]:
            st.markdown(result_cp.get("disciplinary_measures",""))
        with cp_tabs[4]:
            st.markdown(result_cp.get("review_schedule",""))
        st.markdown("<br>", unsafe_allow_html=True)
        action_row(text_to_download=policy_doc, base_filename="compliance_policy",
                   report_data=result_cp, reset_keys=["cp_result"], key_prefix="cp")

# ── 5. Court Document Drafting ────────────────────────────────────
with tab5:
    st.markdown(
        '<div class="notice-box">ℹ️ Drafts are first versions only — always review before filing. '
        "Ensure you comply with the court's specific format rules.</div>",
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns(3)
    cdd_doc_type = c1.selectbox("Document Type", [
        "Statement of Claim / Particulars of Claim",
        "Defence",
        "Reply to Defence",
        "Counter-claim",
        "Skeleton Argument",
        "Written Submissions",
        "Affidavit",
        "Witness Statement",
        "Motion / Application",
        "Appeal Brief",
        "Demand Letter",
        "Other",
    ], key="cdd_dt")
    cdd_court = c2.text_input("Court / Tribunal", placeholder="e.g. High Court, Commercial Court", key="cdd_court")
    cdd_jur   = c3.selectbox("Jurisdiction", ["England & Wales", "Scotland", "Rwanda",
                                               "United States", "International / Other"], key="cdd_jur")
    c4, c5 = st.columns(2)
    cdd_claimant  = c4.text_input("Claimant / Applicant", placeholder="Full legal name", key="cdd_cl")
    cdd_defendant = c5.text_input("Defendant / Respondent", placeholder="Full legal name", key="cdd_def")
    cdd_facts  = st.text_area("Key Facts *", height=120,
                               placeholder="Set out the material facts, events, dates, and what occurred…", key="cdd_facts")
    cdd_relief = st.text_area("Relief / Remedy Sought", height=60,
                               placeholder="e.g. damages of £X, injunction, declaration, costs…", key="cdd_relief")
    cdd_add    = st.text_area("Additional Instructions", height=60,
                               placeholder="Specific legal points, authorities to rely on, format preferences…", key="cdd_add")
    if st.button("🏛️ Draft Court Document", type="primary", disabled=not api_key, key="cdd_btn"):
        if not cdd_facts.strip():
            st.warning("⚠️ Key facts are required.")
        else:
            from utils.drafting_assistant import DraftingAssistant
            with st.spinner("Drafting with Claude Opus 4.7…"):
                try:
                    instructions = (
                        f"COURT DOCUMENT TYPE: {cdd_doc_type}\n"
                        f"Court: {cdd_court}\nJurisdiction: {cdd_jur}\n"
                        f"Claimant: {cdd_claimant}\nDefendant: {cdd_defendant}\n"
                        f"Relief sought: {cdd_relief}\n"
                        f"Additional: {cdd_add}\n\n"
                        "Draft in proper court document format with numbered paragraphs, "
                        "clear section headings, and formal legal language suitable for filing."
                    )
                    result5 = DraftingAssistant(api_key).draft(
                        cdd_doc_type, cdd_jur, "Formal litigation", f"{cdd_claimant} v {cdd_defendant}",
                        cdd_facts, "Formal", instructions)
                    st.session_state.cdd_result = result5
                    st.success("✅ Draft ready!")
                except Exception as exc:
                    st.error(f"Drafting failed: {exc}")
    if st.session_state.get("cdd_result"):
        result5 = st.session_state.cdd_result
        draft_doc = result5.get("draft_document", "")
        st.divider()
        section("📄 Court Document Draft")
        st.markdown(
            f'<div class="revised-doc">{draft_doc.replace(chr(10),"<br>")}</div>',
            unsafe_allow_html=True,
        )
        if result5.get("drafting_notes"):
            section("📝 Drafting Notes")
            for note in result5["drafting_notes"]: st.info(note)
        st.markdown("<br>", unsafe_allow_html=True)
        action_row(text_to_download=draft_doc, base_filename="court_document",
                   report_data=result5, reset_keys=["cdd_result"], key_prefix="cdd")

# ── 6. Template Builder ───────────────────────────────────────────
with tab6:
    from utils.shared.styles import group_header as _gh
    _gh("Template Builder")
    st.markdown("Build a reusable document template by filling in the fields below. The template is saved to your session.")

    if "templates" not in st.session_state:
        st.session_state.templates = []

    t_tab_view, t_tab_create = st.tabs(["📚 My Templates", "➕ Create Template"])

    with t_tab_create:
        with st.form("new_template", clear_on_submit=True):
            tm_name = st.text_input("Template Name *", placeholder="e.g. NDA Template — UK Law")
            tm_cat  = st.selectbox("Category", [
                "Contract", "Court Document", "Legal Letter",
                "Policy", "Memo", "Agreement", "Other",
            ])
            tm_jur  = st.selectbox("Jurisdiction", ["UK", "US", "EU", "Rwanda", "International", "Other"])
            tm_body = st.text_area("Template Text *", height=250,
                                   placeholder="Write your template. Use {{PARTY_NAME}}, {{DATE}}, {{AMOUNT}} etc. as placeholders…")
            tm_notes = st.text_area("Usage Notes", height=60)
            if st.form_submit_button("💾 Save Template"):
                if tm_name.strip() and tm_body.strip():
                    st.session_state.templates.append({
                        "name": tm_name, "category": tm_cat, "jurisdiction": tm_jur,
                        "body": tm_body, "notes": tm_notes,
                    })
                    st.success(f"✅ Template '{tm_name}' saved to session.")
                    st.rerun()
                else:
                    st.warning("⚠️ Name and template text are required.")

    with t_tab_view:
        templates = st.session_state.templates
        if not templates:
            st.markdown('<div class="empty-list">No templates yet. Create one in the tab above.</div>', unsafe_allow_html=True)
        else:
            for i, tmpl in enumerate(templates):
                with st.expander(f"**{tmpl['name']}** · {tmpl['category']} · {tmpl['jurisdiction']}"):
                    st.text_area("Template", value=tmpl["body"], height=150, key=f"tmpl_view_{i}", disabled=True)
                    if tmpl.get("notes"): st.caption(f"Notes: {tmpl['notes']}")
                    # Fill form
                    import re as _re
                    placeholders = _re.findall(r"\{\{(\w+)\}\}", tmpl["body"])
                    if placeholders:
                        st.markdown("**Fill in placeholders:**")
                        fill_vals = {}
                        for ph in set(placeholders):
                            fill_vals[ph] = st.text_input(ph.replace("_", " ").title(), key=f"fill_{i}_{ph}")
                        if st.button("📄 Generate Document from Template", key=f"gen_{i}"):
                            filled = tmpl["body"]
                            for ph, val in fill_vals.items():
                                if val.strip():
                                    filled = filled.replace(f"{{{{{ph}}}}}", val.strip())
                            st.text_area("Filled Document", value=filled, height=200, key=f"filled_{i}")
                            st.download_button("📥 Download (.txt)", filled, f"{tmpl['name']}.txt",
                                               "text/plain", key=f"dl_tmpl_{i}")
                    if st.button("🗑️ Delete Template", key=f"del_tmpl_{i}"):
                        st.session_state.templates.pop(i)
                        st.rerun()
