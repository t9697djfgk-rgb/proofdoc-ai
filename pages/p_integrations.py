import streamlit as st
from utils.shared.sidebar import setup_page
from utils.shared.styles import slim_header, section

from utils.auth import require_lawyer
api_key = setup_page()
require_lawyer()
slim_header("🔗", "Integrations", "Connect eLawFirm to your existing tools and platforms")

if "connected_integrations" not in st.session_state:
    st.session_state.connected_integrations = set()
if "int_requests" not in st.session_state:
    st.session_state.int_requests = []

INTEGRATIONS = [
    {
        "icon": "📧", "name": "Email (SMTP / Outlook)",
        "desc": "Send documents, intake summaries, and signature requests directly from eLawFirm.",
        "category": "Communication",
        "status": "beta",
        "features": ["Send documents to clients", "Automated matter notifications", "Signature request emails"],
    },
    {
        "icon": "📅", "name": "Google / Outlook Calendar",
        "desc": "Sync court dates, deadlines, and task due dates to your personal calendar.",
        "category": "Productivity",
        "status": "beta",
        "features": ["Auto-sync court deadlines", "Task reminders", "Matter hearing dates"],
    },
    {
        "icon": "📁", "name": "Google Drive",
        "desc": "Import documents from Google Drive and save AI outputs and drafts directly.",
        "category": "Storage",
        "status": "coming_soon",
        "features": ["Import from Drive", "Auto-save drafts", "Folder per matter"],
    },
    {
        "icon": "☁️", "name": "OneDrive / SharePoint",
        "desc": "Sync with your firm's Microsoft cloud document store and Teams channels.",
        "category": "Storage",
        "status": "coming_soon",
        "features": ["Sync firm documents", "Teams notifications", "SharePoint libraries"],
    },
    {
        "icon": "📦", "name": "Dropbox",
        "desc": "Access and save documents from your Dropbox account seamlessly.",
        "category": "Storage",
        "status": "coming_soon",
        "features": ["Import from Dropbox", "Auto-save outputs", "Shared folder support"],
    },
    {
        "icon": "✍️", "name": "DocuSign",
        "desc": "Send documents for legally binding electronic signature without leaving eLawFirm.",
        "category": "E-Signature",
        "status": "coming_soon",
        "features": ["In-app signing workflow", "Real-time status tracking", "Signed PDF download"],
    },
    {
        "icon": "✒️", "name": "Adobe Sign",
        "desc": "Send and track e-signature requests via Adobe Sign integration.",
        "category": "E-Signature",
        "status": "coming_soon",
        "features": ["Adobe Sign workflow", "Multi-signatory support", "Audit certificate"],
    },
    {
        "icon": "📝", "name": "Microsoft Word / Office 365",
        "desc": "Open, edit, and sync Word documents directly without manual upload/download.",
        "category": "Productivity",
        "status": "coming_soon",
        "features": ["Open in Word", "Track changes sync", "Co-author support"],
    },
    {
        "icon": "⚖️", "name": "Westlaw / LexisNexis",
        "desc": "Pull verified case law and statute references into your research and documents.",
        "category": "Legal Research",
        "status": "coming_soon",
        "features": ["Live case law search", "Statute citations", "Headnote summaries"],
    },
    {
        "icon": "📊", "name": "QuickBooks / Xero",
        "desc": "Export invoices, time entries, and financial data to your accounting software.",
        "category": "Finance",
        "status": "coming_soon",
        "features": ["Invoice export", "Time entry sync", "Client billing reports"],
    },
    {
        "icon": "🔌", "name": "Zapier / Make",
        "desc": "Build custom automation workflows connecting eLawFirm to 5,000+ apps.",
        "category": "Automation",
        "status": "coming_soon",
        "features": ["Custom triggers", "Automated workflows", "No-code setup"],
    },
    {
        "icon": "🔐", "name": "Single Sign-On (SSO / SAML)",
        "desc": "Authenticate with your firm's identity provider — Azure AD, Okta, Google Workspace.",
        "category": "Security",
        "status": "coming_soon",
        "features": ["SAML 2.0 support", "SCIM provisioning", "MFA enforcement"],
    },
]

STATUS_CFG = {
    "connected":   ("#16a34a", "#f0fdf4", "● Connected"),
    "beta":        ("#0891b2", "#ecfeff", "◎ Available"),
    "coming_soon": ("#94a3b8", "#f1f5f9", "◌ Coming Soon"),
}

CATEGORIES = sorted({i["category"] for i in INTEGRATIONS})

tab_all, tab_connected, tab_request = st.tabs([
    "🔗 All Integrations", "✅ Connected", "💡 Request Integration"
])

with tab_all:
    # Stats banner
    connected_count = len(st.session_state.connected_integrations)
    available_count = sum(1 for i in INTEGRATIONS if i["status"] == "beta")
    st.markdown(
        f"""<div style="display:flex;gap:1rem;margin-bottom:1.2rem;flex-wrap:wrap">
          <div style="flex:1;min-width:120px;background:#f0f4ff;border-radius:10px;padding:.8rem 1rem;
                      border-left:4px solid #1a2744;text-align:center">
            <div style="font-size:1.4rem;font-weight:700;color:#1a2744">{len(INTEGRATIONS)}</div>
            <div style="font-size:.72rem;color:#64748b;text-transform:uppercase;letter-spacing:.05em">Total</div>
          </div>
          <div style="flex:1;min-width:120px;background:#f0fdf4;border-radius:10px;padding:.8rem 1rem;
                      border-left:4px solid #16a34a;text-align:center">
            <div style="font-size:1.4rem;font-weight:700;color:#15803d">{connected_count}</div>
            <div style="font-size:.72rem;color:#64748b;text-transform:uppercase;letter-spacing:.05em">Connected</div>
          </div>
          <div style="flex:1;min-width:120px;background:#ecfeff;border-radius:10px;padding:.8rem 1rem;
                      border-left:4px solid #0891b2;text-align:center">
            <div style="font-size:1.4rem;font-weight:700;color:#0e7490">{available_count}</div>
            <div style="font-size:.72rem;color:#64748b;text-transform:uppercase;letter-spacing:.05em">Available Now</div>
          </div>
          <div style="flex:1;min-width:120px;background:#f1f5f9;border-radius:10px;padding:.8rem 1rem;
                      border-left:4px solid #94a3b8;text-align:center">
            <div style="font-size:1.4rem;font-weight:700;color:#475569">{len(INTEGRATIONS)-available_count}</div>
            <div style="font-size:.72rem;color:#64748b;text-transform:uppercase;letter-spacing:.05em">Coming Soon</div>
          </div>
        </div>""",
        unsafe_allow_html=True,
    )

    cat_filter = st.selectbox("Filter by category", ["All categories"] + CATEGORIES, key="int_cat")

    shown = INTEGRATIONS if cat_filter == "All categories" else [
        i for i in INTEGRATIONS if i["category"] == cat_filter
    ]

    # Group by category for display
    groups: dict[str, list] = {}
    for intg in shown:
        groups.setdefault(intg["category"], []).append(intg)

    for cat, items in groups.items():
        section(f"{'📧' if cat == 'Communication' else '📁' if cat == 'Storage' else '⚖️' if cat == 'Legal Research' else '📅' if cat == 'Productivity' else '✍️' if cat == 'E-Signature' else '💰' if cat == 'Finance' else '🔌' if cat == 'Automation' else '🔐'} {cat}")

        cols = st.columns(2)
        for idx, intg in enumerate(items):
            is_connected = intg["name"] in st.session_state.connected_integrations
            effective_status = "connected" if is_connected else intg["status"]
            fg, bg, badge = STATUS_CFG[effective_status]
            features_html = "".join(f"<li style='font-size:.78rem;color:#475569;margin:.1rem 0'>{f}</li>" for f in intg["features"])

            with cols[idx % 2]:
                st.markdown(
                    f"""<div style="background:white;border:1px solid #e2e8f0;border-radius:12px;
                                  padding:1.1rem 1.2rem;margin-bottom:.8rem;border-top:3px solid {fg}">
                      <div style="display:flex;align-items:flex-start;gap:.8rem;margin-bottom:.6rem">
                        <span style="font-size:1.6rem;flex-shrink:0">{intg['icon']}</span>
                        <div style="flex:1;min-width:0">
                          <div style="font-weight:700;color:#1a2744;font-size:.92rem">{intg['name']}</div>
                          <span style="font-size:.68rem;font-weight:700;color:{fg};background:{bg};
                                       padding:.15rem .5rem;border-radius:20px;border:1px solid {fg}40">{badge}</span>
                        </div>
                      </div>
                      <p style="font-size:.82rem;color:#475569;margin:.4rem 0 .6rem">{intg['desc']}</p>
                      <ul style="margin:0;padding-left:1.1rem">{features_html}</ul>
                    </div>""",
                    unsafe_allow_html=True,
                )
                btn_label = "⚙️ Configure" if is_connected else ("🔌 Connect" if effective_status == "beta" else "🔔 Notify Me")
                if st.button(btn_label, key=f"int_btn_{intg['name'][:15]}", use_container_width=True):
                    if effective_status == "beta":
                        if is_connected:
                            st.session_state.connected_integrations.discard(intg["name"])
                            st.success(f"🔌 **{intg['name']}** disconnected.")
                        else:
                            st.session_state.connected_integrations.add(intg["name"])
                            st.success(f"✅ **{intg['name']}** connected! Configuration options will appear here.")
                        st.rerun()
                    else:
                        st.info(f"🔔 You'll be notified when **{intg['name']}** is available.")

        st.markdown("<br>", unsafe_allow_html=True)

with tab_connected:
    connected = [i for i in INTEGRATIONS if i["name"] in st.session_state.connected_integrations]
    if connected:
        section(f"✅ {len(connected)} Active Connection{'s' if len(connected) != 1 else ''}")
        for intg in connected:
            st.markdown(
                f"""<div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;
                              padding:.9rem 1.1rem;margin-bottom:.5rem;
                              display:flex;align-items:center;gap:1rem">
                  <span style="font-size:1.4rem">{intg['icon']}</span>
                  <div style="flex:1">
                    <div style="font-weight:700;color:#1a2744">{intg['name']}</div>
                    <div style="font-size:.78rem;color:#16a34a">● Active</div>
                  </div>
                  <span style="font-size:.75rem;background:#dcfce7;color:#15803d;padding:.2rem .7rem;
                               border-radius:20px;border:1px solid #86efac">{intg['category']}</span>
                </div>""",
                unsafe_allow_html=True,
            )
            if st.button(f"Disconnect {intg['name']}", key=f"disc_{intg['name'][:15]}"):
                st.session_state.connected_integrations.discard(intg["name"])
                st.rerun()
    else:
        st.markdown(
            '<div style="text-align:center;color:#94a3b8;padding:3rem">'
            '🔗 No integrations connected yet.<br>'
            '<small>Go to All Integrations and click Connect on an available integration.</small>'
            '</div>',
            unsafe_allow_html=True,
        )

with tab_request:
    section("💡 Request an Integration")
    st.markdown("Don't see the tool you use? Let us know — we prioritise integrations based on demand.")
    st.markdown("<br>", unsafe_allow_html=True)

    with st.form("int_request_form", clear_on_submit=True):
        c1, c2 = st.columns(2)
        req_name = c1.text_input("Integration / Tool Name *", placeholder="e.g. Clio, NetDocuments, Sage, PracticePanther")
        req_cat  = c2.selectbox("Category", CATEGORIES + ["Other"])
        req_use  = st.text_area("How would you use it? *", height=80,
                                 placeholder="Describe the workflow — what would you import/export, how often, for what tasks?")
        req_priority = st.radio("Priority for your firm", ["Nice to have", "Would save significant time", "Blocking — we need this now"], horizontal=True)
        if st.form_submit_button("📨 Submit Request", type="primary"):
            if req_name.strip() and req_use.strip():
                st.session_state.int_requests.append({
                    "name": req_name.strip(), "category": req_cat,
                    "use_case": req_use.strip(), "priority": req_priority,
                })
                st.success(f"✅ Request for **{req_name}** submitted — thank you! We'll prioritise based on demand.")
            else:
                st.warning("Please fill in the tool name and use case.")

    if st.session_state.int_requests:
        st.markdown("<br>", unsafe_allow_html=True)
        section(f"📋 Your Requests ({len(st.session_state.int_requests)})")
        for req in st.session_state.int_requests:
            priority_color = {"Blocking — we need this now": "#dc2626",
                              "Would save significant time": "#d97706",
                              "Nice to have": "#64748b"}.get(req["priority"], "#64748b")
            st.markdown(
                f"""<div style="background:#f8fafc;border-radius:8px;padding:.7rem 1rem;
                              margin-bottom:.35rem;border-left:3px solid {priority_color}">
                  <div style="font-weight:700;color:#1a2744">{req['name']}
                    <span style="font-size:.72rem;color:#64748b;font-weight:400;margin-left:.5rem">{req['category']}</span>
                  </div>
                  <div style="font-size:.8rem;color:#475569;margin-top:.2rem">{req['use_case'][:120]}{"…" if len(req['use_case']) > 120 else ""}</div>
                  <div style="font-size:.72rem;color:{priority_color};margin-top:.2rem">{req['priority']}</div>
                </div>""",
                unsafe_allow_html=True,
            )
