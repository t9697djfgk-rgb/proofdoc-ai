import streamlit as st
from utils.database import init_db

init_db()

st.set_page_config(
    page_title="eLawFirm · Legal Workspace",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

user = st.session_state.get("user")

# ── Not logged in ─────────────────────────────────────────────────
if not user:
    pg = st.navigation(
        [st.Page("pages/p_login.py", title="Sign In", icon="🔐", default=True)],
        position="hidden",
    )

# ── Client portal ─────────────────────────────────────────────────
elif user["role"] == "client":
    pg = st.navigation(
        {
            "": [st.Page("pages/p_client_portal.py", title="My Portal", icon="🏢", default=True)],
        },
        position="sidebar",
    )

# ── Admin ─────────────────────────────────────────────────────────
elif user["role"] == "admin":
    pg = st.navigation(
        {
            "": [
                st.Page("pages/p_lawyer_dashboard.py", title="Dashboard",   icon="🏠", default=True),
                st.Page("pages/p_admin.py",            title="Admin Panel", icon="🛡️"),
            ],
            "Matters": [
                st.Page("pages/p_matters_list.py",   title="Matters",        icon="📁"),
                st.Page("pages/p_client_intake.py",  title="Client Intake",  icon="👤"),
                st.Page("pages/p_due_diligence.py",  title="Due Diligence",  icon="🏢"),
            ],
            "Collaboration": [
                st.Page("pages/p_matter_discussion.py", title="Discussions", icon="💬"),
            ],
            "Documents": [
                st.Page("pages/p_doc_library.py",  title="Document Library",  icon="📚"),
                st.Page("pages/p_doc_convert.py",  title="Convert & Process", icon="🔄"),
                st.Page("pages/p_doc_manage.py",   title="Manage & Compare",  icon="🗂️"),
            ],
            "AI Tools": [
                st.Page("pages/p_ai_chat.py",        title="AI Assistant",  icon="💬"),
                st.Page("pages/p_law_library.py",    title="Law Library",   icon="⚖️"),
                st.Page("pages/p_ai_review.py",      title="Review",        icon="🔍"),
                st.Page("pages/p_ai_draft.py",       title="Draft",         icon="📝"),
                st.Page("pages/p_ai_analysis.py",    title="Analysis",      icon="📊"),
                st.Page("pages/p_ai_research.py",    title="Research",      icon="🔬"),
                st.Page("pages/p_ai_calculators.py", title="Calculators",   icon="🧮"),
            ],
            "Trial": [
                st.Page("pages/p_trial.py",    title="Trial Workspace",      icon="🏛️"),
                st.Page("pages/p_evidence.py", title="Evidence & Witnesses", icon="🧪"),
                st.Page("pages/p_bundles.py",  title="Trial Bundles",        icon="📦"),
            ],
            "Operations": [
                st.Page("pages/p_operations.py",   title="Tasks & Calendar", icon="📅"),
                st.Page("pages/p_billing.py",      title="Billing & Time",   icon="💼"),
                st.Page("pages/p_integrations.py", title="Integrations",     icon="🔗"),
            ],
            "Compliance": [
                st.Page("pages/p_compliance.py", title="Compliance Tools", icon="🛡️"),
                st.Page("pages/p_audit.py",      title="Audit Trail",      icon="📋"),
            ],
            "Settings": [
                st.Page("pages/p_settings.py",   title="Settings",        icon="⚙️"),
                st.Page("pages/p_onboarding.py", title="Getting Started", icon="🚀"),
            ],
        },
        position="sidebar",
    )

# ── Lawyer / Staff / Intern ───────────────────────────────────────
else:
    pg = st.navigation(
        {
            "": [
                st.Page("pages/p_lawyer_dashboard.py", title="Dashboard", icon="🏠", default=True),
            ],
            "Matters": [
                st.Page("pages/p_matters_list.py",   title="Matters",       icon="📁"),
                st.Page("pages/p_client_intake.py",  title="Client Intake", icon="👤"),
                st.Page("pages/p_due_diligence.py",  title="Due Diligence", icon="🏢"),
            ],
            "Collaboration": [
                st.Page("pages/p_matter_discussion.py", title="Discussions", icon="💬"),
            ],
            "Documents": [
                st.Page("pages/p_doc_library.py",  title="Document Library",  icon="📚"),
                st.Page("pages/p_doc_convert.py",  title="Convert & Process", icon="🔄"),
                st.Page("pages/p_doc_manage.py",   title="Manage & Compare",  icon="🗂️"),
            ],
            "AI Tools": [
                st.Page("pages/p_ai_chat.py",        title="AI Assistant",  icon="💬"),
                st.Page("pages/p_law_library.py",    title="Law Library",   icon="⚖️"),
                st.Page("pages/p_ai_review.py",      title="Review",        icon="🔍"),
                st.Page("pages/p_ai_draft.py",       title="Draft",         icon="📝"),
                st.Page("pages/p_ai_analysis.py",    title="Analysis",      icon="📊"),
                st.Page("pages/p_ai_research.py",    title="Research",      icon="🔬"),
                st.Page("pages/p_ai_calculators.py", title="Calculators",   icon="🧮"),
            ],
            "Trial": [
                st.Page("pages/p_trial.py",    title="Trial Workspace",      icon="🏛️"),
                st.Page("pages/p_evidence.py", title="Evidence & Witnesses", icon="🧪"),
                st.Page("pages/p_bundles.py",  title="Trial Bundles",        icon="📦"),
            ],
            "Operations": [
                st.Page("pages/p_operations.py",   title="Tasks & Calendar", icon="📅"),
                st.Page("pages/p_billing.py",      title="Billing & Time",   icon="💼"),
                st.Page("pages/p_integrations.py", title="Integrations",     icon="🔗"),
            ],
            "Compliance": [
                st.Page("pages/p_compliance.py", title="Compliance Tools", icon="🛡️"),
                st.Page("pages/p_audit.py",      title="Audit Trail",      icon="📋"),
            ],
            "Settings": [
                st.Page("pages/p_settings.py",   title="Settings",        icon="⚙️"),
                st.Page("pages/p_onboarding.py", title="Getting Started", icon="🚀"),
            ],
        },
        position="sidebar",
    )

pg.run()
