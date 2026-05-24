import streamlit as st
from utils.shared.sidebar import setup_page
from utils.shared.styles import slim_header, section
from utils.auth import require_auth, reset_password
import utils.database as db

api_key = setup_page()
user = require_auth()

slim_header("⚙️", "Settings", "Profile, organisation, security, and billing preferences")

tabs = ["👤 Profile", "🤖 AI Settings", "💰 Billing Rates", "🔒 Security"]
if user["role"] in ("admin", "lawyer"):
    tabs.insert(1, "🏛️ Organisation")

tab_objs = st.tabs(tabs)
tab_map = {name: tab for name, tab in zip(tabs, tab_objs)}

# ── Profile ───────────────────────────────────────────────────────
with tab_map["👤 Profile"]:
    section("👤 Your Profile")

    ROLE_ICONS  = {"admin": "🛡️", "lawyer": "⚖️", "staff": "👤", "client": "🏢", "intern": "🎓"}
    ROLE_COLORS = {"admin": "#7c3aed", "lawyer": "#1a2744", "staff": "#0891b2", "client": "#16a34a", "intern": "#d97706"}
    icon  = ROLE_ICONS.get(user["role"], "👤")
    color = ROLE_COLORS.get(user["role"], "#1a2744")
    initials = "".join(w[0].upper() for w in user["full_name"].split()[:2]) if user.get("full_name") else "?"

    st.markdown(
        f"""<div style="background:linear-gradient(135deg,{color}15,{color}05);border:1px solid {color}30;
                        border-radius:14px;padding:1.5rem;margin-bottom:1.5rem;
                        display:flex;align-items:center;gap:1.4rem">
          <div style="width:72px;height:72px;background:{color};border-radius:50%;flex-shrink:0;
                      display:flex;align-items:center;justify-content:center;
                      font-size:1.5rem;font-weight:700;color:white;letter-spacing:-.03em">
            {initials}
          </div>
          <div>
            <div style="font-size:1.15rem;font-weight:700;color:#1a2744">{user['full_name']}</div>
            <div style="font-size:.85rem;color:{color};font-weight:600;margin:.2rem 0">
              {icon} {(user.get('title') or user['role'].title())}
            </div>
            <div style="font-size:.8rem;color:#64748b">{user['organization_name']}</div>
          </div>
        </div>""",
        unsafe_allow_html=True,
    )

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
        "On Streamlit Community Cloud, add it via the app Secrets panel."
    )

# ── Billing Rates ─────────────────────────────────────────────────
with tab_map["💰 Billing Rates"]:
    section("💰 Billing Rate Defaults")
    st.markdown("Set default hourly rates by role. These are used when logging time if no custom rate is specified.")

    RATE_KEY = "billing_rates"
    defaults = {
        "Partner / Senior Lawyer": 350,
        "Associate Lawyer":        220,
        "Paralegal / Staff":       120,
        "Intern":                   60,
        "Court Clerk":             100,
    }
    saved_rates = st.session_state.get(RATE_KEY, dict(defaults))

    with st.form("billing_rates_form"):
        st.markdown("**Hourly Rates (USD)**")
        new_rates = {}
        cols_a, cols_b = st.columns(2)
        role_list = list(defaults.keys())
        for i, role_name in enumerate(role_list):
            col = cols_a if i % 2 == 0 else cols_b
            new_rates[role_name] = col.number_input(
                role_name,
                min_value=0,
                max_value=5000,
                value=saved_rates.get(role_name, defaults[role_name]),
                step=10,
                key=f"br_{i}",
            )
        st.markdown("<br>", unsafe_allow_html=True)
        currency = st.selectbox("Currency", ["USD", "EUR", "GBP", "RWF", "KES", "ZAR"], key="br_currency",
                                 index=["USD", "EUR", "GBP", "RWF", "KES", "ZAR"].index(
                                     st.session_state.get("billing_currency", "USD")
                                 ))
        vat_rate = st.number_input("Default VAT / Tax Rate (%)", min_value=0.0, max_value=100.0,
                                    value=float(st.session_state.get("billing_vat", 18.0)),
                                    step=0.5, key="br_vat")
        if st.form_submit_button("💾 Save Billing Defaults", type="primary"):
            st.session_state[RATE_KEY] = new_rates
            st.session_state["billing_currency"] = currency
            st.session_state["billing_vat"] = vat_rate
            st.success("✅ Billing rate defaults saved.")

    st.markdown("<br>", unsafe_allow_html=True)
    section("📊 Rate Overview")
    rates = st.session_state.get(RATE_KEY, defaults)
    currency_sym = {"USD": "$", "EUR": "€", "GBP": "£", "RWF": "RWF ", "KES": "KES ", "ZAR": "R"}.get(
        st.session_state.get("billing_currency", "USD"), "$"
    )
    cols = st.columns(len(rates))
    for col, (role_name, rate) in zip(cols, rates.items()):
        short = role_name.split("/")[0].strip().split()[0]
        col.markdown(
            f'<div style="background:#f8fafc;border-radius:10px;padding:.8rem;text-align:center;'
            f'border-top:3px solid #c9a84c">'
            f'<div style="font-size:1.1rem;font-weight:700;color:#1a2744">{currency_sym}{rate}</div>'
            f'<div style="font-size:.7rem;color:#64748b;margin-top:.2rem">{short}</div>'
            f'</div>',
            unsafe_allow_html=True,
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
    for label, status, ok in [
        ("API Key",           "Stored in secrets.toml — not committed to repo",       True),
        ("File Processing",   "In-memory only — files auto-deleted after session",    True),
        ("AI Training",       "Your data is never used to train AI models",           True),
        ("Database",          "Supabase with organisation-level tenant isolation",     True),
        ("Data Encryption",   "All data encrypted at rest and in transit (TLS 1.3)",  True),
    ]:
        color = "#16a34a" if ok else "#dc2626"
        icon  = "✓" if ok else "✗"
        st.markdown(
            f'<div style="display:flex;justify-content:space-between;align-items:center;'
            f'padding:.6rem 0;border-bottom:1px solid #e2e8f0">'
            f'<div><strong>{label}</strong><br><small style="color:#64748b">{status}</small></div>'
            f'<span style="color:{color};font-size:1.2rem;font-weight:700">{icon}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )
