import streamlit as st
import anthropic
from utils.shared.sidebar import setup_page
from utils.shared.styles import slim_header
from utils.auth import require_lawyer
import utils.database as db

api_key = setup_page()
require_lawyer()

_hdr, _btn = st.columns([5, 1])
with _hdr:
    slim_header("💬", "Legal AI Assistant", "Ask anything — powered by Claude Opus 4.7")
with _btn:
    st.markdown("<div style='height:1.6rem'></div>", unsafe_allow_html=True)
    if st.button("＋ New Chat", type="primary", use_container_width=True, key="chat_new_top"):
        st.session_state.chat_messages = []
        st.rerun()

# ── Session state ──────────────────────────────────────────────────
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []

# ── System prompt ──────────────────────────────────────────────────
_SYSTEM = (
    "You are a senior legal assistant at a professional law firm, working alongside qualified "
    "lawyers, barristers, and legal staff. You have deep expertise across contract law, "
    "commercial law, corporate law, litigation, employment, property, family, criminal, and "
    "international law.\n\n"
    "Guidelines:\n"
    "- Use precise legal terminology and professional language.\n"
    "- Cite relevant statutes, regulations, and case law principles where applicable.\n"
    "- Structure complex answers with numbered points or clear headings.\n"
    "- Flag jurisdictional differences proactively.\n"
    "- Note when additional facts are needed for a definitive answer.\n"
    "- When reviewing documents, identify risks, obligations, missing provisions, and "
    "ambiguous clauses.\n"
    "- Be concise but thorough. For short factual questions, answer directly without "
    "unnecessary preamble.\n"
    "- Always note that AI responses are informational and do not replace advice from a "
    "qualified solicitor or barrister on specific matters."
)

# ── Sidebar context panel ──────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<p style="font-size:0.78rem;font-weight:700;color:#1a2744;text-transform:uppercase;'
        'letter-spacing:0.06em;margin-bottom:0.5rem">⚙️ Context</p>',
        unsafe_allow_html=True,
    )

    # Matter selector
    matters = []
    try:
        matters = db.list_matters()
    except Exception:
        pass
    matter_opts = {"— No matter context —": None}
    matter_opts.update({
        f"{m.get('ref', '')} {(m.get('title') or '')[:28]}": m["id"]
        for m in matters
    })
    sel_matter_key = st.selectbox("Matter context", list(matter_opts.keys()), key="chat_matter_sel")
    _matter_id = matter_opts[sel_matter_key]

    # Document paste area
    doc_context = st.text_area(
        "Paste document (optional)",
        height=140,
        placeholder="Paste contract text, clauses, or any document you want to discuss…",
        key="chat_doc_ctx",
    )

    st.divider()

    # Deep analysis toggle
    deep_mode = st.toggle("🧠 Deep Analysis mode",
                          help="Enables extended thinking — slower but more thorough for complex questions",
                          key="chat_deep")

    st.divider()

    # Export
    if st.session_state.chat_messages:
        export_text = "\n\n".join(
            f"{'YOU' if m['role'] == 'user' else 'ASSISTANT'}:\n{m['content']}"
            for m in st.session_state.chat_messages
        )
        st.download_button("📥 Export (.txt)", export_text, "legal_chat.txt",
                           "text/plain", use_container_width=True, key="chat_dl_txt")
        from utils.shared.export_utils import download_pdf
        download_pdf("📄 Export (.pdf)", export_text, "legal_chat.pdf",
                     title="Legal AI Chat", key="chat_dl_pdf")
        st.divider()

    if st.button("🗑️ Clear conversation", use_container_width=True, key="chat_clear"):
        st.session_state.chat_messages = []
        st.rerun()


# ── Build system prompt with injected context ──────────────────────
def _build_system() -> str:
    parts = [_SYSTEM]
    if _matter_id:
        try:
            m = db.get_matter(_matter_id)
            if m:
                tasks   = db.list_tasks(matter_id=_matter_id)
                open_t  = [t for t in tasks if t.get("status") not in ("completed", "cancelled")]
                members = db.get_matter_members(_matter_id)
                lawyers = [
                    (mem.get("profiles") or {}).get("full_name", "")
                    for mem in members
                    if mem.get("role") in ("lead_lawyer", "lawyer")
                ]
                ctx = (
                    "\n\n── ACTIVE MATTER CONTEXT ──\n"
                    f"Reference:   {m.get('ref', '—')}\n"
                    f"Title:       {m.get('title', '—')}\n"
                    f"Type:        {m.get('matter_type', '—')}\n"
                    f"Jurisdiction:{m.get('jurisdiction', '—')}\n"
                    f"Status:      {m.get('status', '—')}\n"
                    f"Lawyers:     {', '.join(l for l in lawyers if l) or '—'}\n"
                )
                if m.get("description"):
                    ctx += f"Description: {m['description']}\n"
                if m.get("opposing_party"):
                    ctx += f"Opposing:    {m['opposing_party']}\n"
                if open_t:
                    ctx += "Open tasks:  " + " | ".join(
                        t.get("title", "") for t in open_t[:6]
                    ) + "\n"
                ctx += "── END MATTER CONTEXT ──"
                parts.append(ctx)
        except Exception:
            pass

    if doc_context and doc_context.strip():
        parts.append(
            "\n\n── DOCUMENT FOR ANALYSIS ──\n"
            + doc_context.strip()
            + "\n── END DOCUMENT ──"
        )

    from utils.shared.sidebar import get_law_context_block
    law_block = get_law_context_block()
    if law_block:
        parts.append("\n\n── APPLICABLE RWANDA LAWS ──\n" + law_block + "\n── END LAWS ──")

    return "\n".join(parts)


# ── Disclaimer banner ──────────────────────────────────────────────
st.markdown(
    '<div style="background:#f0f4ff;border:1px solid #c7d2fe;border-radius:8px;'
    'padding:0.6rem 1rem;margin-bottom:1rem;font-size:0.82rem;color:#3730a3">'
    '⚖️ <b>AI Legal Assistant</b> — Powered by Claude Opus 4.7. Responses are informational '
    'and do not constitute qualified legal advice. Verify important matters with a qualified '
    'solicitor or barrister.</div>',
    unsafe_allow_html=True,
)

# ── Context badges ─────────────────────────────────────────────────
badges = []
if _matter_id:
    m_label = sel_matter_key.strip()
    badges.append(f'<span style="background:#e8f0fe;color:#1a2744;font-size:0.75rem;font-weight:600;'
                  f'padding:0.2rem 0.6rem;border-radius:20px;margin-right:0.4rem">📁 {m_label[:40]}</span>')
if doc_context and doc_context.strip():
    badges.append('<span style="background:#fdf6e3;color:#92400e;font-size:0.75rem;font-weight:600;'
                  'padding:0.2rem 0.6rem;border-radius:20px;margin-right:0.4rem">📄 Document attached</span>')
if st.session_state.get("sidebar_selected_laws"):
    n = len(st.session_state.sidebar_selected_laws)
    badges.append(f'<span style="background:#f0fdf4;color:#166534;font-size:0.75rem;font-weight:600;'
                  f'padding:0.2rem 0.6rem;border-radius:20px;margin-right:0.4rem">'
                  f'⚖️ {n} law{"s" if n > 1 else ""} loaded</span>')
if deep_mode:
    badges.append('<span style="background:#f5f3ff;color:#6d28d9;font-size:0.75rem;font-weight:600;'
                  'padding:0.2rem 0.6rem;border-radius:20px">🧠 Deep Analysis</span>')
if badges:
    st.markdown("".join(badges), unsafe_allow_html=True)
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

# ── Suggested prompts (empty state) ───────────────────────────────
SUGGESTIONS = [
    ("⚖️", "What are the key elements of a valid contract under English law?"),
    ("🔍", "Explain the duty of care in professional negligence claims"),
    ("📝", "What clauses should every commercial NDA include?"),
    ("🏛️", "How does without-prejudice privilege work?"),
    ("📋", "What are the grounds for unfair dismissal in the UK?"),
    ("💼", "Explain conditions, warranties, and innominate terms in contract law"),
    ("🌍", "What is the difference between common law and civil law systems?"),
    ("⚠️", "What constitutes repudiatory breach of contract?"),
    ("🏢", "Explain directors' duties under the Companies Act 2006"),
]

if not st.session_state.chat_messages:
    st.markdown(
        '<p style="font-size:0.78rem;font-weight:600;color:#6b7280;text-transform:uppercase;'
        'letter-spacing:0.06em;margin-bottom:0.75rem">💡 Try asking…</p>',
        unsafe_allow_html=True,
    )
    cols = st.columns(3)
    for i, (icon, text) in enumerate(SUGGESTIONS):
        if cols[i % 3].button(
            f"{icon} {text[:42]}…" if len(text) > 42 else f"{icon} {text}",
            key=f"sug_{i}", use_container_width=True
        ):
            st.session_state.chat_messages.append({"role": "user", "content": text})
            st.rerun()
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

# ── Render history ─────────────────────────────────────────────────
for msg in st.session_state.chat_messages:
    with st.chat_message(msg["role"], avatar="👤" if msg["role"] == "user" else "⚖️"):
        st.markdown(msg["content"])

# ── Chat input + streaming response ───────────────────────────────
if prompt := st.chat_input(
    "Ask a legal question, paste a clause to review, or request a draft…",
    key="chat_input",
):
    if not api_key:
        st.error("Please enter your Anthropic API key in the sidebar to use the assistant.")
        st.stop()

    st.session_state.chat_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    with st.chat_message("assistant", avatar="⚖️"):
        system_prompt = _build_system()
        client = anthropic.Anthropic(api_key=api_key)

        def _stream_gen(stream):
            for text in stream.text_stream:
                yield text

        kwargs: dict = {
            "model": "claude-opus-4-7",
            "max_tokens": 8192,
            "system": system_prompt,
            "messages": [
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.chat_messages
            ],
        }
        if deep_mode:
            kwargs["thinking"] = {"type": "adaptive"}

        try:
            with client.messages.stream(**kwargs) as stream:
                full_text = st.write_stream(_stream_gen(stream))
        except anthropic.BadRequestError as exc:
            full_text = f"Request error: {exc}"
            st.error(full_text)
        except Exception as exc:
            full_text = f"Unexpected error: {exc}"
            st.error(full_text)

    st.session_state.chat_messages.append({"role": "assistant", "content": full_text or ""})
