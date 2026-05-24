import streamlit as st

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,600;0,700;1,600&family=Inter:wght@300;400;500;600;700&display=swap');

/* ═══════════════════════════════════════════════════
   DESIGN TOKENS — Professional Legal Light Mode
═══════════════════════════════════════════════════ */
:root {
    --bg:           #f6f5f0;
    --bg-warm:      #faf9f6;
    --surface:      #ffffff;
    --surface-2:    #f0ede6;
    --navy:         #1a2744;
    --navy-light:   #253461;
    --navy-hover:   #0f1a33;
    --gold:         #c9a84c;
    --gold-light:   #e8c97a;
    --gold-pale:    #fdf6e3;
    --text:         #1a1a2e;
    --text-body:    #374151;
    --text-muted:   #6b7280;
    --text-light:   #9ca3af;
    --border:       rgba(0,0,0,0.08);
    --border-navy:  rgba(26,39,68,0.15);
    --border-gold:  rgba(201,168,76,0.3);
    --green:        #059669;
    --red:          #dc2626;
    --amber:        #d97706;
    --radius-sm:    6px;
    --radius:       10px;
    --radius-lg:    16px;
    --radius-xl:    24px;
    --shadow-sm:    0 1px 3px rgba(0,0,0,0.08),0 1px 2px rgba(0,0,0,0.05);
    --shadow:       0 4px 16px rgba(0,0,0,0.08),0 2px 6px rgba(0,0,0,0.05);
    --shadow-lg:    0 12px 40px rgba(26,39,68,0.12),0 4px 12px rgba(0,0,0,0.06);
    --shadow-gold:  0 6px 24px rgba(201,168,76,0.18);
    --transition:   all 0.22s cubic-bezier(0.4,0,0.2,1);
}

/* ═══════════════════════════════════════════════════
   ANIMATIONS
═══════════════════════════════════════════════════ */
@keyframes fadeInUp {
    from { opacity:0; transform:translateY(18px); }
    to   { opacity:1; transform:translateY(0); }
}
@keyframes fadeIn {
    from { opacity:0; }
    to   { opacity:1; }
}
@keyframes slideInLeft {
    from { opacity:0; transform:translateX(-14px); }
    to   { opacity:1; transform:translateX(0); }
}
@keyframes scaleIn {
    from { opacity:0; transform:scale(0.97); }
    to   { opacity:1; transform:scale(1); }
}
@keyframes shimmer {
    0%   { background-position: -400px 0; }
    100% { background-position: 400px 0; }
}
@keyframes pulse-dot {
    0%,100% { transform:scale(1); opacity:1; }
    50%      { transform:scale(1.35); opacity:0.7; }
}
@keyframes float {
    0%,100% { transform:translateY(0); }
    50%      { transform:translateY(-6px); }
}
@keyframes goldShimmer {
    0%   { background-position:200% center; }
    100% { background-position:-200% center; }
}

/* ═══════════════════════════════════════════════════
   HIDE ALL STREAMLIT CHROME
═══════════════════════════════════════════════════ */
/* Hamburger menu */
#MainMenu                                { display: none !important; }
/* "Made with Streamlit" footer */
footer                                   { display: none !important; }
/* Deploy button & toolbar */
[data-testid="stToolbar"]               { display: none !important; }
[data-testid="stDecoration"]            { display: none !important; }
[data-testid="stStatusWidget"]          { display: none !important; }
/* Running indicator */
[data-testid="stAppRunningMan"]         { display: none !important; }
/* Top header bar — we show our own in the sidebar */
header[data-testid="stHeader"]          { display: none !important; }

/* ═══════════════════════════════════════════════════
   BASE RESET
═══════════════════════════════════════════════════ */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
}
.stApp {
    background: var(--bg) !important;
    color: var(--text) !important;
}
* { box-sizing: border-box; }

/* Scrollbar */
::-webkit-scrollbar { width:7px; height:7px; }
::-webkit-scrollbar-track { background:var(--bg); }
::-webkit-scrollbar-thumb { background:#d1cfc8; border-radius:4px; }
::-webkit-scrollbar-thumb:hover { background:#b8b5ad; }

/* ═══════════════════════════════════════════════════
   MAIN LAYOUT
═══════════════════════════════════════════════════ */
[data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
}
[data-testid="stAppViewBlockContainer"] {
    padding-top: 1.8rem !important;
    max-width: 1100px !important;
}
[data-testid="block-container"] {
    background: transparent !important;
}

/* ═══════════════════════════════════════════════════
   SIDEBAR TOGGLE BUTTON
═══════════════════════════════════════════════════ */
@keyframes togglePulse {
    0%,100% { box-shadow: 2px 0 12px rgba(26,39,68,0.25); }
    50%      { box-shadow: 2px 0 20px rgba(201,168,76,0.35); }
}
@keyframes arrowBounce {
    0%,100% { transform: translateX(0) translateY(-50%); }
    50%      { transform: translateX(2px) translateY(-50%); }
}

/* The toggle tab that sticks out from the sidebar edge */
[data-testid="collapsedControl"] {
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    width: 22px !important;
    height: 56px !important;
    background: linear-gradient(180deg, #1a2744 0%, #253461 100%) !important;
    border-radius: 0 10px 10px 0 !important;
    box-shadow: 2px 0 12px rgba(26,39,68,0.3) !important;
    cursor: pointer !important;
    position: fixed !important;
    top: 50% !important;
    transform: translateY(-50%) !important;
    z-index: 9999 !important;
    transition: width 0.2s ease, background 0.2s ease, box-shadow 0.2s ease !important;
    animation: togglePulse 3s ease-in-out infinite !important;
    border: none !important;
    outline: none !important;
}
[data-testid="collapsedControl"]:hover {
    width: 28px !important;
    background: linear-gradient(180deg, #c9a84c 0%, #e8c97a 100%) !important;
    box-shadow: 2px 0 20px rgba(201,168,76,0.4) !important;
    animation: arrowBounce 0.6s ease-in-out infinite !important;
}
[data-testid="collapsedControl"] svg {
    fill: #ffffff !important;
    width: 12px !important;
    height: 12px !important;
    flex-shrink: 0 !important;
}

/* ═══════════════════════════════════════════════════
   SIDEBAR — Deep Navy (Law Firm Feel)
═══════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: var(--navy) !important;
    border-right: none !important;
    box-shadow: 4px 0 24px rgba(26,39,68,0.12) !important;
    transition: width 0.3s cubic-bezier(0.4,0,0.2,1),
                min-width 0.3s cubic-bezier(0.4,0,0.2,1) !important;
}
[data-testid="stSidebar"] > div {
    background: var(--navy) !important;
}
[data-testid="stSidebar"] * {
    color: rgba(255,255,255,0.75) !important;
}
[data-testid="stSidebar"] strong,
[data-testid="stSidebar"] b {
    color: #ffffff !important;
    font-weight: 600 !important;
}
[data-testid="stSidebar"] .stMarkdown p,
[data-testid="stSidebar"] .stMarkdown li {
    color: rgba(255,255,255,0.72) !important;
    font-size: 0.83rem !important;
    line-height: 1.7 !important;
    animation: slideInLeft 0.35s ease forwards;
}
[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.1) !important;
    margin: 0.9rem 0 !important;
}
[data-testid="stSidebar"] .stCaption,
[data-testid="stSidebar"] [data-testid="stCaptionContainer"] * {
    color: rgba(255,255,255,0.45) !important;
    font-size: 0.73rem !important;
}
[data-testid="stSidebar"] .stTextInput input {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    color: #ffffff !important;
    border-radius: var(--radius-sm) !important;
    font-size: 0.82rem !important;
}
[data-testid="stSidebar"] .stTextInput input::placeholder {
    color: rgba(255,255,255,0.35) !important;
}
[data-testid="stSidebar"] .stTextInput input:focus {
    border-color: var(--gold) !important;
    background: rgba(255,255,255,0.12) !important;
    outline: none !important;
    box-shadow: 0 0 0 3px rgba(201,168,76,0.18) !important;
}
[data-testid="stSidebar"] .stTextInput label {
    color: rgba(255,255,255,0.6) !important;
    font-size: 0.75rem !important;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
[data-testid="stSidebar"] .stAlert {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    border-radius: var(--radius-sm) !important;
    padding: 0.5rem 0.75rem !important;
}
[data-testid="stSidebar"] .stAlert * {
    color: rgba(255,255,255,0.7) !important;
    font-size: 0.78rem !important;
}
/* Sign Out / sidebar buttons */
[data-testid="stSidebar"] .stButton > button {
    background: rgba(255,255,255,0.07) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    color: rgba(255,255,255,0.8) !important;
    border-radius: var(--radius-sm) !important;
    font-size: 0.8rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.02em !important;
    padding: 0.38rem 0.9rem !important;
    transition: var(--transition) !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(201,168,76,0.15) !important;
    border-color: rgba(201,168,76,0.4) !important;
    color: var(--gold-light) !important;
    transform: none !important;
}

/* ═══════════════════════════════════════════════════
   TYPOGRAPHY
═══════════════════════════════════════════════════ */
h1, h2, h3 {
    font-family: 'Playfair Display', Georgia, serif !important;
    color: var(--navy) !important;
    font-weight: 700 !important;
    line-height: 1.25 !important;
    letter-spacing: -0.01em !important;
}
h1 { font-size: 2rem !important; }
h2 { font-size: 1.55rem !important; }
h3 { font-size: 1.2rem !important; }
h4, h5, h6 {
    font-family: 'Inter', sans-serif !important;
    color: var(--navy) !important;
    font-weight: 600 !important;
}
p, li, span, label { color: var(--text-body) !important; }
.stMarkdown p { line-height: 1.72 !important; }
.stMarkdown strong { color: var(--navy) !important; font-weight: 600 !important; }

/* ═══════════════════════════════════════════════════
   BUTTONS
═══════════════════════════════════════════════════ */
.stButton > button {
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.875rem !important;
    letter-spacing: 0.01em !important;
    border-radius: var(--radius) !important;
    padding: 0.55rem 1.4rem !important;
    transition: var(--transition) !important;
    cursor: pointer !important;
    border: none !important;
    background: var(--navy) !important;
    color: #ffffff !important;
    box-shadow: var(--shadow-sm) !important;
}
.stButton > button:hover {
    background: var(--navy-light) !important;
    box-shadow: var(--shadow) !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active {
    transform: translateY(0px) !important;
    box-shadow: var(--shadow-sm) !important;
}
/* Primary type */
.stButton > [data-testid="baseButton-primary"],
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1a2744 0%, #253461 100%) !important;
    color: #ffffff !important;
    box-shadow: 0 4px 14px rgba(26,39,68,0.25) !important;
}
.stButton > [data-testid="baseButton-primary"]:hover,
.stButton > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #0f1a33 0%, #1a2744 100%) !important;
    box-shadow: 0 6px 20px rgba(26,39,68,0.3) !important;
    transform: translateY(-2px) !important;
}
/* Force white text on ALL button states — overrides any Streamlit default blue */
.stButton > button,
.stButton > button:visited,
.stButton > button:hover,
.stButton > button:active,
.stButton > button:focus,
.stButton > button p,
.stButton > button span,
.stButton > button div {
    color: #ffffff !important;
}
/* Download = gold */
.stDownloadButton > button {
    background: linear-gradient(135deg, var(--gold) 0%, var(--gold-light) 100%) !important;
    color: var(--navy) !important;
    font-weight: 600 !important;
    border: none !important;
    box-shadow: var(--shadow-gold) !important;
    border-radius: var(--radius) !important;
    padding: 0.55rem 1.4rem !important;
    transition: var(--transition) !important;
}
.stDownloadButton > button:hover {
    box-shadow: 0 8px 28px rgba(201,168,76,0.3) !important;
    transform: translateY(-2px) !important;
}

/* ═══════════════════════════════════════════════════
   FORM INPUTS
═══════════════════════════════════════════════════ */
.stTextInput > label,
.stTextArea > label,
.stSelectbox > label,
.stMultiSelect > label,
.stFileUploader > label,
.stSlider > label,
.stRadio > label,
.stCheckbox > label {
    font-size: 0.78rem !important;
    font-weight: 600 !important;
    color: var(--text-muted) !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
    margin-bottom: 0.35rem !important;
}
.stTextInput > div > div > input,
.stTextArea > div > div > textarea {
    background: var(--surface) !important;
    border: 1.5px solid var(--border-navy) !important;
    border-radius: var(--radius) !important;
    color: var(--text) !important;
    font-size: 0.9rem !important;
    font-family: 'Inter', sans-serif !important;
    padding: 0.6rem 0.9rem !important;
    transition: border-color 0.18s ease, box-shadow 0.18s ease !important;
    box-shadow: var(--shadow-sm) !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
    border-color: var(--navy) !important;
    box-shadow: 0 0 0 3px rgba(26,39,68,0.1) !important;
    outline: none !important;
}
.stTextInput > div > div > input::placeholder,
.stTextArea > div > div > textarea::placeholder {
    color: var(--text-light) !important;
    font-size: 0.87rem !important;
}

/* Select */
.stSelectbox > div > div,
.stMultiSelect > div > div {
    background: var(--surface) !important;
    border: 1.5px solid var(--border-navy) !important;
    border-radius: var(--radius) !important;
    color: var(--text) !important;
    box-shadow: var(--shadow-sm) !important;
}
.stSelectbox > div > div:hover,
.stMultiSelect > div > div:hover {
    border-color: var(--navy) !important;
}
[data-baseweb="select"] > div {
    background: var(--surface) !important;
    border-color: var(--border-navy) !important;
    border-radius: var(--radius) !important;
}

/* ═══════════════════════════════════════════════════
   TABS
═══════════════════════════════════════════════════ */
[data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 2px solid var(--border) !important;
    gap: 0 !important;
    padding: 0 !important;
}
[data-baseweb="tab"] {
    background: transparent !important;
    border: none !important;
    padding: 0.65rem 1.3rem !important;
    font-size: 0.85rem !important;
    font-weight: 500 !important;
    color: var(--text-muted) !important;
    font-family: 'Inter', sans-serif !important;
    border-bottom: 2.5px solid transparent !important;
    margin-bottom: -2px !important;
    transition: var(--transition) !important;
}
[data-baseweb="tab"]:hover {
    color: var(--navy) !important;
    background: var(--surface-2) !important;
    border-radius: var(--radius-sm) var(--radius-sm) 0 0 !important;
}
[aria-selected="true"][data-baseweb="tab"] {
    color: var(--navy) !important;
    font-weight: 600 !important;
    border-bottom-color: var(--navy) !important;
    background: transparent !important;
}
[data-baseweb="tab-panel"] {
    background: transparent !important;
    padding: 1.2rem 0 0 !important;
}

/* ═══════════════════════════════════════════════════
   METRICS
═══════════════════════════════════════════════════ */
[data-testid="stMetric"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-top: 3px solid var(--navy) !important;
    border-radius: var(--radius) !important;
    padding: 1.1rem 1.3rem !important;
    box-shadow: var(--shadow-sm) !important;
    transition: var(--transition) !important;
    animation: fadeInUp 0.4s ease both;
}
[data-testid="stMetric"]:hover {
    box-shadow: var(--shadow) !important;
    transform: translateY(-2px) !important;
    border-top-color: var(--gold) !important;
}
[data-testid="stMetricLabel"] {
    font-size: 0.73rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.07em !important;
    color: var(--text-muted) !important;
}
[data-testid="stMetricValue"] {
    font-size: 2rem !important;
    font-weight: 700 !important;
    color: var(--navy) !important;
    font-family: 'Playfair Display', serif !important;
    line-height: 1.15 !important;
}
[data-testid="stMetricDelta"] {
    font-size: 0.82rem !important;
    font-weight: 500 !important;
}

/* ═══════════════════════════════════════════════════
   EXPANDERS
═══════════════════════════════════════════════════ */
[data-testid="stExpander"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    box-shadow: var(--shadow-sm) !important;
    margin-bottom: 0.6rem !important;
    overflow: hidden !important;
    transition: var(--transition) !important;
}
[data-testid="stExpander"]:hover {
    border-color: var(--border-navy) !important;
    box-shadow: var(--shadow) !important;
}
[data-testid="stExpander"] summary {
    font-size: 0.88rem !important;
    font-weight: 600 !important;
    color: var(--navy) !important;
    padding: 0.85rem 1.1rem !important;
    background: var(--surface) !important;
}

/* ═══════════════════════════════════════════════════
   ALERTS / NOTICES
═══════════════════════════════════════════════════ */
[data-testid="stAlert"] {
    border-radius: var(--radius) !important;
    border: none !important;
    padding: 0.85rem 1.1rem !important;
    font-size: 0.86rem !important;
    animation: fadeIn 0.3s ease;
}
/* info */
[data-testid="stAlert"][data-baseweb="notification"] {
    background: #eef4ff !important;
    border-left: 4px solid var(--navy) !important;
}
div[data-testid="stNotification"] { border-radius: var(--radius) !important; }
.stSuccess  { background: #ecfdf5 !important; border-left: 4px solid var(--green) !important; }
.stWarning  { background: #fffbeb !important; border-left: 4px solid var(--amber) !important; }
.stError    { background: #fef2f2 !important; border-left: 4px solid var(--red) !important; }
.stInfo     { background: #eff6ff !important; border-left: 4px solid #3b82f6 !important; }

/* ═══════════════════════════════════════════════════
   FILE UPLOADER
═══════════════════════════════════════════════════ */
[data-testid="stFileUploader"] {
    background: var(--surface) !important;
    border: 2px dashed var(--border-navy) !important;
    border-radius: var(--radius-lg) !important;
    padding: 2rem 1.5rem !important;
    text-align: center !important;
    transition: var(--transition) !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--navy) !important;
    background: var(--surface-2) !important;
}
[data-testid="stFileUploader"] * { color: var(--text-muted) !important; }
[data-testid="stFileUploader"] small { font-size: 0.8rem !important; }

/* ═══════════════════════════════════════════════════
   PROGRESS BAR
═══════════════════════════════════════════════════ */
[data-testid="stProgressBar"] > div > div > div > div {
    background: linear-gradient(90deg, var(--navy), var(--gold)) !important;
    border-radius: 4px !important;
    transition: width 0.4s ease !important;
}
[data-testid="stProgressBar"] > div > div {
    background: var(--surface-2) !important;
    border-radius: 4px !important;
    height: 6px !important;
}

/* Spinner */
[data-testid="stSpinner"] > div {
    border-top-color: var(--navy) !important;
}

/* ═══════════════════════════════════════════════════
   DATA TABLE / DATAFRAME
═══════════════════════════════════════════════════ */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    overflow: hidden !important;
    box-shadow: var(--shadow-sm) !important;
}
[data-testid="stDataFrame"] th {
    background: var(--navy) !important;
    color: rgba(255,255,255,0.9) !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    padding: 0.65rem 1rem !important;
    border: none !important;
}
[data-testid="stDataFrame"] td {
    font-size: 0.85rem !important;
    color: var(--text-body) !important;
    padding: 0.6rem 1rem !important;
    border-bottom: 1px solid var(--border) !important;
}
[data-testid="stDataFrame"] tr:hover td {
    background: var(--surface-2) !important;
}
[data-testid="stDataFrame"] tr:nth-child(even) td {
    background: #fafaf7 !important;
}

/* ═══════════════════════════════════════════════════
   SIDEBAR NAV LINKS (page navigation)
═══════════════════════════════════════════════════ */
[data-testid="stSidebarNav"] a {
    color: rgba(255,255,255,0.7) !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    padding: 0.4rem 0.6rem !important;
    border-radius: var(--radius-sm) !important;
    transition: var(--transition) !important;
    letter-spacing: 0.01em !important;
}
[data-testid="stSidebarNav"] a:hover {
    color: #ffffff !important;
    background: rgba(255,255,255,0.08) !important;
}
[data-testid="stSidebarNav"] a[aria-current="page"] {
    color: var(--gold-light) !important;
    background: rgba(201,168,76,0.12) !important;
    font-weight: 600 !important;
}

/* ═══════════════════════════════════════════════════
   CUSTOM HTML COMPONENTS — Cards & Containers
═══════════════════════════════════════════════════ */
.page-header {
    padding: 1.4rem 0 1rem;
    border-bottom: 2px solid var(--border);
    margin-bottom: 1.6rem;
    animation: fadeInUp 0.35s ease both;
}
.page-header h2 {
    font-family: 'Playfair Display', serif !important;
    font-size: 1.75rem !important;
    color: var(--navy) !important;
    margin: 0 0 0.2rem !important;
    font-weight: 700 !important;
}
.page-header .sub {
    color: var(--text-muted) !important;
    font-size: 0.85rem !important;
    margin: 0 !important;
    font-weight: 400 !important;
}

/* metric-card */
.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-top: 3px solid var(--navy);
    border-radius: var(--radius);
    padding: 1.25rem 1.4rem;
    box-shadow: var(--shadow-sm);
    transition: var(--transition);
    animation: fadeInUp 0.4s ease both;
}
.metric-card:hover {
    box-shadow: var(--shadow);
    transform: translateY(-2px);
    border-top-color: var(--gold);
}
.metric-card .mc-value {
    font-family: 'Playfair Display', serif;
    font-size: 2.1rem;
    font-weight: 700;
    color: var(--navy);
    line-height: 1.1;
    margin-bottom: 0.25rem;
}
.metric-card .mc-label {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: var(--text-light);
}
.metric-card .mc-delta {
    font-size: 0.8rem;
    color: var(--green);
    margin-top: 0.3rem;
    font-weight: 500;
}

/* stat-strip */
.stat-strip {
    background: var(--surface);
    border: 1px solid var(--border);
    border-left: 4px solid var(--gold);
    border-radius: var(--radius);
    padding: 1rem 1.2rem;
    display: flex;
    flex-direction: column;
    gap: 0.15rem;
    box-shadow: var(--shadow-sm);
    animation: scaleIn 0.3s ease both;
}
.stat-strip .sv {
    font-family: 'Playfair Display', serif;
    font-size: 1.8rem;
    font-weight: 700;
    color: var(--navy);
    line-height: 1.1;
}
.stat-strip .sl {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--text-light);
}
.stat-strip .sd {
    font-size: 0.8rem;
    color: var(--green);
    font-weight: 500;
}

/* section-title */
.section-title {
    font-size: 0.7rem !important;
    font-weight: 700 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    color: var(--text-light) !important;
    margin: 1.4rem 0 0.6rem !important;
    padding-bottom: 0.35rem !important;
    border-bottom: 1px solid var(--border) !important;
}

/* group-header */
.group-header {
    font-family: 'Playfair Display', serif;
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--navy);
    padding: 0.6rem 0 0.4rem;
    border-bottom: 1px solid var(--border);
    margin-bottom: 0.8rem;
}

/* notice / disclaimer / privilege */
.notice-box {
    background: var(--gold-pale);
    border: 1px solid var(--border-gold);
    border-left: 4px solid var(--gold);
    border-radius: var(--radius);
    padding: 0.85rem 1.1rem;
    font-size: 0.84rem;
    color: #78560a;
    margin: 0.8rem 0;
    animation: fadeIn 0.3s ease;
}
.disclaimer-box {
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    border-left: 4px solid #3b82f6;
    border-radius: var(--radius);
    padding: 0.85rem 1.1rem;
    font-size: 0.84rem;
    color: #1e40af;
    margin: 0.8rem 0;
    animation: fadeIn 0.3s ease;
}
.privilege-box {
    background: #fef9ee;
    border: 1px solid #fde68a;
    border-left: 4px solid var(--amber);
    border-radius: var(--radius);
    padding: 0.85rem 1.1rem;
    font-size: 0.84rem;
    color: #92400e;
    margin: 0.8rem 0;
    animation: fadeIn 0.3s ease;
}

/* placeholder-state */
.placeholder-state {
    text-align: center;
    padding: 3rem 2rem;
    background: var(--surface);
    border: 2px dashed var(--border-navy);
    border-radius: var(--radius-xl);
    animation: fadeInUp 0.4s ease;
}
.placeholder-state .ph-icon {
    font-size: 3rem;
    margin-bottom: 0.8rem;
    animation: float 3s ease-in-out infinite;
    display: inline-block;
}
.placeholder-state h3 {
    color: var(--navy) !important;
    font-family: 'Playfair Display', serif !important;
    margin-bottom: 0.5rem;
}
.placeholder-state .ph-desc {
    color: var(--text-muted) !important;
    font-size: 0.9rem !important;
    max-width: 440px;
    margin: 0 auto 1.5rem;
}
.placeholder-state .ph-list {
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem 1.2rem;
    font-size: 0.83rem;
    color: var(--text-body);
}
.placeholder-state li { margin-bottom: 0.3rem; }

/* feature-card */
.feature-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    position: relative;
    overflow: hidden;
    transition: var(--transition);
    animation: fadeInUp 0.4s ease both;
}
.feature-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: linear-gradient(90deg, var(--navy), var(--gold));
}
.feature-card:hover {
    box-shadow: var(--shadow-lg);
    transform: translateY(-3px);
    border-color: var(--border-navy);
}
.feature-card .fc-badge {
    position: absolute;
    top: 1rem;
    right: 1rem;
}
.feature-card .fc-icon {
    font-size: 2rem;
    margin-bottom: 0.7rem;
}
.feature-card .fc-name {
    font-family: 'Playfair Display', serif;
    font-size: 1.05rem;
    font-weight: 700;
    color: var(--navy);
    margin-bottom: 0.4rem;
}
.feature-card .fc-desc {
    font-size: 0.83rem;
    color: var(--text-muted);
    line-height: 1.6;
    margin-bottom: 0.8rem;
}
.feature-card .fc-best {
    font-size: 0.75rem;
    color: var(--text-light);
    font-weight: 500;
}

/* tool-card */
.tool-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.2rem 1.4rem;
    transition: var(--transition);
    animation: scaleIn 0.3s ease both;
    cursor: pointer;
}
.tool-card:hover {
    border-color: var(--border-navy);
    box-shadow: var(--shadow);
    transform: translateY(-2px);
}

/* Badges */
.badge-available {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    padding: 0.18rem 0.65rem;
    background: #ecfdf5;
    color: #065f46;
    border: 1px solid #a7f3d0;
    border-radius: 999px;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.02em;
}
.badge-beta {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    padding: 0.18rem 0.65rem;
    background: #eff6ff;
    color: #1e40af;
    border: 1px solid #bfdbfe;
    border-radius: 999px;
    font-size: 0.7rem;
    font-weight: 600;
}
.badge-soon {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    padding: 0.18rem 0.65rem;
    background: #f9fafb;
    color: var(--text-muted);
    border: 1px solid var(--border);
    border-radius: 999px;
    font-size: 0.7rem;
    font-weight: 600;
}

/* Risk badges */
.risk-critical { display:inline-block;padding:.18rem .6rem;background:#fee2e2;color:#991b1b;border-radius:999px;font-size:.7rem;font-weight:700;letter-spacing:.03em; }
.risk-high     { display:inline-block;padding:.18rem .6rem;background:#ffedd5;color:#9a3412;border-radius:999px;font-size:.7rem;font-weight:700; }
.risk-medium   { display:inline-block;padding:.18rem .6rem;background:#fffbeb;color:#92400e;border-radius:999px;font-size:.7rem;font-weight:700; }
.risk-low      { display:inline-block;padding:.18rem .6rem;background:#ecfdf5;color:#065f46;border-radius:999px;font-size:.7rem;font-weight:700; }

/* Notification pulse */
.notif-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.4rem;
    background: #fef3c7;
    border: 1px solid #fde68a;
    border-radius: 999px;
    padding: 0.25rem 0.75rem;
    font-size: 0.78rem;
    font-weight: 600;
    color: #92400e;
}
.notif-dot {
    width: 8px;
    height: 8px;
    background: var(--amber);
    border-radius: 50%;
    animation: pulse-dot 1.5s ease-in-out infinite;
    display: inline-block;
}

/* ═══════════════════════════════════════════════════
   CODE BLOCKS
═══════════════════════════════════════════════════ */
code {
    background: var(--surface-2) !important;
    color: var(--navy) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    padding: 0.15em 0.4em !important;
    font-size: 0.82em !important;
    font-family: 'JetBrains Mono', 'Fira Code', monospace !important;
}
pre {
    background: #1e2536 !important;
    border: none !important;
    border-radius: var(--radius) !important;
    padding: 1.2rem 1.4rem !important;
    box-shadow: var(--shadow) !important;
}
pre code {
    background: transparent !important;
    border: none !important;
    color: #e2e8f4 !important;
    padding: 0 !important;
    font-size: 0.83rem !important;
}

/* ═══════════════════════════════════════════════════
   RADIO / CHECKBOX
═══════════════════════════════════════════════════ */
[data-testid="stRadio"] > div {
    gap: 0.5rem !important;
}
[data-testid="stRadio"] label {
    background: var(--surface) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    padding: 0.5rem 0.9rem !important;
    font-size: 0.84rem !important;
    color: var(--text-body) !important;
    cursor: pointer !important;
    transition: var(--transition) !important;
}
[data-testid="stRadio"] label:hover {
    border-color: var(--navy) !important;
    background: var(--surface-2) !important;
}
[data-testid="stRadio"] [aria-checked="true"] + label,
[data-testid="stRadio"] label:has(input:checked) {
    border-color: var(--navy) !important;
    background: #eef2ff !important;
    color: var(--navy) !important;
    font-weight: 600 !important;
}

/* ═══════════════════════════════════════════════════
   DIVIDER
═══════════════════════════════════════════════════ */
hr {
    border: none !important;
    border-top: 1px solid var(--border) !important;
    margin: 1rem 0 !important;
}

/* ═══════════════════════════════════════════════════
   CAPTION / SMALL TEXT
═══════════════════════════════════════════════════ */
.stCaption,
[data-testid="stCaptionContainer"] * {
    color: var(--text-light) !important;
    font-size: 0.78rem !important;
    line-height: 1.55 !important;
}

</style>
"""


def inject_css() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = "", icon: str = "") -> None:
    heading = f"{icon} {title}" if icon else title
    sub_html = f'<p class="sub">{subtitle}</p>' if subtitle else ""
    st.markdown(
        f'<div class="page-header"><h2>{heading}</h2>{sub_html}</div>',
        unsafe_allow_html=True,
    )


def slim_header(icon: str, title: str, subtitle: str = "") -> None:
    """Alias for page_header with positional icon argument (used across all pages)."""
    page_header(title=title, subtitle=subtitle, icon=icon)


def disclaimer() -> None:
    st.markdown(
        '<div class="disclaimer-box">ℹ️ <strong>Disclaimer:</strong> This tool assists with legal '
        "drafting and review. It does not replace the professional judgment of a qualified lawyer. "
        "Do not rely solely on AI output for final legal decisions.</div>",
        unsafe_allow_html=True,
    )


def confidentiality_notice() -> None:
    st.markdown(
        '<div class="notice-box">🔐 <strong>Confidentiality Notice:</strong> Do not upload highly '
        "sensitive or legally privileged material unless your organization has approved this tool. "
        "All files are processed in memory and auto-deleted after your session.</div>",
        unsafe_allow_html=True,
    )


def privilege_warning() -> None:
    st.markdown(
        '<div class="privilege-box">⚠️ <strong>Privilege Warning:</strong> This document may contain '
        "legally privileged or confidential information. Ensure you have authority to process it "
        "using this tool.</div>",
        unsafe_allow_html=True,
    )


def risk_badge(level: str) -> str:
    level = (level or "low").lower()
    cls = {"critical": "risk-critical", "high": "risk-high", "medium": "risk-medium"}.get(level, "risk-low")
    return f'<span class="{cls}">{level.title()}</span>'


def status_badge(status: str) -> str:
    s = (status or "").lower()
    if "available" in s or s == "live":
        return '<span class="badge-available">● Available</span>'
    if "beta" in s:
        return '<span class="badge-beta">◐ Beta</span>'
    return '<span class="badge-soon">◌ Coming Soon</span>'


def section(title: str) -> None:
    st.markdown(f'<p class="section-title">{title}</p>', unsafe_allow_html=True)


def group_header(title: str) -> None:
    st.markdown(f'<div class="group-header">{title}</div>', unsafe_allow_html=True)


def placeholder_feature(
    icon: str,
    name: str,
    description: str,
    capabilities: list[str],
    outputs: list[str],
) -> None:
    caps_html = "".join(f"<li>{c}</li>" for c in capabilities)
    outs_html = "".join(f"<li>{o}</li>" for o in outputs)
    st.markdown(
        f"""
        <div class="placeholder-state">
            <div class="ph-icon">{icon}</div>
            <h3>{name}</h3>
            <p class="ph-desc">{description}</p>
            <div style="display:flex;gap:2rem;justify-content:center;flex-wrap:wrap;text-align:left">
                <div class="ph-list">
                    <p style="font-size:0.68rem;font-weight:700;color:var(--text-light);text-transform:uppercase;
                       letter-spacing:0.08em;margin:0 0 0.4rem">You will be able to</p>
                    <ul style="margin:0;padding-left:1.2rem">{caps_html}</ul>
                </div>
                <div class="ph-list">
                    <p style="font-size:0.68rem;font-weight:700;color:var(--text-light);text-transform:uppercase;
                       letter-spacing:0.08em;margin:0 0 0.4rem">Expected output</p>
                    <ul style="margin:0;padding-left:1.2rem">{outs_html}</ul>
                </div>
            </div>
            <br>
            <span class="badge-soon">◌ Coming Soon</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def feature_card(icon: str, name: str, desc: str, best_for: str, status: str = "available") -> str:
    badge = status_badge(status)
    return (
        f'<div class="feature-card">'
        f'<div class="fc-badge">{badge}</div>'
        f'<div class="fc-icon">{icon}</div>'
        f'<div class="fc-name">{name}</div>'
        f'<div class="fc-desc">{desc}</div>'
        f'<div class="fc-best">Best for: {best_for}</div>'
        f'</div>'
    )


def stat_strip(value: str, label: str, delta: str = "") -> str:
    delta_html = f'<div class="sd">{delta}</div>' if delta else ""
    return (
        f'<div class="stat-strip">'
        f'<div class="sv">{value}</div>'
        f'<div class="sl">{label}</div>'
        f'{delta_html}</div>'
    )
