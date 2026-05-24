import streamlit as st
from utils.auth import sign_in, register_firm

# ── Debug mode (?debug=1) ─────────────────────────────────────────────────────
if st.query_params.get("debug") == "1":
    import os, sys
    st.title("Railway Diagnostics")
    for key in ["SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_SERVICE_KEY", "ANTHROPIC_API_KEY"]:
        val = os.environ.get(key, "").strip()
        if val:
            st.success(f"✅ {key}: {val[:12]}...{val[-6:]}")
        else:
            st.error(f"❌ {key}: NOT SET")
    st.markdown("---")
    try:
        result = sign_in("legalexpertschambers@gmail.com", "Nzeyimana@123")
        if result["ok"]:
            st.success(f"✅ Login OK — role: {result['user']['role']}, org: {result['user']['organization_name']}")
        else:
            st.error(f"❌ Login failed: {result['error']}")
    except Exception as e:
        st.error(f"❌ Exception: {e}")
    st.caption(f"Python {sys.version} · Streamlit {st.__version__}")
    st.stop()

# ── Login page ────────────────────────────────────────────────────────────────
st.markdown("<h2 style='text-align:center;margin-top:3rem'>⚖️ eLawFirm — Sign In</h2>",
            unsafe_allow_html=True)

col_l, col_m, col_r = st.columns([1, 2, 1])
with col_m:

    # Error from previous attempt shown FIRST
    _err = st.session_state.pop("_login_err", None)
    if _err:
        st.error(_err)

    email    = st.text_input("Email address", placeholder="you@yourfirm.com", key="li_email")
    password = st.text_input("Password", type="password", key="li_pw")

    if st.button("Sign In →", type="primary", use_container_width=True, key="li_btn"):
        if not email.strip() or not password:
            st.session_state["_login_err"] = "Please enter your email and password."
            st.rerun()
        else:
            try:
                result = sign_in(email.strip(), password)
            except Exception as exc:
                result = {"ok": False, "error": str(exc)}
            if result["ok"]:
                st.rerun()
            else:
                st.session_state["_login_err"] = result["error"]
                st.rerun()

    st.caption("Forgot your password? Ask your firm administrator to reset it.")
    st.markdown("---")

    with st.expander("➕ Create a new firm account"):
        _rerr = st.session_state.pop("_reg_err", None)
        if _rerr:
            st.error(_rerr)

        firm_name = st.text_input("Law Firm Name", key="reg_firm")
        full_name = st.text_input("Your Full Name", key="reg_name")
        reg_email = st.text_input("Email",          key="reg_email")
        c1, c2    = st.columns(2)
        with c1:
            reg_pw  = st.text_input("Password",         type="password", key="reg_pw")
        with c2:
            reg_pw2 = st.text_input("Confirm password", type="password", key="reg_pw2")

        if st.button("Create Firm Account →", type="primary", use_container_width=True, key="reg_btn"):
            errs = []
            if not firm_name.strip(): errs.append("Firm name required.")
            if not full_name.strip(): errs.append("Your name required.")
            if not reg_email.strip(): errs.append("Email required.")
            if len(reg_pw) < 8:       errs.append("Password min 8 chars.")
            if reg_pw != reg_pw2:     errs.append("Passwords don't match.")
            if errs:
                st.session_state["_reg_err"] = " · ".join(errs)
                st.rerun()
            try:
                result = register_firm(firm_name.strip(), reg_email.strip(), reg_pw, full_name.strip())
            except Exception as exc:
                result = {"ok": False, "error": str(exc)}
            if result["ok"]:
                st.rerun()
            else:
                st.session_state["_reg_err"] = result["error"]
                st.rerun()

    st.caption("⚠️ AI output does not replace qualified legal advice.")
