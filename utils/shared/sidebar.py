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

        # ── Privacy notice ─────────────────────────────────────────
        st.markdown("**🔐 Privacy**")
        st.markdown("- Processed in memory only")
        st.markdown("- Not stored or trained on")
        st.markdown("- Files auto-deleted after session")
        st.divider()
        st.caption("⚠️ AI output does not replace qualified legal advice.")

    return api_key


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
