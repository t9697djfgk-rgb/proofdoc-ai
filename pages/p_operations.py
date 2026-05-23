import streamlit as st
import datetime
from utils.shared.sidebar import setup_page
from utils.shared.styles import slim_header, section, placeholder_feature
from utils.auth import require_lawyer
import utils.database as db

setup_page()
user = require_lawyer()

slim_header("📅", "Tasks & Calendar", "Manage tasks, deadlines, and team workload")

tab_tasks, tab_calendar, tab_workflow = st.tabs([
    "✅ Tasks", "📅 Calendar", "🔁 Workflow Templates",
])

# ── Tasks ──────────────────────────────────────────────────────────
with tab_tasks:
    section("All Tasks")

    STATUS_OPTS   = ["pending", "in_progress", "completed", "cancelled"]
    STATUS_LABELS = {"pending": "Pending", "in_progress": "In Progress",
                     "completed": "Completed", "cancelled": "Cancelled"}
    PRIORITY_OPTS = ["high", "medium", "low"]

    fc1, fc2, fc3, _ = st.columns([1, 1, 1, 1])
    f_status   = fc1.selectbox("Status",   ["All"] + [STATUS_LABELS[s] for s in STATUS_OPTS], key="t_status")
    f_priority = fc2.selectbox("Priority", ["All", "High", "Medium", "Low"], key="t_priority")

    status_arg = None
    if f_status != "All":
        status_arg = {v: k for k, v in STATUS_LABELS.items()}[f_status]

    all_tasks = db.list_tasks(status=status_arg)
    if f_priority != "All":
        all_tasks = [t for t in all_tasks if (t.get("priority") or "").lower() == f_priority.lower()]

    # Quick-add task
    with st.expander("＋ Add a General Task"):
        lawyers = db.list_lawyers()
        lawyer_opts = {"(Unassigned)": None} | {p["full_name"]: p["id"] for p in lawyers}
        with st.form("ops_new_task", clear_on_submit=True):
            ot1, ot2, ot3 = st.columns(3)
            ot_title    = ot1.text_input("Task *", key="ot_t")
            ot_priority = ot2.selectbox("Priority", PRIORITY_OPTS, key="ot_p")
            ot_due      = ot3.text_input("Due (YYYY-MM-DD)", key="ot_d",
                                          placeholder=str(datetime.date.today()))
            ot_assign   = st.selectbox("Assign to", list(lawyer_opts.keys()), key="ot_a")
            if st.form_submit_button("＋ Add Task", type="primary"):
                if not ot_title.strip():
                    st.warning("Title is required.")
                else:
                    db.create_task(
                        title=ot_title.strip(),
                        priority=ot_priority,
                        due_date=ot_due.strip() or None,
                        assigned_to=lawyer_opts[ot_assign],
                        status="pending",
                    )
                    st.rerun()

    if not all_tasks:
        st.markdown(
            '<div style="text-align:center;color:#94a3b8;padding:2rem">'
            '✅ No tasks found.<br>'
            '<small>Add tasks here or inside any matter.</small>'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        h = st.columns([3, 1, 1.5, 1.5, 1.5, 0.8])
        for col, lbl in zip(h, ["Title", "Priority", "Due Date", "Assigned To", "Status", ""]):
            col.markdown(f"**{lbl}**")
        st.divider()

        for t in all_tasks:
            row = st.columns([3, 1, 1.5, 1.5, 1.5, 0.8])
            matter_ref = ""
            if t.get("matter_id"):
                matter_ref = f" · {t.get('matters', {}).get('ref', '')}" if t.get("matters") else ""
            row[0].text(t["title"] + matter_ref)

            pri = (t.get("priority") or "medium").lower()
            pri_badge = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(pri, "⚪")
            row[1].text(f"{pri_badge} {pri.title()}")

            due = str(t.get("due_date") or "")[:10]
            if due:
                due_dt = datetime.date.fromisoformat(due) if due else None
                overdue = due_dt and due_dt < datetime.date.today() and t.get("status") not in ("completed", "cancelled")
                row[2].markdown(f"{'🔴 ' if overdue else ''}{due}")
            else:
                row[2].text("—")

            assigned = (t.get("profiles") or {}).get("full_name", "—")
            row[3].text(assigned)

            cur_status = t.get("status", "pending")
            new_s = row[4].selectbox(
                "", STATUS_OPTS,
                index=STATUS_OPTS.index(cur_status) if cur_status in STATUS_OPTS else 0,
                format_func=lambda s: STATUS_LABELS.get(s, s),
                key=f"ops_ts_{t['id']}",
                label_visibility="collapsed",
            )
            if new_s != cur_status:
                db.update_task(t["id"], status=new_s)
                st.rerun()

            if row[5].button("🗑️", key=f"ops_del_{t['id']}", help="Delete task"):
                db.delete_task(t["id"])
                st.rerun()

        overdue_count = sum(
            1 for t in all_tasks
            if str(t.get("due_date") or "")[:10] < str(datetime.date.today())
            and t.get("status") not in ("completed", "cancelled")
            and t.get("due_date")
        )
        st.caption(f"{len(all_tasks)} tasks" + (f" · {overdue_count} overdue" if overdue_count else ""))

# ── Calendar ───────────────────────────────────────────────────────
with tab_calendar:
    section("Upcoming Deadlines")
    today = datetime.date.today()
    deadline_tasks = db.list_tasks()
    upcoming = [
        t for t in deadline_tasks
        if t.get("due_date")
        and today <= datetime.date.fromisoformat(str(t["due_date"])[:10]) <= today + datetime.timedelta(days=30)
        and t.get("status") not in ("completed", "cancelled")
    ]
    overdue = [
        t for t in deadline_tasks
        if t.get("due_date")
        and datetime.date.fromisoformat(str(t["due_date"])[:10]) < today
        and t.get("status") not in ("completed", "cancelled")
    ]

    if overdue:
        st.error(f"🔴 {len(overdue)} overdue task{'s' if len(overdue) > 1 else ''}")
        for t in overdue[:5]:
            due = str(t["due_date"])[:10]
            days_over = (today - datetime.date.fromisoformat(due)).days
            st.markdown(f"- **{t['title']}** — {due} *(overdue by {days_over}d)*")
        if len(overdue) > 5:
            st.caption(f"…and {len(overdue)-5} more")
        st.markdown("<br>", unsafe_allow_html=True)

    if upcoming:
        st.success(f"📅 {len(upcoming)} deadline{'s' if len(upcoming)>1 else ''} in the next 30 days")
        for t in upcoming:
            due = datetime.date.fromisoformat(str(t["due_date"])[:10])
            days_left = (due - today).days
            label = "Today" if days_left == 0 else (f"Tomorrow" if days_left == 1 else f"in {days_left}d")
            st.markdown(f"- **{t['title']}** — {str(t['due_date'])[:10]} *({label})*")
    elif not overdue:
        st.info("No upcoming deadlines in the next 30 days.")

    st.markdown("<br>", unsafe_allow_html=True)
    placeholder_feature(
        "📅", "Shared Firm Calendar",
        "A calendar for court dates, hearings, and team meetings.",
        ["Add court dates and filing deadlines",
         "Sync with Google Calendar or Outlook",
         "Share calendars with team members",
         "Deadline reminders and notifications"],
        ["Shared calendar view", "Per-matter calendar", "Calendar export (iCal)"],
    )

# ── Workflow Templates ──────────────────────────────────────────────
with tab_workflow:
    placeholder_feature(
        "🔁", "Workflow Templates",
        "Build reusable templates for common matter types.",
        ["Create step-by-step templates for common matter types",
         "Assign responsible lawyer/team to each step",
         "Auto-create tasks when a new matter is opened",
         "Track progress against standard workflow"],
        ["Template library", "Matter progress tracker",
         "Automated task creation", "Workflow completion report"],
    )
