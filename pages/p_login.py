import streamlit as st
from utils.shared.styles import inject_css

inject_css()

st.markdown(
    """
    <style>
    [data-testid="stAppViewContainer"]{background:#f1f5f9}
    .login-box{max-width:420px;margin:3rem auto;background:#fff;
        border-radius:14px;box-shadow:0 4px 24px rgba(0,0,0,.08);padding:2.5rem}
    </style>
    """,
    unsafe_allow_html=True,
)

_, col, _ = st.columns([1, 2, 1])

with col:
    st.markdown("## ⚖️ eLawFirm")
    st.markdown("##### Secure Legal Workspace")
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
