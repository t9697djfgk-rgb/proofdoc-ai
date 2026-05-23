import streamlit as st
from utils.shared.sidebar import setup_page
from utils.shared.styles import slim_header, section
from utils.auth import require_lawyer, is_firm_user
import utils.database as db

setup_page()
user = require_lawyer()

slim_header("📚", "Document Library", "Central repository for all matter documents and files")

tab_all, tab_upload, tab_tools = st.tabs(["📂 All Documents", "⬆️ Upload", "🔗 Document Tools"])

VISIBILITY_LABELS = {
    "internal":          "🔒 Internal",
    "shared_with_client": "🤝 Shared with Client",
    "client_upload":     "📤 Client Upload",
    "final":             "✅ Final",
    "draft":             "📝 Draft",
}

# ── All Documents ──────────────────────────────────────────────────
with tab_all:
    section("All Documents")

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
            '<div style="text-align:center;color:#94a3b8;padding:2rem">'
            '📂 No documents found.<br>'
            '<small>Upload documents using the Upload tab or via matters.</small>'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        h = st.columns([3, 2, 2, 2, 1])
        for col, lbl in zip(h, ["Name", "Matter", "Visibility", "Uploaded", ""]):
            col.markdown(f"**{lbl}**")
        st.divider()

        for doc in docs:
            row = st.columns([3, 2, 2, 2, 1])
            row[0].text(doc.get("name", "")[:55])

            # Matter ref (join via separate query would be expensive; use matter_id key)
            mid = doc.get("matter_id")
            matter_label = "—"
            if mid:
                m_match = next((m for m in matters if m["id"] == mid), None)
                matter_label = m_match["ref"] if m_match else mid[:8]
            row[1].text(matter_label)

            vis = doc.get("visibility", "internal")
            row[2].text(VISIBILITY_LABELS.get(vis, vis))

            ts = str(doc.get("created_at", ""))[:10]
            row[3].text(ts)

            if is_firm_user():
                if row[4].button("🗑️", key=f"dl_del_{doc['id']}", help="Delete document"):
                    db.delete_document(doc["id"])
                    st.rerun()

        st.caption(f"{len(docs)} document{'s' if len(docs) != 1 else ''}")

        # Bulk visibility change (firm users only)
        if is_firm_user():
            st.markdown("<br>", unsafe_allow_html=True)
            with st.expander("⚡ Change Visibility of a Document"):
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
        doc_name = c1.text_input("Document Name *", placeholder="e.g. NDA Draft v2.docx", key="ud_name")
        doc_matter = c2.selectbox("Matter (optional)", list(matter_opts2.keys()), key="ud_matter")
        c3, c4 = st.columns(2)
        doc_vis = c3.selectbox(
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
                name = doc_name.strip()
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
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("**🔄 Convert & Process**")
        st.caption("PDF to Word, Word to PDF, merge, compress.")
        st.page_link("pages/p_doc_convert.py", label="Open Convert Tools →")
    with c2:
        st.markdown("**🗂️ Compare & Manage**")
        st.caption("Document comparison and version tracking.")
        st.page_link("pages/p_doc_manage.py", label="Open Manage Tools →")
    with c3:
        st.markdown("**📝 Draft with AI**")
        st.caption("Clause library and AI-assisted drafting.")
        st.page_link("pages/p_ai_draft.py", label="Open Drafting Tools →")
