import streamlit as st

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Playfair+Display:wght@600;700&display=swap');

/* ═════���═════════════════════════════════════════════
   DESIGN TOKENS
═══════════════���═══════════════════════════════════ */
:root {
    --bg:           #0b0d14;
    --bg-card:      #10131e;
    --bg-elevated:  #161b2e;
    --bg-hover:     #1c2235;
    --border:       rgba(255,255,255,0.06);
    --border-blue:  rgba(79,124,247,0.25);
    --border-gold:  rgba(212,168,83,0.3);
    --text:         #eef0f8;
    --text-dim:     #8a93ab;
    --text-muted:   #525c72;
    --blue:         #4f7cf7;
    --blue-glow:    rgba(79,124,247,0.18);
    --blue-dark:    #3563e0;
    --gold:         #d4a853;
    --gold-light:   #f0c96a;
    --gold-glow:    rgba(212,168,83,0.15);
    --green:        #22c55e;
    --red:          #ef4444;
    --amber:        #f59e0b;
    --radius-sm:    8px;
    --radius:       12px;
    --radius-lg:    18px;
    --shadow:       0 4px 24px rgba(0,0,0,0.4);
    --shadow-blue:  0 8px 32px rgba(79,124,247,0.15);
    --transition:   all 0.2s cubic-bezier(0.4,0,0.2,1);
}

/* ════���══════════════════════════════════════════════
   BASE RESET
══════════════════��══════════════════════════════��═ */
html, body, [class*="css"], .stApp {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

/* Custom scrollbar */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--bg-elevated); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: var(--blue); }

/* ════════���══════════════════════════════════════════
   MAIN LAYOUT
══════════════════════════════════��════════════════ */
[data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
}
[data-testid="stAppViewBlockContainer"] {
    padding-top: 1.5rem !important;
}
[data-testid="block-container"] {
    background: transparent !important;
}
header[data-testid="stHeader"] {
    background: var(--bg) !important;
    border-bottom: 1px solid var(--border) !important;
}

/* ══════════��═══════════════════════════��════════════
   SIDEBAR
═══════════════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: var(--bg-card) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] > div {
    background: var(--bg-card) !important;
}
[data-testid="stSidebar"] * {
    color: var(--text-dim) !important;
}
[data-testid="stSidebar"] strong,
[data-testid="stSidebar"] b {
    color: var(--text) !important;
    font-weight: 600 !important;
}
[data-testid="stSidebar"] .stButton > button {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-dim) !important;
    border-radius: var(--radius-sm) !important;
    font-size: 0.82rem !important;
    transition: var(--transition) !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
    border-color: var(--border-blue) !important;
    color: var(--text) !important;
    background: var(--bg-hover) !important;
}
[data-testid="stSidebarNavItems"] a {
    color: var(--text-dim) !important;
    border-radius: var(--radius-sm) !important;
    font-size: 0.85rem !important;
    transition: var(--transition) !important;
}
[data-testid="stSidebarNavItems"] a:hover,
[data-testid="stSidebarNavItems"] [aria-current="page"] {
    background: var(--bg-elevated) !important;
    color: var(--text) !important;
}
[data-testid="stSidebar"] hr {
    border-color: var(--border) !important;
    margin: 0.75rem 0 !important;
}
[data-testid="stSidebar"] .stCaption,
[data-testid="stSidebar"] small {
    color: var(--text-muted) !important;
    font-size: 0.72rem !important;
}
/* Sidebar nav section labels */
[data-testid="stSidebarNavSeparator"] {
    color: var(--text-muted) !important;
    font-size: 0.65rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
}

/* ════════════════════════════════════════���══════════
   BUTTONS
═══════════════════════════════════════════════════ */
.stButton > button {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border) !important;
    color: var(--text-dim) !important;
    border-radius: var(--radius-sm) !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    transition: var(--transition) !important;
    letter-spacing: 0.01em !important;
}
.stButton > button:hover {
    background: var(--bg-hover) !important;
    border-color: var(--border-blue) !important;
    color: var(--text) !important;
    box-shadow: var(--shadow-blue) !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, var(--blue) 0%, var(--blue-dark) 100%) !important;
    border: none !important;
    color: #fff !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 16px rgba(79,124,247,0.3) !important;
}
.stButton > button[kind="primary"]:hover {
    box-shadow: 0 6px 24px rgba(79,124,247,0.45) !important;
    transform: translateY(-1px) !important;
    filter: brightness(1.08) !important;
}
.stDownloadButton > button {
    background: linear-gradient(135deg, var(--gold) 0%, var(--gold-light) 100%) !important;
    color: #0b0d14 !important;
    border: none !important;
    font-weight: 600 !important;
    border-radius: var(--radius-sm) !important;
    box-shadow: 0 4px 16px rgba(212,168,83,0.3) !important;
}
.stDownloadButton > button:hover {
    box-shadow: 0 6px 24px rgba(212,168,83,0.45) !important;
    transform: translateY(-1px) !important;
}

/* ═══════════════════════════════════════════════════
   FORM INPUTS
═══════════��═════════════════════════���═════════════ */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stNumberInput > div > div > input {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text) !important;
    font-family: 'Inter', sans-serif !important;
    transition: var(--transition) !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus,
.stNumberInput > div > div > input:focus {
    border-color: var(--blue) !important;
    box-shadow: 0 0 0 3px var(--blue-glow) !important;
    outline: none !important;
}
.stTextInput label, .stTextArea label,
.stNumberInput label, .stSelectbox label,
.stRadio label, .stCheckbox label {
    color: var(--text-dim) !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.02em !important;
}
.stSelectbox > div > div {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    color: var(--text) !important;
}
.stSelectbox > div > div:focus-within {
    border-color: var(--blue) !important;
    box-shadow: 0 0 0 3px var(--blue-glow) !important;
}
[data-baseweb="select"] > div {
    background: var(--bg-elevated) !important;
    border-color: var(--border) !important;
    color: var(--text) !important;
}
[data-baseweb="menu"] {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius-sm) !important;
    box-shadow: var(--shadow) !important;
}
[data-baseweb="option"]:hover {
    background: var(--bg-hover) !important;
}

/* ═════════════════════════════════���═════════════════
   TABS
═══════════════���══════════════════════════════���════ */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 0.25rem !important;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important;
    color: var(--text-dim) !important;
    border-radius: var(--radius-sm) var(--radius-sm) 0 0 !important;
    font-size: 0.84rem !important;
    font-weight: 500 !important;
    padding: 0.6rem 1rem !important;
    border: none !important;
    transition: var(--transition) !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: var(--text) !important;
    background: var(--bg-elevated) !important;
}
.stTabs [aria-selected="true"] {
    color: var(--text) !important;
    border-bottom: 2px solid var(--blue) !important;
    font-weight: 600 !important;
}
.stTabs [data-baseweb="tab-panel"] {
    padding-top: 1.25rem !important;
}

/* ═══════════════════════════════════════════════════
   METRICS
═════════════════════════════════════════════��═════ */
[data-testid="stMetric"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    padding: 1.1rem 1.25rem !important;
    transition: var(--transition) !important;
}
[data-testid="stMetric"]:hover {
    border-color: var(--border-blue) !important;
    box-shadow: var(--shadow-blue) !important;
}
[data-testid="stMetricLabel"] {
    color: var(--text-muted) !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.08em !important;
    text-transform: uppercase !important;
}
[data-testid="stMetricValue"] {
    color: var(--text) !important;
    font-size: 1.9rem !important;
    font-weight: 700 !important;
    line-height: 1.1 !important;
}
[data-testid="stMetricDelta"] { font-size: 0.78rem !important; }

/* ═════════════��══════════════════════════���══════════
   EXPANDERS
═════════════���═════════════════════════════════════ */
[data-testid="stExpander"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    margin-bottom: 0.5rem !important;
    transition: var(--transition) !important;
}
[data-testid="stExpander"]:hover {
    border-color: var(--border-blue) !important;
}
[data-testid="stExpander"] summary {
    color: var(--text) !important;
    font-weight: 500 !important;
    font-size: 0.88rem !important;
}

/* ═════════════���═════════════════════════════════════
   ALERTS
════════════════════��════════════════════════���═════ */
[data-testid="stAlert"] {
    border-radius: var(--radius) !important;
    border-left-width: 3px !important;
    font-size: 0.84rem !important;
}
.stSuccess  { background: rgba(34,197,94,0.08) !important; border-color: var(--green) !important; color: #86efac !important; }
.stError    { background: rgba(239,68,68,0.08)  !important; border-color: var(--red)   !important; color: #fca5a5 !important; }
.stWarning  { background: rgba(245,158,11,0.08) !important; border-color: var(--amber) !important; color: #fcd34d !important; }
.stInfo     { background: rgba(79,124,247,0.08) !important; border-color: var(--blue)  !important; color: #93c5fd !important; }

/* ══════��══════════════════════════════��═════════════
   DIVIDER
═══════════════════════════════════════════════���═══ */
hr, [data-testid="stDivider"] {
    border-color: var(--border) !important;
    margin: 1rem 0 !important;
}

/* ══════════════════════════════════��════════════════
   CAPTIONS & MARKDOWN
════════════════���════════════════════════���═════════ */
.stCaption, [data-testid="stCaptionContainer"] {
    color: var(--text-muted) !important;
    font-size: 0.75rem !important;
}
.stMarkdown p { color: var(--text-dim) !important; font-size: 0.9rem !important; line-height: 1.65 !important; }
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3 { color: var(--text) !important; font-weight: 700 !important; }
.stMarkdown h4, .stMarkdown h5, .stMarkdown h6 { color: var(--text-dim) !important; font-weight: 600 !important; }
.stMarkdown a { color: var(--blue) !important; text-decoration: none !important; }
.stMarkdown a:hover { color: var(--gold) !important; }
.stMarkdown code { background: var(--bg-elevated) !important; color: var(--gold) !important;
    border-radius: 4px !important; padding: 0.1em 0.4em !important; font-size: 0.82em !important; }

/* ════��══════════════════════════════════════════════
   FILE UPLOADER
════════════════��══════════════════════════════════ */
[data-testid="stFileUploader"] {
    border: 2px dashed var(--border-blue) !important;
    border-radius: var(--radius) !important;
    background: rgba(79,124,247,0.03) !important;
    transition: var(--transition) !important;
}
[data-testid="stFileUploader"]:hover {
    border-color: var(--blue) !important;
    background: rgba(79,124,247,0.06) !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] {
    color: var(--text-muted) !important;
}

/* ═══════════════════════════════════════════════════
   CODE BLOCKS
════════��══════════════════════════════════════════ */
[data-testid="stCode"] > div,
.stCode {
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border) !important;
    border-radius: var(--radius) !important;
    color: var(--text) !important;
}

/* ═══════════════════════════��═══════════════════════
   PROGRESS BAR
═══════════════════════════════════════��═══════════ */
[data-testid="stProgressBar"] > div > div {
    background: linear-gradient(90deg, var(--blue), var(--gold)) !important;
    border-radius: 4px !important;
}
[data-testid="stProgressBar"] > div {
    background: var(--bg-elevated) !important;
    border-radius: 4px !important;
}

/* ════���════════════════════��═════════════════════════
   SPINNER
═════════════════════════════════════════════���═════ */
[data-testid="stSpinner"] > div > div {
    border-top-color: var(--blue) !important;
}

/* ═══════════════════════════════════════════════════
   PAGE HERO HEADER
═══════════════════════════════════════════════════ */
.hero {
    position: relative;
    background: linear-gradient(135deg, #0d1b3e 0%, #0f2460 50%, #1a3580 100%);
    border: 1px solid var(--border-blue);
    border-radius: var(--radius-lg);
    padding: 3rem 2.5rem;
    margin-bottom: 2rem;
    text-align: center;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute; inset: 0;
    background: radial-gradient(ellipse at 50% -20%, rgba(79,124,247,0.3) 0%, transparent 70%);
    pointer-events: none;
}
.hero h1 {
    margin: 0 0 0.5rem 0;
    font-size: 2.2rem;
    font-weight: 800;
    color: #fff;
    letter-spacing: -0.02em;
}
.hero .sub {
    margin: 0;
    color: rgba(255,255,255,0.65);
    font-size: 0.95rem;
    font-weight: 400;
}
.hero .badge {
    display: inline-block;
    margin-top: 1rem;
    background: rgba(212,168,83,0.12);
    border: 1px solid rgba(212,168,83,0.35);
    color: var(--gold-light);
    border-radius: 20px;
    padding: 0.3rem 1rem;
    font-size: 0.75rem;
    font-weight: 500;
    letter-spacing: 0.03em;
}

/* ═════════��═══════════════════��═════════════════════
   SLIM PAGE HEADER
═══════���══════════════════════════════════���════════ */
.page-header {
    display: flex;
    align-items: baseline;
    gap: 1rem;
    padding-bottom: 1rem;
    margin-bottom: 1.5rem;
    border-bottom: 1px solid var(--border);
}
.page-header h2 {
    color: var(--text) !important;
    font-size: 1.4rem;
    font-weight: 700;
    margin: 0;
    letter-spacing: -0.01em;
}
.page-header .ph-sub {
    color: var(--text-muted);
    font-size: 0.82rem;
    margin: 0;
    font-weight: 400;
}

/* ═════════��═══════════════════════════════���═════════
   SECTION TITLE
═══════════════��════════════════════════════��══════ */
.section-title {
    color: var(--text) !important;
    font-size: 0.95rem;
    font-weight: 600;
    margin: 0 0 1rem 0;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--border);
    letter-spacing: -0.01em;
}

/* ═════════���═════════════════════════════════════════
   GROUP HEADER
═════════��═════════════════════════════���═══════════ */
.group-header {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: var(--bg-elevated);
    border: 1px solid var(--border);
    border-left: 3px solid var(--gold);
    border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
    padding: 0.4rem 1rem;
    margin: 1.25rem 0 0.85rem 0;
    color: var(--text-dim) !important;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    width: 100%;
}

/* ═══════════════════════════════════════════════════
   METRIC CARD (custom HTML)
═════════════════��═══════════════════════���═════════ */
.metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.25rem 1rem;
    text-align: center;
    transition: var(--transition);
}
.metric-card:hover {
    border-color: var(--border-blue);
    box-shadow: var(--shadow-blue);
}
.metric-card .val {
    font-size: 2rem;
    font-weight: 700;
    color: var(--text);
    line-height: 1;
}
.metric-card .lbl {
    font-size: 0.7rem;
    color: var(--text-muted);
    margin-top: 0.35rem;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    font-weight: 600;
}

/* ════════════════════════════════════════��══════════
   STAT STRIP
═══════════════════════════════════════════════════ */
.stat-strip {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.1rem 1.25rem;
    text-align: center;
    transition: var(--transition);
}
.stat-strip:hover { border-color: var(--border-blue); }
.stat-strip .sv {
    font-size: 1.9rem;
    font-weight: 700;
    color: var(--text);
    line-height: 1;
}
.stat-strip .sl {
    font-size: 0.68rem;
    color: var(--text-muted);
    margin-top: 0.3rem;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    font-weight: 600;
}
.stat-strip .sd { font-size: 0.75rem; color: var(--green); margin-top: 0.15rem; }

/* ═══════════════════════════════════════���═══════════
   FEATURE / TOOL CARDS
═══════════════��═══════════════════════════════════ */
.feature-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.25rem;
    height: 100%;
    transition: var(--transition);
    position: relative;
}
.feature-card:hover {
    border-color: var(--border-blue);
    box-shadow: var(--shadow-blue);
    transform: translateY(-2px);
}
.feature-card .fc-icon  { font-size: 1.4rem; margin-bottom: 0.5rem; }
.feature-card .fc-name  { color: var(--text); font-size: 0.88rem; font-weight: 600; margin: 0 0 0.25rem; }
.feature-card .fc-desc  { color: var(--text-dim); font-size: 0.78rem; margin: 0 0 0.4rem; line-height: 1.5; }
.feature-card .fc-best  { color: var(--text-muted); font-size: 0.7rem; font-style: italic; }
.feature-card .fc-badge { position: absolute; top: 0.85rem; right: 0.85rem; }

.tool-card, .feat-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.25rem 1rem;
    text-align: center;
    transition: var(--transition);
    height: 100%;
}
.tool-card:hover, .feat-card:hover {
    border-color: var(--border-blue);
    box-shadow: var(--shadow-blue);
}
.tool-card .icon, .feat-card .icon { font-size: 1.6rem; margin-bottom: 0.5rem; }
.tool-card h4, .feat-card h4 { margin: 0 0 0.3rem; color: var(--text); font-size: 0.88rem; font-weight: 600; }
.tool-card p,  .feat-card p  { margin: 0; color: var(--text-dim); font-size: 0.75rem; }

/* ═══════════════════════════════════════════════════
   QUICK ACTION CARD
═══════════��═════════════════════���═════════════════ */
.quick-action-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.25rem 1rem;
    text-align: center;
    transition: var(--transition);
    height: 100%;
    cursor: pointer;
}
.quick-action-card:hover {
    border-color: var(--border-blue);
    box-shadow: var(--shadow-blue);
    transform: translateY(-2px);
}
.quick-action-card .qa-icon { font-size: 1.5rem; margin-bottom: 0.4rem; }
.quick-action-card h5 { color: var(--text); font-size: 0.82rem; font-weight: 600; margin: 0 0 0.15rem; }
.quick-action-card p  { color: var(--text-muted); font-size: 0.7rem; margin: 0; }

/* ══════════════════════════════════���════════════════
   INTEGRATION CARD
═══════════════════════════════════════════════════ */
.int-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.25rem;
    text-align: center;
    transition: var(--transition);
}
.int-card:hover { border-color: var(--border-blue); box-shadow: var(--shadow-blue); }
.int-card .int-icon { font-size: 1.75rem; margin-bottom: 0.5rem; }
.int-card h5 { color: var(--text); font-size: 0.85rem; font-weight: 600; margin: 0 0 0.2rem; }
.int-card p  { color: var(--text-dim); font-size: 0.75rem; margin: 0; }

/* ═════════════════════════════════════��═════════════
   STATUS BADGES
═══════════════���═══════════════════════════════════ */
.badge-available {
    background: rgba(34,197,94,0.1);
    color: #4ade80;
    border: 1px solid rgba(34,197,94,0.25);
    border-radius: 20px; padding: 2px 10px;
    font-size: 0.7rem; font-weight: 600;
}
.badge-soon {
    background: var(--bg-elevated);
    color: var(--text-muted);
    border: 1px solid var(--border);
    border-radius: 20px; padding: 2px 10px;
    font-size: 0.7rem; font-weight: 600;
}
.badge-beta {
    background: rgba(79,124,247,0.1);
    color: #93c5fd;
    border: 1px solid var(--border-blue);
    border-radius: 20px; padding: 2px 10px;
    font-size: 0.7rem; font-weight: 600;
}

/* ═══════════���═══════════════════════════════════════
   RISK BADGES
═══════════════════════════════════════════════════ */
.risk-critical { background: rgba(239,68,68,0.1); color: #fca5a5; border: 1px solid rgba(239,68,68,0.25); border-radius: 20px; padding: 2px 10px; font-size: 0.72rem; font-weight: 700; }
.risk-high     { background: rgba(249,115,22,0.1); color: #fdba74; border: 1px solid rgba(249,115,22,0.25); border-radius: 20px; padding: 2px 10px; font-size: 0.72rem; font-weight: 600; }
.risk-medium   { background: rgba(245,158,11,0.1); color: #fcd34d; border: 1px solid rgba(245,158,11,0.25); border-radius: 20px; padding: 2px 10px; font-size: 0.72rem; font-weight: 600; }
.risk-low      { background: rgba(34,197,94,0.1);  color: #86efac; border: 1px solid rgba(34,197,94,0.25);  border-radius: 20px; padding: 2px 10px; font-size: 0.72rem; font-weight: 600; }

/* ═════════════════��═════════════════════════════════
   GENERAL BADGES
═══════════════════════════════════════════════════ */
.badge-doc       { display:inline-block; background:rgba(79,124,247,0.1); color:#93c5fd; border:1px solid var(--border-blue); border-radius:20px; padding:0.15rem 0.65rem; font-size:0.72rem; font-weight:600; }
.badge-conf-high { background:rgba(34,197,94,0.1); color:#86efac; border:1px solid rgba(34,197,94,0.25); border-radius:20px; padding:0.15rem 0.65rem; font-size:0.72rem; font-weight:600; }
.badge-conf-low  { background:rgba(245,158,11,0.1); color:#fcd34d; border:1px solid rgba(245,158,11,0.25); border-radius:20px; padding:0.15rem 0.65rem; font-size:0.72rem; font-weight:600; }
.issue-badge     { background:rgba(167,139,250,0.1); color:#c4b5fd; border:1px solid rgba(167,139,250,0.25); border-radius:20px; padding:2px 10px; font-size:0.72rem; font-weight:500; }

/* ═══════════��═════════════════════════════��═════════
   ACTIVITY ITEM
═══════════════════════════════════════════��═══════ */
.activity-item {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 0.7rem 1rem;
    margin-bottom: 0.4rem;
    transition: var(--transition);
}
.activity-item:hover { border-color: var(--border-blue); }
.activity-item .ai-title { font-size: 0.83rem; font-weight: 500; color: var(--text); }
.activity-item .ai-meta  { font-size: 0.72rem; color: var(--text-muted); margin-top: 0.1rem; }

/* ══════════════════════════════════════════���════════
   MATTER ROW
═══════════════════════════════════════════════════ */
.matter-row {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 0.75rem 1rem;
    margin-bottom: 0.35rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    transition: var(--transition);
}
.matter-row:hover { border-color: var(--border-blue); }
.matter-row .mr-ref  { font-size: 0.68rem; color: var(--text-muted); }
.matter-row .mr-name { color: var(--text); font-weight: 600; font-size: 0.88rem; }
.matter-row .mr-meta { color: var(--text-dim); font-size: 0.75rem; }

/* ══════════════════════════════════════���════════════
   SETTINGS ROW
═════════════��═════════════════════════���═══════════ */
.settings-row {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1rem 1.25rem;
    margin-bottom: 0.5rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.settings-row h5 { color: var(--text); font-size: 0.88rem; font-weight: 600; margin: 0 0 0.15rem; }
.settings-row p  { color: var(--text-dim); font-size: 0.78rem; margin: 0; }

/* ═══════════════════════════════════════════════════
   NOTICE BOXES
═══════════════���══════════════════════════��════════ */
.notice-box {
    background: rgba(245,158,11,0.06);
    border: 1px solid rgba(245,158,11,0.2);
    border-left: 3px solid var(--amber);
    border-radius: var(--radius-sm);
    padding: 0.75rem 1rem;
    margin-bottom: 1rem;
    font-size: 0.82rem;
    color: #fcd34d;
}
.privilege-box {
    background: rgba(239,68,68,0.06);
    border: 1px solid rgba(239,68,68,0.2);
    border-left: 3px solid var(--red);
    border-radius: var(--radius-sm);
    padding: 0.75rem 1rem;
    margin-bottom: 1rem;
    font-size: 0.82rem;
    color: #fca5a5;
}
.disclaimer-box {
    background: rgba(79,124,247,0.06);
    border: 1px solid var(--border-blue);
    border-left: 3px solid var(--blue);
    border-radius: var(--radius-sm);
    padding: 0.75rem 1rem;
    margin-bottom: 1.5rem;
    font-size: 0.82rem;
    color: #93c5fd;
}

/* ═══════════════════════════════════════════════════
   DOCUMENT PREVIEW
═══════════════════════════════════════════════════ */
.doc-preview {
    background: var(--bg-elevated);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 2rem 2.5rem;
    max-height: 520px;
    overflow-y: auto;
    line-height: 1.75;
    color: var(--text-dim);
    font-size: 0.91rem;
}
.doc-preview h1, .doc-preview h2, .doc-preview h3 { color: var(--text); }
.doc-preview .stamp {
    background: rgba(212,168,83,0.08);
    border-left: 3px solid var(--gold);
    padding: 0.4rem 0.8rem;
    border-radius: 0 6px 6px 0;
    margin: 0.5rem 0;
    font-style: italic;
    color: var(--gold-light);
}
.doc-preview .sig-block {
    background: rgba(79,124,247,0.06);
    border: 1px dashed var(--border-blue);
    border-radius: 8px;
    padding: 0.6rem 1rem;
    margin: 0.5rem 0;
    color: #93c5fd;
}

/* ═══════���══════════════════════���════════════════════
   REVISED DOC BOX
══════════════��═══════════════════════════���════════ */
.revised-doc {
    background: var(--bg-elevated);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 1.5rem 2rem;
    max-height: 450px;
    overflow-y: auto;
    white-space: pre-wrap;
    font-size: 0.88rem;
    line-height: 1.75;
    color: var(--text-dim);
}

/* ══════════════════════════════════════════��════════
   EMPTY STATE
══════════��══════════════════════════════���═════════ */
.empty-list {
    padding: 2.5rem;
    text-align: center;
    color: var(--text-muted);
    font-size: 0.85rem;
    border: 1px dashed var(--border);
    border-radius: var(--radius);
    line-height: 1.6;
}

/* ══════════════════════���════════════════════════════
   PLACEHOLDER / COMING SOON
════════════════════════════════════��══════════════ */
.placeholder-state {
    background: var(--bg-card);
    border: 1px dashed var(--border);
    border-radius: var(--radius-lg);
    padding: 3rem 2rem;
    text-align: center;
}
.placeholder-state .ph-icon { font-size: 2.2rem; opacity: 0.3; margin-bottom: 0.75rem; }
.placeholder-state h3 { color: var(--text-dim); font-size: 1rem; font-weight: 600; margin: 0 0 0.4rem; }
.placeholder-state .ph-desc { color: var(--text-muted); font-size: 0.82rem; max-width: 420px; margin: 0 auto 0.75rem; }
.placeholder-state .ph-list { text-align: left; display: inline-block; max-width: 380px; margin: 0 0 0.75rem; }
.placeholder-state .ph-list li { color: var(--text-muted); font-size: 0.78rem; margin-bottom: 0.25rem; }
</style>
"""


def inject_css() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)


def page_header(icon: str, title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="hero"><h1>{icon} {title}</h1><p class="sub">{subtitle}</p>'
        '<span class="badge">⚖️ eLawFirm &nbsp;·&nbsp; Powered by Claude Opus 4.7</span></div>',
        unsafe_allow_html=True,
    )


def slim_header(icon: str, title: str, subtitle: str = "") -> None:
    sub_html = f'<span class="ph-sub">&nbsp;— {subtitle}</span>' if subtitle else ""
    st.markdown(
        f'<div class="page-header"><h2>{icon} {title}</h2>{sub_html}</div>',
        unsafe_allow_html=True,
    )


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
                    <p style="font-size:0.68rem;font-weight:700;color:var(--text-muted);text-transform:uppercase;
                       letter-spacing:0.08em;margin:0 0 0.4rem">You will be able to</p>
                    <ul style="margin:0;padding-left:1.2rem">{caps_html}</ul>
                </div>
                <div class="ph-list">
                    <p style="font-size:0.68rem;font-weight:700;color:var(--text-muted);text-transform:uppercase;
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
