import streamlit as st
from utils.shared.styles import inject_css

inject_css()

st.markdown(
    """
    <style>
    .login-wrap{max-width:460px;margin:3rem auto;padding:2.5rem;
        background:#fff;border-radius:12px;box-shadow:0 4px 24px rgba(0,0,0,.08)}
    .login-logo{font-size:2.5rem;text-align:center;margin-bottom:.5rem}
    .login-title{text-align:center;font-size:1.6rem;font-weight:700;color:#1e3a5f;margin-bottom:.25rem}
    .login-sub{text-align:center;color:#64748b;font-size:.9rem;margin-bottom:1.5rem}
    </style>
    """,
    unsafe_allow_html=True,
)

col = st.columns([1, 2, 1])[1]

with col:
    st.markdown('<div class="login-wrap">', unsafe_allow_html=True)
    st.markdown('<div class="login-logo">⚖️</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-title">ProofDoc AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="login-sub">Secure Legal Workspace</div>', unsafe_allow_html=True)

    tab_login, tab_register = st.tabs(["Sign In", "Register New Firm"])

    # ── Sign In ────────────────────────────────────────────────────
    with tab_login:
        with st.form("login_form"):
            email    = st.text_input("Email", placeholder="you@yourfirm.com", key="li_email")
            password = st.text_input("Password", type="password", key="li_pw")
            submitted = st.form_submit_button("Sign In", type="primary", use_container_width=True)

        if submitted:
            if not email or not password:
                st.warning("Please enter your email and password.")
            else:
                from utils.auth import sign_in
                with st.spinner("Signing in…"):
                    result = sign_in(email.strip(), password)
                if result["ok"]:
                    st.success("✅ Signed in!")
                    st.rerun()
                else:
                    st.error(f"❌ {result['error']}")

        st.markdown("<br>", unsafe_allow_html=True)
        st.caption("Forgot your password? Contact your firm administrator to reset it.")

    # ── Register New Firm ──────────────────────────────────────────
    with tab_register:
        st.markdown("Create an account for your law firm. You'll be the **admin** user.")
        with st.form("register_form"):
            firm_name  = st.text_input("Law Firm Name *", placeholder="e.g. Nkurunziza & Associates", key="reg_firm")
            full_name  = st.text_input("Your Full Name *", placeholder="e.g. Marie Uwimana", key="reg_name")
            reg_email  = st.text_input("Your Email *", placeholder="admin@yourfirm.com", key="reg_email")
            reg_pw     = st.text_input("Password *", type="password",
                                        help="Minimum 8 characters", key="reg_pw")
            reg_pw2    = st.text_input("Confirm Password *", type="password", key="reg_pw2")
            submitted2 = st.form_submit_button("Create Firm Account", type="primary", use_container_width=True)

        if submitted2:
            errors = []
            if not firm_name.strip():
                errors.append("Firm name is required.")
            if not full_name.strip():
                errors.append("Your name is required.")
            if not reg_email.strip():
                errors.append("Email is required.")
            if len(reg_pw) < 8:
                errors.append("Password must be at least 8 characters.")
            if reg_pw != reg_pw2:
                errors.append("Passwords do not match.")
            if errors:
                for e in errors:
                    st.warning(e)
            else:
                from utils.auth import register_firm
                with st.spinner("Setting up your firm account…"):
                    result = register_firm(firm_name.strip(), reg_email.strip(),
                                           reg_pw, full_name.strip())
                if result["ok"]:
                    st.success("✅ Firm account created! You are now signed in.")
                    st.rerun()
                else:
                    st.error(f"❌ {result['error']}")

    st.markdown('</div>', unsafe_allow_html=True)
