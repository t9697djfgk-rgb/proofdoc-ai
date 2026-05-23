import streamlit as st
from utils.shared.sidebar import setup_page
from utils.shared.styles import slim_header, section
from utils.auth import require_auth, can_see_internals, is_firm_user
import utils.database as db

setup_page()
user = require_auth()

slim_header("💬", "Matter Discussions", "Secure lawyer–client communication per matter")

matters = db.list_matters(status="Active")
if not matters:
    matters = db.list_matters()

if not matters:
    st.info("No matters found. Create a matter first to start a discussion.")
    st.stop()

# ── Matter selector ───────────────────────────────────────────────
matter_opts = {f"{m['ref']}: {m['title'][:45]}": m["id"] for m in matters}

# Allow pre-selecting via session state (from matter detail links)
default_matter = st.session_state.pop("discussion_matter_id", None)
default_idx = 0
if default_matter:
    keys = list(matter_opts.keys())
    vals = list(matter_opts.values())
    if default_matter in vals:
        default_idx = vals.index(default_matter)

sel_label = st.selectbox("Select Matter", list(matter_opts.keys()),
                          index=default_idx, key="disc_matter_sel")
matter_id = matter_opts[sel_label]
matter    = db.get_matter(matter_id)

# Permission: client must be a member of this matter
if user["role"] == "client" and not db.is_matter_member(matter_id):
    st.error("⛔ You are not assigned to this matter.")
    st.stop()

db.mark_messages_read(matter_id)

# ── Tabs ──────────────────────────────────────────────────────────
if is_firm_user():
    tab_client, tab_internal = st.tabs(["💬 Client Discussion", "🔒 Internal Notes"])
else:
    tab_client = st.container()
    tab_internal = None

# ── Shared message renderer ────────────────────────────────────────
def render_messages(messages: list[dict], show_type_badge: bool = False):
    if not messages:
        st.markdown(
            '<div style="text-align:center;color:#94a3b8;padding:2rem">'
            '💬 No messages yet. Start the conversation below.</div>',
            unsafe_allow_html=True,
        )
        return
    for msg in messages:
        sender_info = msg.get("profiles") or {}
        sender_name = sender_info.get("full_name", "Unknown")
        sender_role = sender_info.get("role", msg.get("sender_role", ""))
        is_mine     = msg.get("sender_id") == user["id"]
        is_internal = msg.get("message_type") == "internal_note"
        ts          = str(msg.get("created_at", ""))[:16].replace("T", " ")

        role_icon   = {"lawyer": "⚖️", "admin": "🛡️", "staff": "👤", "client": "🏢", "intern": "🎓"}.get(sender_role, "💬")
        align       = "right" if is_mine else "left"
        bg          = "#dbeafe" if is_mine else ("#fef3c7" if is_internal else "#f1f5f9")
        border      = "2px solid #d97706" if is_internal else "none"

        st.markdown(
            f"""<div style='text-align:{align};margin:.5rem 0'>
            <div style='display:inline-block;background:{bg};border:{border};
                padding:.7rem 1.1rem;border-radius:14px;max-width:78%;text-align:left'>
            <div style='margin-bottom:.25rem'>
                <small style='color:#475569;font-weight:600'>{role_icon} {sender_name}</small>
                <small style='color:#94a3b8;margin-left:.5rem'>{ts}</small>
                {"<small style='color:#d97706;margin-left:.5rem'>🔒 Internal Note</small>" if is_internal and show_type_badge else ""}
            </div>
            <div>{msg.get('body','')}</div>
            </div></div>""",
            unsafe_allow_html=True,
        )
        atts = msg.get("message_attachments") or []
        if atts:
            for att in atts:
                st.markdown(f"{'&nbsp;' * (40 if is_mine else 4)}📎 `{att.get('file_name','')}`",
                            unsafe_allow_html=True)


# ── Message composer ──────────────────────────────────────────────
def message_composer(msg_type: str, form_key: str):
    with st.form(form_key, clear_on_submit=True):
        body = st.text_area(
            "Message" if msg_type == "client_visible" else "Internal Note",
            height=90,
            placeholder=(
                "Type your message to the client…"
                if msg_type == "client_visible"
                else "Internal note — visible to lawyers and staff only…"
            ),
            key=f"{form_key}_body",
        )
        att_file = st.file_uploader(
            "📎 Attach file (optional)",
            type=["pdf", "docx", "doc", "png", "jpg", "jpeg", "txt", "xlsx"],
            key=f"{form_key}_att",
        )
        label = "Send to Client ➤" if msg_type == "client_visible" else "Save Internal Note 🔒"
        submitted = st.form_submit_button(label, type="primary")

    if submitted:
        if not body.strip():
            st.warning("Message cannot be empty.")
            return
        msg = db.send_message(matter_id, body.strip(), msg_type)
        if msg and att_file:
            doc = db.add_document(
                name=att_file.name,
                matter_id=matter_id,
                file_type=att_file.type,
                file_size=att_file.size,
                visibility="shared_with_client" if msg_type == "client_visible" else "internal",
            )
            if doc:
                db.add_message_attachment(
                    msg["id"], att_file.name,
                    doc.get("file_path", ""),
                    att_file.type, att_file.size, doc.get("id"),
                )
                db.audit("ATTACHMENT_UPLOADED", "document", doc.get("id"),
                         {"matter_id": matter_id, "file_name": att_file.name})

        if msg_type == "client_visible":
            db.notify_matter_members(
                matter_id, "new_message",
                f"New message from {user['full_name']}",
                body=body[:100], exclude_id=user["id"],
                lawyers_only=(user["role"] != "client"),
            )
        st.rerun()


# ── Client Discussion tab ─────────────────────────────────────────
with tab_client:
    # Matter info bar
    c1, c2, c3 = st.columns([3, 1, 1])
    c1.markdown(f"**Matter:** {matter.get('ref','')} — {matter.get('title','')}")
    c2.caption(f"Status: {matter.get('status','')}")
    c3.caption(f"Jurisdiction: {matter.get('jurisdiction','')}")
    st.divider()

    messages = db.list_messages(matter_id)
    client_msgs = [m for m in messages if m.get("message_type") == "client_visible"]

    # Paginate
    PAGE_SIZE = 30
    total_pages = max(1, -(-len(client_msgs) // PAGE_SIZE))
    page_key = f"disc_page_{matter_id}"
    if page_key not in st.session_state:
        st.session_state[page_key] = total_pages
    page = st.session_state[page_key]

    if total_pages > 1:
        cp1, cp2, cp3 = st.columns([1, 2, 1])
        if page > 1 and cp1.button("⬆ Older", key=f"pg_older_{matter_id}"):
            st.session_state[page_key] = page - 1
            st.rerun()
        cp2.caption(f"Page {page} of {total_pages}")
        if page < total_pages and cp3.button("Newer ⬇", key=f"pg_newer_{matter_id}"):
            st.session_state[page_key] = page + 1
            st.rerun()

    start = (page - 1) * PAGE_SIZE
    render_messages(client_msgs[start: start + PAGE_SIZE])

    st.markdown("<br>", unsafe_allow_html=True)
    message_composer("client_visible", f"compose_client_{matter_id}")

# ── Internal Notes tab (firm users only) ─────────────────────────
if is_firm_user() and tab_internal is not None:
    with tab_internal:
        st.markdown(
            '<div style="background:#fef3c7;border:1px solid #d97706;border-radius:8px;'
            'padding:.6rem 1rem;margin-bottom:1rem">'
            '🔒 Internal notes are <strong>never visible to clients</strong>. '
            'Use this for strategy, advice, and private discussions.</div>',
            unsafe_allow_html=True,
        )
        messages = db.list_messages(matter_id)
        internal = [m for m in messages if m.get("message_type") == "internal_note"]
        render_messages(internal, show_type_badge=True)
        st.markdown("<br>", unsafe_allow_html=True)
        message_composer("internal_note", f"compose_internal_{matter_id}")

# ── Matter Members panel ──────────────────────────────────────────
if is_firm_user():
    st.markdown("<br>", unsafe_allow_html=True)
    with st.expander("👥 Matter Members"):
        members = db.get_matter_members(matter_id)
        if members:
            h = st.columns([3, 2, 2])
            h[0].markdown("**Name**"); h[1].markdown("**Role**"); h[2].markdown("**Email**")
            st.divider()
            for mem in members:
                p = mem.get("profiles") or {}
                r = st.columns([3, 2, 2])
                r[0].text(p.get("full_name", "—"))
                r[1].text(mem.get("role", "—").replace("_", " ").title())
                r[2].text(p.get("email", "—"))
        if user["role"] in ("admin", "lawyer", "staff", "intern"):
            st.markdown("<br>", unsafe_allow_html=True)
            lawyers  = db.list_lawyers()
            clients  = db.list_profiles(role="client")
            all_prof = lawyers + clients
            member_ids = {m["profile_id"] for m in members}
            options  = {
                f"{p['full_name']} ({p['role']})": p["id"]
                for p in all_prof if p["id"] not in member_ids
            }
            if options:
                c1, c2, c3 = st.columns([3, 2, 1])
                add_who  = c1.selectbox("Add member", list(options.keys()), key="mm_add_who")
                add_role = c2.selectbox("Role", ["lawyer", "staff", "client"], key="mm_add_role")
                if c3.button("Add", key="mm_add_btn", type="primary"):
                    db.add_matter_member(matter_id, options[add_who], add_role)
                    st.rerun()
