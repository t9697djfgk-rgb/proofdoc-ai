import streamlit as st
from utils.shared.sidebar import setup_page
from utils.shared.styles import slim_header, disclaimer, section
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

    # ── Rwanda Law Library selector ────────────────────────────────
    import utils.database as _db2
    _all_laws = []
    try:
        _all_laws = _db2.list_laws()
    except Exception:
        pass
    if _all_laws:
        with st.expander("⚖️ Include Rwanda Laws as context (optional)", expanded=False):
            st.caption("Select laws from your library to ground the draft in Rwandan legislation.")
            if "da_selected_laws" not in st.session_state:
                st.session_state.da_selected_laws = {}
            for _lw in _all_laws:
                _chk = _lw["id"] in st.session_state.da_selected_laws
                if st.checkbox(f"{_lw['title']} ({_lw.get('year','')})",
                               value=_chk, key=f"da_law_{_lw['id']}"):
                    st.session_state.da_selected_laws[_lw["id"]] = _lw["title"]
                else:
                    st.session_state.da_selected_laws.pop(_lw["id"], None)
            if st.session_state.da_selected_laws:
                st.success(f"✅ {len(st.session_state.da_selected_laws)} law(s) will be included in the draft context.")

    if st.button("📝 Generate Draft", type="primary", disabled=not api_key, key="da_btn"):
        if not key_facts.strip():
            st.warning("⚠️ Key facts are required.")
        else:
            from utils.drafting_assistant import DraftingAssistant
            with st.spinner("Drafting with Claude Opus 4.7…"):
                try:
                    # Append selected Rwanda law text to additional instructions
                    _law_ctx = ""
                    for _lid, _ltitle in st.session_state.get("da_selected_laws", {}).items():
                        _ltxt = _db2.get_law_text(_lid)
                        if _ltxt:
                            _law_ctx += f"\n\n=== APPLICABLE RWANDA LAW: {_ltitle} ===\n{_ltxt[:30_000]}\n=== END ==="
                    _additional_with_laws = (additional or "") + _law_ctx
                    result = DraftingAssistant(api_key).draft(
                        doc_type, jurisdiction, legal_style, parties, key_facts, tone, _additional_with_laws
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
    import utils.database as _dbcl
    from utils.clause_library import CATEGORIES, JURISDICTIONS

    _CLAUSE_SETUP_SQL = """
CREATE TABLE IF NOT EXISTS clause_library_db (
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    organization_id UUID,
    title           TEXT NOT NULL,
    category        TEXT DEFAULT '',
    jurisdiction    TEXT DEFAULT '',
    clause_text     TEXT DEFAULT '',
    notes           TEXT DEFAULT '',
    risk_level      TEXT DEFAULT 'medium',
    approved        BOOLEAN DEFAULT FALSE,
    created_by      UUID,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_clause_lib_org ON clause_library_db(organization_id);
"""
    _cl_db_ok = _dbcl.clauses_db_available()

    if not _cl_db_ok:
        st.info("💡 Run this SQL in Supabase to enable persistent clause storage:")
        st.code(_CLAUSE_SETUP_SQL, language="sql")

    cl_browse, cl_add, cl_ai = st.tabs(["🔍 Browse & Search", "➕ Add Clause", "🤖 AI Extract"])

    with cl_browse:
        sc1, sc2, sc3 = st.columns(3)
        search_q = sc1.text_input("Search clauses", placeholder="e.g. force majeure", key="cl_sq")
        cat_filter = sc2.selectbox("Category", ["All"] + CATEGORIES, key="cl_cf")
        jur_filter = sc3.selectbox("Jurisdiction", ["All"] + JURISDICTIONS, key="cl_jf")
        cat_arg = None if cat_filter == "All" else cat_filter
        jur_arg = None if jur_filter == "All" else jur_filter

        if _cl_db_ok:
            clauses = _dbcl.list_clauses(
                search=search_q or None, category=cat_arg, jurisdiction=jur_arg
            )
        else:
            from utils.clause_library import get_all, search as _cl_search
            clauses = _cl_search(search_q, cat_arg or "", jur_arg or "") if search_q \
                      else [c for c in get_all()
                            if (not cat_arg or c.get("category") == cat_arg)
                            and (not jur_arg or c.get("jurisdiction") == jur_arg)]

        st.caption(f"{len(clauses)} clause(s) found")
        for cl in clauses:
            with st.expander(f"**{cl.get('title','')}** · {cl.get('category','')} · {cl.get('jurisdiction','')}"):
                st.markdown(f'<div class="revised-doc">{cl.get("clause_text","")}</div>', unsafe_allow_html=True)
                if cl.get("notes"): st.caption(f"📝 {cl['notes']}")
                approved = cl.get("approved", False)
                st.markdown(
                    '<span class="badge-available">✅ Approved</span>' if approved
                    else '<span class="badge-soon">◌ Not reviewed</span>',
                    unsafe_allow_html=True,
                )
                cx1, cx2, cx3 = st.columns(3)
                note_edit = cx1.text_input("Notes", value=cl.get("notes",""), key=f"note_{cl['id']}")
                if cx1.button("💾 Save", key=f"save_{cl['id']}"):
                    if _cl_db_ok:
                        _dbcl.update_clause_db(cl["id"], notes=note_edit, approved=approved)
                    else:
                        from utils.clause_library import update_clause as _ucl
                        _ucl(cl["id"], notes=note_edit, approved=approved)
                    st.rerun()
                if cx2.button("🔄 Toggle Approved", key=f"appr_{cl['id']}"):
                    if _cl_db_ok:
                        _dbcl.update_clause_db(cl["id"], approved=not approved)
                    else:
                        from utils.clause_library import update_clause as _ucl
                        _ucl(cl["id"], notes=cl.get("notes",""), approved=not approved)
                    st.rerun()
                if cx3.button("🗑️ Delete", key=f"del_{cl['id']}"):
                    if _cl_db_ok:
                        _dbcl.delete_clause_db(cl["id"])
                    else:
                        from utils.clause_library import delete_clause as _dcl
                        _dcl(cl["id"])
                    st.rerun()

    with cl_add:
        na = st.text_input("Clause Name *", key="cl_an")
        ca = st.selectbox("Category *", CATEGORIES, key="cl_ac")
        ja = st.selectbox("Jurisdiction", JURISDICTIONS, key="cl_aj")
        ta = st.text_area("Clause Text *", height=160, key="cl_at")
        no = st.text_area("Notes", height=60, key="cl_ano")
        if st.button("➕ Add Clause", type="primary", key="cl_abtn"):
            if na.strip() and ta.strip():
                if _cl_db_ok:
                    _dbcl.save_clause(title=na, category=ca, jurisdiction=ja, clause_text=ta, notes=no)
                else:
                    from utils.clause_library import add_clause as _acl
                    _acl(title=na, category=ca, jurisdiction=ja, clause_text=ta, notes=no)
                st.success("✅ Clause added!")
                st.rerun()
            else:
                st.warning("⚠️ Name and text are required.")

    with cl_ai:
        st.markdown("Paste a contract or document — AI will extract all distinct clauses and save them to your library.")
        if not _cl_db_ok:
            st.warning("⚠️ Set up the Supabase table above first to save extracted clauses.")
        cl_doc = st.text_area("Document to extract from *", height=200,
                               placeholder="Paste any contract, agreement, or legal document…", key="cl_ai_doc")
        cl_ai_jur = st.selectbox("Jurisdiction", JURISDICTIONS, key="cl_ai_jur")
        if st.button("🤖 Extract Clauses with AI", type="primary",
                     disabled=not api_key or not _cl_db_ok, key="cl_ai_btn"):
            if not cl_doc.strip():
                st.warning("⚠️ Paste a document first.")
            else:
                import anthropic, json, re
                with st.spinner("Extracting clauses with Claude Opus 4.7…"):
                    try:
                        _cl_client = anthropic.Anthropic(api_key=api_key)
                        _cl_resp = _cl_client.messages.create(
                            model="claude-opus-4-7",
                            max_tokens=4096,
                            messages=[{"role": "user", "content":
                                f"Extract all distinct legal clauses from the document below. "
                                f"For each clause return a JSON object with: title, category (one of: "
                                f"{', '.join(CATEGORIES)}), clause_text (verbatim), notes (1-sentence purpose). "
                                f"Return a JSON array only.\n\nDocument:\n{cl_doc[:20_000]}"}],
                        )
                        raw = next((b.text for b in _cl_resp.content if b.type == "text"), "[]")
                        raw = re.sub(r"^```(?:json)?\s*", "", raw.strip())
                        raw = re.sub(r"\s*```$", "", raw.strip())
                        extracted = json.loads(raw)
                        saved = 0
                        for ec in extracted:
                            if ec.get("title") and ec.get("clause_text"):
                                _dbcl.save_clause(
                                    title=ec["title"],
                                    category=ec.get("category", "Other"),
                                    jurisdiction=cl_ai_jur,
                                    clause_text=ec["clause_text"],
                                    notes=ec.get("notes", ""),
                                )
                                saved += 1
                        st.success(f"✅ {saved} clause(s) extracted and saved to your library!")
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Extraction failed: {exc}")

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
    import utils.database as _dbtpl
    _gh("Template Builder")

    _TPL_SETUP_SQL = """
CREATE TABLE IF NOT EXISTS document_templates (
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    organization_id UUID,
    name            TEXT NOT NULL,
    category        TEXT DEFAULT '',
    jurisdiction    TEXT DEFAULT '',
    body            TEXT DEFAULT '',
    notes           TEXT DEFAULT '',
    created_by      UUID,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_doc_tpl_org ON document_templates(organization_id);
"""
    _tpl_db_ok = _dbtpl.templates_available()
    if not _tpl_db_ok:
        st.info("💡 Run this SQL in Supabase to persist templates across sessions:")
        st.code(_TPL_SETUP_SQL, language="sql")
    else:
        st.markdown("Templates are saved permanently to your firm's library.")

    _GALLERY = [
        {
            "name": "Non-Disclosure Agreement (NDA)",
            "category": "Agreement", "jurisdiction": "UK",
            "body": """NON-DISCLOSURE AGREEMENT

THIS AGREEMENT is made on {{DATE}} between:

1. {{DISCLOSING_PARTY}} ("Disclosing Party"), and
2. {{RECEIVING_PARTY}} ("Receiving Party").

BACKGROUND
The Disclosing Party wishes to disclose certain Confidential Information to the Receiving Party for the purpose of {{PURPOSE}}.

1. DEFINITION OF CONFIDENTIAL INFORMATION
"Confidential Information" means any information disclosed by the Disclosing Party, whether orally, in writing, or otherwise, that is designated as confidential.

2. OBLIGATIONS
The Receiving Party shall:
(a) Keep the Confidential Information strictly confidential;
(b) Not disclose the Confidential Information to any third party without prior written consent;
(c) Use the Confidential Information solely for the Purpose.

3. TERM
This Agreement shall remain in force for {{DURATION}} from the date of this Agreement.

4. GOVERNING LAW
This Agreement shall be governed by the laws of {{JURISDICTION}}.

Signed by {{DISCLOSING_PARTY}}: _________________________ Date: __________
Signed by {{RECEIVING_PARTY}}: _________________________ Date: __________""",
            "notes": "Fill in: DATE, DISCLOSING_PARTY, RECEIVING_PARTY, PURPOSE, DURATION, JURISDICTION",
        },
        {
            "name": "Client Engagement Letter",
            "category": "Legal Letter", "jurisdiction": "International",
            "body": """ENGAGEMENT LETTER

{{DATE}}

{{CLIENT_NAME}}
{{CLIENT_ADDRESS}}

Dear {{CLIENT_NAME}},

Re: {{MATTER_DESCRIPTION}}

We are pleased to confirm our engagement to act on your behalf in connection with the above matter.

SCOPE OF SERVICES
We will provide the following legal services: {{SCOPE_OF_SERVICES}}

FEE ARRANGEMENT
Our fees for this matter will be: {{FEE_ARRANGEMENT}}

BILLING
Invoices will be rendered {{BILLING_FREQUENCY}} and are payable within 30 days of receipt.

CONFIDENTIALITY
We confirm that all information you provide will be kept strictly confidential.

ACCEPTANCE
Please sign and return one copy of this letter to confirm your instructions.

Yours sincerely,

{{LAWYER_NAME}}
{{FIRM_NAME}}""",
            "notes": "Fill in: DATE, CLIENT_NAME, CLIENT_ADDRESS, MATTER_DESCRIPTION, SCOPE_OF_SERVICES, FEE_ARRANGEMENT, BILLING_FREQUENCY, LAWYER_NAME, FIRM_NAME",
        },
        {
            "name": "Demand Letter",
            "category": "Legal Letter", "jurisdiction": "International",
            "body": """WITHOUT PREJUDICE

{{DATE}}

{{RECIPIENT_NAME}}
{{RECIPIENT_ADDRESS}}

Dear {{RECIPIENT_NAME}},

Re: {{MATTER_REFERENCE}} — FORMAL DEMAND

We act on behalf of {{CLIENT_NAME}} ("our client") in connection with the above matter.

BACKGROUND
{{BACKGROUND_FACTS}}

DEMAND
We hereby formally demand that you:
1. {{DEMAND_1}}
2. {{DEMAND_2}}

DEADLINE
Unless we receive your written response and compliance by {{RESPONSE_DEADLINE}}, our client reserves all rights to commence legal proceedings without further notice.

Take this letter seriously. The costs of litigation, including our client's legal costs, may be awarded against you.

Yours faithfully,

{{LAWYER_NAME}}
{{FIRM_NAME}}
Solicitors for {{CLIENT_NAME}}""",
            "notes": "Fill in: DATE, RECIPIENT_NAME, RECIPIENT_ADDRESS, MATTER_REFERENCE, CLIENT_NAME, BACKGROUND_FACTS, DEMAND_1, DEMAND_2, RESPONSE_DEADLINE, LAWYER_NAME, FIRM_NAME",
        },
        {
            "name": "Settlement Agreement",
            "category": "Agreement", "jurisdiction": "International",
            "body": """SETTLEMENT AGREEMENT

THIS SETTLEMENT AGREEMENT is made on {{DATE}} between:

1. {{CLAIMANT_NAME}} ("Claimant"), and
2. {{RESPONDENT_NAME}} ("Respondent").

RECITALS
A. The Claimant has made claims against the Respondent arising from {{DISPUTE_DESCRIPTION}}.
B. The parties wish to resolve this dispute on the terms set out below.

TERMS OF SETTLEMENT
1. SETTLEMENT SUM: The Respondent shall pay the Claimant the sum of {{SETTLEMENT_AMOUNT}} ("Settlement Sum").
2. PAYMENT: Payment shall be made by {{PAYMENT_DEADLINE}} to {{PAYMENT_DETAILS}}.
3. FULL AND FINAL SETTLEMENT: Upon receipt of the Settlement Sum, the Claimant agrees that this constitutes full and final settlement of all claims.
4. CONFIDENTIALITY: The parties agree to keep the terms of this Agreement strictly confidential.
5. GOVERNING LAW: This Agreement is governed by the laws of {{JURISDICTION}}.

Signed: {{CLAIMANT_NAME}} _________________________ Date: __________
Signed: {{RESPONDENT_NAME}} _______________________ Date: __________""",
            "notes": "Fill in: DATE, CLAIMANT_NAME, RESPONDENT_NAME, DISPUTE_DESCRIPTION, SETTLEMENT_AMOUNT, PAYMENT_DEADLINE, PAYMENT_DETAILS, JURISDICTION",
        },
        {
            "name": "Witness Statement",
            "category": "Court Document", "jurisdiction": "UK",
            "body": """WITNESS STATEMENT

Case No: {{CASE_NUMBER}}
Statement of: {{WITNESS_NAME}}
Date: {{DATE}}

I, {{WITNESS_NAME}}, of {{WITNESS_ADDRESS}}, make this statement on the basis of my personal knowledge and belief:

1. I am the {{WITNESS_ROLE}} in this matter.

2. {{STATEMENT_PARAGRAPH_1}}

3. {{STATEMENT_PARAGRAPH_2}}

4. {{STATEMENT_PARAGRAPH_3}}

STATEMENT OF TRUTH
I believe that the facts stated in this witness statement are true.

Signed: _________________________ Date: __________
Full Name: {{WITNESS_NAME}}""",
            "notes": "Fill in: CASE_NUMBER, WITNESS_NAME, DATE, WITNESS_ADDRESS, WITNESS_ROLE, STATEMENT_PARAGRAPH_1, STATEMENT_PARAGRAPH_2, STATEMENT_PARAGRAPH_3",
        },
    ]

    t_tab_gallery, t_tab_view, t_tab_create = st.tabs(["⚡ Template Gallery", "📚 My Templates", "➕ Create Template"])

    with t_tab_gallery:
        st.markdown("Pre-built templates — click **Use Template** to load it into your session and fill in the placeholders.")
        for _tpl in _GALLERY:
            with st.expander(f"**{_tpl['name']}** · {_tpl['category']} · {_tpl['jurisdiction']}"):
                st.text_area("Preview", value=_tpl["body"][:400] + ("…" if len(_tpl["body"]) > 400 else ""),
                              height=120, disabled=True, key=f"gal_prev_{_tpl['name']}")
                if _tpl.get("notes"):
                    st.caption(f"Placeholders: {_tpl['notes']}")
                if st.button("📥 Use Template", key=f"gal_use_{_tpl['name']}", type="primary"):
                    if not any(t["name"] == _tpl["name"] for t in st.session_state.templates):
                        st.session_state.templates.append(_tpl.copy())
                        st.success(f"✅ '{_tpl['name']}' added to My Templates.")
                        st.rerun()
                    else:
                        st.info("Already in My Templates.")

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
                    if _tpl_db_ok:
                        _dbtpl.save_template(tm_name, tm_cat, tm_jur, tm_body, tm_notes)
                    else:
                        if "templates" not in st.session_state:
                            st.session_state.templates = []
                        st.session_state.templates.append({
                            "id": f"s_{len(st.session_state.templates)}",
                            "name": tm_name, "category": tm_cat, "jurisdiction": tm_jur,
                            "body": tm_body, "notes": tm_notes,
                        })
                    st.success(f"✅ Template '{tm_name}' saved.")
                    st.rerun()
                else:
                    st.warning("⚠️ Name and template text are required.")

    with t_tab_view:
        if _tpl_db_ok:
            _tpl_search = st.text_input("Search templates", placeholder="Filter by name…", key="tpl_search")
            templates = _dbtpl.list_templates(search=_tpl_search or None)
        else:
            templates = st.session_state.get("templates", [])

        if not templates:
            st.markdown('<div class="empty-list">No templates yet. Create one or use a gallery template above.</div>',
                        unsafe_allow_html=True)
        else:
            import re as _re
            st.caption(f"{len(templates)} template(s)")
            for i, tmpl in enumerate(templates):
                with st.expander(f"**{tmpl['name']}** · {tmpl.get('category','')} · {tmpl.get('jurisdiction','')}"):
                    body = tmpl.get("body") or (_dbtpl.get_template_body(tmpl["id"]) if _tpl_db_ok else "")
                    st.text_area("Template", value=body, height=150, key=f"tmpl_view_{i}", disabled=True)
                    if tmpl.get("notes"): st.caption(f"Notes: {tmpl['notes']}")
                    placeholders = _re.findall(r"\{\{(\w+)\}\}", body)
                    if placeholders:
                        st.markdown("**Fill in placeholders:**")
                        fill_vals = {}
                        for ph in sorted(set(placeholders)):
                            fill_vals[ph] = st.text_input(ph.replace("_", " ").title(),
                                                           key=f"fill_{i}_{ph}")
                        if st.button("📄 Generate Document", key=f"gen_{i}", type="primary"):
                            filled = body
                            for ph, val in fill_vals.items():
                                if val.strip():
                                    filled = filled.replace(f"{{{{{ph}}}}}", val.strip())
                            st.text_area("Filled Document", value=filled, height=200, key=f"filled_{i}")
                            st.download_button("📥 Download (.txt)", filled,
                                               f"{tmpl['name']}.txt", "text/plain",
                                               key=f"dl_tmpl_{i}")
                    if st.button("🗑️ Delete Template", key=f"del_tmpl_{i}"):
                        if _tpl_db_ok:
                            _dbtpl.delete_template(tmpl["id"])
                        else:
                            st.session_state.templates.pop(i)
                        st.rerun()
