import streamlit as st
from utils.shared.styles import inject_css

inject_css()

# ── Page-level CSS: full-screen split, hide chrome ───────────────────────────
st.markdown("""
<style>
[data-testid="stSidebarNav"]   { display:none !important; }
[data-testid="collapsedControl"]{ display:none !important; }
section[data-testid="stSidebar"]{ display:none !important; }
header[data-testid="stHeader"]  { display:none !important; }
footer                          { display:none !important; }

/* Remove all default page padding so columns touch the edges */
[data-testid="stAppViewBlockContainer"] {
    padding: 0 !important; max-width: 100% !important;
}
.stApp > section > div { padding: 0 !important; }
[data-testid="stMainBlockContainer"] { padding: 0 !important; }

/* Remove gap between the two columns */
[data-testid="stHorizontalBlock"] { gap: 0 !important; }

/* LEFT COLUMN — hero panel */
[data-testid="stHorizontalBlock"] > div:first-child {
    background: linear-gradient(148deg, #0a1628 0%, #1a2744 50%, #1e3160 100%) !important;
    min-height: 100vh !important;
    padding: 0 !important;
    position: relative !important;
}
/* RIGHT COLUMN — form panel */
[data-testid="stHorizontalBlock"] > div:last-child {
    background: #f7f6f2 !important;
    min-height: 100vh !important;
    padding: 3rem 3.5rem !important;
}

/* Tabs styling inside login form */
[data-testid="stHorizontalBlock"] > div:last-child [data-baseweb="tab-list"] {
    background: #ede9e0 !important;
    border-radius: 8px !important;
    padding: 3px !important;
    border: none !important;
    gap: 2px !important;
    margin-bottom: .5rem !important;
}
[data-testid="stHorizontalBlock"] > div:last-child [data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    border-bottom: none !important;
    border-radius: 6px !important;
    padding: .42rem 1rem !important;
    font-size: .82rem !important;
    font-weight: 500 !important;
    color: #6b7280 !important;
    margin: 0 !important;
}
[data-testid="stHorizontalBlock"] > div:last-child [aria-selected="true"][data-baseweb="tab"] {
    background: #ffffff !important;
    color: #1a2744 !important;
    font-weight: 700 !important;
    box-shadow: 0 1px 5px rgba(0,0,0,.1) !important;
    border-bottom: none !important;
}
[data-testid="stHorizontalBlock"] > div:last-child [data-baseweb="tab-panel"] {
    padding: .8rem 0 0 !important;
    background: transparent !important;
}

/* Inputs inside form panel */
[data-testid="stHorizontalBlock"] > div:last-child .stTextInput > label {
    font-size: .73rem !important; font-weight: 700 !important;
    text-transform: uppercase !important; letter-spacing: .07em !important;
    color: #94a3b8 !important;
}
[data-testid="stHorizontalBlock"] > div:last-child .stTextInput input {
    background: #fff !important;
    border: 1.5px solid #dde1eb !important;
    border-radius: 8px !important;
    font-size: .9rem !important;
    padding: .6rem .9rem !important;
    color: #1a1a2e !important;
    box-shadow: 0 1px 3px rgba(0,0,0,.06) !important;
    transition: border-color .18s, box-shadow .18s !important;
}
[data-testid="stHorizontalBlock"] > div:last-child .stTextInput input:focus {
    border-color: #1a2744 !important;
    box-shadow: 0 0 0 3px rgba(26,39,68,.1) !important;
}
[data-testid="stHorizontalBlock"] > div:last-child .stButton > button {
    background: linear-gradient(135deg, #1a2744, #253461) !important;
    color: #fff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: .88rem !important;
    padding: .6rem 1.4rem !important;
    box-shadow: 0 4px 14px rgba(26,39,68,.25) !important;
    transition: all .2s ease !important;
}
[data-testid="stHorizontalBlock"] > div:last-child .stButton > button:hover {
    background: linear-gradient(135deg, #0f1a33, #1a2744) !important;
    box-shadow: 0 6px 20px rgba(26,39,68,.35) !important;
    transform: translateY(-1px) !important;
}
[data-testid="stHorizontalBlock"] > div:last-child .stCaption,
[data-testid="stHorizontalBlock"] > div:last-child [data-testid="stCaptionContainer"] * {
    color: #9ca3af !important; font-size: .74rem !important;
}
[data-testid="stHorizontalBlock"] > div:last-child .stAlert {
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)

# ── Two-column split layout ───────────────────────────────────────────────────
col_hero, col_form = st.columns([1, 1], gap="small")

# ─── LEFT: Hero panel (pure HTML/CSS — no Streamlit widgets) ─────────────────
with col_hero:
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;1,600&family=Inter:wght@300;400;500;600;700&display=swap');

    @keyframes floatScales { 0%,100%{transform:translateY(0)} 50%{transform:translateY(-10px)} }
    @keyframes heroGlow    { 0%{opacity:.5} 100%{opacity:1} }
    @keyframes shimmerG    { from{background-position:200% center} to{background-position:-200% center} }
    @keyframes fadeUp      { from{opacity:0;transform:translateY(18px)} to{opacity:1;transform:translateY(0)} }
    @keyframes dotPulse    { 0%,100%{opacity:.3} 50%{opacity:.7} }

    .h-wrap {
        min-height: 100vh;
        display: flex; flex-direction: column;
        justify-content: space-between;
        padding: 3rem 3rem;
        position: relative; overflow: hidden;
        font-family: 'Inter', sans-serif;
    }
    /* Radial glow overlay */
    .h-wrap::before {
        content:'';
        position:absolute; inset:0;
        background:
            radial-gradient(ellipse at 25% 35%, rgba(201,168,76,.07) 0%, transparent 55%),
            radial-gradient(ellipse at 75% 65%, rgba(79,100,200,.08) 0%, transparent 55%);
        animation: heroGlow 7s ease-in-out infinite alternate;
        pointer-events:none;
    }
    /* Dot grid */
    .h-wrap::after {
        content:'';
        position:absolute; inset:0;
        background-image: radial-gradient(rgba(255,255,255,.035) 1.5px, transparent 1.5px);
        background-size: 30px 30px;
        pointer-events:none;
    }

    /* Brand */
    .h-brand {
        position:relative; z-index:2;
        animation: fadeUp .5s ease both;
        display:flex; align-items:center; gap:.6rem;
    }
    .h-logo-box {
        width:42px; height:42px; border-radius:10px;
        background: linear-gradient(135deg,#c9a84c,#e8c97a);
        display:flex; align-items:center; justify-content:center;
        font-size:1.4rem;
        box-shadow: 0 4px 18px rgba(201,168,76,.35);
    }
    .h-brand-text { font-size:1.45rem; font-weight:800; color:#fff; letter-spacing:-.02em; }
    .h-brand-sub  { font-size:.7rem; color:rgba(255,255,255,.4);
                    text-transform:uppercase; letter-spacing:.12em; margin-top:.18rem; }

    /* Centre visual */
    .h-center {
        position:relative; z-index:2; text-align:center;
        display:flex; flex-direction:column; align-items:center;
        flex:1; justify-content:center; padding:1.5rem 0;
        animation: fadeUp .6s .1s ease both;
    }
    .h-svg { width:145px; height:145px; animation: floatScales 5s ease-in-out infinite;
              filter: drop-shadow(0 10px 28px rgba(201,168,76,.22)); }

    .h-title {
        font-family:'Playfair Display',Georgia,serif;
        font-size:2rem; font-weight:700; color:#fff;
        line-height:1.2; margin:1.3rem 0 .65rem;
        letter-spacing:-.01em;
    }
    .h-title em {
        font-style:italic;
        background: linear-gradient(90deg,#c9a84c,#f0d07a,#c9a84c);
        background-size:200% auto;
        -webkit-background-clip:text; -webkit-text-fill-color:transparent;
        background-clip:text;
        animation: shimmerG 3s linear infinite;
    }
    .h-desc { font-size:.87rem; color:rgba(255,255,255,.55); max-width:300px; line-height:1.65; }

    /* Stats */
    .h-stats {
        display:flex; justify-content:center; gap:2.5rem;
        margin-top:1.8rem; position:relative; z-index:2;
        animation: fadeUp .6s .25s ease both;
    }
    .h-stat .n { font-family:'Playfair Display',serif; font-size:1.5rem; font-weight:700; color:#c9a84c; }
    .h-stat .l { font-size:.68rem; color:rgba(255,255,255,.38); text-transform:uppercase; letter-spacing:.09em; margin-top:.15rem; }

    /* Features */
    .h-features { position:relative; z-index:2; animation: fadeUp .6s .35s ease both; }
    .h-feat {
        display:flex; align-items:center; gap:.65rem;
        font-size:.82rem; color:rgba(255,255,255,.62);
        padding:.32rem 0;
        border-bottom:1px solid rgba(255,255,255,.05);
    }
    .h-feat:last-child { border:none; }
    .h-dot { width:6px; height:6px; border-radius:50%; background:#c9a84c; flex-shrink:0; }

    /* Gold separator line */
    .h-line { width:40px; height:2px; background:linear-gradient(90deg,#c9a84c,transparent); margin:.6rem 0; }
    </style>

    <div class="h-wrap">

      <!-- Brand -->
      <div class="h-brand">
        <div>
          <div class="h-logo-box">⚖</div>
        </div>
        <div>
          <div class="h-brand-text">eLawFirm</div>
          <div class="h-brand-sub">Intelligent Legal Platform</div>
        </div>
      </div>

      <!-- Central visual -->
      <div class="h-center">
        <!-- Scales of Justice + Circuit SVG -->
        <svg class="h-svg" viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
          <!-- Outer glow rings -->
          <circle cx="100" cy="100" r="90" stroke="rgba(201,168,76,.04)" stroke-width="1"/>
          <circle cx="100" cy="100" r="75" stroke="rgba(201,168,76,.06)" stroke-width="1"/>
          <!-- Pole -->
          <rect x="98.5" y="28" width="3" height="128" rx="1.5" fill="rgba(201,168,76,.65)"/>
          <!-- Top orb -->
          <circle cx="100" cy="24" r="6" fill="#c9a84c" opacity=".9"/>
          <circle cx="100" cy="24" r="10" fill="none" stroke="rgba(201,168,76,.3)" stroke-width="1"/>
          <!-- Crossbar -->
          <rect x="28" y="52" width="144" height="3.5" rx="1.75" fill="rgba(201,168,76,.55)"/>
          <!-- Left arm chain -->
          <path d="M42 55.5 L36 92" stroke="rgba(201,168,76,.45)" stroke-width="1.5" stroke-dasharray="3.5 3"/>
          <!-- Right arm chain -->
          <path d="M158 55.5 L164 92" stroke="rgba(201,168,76,.45)" stroke-width="1.5" stroke-dasharray="3.5 3"/>
          <!-- Left pan -->
          <ellipse cx="34" cy="94" rx="22" ry="7" fill="rgba(201,168,76,.12)" stroke="rgba(201,168,76,.55)" stroke-width="1.5"/>
          <!-- Right pan (slightly lower — balanced-unbalanced feel) -->
          <ellipse cx="166" cy="97" rx="22" ry="7" fill="rgba(201,168,76,.12)" stroke="rgba(201,168,76,.55)" stroke-width="1.5"/>
          <!-- Base -->
          <rect x="62" y="152" width="76" height="7" rx="3.5" fill="rgba(201,168,76,.4)"/>
          <rect x="78" y="159" width="44" height="5" rx="2.5" fill="rgba(201,168,76,.25)"/>
          <!-- Circuit traces — technology layer -->
          <line x1="34" y1="102" x2="34"  y2="130" stroke="rgba(79,120,220,.35)" stroke-width="1"/>
          <line x1="34" y1="130" x2="60"  y2="130" stroke="rgba(79,120,220,.35)" stroke-width="1"/>
          <line x1="60" y1="130" x2="60"  y2="148" stroke="rgba(79,120,220,.35)" stroke-width="1"/>
          <line x1="166" y1="105" x2="166" y2="130" stroke="rgba(79,120,220,.35)" stroke-width="1"/>
          <line x1="166" y1="130" x2="140" y2="130" stroke="rgba(79,120,220,.35)" stroke-width="1"/>
          <line x1="140" y1="130" x2="140" y2="148" stroke="rgba(79,120,220,.35)" stroke-width="1"/>
          <!-- Circuit nodes -->
          <circle cx="34"  cy="130" r="3" fill="rgba(79,120,220,.55)"/>
          <circle cx="60"  cy="148" r="2.5" fill="rgba(79,120,220,.4)"/>
          <circle cx="166" cy="130" r="3" fill="rgba(79,120,220,.55)"/>
          <circle cx="140" cy="148" r="2.5" fill="rgba(79,120,220,.4)"/>
          <circle cx="100" cy="80"  r="2" fill="rgba(201,168,76,.5)"/>
          <circle cx="28"  cy="52"  r="3" fill="rgba(201,168,76,.6)"/>
          <circle cx="172" cy="52"  r="3" fill="rgba(201,168,76,.6)"/>
        </svg>

        <div class="h-line"></div>
        <h2 class="h-title">Where <em>Justice</em><br>Meets Intelligence</h2>
        <p class="h-desc">AI-powered legal tools built for professionals who demand precision, speed, and confidentiality.</p>

        <div class="h-stats">
          <div class="h-stat"><div class="n">5+</div><div class="l">AI Tools</div></div>
          <div class="h-stat"><div class="n">100%</div><div class="l">Confidential</div></div>
          <div class="h-stat"><div class="n">5</div><div class="l">Role Levels</div></div>
        </div>
      </div>

      <!-- Feature list -->
      <div class="h-features">
        <div class="h-feat"><div class="h-dot"></div>Document drafting &amp; clause library</div>
        <div class="h-feat"><div class="h-dot"></div>AI legal research with jurisdiction awareness</div>
        <div class="h-feat"><div class="h-dot"></div>Matter management &amp; client portal</div>
        <div class="h-feat"><div class="h-dot"></div>PDF-to-Word conversion &amp; document processing</div>
      </div>

    </div>
    """, unsafe_allow_html=True)

# ─── RIGHT: Form panel ────────────────────────────────────────────────────────
with col_form:
    # Centred wrapper
    st.markdown("""
    <style>
    @keyframes fadeUp2 { from{opacity:0;transform:translateY(16px)} to{opacity:1;transform:translateY(0)} }
    .f-wrap {
        padding: 0;
        font-family: 'Inter', sans-serif;
        animation: fadeUp2 .5s .15s ease both;
        margin-bottom: 1.5rem;
    }
    .f-title {
        font-family:'Playfair Display',Georgia,serif;
        font-size:1.8rem; font-weight:700; color:#1a2744;
        margin:0 0 .3rem; letter-spacing:-.01em;
    }
    .f-sub { font-size:.87rem; color:#6b7280; margin:0 0 1.8rem; }
    .f-gold-bar { width:36px; height:3px; background:#c9a84c; border-radius:2px; margin-bottom:1.2rem; }
    .f-footer {
        margin-top:2rem; font-size:.72rem; color:#9ca3af;
        text-align:center; padding-top:1rem;
        border-top:1px solid #e9e6df;
    }
    </style>
    <div class="f-wrap">
      <div class="f-gold-bar"></div>
      <h1 class="f-title">Welcome back</h1>
      <p class="f-sub">Sign in to your firm workspace or create a new one.</p>
    </div>
    """, unsafe_allow_html=True)

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
            "<p style='font-size:.83rem;color:#6b7280;margin:0 0 .8rem'>"
            "Create a new firm account. You will be the <strong style='color:#1a2744'>admin</strong>.</p>",
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
        "<div class='f-footer'>⚖ eLawFirm &nbsp;·&nbsp; AI output does not replace qualified legal advice</div>",
        unsafe_allow_html=True,
    )
