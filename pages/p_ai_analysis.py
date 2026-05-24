import streamlit as st
from utils.shared.sidebar import setup_page, get_law_context_block
from utils.shared.styles import slim_header, disclaimer, section, risk_badge
from utils.shared.document_input import document_input_ui, two_document_input_ui
from utils.shared.export_utils import download_json, download_docx_from_dict

from utils.auth import require_lawyer
api_key = setup_page("Analysis")
require_lawyer()


def _with_laws(text: str) -> str:
    ctx = get_law_context_block()
    if ctx:
        return (
            "[APPLICABLE RWANDA LAWS — use as legal context for your analysis]\n"
            + ctx
            + "\n[END LAWS — document to analyse follows]\n\n"
            + text
        )
    return text
slim_header("📊", "Analysis", "Contract summaries, due diligence, risk reports, and document comparison")
disclaimer()

tab1, tab2, tab3, tab4 = st.tabs([
    "🏢 Due Diligence Review",
    "🔍 Document Comparison",
    "📋 Contract Summary",
    "🚨 Risk Report Generator",
])

# ── 1. Due Diligence Review ───────────────────────────────────────
with tab1:
    from utils.shared.styles import confidentiality_notice
    confidentiality_notice()
    text1 = document_input_ui("dda", paste_placeholder="Paste due diligence document, SPA, or disclosure letter here…")
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    matter_type = c1.selectbox("Matter Type", [
        "M&A / Acquisition", "Joint venture", "Investment / Fundraising",
        "Real estate transaction", "Banking / Finance", "Commercial agreement", "Other",
    ], key="dda_mt")
    client_perspective = c2.selectbox("Client Perspective", [
        "Buyer / Investor", "Seller / Target", "Lender", "Borrower", "Neutral review",
    ], key="dda_cp")
    key_concerns = c3.text_input("Key Concerns", placeholder="e.g. IP, litigation, regulatory", key="dda_kc")
    if st.button("🏢 Run Due Diligence Review", type="primary", disabled=not api_key, key="dda_btn"):
        if not text1:
            st.warning("⚠️ Upload or paste a document first.")
        else:
            from utils.due_diligence import DueDiligenceReview
            with st.spinner("Reviewing with Claude Opus 4.7…"):
                try:
                    result1 = DueDiligenceReview(api_key).review(_with_laws(text1), matter_type, client_perspective, key_concerns)
                    st.session_state.dda_result = result1
                    st.success("✅ Review complete!")
                except Exception as exc:
                    st.error(f"Review failed: {exc}")
    if st.session_state.get("dda_result"):
        result1 = st.session_state.dda_result
        red_flags = result1.get("red_flags", [])
        mat = result1.get("matters_for_attention", [])
        st.divider()
        m1, m2, m3 = st.columns(3)
        m1.markdown(f'<div class="metric-card"><div class="val" style="color:#dc2626">{len(red_flags)}</div><div class="lbl">Red Flags</div></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="metric-card"><div class="val" style="color:#d97706">{len(mat)}</div><div class="lbl">Matters for Attention</div></div>', unsafe_allow_html=True)
        m3.markdown(f'<div class="metric-card"><div class="val">{result1.get("overall_risk","—")}</div><div class="lbl">Overall Risk</div></div>', unsafe_allow_html=True)
        st.markdown(f"**Executive Summary:** {result1.get('executive_summary','')}")
        if red_flags:
            st.markdown("<br>", unsafe_allow_html=True)
            section(f"🚨 Red Flags ({len(red_flags)})")
            SEV_CFG = {
                "critical": ("#dc2626", "#fef2f2", "🔴"),
                "high":     ("#ea580c", "#fff7ed", "🟠"),
                "medium":   ("#d97706", "#fffbeb", "🟡"),
                "low":      ("#059669", "#ecfdf5", "🟢"),
            }
            for rf in red_flags:
                sev = (rf.get("severity") or "medium").lower()
                fg, bg, icon = SEV_CFG.get(sev, ("#6b7280", "#f1f5f9", "⚪"))
                st.markdown(
                    f"""<div style="background:{bg};border-radius:10px;padding:.85rem 1rem;
                                  margin-bottom:.4rem;border-left:4px solid {fg}">
                      <div style="display:flex;align-items:center;gap:.6rem;margin-bottom:.4rem">
                        <span>{icon}</span>
                        <span style="font-size:.7rem;font-weight:700;color:{fg};text-transform:uppercase;
                                     letter-spacing:.04em">{rf.get('category','')}</span>
                        <span style="margin-left:auto">{risk_badge(sev)}</span>
                      </div>
                      <p style="margin:0;font-weight:600;color:#1a1a2e;font-size:.88rem">{rf.get('issue','')}</p>
                      {f'<p style="margin:.3rem 0 0;font-size:.82rem;color:#374151"><b>Implication:</b> {rf.get("implication","")}</p>' if rf.get("implication") else ""}
                      {f'<p style="margin:.2rem 0 0;font-size:.82rem;color:#1a2744"><b>Recommendation:</b> {rf.get("recommendation","")}</p>' if rf.get("recommendation") else ""}
                    </div>""",
                    unsafe_allow_html=True,
                )
        for m in mat: st.warning(m)
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: download_json("📥 Download DD Report (.json)", result1, "due_diligence.json", key="dda_dl")
        with c2: download_docx_from_dict("📝 Download (.docx)", result1, "due_diligence_review.docx",
                                          title="Due Diligence Review", key="dda_dl_docx")
        with c3:
            if st.button("🔄 Reset", key="dda_rst", use_container_width=True):
                st.session_state.pop("dda_result", None); st.rerun()

# ── 2. Document Comparison ────────────────────────────────────────
with tab2:
    orig_text, rev_text = two_document_input_ui("dca")
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    doc_type2 = c1.selectbox("Document Type", [
        "Contract", "NDA", "Shareholder agreement", "Employment agreement",
        "Settlement", "Court pleading", "Policy", "Other",
    ], key="dca_dt")
    client_pos2 = c2.selectbox("Client Position", [
        "Neutral review", "Buyer / Investor", "Seller / Target", "Claimant", "Defendant",
    ], key="dca_cp")
    if st.button("🔍 Compare Documents", type="primary", disabled=not api_key, key="dca_btn"):
        if not orig_text or not rev_text:
            st.warning("⚠️ Both documents are required.")
        else:
            from utils.document_comparison import DocumentComparison
            with st.spinner("Comparing with Claude Opus 4.7…"):
                try:
                    result2 = DocumentComparison(api_key).compare(orig_text, rev_text, doc_type2, client_pos2)
                    st.session_state.dca_result = result2
                    st.success("✅ Comparison complete!")
                except Exception as exc:
                    st.error(f"Comparison failed: {exc}")
    if st.session_state.get("dca_result"):
        result2 = st.session_state.dca_result
        changes = result2.get("changes", [])
        st.divider()
        m1, m2, m3 = st.columns(3)
        m1.markdown(f'<div class="metric-card"><div class="val">{len(changes)}</div><div class="lbl">Changes</div></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="metric-card"><div class="val" style="color:#dc2626">{len(result2.get("significant_changes",[]))}</div><div class="lbl">High-Impact</div></div>', unsafe_allow_html=True)
        m3.markdown(f'<div class="metric-card"><div class="val">{result2.get("net_effect","—")}</div><div class="lbl">Net Effect</div></div>', unsafe_allow_html=True)
        st.markdown(f"**Summary:** {result2.get('summary','')}")
        if changes:
            st.markdown("<br>", unsafe_allow_html=True)
            section(f"📋 Changes ({len(changes)})")
            for ch in changes:
                row = st.columns([1, 3, 3, 2, 1])
                row[0].markdown(f"`{ch.get('change_type','')}`")
                row[1].markdown(f'<span style="color:#dc2626">{ch.get("original_text","")}</span>', unsafe_allow_html=True)
                row[2].markdown(f'<span style="color:#16a34a">{ch.get("revised_text","")}</span>', unsafe_allow_html=True)
                row[3].markdown(ch.get("legal_significance",""))
                row[4].markdown(risk_badge(ch.get("impact_level","low")), unsafe_allow_html=True)
                st.markdown('<hr style="margin:0.25rem 0;border-color:#f1f5f9">', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: download_json("📥 Download Report (.json)", result2, "comparison.json", key="dca_dl")
        with c2: download_docx_from_dict("📝 Download (.docx)", result2, "document_comparison.docx",
                                          title="Document Comparison Report", key="dca_dl_docx")
        with c3:
            if st.button("🔄 Reset", key="dca_rst", use_container_width=True):
                st.session_state.pop("dca_result", None); st.rerun()

# ── 3. Contract Summary ───────────────────────────────────────────
with tab3:
    st.markdown("Generate a structured plain-English summary of any contract — parties, key terms, obligations, and risk flags.")
    text3 = document_input_ui("cs", paste_placeholder="Paste the contract text here…")
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    cs_type = c1.selectbox("Contract Type", [
        "Service agreement", "NDA", "Employment contract", "SPA",
        "Shareholder agreement", "Loan agreement", "Lease", "Other",
    ], key="cs_ct")
    cs_persp = c2.selectbox("Client Perspective", [
        "Neutral", "Buyer / Investor", "Seller / Target",
        "Service Provider", "Client / Customer", "Employer", "Employee",
    ], key="cs_persp")
    if st.button("📋 Summarise Contract", type="primary", disabled=not api_key, key="cs_btn"):
        if not text3:
            st.warning("⚠️ Upload or paste a contract first.")
        else:
            from utils.contract_summary import ContractSummarizer
            with st.spinner("Summarising with Claude Opus 4.7…"):
                try:
                    result3 = ContractSummarizer(api_key).summarize(_with_laws(text3), cs_type, cs_persp)
                    st.session_state.cs_result = result3
                    st.success("✅ Summary complete!")
                except Exception as exc:
                    st.error(f"Summarisation failed: {exc}")
    if st.session_state.get("cs_result"):
        result3 = st.session_state.cs_result
        st.divider()
        st.markdown(f"**Executive Summary:** {result3.get('executive_summary','')}")
        st.markdown(f"**Client Advice:** {result3.get('client_advice','')}")
        cs_tabs = st.tabs(["📋 Key Terms", "👥 Parties", "⚖️ Obligations", "🔑 Rights", "⚠️ Risk Flags", "❌ Missing Clauses"])
        with cs_tabs[0]:
            kt = result3.get("key_terms", {})
            for k, v in kt.items():
                if v:
                    st.markdown(f"**{k.replace('_',' ').title()}:** {v}")
        with cs_tabs[1]:
            for p in result3.get("parties", []):
                st.markdown(f"- **{p.get('name','')}** — {p.get('role','')}")
        with cs_tabs[2]:
            for ob in result3.get("key_obligations", []):
                st.markdown(f"- **{ob.get('party','')}**: {ob.get('obligation','')} _{ob.get('deadline','')}_")
        with cs_tabs[3]:
            for r in result3.get("key_rights", []): st.markdown(f"- {r}")
        with cs_tabs[4]:
            for rf in result3.get("risk_flags", []):
                fn = st.error if rf.get("severity") == "high" else st.warning
                fn(f"**{rf.get('issue','')}** — {rf.get('recommendation','')}")
        with cs_tabs[5]:
            for m in result3.get("missing_standard_clauses", []): st.warning(m)
            if not result3.get("missing_standard_clauses"):
                st.success("No missing standard clauses identified.")
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: download_json("📥 Download Summary (.json)", result3, "contract_summary.json", key="cs_dl")
        with c2: download_docx_from_dict("📝 Download (.docx)", result3, "contract_summary.docx",
                                          title="Contract Summary", key="cs_dl_docx")
        with c3:
            if st.button("🔄 Reset", key="cs_rst", use_container_width=True):
                st.session_state.pop("cs_result", None); st.rerun()

# ── 4. Risk Report Generator ──────────────────────────────────────
with tab4:
    st.markdown("Generate a board-ready risk register and report from any legal document or contract.")
    text4 = document_input_ui("rr", paste_placeholder="Paste one or more documents (separated by ---) here…")
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    rr_type = c1.selectbox("Document Type", [
        "Contract / Agreement", "Corporate documents", "Litigation bundle",
        "Due diligence report", "Regulatory filing", "Other",
    ], key="rr_dt")
    rr_audience = c2.selectbox("Reporting Audience", [
        "Board / Senior management", "Client briefing", "Legal team internal",
        "Investor / Lender", "Regulatory body",
    ], key="rr_aud")
    rr_jur = c3.text_input("Jurisdiction", placeholder="e.g. UK, Rwanda", key="rr_jur")
    if st.button("🚨 Generate Risk Report", type="primary", disabled=not api_key, key="rr_btn"):
        if not text4:
            st.warning("⚠️ Upload or paste a document first.")
        else:
            from utils.contract_summary import RiskReportGenerator
            with st.spinner("Generating with Claude Opus 4.7…"):
                try:
                    result4 = RiskReportGenerator(api_key).generate(_with_laws(text4), rr_type, rr_audience, rr_jur)
                    st.session_state.rr_result = result4
                    st.success("✅ Risk report ready!")
                except Exception as exc:
                    st.error(f"Generation failed: {exc}")
    if st.session_state.get("rr_result"):
        result4 = st.session_state.rr_result
        register = result4.get("risk_register", [])
        st.divider()
        ov_col = {"Critical": "#dc2626", "High": "#d97706", "Medium": "#2563eb", "Low": "#16a34a"}.get(result4.get("overall_risk_rating",""), "#64748b")
        m1, m2, m3 = st.columns(3)
        m1.markdown(f'<div class="metric-card"><div class="val" style="color:{ov_col}">{result4.get("overall_risk_rating","—")}</div><div class="lbl">Overall Risk</div></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="metric-card"><div class="val">{len(register)}</div><div class="lbl">Risks Identified</div></div>', unsafe_allow_html=True)
        immediate = len([r for r in register if r.get("priority") == "Immediate"])
        m3.markdown(f'<div class="metric-card"><div class="val" style="color:#dc2626">{immediate}</div><div class="lbl">Immediate Actions</div></div>', unsafe_allow_html=True)
        st.markdown(f"**Executive Summary:** {result4.get('executive_summary','')}")
        if result4.get("immediate_actions"):
            st.markdown("<br>", unsafe_allow_html=True)
            section("🚨 Immediate Actions Required")
            for a in result4["immediate_actions"]: st.error(f"→ {a}")
        if register:
            st.markdown("<br>", unsafe_allow_html=True)
            section(f"📋 Risk Register ({len(register)} risks)")
            hdr = st.columns([0.8, 1.5, 2.5, 1, 1, 2.5, 1.5])
            for col, lbl in zip(hdr, ["ID", "Category", "Risk", "Likelihood", "Impact", "Action", "Priority"]):
                col.markdown(f"**{lbl}**")
            st.divider()
            for r in register:
                row = st.columns([0.8, 1.5, 2.5, 1, 1, 2.5, 1.5])
                row[0].text(r.get("risk_id",""))
                row[1].text(r.get("category",""))
                row[2].markdown(r.get("description",""))
                row[3].markdown(risk_badge(r.get("likelihood","medium").lower()), unsafe_allow_html=True)
                row[4].markdown(risk_badge(r.get("impact","medium").lower()), unsafe_allow_html=True)
                row[5].markdown(r.get("recommended_action",""))
                row[6].text(r.get("priority",""))
                st.markdown('<hr style="margin:0.25rem 0;border-color:#f1f5f9">', unsafe_allow_html=True)
        if result4.get("compliance_gaps"):
            st.markdown("<br>", unsafe_allow_html=True)
            section("⚠️ Compliance Gaps")
            for g in result4["compliance_gaps"]: st.warning(g)
        st.markdown(f"\n**Conclusion:** {result4.get('conclusion','')}")
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1: download_json("📥 Download Risk Report (.json)", result4, "risk_report.json", key="rr_dl")
        with c2: download_docx_from_dict("📝 Download (.docx)", result4, "risk_report.docx",
                                          title="Risk Report", key="rr_dl_docx")
        with c3:
            if st.button("🔄 Reset", key="rr_rst", use_container_width=True):
                st.session_state.pop("rr_result", None); st.rerun()
