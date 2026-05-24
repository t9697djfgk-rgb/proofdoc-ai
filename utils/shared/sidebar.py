import streamlit as st
from utils.shared.styles import inject_css


def render_sidebar(tool_name: str = "") -> str | None:
    """Renders the sidebar. Returns the Anthropic API key if available."""
    inject_css()
    with st.sidebar:
        user = st.session_state.get("user")

        # ── Logged-in user info ────────────────────────────────────
        if user:
            role_icon = {"admin": "🛡️", "lawyer": "⚖️", "staff": "👤", "client": "🏢", "intern": "🎓"}.get(user["role"], "👤")
            st.markdown(f"**{role_icon} {user['full_name']}**")
            st.caption(f"{user.get('title') or user['role'].title()} · {user['organization_name']}")
            if st.button("Sign Out", use_container_width=True, key="sb_signout"):
                from utils.auth import sign_out
                sign_out()
                st.rerun()
            st.divider()

        # ── Global search ──────────────────────────────────────────
        if user and user.get("role") != "client":
            query = st.text_input("🔍 Search", placeholder="Matters, clients, docs…",
                                  key="sb_search", label_visibility="collapsed")
            if query and len(query) >= 2:
                _render_search_results(query)
            st.divider()

        # ── Notifications ──────────────────────────────────────────
        if user:
            from utils import database as db
            unread = db.unread_notification_count()
            bell = f"🔔 **{unread} unread**" if unread > 0 else "🔕 Notifications"
            with st.expander(bell, expanded=unread > 0):
                if unread > 0:
                    if st.button("✓ Mark all read", key="sb_mark_read", use_container_width=True):
                        db.mark_notifications_read()
                        st.rerun()
                notifications = db.list_notifications(limit=10)
                if notifications:
                    for n in notifications:
                        is_unread = not n.get("read_at")
                        dot = "🔵 " if is_unread else "   "
                        ts = (n.get("created_at") or "")[:16].replace("T", " ")
                        st.markdown(
                            f"<div style='padding:0.35rem 0.5rem;border-radius:6px;"
                            f"background:{'rgba(201,168,76,0.08)' if is_unread else 'transparent'};"
                            f"margin-bottom:0.25rem;font-size:0.8rem;line-height:1.4'>"
                            f"{dot}<b>{n.get('title','')}</b><br>"
                            f"<span style='color:#6b7280'>{n.get('message','')}</span><br>"
                            f"<span style='color:#9ca3af;font-size:0.72rem'>{ts}</span></div>",
                            unsafe_allow_html=True,
                        )
                else:
                    st.caption("No notifications yet.")
            st.divider()

        # ── API key (for AI tools — lawyers/staff only) ───────────
        api_key = None
        if not user or user.get("role") in ("admin", "lawyer", "staff"):
            try:
                import os as _os
                api_key = _os.environ.get("ANTHROPIC_API_KEY", "")
                if not api_key:
                    api_key = st.secrets["ANTHROPIC_API_KEY"]
                if not api_key:
                    raise KeyError
                if tool_name:
                    st.markdown(f"**🔧 {tool_name}**")
                    st.divider()
            except Exception:
                key = st.text_input("Anthropic API Key", type="password",
                                    placeholder="sk-ant-...", key="sidebar_api_key")
                if key:
                    api_key = key
                    st.success("✅ API key set")
                else:
                    st.warning("Enter your API key to use AI tools")
                if tool_name:
                    st.divider()

        # ── Quick Time Tracker ─────────────────────────────────────
        if user and user.get("role") != "client":
            import time as _time
            st.markdown(
                '<p style="font-size:0.75rem;font-weight:700;color:#1a2744;'
                'text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.4rem">'
                '⏱️ Time Tracker</p>',
                unsafe_allow_html=True,
            )
            if "timer_running" not in st.session_state:
                st.session_state.timer_running = False
                st.session_state.timer_start   = 0.0
                st.session_state.timer_matter  = None

            if not st.session_state.timer_running:
                try:
                    from utils import database as _tdb
                    _tm_list = _tdb.list_matters()
                except Exception:
                    _tm_list = []
                _tm_opts = {"— No matter —": None}
                _tm_opts.update({
                    f"{m.get('ref','')} {(m.get('title') or '')[:22]}": m["id"]
                    for m in _tm_list
                })
                _tm_sel = st.selectbox("Matter", list(_tm_opts.keys()),
                                       key="sb_timer_matter", label_visibility="collapsed")
                if st.button("▶ Start Timer", use_container_width=True, key="sb_timer_start"):
                    st.session_state.timer_running = True
                    st.session_state.timer_start   = _time.time()
                    st.session_state.timer_matter  = _tm_opts[_tm_sel]
                    st.rerun()
            else:
                _elapsed = _time.time() - st.session_state.timer_start
                _th = int(_elapsed // 3600)
                _tm2 = int((_elapsed % 3600) // 60)
                _ts2 = int(_elapsed % 60)
                st.markdown(
                    f'<div style="font-size:1.4rem;font-weight:800;color:#1a2744;'
                    f'letter-spacing:.05em;text-align:center;padding:.3rem 0">'
                    f'⏱ {_th:02d}:{_tm2:02d}:{_ts2:02d}</div>',
                    unsafe_allow_html=True,
                )
                _tdesc = st.text_input("What are you working on?", key="sb_timer_desc",
                                       label_visibility="collapsed",
                                       placeholder="e.g. Drafting NDA, client call…")
                _trate = st.number_input("Rate (£/hr)", min_value=0.0, step=50.0,
                                         value=250.0, key="sb_timer_rate",
                                         label_visibility="collapsed")
                _sc1, _sc2 = st.columns(2)
                if _sc1.button("⏹ Log", type="primary",
                               use_container_width=True, key="sb_timer_stop"):
                    _hours = max(round(_elapsed / 3600 * 4) / 4, 0.25)
                    try:
                        from utils import database as _tdb
                        _tdb.add_time_entry(
                            st.session_state.timer_matter, _hours,
                            _tdesc.strip() or "Timer session",
                            _trate,
                        )
                        st.success(f"✅ {_hours:.2f}h logged!")
                    except Exception:
                        pass
                    st.session_state.timer_running = False
                    st.session_state.timer_start   = 0.0
                    st.rerun()
                if _sc2.button("✕ Discard", use_container_width=True, key="sb_timer_cancel"):
                    st.session_state.timer_running = False
                    st.session_state.timer_start   = 0.0
                    st.rerun()
            st.divider()

        # ── Rwanda Laws selector (AI tool pages only) ─────────────
        if tool_name and user and user.get("role") != "client":
            try:
                from utils import database as db
                st.markdown(
                    '<p style="font-size:0.75rem;font-weight:700;color:#1a2744;'
                    'text-transform:uppercase;letter-spacing:0.05em;margin-bottom:0.4rem">'
                    '⚖️ Rwanda Laws</p>',
                    unsafe_allow_html=True,
                )
                if "sidebar_selected_laws" not in st.session_state:
                    st.session_state.sidebar_selected_laws = {}

                _law_search = st.text_input(
                    "Search Rwanda laws",
                    placeholder="e.g. labour, land, company…",
                    key="sb_law_search",
                    label_visibility="collapsed",
                )
                _law_list = db.list_laws(search=_law_search if _law_search else None)
                if _law_list:
                    for _lw in _law_list[:8]:
                        _checked = _lw["id"] in st.session_state.sidebar_selected_laws
                        if st.checkbox(
                            f"{_lw['title'][:36]}{'…' if len(_lw['title']) > 36 else ''}",
                            value=_checked,
                            key=f"sb_law_{_lw['id']}",
                        ):
                            st.session_state.sidebar_selected_laws[_lw["id"]] = _lw["title"]
                        else:
                            st.session_state.sidebar_selected_laws.pop(_lw["id"], None)
                    if st.session_state.sidebar_selected_laws:
                        n = len(st.session_state.sidebar_selected_laws)
                        st.markdown(
                            f'<span style="background:#f0fdf4;color:#166534;font-size:0.73rem;'
                            f'font-weight:600;padding:0.15rem 0.55rem;border-radius:20px">'
                            f'⚖️ {n} law{"s" if n > 1 else ""} selected</span>',
                            unsafe_allow_html=True,
                        )
                elif _law_search:
                    st.caption("No matching laws.")
                else:
                    st.caption("Upload laws in ⚖️ Law Library first.")
                st.divider()
            except Exception:
                pass

        # ── Privacy notice ─────────────────────────────────────────
        st.markdown("**🔐 Privacy**")
        st.markdown("- Processed in memory only")
        st.markdown("- Not stored or trained on")
        st.markdown("- Files auto-deleted after session")
        st.divider()
        st.caption("⚠️ AI output does not replace qualified legal advice.")

    return api_key


def get_law_context_block() -> str:
    """Return formatted Rwanda law text for all sidebar-selected laws."""
    selected = st.session_state.get("sidebar_selected_laws", {})
    if not selected:
        return ""
    try:
        from utils import database as db
        parts = []
        for law_id, law_title in selected.items():
            try:
                text = db.get_law_text(law_id)
                if text:
                    truncated = text[:50_000]
                    note = "\n[truncated]" if len(text) > 50_000 else ""
                    parts.append(
                        f"── RWANDA LAW: {law_title} ──\n{truncated}{note}\n── END LAW ──"
                    )
            except Exception:
                pass
        return "\n\n".join(parts)
    except Exception:
        return ""


def _render_search_results(query: str) -> None:
    from utils import database as db
    q = query.lower()
    matter_hits, client_hits, doc_hits = [], [], []

    try:
        for m in db.list_matters()[:60]:
            if q in (m.get("title") or "").lower() or q in (m.get("ref") or "").lower():
                matter_hits.append(m)
    except Exception:
        pass

    try:
        for c in db.list_clients()[:60]:
            name = c.get("name") or c.get("company_name") or ""
            if q in name.lower():
                client_hits.append(c)
    except Exception:
        pass

    try:
        for d in db.list_documents()[:60]:
            if q in (d.get("name") or "").lower() or q in (d.get("file_name") or "").lower():
                doc_hits.append(d)
    except Exception:
        pass

    total = len(matter_hits) + len(client_hits) + len(doc_hits)
    if total == 0:
        st.caption("No matches found.")
        return

    for m in matter_hits[:3]:
        label = f"📁 {m.get('ref','')} {(m.get('title') or '')[:22]}"
        if st.button(label, key=f"srch_m_{m['id']}", use_container_width=True):
            st.session_state.selected_matter_id = m["id"]
            st.switch_page("pages/p_matters_list.py")

    for c in client_hits[:2]:
        label = f"🏢 {(c.get('name') or c.get('company_name') or '')[:28]}"
        if st.button(label, key=f"srch_c_{c['id']}", use_container_width=True):
            st.switch_page("pages/p_matters_list.py")

    for d in doc_hits[:2]:
        label = f"📄 {(d.get('name') or d.get('file_name') or '')[:28]}"
        if st.button(label, key=f"srch_d_{d['id']}", use_container_width=True):
            st.switch_page("pages/p_doc_library.py")

    if total > 7:
        st.caption(f"+{total - 7} more results")


def setup_page(section: str = "") -> str | None:
    """
    One-call page initialiser. Injects CSS and renders the sidebar.
    Does NOT enforce auth — call require_auth() separately in pages that need it.
    Returns the api_key (or None).
    """
    inject_css()
    return render_sidebar(section)
