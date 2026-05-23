import streamlit as st
from utils.shared.sidebar import setup_page
from utils.shared.styles import slim_header, placeholder_feature, group_header
from utils import database as db

setup_page()
slim_header("📁", "Matters", "Manage clients, matters, leads, and engagement workflow")

tab_matters, tab_clients, tab_leads, tab_conflict, tab_engagement = st.tabs([
    "📁 Matters", "👥 Clients", "🔮 Leads", "⚖️ Conflict Check", "📜 Engagement Letters",
])

# ── MATTERS ──────────────────────────────────────────────────────────────────
with tab_matters:
    # New Matter dialog state
    if "show_new_matter" not in st.session_state:
        st.session_state.show_new_matter = False
    if "selected_matter_id" not in st.session_state:
        st.session_state.selected_matter_id = None

    col_hd, col_btn = st.columns([3, 1])
    col_hd.markdown("### Active Matters")
    if col_btn.button("＋ New Matter", type="primary", use_container_width=True):
        st.session_state.show_new_matter = True

    # New Matter form
    if st.session_state.show_new_matter:
        with st.form("new_matter_form", clear_on_submit=True):
            group_header("Create New Matter")
            f1, f2 = st.columns(2)
            m_title  = f1.text_input("Matter Title *", placeholder="e.g. Smith v Jones — Breach of Contract")
            clients  = db.list_clients(status="Active")
            client_options = {"(No client)": ""} | {c["name"]: c["id"] for c in clients}
            m_client = f2.selectbox("Client", list(client_options.keys()))
            f3, f4, f5 = st.columns(3)
            m_type   = f3.selectbox("Matter Type", [
                "Commercial", "Employment", "Property", "Family", "Criminal",
                "Immigration", "Intellectual Property", "Corporate", "Litigation", "Other",
            ])
            m_juris  = f4.selectbox("Jurisdiction", ["UK", "US", "EU", "Rwanda", "International", "Other"])
            m_lawyer = f5.text_input("Lead Lawyer", placeholder="e.g. Jane Smith")
            m_dead   = f1.text_input("Deadline (YYYY-MM-DD)", placeholder="2026-12-31")
            m_desc   = st.text_area("Description", height=80)
            s1, s2, _ = st.columns(3)
            submitted = s1.form_submit_button("💾 Save Matter", type="primary", use_container_width=True)
            if s2.form_submit_button("Cancel", use_container_width=True):
                st.session_state.show_new_matter = False
                st.rerun()
            if submitted:
                if not m_title.strip():
                    st.error("Matter title is required.")
                else:
                    matter = db.create_matter(
                        title=m_title.strip(),
                        client_id=client_options.get(m_client, ""),
                        type_=m_type,
                        jurisdiction=m_juris,
                        deadline=m_dead.strip(),
                        lead_lawyer=m_lawyer.strip(),
                        description=m_desc.strip(),
                    )
                    st.session_state.show_new_matter = False
                    st.session_state.selected_matter_id = matter["id"]
                    st.success(f"✅ Matter {matter['ref']} created.")
                    st.rerun()

    # Matter list
    matters = db.list_matters()
    if not matters:
        st.markdown(
            '<div class="empty-list" style="margin-top:1rem">'
            '📁 No matters yet.<br>'
            '<small>Click <strong>＋ New Matter</strong> to create your first matter.</small>'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        # Status filter
        f_col1, f_col2, _ = st.columns([1, 1, 2])
        status_filter  = f_col1.selectbox("Status", ["All", "Active", "Closed", "On Hold"], key="m_status")
        search_filter  = f_col2.text_input("Search", placeholder="Title or ref…", key="m_search")
        visible = [
            m for m in matters
            if (status_filter == "All" or m["status"] == status_filter)
            and (not search_filter or search_filter.lower() in m["title"].lower() or search_filter.lower() in m["ref"].lower())
        ]

        # Header row
        h = st.columns([1, 3, 1.5, 1, 1.5, 1])
        for col, lbl in zip(h, ["Ref", "Title", "Type", "Status", "Deadline", "Action"]):
            col.markdown(f"**{lbl}**")
        st.divider()

        for m in visible:
            row = st.columns([1, 3, 1.5, 1, 1.5, 1])
            row[0].text(m["ref"])
            row[1].text(m["title"])
            row[2].text(m["type"] or "—")
            status_color = {"Active": "🟢", "Closed": "🔴", "On Hold": "🟡"}.get(m["status"], "⚪")
            row[3].text(f"{status_color} {m['status']}")
            row[4].text(m["deadline"] or "—")
            if row[5].button("Open", key=f"open_{m['id']}", use_container_width=True):
                st.session_state.selected_matter_id = m["id"]
                st.rerun()

        st.caption(f"{len(visible)} of {len(matters)} matters shown")

    # Matter detail panel
    if st.session_state.selected_matter_id:
        matter = db.get_matter(st.session_state.selected_matter_id)
        if matter:
            st.markdown("---")
            st.markdown(f"### 📁 {matter['ref']} — {matter['title']}")
            d1, d2, d3, d4 = st.columns(4)
            d1.metric("Type",        matter.get("type") or "—")
            d2.metric("Status",      matter.get("status") or "—")
            d3.metric("Jurisdiction",matter.get("jurisdiction") or "—")
            d4.metric("Lead Lawyer", matter.get("lead_lawyer") or "—")

            m_tabs = st.tabs([
                "Overview", "Tasks", "Notes", "Time", "Documents",
                "AI Reviews", "Drafts", "Deadlines", "Timeline", "Evidence",
                "Billing", "Audit History",
            ])

            # Overview
            with m_tabs[0]:
                group_header("Matter Details")
                e1, e2 = st.columns(2)
                new_status  = e1.selectbox("Status", ["Active", "Closed", "On Hold"],
                                           index=["Active","Closed","On Hold"].index(matter.get("status","Active")),
                                           key="edit_status")
                new_deadline= e2.text_input("Deadline", value=matter.get("deadline") or "", key="edit_dead")
                new_desc    = st.text_area("Description", value=matter.get("description") or "", key="edit_desc")
                if st.button("💾 Save Changes", key="save_matter"):
                    db.update_matter(matter["id"], status=new_status,
                                     deadline=new_deadline, description=new_desc)
                    st.success("✅ Matter updated.")
                    st.rerun()
                col_close, col_del, _ = st.columns(3)
                if col_close.button("🗄️ Close Matter", key="close_m"):
                    db.update_matter(matter["id"], status="Closed")
                    st.session_state.selected_matter_id = None
                    st.rerun()
                if col_del.button("🗑️ Delete Matter", key="del_m"):
                    db.delete_matter(matter["id"])
                    st.session_state.selected_matter_id = None
                    st.success("Matter deleted.")
                    st.rerun()

            # Tasks
            with m_tabs[1]:
                tasks = db.list_tasks(matter_id=matter["id"])
                with st.form("new_task", clear_on_submit=True):
                    t1, t2, t3 = st.columns(3)
                    t_title    = t1.text_input("Task *")
                    t_priority = t2.selectbox("Priority", ["High", "Medium", "Low"])
                    t_due      = t3.text_input("Due (YYYY-MM-DD)")
                    t_assign   = st.text_input("Assigned to")
                    if st.form_submit_button("＋ Add Task"):
                        if t_title.strip():
                            db.create_task(matter["id"], t_title.strip(),
                                           priority=t_priority, due_date=t_due.strip(),
                                           assigned_to=t_assign.strip())
                            st.rerun()

                if not tasks:
                    st.markdown('<div class="empty-list">No tasks yet.</div>', unsafe_allow_html=True)
                else:
                    for t in tasks:
                        tc = st.columns([3, 1, 1, 1, 0.5])
                        tc[0].text(t["title"])
                        tc[1].text(t["priority"])
                        tc[2].text(t["due_date"] or "—")
                        new_s = tc[3].selectbox("", ["Pending","In Progress","Done"],
                                                index=["Pending","In Progress","Done"].index(t["status"]),
                                                key=f"ts_{t['id']}", label_visibility="collapsed")
                        if new_s != t["status"]:
                            db.update_task(t["id"], status=new_s)
                            st.rerun()
                        if tc[4].button("🗑️", key=f"del_t_{t['id']}"):
                            db.delete_task(t["id"])
                            st.rerun()

            # Notes
            with m_tabs[2]:
                with st.form("new_note", clear_on_submit=True):
                    n_body   = st.text_area("Note", height=80)
                    n_author = st.text_input("Author", placeholder="Your name")
                    if st.form_submit_button("＋ Add Note"):
                        if n_body.strip():
                            db.add_note(matter["id"], n_body.strip(), n_author.strip())
                            st.rerun()
                for note in db.list_notes(matter["id"]):
                    st.markdown(
                        f'<div class="activity-item">'
                        f'<strong>{note["author"] or "Anonymous"}</strong> · {note["created_at"][:16]}<br>{note["body"]}'
                        f'</div>',
                        unsafe_allow_html=True,
                    )

            # Time
            with m_tabs[3]:
                with st.form("new_time", clear_on_submit=True):
                    ti1, ti2, ti3 = st.columns(3)
                    ti_hours  = ti1.number_input("Hours", min_value=0.25, step=0.25, value=1.0)
                    ti_rate   = ti2.number_input("Rate (£/hr)", min_value=0.0, step=50.0, value=0.0)
                    ti_date   = ti3.text_input("Date (YYYY-MM-DD)")
                    ti_desc   = st.text_input("Description")
                    ti_lawyer = st.text_input("Lawyer")
                    if st.form_submit_button("＋ Log Time"):
                        db.add_time_entry(matter["id"], ti_hours, ti_desc.strip(),
                                          ti_rate, ti_lawyer.strip(), ti_date.strip())
                        st.rerun()
                entries = db.list_time_entries(matter["id"])
                if entries:
                    total_h   = sum(e["hours"] for e in entries)
                    total_val = sum(e["hours"] * (e["rate"] or 0) for e in entries)
                    m1, m2 = st.columns(2)
                    m1.metric("Total Hours", f"{total_h:.2f} h")
                    m2.metric("Total Value",  f"£{total_val:,.2f}")
                    st.divider()
                    for e in entries:
                        st.text(f"{e['date']}  {e['hours']:.2f}h  £{(e['rate'] or 0):.0f}/hr  {e['description'] or '—'}  {e['lawyer'] or ''}")
                else:
                    st.markdown('<div class="empty-list">No time entries yet.</div>', unsafe_allow_html=True)

            # Remaining tabs are placeholders linked to existing tools
            for tab_obj, label in zip(m_tabs[4:], [
                "Documents", "AI Reviews", "Drafts", "Deadlines",
                "Timeline", "Evidence", "Billing", "Audit History",
            ]):
                with tab_obj:
                    st.markdown(
                        f'<div class="empty-list">💡 Use the <strong>{label}</strong> section in the main sidebar to work with files linked to this matter.</div>',
                        unsafe_allow_html=True,
                    )

        if st.button("← Back to Matters list"):
            st.session_state.selected_matter_id = None
            st.rerun()

# ── CLIENTS ──────────────────────────────────────────────────────────────────
with tab_clients:
    if "show_new_client" not in st.session_state:
        st.session_state.show_new_client = False

    col_hd, col_btn = st.columns([3, 1])
    col_hd.markdown("### Clients")
    if col_btn.button("＋ Add Client", type="primary", use_container_width=True):
        st.session_state.show_new_client = True

    if st.session_state.show_new_client:
        with st.form("new_client_form", clear_on_submit=True):
            group_header("Add New Client")
            fc1, fc2 = st.columns(2)
            c_name    = fc1.text_input("Full Name *", placeholder="Jane Smith")
            c_company = fc2.text_input("Company / Firm", placeholder="Smith & Co Ltd")
            fc3, fc4, fc5 = st.columns(3)
            c_email   = fc3.text_input("Email", placeholder="jane@example.com")
            c_phone   = fc4.text_input("Phone", placeholder="+44 7700 900000")
            c_type    = fc5.selectbox("Client Type", ["Individual", "Company", "Government", "NGO", "Other"])
            c_notes   = st.text_area("Notes", height=60)
            fs1, fs2, _ = st.columns(3)
            if fs1.form_submit_button("💾 Save Client", type="primary", use_container_width=True):
                if not c_name.strip():
                    st.error("Client name is required.")
                else:
                    db.create_client(c_name.strip(), c_email.strip(), c_phone.strip(),
                                     c_company.strip(), c_type, c_notes.strip())
                    st.session_state.show_new_client = False
                    st.success(f"✅ Client '{c_name}' added.")
                    st.rerun()
            if fs2.form_submit_button("Cancel", use_container_width=True):
                st.session_state.show_new_client = False
                st.rerun()

    clients = db.list_clients()
    if not clients:
        st.markdown(
            '<div class="empty-list" style="margin-top:1rem">'
            '👥 No clients yet.<br>'
            '<small>Click <strong>＋ Add Client</strong> to add your first client.</small>'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        ch = st.columns([2.5, 2, 1.5, 1, 0.8])
        for col, lbl in zip(ch, ["Name", "Company", "Email", "Type", "Status"]):
            col.markdown(f"**{lbl}**")
        st.divider()
        for c in clients:
            cr = st.columns([2.5, 2, 1.5, 1, 0.8])
            cr[0].text(c["name"])
            cr[1].text(c["company"] or "—")
            cr[2].text(c["email"] or "—")
            cr[3].text(c["type"] or "—")
            badge = "🟢" if c["status"] == "Active" else "🔴"
            cr[4].text(badge)
        st.caption(f"{len(clients)} clients")

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
    group_header("Conflict Check")
    st.markdown("Check a new party name against all existing clients and matters.")
    search_party = st.text_input("Party name to screen", placeholder="e.g. Acme Corp or John Smith")
    if st.button("🔍 Run Conflict Check", disabled=not search_party.strip()):
        name_lower = search_party.strip().lower()
        all_clients = db.list_clients()
        all_matters = db.list_matters()
        client_hits = [c for c in all_clients if name_lower in c["name"].lower() or name_lower in (c.get("company") or "").lower()]
        matter_hits = [m for m in all_matters if name_lower in m["title"].lower()]
        if client_hits or matter_hits:
            st.warning(f"⚠️ Potential conflict found for **'{search_party}'**.")
            if client_hits:
                st.markdown("**Matching clients:**")
                for c in client_hits:
                    st.markdown(f"- {c['name']} ({c.get('company') or 'Individual'}) — Status: {c['status']}")
            if matter_hits:
                st.markdown("**Matching matters:**")
                for m in matter_hits:
                    st.markdown(f"- {m['ref']}: {m['title']} — {m['status']}")
        else:
            st.success(f"✅ No conflicts found for **'{search_party}'** in current client or matter database.")

    st.markdown("<br>", unsafe_allow_html=True)
    placeholder_feature(
        "⚖️", "Full Conflict Screening",
        "Advanced conflict engine: screen against all related parties, opposing counsel, and historical matters.",
        ["Screen against parties, directors, and related entities",
         "Compare against historical (closed) matters",
         "Flag potential conflicts with confidence score",
         "Generate conflict-clear certificate"],
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
