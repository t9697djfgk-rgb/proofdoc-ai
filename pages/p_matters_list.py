import streamlit as st
from utils.shared.sidebar import setup_page
from utils.shared.styles import slim_header, inject_css, group_header, section
inject_css()
from utils.auth import require_lawyer
from utils import database as db

api_key = setup_page()
require_lawyer()

slim_header("📁", "Matters", "Manage clients, matters, and engagement workflow")

tab_matters, tab_clients, tab_conflict, tab_engagement = st.tabs([
    "📁 Matters", "👥 Clients", "⚖️ Conflict Check", "📜 Engagement Letters",
])

# ── MATTERS ────────────────────────────────────────────────────────
with tab_matters:
    if "show_new_matter" not in st.session_state:
        st.session_state.show_new_matter = False
    if "selected_matter_id" not in st.session_state:
        st.session_state.selected_matter_id = None

    col_hd, col_btn = st.columns([3, 1])
    col_hd.markdown("### Active Matters")
    if col_btn.button("＋ New Matter", type="primary", use_container_width=True):
        st.session_state.show_new_matter = True

    if st.session_state.show_new_matter:
        with st.form("new_matter_form", clear_on_submit=True):
            group_header("Create New Matter")
            f1, f2 = st.columns(2)
            m_title  = f1.text_input("Matter Title *", placeholder="e.g. Smith v Jones — Breach of Contract")
            clients  = db.list_clients()
            client_opts = {"(No client)": ""} | {c["name"]: c["id"] for c in clients}
            m_client = f2.selectbox("Client", list(client_opts.keys()))
            f3, f4 = st.columns(2)
            m_type   = f3.selectbox("Matter Type", [
                "Commercial", "Employment", "Property", "Family", "Criminal",
                "Immigration", "Intellectual Property", "Corporate", "Litigation", "Other",
            ])
            m_juris  = f4.selectbox("Jurisdiction", ["Rwanda", "UK", "US", "EU", "International", "Other"])
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
                    user = st.session_state.get("user", {})
                    existing = db.list_matters()
                    ref = f"MAT-{__import__('datetime').date.today().year}-{len(existing)+1:04d}"
                    matter = db.create_matter(
                        ref=ref,
                        title=m_title.strip(),
                        matter_type=m_type,
                        jurisdiction=m_juris,
                        description=m_desc.strip(),
                    )
                    if matter and client_opts.get(m_client):
                        client_profile = db.get_db().table("clients").select("profile_id").eq("id", client_opts[m_client]).maybe_single().execute()
                        if client_profile.data and client_profile.data.get("profile_id"):
                            db.add_matter_member(matter["id"], client_profile.data["profile_id"], "client")
                    st.session_state.show_new_matter = False
                    if matter:
                        st.session_state.selected_matter_id = matter["id"]
                    st.rerun()

    matters = db.list_matters()
    if not matters:
        st.markdown(
            '<div class="empty-list" style="margin-top:1rem">'
            '📁 No matters yet.<br>'
            '<small>Click <strong>＋ New Matter</strong> to create your first matter.</small>'
            '</div>', unsafe_allow_html=True,
        )
    else:
        f_col1, f_col2, _ = st.columns([1, 1, 2])
        status_filter = f_col1.selectbox("Status", ["All", "Active", "Closed", "On Hold", "Archived"], key="m_status")
        search_filter = f_col2.text_input("Search", placeholder="Title or ref…", key="m_search")
        visible = [
            m for m in matters
            if (status_filter == "All" or m.get("status") == status_filter)
            and (not search_filter or search_filter.lower() in m["title"].lower()
                 or search_filter.lower() in m.get("ref", "").lower())
        ]
        STATUS_CFG = {
            "Active":   ("#16a34a", "#dcfce7"),
            "On Hold":  ("#d97706", "#fef9c3"),
            "Closed":   ("#64748b", "#f1f5f9"),
            "Archived": ("#94a3b8", "#f8fafc"),
        }
        for m in visible:
            status = m.get("status", "Active")
            fg, bg = STATUS_CFG.get(status, ("#64748b", "#f1f5f9"))
            ref    = m.get("ref", "—")
            title  = (m.get("title") or "Untitled")
            mtype  = m.get("matter_type") or "—"
            juris  = m.get("jurisdiction") or "—"
            updated = str(m.get("updated_at", m.get("created_at", "")))[:10]
            card_col, btn_col = st.columns([9, 1])
            card_col.markdown(
                f"""
                <div style="background:#fff;border-radius:10px;padding:0.75rem 1rem;
                            border:1px solid rgba(0,0,0,0.07);
                            border-left:4px solid {fg};
                            box-shadow:0 1px 4px rgba(0,0,0,0.05);margin-bottom:0.1rem">
                  <div style="display:flex;align-items:center;gap:0.75rem;flex-wrap:wrap">
                    <span style="font-weight:700;color:#1a2744;font-size:0.88rem">{ref}</span>
                    <span style="font-size:0.88rem;color:#374151">{title[:60]}</span>
                    <span style="background:{bg};color:{fg};font-size:0.7rem;font-weight:600;
                                 padding:0.15rem 0.5rem;border-radius:20px;margin-left:auto">
                      {status}</span>
                  </div>
                  <div style="margin-top:0.3rem;display:flex;gap:1.2rem;font-size:0.75rem;color:#9ca3af;flex-wrap:wrap">
                    <span>📂 {mtype}</span><span>🌍 {juris}</span><span>🕐 {updated}</span>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if btn_col.button("Open →", key=f"open_{m['id']}", use_container_width=True):
                st.session_state.selected_matter_id = m["id"]
                st.rerun()
        st.caption(f"{len(visible)} of {len(matters)} matters shown")

    # ── Matter Detail ──────────────────────────────────────────────
    if st.session_state.get("selected_matter_id"):
        matter = db.get_matter(st.session_state.selected_matter_id)
        if matter:
            st.markdown("---")
            st.markdown(f"### 📁 {matter.get('ref','')} — {matter['title']}")
            d1, d2, d3, d4 = st.columns(4)
            d1.metric("Type",         matter.get("matter_type") or "—")
            d2.metric("Status",       matter.get("status") or "—")
            d3.metric("Jurisdiction", matter.get("jurisdiction") or "—")
            d4.metric("Priority",     matter.get("priority") or "—")

            m_tabs = st.tabs([
                "Overview", "Tasks", "Notes", "Time", "Documents",
                "Members", "Discussion", "AI Reviews", "Drafts",
                "Deadlines", "Billing", "Audit",
            ])

            # Overview
            with m_tabs[0]:
                with st.form("edit_matter_form"):
                    e1, e2 = st.columns(2)
                    status_opts = ["Active", "On Hold", "Closed", "Archived"]
                    curr_status = matter.get("status", "Active")
                    new_status  = e1.selectbox("Status", status_opts,
                                               index=status_opts.index(curr_status) if curr_status in status_opts else 0)
                    priority_opts = ["high", "medium", "low"]
                    curr_pri = matter.get("priority", "medium")
                    new_priority = e2.selectbox("Priority", priority_opts,
                                                index=priority_opts.index(curr_pri) if curr_pri in priority_opts else 1)
                    new_close = e1.text_input("Close Date (YYYY-MM-DD)", value=str(matter.get("close_date") or ""))
                    new_court = e2.text_input("Court Reference", value=matter.get("court_reference") or "")
                    new_opp   = e1.text_input("Opposing Party",  value=matter.get("opposing_party") or "")
                    new_desc  = st.text_area("Description", value=matter.get("description") or "")
                    if st.form_submit_button("💾 Save Changes", type="primary"):
                        db.update_matter(matter["id"],
                                         status=new_status, priority=new_priority,
                                         description=new_desc,
                                         court_reference=new_court.strip(),
                                         opposing_party=new_opp.strip(),
                                         close_date=new_close.strip() or None)
                        st.success("✅ Matter updated.")
                        st.rerun()
                col_del, _ = st.columns([1, 3])
                if col_del.button("🗑️ Delete Matter", key="del_m"):
                    db.delete_matter(matter["id"])
                    st.session_state.selected_matter_id = None
                    st.rerun()

            # Tasks
            with m_tabs[1]:
                lawyers = db.list_lawyers()
                lawyer_opts = {"Unassigned": None} | {l["full_name"]: l["id"] for l in lawyers}
                with st.form("new_task_form", clear_on_submit=True):
                    t1, t2, t3 = st.columns(3)
                    t_title    = t1.text_input("Task *")
                    t_priority = t2.selectbox("Priority", ["high", "medium", "low"])
                    t_due      = t3.text_input("Due (YYYY-MM-DD)")
                    t_assign   = st.selectbox("Assign to", list(lawyer_opts.keys()), key="task_assign")
                    if st.form_submit_button("＋ Add Task"):
                        if t_title.strip():
                            db.create_task(
                                matter_id=matter["id"], title=t_title.strip(),
                                priority=t_priority,
                                due_date=t_due.strip() or None,
                                assigned_to=lawyer_opts[t_assign],
                            )
                            st.rerun()
                tasks = db.list_tasks(matter_id=matter["id"])
                if not tasks:
                    st.markdown('<div class="empty-list">No tasks yet.</div>', unsafe_allow_html=True)
                else:
                    STATUS_MAP = {"pending": 0, "in_progress": 1, "completed": 2, "cancelled": 3}
                    STATUS_OPTS = ["pending", "in_progress", "completed", "cancelled"]
                    for t in tasks:
                        tc = st.columns([3, 1, 1, 1.5, 0.5])
                        tc[0].text(t["title"])
                        tc[1].text((t.get("priority") or "").title())
                        tc[2].text(str(t.get("due_date") or "—")[:10])
                        curr = t.get("status", "pending")
                        new_s = tc[3].selectbox("", STATUS_OPTS,
                                                index=STATUS_MAP.get(curr, 0),
                                                key=f"ts_{t['id']}", label_visibility="collapsed")
                        if new_s != curr:
                            db.update_task(t["id"], status=new_s)
                            st.rerun()
                        if tc[4].button("🗑️", key=f"del_t_{t['id']}"):
                            db.delete_task(t["id"])
                            st.rerun()

            # Notes
            with m_tabs[2]:
                user = st.session_state.get("user", {})
                with st.form("new_note_form", clear_on_submit=True):
                    n_title = st.text_input("Title (optional)")
                    n_body  = st.text_area("Note *", height=80)
                    if st.form_submit_button("＋ Add Note"):
                        if n_body.strip():
                            db.add_note(matter["id"], n_body.strip(), n_title.strip())
                            st.rerun()
                for note in db.list_notes(matter["id"]):
                    author = (note.get("profiles") or {}).get("full_name", "Anonymous")
                    st.markdown(
                        f'<div class="activity-item"><strong>{author}</strong> · '
                        f'{str(note.get("created_at",""))[:16]}<br>'
                        f'{"<b>" + note["title"] + "</b><br>" if note.get("title") else ""}'
                        f'{note["body"]}</div>', unsafe_allow_html=True,
                    )

            # Time
            with m_tabs[3]:
                with st.form("new_time_form", clear_on_submit=True):
                    ti1, ti2, ti3 = st.columns(3)
                    ti_hours = ti1.number_input("Hours", min_value=0.25, step=0.25, value=1.0)
                    ti_rate  = ti2.number_input("Rate (£/hr)", min_value=0.0, step=50.0, value=250.0)
                    ti_date  = ti3.text_input("Date (YYYY-MM-DD)",
                                              value=str(__import__("datetime").date.today()))
                    ti_desc  = st.text_input("Description *")
                    if st.form_submit_button("＋ Log Time"):
                        if ti_desc.strip():
                            db.add_time_entry(matter["id"], ti_hours, ti_desc.strip(),
                                              ti_rate, entry_date=ti_date.strip())
                            st.rerun()
                entries = db.list_time_entries(matter["id"])
                if entries:
                    total_h   = sum(e["hours"] for e in entries)
                    total_val = sum(e["hours"] * (e.get("rate") or 0) for e in entries)
                    m1, m2 = st.columns(2)
                    m1.metric("Total Hours", f"{total_h:.2f} h")
                    m2.metric("Total Value",  f"£{total_val:,.2f}")
                    st.divider()
                    for e in entries:
                        st.text(f"{str(e.get('entry_date',''))[:10]}  {e['hours']:.2f}h  "
                                f"£{(e.get('rate') or 0):.0f}/hr  {e.get('description','—')}")
                else:
                    st.markdown('<div class="empty-list">No time entries yet.</div>', unsafe_allow_html=True)

            # Documents
            with m_tabs[4]:
                docs = db.list_documents(matter_id=matter["id"])
                if docs:
                    for d in docs:
                        vis = d.get("visibility","internal")
                        vis_icon = {"internal":"🔒","shared_with_client":"🟢","client_upload":"📤","final":"🏁","draft":"📝"}.get(vis,"📄")
                        c1, c2, c3 = st.columns([4, 2, 1])
                        c1.markdown(f"{vis_icon} **{d['name']}**")
                        c2.caption(vis.replace("_"," ").title())
                        c3.caption(str(d.get("created_at",""))[:10])
                else:
                    st.info("No documents yet. Upload via the Document Library.")
                st.markdown("<br>", unsafe_allow_html=True)
                up_file = st.file_uploader("Upload document to this matter", key=f"mdoc_{matter['id']}")
                vis_choice = st.selectbox("Visibility", ["internal","shared_with_client","draft","final"],
                                          key=f"mvis_{matter['id']}")
                if st.button("Upload", key=f"mup_{matter['id']}") and up_file:
                    db.add_document(up_file.name, matter["id"], file_type=up_file.type,
                                    file_size=up_file.size, visibility=vis_choice)
                    st.success(f"✅ {up_file.name} uploaded.")
                    st.rerun()

            # Members
            with m_tabs[5]:
                members = db.get_matter_members(matter["id"])
                ROLE_ICONS = {"lead_lawyer":"⭐","lawyer":"⚖️","staff":"👤","client":"🏢","intern":"🎓"}
                if members:
                    for mem in members:
                        p = mem.get("profiles") or {}
                        c1, c2, c3 = st.columns([3, 2, 1])
                        c1.text(p.get("full_name","—"))
                        c2.text(f"{ROLE_ICONS.get(mem['role'],'👤')} {mem['role'].replace('_',' ').title()}")
                        c3.text(p.get("email","—"))
                else:
                    st.caption("No members assigned yet.")
                st.markdown("<br>", unsafe_allow_html=True)
                all_profiles = db.list_profiles()
                member_ids = {m["profile_id"] for m in members}
                opts = {f"{p['full_name']} ({p['role']})": p["id"] for p in all_profiles if p["id"] not in member_ids}
                if opts:
                    c1, c2, c3 = st.columns([3, 2, 1])
                    add_who  = c1.selectbox("Add member", list(opts.keys()), key=f"madd_who_{matter['id']}")
                    add_role = c2.selectbox("Role", ["lawyer","staff","client","intern","lead_lawyer"], key=f"madd_role_{matter['id']}")
                    if c3.button("Add", key=f"madd_btn_{matter['id']}", type="primary"):
                        db.add_matter_member(matter["id"], opts[add_who], add_role)
                        st.rerun()

            # Discussion shortcut
            with m_tabs[6]:
                unread = db.unread_message_count(matter["id"])
                if unread > 0:
                    st.warning(f"🔔 {unread} unread message(s) in this matter.")
                if st.button("💬 Open Matter Discussion", type="primary", key=f"disc_btn_{matter['id']}"):
                    st.session_state["discussion_matter_id"] = matter["id"]
                    st.switch_page("pages/p_matter_discussion.py")
                st.caption("Full discussion thread, internal notes, and file attachments are in the Discussion page.")

            # m_tabs[7] – AI Reviews
            with m_tabs[7]:
                st.markdown(
                    '<div class="notice-box">🔍 AI Contract Review, clause risk analysis, and document editing '
                    'suggestions are in the <b>AI Tools</b> section. Navigate there to run analysis on this matter.</div>',
                    unsafe_allow_html=True,
                )
                _rc1, _rc2, _rc3 = st.columns(3)
                if _rc1.button("🔍 AI Review", key=f"go_rev_{matter['id']}", use_container_width=True, type="primary"):
                    st.switch_page("pages/p_ai_review.py")
                if _rc2.button("📊 AI Analysis", key=f"go_an_{matter['id']}", use_container_width=True):
                    st.switch_page("pages/p_ai_analysis.py")
                if _rc3.button("🔬 Research", key=f"go_res_{matter['id']}", use_container_width=True):
                    st.switch_page("pages/p_ai_research.py")

            # m_tabs[8] – Drafts
            with m_tabs[8]:
                st.markdown(
                    '<div class="notice-box">📝 Draft contracts, court documents, legal memos, and engagement '
                    'letters via the <b>AI Tools → Draft</b> page.</div>',
                    unsafe_allow_html=True,
                )
                _dc1, _dc2 = st.columns(2)
                if _dc1.button("📝 Drafting Assistant", key=f"go_dr_{matter['id']}", use_container_width=True, type="primary"):
                    st.switch_page("pages/p_ai_draft.py")
                if _dc2.button("🧮 Calculators", key=f"go_calc_{matter['id']}", use_container_width=True):
                    st.switch_page("pages/p_ai_calculators.py")

            # m_tabs[9] – Deadlines
            with m_tabs[9]:
                import datetime as _dt2
                _today2 = _dt2.date.today()
                _tasks_dl = db.list_tasks(matter_id=matter["id"])
                _with_due = [t for t in _tasks_dl
                             if t.get("due_date") and t.get("status") not in ("completed", "cancelled")]
                _with_due.sort(key=lambda t: str(t.get("due_date", "9999")))
                if _with_due:
                    for t in _with_due:
                        _due2 = _dt2.date.fromisoformat(str(t["due_date"])[:10])
                        _days2 = (_due2 - _today2).days
                        if _days2 < 0:    _fg2, _bg2, _lbl2 = "#dc2626", "#fef2f2", "OVERDUE"
                        elif _days2 == 0: _fg2, _bg2, _lbl2 = "#7c3aed", "#f5f3ff", "TODAY"
                        elif _days2 <= 3: _fg2, _bg2, _lbl2 = "#d97706", "#fffbeb", f"{_days2}d"
                        elif _days2 <= 14:_fg2, _bg2, _lbl2 = "#059669", "#f0fdf4", f"{_days2}d"
                        else:             _fg2, _bg2, _lbl2 = "#64748b", "#f1f5f9", f"{_days2}d"
                        _pri2_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(
                            (t.get("priority") or "").lower(), "📌")
                        st.markdown(
                            f"""<div style="background:{_bg2};border-radius:8px;padding:.65rem 1rem;
                                          margin-bottom:.35rem;border-left:3px solid {_fg2};
                                          display:flex;align-items:center;gap:1rem;flex-wrap:wrap">
                              <span>{_pri2_icon}</span>
                              <div style="flex:1;min-width:0">
                                <p style="margin:0;font-size:.86rem;font-weight:600;color:#1a1a2e">{t.get('title','')}</p>
                                <p style="margin:0;font-size:.74rem;color:#64748b">Due: {str(t['due_date'])[:10]}</p>
                              </div>
                              <span style="background:white;color:{_fg2};font-size:.72rem;font-weight:700;
                                           padding:.25rem .6rem;border-radius:20px;border:1px solid {_fg2}">{_lbl2}</span>
                            </div>""",
                            unsafe_allow_html=True,
                        )
                else:
                    st.markdown('<div class="empty-list">⏰ No active deadlines for this matter.</div>',
                                unsafe_allow_html=True)

            # m_tabs[10] – Billing
            with m_tabs[10]:
                _entries2 = db.list_time_entries(matter["id"])
                if _entries2:
                    _total_h2   = sum(e["hours"] for e in _entries2)
                    _total_val2 = sum(e["hours"] * (e.get("rate") or 0) for e in _entries2)
                    _billed2    = sum(e["hours"] * (e.get("rate") or 0) for e in _entries2 if e.get("billed"))
                    bc1, bc2, bc3 = st.columns(3)
                    bc1.metric("Total Hours", f"{_total_h2:.1f} h")
                    bc2.metric("Total Value",  f"£{_total_val2:,.0f}")
                    bc3.metric("Unbilled",     f"£{_total_val2 - _billed2:,.0f}")
                    st.divider()
                    for e in _entries2[:20]:
                        _bstat2 = "✅" if e.get("billed") else "🔵"
                        st.markdown(
                            f"""<div style="background:#f8fafc;border-radius:7px;padding:.5rem .9rem;
                                          margin-bottom:.25rem;border-left:3px solid #c9a84c;
                                          display:flex;align-items:center;gap:.75rem;flex-wrap:wrap">
                              <span style="font-size:.73rem;color:#9ca3af;white-space:nowrap">{str(e.get('entry_date',''))[:10]}</span>
                              <span style="flex:1;font-size:.84rem;color:#1a2744">{e.get('description','—')}</span>
                              <span style="font-size:.8rem;font-weight:600;color:#1a2744">{e['hours']:.1f}h</span>
                              <span style="font-size:.78rem;color:#64748b">£{(e.get('rate') or 0):.0f}/hr</span>
                              <span style="font-size:.8rem;font-weight:700;color:#c9a84c">£{e['hours']*(e.get('rate') or 0):,.0f}</span>
                              <span>{_bstat2}</span>
                            </div>""",
                            unsafe_allow_html=True,
                        )
                    if st.button("💼 Full Billing & Invoicing →", key=f"bill_full_{matter['id']}"):
                        st.switch_page("pages/p_billing.py")
                else:
                    st.markdown('<div class="empty-list">💼 No time entries yet for this matter.</div>',
                                unsafe_allow_html=True)

            # m_tabs[11] – Audit
            with m_tabs[11]:
                _uid_org2 = (st.session_state.get("user") or {}).get("organization_id")
                try:
                    _al2 = (db.get_db().table("audit_logs")
                            .select("*").eq("organization_id", _uid_org2)
                            .eq("resource_id", matter["id"])
                            .order("created_at", desc=True).limit(50).execute()).data or []
                except Exception:
                    _al2 = []
                if _al2:
                    _AC2 = {
                        "CREATE": ("#2563eb", "#eff6ff"), "UPDATE": ("#d97706", "#fffbeb"),
                        "DELETE": ("#dc2626", "#fef2f2"), "MATTER": ("#1a2744", "#f0f4ff"),
                    }
                    for _l2 in _al2:
                        _root2 = _l2.get("action", "").split("_")[0].upper()
                        _fg3, _bg3 = _AC2.get(_root2, ("#1a2744", "#f1f5f9"))
                        _ts2  = str(_l2.get("created_at", ""))[:16].replace("T", " ")
                        _act2 = _l2.get("actor_name", "System") or "System"
                        st.markdown(
                            f"""<div style="background:{_bg3};border-radius:8px;padding:.5rem .9rem;
                                          margin-bottom:.3rem;border-left:3px solid {_fg3};
                                          display:flex;align-items:center;gap:.8rem;flex-wrap:wrap">
                              <span style="font-size:.68rem;font-weight:700;color:{_fg3};background:white;
                                           padding:.15rem .45rem;border-radius:20px;
                                           border:1px solid {_fg3};white-space:nowrap">{_l2.get('action','')}</span>
                              <span style="font-size:.82rem;font-weight:600;color:#1a2744">{_act2}</span>
                              <span style="margin-left:auto;font-size:.7rem;color:#94a3b8;white-space:nowrap">{_ts2}</span>
                            </div>""",
                            unsafe_allow_html=True,
                        )
                else:
                    st.markdown('<div class="empty-list">📋 No audit entries recorded for this matter yet.</div>',
                                unsafe_allow_html=True)

        if st.button("← Back to list"):
            st.session_state.selected_matter_id = None
            st.rerun()

# ── CLIENTS ────────────────────────────────────────────────────────
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
            c_email   = fc3.text_input("Email",  placeholder="jane@example.com")
            c_phone   = fc4.text_input("Phone",  placeholder="+250 7xx xxx xxx")
            c_type    = fc5.selectbox("Client Type", ["individual","company","government","ngo","other"])
            c_notes   = st.text_area("Notes", height=60)
            fs1, fs2, _ = st.columns(3)
            if fs1.form_submit_button("💾 Save Client", type="primary", use_container_width=True):
                if not c_name.strip():
                    st.error("Client name is required.")
                else:
                    db.create_client(
                        name=c_name.strip(), email=c_email.strip(),
                        phone=c_phone.strip(), company_name=c_company.strip(),
                        client_type=c_type, notes=c_notes.strip(),
                    )
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
            '</div>', unsafe_allow_html=True,
        )
    else:
        ch = st.columns([2.5, 2, 1.5, 1.5, 0.8])
        for col, lbl in zip(ch, ["Name", "Company", "Email", "Type", "Active"]):
            col.markdown(f"**{lbl}**")
        st.divider()
        for c in clients:
            cr = st.columns([2.5, 2, 1.5, 1.5, 0.8])
            cr[0].text(c.get("name",""))
            cr[1].text(c.get("company_name") or "—")
            cr[2].text(c.get("email") or "—")
            cr[3].text((c.get("client_type") or "").title())
            cr[4].text("🟢" if c.get("is_active") else "🔴")
        st.caption(f"{len(clients)} clients")

# ── CONFLICT CHECK ─────────────────────────────────────────────────
with tab_conflict:
    group_header("Conflict Check")
    st.markdown("Check a party name against all existing clients and matters.")
    search_party = st.text_input("Party name to screen", placeholder="e.g. Acme Corp or John Smith")
    if st.button("🔍 Run Conflict Check", disabled=not search_party.strip()):
        name_lower  = search_party.strip().lower()
        all_clients = db.list_clients()
        all_matters = db.list_matters()
        client_hits = [c for c in all_clients if name_lower in (c.get("name") or "").lower()
                       or name_lower in (c.get("company_name") or "").lower()]
        matter_hits = [m for m in all_matters if name_lower in m["title"].lower()
                       or name_lower in (m.get("opposing_party") or "").lower()]
        if client_hits or matter_hits:
            st.warning(f"⚠️ Potential conflict found for **'{search_party}'**.")
            if client_hits:
                st.markdown("**Matching clients:**")
                for c in client_hits:
                    st.markdown(f"- {c['name']} ({c.get('company_name') or 'Individual'})")
            if matter_hits:
                st.markdown("**Matching matters:**")
                for m in matter_hits:
                    st.markdown(f"- {m.get('ref','')}: {m['title']} — {m.get('status','')}")
        else:
            st.success(f"✅ No conflicts found for **'{search_party}'**.")

# ── ENGAGEMENT LETTERS ─────────────────────────────────────────────
with tab_engagement:
    # api_key already set at top of page

    section("📜 Generate Engagement Letter")
    st.markdown(
        '<div class="notice-box">ℹ️ Select a matter and fill in the fee details. '
        "Claude will draft a professional engagement letter ready for review and signature.</div>",
        unsafe_allow_html=True,
    )

    matters_for_eng = db.list_matters()
    if not matters_for_eng:
        st.info("Create a matter first.")
    else:
        eng_opts = {f"{m.get('ref','')} – {m['title'][:45]}": m for m in matters_for_eng}
        eng_sel  = st.selectbox("Select matter", list(eng_opts.keys()), key="eng_matter")
        eng_m    = eng_opts[eng_sel]

        c1, c2, c3 = st.columns(3)
        eng_fee_type = c1.selectbox("Fee arrangement", [
            "Fixed fee", "Hourly rate", "Retainer", "Conditional fee", "Damages-based agreement", "Pro bono",
        ], key="eng_fee_type")
        eng_amount   = c2.text_input("Fee amount / rate", placeholder="e.g. £5,000 or £250/hr", key="eng_amt")
        eng_currency = c3.selectbox("Currency", ["RWF", "USD", "GBP", "EUR"], key="eng_cur")
        eng_scope    = st.text_area("Scope of services", height=80,
                                     placeholder="Describe the legal services to be provided…", key="eng_scope")
        eng_terms    = st.text_area("Special terms / exclusions (optional)", height=60, key="eng_terms")
        eng_law      = st.selectbox("Governing law", ["Rwanda", "England & Wales", "New York", "Other"], key="eng_law")

        if st.button("📜 Generate Engagement Letter", type="primary",
                     disabled=not api_key or not eng_scope.strip(), key="eng_gen"):
            from utils.drafting_assistant import DraftingAssistant
            with st.spinner("Drafting engagement letter with Claude Opus 4.7…"):
                try:
                    result = DraftingAssistant(api_key).draft(
                        doc_type="Client Engagement Letter",
                        jurisdiction=eng_law,
                        legal_style="Professional law firm correspondence",
                        parties=f"Law firm: {st.session_state['user']['organization_name']} | Client: {eng_m['title']}",
                        key_facts=(
                            f"Matter: {eng_m.get('ref','')} – {eng_m['title']}\n"
                            f"Matter type: {eng_m.get('matter_type','')}\n"
                            f"Fee arrangement: {eng_fee_type}, {eng_amount} {eng_currency}\n"
                            f"Scope: {eng_scope}"
                        ),
                        tone="Professional and formal",
                        additional=eng_terms or "Standard terms apply.",
                    )
                    st.session_state["eng_result"] = result
                except Exception as exc:
                    st.error(f"Generation failed: {exc}")

        if st.session_state.get("eng_result"):
            res = st.session_state.eng_result
            letter = res.get("draft_document", "")
            st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
            section("📄 Draft Engagement Letter")
            st.markdown(
                f'<div class="revised-doc">{letter.replace(chr(10), "<br>")}</div>',
                unsafe_allow_html=True,
            )
            if res.get("missing_information"):
                with st.expander("⚠️ Missing information — complete before sending"):
                    for item in res["missing_information"]:
                        st.warning(item)
            st.download_button(
                "⬇️ Download (.txt)", data=letter,
                file_name=f"engagement_letter_{eng_m.get('ref','matter')}.txt",
                mime="text/plain", key="dl_eng",
            )
            if st.button("🗑️ Clear", key="eng_clear"):
                del st.session_state["eng_result"]
                st.rerun()
