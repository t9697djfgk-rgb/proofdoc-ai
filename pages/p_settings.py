import streamlit as st
from utils.shared.sidebar import setup_page
from utils.shared.styles import slim_header, group_header, placeholder_feature, section

setup_page()
slim_header("⚙️", "Settings", "Configure your profile, firm, team, AI preferences, and security")

tab_profile, tab_org, tab_team, tab_ai, tab_security = st.tabs([
    "👤 Profile", "🏛️ Organisation", "👥 Users & Roles",
    "🤖 AI Settings", "🔒 Security & Data",
])

# ── Profile ───────────────────────────────────────────────────────
with tab_profile:
    section("👤 Your Profile")
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown(
            '<div style="width:80px;height:80px;background:#1e3a5f;border-radius:50%;'
            'display:flex;align-items:center;justify-content:center;font-size:2rem;color:white">👤</div>',
            unsafe_allow_html=True,
        )
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Change Photo", use_container_width=True):
            st.info("Photo upload coming soon.")
    with c2:
        first_name = st.text_input("First Name", placeholder="Jane")
        last_name = st.text_input("Last Name", placeholder="Smith")
        email = st.text_input("Email", placeholder="jane.smith@lawfirm.com")
        role = st.text_input("Role / Title", placeholder="e.g. Senior Associate, Partner")
    c1b, c2b, _ = st.columns(3)
    if c1b.button("💾 Save Profile", type="primary", use_container_width=True):
        st.success("✅ Profile saved. (Persistence coming soon)")
    if c2b.button("🔑 Change Password", use_container_width=True):
        st.info("Password management coming soon.")

    st.markdown("<br>", unsafe_allow_html=True)
    placeholder_feature(
        "👤", "Full Profile Management",
        "Manage your complete professional profile, notification preferences, and appearance settings.",
        ["Update personal details and profile photo",
         "Set notification preferences (email, in-app, SMS)",
         "Choose preferred language and timezone",
         "Manage two-factor authentication"],
        ["Updated profile", "Notification settings saved",
         "Personalised workspace preferences"],
    )

# ── Organisation ──────────────────────────────────────────────────
with tab_org:
    section("🏛️ Organisation Settings")
    org_name = st.text_input("Firm / Organisation Name", placeholder="e.g. Smith & Jones LLP")
    org_type = st.selectbox("Organisation Type", [
        "Law firm", "In-house legal team", "Barrister chambers",
        "Legal aid organisation", "Regulatory body", "Other",
    ])
    jurisdiction = st.selectbox("Primary Jurisdiction", [
        "UK", "US", "EU", "Rwanda", "International", "Other",
    ])
    c1, _ = st.columns(2)
    if c1.button("💾 Save Organisation Settings", type="primary", use_container_width=True):
        st.success("✅ Organisation settings saved. (Persistence coming soon)")

    st.markdown("<br>", unsafe_allow_html=True)
    placeholder_feature(
        "🏛️", "Firm Branding",
        "Apply your firm's branding — logo, colours, and letterhead — to all generated documents.",
        ["Upload firm logo for documents and exports",
         "Set primary and secondary brand colours",
         "Configure letterhead template for memos and letters",
         "Apply branding to all AI-generated outputs"],
        ["Branded document outputs", "Firm logo in headers",
         "Consistent letterhead across all exports"],
    )

# ── Users & Roles ─────────────────────────────────────────────────
with tab_team:
    placeholder_feature(
        "👥", "Users & Role Management",
        "Manage team members, assign roles, and control access to sections and matters.",
        ["Invite team members by email",
         "Assign roles: Admin, Partner, Associate, Paralegal, Support, Client",
         "Set section-level permissions per role",
         "Manage matter-level access restrictions"],
        ["User directory", "Role permission matrix",
         "Pending invitation list", "Access change audit log"],
    )

# ── AI Settings ───────────────────────────────────────────────────
with tab_ai:
    section("🤖 AI Configuration")
    st.markdown("**Current AI Provider:** Anthropic Claude Opus 4.7")
    st.markdown("**API Key Status:** Loaded from secrets")

    st.markdown("<br>", unsafe_allow_html=True)
    st.info(
        "🔑 Your API key is stored in `.streamlit/secrets.toml` and is never committed to version control. "
        "On Streamlit Cloud, add it via the Secrets management panel."
    )

    group_header("AI Preferences (Coming Soon)")
    placeholder_feature(
        "🤖", "AI Settings",
        "Configure AI model preferences, default instructions, and jurisdiction-specific behaviour.",
        ["Select preferred Claude model (Opus / Sonnet / Haiku)",
         "Set default jurisdiction and legal style for all AI tools",
         "Add firm-specific instructions appended to all prompts",
         "Configure output language and terminology preferences"],
        ["Saved AI preferences applied across all tools",
         "Firm-specific AI behaviour", "Model cost vs. quality balance control"],
    )

# ── Security & Data ───────────────────────────────────────────────
with tab_security:
    section("🔒 Security & Data Retention")
    group_header("Current Security Status")
    for label, status, color in [
        ("API Key", "Loaded from secrets.toml (not committed to repo)", "#16a34a"),
        ("File Processing", "In-memory only — files auto-deleted after session", "#16a34a"),
        ("Data Retention", "No persistent storage — session-only", "#16a34a"),
        ("AI Training", "Your data is never used to train AI models", "#16a34a"),
    ]:
        st.markdown(
            f'<div class="settings-row">'
            f'<div><h5>{label}</h5><p>{status}</p></div>'
            f'<span style="color:{color};font-size:1.2rem">✓</span>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<br>", unsafe_allow_html=True)
    placeholder_feature(
        "🔒", "Advanced Security Settings",
        "Configure 2FA, SSO, session timeouts, and IP restrictions for enterprise deployments.",
        ["Enable two-factor authentication (2FA)",
         "Configure SSO / SAML integration",
         "Set automatic session timeout duration",
         "Restrict access to approved IP ranges",
         "Configure data residency requirements"],
        ["2FA enabled for all users", "SSO configured and tested",
         "Session policy applied", "IP allowlist enforced"],
    )
