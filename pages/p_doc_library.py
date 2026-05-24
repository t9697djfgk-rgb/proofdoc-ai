import streamlit as st
from utils.shared.sidebar import setup_page
from utils.shared.styles import slim_header, section
from utils.auth import require_lawyer, is_firm_user
import utils.database as db

api_key = setup_page()
user = require_lawyer()

slim_header("📚", "Document Library", "Central repository for all matter documents and files")

tab_all, tab_upload, tab_tools = st.tabs(["📂 All Documents", "⬆️ Upload", "🔗 Document Tools"])

VISIBILITY_LABELS = {
    "internal":           "🔒 Internal",
    "shared_with_client": "🤝 Shared with Client",
    "client_upload":      "📤 Client Upload",
    "final":              "✅ Final",
    "draft":              "📝 Draft",
}
VIS_COLORS = {
    "internal":           ("#1a2744", "#f0f4ff"),
    "shared_with_client": ("#16a34a", "#f0fdf4"),
    "client_upload":      ("#0891b2", "#ecfeff"),
    "final":              ("#7c3aed", "#f5f3ff"),
    "draft":              ("#d97706", "#fffbeb"),
}
FILE_ICONS = {
    "application/pdf":           "📄",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "📝",
    "application/msword":        "📝",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":       "📊",
    "image/png":                 "🖼️",
    "image/jpeg":                "🖼️",
    "text/plain":                "📃",
}

# ── All Documents ──────────────────────────────────────────────────
with tab_all:
    # Filters
    fc1, fc2, fc3 = st.columns(3)
    matters = db.list_matters()
    matter_opts = {"All Matters": None} | {f"{m['ref']}: {m['title'][:40]}": m["id"] for m in matters}
    f_matter = fc1.selectbox("Matter", list(matter_opts.keys()), key="dl_matter")
    f_vis    = fc2.selectbox("Visibility", ["All"] + list(VISIBILITY_LABELS.keys()), key="dl_vis",
                              format_func=lambda v: "All" if v == "All" else VISIBILITY_LABELS.get(v, v))
    f_search = fc3.text_input("Search by name", placeholder="e.g. NDA, contract…", key="dl_search")

    docs = db.list_documents(
        matter_id=matter_opts[f_matter],
        visibility=None if f_vis == "All" else f_vis,
    )

    if f_search.strip():
        docs = [d for d in docs if f_search.strip().lower() in d.get("name", "").lower()]

    if not docs:
        st.markdown(
            '<div style="text-align:center;color:#94a3b8;padding:2.5rem">'
            '📂 No documents found.<br>'
            '<small>Upload documents using the Upload tab or via matters.</small>'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        # Stats banner
        by_vis = {}
        for d in docs:
            v = d.get("visibility", "internal")
            by_vis[v] = by_vis.get(v, 0) + 1

        stat_cards = [("All Documents", len(docs), "#1a2744", "#f0f4ff")]
        for v, cnt in sorted(by_vis.items(), key=lambda x: -x[1]):
            fg, bg = VIS_COLORS.get(v, ("#64748b", "#f1f5f9"))
            stat_cards.append((VISIBILITY_LABELS.get(v, v).replace("🔒 ", "").replace("🤝 ", "").replace("📤 ", "").replace("✅ ", "").replace("📝 ", ""), cnt, fg, bg))

        col_count = min(len(stat_cards), 5)
        stat_cols = st.columns(col_count)
        for col, (label, cnt, fg, bg) in zip(stat_cols, stat_cards[:col_count]):
            col.markdown(
                f'<div style="background:{bg};border-radius:10px;padding:.7rem 1rem;'
                f'border-left:3px solid {fg};text-align:center;margin-bottom:.5rem">'
                f'<div style="font-size:1.3rem;font-weight:700;color:{fg}">{cnt}</div>'
                f'<div style="font-size:.68rem;color:#64748b;text-transform:uppercase;letter-spacing:.05em">{label}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)
        st.caption(f"{len(docs)} document{'s' if len(docs) != 1 else ''}")

        _vers_avail = db.doc_versions_available()

        # Document cards
        for doc in docs:
            vis = doc.get("visibility", "internal")
            fg, bg = VIS_COLORS.get(vis, ("#64748b", "#f1f5f9"))
            vis_label = VISIBILITY_LABELS.get(vis, vis)
            ftype = doc.get("file_type", "") or ""
            ficon = FILE_ICONS.get(ftype, "📎")
            ts = str(doc.get("created_at", ""))[:10]
            name = doc.get("name", "Untitled")

            mid = doc.get("matter_id")
            matter_label = "—"
            if mid:
                m_match = next((m for m in matters if m["id"] == mid), None)
                matter_label = m_match["ref"] if m_match else mid[:8]

            fsize = doc.get("file_size")
            size_str = f"{fsize // 1024} KB" if fsize and fsize >= 1024 else (f"{fsize} B" if fsize else "")

            # Version count badge
            if _vers_avail:
                _versions = db.list_document_versions(doc["id"])
                _ver_badge = (
                    f'<span style="font-size:.68rem;color:#7c3aed;background:#f5f3ff;'
                    f'padding:.1rem .4rem;border-radius:20px;font-weight:600">v{len(_versions)+1}</span>'
                    if _versions else ""
                )
            else:
                _versions, _ver_badge = [], ""

            del_col, card_col = st.columns([0.08, 0.92])
            with card_col:
                st.markdown(
                    f"""<div style="background:white;border:1px solid #e2e8f0;border-radius:10px;
                                  padding:.75rem 1rem;margin-bottom:.2rem;
                                  border-left:4px solid {fg};display:flex;align-items:center;gap:1rem;flex-wrap:wrap">
                      <span style="font-size:1.3rem">{ficon}</span>
                      <div style="flex:1;min-width:0">
                        <div style="font-weight:600;color:#1a2744;font-size:.88rem;
                                    white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{name}
                          {_ver_badge}
                        </div>
                        <div style="font-size:.75rem;color:#64748b;margin-top:.15rem">
                          {matter_label}{(" · " + size_str) if size_str else ""}
                        </div>
                      </div>
                      <div style="display:flex;align-items:center;gap:.8rem;flex-shrink:0">
                        <span style="font-size:.72rem;font-weight:700;color:{fg};background:{bg};
                                     padding:.2rem .6rem;border-radius:20px;border:1px solid {fg}40">{vis_label}</span>
                        <span style="font-size:.75rem;color:#94a3b8">{ts}</span>
                      </div>
                    </div>""",
                    unsafe_allow_html=True,
                )

                if _vers_avail and is_firm_user():
                    with st.expander(f"📚 Version History ({len(_versions)+1} total)", expanded=False):
                        # Current version
                        st.markdown(
                            f'<div style="background:#f0fdf4;border-radius:6px;padding:.4rem .7rem;'
                            f'margin-bottom:.25rem;font-size:.8rem;border-left:3px solid #16a34a">'
                            f'<b>v{len(_versions)+1}</b> — <em>Current</em> · {ts}'
                            f'</div>',
                            unsafe_allow_html=True,
                        )
                        for _v in _versions:
                            _vts = str(_v.get("created_at",""))[:10]
                            st.markdown(
                                f'<div style="background:#f8fafc;border-radius:6px;padding:.4rem .7rem;'
                                f'margin-bottom:.25rem;font-size:.8rem;border-left:3px solid #94a3b8">'
                                f'<b>v{_v["version_number"]}</b> — {_v.get("name","") or "Version"}'
                                f'{(" · " + _v["notes"]) if _v.get("notes") else ""} · <span style="color:#9ca3af">{_vts}</span>'
                                f'</div>',
                                unsafe_allow_html=True,
                            )
                        st.markdown("**Upload new version:**")
                        _nv_name  = st.text_input("Version name/label", key=f"nv_name_{doc['id']}",
                                                   placeholder="e.g. Draft v2 with client changes")
                        _nv_notes = st.text_input("Notes", key=f"nv_notes_{doc['id']}",
                                                   placeholder="What changed?")
                        _nv_file  = st.file_uploader("Attach file (optional)", key=f"nv_file_{doc['id']}")
                        if st.button("⬆️ Save New Version", key=f"nv_save_{doc['id']}", type="primary"):
                            _next_ver = len(_versions) + 1
                            db.add_document_version(
                                doc_id=doc["id"],
                                version_number=_next_ver,
                                name=_nv_name.strip() or f"Version {_next_ver}",
                                notes=_nv_notes.strip(),
                                file_type=_nv_file.type if _nv_file else ftype,
                                file_size=_nv_file.size if _nv_file else None,
                            )
                            # Update main doc record with new name if provided
                            if _nv_name.strip():
                                db.update_document_visibility(doc["id"], vis)
                            st.success(f"✅ Version {_next_ver} saved.")
                            st.rerun()

            with del_col:
                if is_firm_user():
                    st.markdown("<br>", unsafe_allow_html=True)
                    if st.button("🗑️", key=f"dl_del_{doc['id']}", help="Delete document"):
                        db.delete_document(doc["id"])
                        st.rerun()

        # Version control setup prompt
        if is_firm_user() and not _vers_avail:
            with st.expander("💡 Enable Document Version Control"):
                st.info("Run this SQL in your Supabase SQL Editor to enable version history:")
                st.code(
                    "CREATE TABLE document_versions (\n"
                    "  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),\n"
                    "  organization_id text NOT NULL,\n"
                    "  document_id uuid REFERENCES documents(id) ON DELETE CASCADE,\n"
                    "  version_number integer NOT NULL,\n"
                    "  name text,\n"
                    "  notes text,\n"
                    "  file_type text,\n"
                    "  file_size bigint,\n"
                    "  uploaded_by uuid,\n"
                    "  created_at timestamptz DEFAULT now()\n"
                    ");",
                    language="sql",
                )

        # Bulk visibility change (firm users only)
        if is_firm_user():
            st.markdown("<br>", unsafe_allow_html=True)
            with st.expander("⚡ Change Document Visibility"):
                doc_opts = {d.get("name", d["id"]): d["id"] for d in docs}
                c1, c2, c3 = st.columns([3, 2, 1])
                sel_doc = c1.selectbox("Document", list(doc_opts.keys()), key="vis_doc")
                new_vis = c2.selectbox("New Visibility", list(VISIBILITY_LABELS.keys()),
                                       format_func=lambda v: VISIBILITY_LABELS.get(v, v), key="vis_new")
                if c3.button("Apply", key="vis_apply", type="primary"):
                    db.update_document_visibility(doc_opts[sel_doc], new_vis)
                    st.success("✅ Visibility updated.")
                    st.rerun()

# ── Upload ─────────────────────────────────────────────────────────
with tab_upload:
    section("⬆️ Upload Document")
    st.info("Documents uploaded here are stored as metadata records. File content can be attached via the matter discussion or client portal.")

    with st.form("upload_doc_form", clear_on_submit=True):
        matters_active = db.list_matters(status="Active") or matters
        matter_opts2 = {"(No specific matter)": None} | {f"{m['ref']}: {m['title'][:40]}": m["id"] for m in matters_active}
        c1, c2 = st.columns(2)
        doc_name   = c1.text_input("Document Name *", placeholder="e.g. NDA Draft v2.docx", key="ud_name")
        doc_matter = c2.selectbox("Matter (optional)", list(matter_opts2.keys()), key="ud_matter")
        c3, c4 = st.columns(2)
        doc_vis  = c3.selectbox(
            "Visibility *",
            list(VISIBILITY_LABELS.keys()),
            format_func=lambda v: VISIBILITY_LABELS.get(v, v),
            key="ud_vis",
        )
        doc_desc = c4.text_input("Description (optional)", key="ud_desc")
        uploaded_file = st.file_uploader(
            "Attach file (optional)",
            type=["pdf", "docx", "doc", "xlsx", "png", "jpg", "txt"],
            key="ud_file",
        )
        if st.form_submit_button("⬆️ Upload", type="primary"):
            if not doc_name.strip():
                st.warning("Document name is required.")
            else:
                name  = doc_name.strip()
                ftype = uploaded_file.type if uploaded_file else None
                fsize = uploaded_file.size if uploaded_file else None
                result = db.add_document(
                    name=name,
                    matter_id=matter_opts2[doc_matter],
                    file_type=ftype,
                    file_size=fsize,
                    visibility=doc_vis,
                    description=doc_desc.strip(),
                )
                if result:
                    st.success(f"✅ **{name}** added to the document library.")
                else:
                    st.error("Failed to save document record.")

# ── Document Tools ─────────────────────────────────────────────────
with tab_tools:
    section("🔗 Quick Links to Document Tools")

    tools = [
        ("🔄 Convert & Process", "PDF to Word, Word to PDF, merge, compress.", "pages/p_doc_convert.py", "Open Convert Tools →", "#1a2744"),
        ("🗂️ Compare & Manage",  "Document comparison, version tracking, e-signature.", "pages/p_doc_manage.py",  "Open Manage Tools →",   "#7c3aed"),
        ("📝 Draft with AI",     "Clause library and AI-assisted drafting.",            "pages/p_ai_draft.py",    "Open Drafting Tools →", "#c9a84c"),
    ]
    tc1, tc2, tc3 = st.columns(3)
    for col, (title, caption, link, lbl, color) in zip([tc1, tc2, tc3], tools):
        with col:
            st.markdown(
                f'<div style="background:white;border:1px solid #e2e8f0;border-radius:12px;'
                f'padding:1.2rem;border-top:4px solid {color};min-height:120px">'
                f'<div style="font-weight:700;color:#1a2744;margin-bottom:.4rem">{title}</div>'
                f'<div style="font-size:.82rem;color:#64748b">{caption}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            st.page_link(link, label=lbl)
