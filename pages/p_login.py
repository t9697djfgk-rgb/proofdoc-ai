import streamlit as st
from utils.shared.styles import inject_css

inject_css()

st.markdown(
    """
    <style>
    /* ── Hide Streamlit chrome on login ── */
    [data-testid="stSidebarNav"]  { display:none !important; }
    [data-testid="collapsedControl"]{ display:none !important; }
    section[data-testid="stSidebar"]{ display:none !important; }
    header[data-testid="stHeader"]  { display:none !important; }
    [data-testid="stAppViewBlockContainer"]{ max-width:100% !important; padding:0 !important; }

    /* ── Full-screen layout ── */
    .login-wrap {
        display:flex; min-height:100vh;
        font-family:'Inter',sans-serif;
    }

    /* ════════════════════════════════
       LEFT HERO PANEL
    ════════════════════════════════ */
    .login-hero {
        flex: 1.1;
        background: linear-gradient(145deg, #0f1a2e 0%, #1a2744 55%, #25356e 100%);
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        padding: 3rem 3.5rem;
        position: relative;
        overflow: hidden;
    }

    /* Animated geometric background */
    .login-hero::before {
        content:'';
        position:absolute; inset:0;
        background:
            radial-gradient(ellipse at 20% 30%, rgba(201,168,76,0.06) 0%, transparent 55%),
            radial-gradient(ellipse at 80% 70%, rgba(79,100,200,0.08) 0%, transparent 55%);
        animation: heroGlow 8s ease-in-out infinite alternate;
    }
    @keyframes heroGlow {
        from { opacity:0.6; transform:scale(1); }
        to   { opacity:1;   transform:scale(1.04); }
    }

    /* Grid dot pattern */
    .login-hero::after {
        content:'';
        position:absolute; inset:0;
        background-image: radial-gradient(rgba(255,255,255,0.04) 1.5px, transparent 1.5px);
        background-size: 32px 32px;
        pointer-events:none;
    }

    /* Brand mark */
    .hero-brand {
        position:relative; z-index:2;
        animation: fadeInDown 0.6s ease both;
    }
    @keyframes fadeInDown {
        from { opacity:0; transform:translateY(-16px); }
        to   { opacity:1; transform:translateY(0); }
    }
    .hero-logo {
        font-size:1.6rem; font-weight:800; letter-spacing:-0.02em;
        color:#ffffff;
        display:flex; align-items:center; gap:0.5rem;
    }
    .hero-logo-icon {
        width:40px; height:40px;
        background:linear-gradient(135deg, #c9a84c, #e8c97a);
        border-radius:10px;
        display:inline-flex; align-items:center; justify-content:center;
        font-size:1.3rem;
        box-shadow: 0 4px 16px rgba(201,168,76,0.35);
    }
    .hero-tagline {
        margin-top:0.35rem;
        font-size:0.78rem; color:rgba(255,255,255,0.45);
        text-transform:uppercase; letter-spacing:0.1em;
    }

    /* Central visual */
    .hero-visual {
        position:relative; z-index:2;
        display:flex; flex-direction:column;
        align-items:center; justify-content:center;
        flex:1; padding:2rem 0;
        animation: fadeInUp 0.7s 0.15s ease both;
    }
    @keyframes fadeInUp {
        from { opacity:0; transform:translateY(20px); }
        to   { opacity:1; transform:translateY(0); }
    }

    /* SVG scales of justice */
    .scales-svg {
        width:160px; height:160px;
        filter: drop-shadow(0 12px 32px rgba(201,168,76,0.25));
        animation: floatScales 5s ease-in-out infinite;
    }
    @keyframes floatScales {
        0%,100% { transform:translateY(0); }
        50%      { transform:translateY(-10px); }
    }

    .hero-headline {
        font-family:'Playfair Display',Georgia,serif;
        font-size:2.1rem; font-weight:700; color:#ffffff;
        line-height:1.22; text-align:center;
        margin: 1.4rem 0 0.7rem;
        letter-spacing:-0.01em;
    }
    .hero-headline em {
        font-style:italic;
        background:linear-gradient(90deg,#c9a84c,#e8c97a,#c9a84c);
        background-size:200% auto;
        -webkit-background-clip:text; -webkit-text-fill-color:transparent;
        background-clip:text;
        animation: shimmerText 3.5s linear infinite;
    }
    @keyframes shimmerText {
        from { background-position:200% center; }
        to   { background-position:-200% center; }
    }
    .hero-sub {
        font-size:0.9rem; color:rgba(255,255,255,0.55);
        text-align:center; max-width:320px; line-height:1.65;
        margin:0 auto;
    }

    /* Animated stats row */
    .hero-stats {
        display:flex; gap:2rem; margin-top:2rem;
        position:relative; z-index:2;
        justify-content:center;
        animation: fadeIn 0.8s 0.4s ease both;
    }
    @keyframes fadeIn { from{opacity:0} to{opacity:1} }
    .hero-stat {
        text-align:center;
    }
    .hero-stat .hs-n {
        font-family:'Playfair Display',serif;
        font-size:1.5rem; font-weight:700; color:#c9a84c;
        line-height:1;
    }
    .hero-stat .hs-l {
        font-size:0.7rem; color:rgba(255,255,255,0.4);
        text-transform:uppercase; letter-spacing:0.08em;
        margin-top:0.2rem;
    }

    /* Features list */
    .hero-features {
        position:relative; z-index:2;
        display:flex; flex-direction:column; gap:0.6rem;
        animation: fadeInUp 0.7s 0.3s ease both;
    }
    .hero-feat {
        display:flex; align-items:center; gap:0.7rem;
        font-size:0.83rem; color:rgba(255,255,255,0.65);
    }
    .hero-feat-dot {
        width:6px; height:6px; border-radius:50%;
        background: var(--gold,#c9a84c);
        flex-shrink:0;
    }

    /* ════════════════════════════════
       RIGHT FORM PANEL
    ════════════════════════════════ */
    .login-form-panel {
        flex:0.9;
        background:#faf9f6;
        display:flex; flex-direction:column;
        align-items:center; justify-content:center;
        padding:3rem 3.5rem;
        position:relative;
    }
    .login-form-panel::before {
        content:'';
        position:absolute; top:0; left:0; width:2px; height:100%;
        background:linear-gradient(180deg,transparent,rgba(201,168,76,0.4),transparent);
    }
    .form-header {
        width:100%; max-width:380px;
        margin-bottom:1.8rem;
        animation: fadeInUp 0.5s 0.1s ease both;
    }
    .form-title {
        font-family:'Playfair Display',Georgia,serif;
        font-size:1.75rem; font-weight:700;
        color:#1a2744; margin:0 0 0.35rem; letter-spacing:-0.01em;
    }
    .form-subtitle {
        font-size:0.87rem; color:#6b7280; margin:0;
    }
    .form-box {
        width:100%; max-width:380px;
        animation: scaleIn 0.45s 0.2s ease both;
    }
    @keyframes scaleIn {
        from { opacity:0; transform:scale(0.97); }
        to   { opacity:1; transform:scale(1); }
    }
    .form-divider {
        display:flex; align-items:center; gap:0.75rem;
        margin:1.2rem 0;
    }
    .form-divider hr { flex:1; border:none; border-top:1px solid #e5e7eb; }
    .form-divider span { font-size:0.75rem; color:#9ca3af; white-space:nowrap; }

    /* Footer */
    .login-footer {
        position:absolute; bottom:1.4rem;
        font-size:0.72rem; color:#9ca3af; text-align:center;
    }

    /* Make Streamlit tabs look nice on this page */
    .form-box [data-baseweb="tab-list"] {
        background:#f0ede6 !important;
        border-radius:8px !important;
        padding:3px !important;
        border:none !important;
        gap:2px !important;
    }
    .form-box [data-baseweb="tab"] {
        border-radius:6px !important;
        border:none !important;
        padding:0.45rem 1rem !important;
        font-size:0.82rem !important;
        font-weight:500 !important;
        color:#6b7280 !important;
        border-bottom:none !important;
        margin:0 !important;
    }
    .form-box [aria-selected="true"][data-baseweb="tab"] {
        background:#ffffff !important;
        color:#1a2744 !important;
        font-weight:600 !important;
        box-shadow:0 1px 4px rgba(0,0,0,0.1) !important;
        border-bottom:none !important;
    }
    </style>

    <div class="login-wrap">

      <!-- LEFT HERO -->
      <div class="login-hero">
        <div class="hero-brand">
          <div class="hero-logo">
            <span class="hero-logo-icon">⚖</span>
            eLawFirm
          </div>
          <div class="hero-tagline">Intelligent Legal Platform</div>
        </div>

        <div class="hero-visual">
          <!-- Scales of Justice SVG -->
          <svg class="scales-svg" viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
            <!-- Pole -->
            <rect x="98" y="30" width="4" height="130" fill="rgba(201,168,76,0.7)" rx="2"/>
            <!-- Base -->
            <rect x="60" y="155" width="80" height="8" fill="rgba(201,168,76,0.5)" rx="4"/>
            <rect x="75" y="163" width="50" height="5" fill="rgba(201,168,76,0.3)" rx="2.5"/>
            <!-- Top crossbar -->
            <rect x="30" y="52" width="140" height="4" fill="rgba(201,168,76,0.6)" rx="2"/>
            <!-- Left chain -->
            <line x1="42" y1="56" x2="38" y2="90" stroke="rgba(201,168,76,0.5)" stroke-width="1.5" stroke-dasharray="4 3"/>
            <!-- Right chain -->
            <line x1="158" y1="56" x2="162" y2="90" stroke="rgba(201,168,76,0.5)" stroke-width="1.5" stroke-dasharray="4 3"/>
            <!-- Left pan -->
            <ellipse cx="36" cy="93" rx="20" ry="6" fill="rgba(201,168,76,0.25)" stroke="rgba(201,168,76,0.6)" stroke-width="1.5"/>
            <!-- Right pan -->
            <ellipse cx="164" cy="93" rx="20" ry="6" fill="rgba(201,168,76,0.25)" stroke="rgba(201,168,76,0.6)" stroke-width="1.5"/>
            <!-- Circuit dots — tech layer -->
            <circle cx="40"  cy="130" r="3" fill="rgba(79,120,220,0.6)"/>
            <circle cx="160" cy="130" r="3" fill="rgba(79,120,220,0.6)"/>
            <circle cx="100" cy="20"  r="4" fill="rgba(201,168,76,0.8)"/>
            <circle cx="30"  cy="52"  r="3" fill="rgba(201,168,76,0.6)"/>
            <circle cx="170" cy="52"  r="3" fill="rgba(201,168,76,0.6)"/>
            <!-- Circuit lines -->
            <line x1="40" y1="130" x2="65"  y2="130" stroke="rgba(79,120,220,0.3)" stroke-width="1"/>
            <line x1="65" y1="130" x2="65"  y2="145" stroke="rgba(79,120,220,0.3)" stroke-width="1"/>
            <line x1="160" y1="130" x2="135" y2="130" stroke="rgba(79,120,220,0.3)" stroke-width="1"/>
            <line x1="135" y1="130" x2="135" y2="145" stroke="rgba(79,120,220,0.3)" stroke-width="1"/>
            <!-- Glow halos -->
            <circle cx="100" cy="100" r="70" stroke="rgba(201,168,76,0.05)" stroke-width="1" fill="none"/>
            <circle cx="100" cy="100" r="88" stroke="rgba(79,120,220,0.04)" stroke-width="1" fill="none"/>
          </svg>

          <h2 class="hero-headline">
            Where <em>Justice</em><br>Meets Intelligence
          </h2>
          <p class="hero-sub">
            AI-powered legal tools built for professionals who demand precision, speed, and confidentiality.
          </p>
        </div>

        <div style="position:relative;z-index:2;display:flex;flex-direction:column;gap:1.5rem">
          <div class="hero-stats">
            <div class="hero-stat"><div class="hs-n">5+</div><div class="hs-l">AI Tools</div></div>
            <div class="hero-stat"><div class="hs-n">100%</div><div class="hs-l">Confidential</div></div>
            <div class="hero-stat"><div class="hs-n">5 Roles</div><div class="hs-l">Access Levels</div></div>
          </div>
          <div class="hero-features">
            <div class="hero-feat"><div class="hero-feat-dot"></div>Document drafting &amp; clause library</div>
            <div class="hero-feat"><div class="hero-feat-dot"></div>AI legal research with jurisdiction awareness</div>
            <div class="hero-feat"><div class="hero-feat-dot"></div>Matter management &amp; client portal</div>
            <div class="hero-feat"><div class="hero-feat-dot"></div>PDF-to-Word conversion &amp; document processing</div>
          </div>
        </div>
      </div>

      <!-- RIGHT FORM (rendered by Streamlit below) -->
      <div class="login-form-panel">
        <div class="form-header">
          <h1 class="form-title">Welcome back</h1>
          <p class="form-subtitle">Sign in to your firm workspace, or create a new one.</p>
        </div>
        <div class="form-box" id="st-login-form">
    """,
    unsafe_allow_html=True,
)

# ── Streamlit form rendered inside .form-box ────────────────────────────────
tab_login, tab_register = st.tabs(["Sign In", "Register New Firm"])

with tab_login:
    email    = st.text_input("Email address", placeholder="you@yourfirm.com", key="li_email")
    password = st.text_input("Password", type="password", key="li_pw")

    if st.button("Sign In →", type="primary", use_container_width=True, key="li_btn"):
        if not email.strip() or not password:
            st.warning("Please enter both email and password.")
        else:
            with st.spinner("Signing in…"):
                from utils.auth import sign_in
                result = sign_in(email.strip(), password)
            if result["ok"]:
                st.rerun()
            else:
                st.error(f"❌ {result['error']}")

    st.caption("Forgot your password? Ask your firm administrator to reset it.")

with tab_register:
    st.markdown(
        "<p style='font-size:0.83rem;color:#6b7280;margin:0 0 .9rem'>Create a new firm account. You will be the <strong>admin</strong>.</p>",
        unsafe_allow_html=True,
    )
    firm_name = st.text_input("Law Firm Name", placeholder="e.g. Nkurunziza & Associates", key="reg_firm")
    full_name = st.text_input("Your Full Name", placeholder="e.g. Marie Uwimana", key="reg_name")
    reg_email = st.text_input("Email", placeholder="admin@yourfirm.com", key="reg_email")
    c1, c2 = st.columns(2)
    with c1:
        reg_pw  = st.text_input("Password", type="password", help="Min 8 characters", key="reg_pw")
    with c2:
        reg_pw2 = st.text_input("Confirm", type="password", key="reg_pw2")

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

st.markdown(
    """
        </div>
        <div class="login-footer">
          ⚖ eLawFirm &nbsp;·&nbsp; AI output does not replace qualified legal advice
        </div>
      </div>

    </div>
    """,
    unsafe_allow_html=True,
)
