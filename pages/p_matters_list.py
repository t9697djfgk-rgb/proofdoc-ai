import streamlit as st
from utils.shared.sidebar import setup_page
from utils.shared.styles import slim_header, placeholder_feature, group_header

setup_page()
slim_header("📁", "Matters", "Manage clients, matters, leads, and engagement workflow")

tab_matters, tab_clients, tab_leads, tab_conflict, tab_engagement = st.tabs([
    "📁 Matters", "👥 Clients", "🔮 Leads", "⚖️ Conflict Check", "📜 Engagement Letters",
])

# ── MATTERS ──────────────────────────────────────────────────────
with tab_matters:
    c_left, c_right = st.columns([3, 1])
    c_left.markdown("### Active Matters")
    if c_right.button("+ New Matter", type="primary", use_container_width=True):
        st.info("Matter creation requires a database — coming soon.")

    st.markdown(
        '<div class="empty-list" style="margin-top:1rem">'
        '📁 No matters yet.<br>'
        '<small>Create your first matter to start organising client work.</small>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    group_header("Matter Structure — What each matter will contain")
    tabs_inner = st.tabs([
        "Overview", "Documents", "AI Reviews", "Drafts",
        "Deadlines", "Timeline", "Evidence", "Trial",
        "Research", "Billing", "Notes", "Audit History",
    ])
    for tab in tabs_inner:
        with tab:
            st.markdown(
                '<div class="empty-list">Open or create a matter to view this section.</div>',
                unsafe_allow_html=True,
            )

# ── CLIENTS ──────────────────────────────────────────────────────
with tab_clients:
    c_left, c_right = st.columns([3, 1])
    c_left.markdown("### Clients")
    if c_right.button("+ Add Client", type="primary", use_container_width=True):
        st.info("Client directory requires a database — coming soon.")

    st.markdown(
        '<div class="empty-list" style="margin-top:1rem">'
        '👥 No clients yet.<br>'
        '<small>Add a client to begin managing their matters.</small>'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown("<br>", unsafe_allow_html=True)
    placeholder_feature(
        "👥", "Client Directory",
        "A full client directory with contact details, matter history, billing, and portal access.",
        ["Add and manage client profiles", "Link clients to matters", "View billing history",
         "Send secure documents via client portal"],
        ["Client profile card", "Matter list per client", "Document access log", "Billing summary"],
    )

# ── LEADS ─────────────────────────────────────────────────────────
with tab_leads:
    placeholder_feature(
        "🔮", "Lead Management",
        "Track prospective clients and convert them into active matters once engaged.",
        ["Log new leads from enquiries", "Track lead status (new, contacted, quoted, converted)",
         "Convert lead to matter with one click", "Generate initial advice letters"],
        ["Lead pipeline view", "Conversion funnel metrics", "Automated follow-up log"],
    )

# ── CONFLICT CHECK ────────────────────────────────────────────────
with tab_conflict:
    placeholder_feature(
        "⚖️", "Conflict Check",
        "Screen new matters against existing clients and opposing parties to detect conflicts of interest.",
        ["Enter party names and run conflict screen", "Compare against existing client database",
         "Flag potential conflicts with confidence score", "Generate conflict-clear certificate"],
        ["Conflict report", "Clear certificate", "Flagged conflicts list with detail"],
    )

# ── ENGAGEMENT LETTERS ────────────────────────────────────────────
with tab_engagement:
    placeholder_feature(
        "📜", "Engagement Letters",
        "Generate and manage client engagement letters for new matters.",
        ["Draft engagement letters from matter details", "Include scope, fees, terms, and retainer info",
         "Send for e-signature", "Log signed versions in matter"],
        ["Engagement letter draft (Word/PDF)", "Signature-ready document", "Signed copy stored in matter"],
    )
