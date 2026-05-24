import streamlit as st

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── Hero / Page Header ── */
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

/* ── Page header bar (non-hero, slim) ── */
.page-header {
    border-bottom: 1px solid #e2e8f0;
    padding-bottom: 1rem;
    margin-bottom: 1.5rem;
}
.page-header h2 { color: #1e3a5f; font-size: 1.3rem; font-weight: 700; margin: 0 0 0.2rem 0; }
.page-header .ph-sub { color: #64748b; font-size: 0.85rem; margin: 0; }

/* ── Dashboard Quick Action Cards ── */
.quick-action-card {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.25rem 1rem;
    text-align: center;
    transition: all 0.18s;
    height: 100%;
}
.quick-action-card:hover {
    border-color: #1e3a5f;
    box-shadow: 0 4px 20px rgba(30,58,95,0.12);
    transform: translateY(-1px);
}
.quick-action-card .qa-icon { font-size: 1.7rem; margin-bottom: 0.4rem; }
.quick-action-card h5 { color: #1e3a5f; font-size: 0.85rem; font-weight: 600; margin: 0 0 0.15rem 0; }
.quick-action-card p  { color: #94a3b8; font-size: 0.72rem; margin: 0; }

/* ── Stat Strip (Dashboard) ── */
.stat-strip {
    background: white; border: 1px solid #e2e8f0; border-radius: 10px;
    padding: 1rem 1.25rem; text-align: center;
}
.stat-strip .sv { font-size: 1.8rem; font-weight: 700; color: #1e3a5f; line-height: 1; }
.stat-strip .sl { font-size: 0.72rem; color: #94a3b8; margin-top: 0.2rem;
    text-transform: uppercase; letter-spacing: 0.05em; }
.stat-strip .sd { font-size: 0.75rem; color: #16a34a; margin-top: 0.1rem; }

/* ── Metric Card (AI tool result metrics) ── */
.metric-card {
    background: white; border: 1px solid #e2e8f0; border-radius: 10px;
    padding: 1rem; text-align: center; box-shadow: 0 2px 6px rgba(0,0,0,0.05);
}
.metric-card .val { font-size: 2rem; font-weight: 700; color: #1e3a5f; }
.metric-card .lbl { font-size: 0.75rem; color: #64748b; margin-top: 0.2rem; }

/* ── Feature / Tool Cards (catalogue view) ── */
.feature-card {
    background: white; border: 1px solid #e2e8f0; border-radius: 12px;
    padding: 1.25rem; height: 100%; transition: all 0.18s; position: relative;
}
.feature-card:hover { border-color: #93c5fd; box-shadow: 0 4px 16px rgba(30,58,95,0.08); }
.feature-card .fc-icon  { font-size: 1.5rem; margin-bottom: 0.45rem; }
.feature-card .fc-name  { color: #1e3a5f; font-size: 0.88rem; font-weight: 600; margin: 0 0 0.2rem 0; }
.feature-card .fc-desc  { color: #64748b; font-size: 0.78rem; margin: 0 0 0.35rem 0; line-height: 1.4; }
.feature-card .fc-best  { color: #94a3b8; font-size: 0.7rem; font-style: italic; }
.feature-card .fc-badge { position: absolute; top: 1rem; right: 1rem; }

/* ── Shared tool/feat card (old style, kept for compat) ── */
.tool-card {
    background: white; border: 1px solid #e2e8f0; border-radius: 12px;
    padding: 1.2rem 1rem; text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06); transition: box-shadow 0.2s; height: 100%;
}
.tool-card:hover { box-shadow: 0 6px 20px rgba(30,58,95,0.15); }
.tool-card .icon { font-size: 1.8rem; margin-bottom: 0.4rem; }
.tool-card h4 { margin: 0 0 0.3rem 0; color: #1e3a5f; font-size: 0.88rem; font-weight: 600; }
.tool-card p  { margin: 0; color: #64748b; font-size: 0.75rem; }
.feat-card {
    background: white; border: 1px solid #e2e8f0; border-radius: 12px;
    padding: 1.2rem 1rem; text-align: center; box-shadow: 0 2px 8px rgba(0,0,0,0.06);
}
.feat-card .icon { font-size: 2rem; margin-bottom: 0.5rem; }
.feat-card h4 { margin: 0 0 0.3rem 0; color: #1e3a5f; font-size: 0.95rem; font-weight: 600; }
.feat-card p { margin: 0; color: #64748b; font-size: 0.8rem; }

/* ── Status Badges ── */
.badge-available { background:#dcfce7; color:#166534; border-radius:20px; padding:2px 10px; font-size:0.72rem; font-weight:600; }
.badge-soon      { background:#f1f5f9; color:#475569; border-radius:20px; padding:2px 10px; font-size:0.72rem; font-weight:600; }
.badge-beta      { background:#eff6ff; color:#1d4ed8; border-radius:20px; padding:2px 10px; font-size:0.72rem; font-weight:600; }

/* ── Risk Badges ── */
.risk-critical { background:#fce7f3; color:#9d174d; border-radius:12px; padding:2px 10px; font-size:0.75rem; font-weight:700; }
.risk-high     { background:#fee2e2; color:#991b1b; border-radius:12px; padding:2px 10px; font-size:0.75rem; font-weight:600; }
.risk-medium   { background:#fef9c3; color:#854d0e; border-radius:12px; padding:2px 10px; font-size:0.75rem; font-weight:600; }
.risk-low      { background:#dcfce7; color:#166534; border-radius:12px; padding:2px 10px; font-size:0.75rem; font-weight:600; }

/* ── General Badges ── */
.badge-doc     { display:inline-block; background:#dbeafe; color:#1e40af; border-radius:20px; padding:0.2rem 0.7rem; font-size:0.75rem; font-weight:600; }
.badge-conf-high { background:#dcfce7; color:#166534; border-radius:20px; padding:0.2rem 0.7rem; font-size:0.75rem; font-weight:600; }
.badge-conf-low  { background:#fef9c3; color:#854d0e; border-radius:20px; padding:0.2rem 0.7rem; font-size:0.75rem; font-weight:600; }
.issue-badge   { background:#ede9fe; color:#5b21b6; border-radius:12px; padding:2px 10px; font-size:0.75rem; font-weight:500; }

/* ── Placeholder / Coming-Soon State ── */
.placeholder-state {
    background: #f8fafc; border: 2px dashed #cbd5e1;
    border-radius: 16px; padding: 3rem 2rem; text-align: center;
}
.placeholder-state .ph-icon { font-size: 2.5rem; opacity: 0.4; margin-bottom: 0.75rem; }
.placeholder-state h3 { color: #334155; font-size: 1rem; font-weight: 600; margin: 0 0 0.4rem 0; }
.placeholder-state .ph-desc { color: #64748b; font-size: 0.82rem; max-width: 420px; margin: 0 auto 0.75rem auto; }
.placeholder-state .ph-list { text-align: left; display: inline-block; max-width: 380px; margin: 0 0 0.75rem 0; }
.placeholder-state .ph-list li { color: #64748b; font-size: 0.78rem; margin-bottom: 0.2rem; }

/* ── Activity / Recent List Items ── */
.activity-item {
    background: white; border: 1px solid #f1f5f9; border-radius: 8px;
    padding: 0.65rem 1rem; margin-bottom: 0.35rem;
}
.activity-item .ai-title { font-size: 0.82rem; font-weight: 500; color: #1e293b; }
.activity-item .ai-meta  { font-size: 0.72rem; color: #94a3b8; margin-top: 0.1rem; }

/* ── Integration Cards ── */
.int-card {
    background: white; border: 1px solid #e2e8f0; border-radius: 12px;
    padding: 1.25rem; text-align: center; transition: all 0.18s;
}
.int-card:hover { border-color: #93c5fd; box-shadow: 0 4px 16px rgba(30,58,95,0.08); }
.int-card .int-icon { font-size: 2rem; margin-bottom: 0.5rem; }
.int-card h5 { color: #1e3a5f; font-size: 0.85rem; font-weight: 600; margin: 0 0 0.2rem 0; }
.int-card p  { color: #64748b; font-size: 0.75rem; margin: 0; }

/* ── Empty List State ── */
.empty-list {
    padding: 2rem; text-align: center; color: #94a3b8; font-size: 0.85rem;
    border: 1px dashed #e2e8f0; border-radius: 10px;
}

/* ── Group Header (within-page section divider) ── */
.group-header {
    background: #f8fafc; border-left: 3px solid #c9a84c;
    border-radius: 0 8px 8px 0; padding: 0.45rem 1rem;
    margin: 1.5rem 0 1rem 0; color: #1e3a5f; font-size: 0.8rem;
    font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase;
}

/* ── Section Title ── */
.section-title {
    color: #1e3a5f; font-size: 1.05rem; font-weight: 600;
    border-bottom: 2px solid #c9a84c; padding-bottom: 0.4rem; margin-bottom: 1rem;
}

/* ── Notice / Alert Boxes ── */
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

/* ── Document Preview ── */
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

/* ── Revised Doc Box ── */
.revised-doc {
    background: #f8fbff; border: 1px solid #bfdbfe; border-radius: 12px;
    padding: 1.5rem 2rem; max-height: 450px; overflow-y: auto;
    white-space: pre-wrap; font-size: 0.9rem; line-height: 1.75; color: #1a1a2e;
}

/* ── Matter / Document List Item ── */
.matter-row {
    background: white; border: 1px solid #f1f5f9; border-radius: 8px;
    padding: 0.75rem 1rem; margin-bottom: 0.35rem;
    display: flex; justify-content: space-between; align-items: center;
}
.matter-row .mr-ref  { font-size: 0.7rem; color: #94a3b8; }
.matter-row .mr-name { color: #1e3a5f; font-weight: 600; font-size: 0.88rem; }
.matter-row .mr-meta { color: #64748b; font-size: 0.75rem; }

/* ── Settings Row ── */
.settings-row {
    background: white; border: 1px solid #e2e8f0; border-radius: 10px;
    padding: 1rem 1.25rem; margin-bottom: 0.5rem;
    display: flex; justify-content: space-between; align-items: center;
}
.settings-row h5 { color: #1e3a5f; font-size: 0.88rem; font-weight: 600; margin: 0 0 0.15rem 0; }
.settings-row p  { color: #64748b; font-size: 0.78rem; margin: 0; }

/* ── File Uploader ── */
[data-testid="stFileUploader"] {
    border: 2px dashed #93c5fd !important; border-radius: 12px !important;
    padding: 0.5rem !important; background: #f8fbff !important;
}

/* ── Buttons ── */
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

/* ── Sidebar ── */
[data-testid="stSidebar"] { background: #0d1b2a !important; }
[data-testid="stSidebar"] * { color: #e2e8f0 !important; }
[data-testid="stSidebar"] .stTextInput input { background: #1e3a5f !important; border-color: #2d5f8e !important; }
[data-testid="stSidebar"] hr { border-color: #2d5f8e !important; }
[data-testid="stSidebarNavItems"] { padding-top: 0.5rem; }
</style>
"""


def inject_css() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)


def page_header(icon: str, title: str, subtitle: str) -> None:
    st.markdown(
        f'<div class="hero"><h1>{icon} {title}</h1><p class="sub">{subtitle}</p>'
        '<span class="badge">⚖️ eLawFirm Legal Workspace &nbsp;·&nbsp; Powered by Claude Opus 4.7</span></div>',
        unsafe_allow_html=True,
    )


def slim_header(icon: str, title: str, subtitle: str = "") -> None:
    """Compact non-hero header for hub pages."""
    sub_html = f'<p class="ph-sub">{subtitle}</p>' if subtitle else ""
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
    """Returns HTML for Available / Coming Soon / Beta status badge."""
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
    """Renders a Coming Soon placeholder for unimplemented features."""
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
                    <p style="font-size:0.72rem;font-weight:600;color:#94a3b8;text-transform:uppercase;
                       letter-spacing:0.05em;margin:0 0 0.3rem 0">You will be able to</p>
                    <ul style="margin:0;padding-left:1.2rem">{caps_html}</ul>
                </div>
                <div class="ph-list">
                    <p style="font-size:0.72rem;font-weight:600;color:#94a3b8;text-transform:uppercase;
                       letter-spacing:0.05em;margin:0 0 0.3rem 0">Expected output</p>
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
    """Returns HTML for a tool catalogue card."""
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
    """Returns HTML for a dashboard stat card."""
    delta_html = f'<div class="sd">{delta}</div>' if delta else ""
    return (
        f'<div class="stat-strip">'
        f'<div class="sv">{value}</div>'
        f'<div class="sl">{label}</div>'
        f'{delta_html}</div>'
    )
