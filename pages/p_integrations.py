import streamlit as st
from utils.shared.sidebar import setup_page
from utils.shared.styles import slim_header, group_header

from utils.auth import require_lawyer
setup_page()
require_lawyer()
slim_header("🔗", "Integrations", "Connect ProofDoc AI to your existing tools and platforms")

st.markdown(
    '<div class="disclaimer-box">ℹ️ Integrations are currently in development. '
    "Connect your tools to unlock automatic document sync, calendar sharing, and workflow automation.</div>",
    unsafe_allow_html=True,
)

_integrations = [
    ("📧", "Email (SMTP / Outlook)", "Send documents and intake summaries directly from ProofDoc AI.", "Coming Soon"),
    ("📝", "Microsoft Word / Office 365", "Open and edit documents in Word and sync changes back.", "Coming Soon"),
    ("📁", "Google Drive", "Import documents from Google Drive and save outputs directly.", "Coming Soon"),
    ("☁️", "OneDrive / SharePoint", "Sync with your firm's Microsoft cloud document store.", "Coming Soon"),
    ("📦", "Dropbox", "Access and save documents from your Dropbox account.", "Coming Soon"),
    ("📅", "Google / Outlook Calendar", "Sync court dates and task deadlines to your calendar.", "Coming Soon"),
    ("✍️", "E-Signature (DocuSign / Adobe Sign)", "Send documents for electronic signature without leaving the app.", "Coming Soon"),
    ("⚖️", "Legal Databases (Westlaw / LexisNexis)", "Pull case law and statute references into your research.", "Coming Soon"),
    ("🔐", "Single Sign-On (SSO / SAML)", "Authenticate with your firm's existing identity provider.", "Coming Soon"),
    ("🔌", "Zapier / Make (Automation)", "Build custom automation workflows between ProofDoc AI and other apps.", "Coming Soon"),
    ("💼", "Practice Management Systems", "Sync matters, time, and billing with popular legal PMS platforms.", "Coming Soon"),
    ("📊", "Accounting (QuickBooks / Xero)", "Export invoices and financial data to your accounting software.", "Coming Soon"),
]

group_header("Available Integrations")
rows = [_integrations[i:i+3] for i in range(0, len(_integrations), 3)]
for row in rows:
    cols = st.columns(3)
    for col, (icon, name, desc, status) in zip(cols, row):
        with col:
            st.markdown(
                f'<div class="int-card">'
                f'<div class="int-icon">{icon}</div>'
                f'<h5>{name}</h5>'
                f'<p>{desc}</p>'
                f'<br><span class="badge-soon">◌ {status}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
            if st.button("Request Access", key=f"int_{name[:10]}", use_container_width=True):
                st.info(f"Request noted for **{name}**. We'll notify you when available.")
    st.markdown("<br>", unsafe_allow_html=True)

st.divider()
st.markdown("### 💡 Request a New Integration")
col1, col2 = st.columns(2)
with col1:
    req_name = st.text_input("Integration name", placeholder="e.g. Clio, NetDocuments, Sage")
    req_reason = st.text_area("Why do you need it?", height=80)
    if st.button("Submit Request", type="primary"):
        if req_name.strip():
            st.success(f"✅ Integration request for **{req_name}** submitted. Thank you!")
        else:
            st.warning("Please enter the integration name.")
