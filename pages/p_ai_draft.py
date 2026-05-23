import streamlit as st
from utils.shared.sidebar import setup_page
from utils.shared.styles import slim_header, disclaimer, section, placeholder_feature
from utils.shared.export_utils import action_row, download_json

api_key = setup_page()
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

# ── 5. Court Document Drafting (placeholder) ─────────────────────
with tab5:
    placeholder_feature(
        "🏛️", "Court Document Drafting",
        "Generate court-ready pleadings, motions, submissions, and applications from your facts.",
        ["Select document type (claim, defence, motion, etc.)", "Enter parties and facts",
         "AI drafts in correct court format", "Review and customise before filing"],
        ["Court document draft in correct jurisdiction format",
         "Checklist of required attachments", "Filing instructions"],
    )

# ── 6. Template Builder (placeholder) ────────────────────────────
with tab6:
    placeholder_feature(
        "🔧", "Template Builder",
        "Create reusable document templates with smart fields, auto-fill variables, and approval workflows.",
        ["Build templates from scratch or from existing documents",
         "Add smart fields (party names, dates, amounts)", "Set required and optional fields",
         "Share templates with team and set access permissions"],
        ["Saved template with smart fields", "Filled document from template",
         "Template library for the firm"],
    )
