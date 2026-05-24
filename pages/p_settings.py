import streamlit as st
from utils.shared.sidebar import setup_page
from utils.shared.styles import slim_header, section
from utils.auth import require_auth, reset_password
import utils.database as db

setup_page()
user = require_auth()

slim_header("⚙️", "Settings", f"Profile, organisation, and security settings")

tabs = ["👤 Profile", "🤖 AI Settings", "🔒 Security"]
if user["role"] in ("admin", "lawyer"):
    tabs.insert(1, "🏛️ Organisation")

tab_objs = st.tabs(tabs)
tab_map = {name: tab for name, tab in zip(tabs, tab_objs)}

# ── Profile ───────────────────────────────────────────────────────
with tab_map["👤 Profile"]:
    section("👤 Your Profile")

    ROLE_ICONS = {"admin": "🛡️", "lawyer": "⚖️", "staff": "👤", "client": "🏢", "intern": "🎓"}
    icon = ROLE_ICONS.get(user["role"], "👤")

    c1, c2 = st.columns([1, 3])
    c1.markdown(
        f'<div style="width:72px;height:72px;background:#1e3a5f;border-radius:50%;'
        f'display:flex;align-items:center;justify-content:center;font-size:1.8rem">'
        f'{icon}</div>',
        unsafe_allow_html=True,
    )
    with c2:
        st.markdown(f"**{user['full_name']}**")
        st.caption(f"{user.get('title') or user['role'].title()} · {user['organization_name']}")

    st.markdown("<br>", unsafe_allow_html=True)
    with st.form("profile_form"):
        c1, c2 = st.columns(2)
        new_name  = c1.text_input("Full Name *", value=user.get("full_name", ""), key="pf_name")
        new_title = c2.text_input("Title / Role", value=user.get("title", "") or "", key="pf_title",
                                   placeholder="e.g. Senior Associate")
        if st.form_submit_button("💾 Save Profile", type="primary"):
            if not new_name.strip():
                st.warning("Name is required.")
            else:
                db.get_db().table("profiles").update({
                    "full_name": new_name.strip(),
                    "title": new_title.strip() or None,
                }).eq("id", user["id"]).execute()
                st.session_state["user"]["full_name"] = new_name.strip()
                st.session_state["user"]["title"] = new_title.strip() or None
                st.success("✅ Profile updated.")
                st.rerun()

# ── Organisation ──────────────────────────────────────────────────
if "🏛️ Organisation" in tab_map:
    with tab_map["🏛️ Organisation"]:
        section("🏛️ Organisation Details")
        org_resp = (
            db.get_db().table("organizations")
            .select("*")
            .eq("id", user["organization_id"])
            .maybe_single()
            .execute()
        )
        org = org_resp.data or {}

        with st.form("settings_org_form"):
            c1, c2 = st.columns(2)
            org_name  = c1.text_input("Firm Name",  value=org.get("name", ""),    key="so_name")
            org_email = c2.text_input("Email",       value=org.get("email", ""),   key="so_email")
            org_phone = c1.text_input("Phone",       value=org.get("phone", ""),   key="so_phone")
            org_addr  = c2.text_input("Address",     value=org.get("address", ""), key="so_addr")
            if st.form_submit_button("💾 Save Changes", type="primary"):
                db.get_db().table("organizations").update({
                    "name": org_name, "email": org_email,
                    "phone": org_phone, "address": org_addr,
                }).eq("id", user["organization_id"]).execute()
                st.session_state["user"]["organization_name"] = org_name
                st.success("✅ Organisation details updated.")
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.metric("Subscription Plan",   (org.get("subscription_plan") or "starter").title())
        c2.metric("Subscription Status", (org.get("subscription_status") or "active").title())

# ── AI Settings ───────────────────────────────────────────────────
with tab_map["🤖 AI Settings"]:
    section("🤖 AI Configuration")
    st.markdown("**Current AI Provider:** Anthropic Claude Opus 4.7")
    try:
        import os as _os
        _ = st.secrets.get("ANTHROPIC_API_KEY") or _os.environ.get("ANTHROPIC_API_KEY") or ""
        if not _:
            raise KeyError
        st.success("✅ API key loaded from secrets")
    except Exception:
        st.warning("⚠️ API key not found in secrets.toml — enter it in the sidebar to use AI tools")

    st.info(
        "The API key is stored in `.streamlit/secrets.toml` and is never committed to version control. "
        "On Railway/Streamlit Cloud, add it via the environment variables / secrets panel."
    )

# ── Security ──────────────────────────────────────────────────────
with tab_map["🔒 Security"]:
    section("🔑 Change Password")
    with st.form("change_pw_form"):
        new_pw1 = st.text_input("New Password", type="password", key="cpw1")
        new_pw2 = st.text_input("Confirm New Password", type="password", key="cpw2")
        if st.form_submit_button("Update Password", type="primary"):
            if not new_pw1:
                st.warning("Enter a new password.")
            elif len(new_pw1) < 8:
                st.warning("Password must be at least 8 characters.")
            elif new_pw1 != new_pw2:
                st.warning("Passwords do not match.")
            else:
                result = reset_password(user["id"], new_pw1)
                if result["ok"]:
                    st.success("✅ Password updated successfully.")
                else:
                    st.error(f"❌ {result['error']}")

    st.markdown("<br>", unsafe_allow_html=True)
    section("🔒 Security Status")
    for label, status in [
        ("API Key",       "Stored in secrets.toml — not committed to repo"),
        ("File Processing", "In-memory only — files auto-deleted after session"),
        ("AI Training",   "Your data is never used to train AI models"),
        ("Database",      "Supabase with organisation-level tenant isolation"),
    ]:
        st.markdown(
            f'<div style="display:flex;justify-content:space-between;padding:.5rem 0;'
            f'border-bottom:1px solid #e2e8f0">'
            f'<div><strong>{label}</strong><br><small style="color:#64748b">{status}</small></div>'
            f'<span style="color:#16a34a;font-size:1.2rem">✓</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
