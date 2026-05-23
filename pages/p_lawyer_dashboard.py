import streamlit as st
from utils.shared.sidebar import setup_page
from utils.shared.styles import slim_header, section
from utils.auth import require_lawyer
import utils.database as db

setup_page()
user = require_lawyer()

slim_header("🏠", f"Welcome, {user['full_name'].split()[0]}", f"{user['organization_name']} · {user['role'].title()}")

stats = db.dashboard_stats()

# ── KPI row ───────────────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)
m1.metric("Active Matters",   stats.get("active_matters", 0))
m2.metric("Total Clients",    stats.get("total_clients", 0))
m3.metric("Pending Tasks",    stats.get("pending_tasks", 0))
m4.metric("Overdue Tasks",    stats.get("overdue_tasks", 0),
          delta=f"-{stats.get('overdue_tasks',0)} overdue" if stats.get("overdue_tasks") else None,
          delta_color="inverse")

st.markdown("<br>", unsafe_allow_html=True)

col_left, col_right = st.columns(2, gap="large")

# ── Recent Matters ────────────────────────────────────────────────
with col_left:
    section("📁 Recent Matters")
    recent = stats.get("recent_matters", [])
    if recent:
        STATUS_COLORS = {
            "Active":    "#16a34a",
            "On Hold":   "#d97706",
            "Closed":    "#64748b",
            "Archived":  "#94a3b8",
        }
        for m in recent:
            color = STATUS_COLORS.get(m.get("status", ""), "#64748b")
            with st.container():
                c1, c2 = st.columns([4, 1])
                c1.markdown(f"**{m.get('ref','')}** — {m.get('title','')[:40]}")
                c2.markdown(
                    f"<span style='color:{color};font-size:.8rem'>{m.get('status','')}</span>",
                    unsafe_allow_html=True,
                )
    else:
        st.caption("No matters yet. Create your first matter in the Matters section.")

    st.markdown("<br>", unsafe_allow_html=True)
    section("📋 Overdue Tasks")
    overdue = stats.get("overdue_task_list", [])
    if overdue:
        for t in overdue:
            with st.container():
                c1, c2 = st.columns([4, 1])
                c1.markdown(f"⚠️ {t.get('title','')}")
                c2.caption(str(t.get("due_date", ""))[:10])
    else:
        st.success("✅ No overdue tasks.")

# ── Notifications + Quick Actions ────────────────────────────────
with col_right:
    section("🔔 Notifications")
    notifs = db.list_notifications(limit=10)
    if notifs:
        for n in notifs:
            icon = "🔵" if not n.get("is_read") else "⚪"
            with st.container():
                st.markdown(f"{icon} **{n['title']}**")
                if n.get("body"):
                    st.caption(n["body"])
                st.caption(str(n.get("created_at", ""))[:16].replace("T", " "))
        if any(not n.get("is_read") for n in notifs):
            if st.button("Mark all read", key="dash_mark_read"):
                db.mark_notifications_read()
                st.rerun()
    else:
        st.caption("No notifications.")

    st.markdown("<br>", unsafe_allow_html=True)
    section("⚡ Quick Actions")
    qa1, qa2 = st.columns(2)
    if qa1.button("➕ New Matter",        use_container_width=True, key="qa_matter"):
        st.switch_page("pages/p_matters_list.py")
    if qa2.button("💬 Discussions",       use_container_width=True, key="qa_disc"):
        st.switch_page("pages/p_matter_discussion.py")
    if qa1.button("📝 New Draft",         use_container_width=True, key="qa_draft"):
        st.switch_page("pages/p_ai_draft.py")
    if qa2.button("🔍 AI Review",         use_container_width=True, key="qa_review"):
        st.switch_page("pages/p_ai_review.py")
    if qa1.button("⏱️ Log Time",          use_container_width=True, key="qa_time"):
        st.switch_page("pages/p_billing.py")
    if qa2.button("📋 Tasks",             use_container_width=True, key="qa_tasks"):
        st.switch_page("pages/p_operations.py")
