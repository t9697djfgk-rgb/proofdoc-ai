import streamlit as st

st.set_page_config(
    page_title="ProofDoc AI · Legal Workspace",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Navigation ────────────────────────────────────────────────────
pg = st.navigation(
    {
        "": [
            st.Page("pages/p_dashboard.py", title="Dashboard", icon="🏠", default=True),
        ],
        "Matters": [
            st.Page("pages/p_matters_list.py",  title="Matters",        icon="📁"),
            st.Page("pages/p_client_intake.py", title="Client Intake",  icon="👤"),
            st.Page("pages/p_due_diligence.py", title="Due Diligence",  icon="🏢"),
        ],
        "Documents": [
            st.Page("pages/p_doc_library.py",  title="Document Library",   icon="📚"),
            st.Page("pages/p_doc_convert.py",  title="Convert & Process",  icon="🔄"),
            st.Page("pages/p_doc_manage.py",   title="Manage & Compare",   icon="🗂️"),
        ],
        "AI Tools": [
            st.Page("pages/p_ai_review.py",      title="Review",       icon="🔍"),
            st.Page("pages/p_ai_draft.py",       title="Draft",        icon="📝"),
            st.Page("pages/p_ai_analysis.py",    title="Analysis",     icon="📊"),
            st.Page("pages/p_ai_research.py",    title="Research",     icon="🔬"),
            st.Page("pages/p_ai_calculators.py", title="Calculators",  icon="🧮"),
        ],
        "Trial": [
            st.Page("pages/p_trial.py",    title="Trial Workspace",     icon="🏛️"),
            st.Page("pages/p_evidence.py", title="Evidence & Witnesses", icon="🧪"),
            st.Page("pages/p_bundles.py",  title="Trial Bundles",       icon="📦"),
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
            st.Page("pages/p_settings.py", title="Settings", icon="⚙️"),
        ],
    },
    position="sidebar",
)

pg.run()
