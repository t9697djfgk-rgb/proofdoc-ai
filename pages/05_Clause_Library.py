import streamlit as st
from datetime import datetime
from utils.shared.styles import inject_css, page_header, section, risk_badge
from utils.shared.sidebar import render_sidebar
from utils.clause_library import (
    CATEGORIES, JURISDICTIONS, get_all, search, add_clause, update_clause, delete_clause
)

st.set_page_config(page_title="Clause Library · ProofDoc AI", page_icon="📚", layout="wide")
inject_css()
render_sidebar("Clause Library")
page_header("📚", "Clause Library", "Browse, search, store, and reuse legal clauses")

tab_browse, tab_add = st.tabs(["🔍 Browse & Search", "➕ Add Custom Clause"])

# ── Browse & Search ──────────────────────────────────────────────
with tab_browse:
    f1, f2, f3 = st.columns([2, 1.5, 1.5])
    query = f1.text_input("Search", placeholder="Search by title or text…", key="cl_query")
    cat_filter = f2.selectbox("Category", ["All"] + CATEGORIES, key="cl_cat")
    jur_filter = f3.selectbox("Jurisdiction", ["All"] + JURISDICTIONS, key="cl_jur")

    clauses = search(
        query=query,
        category=cat_filter if cat_filter != "All" else "",
        jurisdiction=jur_filter if jur_filter != "All" else "",
    )

    st.caption(f"Showing {len(clauses)} clause(s)")
    st.markdown("<br>", unsafe_allow_html=True)

    if not clauses:
        st.info("No clauses found. Try a different search or add a custom clause.")
    else:
        for clause in clauses:
            approved_tag = "✅ Firm-approved" if clause.get("approved") else "📝 Draft"
            header = (
                f"**{clause.get('title','')}** &nbsp; "
                f"<span class='badge-doc'>{clause.get('category','')}</span> &nbsp; "
                f"<span class='badge-doc'>{clause.get('jurisdiction','')}</span> &nbsp; "
                f"{risk_badge(clause.get('risk_level','low'))} &nbsp; {approved_tag}"
            )
            with st.expander(clause.get("title",""), expanded=False):
                st.markdown(header, unsafe_allow_html=True)

                if clause.get("notes"):
                    st.caption(f"📌 {clause['notes']}")

                st.code(clause.get("clause_text", ""), language=None)

                btn_cols = st.columns([1, 1, 1, 1, 2])
                with btn_cols[0]:
                    st.download_button(
                        "📋 Copy (.txt)",
                        data=clause.get("clause_text",""),
                        file_name=f"{clause.get('id','clause')}.txt",
                        mime="text/plain",
                        use_container_width=True,
                        key=f"dl_{clause['id']}",
                    )

                # Toggle approved
                with btn_cols[1]:
                    approved_label = "✅ Approved" if clause.get("approved") else "Mark Approved"
                    if st.button(approved_label, use_container_width=True, key=f"appr_{clause['id']}"):
                        update_clause(clause["id"], approved=not clause.get("approved"))
                        st.rerun()

                # Edit notes
                with btn_cols[2]:
                    if st.button("📝 Edit Notes", use_container_width=True, key=f"note_{clause['id']}"):
                        st.session_state[f"edit_note_{clause['id']}"] = True

                # Delete
                with btn_cols[3]:
                    if st.button("🗑️ Delete", use_container_width=True, key=f"del_{clause['id']}"):
                        delete_clause(clause["id"])
                        st.success("Clause deleted.")
                        st.rerun()

                # Inline notes editor
                if st.session_state.get(f"edit_note_{clause['id']}"):
                    new_note = st.text_area("Notes", value=clause.get("notes",""), key=f"note_txt_{clause['id']}")
                    if st.button("Save Notes", key=f"save_note_{clause['id']}"):
                        update_clause(clause["id"], notes=new_note)
                        st.session_state.pop(f"edit_note_{clause['id']}", None)
                        st.rerun()

# ── Add Custom Clause ────────────────────────────────────────────
with tab_add:
    section("➕ Add Custom Clause")
    with st.form("add_clause_form"):
        title = st.text_input("Clause Title *", placeholder="e.g. Confidentiality Clause (Unilateral)")
        col1, col2, col3 = st.columns(3)
        category = col1.selectbox("Category *", CATEGORIES)
        jurisdiction = col2.selectbox("Jurisdiction *", JURISDICTIONS)
        risk_level = col3.selectbox("Risk Level", ["low", "medium", "high"])
        clause_text = st.text_area("Clause Text *", height=250,
                                    placeholder="Enter the full clause text here…")
        notes = st.text_area("Notes / Usage Guidance", height=80,
                              placeholder="When to use, conditions, jurisdictional notes…")
        approved = st.checkbox("Mark as firm-approved")

        submitted = st.form_submit_button("➕ Add Clause", type="primary")
        if submitted:
            if not title.strip() or not clause_text.strip():
                st.error("Title and clause text are required.")
            else:
                new = add_clause(
                    title=title.strip(),
                    category=category,
                    jurisdiction=jurisdiction,
                    clause_text=clause_text.strip(),
                    notes=notes.strip(),
                    risk_level=risk_level,
                    approved=approved,
                )
                st.success(f"✅ Clause '{new['title']}' added (ID: {new['id']})")
                st.rerun()
