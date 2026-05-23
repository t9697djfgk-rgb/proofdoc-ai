import streamlit as st
from utils.shared.sidebar import setup_page
from utils.shared.styles import slim_header, group_header, placeholder_feature

setup_page()
slim_header("📦", "Trial Bundles", "Build, paginate, and index court bundles, exhibit lists, and witness lists")

group_header("Bundle Preparation")
c1, c2 = st.columns(2)
with c1:
    placeholder_feature(
        "📦", "Trial Bundle Builder",
        "Compile and organise documents into a properly paginated court bundle.",
        ["Upload documents and assign to bundle sections",
         "Auto-generate index with page numbers",
         "Re-order documents by drag-and-drop",
         "Export as single paginated PDF with tab dividers"],
        ["Paginated PDF bundle", "Bundle index (section, document, page reference)",
         "Tab-divider pages", "Electronic index in Word/Excel"],
    )
with c2:
    placeholder_feature(
        "🔢", "Bundle Pagination & Index",
        "Paginate an existing PDF bundle and generate a formatted index.",
        ["Upload existing bundle PDF", "Apply sequential page numbering",
         "Generate index from bookmarks or manual entries",
         "Match index to bundle tab structure"],
        ["Re-paginated PDF", "Formatted index document",
         "Cross-reference table (document title → page)"],
    )

st.markdown("<br>", unsafe_allow_html=True)
group_header("Trial Lists")
c3, c4 = st.columns(2)
with c3:
    placeholder_feature(
        "📋", "Exhibit List",
        "Create and manage a formal exhibit list for trial or arbitration.",
        ["Add exhibits with reference numbers, descriptions, and dates",
         "Link exhibits to bundle page references",
         "Track which exhibits are agreed / disputed",
         "Export in court-required format"],
        ["Formatted exhibit list", "Agreed / disputed exhibit schedule",
         "Bundle cross-reference column"],
    )
with c4:
    placeholder_feature(
        "🧑‍⚖️", "Witness & Issues List",
        "Manage witness lists and issues lists for trial or hearing preparation.",
        ["Add witnesses with estimated time and topics",
         "Build issues list linked to relevant witnesses and exhibits",
         "Export witness order and issues schedule"],
        ["Witness order and schedule", "Issues list with evidence references",
         "Trial timetable estimate"],
    )
