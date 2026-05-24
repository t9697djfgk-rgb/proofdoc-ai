import streamlit as st
from utils.shared.styles import inject_css

inject_css()

# ── Page-level CSS ────────────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stSidebarNav"]    { display:none !important; }
[data-testid="collapsedControl"]{ display:none !important; }
section[data-testid="stSidebar"]{ display:none !important; }
header[data-testid="stHeader"]  { display:none !important; }
footer                          { display:none !important; }
#MainMenu                       { display:none !important; }

[data-testid="stAppViewBlockContainer"] { padding:0 !important; max-width:100% !important; }
.stApp > section > div          { padding:0 !important; }
[data-testid="stMainBlockContainer"] { padding:0 !important; }
[data-testid="stHorizontalBlock"] { gap:0 !important; }

/* LEFT column — navy hero */
[data-testid="stHorizontalBlock"] > div:first-child {
    background: linear-gradient(148deg,#07111f 0%,#1a2744 50%,#1e3263 100%) !important;
    min-height:100vh !important; padding:0 !important; overflow:hidden !important;
}
/* RIGHT column — form */
[data-testid="stHorizontalBlock"] > div:last-child {
    background:#f7f6f2 !important;
    min-height:100vh !important;
    padding:3rem 3.5rem !important;
}

/* Tab strip in form panel */
[data-testid="stHorizontalBlock"] > div:last-child [data-baseweb="tab-list"] {
    background:#ede9e0 !important; border-radius:8px !important;
    padding:3px !important; border:none !important; gap:2px !important;
}
[data-testid="stHorizontalBlock"] > div:last-child [data-baseweb="tab"] {
    background:transparent !important; border:none !important; border-bottom:none !important;
    border-radius:6px !important; padding:.42rem 1.1rem !important;
    font-size:.82rem !important; font-weight:500 !important; color:#6b7280 !important; margin:0 !important;
}
[data-testid="stHorizontalBlock"] > div:last-child [aria-selected="true"][data-baseweb="tab"] {
    background:#fff !important; color:#1a2744 !important; font-weight:700 !important;
    box-shadow:0 1px 5px rgba(0,0,0,.1) !important; border-bottom:none !important;
}
[data-testid="stHorizontalBlock"] > div:last-child [data-baseweb="tab-panel"] {
    padding:.9rem 0 0 !important; background:transparent !important;
}
/* Inputs */
[data-testid="stHorizontalBlock"] > div:last-child .stTextInput > label {
    font-size:.73rem !important; font-weight:700 !important;
    text-transform:uppercase !important; letter-spacing:.07em !important; color:#94a3b8 !important;
}
[data-testid="stHorizontalBlock"] > div:last-child .stTextInput input {
    background:#fff !important; border:1.5px solid #dde1eb !important;
    border-radius:8px !important; font-size:.9rem !important; color:#1a1a2e !important;
    padding:.6rem .9rem !important; box-shadow:0 1px 3px rgba(0,0,0,.06) !important;
}
[data-testid="stHorizontalBlock"] > div:last-child .stTextInput input:focus {
    border-color:#1a2744 !important; box-shadow:0 0 0 3px rgba(26,39,68,.1) !important;
}
[data-testid="stHorizontalBlock"] > div:last-child .stButton > button {
    background:linear-gradient(135deg,#1a2744,#253461) !important;
    color:#fff !important; border:none !important; border-radius:8px !important;
    font-weight:600 !important; font-size:.88rem !important;
    padding:.62rem 1.4rem !important; box-shadow:0 4px 14px rgba(26,39,68,.25) !important;
    transition:all .2s ease !important;
}
[data-testid="stHorizontalBlock"] > div:last-child .stButton > button:hover {
    box-shadow:0 6px 20px rgba(26,39,68,.35) !important; transform:translateY(-1px) !important;
}
[data-testid="stHorizontalBlock"] > div:last-child .stCaption * { color:#9ca3af !important; font-size:.74rem !important; }
</style>
""", unsafe_allow_html=True)

# ── Split layout ──────────────────────────────────────────────────────────────
col_hero, col_form = st.columns([1, 1], gap="small")

# ── LEFT: Animated hero panel ─────────────────────────────────────────────────
with col_hero:
    # CSS must be in its own call — Streamlit drops HTML after </style> otherwise
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;1,600&family=Inter:wght@300;400;500;600;700&display=swap');

/* ── All animations ── */
@keyframes floatScales  { 0%,100%{transform:translateY(0) rotate(0deg)}   50%{transform:translateY(-12px) rotate(1deg)} }
@keyframes shimmerGold  { from{background-position:200% center} to{background-position:-200% center} }
@keyframes fadeUp       { from{opacity:0;transform:translateY(20px)} to{opacity:1;transform:translateY(0)} }
@keyframes fadeIn       { from{opacity:0} to{opacity:1} }
@keyframes pulseRing    { 0%{transform:scale(.95);opacity:.5} 70%{transform:scale(1.08);opacity:0} 100%{transform:scale(.95);opacity:0} }
@keyframes spinOrbit    { from{transform:rotate(0deg) translateX(90px) rotate(0deg)} to{transform:rotate(360deg) translateX(90px) rotate(-360deg)} }
@keyframes spinOrbit2   { from{transform:rotate(120deg) translateX(75px) rotate(-120deg)} to{transform:rotate(480deg) translateX(75px) rotate(-480deg)} }
@keyframes spinOrbit3   { from{transform:rotate(240deg) translateX(110px) rotate(-240deg)} to{transform:rotate(600deg) translateX(110px) rotate(-600deg)} }
@keyframes driftDot     { 0%,100%{transform:translate(0,0);opacity:.18} 33%{transform:translate(12px,-18px);opacity:.35} 66%{transform:translate(-8px,10px);opacity:.22} }
@keyframes driftDot2    { 0%,100%{transform:translate(0,0);opacity:.12} 50%{transform:translate(-15px,-12px);opacity:.3} }
@keyframes lineGrow     { from{stroke-dashoffset:200} to{stroke-dashoffset:0} }

/* ── Feature cycle ── */
@keyframes featCycle {
    0%   { opacity:0; transform:translateY(14px) scale(.97); }
    8%   { opacity:1; transform:translateY(0) scale(1); }
    22%  { opacity:1; transform:translateY(0) scale(1); }
    30%  { opacity:0; transform:translateY(-14px) scale(.97); }
    100% { opacity:0; }
}

/* ── Stat counter bar ── */
@keyframes barFill1 { from{width:0} to{width:92%} }
@keyframes barFill2 { from{width:0} to{width:78%} }
@keyframes barFill3 { from{width:0} to{width:85%} }

/* ── Wrapper ── */
.hw {
    min-height:100vh;
    display:flex; flex-direction:column; justify-content:space-between;
    padding:2.8rem 3rem; position:relative; overflow:hidden;
    font-family:'Inter',sans-serif;
    background: linear-gradient(148deg,#07111f 0%,#1a2744 52%,#1e3263 100%);
}

/* Animated radial glow */
.hw::before {
    content:''; position:absolute; inset:0; pointer-events:none;
    background:
        radial-gradient(ellipse at 20% 30%,rgba(201,168,76,.08) 0%,transparent 55%),
        radial-gradient(ellipse at 80% 70%,rgba(79,110,220,.1) 0%,transparent 55%),
        radial-gradient(ellipse at 50% 100%,rgba(26,39,68,.6) 0%,transparent 60%);
    animation: fadeIn 1.5s ease both;
}
/* Dot grid */
.hw::after {
    content:''; position:absolute; inset:0; pointer-events:none;
    background-image: radial-gradient(rgba(255,255,255,.028) 1.5px, transparent 1.5px);
    background-size:28px 28px;
}

/* Drifting background particles */
.p1,.p2,.p3,.p4,.p5,.p6 {
    position:absolute; border-radius:50%; pointer-events:none;
}
.p1{width:3px;height:3px;background:rgba(201,168,76,.4);top:15%;left:20%;animation:driftDot 8s ease-in-out infinite;}
.p2{width:2px;height:2px;background:rgba(201,168,76,.3);top:40%;left:75%;animation:driftDot2 11s ease-in-out infinite 2s;}
.p3{width:4px;height:4px;background:rgba(79,110,220,.35);top:65%;left:15%;animation:driftDot 14s ease-in-out infinite 1s;}
.p4{width:2px;height:2px;background:rgba(255,255,255,.2);top:80%;left:60%;animation:driftDot2 9s ease-in-out infinite 3s;}
.p5{width:3px;height:3px;background:rgba(201,168,76,.25);top:25%;left:85%;animation:driftDot 12s ease-in-out infinite 4s;}
.p6{width:2px;height:2px;background:rgba(79,110,220,.3);top:55%;left:45%;animation:driftDot2 10s ease-in-out infinite 1.5s;}

/* Brand */
.hw-brand { position:relative;z-index:3; display:flex;align-items:center;gap:.65rem; animation:fadeUp .5s ease both; }
.hw-logo  { width:44px;height:44px;border-radius:12px;background:linear-gradient(135deg,#c9a84c,#e8c97a);
             display:flex;align-items:center;justify-content:center;font-size:1.4rem;
             box-shadow:0 4px 20px rgba(201,168,76,.4); }
.hw-name  { font-size:1.5rem;font-weight:800;color:#ffffff;letter-spacing:-.02em; }
.hw-sub   { font-size:.68rem;color:rgba(255,255,255,.4);text-transform:uppercase;letter-spacing:.12em;margin-top:.15rem; }

/* Central visual */
.hw-center { position:relative;z-index:3;text-align:center;flex:1;
              display:flex;flex-direction:column;align-items:center;justify-content:center;
              padding:1.5rem 0; animation:fadeUp .6s .12s ease both; }

/* Orbit system */
.orbit-wrap { position:relative;width:220px;height:220px;margin:0 auto; }
.orbit-ring  { position:absolute;inset:0;border-radius:50%;border:1px solid rgba(201,168,76,.12); }
.orbit-ring2 { position:absolute;inset:15%;border-radius:50%;border:1px solid rgba(79,110,220,.1); }
.pulse-ring  { position:absolute;inset:-8px;border-radius:50%;border:2px solid rgba(201,168,76,.25);
               animation:pulseRing 2.8s ease-out infinite; }
.pulse-ring2 { position:absolute;inset:-8px;border-radius:50%;border:2px solid rgba(201,168,76,.15);
               animation:pulseRing 2.8s ease-out infinite 1.4s; }

/* Orbiting dots */
.orb-dot { position:absolute;top:50%;left:50%;width:8px;height:8px;border-radius:50%;margin:-4px 0 0 -4px; }
.od1 { background:rgba(201,168,76,.8); animation:spinOrbit 6s linear infinite; box-shadow:0 0 8px rgba(201,168,76,.6); }
.od2 { background:rgba(79,110,220,.8); animation:spinOrbit2 9s linear infinite; width:6px;height:6px;margin:-3px 0 0 -3px; box-shadow:0 0 6px rgba(79,110,220,.5); }
.od3 { background:rgba(255,255,255,.5); animation:spinOrbit3 12s linear infinite; width:5px;height:5px;margin:-2.5px 0 0 -2.5px; }

/* Scales SVG centered */
.scales-center { position:absolute;inset:0;display:flex;align-items:center;justify-content:center; }
.hw-svg { width:130px;height:130px; animation:floatScales 5s ease-in-out infinite;
           filter:drop-shadow(0 10px 30px rgba(201,168,76,.3)); }

/* Headline */
.hw-title { font-family:'Playfair Display',Georgia,serif;
             font-size:1.95rem;font-weight:700;color:#ffffff;
             line-height:1.22;margin:1.4rem 0 .6rem;letter-spacing:-.01em; }
.hw-title em {
    font-style:italic;
    background:linear-gradient(90deg,#c9a84c,#f0d07a,#c9a84c,#e8c97a);
    background-size:300% auto;
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
    animation:shimmerGold 3s linear infinite;
}
.hw-desc { font-size:.87rem;color:rgba(255,255,255,.6);max-width:290px;line-height:1.65;margin:0 auto; }

/* ── Cycling feature showcase ── */
.feat-box {
    position:relative; z-index:3;
    margin:1.6rem 0 0;
    height:62px; overflow:hidden;
    animation:fadeIn .8s .5s ease both;
}
.feat-label {
    position:absolute; inset:0;
    display:flex; align-items:center; gap:.85rem;
    opacity:0;
    animation: featCycle 20s ease-in-out infinite;
}
.feat-label:nth-child(1) { animation-delay:0s; }
.feat-label:nth-child(2) { animation-delay:5s; }
.feat-label:nth-child(3) { animation-delay:10s; }
.feat-label:nth-child(4) { animation-delay:15s; }

.feat-icon {
    width:44px; height:44px; border-radius:12px; flex-shrink:0;
    display:flex; align-items:center; justify-content:center;
    font-size:1.3rem;
    background:rgba(255,255,255,.07);
    border:1px solid rgba(255,255,255,.1);
    box-shadow:0 2px 12px rgba(0,0,0,.2);
}
.feat-text { text-align:left; }
.feat-text .ft { font-size:.92rem;font-weight:600;color:#ffffff; }
.feat-text .fs { font-size:.75rem;color:rgba(255,255,255,.5);margin-top:.1rem; }

/* ── Animated stat bars ── */
.hw-stats { position:relative;z-index:3; animation:fadeUp .7s .35s ease both; }
.stat-row { margin-bottom:.7rem; }
.stat-top { display:flex;justify-content:space-between;margin-bottom:.3rem; }
.stat-top span { font-size:.72rem;color:rgba(255,255,255,.55);font-weight:500; }
.stat-top strong { font-size:.72rem;color:rgba(255,255,255,.75);font-weight:700; }
.stat-bar-bg { height:3px;background:rgba(255,255,255,.08);border-radius:2px;overflow:hidden; }
.stat-bar-fill { height:100%;border-radius:2px; background:linear-gradient(90deg,#c9a84c,#e8c97a); }
.sb1 { animation:barFill1 1.8s .6s ease both; }
.sb2 { animation:barFill2 1.8s .8s ease both; }
.sb3 { animation:barFill3 1.8s 1s ease both; }

/* Gold divider */
.hw-line { width:36px;height:2.5px;background:linear-gradient(90deg,#c9a84c,transparent);border-radius:2px;margin:.5rem 0 1rem; }
</style>
""", unsafe_allow_html=True)

    # HTML in a separate call so Streamlit doesn't swallow it after the <style> block
    st.markdown("""
<div class="hw">
  <!-- particles -->
  <div class="p1"></div><div class="p2"></div><div class="p3"></div>
  <div class="p4"></div><div class="p5"></div><div class="p6"></div>

  <!-- Brand -->
  <div class="hw-brand">
    <div class="hw-logo">⚖</div>
    <div>
      <div class="hw-name">eLawFirm</div>
      <div class="hw-sub">Intelligent Legal Platform</div>
    </div>
  </div>

  <!-- Central visual -->
  <div class="hw-center">
    <div class="orbit-wrap">
      <div class="orbit-ring"></div>
      <div class="orbit-ring2"></div>
      <div class="pulse-ring"></div>
      <div class="pulse-ring2"></div>
      <div class="orb-dot od1"></div>
      <div class="orb-dot od2"></div>
      <div class="orb-dot od3"></div>
      <!-- SVG Scales of Justice -->
      <div class="scales-center">
        <svg class="hw-svg" viewBox="0 0 200 200" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="100" cy="100" r="88" stroke="rgba(201,168,76,.06)" stroke-width="1"/>
          <rect x="98.5" y="30" width="3" height="120" rx="1.5" fill="rgba(201,168,76,.7)"/>
          <circle cx="100" cy="26" r="5.5" fill="#c9a84c"/>
          <rect x="30" y="52" width="140" height="3" rx="1.5" fill="rgba(201,168,76,.6)"/>
          <path d="M44 55 L38 90" stroke="rgba(201,168,76,.5)" stroke-width="1.5" stroke-dasharray="3.5 3" stroke-dashoffset="0"/>
          <path d="M156 55 L162 90" stroke="rgba(201,168,76,.5)" stroke-width="1.5" stroke-dasharray="3.5 3"/>
          <ellipse cx="36" cy="93" rx="20" ry="6" fill="rgba(201,168,76,.1)" stroke="rgba(201,168,76,.6)" stroke-width="1.5"/>
          <ellipse cx="164" cy="96" rx="20" ry="6" fill="rgba(201,168,76,.1)" stroke="rgba(201,168,76,.6)" stroke-width="1.5"/>
          <rect x="64" y="148" width="72" height="6" rx="3" fill="rgba(201,168,76,.4)"/>
          <!-- Circuit traces -->
          <path d="M36 99 L36 128 L62 128 L62 144" stroke="rgba(79,110,220,.4)" stroke-width="1" fill="none" stroke-dasharray="200" stroke-dashoffset="200" style="animation:lineGrow 1.5s 1s ease forwards"/>
          <path d="M164 102 L164 128 L138 128 L138 144" stroke="rgba(79,110,220,.4)" stroke-width="1" fill="none" stroke-dasharray="200" stroke-dashoffset="200" style="animation:lineGrow 1.5s 1.3s ease forwards"/>
          <circle cx="36" cy="128" r="2.5" fill="rgba(79,110,220,.6)"/>
          <circle cx="62" cy="144" r="2" fill="rgba(79,110,220,.5)"/>
          <circle cx="164" cy="128" r="2.5" fill="rgba(79,110,220,.6)"/>
          <circle cx="138" cy="144" r="2" fill="rgba(79,110,220,.5)"/>
          <circle cx="30" cy="52" r="2.5" fill="rgba(201,168,76,.7)"/>
          <circle cx="170" cy="52" r="2.5" fill="rgba(201,168,76,.7)"/>
        </svg>
      </div>
    </div>

    <div class="hw-line"></div>
    <h2 class="hw-title">Where <em>Justice</em><br>Meets Intelligence</h2>
    <p class="hw-desc">AI-powered legal tools built for professionals who demand precision, speed, and confidentiality.</p>

    <!-- Cycling feature animation -->
    <div class="feat-box">
      <div class="feat-label">
        <div class="feat-icon">✍️</div>
        <div class="feat-text">
          <div class="ft">Document Drafting</div>
          <div class="fs">AI-assisted clause library &amp; templates</div>
        </div>
      </div>
      <div class="feat-label">
        <div class="feat-icon">🔍</div>
        <div class="feat-text">
          <div class="ft">Legal Research</div>
          <div class="fs">Jurisdiction-aware AI with Rwanda law</div>
        </div>
      </div>
      <div class="feat-label">
        <div class="feat-icon">⚖️</div>
        <div class="feat-text">
          <div class="ft">Matter Management</div>
          <div class="fs">Client portal, tasks &amp; billing</div>
        </div>
      </div>
      <div class="feat-label">
        <div class="feat-icon">📄</div>
        <div class="feat-text">
          <div class="ft">Document Conversion</div>
          <div class="fs">PDF-to-Word in seconds</div>
        </div>
      </div>
    </div>
  </div>

  <!-- Animated stat bars -->
  <div class="hw-stats">
    <div class="stat-row">
      <div class="stat-top"><span>Document accuracy</span><strong>92%</strong></div>
      <div class="stat-bar-bg"><div class="stat-bar-fill sb1"></div></div>
    </div>
    <div class="stat-row">
      <div class="stat-top"><span>Research speed</span><strong>78× faster</strong></div>
      <div class="stat-bar-bg"><div class="stat-bar-fill sb2"></div></div>
    </div>
    <div class="stat-row">
      <div class="stat-top"><span>Client satisfaction</span><strong>4.9 / 5</strong></div>
      <div class="stat-bar-bg"><div class="stat-bar-fill sb3"></div></div>
    </div>
  </div>

</div>
""", unsafe_allow_html=True)

# ── RIGHT: Form panel ─────────────────────────────────────────────────────────
with col_form:
    st.markdown("""
    <style>
    @keyframes fadeUp3 { from{opacity:0;transform:translateY(14px)} to{opacity:1;transform:translateY(0)} }
    .f-head { animation:fadeUp3 .5s .15s ease both; margin-bottom:1.6rem; }
    .f-bar  { width:34px;height:3px;background:#c9a84c;border-radius:2px;margin-bottom:1rem; }
    .f-title{ font-family:'Playfair Display',Georgia,serif;font-size:1.75rem;font-weight:700;color:#1a2744;margin:0 0 .3rem;letter-spacing:-.01em; }
    .f-sub  { font-size:.87rem;color:#6b7280;margin:0; }
    .f-foot { margin-top:2rem;font-size:.72rem;color:#9ca3af;text-align:center;padding-top:1rem;border-top:1px solid #e9e6df; }
    </style>
    """, unsafe_allow_html=True)
    st.markdown("""
    <div class="f-head">
      <div class="f-bar"></div>
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
            "Create a new firm account — you will be the <strong style='color:#1a2744'>admin</strong>.</p>",
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
        "<div class='f-foot'>⚖ eLawFirm &nbsp;·&nbsp; AI output does not replace qualified legal advice</div>",
        unsafe_allow_html=True,
    )
