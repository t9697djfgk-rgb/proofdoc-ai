import streamlit as st
from utils.shared.sidebar import setup_page
from utils.shared.styles import slim_header, placeholder_feature, group_header

setup_page()
slim_header("📚", "Document Library", "Central repository for all matter documents and files")

st.markdown("<br>", unsafe_allow_html=True)

# Quick links to working tools
group_header("Available Now")
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(
        '<div class="feature-card">'
        '<div class="fc-badge"><span class="badge-available">● Available</span></div>'
        '<div class="fc-icon">🔄</div>'
        '<div class="fc-name">Convert & Process</div>'
        '<div class="fc-desc">PDF to Word, Word to PDF, merge PDFs, and more.</div>'
        '<div class="fc-best">Best for: File format conversion</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.page_link("pages/p_doc_convert.py", label="Open Convert Tools →", use_container_width=True)
with c2:
    st.markdown(
        '<div class="feature-card">'
        '<div class="fc-badge"><span class="badge-available">● Available</span></div>'
        '<div class="fc-icon">🗂️</div>'
        '<div class="fc-name">Compare & Manage</div>'
        '<div class="fc-desc">Document comparison, version control, and e-signature tracking.</div>'
        '<div class="fc-best">Best for: Redline reviews</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.page_link("pages/p_doc_manage.py", label="Open Manage Tools →", use_container_width=True)
with c3:
    st.markdown(
        '<div class="feature-card">'
        '<div class="fc-badge"><span class="badge-available">● Available</span></div>'
        '<div class="fc-icon">📖</div>'
        '<div class="fc-name">Clause Library</div>'
        '<div class="fc-desc">Browse, search, and manage reusable standard clause templates.</div>'
        '<div class="fc-best">Best for: Drafting efficiency</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.page_link("pages/p_ai_draft.py", label="Open Clause Library →", use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)
group_header("Coming Soon")

placeholder_feature(
    "📚", "Document Library",
    "A searchable, matter-linked central document repository with folders, tags, and version history.",
    [
        "Upload documents directly to matter folders",
        "Search documents by name, type, date, or content",
        "Tag documents with matter references",
        "Set access permissions per user or team",
        "View document history and restore earlier versions",
    ],
    [
        "Organised folder structure per matter",
        "Full-text search across all documents",
        "Version history timeline",
        "Access and audit log per document",
    ],
)
