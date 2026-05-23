import streamlit as st
from utils.shared.sidebar import setup_page
from utils.shared.styles import slim_header, section, risk_badge
from utils.auth import require_auth
import utils.database as db

setup_page()
user = require_auth()
if user["role"] != "client":
    st.switch_page("pages/p_lawyer_dashboard.py")

slim_header("🏢", f"Welcome, {user['full_name'].split()[0]}", "Your secure client portal")

tab_home, tab_matters, tab_docs, tab_disc, tab_invoices, tab_profile = st.tabs([
    "🏠 Dashboard", "📁 My Matters", "📄 My Documents",
    "💬 Discussions", "🧾 Invoices", "👤 Profile",
])

# ── Dashboard ─────────────────────────────────────────────────────
with tab_home:
    matters   = db.list_matters()
    notifs    = db.list_notifications(limit=5)
    unread    = db.unread_notification_count()

    m1, m2, m3 = st.columns(3)
    m1.metric("My Matters",       len(matters))
    m2.metric("Unread Messages",  unread)
    m3.metric("Active Matters",   sum(1 for m in matters if m.get("status") == "Active"))

    st.markdown("<br>", unsafe_allow_html=True)
    c_left, c_right = st.columns(2, gap="large")

    with c_left:
        section("📁 My Matters")
        if matters:
            for m in matters:
                status = m.get("status", "")
                color = {"Active": "#16a34a", "On Hold": "#d97706"}.get(status, "#64748b")
                st.markdown(
                    f"**{m.get('ref','')}** — {m.get('title','')[:45]}<br>"
                    f"<small style='color:{color}'>{status}</small>",
                    unsafe_allow_html=True,
                )
                st.divider()
        else:
            st.caption("No matters assigned yet.")

    with c_right:
        section("🔔 Recent Notifications")
        if notifs:
            for n in notifs:
                icon = "🔵" if not n.get("is_read") else "⚪"
                st.markdown(f"{icon} **{n['title']}**")
                if n.get("body"):
                    st.caption(n["body"])
                st.caption(str(n.get("created_at", ""))[:16].replace("T", " "))
        else:
            st.caption("No notifications yet.")

# ── My Matters ────────────────────────────────────────────────────
with tab_matters:
    matters = db.list_matters()
    if not matters:
        st.info("No matters have been assigned to you yet. Your lawyer will add you to your matters.")
    else:
        for m in matters:
            with st.expander(f"📁 {m.get('ref','')} — {m.get('title','')}"):
                c1, c2, c3 = st.columns(3)
                c1.metric("Status",       m.get("status", "—"))
                c2.metric("Jurisdiction", m.get("jurisdiction", "—"))
                c3.metric("Open Date",    str(m.get("open_date", "—"))[:10])
                if m.get("description"):
                    st.markdown(f"**Description:** {m['description']}")
                if m.get("court_reference"):
                    st.markdown(f"**Court Ref:** {m['court_reference']}")

                # Assigned lawyer
                members = db.get_matter_members(m["id"])
                lawyers = [mem for mem in members if mem.get("role") in ("lead_lawyer", "lawyer")]
                if lawyers:
                    names = ", ".join(
                        mem.get("profiles", {}).get("full_name", "—")
                        for mem in lawyers
                    )
                    st.markdown(f"**Your Lawyer:** {names}")

                # Tasks visible to client
                tasks = [t for t in db.list_tasks(matter_id=m["id"])
                         if t.get("status") != "completed"]
                if tasks:
                    st.markdown(f"**Upcoming steps ({len(tasks)}):**")
                    for t in tasks[:5]:
                        due = str(t.get("due_date", ""))[:10]
                        st.markdown(f"- {t.get('title','')} {'· due ' + due if due else ''}")

# ── My Documents ─────────────────────────────────────────────────
with tab_docs:
    section("📄 Documents Shared With You")
    all_docs = db.list_documents()
    if not all_docs:
        st.info("No documents have been shared with you yet.")
    else:
        col_filter = st.selectbox("Filter by matter", ["All matters"] +
                                   list({d.get("matter_id", "General") for d in all_docs}),
                                   key="cdoc_filter")
        shown = all_docs if col_filter == "All matters" else [d for d in all_docs if d.get("matter_id") == col_filter]

        for d in shown:
            c1, c2, c3 = st.columns([4, 2, 1])
            vis_icon = {"shared_with_client": "🟢", "final": "🏁",
                        "client_upload": "📤", "draft": "📝"}.get(d.get("visibility",""), "📄")
            c1.markdown(f"{vis_icon} **{d['name']}**")
            c2.caption(d.get("visibility", "").replace("_", " ").title())
            c3.caption(str(d.get("created_at", ""))[:10])
            st.markdown("---")

    st.markdown("<br>", unsafe_allow_html=True)
    section("📤 Upload a Document")
    matters_mine = db.list_matters()
    matter_opts  = {f"{m['ref']}: {m['title'][:35]}": m["id"] for m in matters_mine}
    if matter_opts:
        sel_matter = st.selectbox("Select matter", list(matter_opts.keys()), key="cup_matter")
        up_file    = st.file_uploader("Choose file", key="cup_file")
        up_desc    = st.text_input("Description (optional)", key="cup_desc")
        if st.button("📤 Upload", type="primary", key="cup_btn") and up_file:
            doc = db.add_document(
                name=up_file.name,
                matter_id=matter_opts[sel_matter],
                file_type=up_file.type,
                file_size=up_file.size,
                visibility="client_upload",
                description=up_desc.strip(),
            )
            db.notify_matter_members(
                matter_opts[sel_matter], "document_uploaded",
                f"Client uploaded: {up_file.name}",
                body=f"Uploaded by {user['full_name']}",
                exclude_id=user["id"], lawyers_only=True,
            )
            st.success(f"✅ {up_file.name} uploaded.")
            st.rerun()
    else:
        st.info("You must be assigned to a matter before uploading documents.")

# ── Discussions ───────────────────────────────────────────────────
with tab_disc:
    matters_mine = db.list_matters()
    if not matters_mine:
        st.info("No matters assigned yet.")
    else:
        matter_opts = {f"{m['ref']}: {m['title'][:40]}": m["id"] for m in matters_mine}
        sel = st.selectbox("Select matter to view discussion", list(matter_opts.keys()), key="cdisc_sel")
        mid = matter_opts[sel]
        db.mark_messages_read(mid)
        messages = db.list_messages(mid)

        st.markdown("<br>", unsafe_allow_html=True)
        if messages:
            for msg in messages:
                sender = (msg.get("profiles") or {}).get("full_name", "Unknown")
                is_mine = msg.get("sender_id") == user["id"]
                align = "right" if is_mine else "left"
                bg    = "#dbeafe" if is_mine else "#f1f5f9"
                ts    = str(msg.get("created_at",""))[:16].replace("T"," ")
                st.markdown(
                    f"""<div style='text-align:{align};margin:.4rem 0'>
                    <div style='display:inline-block;background:{bg};padding:.6rem 1rem;
                    border-radius:12px;max-width:75%;text-align:left'>
                    <small style='color:#64748b'><b>{sender}</b> · {ts}</small><br>
                    {msg.get('body','')}
                    </div></div>""",
                    unsafe_allow_html=True,
                )
                for att in (msg.get("message_attachments") or []):
                    st.markdown(f"📎 {att.get('file_name','')}")
        else:
            st.info("No messages yet. Start the conversation below.")

        st.markdown("<br>", unsafe_allow_html=True)
        with st.form("client_msg_form", clear_on_submit=True):
            body = st.text_area("Your message", height=80, placeholder="Type your message…", key="cmsg_body")
            att  = st.file_uploader("Attach a file (optional)", key="cmsg_att")
            sent = st.form_submit_button("Send Message ➤", type="primary")
        if sent:
            if not body.strip():
                st.warning("Message cannot be empty.")
            else:
                msg = db.send_message(mid, body.strip(), "client_visible")
                if att and msg:
                    doc = db.add_document(att.name, mid, file_type=att.type, file_size=att.size,
                                           visibility="client_upload")
                    if doc:
                        db.add_message_attachment(msg["id"], att.name, doc.get("file_path",""),
                                                   att.type, att.size, doc.get("id"))
                db.notify_matter_members(mid, "new_message",
                    f"New message from {user['full_name']}",
                    body=body[:100], exclude_id=user["id"], lawyers_only=True)
                st.rerun()

# ── Invoices ──────────────────────────────────────────────────────
with tab_invoices:
    section("🧾 My Invoices")
    org = user.get("organization_id")
    if org:
        invoices_resp = (
            db.get_db().table("invoices")
            .select("*, matters(ref,title)")
            .eq("organization_id", org)
            .order("created_at", desc=True)
            .execute()
        )
        invoices = invoices_resp.data or []
        if invoices:
            for inv in invoices:
                matter_label = ""
                if inv.get("matters"):
                    matter_label = f" · {inv['matters'].get('ref','')} {inv['matters'].get('title','')[:30]}"
                status_color = {
                    "paid": "#16a34a", "sent": "#2563eb",
                    "overdue": "#dc2626", "draft": "#64748b",
                }.get(inv.get("status",""), "#64748b")
                c1, c2, c3, c4 = st.columns([2, 2, 2, 1])
                c1.markdown(f"**{inv.get('invoice_number','')}**{matter_label}")
                c2.markdown(f"£{inv.get('total', 0):,.2f}")
                c3.caption(str(inv.get("due_date",""))[:10])
                c4.markdown(f"<span style='color:{status_color}'>{inv.get('status','').title()}</span>",
                            unsafe_allow_html=True)
                st.divider()
        else:
            st.info("No invoices yet.")
    else:
        st.info("No invoices yet.")

# ── Profile ───────────────────────────────────────────────────────
with tab_profile:
    section("👤 My Profile")
    profile = db.get_profile(user["id"]) or {}
    c1, c2 = st.columns(2)
    c1.markdown(f"**Name:** {profile.get('full_name','')}")
    c1.markdown(f"**Email:** {profile.get('email','')}")
    c2.markdown(f"**Role:** {profile.get('role','').title()}")
    c2.markdown(f"**Firm:** {user['organization_name']}")

    st.markdown("<br>", unsafe_allow_html=True)
    section("🔑 Change Password")
    with st.form("cp_form"):
        new_pw  = st.text_input("New Password", type="password", key="cp_pw")
        new_pw2 = st.text_input("Confirm New Password", type="password", key="cp_pw2")
        if st.form_submit_button("Update Password"):
            if len(new_pw) < 8:
                st.warning("Password must be at least 8 characters.")
            elif new_pw != new_pw2:
                st.warning("Passwords do not match.")
            else:
                from utils.auth import reset_password
                result = reset_password(user["id"], new_pw)
                if result["ok"]:
                    st.success("✅ Password updated.")
                else:
                    st.error(result["error"])
