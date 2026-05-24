import streamlit as st
import io as _io
import zipfile as _zf
import json as _json
from datetime import date as _date
from utils.shared.sidebar import setup_page
from utils.shared.styles import slim_header, disclaimer, section, risk_badge, group_header
from utils.shared.document_input import two_document_input_ui
from utils.shared.export_utils import download_json

api_key = setup_page()
slim_header("🗂️", "Manage & Compare", "Document comparison, version history, e-signature, and export")

tab_compare, tab_version, tab_esig, tab_export = st.tabs([
    "🔍 Document Comparison",
    "📂 Version History",
    "✍️ E-Signature",
    "📤 Export Center",
])

# ── Document Comparison ───────────────────────────────────────────
with tab_compare:
    disclaimer()
    st.markdown("Upload two versions of a document. The AI will identify legally significant changes.")

    orig_text, rev_text = two_document_input_ui("dc")

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    doc_type = c1.selectbox("Document Type", [
        "Contract", "NDA", "Shareholder agreement", "Employment agreement",
        "Settlement", "Court pleading", "Policy document", "Other",
    ])
    client_position = c2.selectbox("Your Client's Position", [
        "Neutral review", "Buyer / Investor", "Seller / Target",
        "Claimant / Plaintiff", "Defendant",
    ])

    submit = st.button("🔍 Compare Documents", type="primary", disabled=not api_key)

    if submit:
        if not orig_text or not rev_text:
            st.warning("⚠️ Both documents are required for comparison.")
        else:
            from utils.document_comparison import DocumentComparison
            with st.spinner("Comparing with Claude Opus 4.7…"):
                try:
                    result = DocumentComparison(api_key).compare(orig_text, rev_text, doc_type, client_position)
                    st.session_state.dc_result = result
                    st.success("✅ Comparison complete!")
                except Exception as exc:
                    st.error(f"Comparison failed: {exc}")

    if st.session_state.get("dc_result"):
        result   = st.session_state.dc_result
        changes  = result.get("changes", [])
        significant = result.get("significant_changes", [])

        st.divider()
        m1, m2, m3 = st.columns(3)
        for col, val, label, fg, bg in [
            (m1, len(changes),      "Total Changes",     "#1a2744", "#f0f4ff"),
            (m2, len(significant),  "High-Impact",       "#dc2626", "#fef2f2"),
            (m3, result.get("net_effect", "—"), "Net Effect", "#d97706", "#fffbeb"),
        ]:
            col.markdown(
                f'<div style="background:{bg};border-radius:10px;padding:.8rem;text-align:center;'
                f'border-top:3px solid {fg}">'
                f'<div style="font-size:1.4rem;font-weight:700;color:{fg}">{val}</div>'
                f'<div style="font-size:.72rem;color:#64748b;text-transform:uppercase;letter-spacing:.05em">{label}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.markdown(f"<br>**Summary:** {result.get('summary', '')}", unsafe_allow_html=True)

        if changes:
            st.markdown("<br>", unsafe_allow_html=True)
            section(f"📋 Changes ({len(changes)})")
            hdr = st.columns([1, 3, 3, 2, 1])
            for col, lbl in zip(hdr, ["Type", "Original", "Revised", "Legal Significance", "Impact"]):
                col.markdown(f"**{lbl}**")
            st.divider()
            for ch in changes:
                row = st.columns([1, 3, 3, 2, 1])
                row[0].markdown(f"`{ch.get('change_type', '')}`")
                row[1].markdown(f'<span style="color:#dc2626">{ch.get("original_text", "")}</span>', unsafe_allow_html=True)
                row[2].markdown(f'<span style="color:#16a34a">{ch.get("revised_text", "")}</span>', unsafe_allow_html=True)
                row[3].markdown(ch.get("legal_significance", ""))
                row[4].markdown(risk_badge(ch.get("impact_level", "low")), unsafe_allow_html=True)
                st.markdown('<hr style="margin:0.25rem 0;border-color:#f1f5f9">', unsafe_allow_html=True)

        if significant:
            st.markdown("<br>", unsafe_allow_html=True)
            section("🚨 High-Impact Changes")
            for s in significant:
                st.error(s)

        st.markdown("<br>", unsafe_allow_html=True)
        c1, _, c3 = st.columns(3)
        with c1:
            download_json("📥 Download Comparison Report (.json)", result, "comparison_report.json", key="dc_dl")
        with c3:
            if st.button("🔄 Reset", use_container_width=True, key="dc_reset"):
                st.session_state.pop("dc_result", None)
                st.rerun()

# ── Version History ───────────────────────────────────────────────
with tab_version:
    section("📂 Version History")
    st.markdown("Track document versions within this session. Tag each version and add change notes.")

    if "vh_versions" not in st.session_state:
        st.session_state.vh_versions = []

    versions: list[dict] = st.session_state.vh_versions

    # Add version form
    with st.expander("➕ Add Version Entry", expanded=not versions):
        with st.form("vh_add_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            vh_doc   = c1.text_input("Document Name *", placeholder="e.g. NDA_ClientA.docx", key="vh_doc")
            vh_label = c2.text_input("Version Label *", placeholder="e.g. v1.0, Draft 2, Final", key="vh_label")
            c3, c4 = st.columns(2)
            vh_author = c3.text_input("Author", placeholder="Your name", key="vh_author")
            vh_tag    = c4.selectbox("Status Tag", ["Draft", "Under Review", "Approved", "Final", "Executed", "Archived"], key="vh_tag")
            vh_notes  = st.text_area("Change Notes", height=80, placeholder="Describe what changed in this version…", key="vh_notes")
            vh_file   = st.file_uploader("Attach file (optional)", type=["pdf", "docx", "doc", "txt"], key="vh_file")
            if st.form_submit_button("📎 Add Version", type="primary"):
                if not vh_doc.strip() or not vh_label.strip():
                    st.warning("Document name and version label are required.")
                else:
                    entry = {
                        "id":       len(versions) + 1,
                        "document": vh_doc.strip(),
                        "label":    vh_label.strip(),
                        "author":   vh_author.strip() or "—",
                        "tag":      vh_tag,
                        "notes":    vh_notes.strip(),
                        "filename": vh_file.name if vh_file else None,
                        "date":     str(_date.today()),
                    }
                    st.session_state.vh_versions.append(entry)
                    st.success(f"✅ Version **{vh_label}** of *{vh_doc}* recorded.")
                    st.rerun()

    if versions:
        # Group by document name
        docs_seen = list(dict.fromkeys(v["document"] for v in versions))
        f_doc = st.selectbox("Filter by document", ["All documents"] + docs_seen, key="vh_filter")
        shown = versions if f_doc == "All documents" else [v for v in versions if v["document"] == f_doc]

        TAG_CFG = {
            "Draft":        ("#d97706", "#fffbeb"),
            "Under Review": ("#0891b2", "#ecfeff"),
            "Approved":     ("#16a34a", "#f0fdf4"),
            "Final":        ("#7c3aed", "#f5f3ff"),
            "Executed":     ("#1a2744", "#f0f4ff"),
            "Archived":     ("#64748b", "#f1f5f9"),
        }

        st.markdown(f"**{len(shown)} version{'s' if len(shown) != 1 else ''}**")
        for v in reversed(shown):
            fg, bg = TAG_CFG.get(v["tag"], ("#64748b", "#f1f5f9"))
            st.markdown(
                f"""<div style="background:white;border:1px solid #e2e8f0;border-radius:10px;
                              padding:.85rem 1.1rem;margin-bottom:.5rem;border-left:4px solid {fg}">
                  <div style="display:flex;align-items:center;gap:.8rem;flex-wrap:wrap;margin-bottom:.35rem">
                    <span style="font-weight:700;color:#1a2744">{v['document']}</span>
                    <span style="font-size:.75rem;font-weight:700;color:{fg};background:{bg};
                                 padding:.15rem .55rem;border-radius:20px;border:1px solid {fg}40">{v['label']}</span>
                    <span style="font-size:.72rem;font-weight:600;color:{fg};background:{bg};
                                 padding:.15rem .5rem;border-radius:20px">{v['tag']}</span>
                    <span style="margin-left:auto;font-size:.75rem;color:#94a3b8">{v['date']} · {v['author']}</span>
                  </div>
                  {f'<div style="font-size:.83rem;color:#475569">{v["notes"]}</div>' if v["notes"] else ""}
                  {f'<div style="font-size:.78rem;color:#94a3b8;margin-top:.25rem">📎 {v["filename"]}</div>' if v.get("filename") else ""}
                </div>""",
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, _ = st.columns(3)
        c1.download_button(
            "📥 Export Version Log (JSON)",
            _json.dumps(shown, indent=2),
            "version_history.json",
            "application/json",
            use_container_width=True,
        )
        if c2.button("🗑️ Clear All Versions", use_container_width=True, key="vh_clear"):
            st.session_state.vh_versions = []
            st.rerun()
    else:
        st.markdown(
            '<div style="text-align:center;color:#94a3b8;padding:2rem">'
            '📂 No versions recorded yet. Use the form above to start tracking.</div>',
            unsafe_allow_html=True,
        )

# ── E-Signature Tracker ───────────────────────────────────────────
with tab_esig:
    section("✍️ Signature Request Tracker")
    st.markdown("Track e-signature requests. Send requests via your email client and record status here.")
    st.info(
        "💡 **Integration note:** For legally-binding automated e-signatures, integrate with DocuSign, "
        "Adobe Sign, or HelloSign. This tracker lets you record and monitor requests in the meantime."
    )

    if "esig_requests" not in st.session_state:
        st.session_state.esig_requests = []

    requests: list[dict] = st.session_state.esig_requests

    with st.expander("➕ New Signature Request", expanded=not requests):
        with st.form("esig_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            esig_doc    = c1.text_input("Document Name *", placeholder="e.g. Service Agreement v3.pdf", key="esig_doc")
            esig_matter = c2.text_input("Matter Reference", placeholder="e.g. MAT-2026-001", key="esig_matter")
            c3, c4 = st.columns(2)
            esig_signatories = c3.text_area("Signatories (one per line) *", height=90,
                                             placeholder="John Smith <john@example.com>\nJane Doe <jane@co.com>",
                                             key="esig_sigs")
            esig_deadline = c4.date_input("Deadline", value=None, key="esig_deadline")
            esig_notes = st.text_input("Notes", placeholder="e.g. Awaiting board approval before sending", key="esig_notes")
            if st.form_submit_button("📨 Add Request", type="primary"):
                if not esig_doc.strip() or not esig_signatories.strip():
                    st.warning("Document name and at least one signatory are required.")
                else:
                    sigs = [s.strip() for s in esig_signatories.strip().splitlines() if s.strip()]
                    req = {
                        "id":          len(requests) + 1,
                        "document":    esig_doc.strip(),
                        "matter":      esig_matter.strip() or "—",
                        "signatories": sigs,
                        "deadline":    str(esig_deadline) if esig_deadline else "—",
                        "notes":       esig_notes.strip(),
                        "status":      "Pending",
                        "created":     str(_date.today()),
                        "sig_status":  {s: "Pending" for s in sigs},
                    }
                    st.session_state.esig_requests.append(req)
                    st.success(f"✅ Signature request for **{esig_doc}** added.")
                    st.rerun()

    if requests:
        STATUS_CFG = {
            "Pending":   ("#d97706", "#fffbeb"),
            "Sent":      ("#0891b2", "#ecfeff"),
            "Partially Signed": ("#7c3aed", "#f5f3ff"),
            "Completed": ("#16a34a", "#f0fdf4"),
            "Declined":  ("#dc2626", "#fef2f2"),
            "Expired":   ("#64748b", "#f1f5f9"),
        }
        SIG_STATUS_OPTIONS = ["Pending", "Sent", "Signed", "Declined", "Viewed"]

        for req in requests:
            fg, bg = STATUS_CFG.get(req["status"], ("#64748b", "#f1f5f9"))
            with st.container():
                st.markdown(
                    f"""<div style="background:white;border:1px solid #e2e8f0;border-radius:10px;
                                  padding:.85rem 1.1rem;margin-bottom:.3rem;border-left:4px solid {fg}">
                      <div style="display:flex;align-items:center;gap:.8rem;flex-wrap:wrap">
                        <span style="font-weight:700;color:#1a2744">✍️ {req['document']}</span>
                        <span style="font-size:.75rem;color:#64748b">{req['matter']}</span>
                        <span style="font-size:.72rem;font-weight:700;color:{fg};background:{bg};
                                     padding:.15rem .55rem;border-radius:20px;border:1px solid {fg}40">{req['status']}</span>
                        <span style="margin-left:auto;font-size:.75rem;color:#94a3b8">
                          Due: {req['deadline']} · Created: {req['created']}
                        </span>
                      </div>
                      {f'<div style="font-size:.8rem;color:#64748b;margin-top:.35rem">📝 {req["notes"]}</div>' if req.get("notes") else ""}
                    </div>""",
                    unsafe_allow_html=True,
                )

                with st.expander(f"Manage signatories · {len(req['signatories'])} person(s)"):
                    for sig in req["signatories"]:
                        sig_col1, sig_col2 = st.columns([3, 2])
                        sig_col1.markdown(f"**{sig}**")
                        cur = req["sig_status"].get(sig, "Pending")
                        new_stat = sig_col2.selectbox(
                            "Status",
                            SIG_STATUS_OPTIONS,
                            index=SIG_STATUS_OPTIONS.index(cur) if cur in SIG_STATUS_OPTIONS else 0,
                            key=f"esig_stat_{req['id']}_{sig}",
                            label_visibility="collapsed",
                        )
                        if new_stat != cur:
                            req["sig_status"][sig] = new_stat
                            signed_count = sum(1 for s in req["sig_status"].values() if s == "Signed")
                            total = len(req["signatories"])
                            if signed_count == total:
                                req["status"] = "Completed"
                            elif signed_count > 0:
                                req["status"] = "Partially Signed"
                            elif any(s == "Declined" for s in req["sig_status"].values()):
                                req["status"] = "Declined"
                            elif any(s == "Sent" for s in req["sig_status"].values()):
                                req["status"] = "Sent"
                            st.rerun()

                    c_stat, c_del = st.columns([3, 1])
                    new_overall = c_stat.selectbox(
                        "Override request status",
                        list(STATUS_CFG.keys()),
                        index=list(STATUS_CFG.keys()).index(req["status"]) if req["status"] in STATUS_CFG else 0,
                        key=f"esig_overall_{req['id']}",
                    )
                    if new_overall != req["status"]:
                        req["status"] = new_overall
                        st.rerun()
                    if c_del.button("🗑️ Remove", key=f"esig_del_{req['id']}", use_container_width=True):
                        st.session_state.esig_requests = [r for r in requests if r["id"] != req["id"]]
                        st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        # Summary
        total_sigs = sum(len(r["signatories"]) for r in requests)
        signed = sum(1 for r in requests for s, st_ in r["sig_status"].items() if st_ == "Signed")
        completed = sum(1 for r in requests if r["status"] == "Completed")
        s1, s2, s3, s4 = st.columns(4)
        for col, val, label, color in [
            (s1, len(requests), "Requests",  "#1a2744"),
            (s2, completed,     "Completed", "#16a34a"),
            (s3, total_sigs,    "Signatories","#0891b2"),
            (s4, signed,        "Signed",    "#7c3aed"),
        ]:
            col.markdown(
                f'<div style="background:#f8fafc;border-radius:10px;padding:.7rem;text-align:center;'
                f'border-top:3px solid {color}"><div style="font-size:1.3rem;font-weight:700;color:{color}">{val}</div>'
                f'<div style="font-size:.7rem;color:#64748b;text-transform:uppercase;letter-spacing:.05em">{label}</div></div>',
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, _ = st.columns(3)
        c1.download_button(
            "📥 Export Signature Log (JSON)",
            _json.dumps(requests, indent=2),
            "esignature_log.json",
            "application/json",
            use_container_width=True,
        )
        if c2.button("🗑️ Clear All Requests", use_container_width=True, key="esig_clear"):
            st.session_state.esig_requests = []
            st.rerun()
    else:
        st.markdown(
            '<div style="text-align:center;color:#94a3b8;padding:2rem">'
            '✍️ No signature requests yet. Use the form above to start tracking.</div>',
            unsafe_allow_html=True,
        )

# ── Export Center ─────────────────────────────────────────────────
with tab_export:
    group_header("Export Center")
    st.markdown("Collect AI outputs and documents from this session and export them together.")

    _RESULT_LABELS = {
        "ler_result":  ("✍️", "Legal English Review",        "ler_review"),
        "crc_result":  ("⚠️", "Contract Risk Check",         "contract_risk"),
        "cc_result":   ("📚", "Citation Check",              "citation_check"),
        "de_result":   ("⏰", "Deadline Extraction",         "deadlines"),
        "is_result":   ("🔍", "Legal Issue Spotter",         "issue_spotter"),
        "dda_result":  ("🏢", "Due Diligence Review",        "due_diligence"),
        "dca_result":  ("🔍", "Document Comparison",        "doc_comparison"),
        "cs_result":   ("📋", "Contract Summary",           "contract_summary"),
        "rr_result":   ("🚨", "Risk Report",                "risk_report"),
        "da_result":   ("📝", "Legal Draft",                "legal_draft"),
        "lm_result":   ("📄", "Legal Memo",                 "legal_memo"),
        "cp_result":   ("🛡️", "Compliance Policy",          "compliance_policy"),
        "cdc_result":  ("🏛️", "Court Document Check",       "court_doc_check"),
        "tg_result":   ("📅", "Matter Timeline",            "timeline"),
        "ea_result":   ("🧪", "Evidence Analysis",          "evidence_analysis"),
        "wa_result":   ("👤", "Witness Analysis",           "witness_analysis"),
        "ce_result":   ("❓", "Cross-Examination Plan",     "cross_examination"),
        "fc_result":   ("📋", "Filing Checklist",           "filing_checklist"),
        "ab_result":   ("💬", "Legal Argument",             "argument"),
        "hp_result":   ("📝", "Hearing Prep Notes",         "hearing_prep"),
        "lr_result":   ("🔬", "Legal Research",             "research"),
        "csum_result": ("📑", "Case Summary",               "case_summary"),
        "se_result":   ("📖", "Statute Explanation",        "statute_explanation"),
    }

    available = {k: v for k, v in _RESULT_LABELS.items() if st.session_state.get(k)}

    if not available:
        st.markdown(
            '<div style="text-align:center;color:#94a3b8;padding:2rem">'
            '📭 No AI results in this session yet.<br>'
            '<small>Run any AI tool then return here to export.</small></div>',
            unsafe_allow_html=True,
        )
        st.page_link("pages/p_ai_review.py", label="Go to AI Review Tools →")
    else:
        section(f"📦 Available Exports ({len(available)} results)")
        selected_keys = []
        for k, (icon, label, _) in available.items():
            if st.checkbox(f"{icon} {label}", value=True, key=f"exp_{k}"):
                selected_keys.append(k)

        st.markdown("<br>", unsafe_allow_html=True)
        matter_ref = st.text_input("Matter Reference (for filename prefix)",
                                   placeholder="e.g. MAT-2026-0001", key="exp_ref")
        export_format = st.radio("Export Format", ["Individual JSON files (ZIP)",
                                                    "Single combined JSON"], horizontal=True)
        prefix = f"{matter_ref}_" if matter_ref.strip() else ""

        if st.button("📤 Export Selected", type="primary", disabled=not selected_keys, key="exp_btn"):
            if export_format == "Single combined JSON":
                combined = {}
                for k in selected_keys:
                    _, label, slug = _RESULT_LABELS[k]
                    combined[slug] = {"label": label, "data": st.session_state[k]}
                buf = _io.BytesIO(_json.dumps(combined, indent=2).encode())
                fname = f"{prefix}elawfirm_export.json"
                st.download_button("📥 Download Combined JSON", buf.getvalue(),
                                   fname, "application/json", key="exp_dl_combined")
                st.success(f"✅ {len(selected_keys)} results combined into {fname}")
            else:
                zip_buf = _io.BytesIO()
                with _zf.ZipFile(zip_buf, "w", _zf.ZIP_DEFLATED) as zf:
                    for k in selected_keys:
                        _, label, slug = _RESULT_LABELS[k]
                        data = _json.dumps(st.session_state[k], indent=2)
                        zf.writestr(f"{prefix}{slug}.json", data)
                fname = f"{prefix}elawfirm_export.zip"
                st.download_button("📥 Download ZIP", zip_buf.getvalue(),
                                   fname, "application/zip", key="exp_dl_zip")
                st.success(f"✅ {len(selected_keys)} files bundled into {fname}")

        audit = st.session_state.get("last_audit", [])
        if audit:
            st.divider()
            section("📋 Session Audit Log")
            st.caption(f"{len(audit)} entries — documents processed this session")
            audit_buf = _io.BytesIO(_json.dumps(audit, indent=2).encode())
            st.download_button("📥 Export Audit Log (.json)", audit_buf.getvalue(),
                               f"{prefix}audit_log.json", "application/json", key="exp_audit")
