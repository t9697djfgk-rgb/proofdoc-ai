import streamlit as st
from utils.shared.sidebar import setup_page
from utils.shared.styles import slim_header, group_header, placeholder_feature

setup_page()
slim_header("🛡️", "Compliance Tools", "Redaction, privilege, confidentiality, ethical walls, and data protection")

st.markdown(
    '<div class="notice-box">🔐 All compliance tools process data in memory only. '
    "No content is stored, logged externally, or used for AI training.</div>",
    unsafe_allow_html=True,
)

tab_protect, tab_ethics, tab_security = st.tabs([
    "🔐 Data Protection", "⚖️ Ethics & Privilege", "🔒 Security Controls",
])

with tab_protect:
    group_header("Document Protection Tools")
    c1, c2 = st.columns(2)
    with c1:
        placeholder_feature(
            "✂️", "Redaction Helper",
            "Automatically identify and redact sensitive information before disclosure.",
            ["Upload document to scan for sensitive data",
             "AI identifies names, dates, account numbers, legal privilege markers",
             "Review and confirm each proposed redaction",
             "Download redacted PDF with black boxes"],
            ["Redacted PDF", "Redaction log (what was redacted and why)",
             "Unredacted archive copy (access-controlled)"],
        )
    with c2:
        placeholder_feature(
            "🔔", "Confidentiality Notice Generator",
            "Automatically add jurisdiction-appropriate confidentiality notices to documents.",
            ["Select jurisdiction and document type",
             "AI generates appropriate notice text",
             "Append to document header or footer",
             "Save custom firm templates"],
            ["Document with embedded notice", "Notice text variants per jurisdiction",
             "Firm template library"],
        )

    st.markdown("<br>", unsafe_allow_html=True)
    placeholder_feature(
        "🗄️", "Data Retention Manager",
        "Apply retention policies to matters and documents in line with regulatory requirements.",
        ["Set retention period per matter type or jurisdiction",
         "Flag documents approaching retention expiry",
         "Archive or delete documents on policy schedule",
         "Generate data retention compliance report"],
        ["Retention policy schedule", "Documents-approaching-expiry list",
         "Deletion/archive log", "Compliance report"],
    )

with tab_ethics:
    group_header("Professional Ethics & Privilege")
    c1, c2 = st.columns(2)
    with c1:
        placeholder_feature(
            "⚠️", "Privilege Warning System",
            "Flag potentially privileged documents before disclosure or sharing.",
            ["Scan documents for privilege markers",
             "Flag items meeting legal professional privilege tests",
             "Require senior approval before disclosure of flagged items",
             "Log privilege review decisions"],
            ["Privilege flag report", "Approval workflow log",
             "Disclosure schedule with privilege status column"],
        )
    with c2:
        placeholder_feature(
            "🧱", "Ethical Walls",
            "Create information barriers between teams working on conflicting matters.",
            ["Define which lawyers are walled off from which matters",
             "Enforce document and system access restrictions",
             "Log all access attempts to walled matters",
             "Generate ethical wall certificate"],
            ["Ethical wall configuration", "Access restriction enforcement",
             "Wall breach alert log", "Ethical wall certificate"],
        )

    st.markdown("<br>", unsafe_allow_html=True)
    placeholder_feature(
        "🔍", "Conflict of Interest Monitor",
        "Monitor for new conflicts as matters evolve and new parties are added.",
        ["Continuous conflict screening as parties are added to matters",
         "Alert responsible lawyer when new conflict detected",
         "Maintain conflict waiver log",
         "Generate conflict-clear certificates"],
        ["Ongoing conflict alert system", "Conflict waiver register",
         "Clear certificate per matter"],
    )

with tab_security:
    group_header("Security & Permissions")
    c1, c2 = st.columns(2)
    with c1:
        placeholder_feature(
            "👥", "User Permissions",
            "Control who can access which sections, matters, and documents.",
            ["Assign roles (partner, associate, paralegal, admin, client)",
             "Set matter-level access permissions",
             "Restrict access to sensitive matters",
             "Review and audit permission changes"],
            ["Permission matrix per user and matter",
             "Access change audit log", "Permission report"],
        )
    with c2:
        placeholder_feature(
            "🔍", "Security Review",
            "Periodic security review of platform usage, access patterns, and risk indicators.",
            ["Review failed login attempts and unusual access patterns",
             "Identify high-risk document access",
             "Generate security review report for IT / management"],
            ["Security review summary", "Risk indicators dashboard",
             "Recommended actions list"],
        )
