import streamlit as st

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.hero {
    background: linear-gradient(135deg, #0d1b2a 0%, #1e3a5f 60%, #2d5f8e 100%);
    border-radius: 16px; padding: 2.5rem 2rem; margin-bottom: 2rem;
    text-align: center; color: white;
    box-shadow: 0 8px 32px rgba(30,58,95,0.3);
}
.hero h1 { margin: 0 0 0.4rem 0; font-size: 2rem; font-weight: 700; }
.hero .sub { margin: 0; opacity: 0.85; font-size: 0.95rem; }
.hero .badge {
    display: inline-block; margin-top: 0.8rem;
    background: rgba(201,168,76,0.2); border: 1px solid rgba(201,168,76,0.5);
    color: #f0d080; border-radius: 20px; padding: 0.25rem 0.9rem; font-size: 0.78rem;
}

.tool-card {
    background: white; border: 1px solid #e2e8f0; border-radius: 12px;
    padding: 1.2rem 1rem; text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    transition: box-shadow 0.2s; height: 100%;
}
.tool-card:hover { box-shadow: 0 6px 20px rgba(30,58,95,0.15); }
.tool-card .icon { font-size: 1.8rem; margin-bottom: 0.4rem; }
.tool-card h4 { margin: 0 0 0.3rem 0; color: #1e3a5f; font-size: 0.88rem; font-weight: 600; }
.tool-card p { margin: 0; color: #64748b; font-size: 0.75rem; }

.feat-card {
    background: white; border: 1px solid #e2e8f0; border-radius: 12px;
    padding: 1.2rem 1rem; text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.feat-card .icon { font-size: 2rem; margin-bottom: 0.5rem; }
.feat-card h4 { margin: 0 0 0.3rem 0; color: #1e3a5f; font-size: 0.95rem; font-weight: 600; }
.feat-card p { margin: 0; color: #64748b; font-size: 0.8rem; }

.metric-card {
    background: white; border: 1px solid #e2e8f0; border-radius: 10px;
    padding: 1rem; text-align: center; box-shadow: 0 2px 6px rgba(0,0,0,0.05);
}
.metric-card .val { font-size: 2rem; font-weight: 700; color: #1e3a5f; }
.metric-card .lbl { font-size: 0.75rem; color: #64748b; margin-top: 0.2rem; }

.doc-preview {
    background: white; border: 1px solid #e2e8f0; border-radius: 12px;
    padding: 2rem 2.5rem; max-height: 520px; overflow-y: auto;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.04);
    line-height: 1.7; color: #1a1a2e; font-size: 0.92rem;
}
.doc-preview h1, .doc-preview h2, .doc-preview h3 { color: #1e3a5f; }
.doc-preview .stamp {
    background: #fff8e7; border-left: 3px solid #c9a84c;
    padding: 0.4rem 0.8rem; border-radius: 0 6px 6px 0; margin: 0.5rem 0; font-style: italic;
}
.doc-preview .sig-block {
    background: #f0f4ff; border: 1px dashed #93c5fd;
    border-radius: 8px; padding: 0.6rem 1rem; margin: 0.5rem 0;
}

.revised-doc {
    background: #f8fbff; border: 1px solid #bfdbfe; border-radius: 12px;
    padding: 1.5rem 2rem; max-height: 450px; overflow-y: auto;
    white-space: pre-wrap; font-size: 0.9rem; line-height: 1.75; color: #1a1a2e;
}

.risk-critical { background:#fce7f3; color:#9d174d; border-radius:12px; padding:2px 10px; font-size:0.75rem; font-weight:700; }
.risk-high     { background:#fee2e2; color:#991b1b; border-radius:12px; padding:2px 10px; font-size:0.75rem; font-weight:600; }
.risk-medium   { background:#fef9c3; color:#854d0e; border-radius:12px; padding:2px 10px; font-size:0.75rem; font-weight:600; }
.risk-low      { background:#dcfce7; color:#166534; border-radius:12px; padding:2px 10px; font-size:0.75rem; font-weight:600; }

.badge-doc     { display:inline-block; background:#dbeafe; color:#1e40af; border-radius:20px; padding:0.2rem 0.7rem; font-size:0.75rem; font-weight:600; }
.issue-badge   { background:#ede9fe; color:#5b21b6; border-radius:12px; padding:2px 10px; font-size:0.75rem; font-weight:500; }

.section-title {
    color: #1e3a5f; font-size: 1.1rem; font-weight: 600;
    border-bottom: 2px solid #c9a84c; padding-bottom: 0.4rem; margin-bottom: 1rem;
}

.notice-box {
    background: #fffbeb; border: 1px solid #fcd34d; border-radius: 10px;
    padding: 0.75rem 1rem; margin-bottom: 1rem; font-size: 0.82rem; color: #92400e;
}
.privilege-box {
    background: #fef2f2; border: 1px solid #fca5a5; border-radius: 10px;
    padding: 0.75rem 1rem; margin-bottom: 1rem; font-size: 0.82rem; color: #7f1d1d;
}
.disclaimer-box {
    background: #f0f9ff; border: 1px solid #bae6fd; border-radius: 10px;
    padding: 0.75rem 1rem; margin-bottom: 1.5rem; font-size: 0.82rem; color: #0c4a6e;
}

[data-testid="stFileUploader"] {
    border: 2px dashed #93c5fd !important; border-radius: 12px !important;
    padding: 0.5rem !important; background: #f8fbff !important;
}
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #1e3a5f, #2d5f8e) !important;
    border: none !important; border-radius: 8px !important;
    font-weight: 600 !important; box-shadow: 0 4px 12px rgba(30,58,95,0.3) !important;
}
.stDownloadButton > button {
    background: linear-gradient(135deg, #c9a84c, #e8c84a) !important;
    color: #1a1a2e !important; border: none !important; border-radius: 8px !important;
    font-weight: 600 !important; box-shadow: 0 4px 12px rgba(201,168,76,0.35) !important;
}
[data-testid="stSidebar"] { background: #0d1b2a !important; }
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
[data-testid="stSidebar"] .stTextInput input { background: #1e3a5f !important; border-color: #2d5f8e !important; }
[data-testid="stSidebar"] hr { border-color: #2d5f8e !important; }
</style>
"""


def inject_css() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)


def page_header(icon: str, title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="hero"><h1>{icon} {title}</h1><p class="sub">{subtitle}</p>'
        '<span class="badge">⚖️ ProofDoc AI Legal Platform &nbsp;·&nbsp; Powered by Claude Opus 4.7</span></div>',
        unsafe_allow_html=True,
    )


def disclaimer() -> None:
    st.markdown(
        '<div class="disclaimer-box">ℹ️ <strong>Disclaimer:</strong> This tool assists with legal drafting '
        "and review. It does not replace the professional judgment of a qualified lawyer. Do not rely "
        "solely on AI output for final legal decisions.</div>",
        unsafe_allow_html=True,
    )


def confidentiality_notice() -> None:
    st.markdown(
        '<div class="notice-box">🔐 <strong>Confidentiality Notice:</strong> Do not upload highly sensitive '
        "or legally privileged material unless your organization has approved this tool for that use. "
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


def section(title: str) -> None:
    st.markdown(f'<p class="section-title">{title}</p>', unsafe_allow_html=True)
