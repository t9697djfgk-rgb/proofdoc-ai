import streamlit as st
from utils.shared.styles import inject_css

inject_css()

st.markdown(
    """
    <style>
    [data-testid="stSidebarNav"]{display:none}
    [data-testid="collapsedControl"]{display:none}
    section[data-testid="stSidebar"]{display:none}
    .login-hero{text-align:center;padding:2.5rem 0 1.5rem}
    .login-brand{font-size:2.4rem;font-weight:800;letter-spacing:-0.03em;
        background:linear-gradient(135deg,#4f7cf7,#d4a853);
        -webkit-background-clip:text;-webkit-text-fill-color:transparent;
        background-clip:text}
    .login-tagline{color:#8a93ab;font-size:.9rem;letter-spacing:.08em;
        text-transform:uppercase;margin-top:.3rem}
    </style>
    """,
    unsafe_allow_html=True,
)

_, col, _ = st.columns([1, 2, 1])

with col:
    st.markdown(
        '<div class="login-hero">'
        '<div class="login-brand">⚖ eLawFirm</div>'
        '<div class="login-tagline">Secure Legal Workspace</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    tab_login, tab_register = st.tabs(["Sign In", "Register New Firm"])

    # ── Sign In ────────────────────────────────────────────────────
    with tab_login:
        email    = st.text_input("Email", placeholder="you@yourfirm.com", key="li_email")
        password = st.text_input("Password", type="password", key="li_pw")

        if st.button("Sign In →", type="primary", use_container_width=True, key="li_btn"):
            if not email.strip() or not password:
                st.warning("Enter your email and password.")
            else:
                with st.spinner("Signing in…"):
                    from utils.auth import sign_in
                    result = sign_in(email.strip(), password)
                if result["ok"]:
                    st.rerun()
                else:
                    st.error(f"❌ {result['error']}")

        st.caption("Forgot your password? Ask your firm administrator to reset it.")

    # ── Register New Firm ──────────────────────────────────────────
    with tab_register:
        st.markdown("Create a new firm account. You'll be the **admin**.")
        firm_name = st.text_input("Law Firm Name *", placeholder="e.g. Nkurunziza & Associates", key="reg_firm")
        full_name = st.text_input("Your Full Name *", placeholder="e.g. Marie Uwimana", key="reg_name")
        reg_email = st.text_input("Email *", placeholder="admin@yourfirm.com", key="reg_email")
        reg_pw    = st.text_input("Password *", type="password", help="Minimum 8 characters", key="reg_pw")
        reg_pw2   = st.text_input("Confirm Password *", type="password", key="reg_pw2")

        if st.button("Create Firm Account →", type="primary", use_container_width=True, key="reg_btn"):
            errors = []
            if not firm_name.strip(): errors.append("Firm name is required.")
            if not full_name.strip(): errors.append("Your name is required.")
            if not reg_email.strip(): errors.append("Email is required.")
            if len(reg_pw) < 8:       errors.append("Password must be at least 8 characters.")
            if reg_pw != reg_pw2:     errors.append("Passwords do not match.")
            if errors:
                for e in errors:
                    st.warning(e)
            else:
                with st.spinner("Creating your firm account…"):
                    from utils.auth import register_firm
                    result = register_firm(firm_name.strip(), reg_email.strip(),
                                           reg_pw, full_name.strip())
                if result["ok"]:
                    st.rerun()
                else:
                    st.error(f"❌ {result['error']}")
