import streamlit as st
import fitz  # PyMuPDF
from utils.shared.sidebar import setup_page
from utils.shared.styles import slim_header, section
from utils.auth import require_lawyer
import utils.database as db

setup_page()
require_lawyer()
slim_header("⚖️", "Rwanda Law Library", "Upload in-force laws as PDF — use them as context in AI tools")

_SETUP_SQL = """
CREATE TABLE IF NOT EXISTS law_library (
    id          UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    organization_id UUID,
    title       TEXT NOT NULL,
    reference   TEXT DEFAULT '',
    category    TEXT DEFAULT '',
    year        INTEGER,
    full_text   TEXT DEFAULT '',
    file_name   TEXT DEFAULT '',
    uploaded_by UUID,
    created_at  TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_law_library_org ON law_library(organization_id);
"""

# ── Setup check ────────────────────────────────────────────────────
try:
    _law_lib_ok = db.law_library_available()
except AttributeError:
    # database module loaded before this code was deployed — force a hard reload
    import importlib, utils.database as _dbmod
    importlib.reload(_dbmod)
    import utils.database as db
    try:
        _law_lib_ok = db.law_library_available()
    except AttributeError:
        _law_lib_ok = False

if not _law_lib_ok:
    st.warning("The **law_library** table has not been created in your Supabase project yet.")
    st.markdown("Run the following SQL once in your **Supabase → SQL Editor**, then refresh:")
    st.code(_SETUP_SQL, language="sql")
    st.stop()

tab_upload, tab_browse = st.tabs(["📤 Upload Law PDF", "📚 Browse Library"])

# ══════════════════════════════════════════════════════════════════
# TAB 1 — UPLOAD
# ══════════════════════════════════════════════════════════════════
with tab_upload:
    section("Upload a Law PDF from amategeko.gov.rw")
    st.markdown(
        '<div style="background:#f0f4ff;border:1px solid #c7d2fe;border-radius:8px;'
        'padding:0.7rem 1rem;margin-bottom:1rem;font-size:0.83rem">'
        '📥 <b>How to get law PDFs:</b> Go to '
        '<a href="https://amategeko.gov.rw/laws/in-force/1" target="_blank">'
        'amategeko.gov.rw</a>, open any law, download its PDF, then upload it here. '
        'Text is extracted automatically and stored for use in AI Chat and Drafting tools.</div>',
        unsafe_allow_html=True,
    )

    up_col, meta_col = st.columns([1, 1], gap="large")

    with up_col:
        pdf_file = st.file_uploader(
            "Upload Law PDF",
            type=["pdf"],
            key="law_upload_file",
            help="Download the PDF from amategeko.gov.rw and upload here",
        )
        if pdf_file:
            st.caption(f"📄 {pdf_file.name} · {pdf_file.size / 1024:.1f} KB")
            # Extract text preview
            if "law_preview_text" not in st.session_state or \
               st.session_state.get("law_preview_name") != pdf_file.name:
                with st.spinner("Extracting text…"):
                    try:
                        doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
                        pages = len(doc)
                        text = "\n".join(page.get_text() for page in doc)
                        doc.close()
                        st.session_state.law_preview_text = text
                        st.session_state.law_preview_pages = pages
                        st.session_state.law_preview_name  = pdf_file.name
                    except Exception as exc:
                        st.error(f"Could not extract text: {exc}")
                        st.session_state.law_preview_text = ""

            text = st.session_state.get("law_preview_text", "")
            pages = st.session_state.get("law_preview_pages", 0)
            if text:
                st.success(f"✅ {pages} page(s) · {len(text):,} characters extracted")
                with st.expander("Preview extracted text (first 1,000 chars)"):
                    st.text(text[:1000])

    with meta_col:
        section("Law Details")
        law_title    = st.text_input("Law Title *",
                                     value=pdf_file.name.replace(".pdf", "").replace("_", " ") if pdf_file else "",
                                     key="law_title",
                                     placeholder="e.g. Labour Code of Rwanda")
        law_ref      = st.text_input("Reference / Number",   key="law_ref",
                                     placeholder="e.g. Law No. 66/2018")
        law_category = st.selectbox("Category", [
            "General", "Labour Law", "Company Law", "Tax Law", "Land Law",
            "Family Law", "Criminal Law", "Civil Procedure", "Constitutional Law",
            "Environmental Law", "Banking & Finance", "Intellectual Property", "Other",
        ], key="law_cat")
        law_year     = st.number_input("Year", min_value=1960, max_value=2030,
                                       value=2024, step=1, key="law_year")

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    save_disabled = not (pdf_file and st.session_state.get("law_preview_text") and law_title.strip())
    if st.button("💾 Save to Law Library", type="primary",
                 disabled=save_disabled, use_container_width=True, key="law_save_btn"):
        ok = db.save_law(
            title=law_title.strip(),
            full_text=st.session_state.law_preview_text,
            reference=law_ref.strip(),
            category=law_category,
            year=int(law_year),
            file_name=pdf_file.name,
        )
        if ok:
            st.success(f"✅ **{law_title}** saved to the Law Library!")
            for k in ("law_preview_text", "law_preview_pages", "law_preview_name"):
                st.session_state.pop(k, None)
            st.rerun()
        else:
            st.error("Failed to save — check that the law_library table exists in Supabase.")


# ══════════════════════════════════════════════════════════════════
# TAB 2 — BROWSE
# ══════════════════════════════════════════════════════════════════
with tab_browse:
    search_q = st.text_input("🔍 Search laws", placeholder="Filter by title…", key="law_search")
    laws = db.list_laws(search=search_q if search_q else None)

    if not laws:
        st.markdown(
            '<div style="text-align:center;color:#9ca3af;padding:2rem">'
            '⚖️ No laws in the library yet.<br>'
            '<small>Upload a law PDF in the <b>Upload</b> tab to get started.</small>'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        st.caption(f"{len(laws)} law(s) in library")
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        CAT_COLORS = {
            "Labour Law":       "#2563eb", "Company Law":          "#059669",
            "Tax Law":          "#d97706", "Land Law":             "#7c3aed",
            "Family Law":       "#db2777", "Criminal Law":         "#dc2626",
            "Civil Procedure":  "#0891b2", "Constitutional Law":   "#1a2744",
            "Environmental Law":"#16a34a", "Banking & Finance":    "#c9a84c",
        }

        for law in laws:
            cat    = law.get("category") or "General"
            color  = CAT_COLORS.get(cat, "#64748b")
            ref    = law.get("reference") or ""
            year   = law.get("year") or ""
            added  = str(law.get("created_at", ""))[:10]

            with st.expander(
                f"⚖️  **{law['title']}**  ·  {ref}  ·  {year}"
            ):
                meta1, meta2, meta3 = st.columns(3)
                meta1.markdown(
                    f'<span style="background:{color}22;color:{color};font-size:0.75rem;'
                    f'font-weight:600;padding:0.2rem 0.6rem;border-radius:20px">{cat}</span>',
                    unsafe_allow_html=True,
                )
                meta2.caption(f"📅 Added: {added}")
                meta3.caption(f"📄 {law.get('file_name','')}")

                # Full text preview
                preview_key = f"law_show_{law['id']}"
                if st.button("📖 View extracted text", key=f"law_view_{law['id']}"):
                    st.session_state[preview_key] = not st.session_state.get(preview_key, False)
                if st.session_state.get(preview_key):
                    full = db.get_law_text(law["id"])
                    if full:
                        st.text_area("Law text", value=full[:5000] + ("…" if len(full) > 5000 else ""),
                                     height=260, disabled=True, key=f"law_txt_{law['id']}")
                        st.caption(f"Total: {len(full):,} characters")
                    else:
                        st.info("No text found.")

                # Delete
                if st.button("🗑️ Remove from library", key=f"law_del_{law['id']}"):
                    db.delete_law(law["id"])
                    st.rerun()
