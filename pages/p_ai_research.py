import streamlit as st
from utils.shared.sidebar import setup_page, get_law_context_block
from utils.shared.styles import slim_header, group_header, section
from utils.shared.export_utils import download_json, download_docx_from_dict, download_docx
from utils.auth import require_lawyer

api_key = setup_page("Research")
user = require_lawyer()
slim_header("🔬", "Research", "Legal research, case summaries, statute explainers, and translation tools")

tab_research, tab_translation = st.tabs(["🔬 Research Tools", "🌍 Translation & Terminology"])

# ── Research Tools ────────────────────────────────────────────────
with tab_research:
    r_tab1, r_tab2, r_tab3, r_tab4 = st.tabs([
        "🔬 Legal Research", "📑 Case Summary", "📖 Statute Explainer", "🔤 Term Checker",
    ])

    # Legal Research Assistant
    with r_tab1:
        st.markdown("Ask any legal question and receive a structured answer with authorities and principles.")
        question = st.text_area("Legal Question *", height=100,
            placeholder="e.g. Under English law, when does a duty of care arise in negligence?")
        c1, c2 = st.columns(2)
        lr_jur  = c1.text_input("Jurisdiction", placeholder="e.g. UK, Rwandan law, International", key="lr_jur")
        lr_area = c2.text_input("Area of Law", placeholder="e.g. Contract law, Tort, Criminal", key="lr_area")
        if st.button("🔬 Research", type="primary", disabled=not api_key, key="lr_btn"):
            if not question.strip():
                st.warning("⚠️ Enter a legal question first.")
            else:
                from utils.research_tools import LegalResearchAssistant
                with st.spinner("Researching with Claude Opus 4.7…"):
                    try:
                        result = LegalResearchAssistant(api_key).research(
                            question.strip(), lr_jur, lr_area,
                            extra_context=get_law_context_block(),
                        )
                        st.session_state.lr_result = result
                        st.success("✅ Research complete!")
                    except Exception as exc:
                        st.error(f"Research failed: {exc}")
        if st.session_state.get("lr_result"):
            r = st.session_state.lr_result
            st.divider()
            st.markdown(f"### Answer\n{r.get('answer','')}")
            if r.get("key_principles"):
                st.markdown("<br>", unsafe_allow_html=True)
                section("⚖️ Key Principles")
                for p in r["key_principles"]: st.markdown(f"- {p}")
            if r.get("relevant_authorities"):
                st.markdown("<br>", unsafe_allow_html=True)
                section("📚 Relevant Authorities")
                for a in r["relevant_authorities"]:
                    st.markdown(
                        f'<div style="background:#f0f4ff;border-radius:8px;padding:.6rem 1rem;'
                        f'margin-bottom:.35rem;border-left:3px solid #1a2744">'
                        f'<span style="font-weight:700;color:#1a2744;font-size:.88rem">{a.get("name","")}</span>'
                        f'&nbsp;<code style="font-size:.78rem;background:#e2e8f0;padding:.1rem .4rem;border-radius:4px">{a.get("citation","")}</code>'
                        f'<div style="font-size:.82rem;color:#475569;margin-top:.25rem">{a.get("relevance","")}</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
            if r.get("practical_implications"):
                st.markdown("<br>", unsafe_allow_html=True)
                section("💡 Practical Implications")
                for p in r["practical_implications"]: st.markdown(f"- {p}")
            if r.get("areas_of_uncertainty"):
                st.markdown("<br>", unsafe_allow_html=True)
                section("⚠️ Areas of Uncertainty")
                for u in r["areas_of_uncertainty"]: st.warning(u)
            st.info(f"ℹ️ {r.get('disclaimer','AI-generated — verify with primary sources')}")
            c1, c2, c3 = st.columns(3)
            with c1: download_json("📥 Export Research (.json)", r, "legal_research.json", key="lr_dl")
            with c2: download_docx_from_dict("📝 Download (.docx)", r, "legal_research.docx",
                                              title="Legal Research Memo", key="lr_dl_docx")
            with c3:
                if st.button("🔄 Reset", key="lr_rst", use_container_width=True):
                    st.session_state.pop("lr_result", None); st.rerun()

    # Case Summary Generator
    with r_tab2:
        st.markdown("Upload or paste a judgment and receive a structured case summary with ratio and key principles.")
        from utils.shared.document_input import document_input_ui
        cs_text = document_input_ui("csum", paste_placeholder="Paste the case judgment or report here…")
        cs_jur  = st.text_input("Jurisdiction", placeholder="e.g. UK, Rwanda", key="csum_jur")
        if st.button("📑 Summarise Case", type="primary", disabled=not api_key, key="csum_btn"):
            if not cs_text:
                st.warning("⚠️ Upload or paste a case first.")
            else:
                from utils.research_tools import CaseSummarizer
                with st.spinner("Summarising with Claude Opus 4.7…"):
                    try:
                        result = CaseSummarizer(api_key).summarize(cs_text, cs_jur)
                        st.session_state.csum_result = result
                        st.success("✅ Summary complete!")
                    except Exception as exc:
                        st.error(f"Summarisation failed: {exc}")
        if st.session_state.get("csum_result"):
            r = st.session_state.csum_result
            st.divider()
            st.markdown(
                f'<div style="background:#f0f4ff;border-radius:12px;padding:1rem 1.2rem;margin-bottom:.8rem">'
                f'<div style="font-size:1rem;font-weight:700;color:#1a2744">{r.get("case_name","—")}</div>'
                f'<div style="display:flex;gap:1rem;flex-wrap:wrap;margin-top:.4rem">'
                f'<code style="font-size:.8rem;background:#e2e8f0;padding:.15rem .5rem;border-radius:4px">{r.get("citation","—")}</code>'
                f'<span style="font-size:.8rem;color:#64748b">{r.get("court","—")} · {r.get("date","")}</span>'
                f'</div></div>',
                unsafe_allow_html=True,
            )
            st.markdown(f"**Facts:** {r.get('facts','')}")
            if r.get("issues"):
                st.markdown("**Issues Decided:**")
                for i in r["issues"]: st.markdown(f"- {i}")
            st.markdown(f"**Held:** {r.get('held','')}")
            st.markdown(f"**Ratio Decidendi:** _{r.get('ratio_decidendi','')}_")
            if r.get("obiter_dicta"):
                st.markdown("**Obiter:**")
                for o in r["obiter_dicta"]: st.markdown(f"- {o}")
            if r.get("key_principles"):
                section("⚖️ Key Principles")
                for p in r["key_principles"]: st.markdown(f"- {p}")
            st.markdown(f"**Significance:** {r.get('significance','')}")
            c1, c2, c3 = st.columns(3)
            with c1: download_json("📥 Export Summary (.json)", r, "case_summary.json", key="csum_dl")
            with c2: download_docx_from_dict("📝 Download (.docx)", r, "case_summary.docx",
                                              title="Case Summary", key="csum_dl_docx")
            with c3:
                if st.button("🔄 Reset", key="csum_rst", use_container_width=True):
                    st.session_state.pop("csum_result", None); st.rerun()

    # Statute Explainer
    with r_tab3:
        st.markdown("Paste any statute or regulation and receive a plain-English explanation section by section.")
        from utils.shared.document_input import document_input_ui
        se_text = document_input_ui("se", paste_placeholder="Paste the statute, regulation, or section here…")
        c1, c2 = st.columns(2)
        se_jur  = c1.text_input("Jurisdiction", placeholder="e.g. UK, Rwanda", key="se_jur")
        se_aud  = c2.selectbox("Audience", ["Legal professional", "Business client",
                                             "General public", "Compliance officer"], key="se_aud")
        if st.button("📖 Explain Statute", type="primary", disabled=not api_key, key="se_btn"):
            if not se_text:
                st.warning("⚠️ Upload or paste a statute first.")
            else:
                from utils.research_tools import StatuteExplainer
                with st.spinner("Explaining with Claude Opus 4.7…"):
                    try:
                        result = StatuteExplainer(api_key).explain(se_text, se_jur, se_aud)
                        st.session_state.se_result = result
                        st.success("✅ Explanation ready!")
                    except Exception as exc:
                        st.error(f"Explanation failed: {exc}")
        if st.session_state.get("se_result"):
            r = st.session_state.se_result
            st.divider()
            st.markdown(f"## {r.get('title','')}")
            st.markdown(f"**Purpose:** {r.get('purpose','')}")
            st.markdown(r.get("plain_english_summary",""))
            if r.get("key_provisions"):
                section("📋 Key Provisions")
                for p in r["key_provisions"]:
                    imp_color = {"high": "#dc2626", "medium": "#d97706", "low": "#16a34a"}.get(p.get("importance",""),"#64748b")
                    with st.expander(f"§{p.get('section','')} — {p.get('heading','')}"):
                        st.markdown(p.get("explanation",""))
                        st.markdown(f'<span style="color:{imp_color};font-size:0.8rem">Importance: {p.get("importance","").title()}</span>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                if r.get("key_obligations"):
                    section("✅ Key Obligations")
                    for o in r["key_obligations"]: st.markdown(f"- {o}")
            with c2:
                if r.get("penalties"):
                    section("⚠️ Penalties")
                    for p in r["penalties"]: st.warning(p)
            if r.get("faqs"):
                section("❓ Frequently Asked Questions")
                for faq in r["faqs"]:
                    with st.expander(faq.get("question","")):
                        st.markdown(faq.get("answer",""))
            c1, c2, c3 = st.columns(3)
            with c1: download_json("📥 Export Explanation (.json)", r, "statute_explanation.json", key="se_dl")
            with c2: download_docx_from_dict("📝 Download (.docx)", r, "statute_explanation.docx",
                                              title="Statute Explanation", key="se_dl_docx")
            with c3:
                if st.button("🔄 Reset", key="se_rst", use_container_width=True):
                    st.session_state.pop("se_result", None); st.rerun()

    # Legal Term Checker
    with r_tab4:
        st.markdown("Look up the precise legal definition of any term with jurisdiction-specific usage guidance.")
        tc_term = st.text_input("Legal Term or Phrase *", placeholder="e.g. 'res judicata', 'force majeure', 'novation'")
        c1, c2 = st.columns(2)
        tc_jur  = c1.text_input("Jurisdiction", placeholder="e.g. UK, Rwanda, International", key="tc_jur")
        tc_area = c2.text_input("Area of Law", placeholder="e.g. Contract, Procedure, Evidence", key="tc_area")
        if st.button("🔤 Look Up Term", type="primary", disabled=not api_key, key="tc_btn"):
            if not tc_term.strip():
                st.warning("⚠️ Enter a term first.")
            else:
                from utils.research_tools import LegalTermChecker
                with st.spinner("Looking up with Claude Opus 4.7…"):
                    try:
                        result = LegalTermChecker(api_key).check(tc_term.strip(), tc_jur, tc_area)
                        st.session_state.tc_result = result
                        st.success("✅ Done!")
                    except Exception as exc:
                        st.error(f"Lookup failed: {exc}")
        if st.session_state.get("tc_result"):
            r = st.session_state.tc_result
            st.divider()
            st.markdown(f"## {r.get('term','')}")
            st.markdown(f"**Legal Definition:** {r.get('definition','')}")
            st.markdown(f"**Plain English:** {r.get('plain_english','')}")
            st.markdown(f"**Correct Usage:** {r.get('correct_usage','')}")
            if r.get("example_clause"):
                section("📝 Example Clause")
                st.code(r["example_clause"])
            if r.get("common_mistakes"):
                section("⚠️ Common Mistakes")
                for m in r["common_mistakes"]: st.warning(m)
            if r.get("jurisdiction_variations"):
                section("🌍 Jurisdiction Variations")
                for v in r["jurisdiction_variations"]:
                    st.markdown(f"**{v.get('jurisdiction','')}:** _{v.get('equivalent_term','')}_  — {v.get('difference','')}")
            c1, c2, c3 = st.columns(3)
            with c1: download_json("📥 Export (.json)", r, "legal_term.json", key="tc_dl")
            with c2: download_docx_from_dict("📝 Download (.docx)", r, "legal_term_clarification.docx",
                                              title="Legal Term Clarification", key="tc_dl_docx")
            with c3:
                if st.button("🔄 Reset", key="tc_rst", use_container_width=True):
                    st.session_state.pop("tc_result", None); st.rerun()

# ── Translation & Terminology ─────────────────────────────────────
with tab_translation:
    t_tab1, t_tab2 = st.tabs(["🌍 Legal Translation", "🔍 Bilingual Review"])

    with t_tab1:
        st.markdown("Translate legal documents between languages while preserving exact legal meaning and terminology.")
        from utils.shared.document_input import document_input_ui
        lt_text = document_input_ui("lt", paste_placeholder="Paste the document to translate…")
        c1, c2, c3, c4 = st.columns(4)
        lt_src  = c1.text_input("Source Language", placeholder="e.g. French", key="lt_src")
        lt_tgt  = c2.text_input("Target Language", placeholder="e.g. English", key="lt_tgt")
        lt_type = c3.selectbox("Document Type", [
            "Contract", "Court document", "Legal letter", "Statute", "Affidavit", "Other",
        ], key="lt_type")
        lt_form = c4.selectbox("Formality", ["Formal legal", "Professional", "Plain language"], key="lt_form")
        if st.button("🌍 Translate", type="primary", disabled=not api_key, key="lt_btn"):
            if not lt_text:
                st.warning("⚠️ Upload or paste a document first.")
            elif not lt_src.strip() or not lt_tgt.strip():
                st.warning("⚠️ Specify source and target languages.")
            else:
                from utils.legal_translation import LegalTranslator
                with st.spinner("Translating with Claude Opus 4.7…"):
                    try:
                        result = LegalTranslator(api_key).translate(lt_text, lt_src, lt_tgt, lt_type, lt_form)
                        st.session_state.lt_result = result
                        st.success("✅ Translation complete!")
                    except Exception as exc:
                        st.error(f"Translation failed: {exc}")
        if st.session_state.get("lt_result"):
            r = st.session_state.lt_result
            st.divider()
            col_orig, col_trans = st.columns(2)
            with col_orig:
                st.markdown(f"**Original ({lt_src})**")
                st.text_area("", value=lt_text, height=300, disabled=True, key="lt_orig_view")
            with col_trans:
                st.markdown(f"**Translation ({lt_tgt})**")
                st.text_area("", value=r.get("translated_text",""), height=300, key="lt_trans_view")
            if r.get("translator_notes"):
                section("📝 Translator Notes")
                for n in r["translator_notes"]:
                    st.markdown(f"- **{n.get('original_term','')}** → **{n.get('translated_term','')}**: {n.get('note','')}")
            if r.get("untranslatable_terms"):
                section("⚠️ Untranslatable Terms")
                for t in r["untranslatable_terms"]:
                    st.warning(f"**{t.get('term','')}**: {t.get('explanation','')} (Closest: _{t.get('closest_equivalent','')}_)")
            _lt_c1, _lt_c2, _lt_c3 = st.columns(3)
            with _lt_c1:
                st.download_button("📥 Download Translation (.txt)",
                    r.get("translated_text",""), "translation.txt", "text/plain",
                    use_container_width=True, key="lt_dl")
            with _lt_c2:
                download_docx("📝 Download (.docx)", r.get("translated_text",""),
                              "translation.docx", title="Legal Translation", key="lt_dl_docx")
            with _lt_c3:
                if st.button("🔄 Reset", key="lt_rst", use_container_width=True):
                    st.session_state.pop("lt_result", None); st.rerun()

    with t_tab2:
        st.markdown("Compare an original legal document with its translation to detect meaning discrepancies.")
        from utils.shared.document_input import two_document_input_ui
        bl_orig, bl_trans = two_document_input_ui("bl")
        c1, c2 = st.columns(2)
        bl_src = c1.text_input("Source Language", placeholder="e.g. French", key="bl_src")
        bl_tgt = c2.text_input("Target Language", placeholder="e.g. English", key="bl_tgt")
        if st.button("🔍 Review Translation", type="primary", disabled=not api_key, key="bl_btn"):
            if not bl_orig or not bl_trans:
                st.warning("⚠️ Both documents required.")
            else:
                from utils.legal_translation import BilingualReviewer
                with st.spinner("Reviewing with Claude Opus 4.7…"):
                    try:
                        result = BilingualReviewer(api_key).review(bl_orig, bl_trans, bl_src, bl_tgt)
                        st.session_state.bl_result = result
                        st.success("✅ Review complete!")
                    except Exception as exc:
                        st.error(f"Review failed: {exc}")
        if st.session_state.get("bl_result"):
            r = st.session_state.bl_result
            st.divider()
            acc_color = {"Excellent": "#16a34a", "Good": "#2563eb", "Acceptable": "#d97706", "Poor": "#dc2626"}.get(r.get("overall_accuracy",""),"#64748b")
            st.markdown(f'<div class="metric-card" style="width:fit-content"><div class="val" style="color:{acc_color}">{r.get("overall_accuracy","—")}</div><div class="lbl">Overall Accuracy</div></div>', unsafe_allow_html=True)
            st.markdown(f"**Assessment:** {r.get('summary','')}")
            discrepancies = r.get("discrepancies", [])
            if discrepancies:
                section(f"⚠️ Discrepancies ({len(discrepancies)})")
                for d in discrepancies:
                    sev = d.get("severity","medium")
                    fn = st.error if sev == "critical" else (st.warning if sev == "high" else st.info)
                    with st.expander(f"{sev.upper()}: {d.get('issue','')}"):
                        st.markdown(f"**Original:** {d.get('original_text','')}")
                        st.markdown(f"**Translation:** {d.get('translated_text','')}")
                        st.markdown(f"**Correction:** {d.get('suggested_correction','')}")
            else:
                st.success("No significant discrepancies found.")
            if st.button("🔄 Reset", key="bl_rst"):
                st.session_state.pop("bl_result", None); st.rerun()
