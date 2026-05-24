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

        # ── Notifications badge ────────────────────────────────────
        if user:
            from utils import database as db
            unread = db.unread_notification_count()
            if unread > 0:
                st.markdown(f"🔔 **{unread} unread notification{'s' if unread > 1 else ''}**")
                if st.button("Mark all read", key="sb_mark_read", use_container_width=False):
                    db.mark_notifications_read()
                    st.rerun()
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


def setup_page(section: str = "") -> str | None:
    """
    One-call page initialiser. Injects CSS and renders the sidebar.
    Does NOT enforce auth — call require_auth() separately in pages that need it.
    Returns the api_key (or None).
    """
    inject_css()
    return render_sidebar(section)
