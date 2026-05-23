import streamlit as st
from utils.shared.sidebar import setup_page
from utils.shared.styles import stat_strip, group_header

api_key = setup_page()

# ── Header ────────────────────────────────────────────────────────
st.markdown(
    """
    <div class="hero">
        <h1>⚖️ ProofDoc AI</h1>
        <p class="sub">Your legal workspace — matters, documents, AI tools, and trial preparation in one place</p>
        <span class="badge">🔐 Confidentiality-first &nbsp;·&nbsp; Powered by Claude Opus 4.7</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Stats row ─────────────────────────────────────────────────────
audit = st.session_state.get("last_audit", [])
ai_count = sum(
    1 for k in st.session_state
    if k.endswith("_result") and st.session_state[k]
)
s1, s2, s3, s4 = st.columns(4)
s1.markdown(stat_strip("—", "Active Matters", "Coming soon"), unsafe_allow_html=True)
s2.markdown(stat_strip(str(len(audit)), "Docs Processed", "This session"), unsafe_allow_html=True)
s3.markdown(stat_strip(str(ai_count), "AI Reviews Run", "This session"), unsafe_allow_html=True)
s4.markdown(stat_strip("—", "Tasks Due Today", "Coming soon"), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Quick Actions ─────────────────────────────────────────────────
group_header("Quick Actions")

actions = [
    ("pages/p_ai_review.py",   "🔍", "Review Document",   "AI grammar, risk & citation review"),
    ("pages/p_ai_draft.py",    "📝", "Draft Document",     "Generate legal drafts and memos"),
    ("pages/p_doc_convert.py", "🔄", "Convert File",       "PDF ↔ Word, merge, process"),
    ("pages/p_matters_list.py","📁", "Open Matter",        "Clients, matters & timelines"),
    ("pages/p_trial.py",       "🏛️", "Prepare Trial",      "Court docs, evidence & bundles"),
    ("pages/p_compliance.py",  "🛡️", "Compliance Tools",  "Policies, redaction & audit"),
]

cols = st.columns(6)
for col, (page, icon, title, desc) in zip(cols, actions):
    with col:
        st.markdown(
            f'<div class="quick-action-card">'
            f'<div class="qa-icon">{icon}</div>'
            f'<h5>{title}</h5>'
            f'<p>{desc}</p>'
            f'</div>',
            unsafe_allow_html=True,
        )
        st.page_link(page, label="Open →", use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── Recent Activity (3 columns) ───────────────────────────────────
group_header("Recent Activity")

col_m, col_d, col_ai = st.columns(3)

with col_m:
    st.markdown("**📁 Recent Matters**")
    st.markdown(
        '<div class="empty-list">No active matters yet.<br>'
        '<small>Open a matter to get started.</small></div>',
        unsafe_allow_html=True,
    )
    st.page_link("pages/p_matters_list.py", label="+ New Matter")

with col_d:
    st.markdown("**📄 Recent Documents**")
    if audit:
        for entry in audit[-5:]:
            st.markdown(
                f'<div class="activity-item">'
                f'<div class="ai-title">📄 {entry.get("file","Unknown")[:32]}</div>'
                f'<div class="ai-meta">{entry.get("action","")} · {entry.get("timestamp","")[:16]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            '<div class="empty-list">No documents processed yet.<br>'
            '<small>Convert or upload a document.</small></div>',
            unsafe_allow_html=True,
        )
    st.page_link("pages/p_doc_library.py", label="Go to Document Library")

with col_ai:
    st.markdown("**🤖 Recent AI Reviews**")
    review_keys = {
        "ler_result": ("✍️", "Legal English Review"),
        "crc_result": ("⚠️", "Contract Risk Check"),
        "cc_result":  ("📚", "Citation Check"),
        "de_result":  ("⏰", "Deadline Extraction"),
        "da_result":  ("📝", "Legal Draft"),
        "lm_result":  ("📄", "Legal Memo"),
    }
    shown = 0
    for key, (icon, label) in review_keys.items():
        if st.session_state.get(key):
            st.markdown(
                f'<div class="activity-item">'
                f'<div class="ai-title">{icon} {label}</div>'
                f'<div class="ai-meta">Completed this session</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
            shown += 1
    if shown == 0:
        st.markdown(
            '<div class="empty-list">No AI reviews yet.<br>'
            '<small>Open an AI tool to get started.</small></div>',
            unsafe_allow_html=True,
        )
    st.page_link("pages/p_ai_review.py", label="Open AI Tools")

st.markdown("<br>", unsafe_allow_html=True)

# ── Deadlines + Tasks (2 columns) ────────────────────────────────
group_header("Deadlines & Tasks")
col_dl, col_tk = st.columns(2)

with col_dl:
    st.markdown("**📅 Upcoming Deadlines**")
    de_result = st.session_state.get("de_result")
    if de_result:
        deadlines = de_result.get("deadlines", [])[:5]
        if deadlines:
            for dl in deadlines:
                st.markdown(
                    f'<div class="activity-item">'
                    f'<div class="ai-title">⏰ {dl.get("date_or_period","?")}</div>'
                    f'<div class="ai-meta">{dl.get("action_required","")[:60]}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
        else:
            st.markdown('<div class="empty-list">No deadlines extracted yet.</div>', unsafe_allow_html=True)
    else:
        st.markdown(
            '<div class="empty-list">No deadlines found.<br>'
            '<small>Run Deadline Extractor on a contract or court order.</small></div>',
            unsafe_allow_html=True,
        )
    st.page_link("pages/p_ai_review.py", label="Extract Deadlines →")

with col_tk:
    st.markdown("**✅ Tasks Due Today**")
    st.markdown(
        '<div class="empty-list">Task management coming soon.<br>'
        '<small>Assign tasks to matters and track progress.</small></div>',
        unsafe_allow_html=True,
    )
    st.page_link("pages/p_operations.py", label="Go to Tasks →")

st.markdown("<br>", unsafe_allow_html=True)

# ── Audit Activity ────────────────────────────────────────────────
if audit:
    group_header("Recent Audit Activity")
    for entry in reversed(audit[-5:]):
        st.markdown(
            f'<div class="activity-item">'
            f'<div class="ai-title">🔒 {entry.get("action","")} — {entry.get("file","")[:40]}</div>'
            f'<div class="ai-meta">Session {entry.get("session","")[:8]} · {entry.get("timestamp","")[:19]}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )
    st.page_link("pages/p_audit.py", label="View full Audit Trail →")
