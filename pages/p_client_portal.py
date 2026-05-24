import streamlit as st
from utils.shared.sidebar import setup_page
from utils.shared.styles import slim_header, inject_css, section
from utils.auth import require_auth
import utils.database as db
from datetime import date

setup_page()
user = require_auth()
if user["role"] != "client":
    st.switch_page("pages/p_lawyer_dashboard.py")

inject_css()

first_name = user["full_name"].split()[0]
slim_header("🏢", f"Welcome, {first_name}", f"{user['organization_name']} · Client Portal")

tab_home, tab_matters, tab_docs, tab_disc, tab_billing, tab_profile = st.tabs([
    "🏠 Overview", "📁 My Matters", "📄 Documents", "💬 Discussions", "💼 Billing", "👤 Profile",
])

# ══════════════════════════════════════════════════════════════════
# TAB 1 – OVERVIEW
# ══════════════════════════════════════════════════════════════════
with tab_home:
    matters   = db.list_matters()
    notifs    = db.list_notifications(limit=6)
    unread_n  = sum(1 for n in notifs if not n.get("is_read"))
    active_m  = sum(1 for m in matters if m.get("status") == "Active")
    all_docs  = db.list_documents()

    # KPI cards
    c1, c2, c3 = st.columns(3)
    for col, icon, label, value, color, bg in [
        (c1, "📁", "My Matters",     len(matters),  "#1a2744", "#e8f0fe"),
        (c2, "⚡", "Active Matters", active_m,      "#059669", "#ecfdf5"),
        (c3, "🔔", "Notifications",  unread_n,       "#d97706", "#fffbeb"),
    ]:
        col.markdown(
            f"""<div style="background:{bg};border-radius:12px;padding:1rem 1.1rem;
                            border-left:4px solid {color}">
              <p style="margin:0;font-size:0.72rem;font-weight:600;color:#6b7280;
                        text-transform:uppercase">{icon} {label}</p>
              <p style="margin:0.2rem 0 0;font-size:1.8rem;font-weight:700;color:{color}">{value}</p>
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    left, right = st.columns([3, 2], gap="large")

    with left:
        section("📁 My Matters")
        STATUS_CFG = {
            "Active":   ("#16a34a", "#dcfce7"),
            "On Hold":  ("#d97706", "#fef9c3"),
            "Closed":   ("#64748b", "#f1f5f9"),
        }
        if matters:
            for m in matters:
                status = m.get("status", "Active")
                fg, bg = STATUS_CFG.get(status, ("#64748b", "#f1f5f9"))
                st.markdown(
                    f"""<div style="background:#fff;border-radius:9px;padding:0.75rem 1rem;
                                    margin-bottom:0.4rem;border:1px solid rgba(0,0,0,0.07);
                                    border-left:4px solid {fg}">
                      <div style="display:flex;align-items:center;gap:0.5rem">
                        <span style="font-weight:700;color:#1a2744;font-size:0.88rem">
                          {m.get('ref','')}</span>
                        <span style="font-size:0.85rem;color:#374151">{m.get('title','')[:45]}</span>
                        <span style="margin-left:auto;background:{bg};color:{fg};font-size:0.7rem;
                                     font-weight:600;padding:0.15rem 0.45rem;border-radius:20px">
                          {status}</span>
                      </div>
                      {'<p style="margin:0.2rem 0 0;font-size:0.75rem;color:#9ca3af">'+m.get('matter_type','')+'</p>' if m.get('matter_type') else ''}
                    </div>""",
                    unsafe_allow_html=True,
                )
        else:
            st.caption("No matters assigned yet. Your lawyer will add you shortly.")

    with right:
        section("🔔 Notifications")
        if notifs:
            for n in notifs:
                is_read = n.get("is_read", False)
                bg  = "#fff" if is_read else "#fdf6e3"
                dot = "⚪" if is_read else "🟡"
                ts  = str(n.get("created_at",""))[:16].replace("T"," ")
                st.markdown(
                    f"""<div style="background:{bg};border-radius:8px;padding:0.6rem 0.85rem;
                                    margin-bottom:0.3rem;border:1px solid {'rgba(0,0,0,0.07)' if is_read else '#c9a84c'}">
                      <div style="display:flex;gap:0.5rem;align-items:flex-start">
                        <span style="font-size:0.65rem;margin-top:0.15rem">{dot}</span>
                        <div>
                          <p style="margin:0;font-size:0.82rem;font-weight:{'400' if is_read else '600'};
                                    color:#1a1a2e">{n.get('title','')}</p>
                          {'<p style="margin:0.1rem 0 0;font-size:0.73rem;color:#6b7280">'+n.get('body','')+'</p>' if n.get('body') else ''}
                          <p style="margin:0.15rem 0 0;font-size:0.68rem;color:#9ca3af">{ts}</p>
                        </div>
                      </div>
                    </div>""",
                    unsafe_allow_html=True,
                )
            if unread_n:
                if st.button("Mark all read", key="cp_mark_read", use_container_width=True):
                    db.mark_notifications_read()
                    st.rerun()
        else:
            st.caption("No notifications yet.")

# ══════════════════════════════════════════════════════════════════
# TAB 2 – MY MATTERS
# ══════════════════════════════════════════════════════════════════
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
                c3.metric("Open Date",    str(m.get("open_date", "—") or "—")[:10])

                if m.get("description"):
                    st.markdown(
                        f'<div style="background:#f8fafc;border-radius:8px;padding:0.75rem;'
                        f'margin:0.5rem 0;font-size:0.85rem;color:#374151">'
                        f'{m["description"]}</div>',
                        unsafe_allow_html=True,
                    )

                members = db.get_matter_members(m["id"])
                lawyers = [mem for mem in members if mem.get("role") in ("lead_lawyer", "lawyer")]
                if lawyers:
                    names = ", ".join(
                        (mem.get("profiles") or {}).get("full_name", "—") for mem in lawyers
                    )
                    st.markdown(
                        f'<p style="font-size:0.83rem;color:#1a2744"><b>Your Lawyer:</b> {names}</p>',
                        unsafe_allow_html=True,
                    )

                tasks = [t for t in db.list_tasks(matter_id=m["id"])
                         if t.get("status") not in ("completed", "cancelled")]
                if tasks:
                    st.markdown(f"**Upcoming steps ({len(tasks)}):**")
                    for t in tasks[:6]:
                        due = str(t.get("due_date",""))[:10]
                        pri = (t.get("priority") or "").lower()
                        icon = {"high":"🔴","medium":"🟡","low":"🟢"}.get(pri,"📌")
                        st.markdown(
                            f'<div style="font-size:0.83rem;padding:0.2rem 0;color:#374151">'
                            f'{icon} {t.get("title","")}{"  <small style=\'color:#9ca3af\'>· due "+due+"</small>" if due else ""}'
                            f'</div>',
                            unsafe_allow_html=True,
                        )

# ══════════════════════════════════════════════════════════════════
# TAB 3 – DOCUMENTS
# ══════════════════════════════════════════════════════════════════
with tab_docs:
    section("📄 Documents Shared With You")
    all_docs = db.list_documents(visibility="shared_with_client") or db.list_documents()
    CLIENT_VIS = {"shared_with_client", "final", "client_upload"}
    shown_docs = [d for d in all_docs if d.get("visibility","") in CLIENT_VIS]

    if shown_docs:
        VIS_CFG = {
            "shared_with_client": ("🟢", "#dcfce7", "#16a34a", "Shared"),
            "final":              ("🏁", "#e8f0fe", "#1a2744", "Final"),
            "client_upload":      ("📤", "#fffbeb", "#d97706", "Your upload"),
        }
        for d in shown_docs:
            vis = d.get("visibility","")
            icon, bg, fg, label = VIS_CFG.get(vis, ("📄","#f8fafc","#6b7280","Document"))
            st.markdown(
                f"""<div style="background:#fff;border-radius:9px;padding:0.7rem 1rem;
                                margin-bottom:0.35rem;border:1px solid rgba(0,0,0,0.07)">
                  <div style="display:flex;align-items:center;gap:0.6rem">
                    <span style="font-size:1.1rem">{icon}</span>
                    <span style="font-weight:600;font-size:0.87rem;color:#1a2744;flex:1">{d['name']}</span>
                    <span style="background:{bg};color:{fg};font-size:0.7rem;font-weight:600;
                                 padding:0.15rem 0.45rem;border-radius:20px">{label}</span>
                    <span style="font-size:0.72rem;color:#9ca3af">{str(d.get('created_at',''))[:10]}</span>
                  </div>
                </div>""",
                unsafe_allow_html=True,
            )
    else:
        st.info("No documents have been shared with you yet.")

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
    section("📤 Upload a Document")
    matters_mine = db.list_matters()
    matter_opts  = {f"{m['ref']}: {m['title'][:35]}": m["id"] for m in matters_mine}
    if matter_opts:
        sel_m   = st.selectbox("Select matter", list(matter_opts.keys()), key="cup_matter")
        up_file = st.file_uploader("Choose file", key="cup_file")
        up_desc = st.text_input("Description (optional)", key="cup_desc")
        if st.button("📤 Upload", type="primary", key="cup_btn") and up_file:
            db.add_document(
                name=up_file.name, matter_id=matter_opts[sel_m],
                file_type=up_file.type, file_size=up_file.size,
                visibility="client_upload", description=up_desc.strip(),
            )
            db.notify_matter_members(
                matter_opts[sel_m], "document_uploaded",
                f"Client uploaded: {up_file.name}",
                body=f"Uploaded by {user['full_name']}",
                exclude_id=user["id"], lawyers_only=True,
            )
            st.success(f"✅ {up_file.name} uploaded.")
            st.rerun()
    else:
        st.info("You must be assigned to a matter before uploading documents.")

# ══════════════════════════════════════════════════════════════════
# TAB 4 – DISCUSSIONS
# ══════════════════════════════════════════════════════════════════
with tab_disc:
    matters_mine = db.list_matters()
    if not matters_mine:
        st.info("No matters assigned yet.")
    else:
        matter_opts = {f"{m['ref']}: {m['title'][:40]}": m["id"] for m in matters_mine}
        sel = st.selectbox("Select matter", list(matter_opts.keys()), key="cdisc_sel")
        mid = matter_opts[sel]
        db.mark_messages_read(mid)
        messages = db.list_messages(mid)

        st.markdown(
            f'<div style="background:#fff;border-radius:12px;padding:1rem;'
            f'min-height:200px;max-height:420px;overflow-y:auto;'
            f'border:1px solid rgba(0,0,0,0.08);margin-bottom:0.75rem">',
            unsafe_allow_html=True,
        )
        if messages:
            for msg in messages:
                sender = (msg.get("profiles") or {}).get("full_name", "Unknown")
                is_mine = msg.get("sender_id") == user["id"]
                align = "right" if is_mine else "left"
                bg    = "#dbeafe" if is_mine else "#f1f5f9"
                fg    = "#1e40af" if is_mine else "#374151"
                ts    = str(msg.get("created_at",""))[:16].replace("T"," ")
                st.markdown(
                    f"""<div style="text-align:{align};margin:0.4rem 0">
                      <div style="display:inline-block;background:{bg};color:{fg};
                                  padding:0.55rem 0.9rem;border-radius:12px;
                                  max-width:78%;text-align:left">
                        <small style="color:#64748b;font-size:0.72rem">
                          <b>{sender}</b> · {ts}</small><br>
                        <span style="font-size:0.85rem">{msg.get('body','')}</span>
                      </div>
                    </div>""",
                    unsafe_allow_html=True,
                )
        else:
            st.markdown(
                '<p style="text-align:center;color:#9ca3af;padding:2rem 0;font-size:0.85rem">'
                'No messages yet. Start the conversation below.</p>',
                unsafe_allow_html=True,
            )
        st.markdown("</div>", unsafe_allow_html=True)

        with st.form("client_msg_form", clear_on_submit=True):
            body = st.text_area("Your message", height=80,
                                 placeholder="Type your message…", key="cmsg_body",
                                 label_visibility="collapsed")
            att  = st.file_uploader("Attach file (optional)", key="cmsg_att")
            sent = st.form_submit_button("Send ➤", type="primary", use_container_width=True)

        if sent:
            if not body.strip():
                st.warning("Message cannot be empty.")
            else:
                msg = db.send_message(mid, body.strip(), "client_visible")
                if att and msg:
                    doc = db.add_document(att.name, mid, file_type=att.type,
                                           file_size=att.size, visibility="client_upload")
                    if doc:
                        db.add_message_attachment(msg["id"], att.name,
                                                   doc.get("file_path",""), att.type,
                                                   att.size, doc.get("id"))
                db.notify_matter_members(
                    mid, "new_message", f"New message from {user['full_name']}",
                    body=body[:100], exclude_id=user["id"], lawyers_only=True,
                )
                st.rerun()

# ══════════════════════════════════════════════════════════════════
# TAB 5 – BILLING
# ══════════════════════════════════════════════════════════════════
with tab_billing:
    section("🧾 Invoices")

    _inv_status_cfg = {
        "sent":     ("#2563eb", "#eff6ff", "Awaiting Approval"),
        "approved": ("#16a34a", "#f0fdf4", "Approved"),
        "queried":  ("#d97706", "#fffbeb", "Queried"),
        "paid":     ("#7c3aed", "#f5f3ff", "Paid"),
        "draft":    ("#64748b", "#f8fafc", "Draft"),
    }

    _all_invs = db.list_invoices()
    if _all_invs:
        for _inv in _all_invs:
            _s = _inv.get("status", "sent")
            _fg, _bg, _slbl = _inv_status_cfg.get(_s, ("#64748b", "#f8fafc", _s.title()))
            _inv_key = _inv["id"]
            _ic1, _ic2, _ic3, _ic4, _ic5 = st.columns([2.5, 1.5, 1.5, 1.5, 1.5])
            _ic1.markdown(f"**{_inv.get('invoice_number','—')}**")
            _ic2.caption(str(_inv.get("issued_date",""))[:10])
            _ic3.markdown(f"**£{_inv.get('total_amount',0):,.2f}**")
            _ic4.markdown(
                f'<span style="background:{_bg};color:{_fg};font-size:.72rem;font-weight:600;'
                f'padding:.15rem .5rem;border-radius:20px">{_slbl}</span>',
                unsafe_allow_html=True,
            )
            if _s == "sent":
                _ba, _bq = _ic5.columns(2)
                if _ba.button("✅", key=f"inv_approve_{_inv_key}", help="Approve invoice"):
                    db.update_invoice_status(_inv_key, "approved")
                    db.notify_matter_members(
                        _inv.get("matter_id",""),
                        "invoice_ready",
                        f"Invoice {_inv.get('invoice_number','')} approved by client",
                        body=f"Approved by {user['full_name']}",
                    )
                    st.success("Invoice approved.")
                    st.rerun()
                if _bq.button("❓", key=f"inv_query_{_inv_key}", help="Query invoice"):
                    db.update_invoice_status(_inv_key, "queried")
                    db.notify_matter_members(
                        _inv.get("matter_id",""),
                        "invoice_ready",
                        f"Invoice {_inv.get('invoice_number','')} queried by client",
                        body=f"Queried by {user['full_name']} — please contact your lawyer",
                    )
                    st.info("Query raised. Your lawyer will be in touch.")
                    st.rerun()

            if st.session_state.get(f"inv_expand_{_inv_key}"):
                st.markdown(
                    f"<pre style='background:#f8fafc;border-radius:8px;padding:1rem;"
                    f"font-size:.78rem;overflow-x:auto;margin-top:.4rem'>"
                    f"{_inv.get('invoice_text','')}</pre>",
                    unsafe_allow_html=True,
                )
            if st.button("👁 View", key=f"inv_tog_{_inv_key}", use_container_width=False):
                _k = f"inv_expand_{_inv_key}"
                st.session_state[_k] = not st.session_state.get(_k, False)
                st.rerun()
            st.divider()
    else:
        st.info("No invoices have been issued yet. Your lawyer will send invoices here for your review.")

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    section("💼 Time Summary")
    matters_b = db.list_matters()
    if matters_b:
        _all_entries = []
        for _m in matters_b:
            _es = db.list_time_entries(matter_id=_m["id"])
            for _e in _es:
                _e["_matter_title"] = _m.get("title", "—")
                _e["_matter_ref"]   = _m.get("ref", "")
            _all_entries.extend(_es)

        if _all_entries:
            _t_hrs = sum(e["hours"] for e in _all_entries)
            _t_val = sum(e["hours"] * (e.get("rate") or 0) for e in _all_entries)
            _billed_val = sum(e["hours"] * (e.get("rate") or 0)
                              for e in _all_entries if e.get("billed"))
            bc1, bc2, bc3 = st.columns(3)
            bc1.metric("Total Hours Recorded", f"{_t_hrs:.1f} h")
            bc2.metric("Total Fees",            f"£{_t_val:,.0f}")
            bc3.metric("Invoiced",              f"£{_billed_val:,.0f}")

            st.divider()
            for _m in matters_b:
                _m_entries = [e for e in _all_entries if e.get("_matter_ref") == _m.get("ref")]
                if not _m_entries:
                    continue
                _m_hrs = sum(e["hours"] for e in _m_entries)
                _m_val = sum(e["hours"] * (e.get("rate") or 0) for e in _m_entries)
                with st.expander(
                    f"📁 {_m.get('ref','')} — {_m.get('title','')[:40]}  ·  "
                    f"{_m_hrs:.1f}h  ·  £{_m_val:,.0f}"
                ):
                    for e in _m_entries:
                        st.markdown(
                            f"""<div style="background:#f8fafc;border-radius:6px;padding:.45rem .8rem;
                                          margin-bottom:.2rem;border-left:3px solid #c9a84c;
                                          display:flex;align-items:center;gap:.75rem;font-size:.82rem">
                              <span style="color:#9ca3af;white-space:nowrap">{str(e.get('entry_date',''))[:10]}</span>
                              <span style="flex:1;color:#374151">{e.get('description','—')}</span>
                              <span style="font-weight:600;color:#1a2744">{e['hours']:.1f}h</span>
                              <span style="color:#c9a84c;font-weight:700">£{e['hours']*(e.get('rate') or 0):,.0f}</span>
                            </div>""",
                            unsafe_allow_html=True,
                        )
        else:
            st.info("No time entries recorded for your matters yet.")
    else:
        st.info("No matters assigned yet.")


# ══════════════════════════════════════════════════════════════════
# TAB 6 – PROFILE
# ══════════════════════════════════════════════════════════════════
with tab_profile:
    profile = db.get_profile(user["id"]) or {}
    left, right = st.columns(2, gap="large")

    with left:
        section("👤 My Details")
        st.markdown(
            f"""<div style="background:#fff;border-radius:12px;padding:1.25rem;
                            border:1px solid rgba(0,0,0,0.08)">
              <div style="display:flex;align-items:center;gap:1rem;margin-bottom:1rem">
                <div style="background:#1a2744;color:#fff;border-radius:50%;
                            width:52px;height:52px;display:flex;align-items:center;
                            justify-content:center;font-size:1.4rem;font-weight:700;flex-shrink:0">
                  {first_name[0].upper()}</div>
                <div>
                  <p style="margin:0;font-weight:700;color:#1a2744;font-size:1rem">
                    {profile.get('full_name','')}</p>
                  <p style="margin:0;font-size:0.82rem;color:#6b7280">{profile.get('email','')}</p>
                </div>
              </div>
              <div style="border-top:1px solid #f1f5f9;padding-top:0.75rem">
                <p style="margin:0.2rem 0;font-size:0.83rem;color:#374151">
                  <b>Role:</b> {profile.get('role','client').title()}</p>
                <p style="margin:0.2rem 0;font-size:0.83rem;color:#374151">
                  <b>Firm:</b> {user['organization_name']}</p>
              </div>
            </div>""",
            unsafe_allow_html=True,
        )

    with right:
        section("🔑 Change Password")
        with st.form("cp_form"):
            new_pw  = st.text_input("New Password", type="password", key="cp_pw")
            new_pw2 = st.text_input("Confirm Password", type="password", key="cp_pw2")
            if st.form_submit_button("Update Password", type="primary"):
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
