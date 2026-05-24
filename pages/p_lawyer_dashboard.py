import streamlit as st
from utils.shared.sidebar import setup_page
from utils.shared.styles import inject_css, slim_header
from utils.auth import require_lawyer
import utils.database as db
from datetime import date

setup_page()
user = require_lawyer()
inject_css()

first_name = user["full_name"].split()[0]
org_name   = user["organization_name"]
role_label = user["role"].title()

# ── Greeting ──────────────────────────────────────────────────────
today = date.today()
hour  = __import__("datetime").datetime.now().hour
greeting = "Good morning" if hour < 12 else ("Good afternoon" if hour < 17 else "Good evening")

st.markdown(
    f"""
    <div style="margin-bottom:1.5rem">
      <h2 style="font-family:'Playfair Display',serif;color:#1a2744;margin:0;font-size:1.75rem">
        {greeting}, {first_name} 👋
      </h2>
      <p style="color:#6b7280;margin:0.25rem 0 0;font-size:0.95rem">
        {org_name} &nbsp;·&nbsp; {role_label} &nbsp;·&nbsp; {today.strftime("%A, %d %B %Y")}
      </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── Load data ─────────────────────────────────────────────────────
stats  = db.dashboard_stats()
notifs = db.list_notifications(limit=8)

active_matters = stats.get("active_matters", 0)
total_clients  = stats.get("total_clients",  0)
pending_tasks  = stats.get("pending_tasks",  0)
overdue_tasks  = stats.get("overdue_tasks",  0)
recent_matters = stats.get("recent_matters", [])
overdue_list   = stats.get("overdue_task_list", [])

# ── KPI Cards ─────────────────────────────────────────────────────
CARDS = [
    ("⚖️",  "Active Matters",  active_matters, "#1a2744", "#e8f0fe", None),
    ("👥",  "Clients",         total_clients,  "#059669", "#ecfdf5", None),
    ("📋",  "Pending Tasks",   pending_tasks,  "#d97706", "#fffbeb", None),
    ("⚠️",  "Overdue Tasks",   overdue_tasks,  "#dc2626", "#fef2f2", f"Needs attention" if overdue_tasks else "All on track"),
]

cols = st.columns(4, gap="small")
for col, (icon, label, value, color, bg, note) in zip(cols, CARDS):
    note_html = f'<p style="margin:0;font-size:0.72rem;color:{color};opacity:0.85">{note}</p>' if note else ""
    col.markdown(
        f"""
        <div style="background:{bg};border-radius:14px;padding:1.1rem 1.25rem;
                    border-left:4px solid {color};box-shadow:0 2px 8px rgba(0,0,0,0.06)">
          <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.4rem">
            <span style="font-size:1.3rem">{icon}</span>
            <span style="font-size:0.78rem;font-weight:600;color:#6b7280;text-transform:uppercase;
                         letter-spacing:0.05em">{label}</span>
          </div>
          <p style="margin:0;font-size:2rem;font-weight:700;color:{color};line-height:1">{value}</p>
          {note_html}
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

# ── Main two-column layout ────────────────────────────────────────
left, right = st.columns([3, 2], gap="large")

# ── LEFT: Recent Matters ──────────────────────────────────────────
with left:
    st.markdown(
        '<p style="font-size:0.78rem;font-weight:700;color:#1a2744;text-transform:uppercase;'
        'letter-spacing:0.07em;margin-bottom:0.75rem">📁 Recent Matters</p>',
        unsafe_allow_html=True,
    )

    STATUS_CFG = {
        "Active":   ("#16a34a", "#dcfce7"),
        "On Hold":  ("#d97706", "#fef9c3"),
        "Closed":   ("#64748b", "#f1f5f9"),
        "Archived": ("#94a3b8", "#f8fafc"),
    }

    if recent_matters:
        for m in recent_matters:
            status = m.get("status", "Active")
            fg, bg = STATUS_CFG.get(status, ("#64748b", "#f1f5f9"))
            ref    = m.get("ref", "—")
            title  = (m.get("title") or "Untitled")[:52]
            client = (m.get("client_name") or "")
            updated = str(m.get("updated_at", m.get("created_at", "")))[:10]
            st.markdown(
                f"""
                <div style="background:#fff;border-radius:10px;padding:0.8rem 1rem;
                            margin-bottom:0.5rem;border:1px solid rgba(0,0,0,0.07);
                            box-shadow:0 1px 4px rgba(0,0,0,0.05);
                            display:flex;align-items:center;gap:0.75rem">
                  <div style="flex:1;min-width:0">
                    <div style="display:flex;align-items:center;gap:0.5rem;flex-wrap:wrap">
                      <span style="font-weight:600;color:#1a2744;font-size:0.88rem">{ref}</span>
                      <span style="font-size:0.82rem;color:#374151;white-space:nowrap;
                                   overflow:hidden;text-overflow:ellipsis">{title}</span>
                    </div>
                    {'<p style="margin:0.15rem 0 0;font-size:0.75rem;color:#6b7280">'+client+'</p>' if client else ''}
                  </div>
                  <div style="text-align:right;flex-shrink:0">
                    <span style="background:{bg};color:{fg};font-size:0.7rem;font-weight:600;
                                 padding:0.2rem 0.55rem;border-radius:20px">{status}</span>
                    <p style="margin:0.25rem 0 0;font-size:0.7rem;color:#9ca3af">{updated}</p>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            '<div style="background:#fff;border-radius:10px;padding:1.5rem;text-align:center;'
            'border:1px dashed #d1cfc8;color:#9ca3af;font-size:0.88rem">'
            '📁 No matters yet — create your first in the Matters section.</div>',
            unsafe_allow_html=True,
        )

    if st.button("View all matters →", key="dash_all_matters"):
        st.switch_page("pages/p_matters_list.py")

    st.markdown("<div style='height:1.25rem'></div>", unsafe_allow_html=True)

    # ── Overdue tasks ──────────────────────────────────────────────
    st.markdown(
        '<p style="font-size:0.78rem;font-weight:700;color:#1a2744;text-transform:uppercase;'
        'letter-spacing:0.07em;margin-bottom:0.75rem">⚠️ Overdue Tasks</p>',
        unsafe_allow_html=True,
    )

    if overdue_list:
        for t in overdue_list[:5]:
            due = str(t.get("due_date", ""))[:10]
            st.markdown(
                f"""
                <div style="background:#fff5f5;border-radius:8px;padding:0.65rem 0.9rem;
                            margin-bottom:0.4rem;border-left:3px solid #dc2626;
                            display:flex;align-items:center;gap:0.75rem">
                  <span style="font-size:1rem">🔴</span>
                  <div style="flex:1">
                    <p style="margin:0;font-size:0.85rem;font-weight:500;color:#1a1a2e">
                      {t.get('title','Untitled task')}</p>
                    <p style="margin:0;font-size:0.72rem;color:#dc2626">Due: {due}</p>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            '<div style="background:#f0fdf4;border-radius:10px;padding:0.9rem 1rem;'
            'border-left:3px solid #16a34a;color:#166534;font-size:0.85rem">'
            '✅ No overdue tasks — great work!</div>',
            unsafe_allow_html=True,
        )

# ── RIGHT: Notifications + Quick Actions ─────────────────────────
with right:
    # Notifications
    unread = sum(1 for n in notifs if not n.get("is_read"))
    badge  = f' <span style="background:#dc2626;color:#fff;font-size:0.65rem;padding:0.1rem 0.4rem;border-radius:20px;vertical-align:middle">{unread}</span>' if unread else ""

    st.markdown(
        f'<p style="font-size:0.78rem;font-weight:700;color:#1a2744;text-transform:uppercase;'
        f'letter-spacing:0.07em;margin-bottom:0.75rem">🔔 Notifications{badge}</p>',
        unsafe_allow_html=True,
    )

    if notifs:
        for n in notifs:
            is_read  = n.get("is_read", False)
            bg       = "#ffffff" if is_read else "#fdf6e3"
            border   = "rgba(0,0,0,0.07)" if is_read else "#c9a84c"
            dot      = "⚪" if is_read else "🟡"
            ts       = str(n.get("created_at", ""))[:16].replace("T", " ")
            st.markdown(
                f"""
                <div style="background:{bg};border-radius:9px;padding:0.65rem 0.85rem;
                            margin-bottom:0.4rem;border:1px solid {border}">
                  <div style="display:flex;align-items:flex-start;gap:0.5rem">
                    <span style="font-size:0.7rem;margin-top:0.15rem">{dot}</span>
                    <div style="flex:1;min-width:0">
                      <p style="margin:0;font-size:0.82rem;font-weight:{'600' if not is_read else '400'};
                                color:#1a1a2e">{n.get('title','')}</p>
                      {'<p style="margin:0.15rem 0 0;font-size:0.73rem;color:#6b7280">'+n.get('body','')+'</p>' if n.get('body') else ''}
                      <p style="margin:0.2rem 0 0;font-size:0.68rem;color:#9ca3af">{ts}</p>
                    </div>
                  </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        if unread:
            if st.button("Mark all as read", key="dash_mark_read", use_container_width=True):
                db.mark_notifications_read()
                st.rerun()
    else:
        st.markdown(
            '<div style="background:#fff;border-radius:10px;padding:1.2rem;text-align:center;'
            'border:1px dashed #d1cfc8;color:#9ca3af;font-size:0.85rem">'
            'No notifications.</div>',
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:1.25rem'></div>", unsafe_allow_html=True)

    # Quick Actions
    st.markdown(
        '<p style="font-size:0.78rem;font-weight:700;color:#1a2744;text-transform:uppercase;'
        'letter-spacing:0.07em;margin-bottom:0.75rem">⚡ Quick Actions</p>',
        unsafe_allow_html=True,
    )

    ACTIONS = [
        ("➕ New Matter",    "pages/p_matters_list.py",       "qa_matter"),
        ("💬 Discussions",  "pages/p_matter_discussion.py",  "qa_disc"),
        ("📝 Draft",        "pages/p_ai_draft.py",           "qa_draft"),
        ("🔍 AI Review",    "pages/p_ai_review.py",          "qa_review"),
        ("⏱️ Log Time",     "pages/p_billing.py",            "qa_time"),
        ("📋 Tasks",        "pages/p_operations.py",         "qa_tasks"),
    ]

    col_a, col_b = st.columns(2, gap="small")
    for i, (label, page, key) in enumerate(ACTIONS):
        col = col_a if i % 2 == 0 else col_b
        if col.button(label, key=key, use_container_width=True):
            st.switch_page(page)
