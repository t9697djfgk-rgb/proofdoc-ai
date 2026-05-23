import streamlit as st
from utils.shared.sidebar import setup_page
from utils.shared.styles import slim_header, group_header, placeholder_feature
from utils import database as db

setup_page()
slim_header("📅", "Tasks & Calendar", "Manage tasks, deadlines, workflow templates, and firm calendar")

tab_tasks, tab_calendar, tab_workflow = st.tabs([
    "✅ Tasks", "📅 Calendar", "🔁 Workflow Templates",
])

with tab_tasks:
    group_header("All Tasks")

    # Filters
    fc1, fc2, fc3, _ = st.columns([1, 1, 1, 1])
    f_status   = fc1.selectbox("Status",   ["All", "Pending", "In Progress", "Done"], key="t_status")
    f_priority = fc2.selectbox("Priority", ["All", "High", "Medium", "Low"],          key="t_priority")

    all_tasks = db.list_tasks(status="" if f_status == "All" else f_status)
    if f_priority != "All":
        all_tasks = [t for t in all_tasks if t["priority"] == f_priority]

    # Quick-add task (no matter)
    with st.expander("＋ Add a General Task"):
        with st.form("ops_new_task", clear_on_submit=True):
            ot1, ot2, ot3 = st.columns(3)
            ot_title    = ot1.text_input("Task *")
            ot_priority = ot2.selectbox("Priority", ["High", "Medium", "Low"])
            ot_due      = ot3.text_input("Due (YYYY-MM-DD)")
            ot_assign   = st.text_input("Assigned to")
            if st.form_submit_button("＋ Add Task"):
                if ot_title.strip():
                    db.create_task("", ot_title.strip(), priority=ot_priority,
                                   due_date=ot_due.strip(), assigned_to=ot_assign.strip())
                    st.rerun()

    if not all_tasks:
        st.markdown(
            '<div class="empty-list" style="margin-top:1rem">'
            '✅ No tasks yet.<br>'
            '<small>Add tasks here or inside any matter.</small>'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        h = st.columns([3, 1, 1.5, 1.5, 0.8])
        for col, lbl in zip(h, ["Title", "Priority", "Due Date", "Status", ""]):
            col.markdown(f"**{lbl}**")
        st.divider()
        for t in all_tasks:
            row = st.columns([3, 1, 1.5, 1.5, 0.8])
            row[0].text(t["title"])
            pri_badge = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(t["priority"], "⚪")
            row[1].text(f"{pri_badge} {t['priority']}")
            row[2].text(t["due_date"] or "—")
            new_s = row[3].selectbox("", ["Pending", "In Progress", "Done"],
                                     index=["Pending","In Progress","Done"].index(t["status"]),
                                     key=f"ops_ts_{t['id']}", label_visibility="collapsed")
            if new_s != t["status"]:
                db.update_task(t["id"], status=new_s)
                st.rerun()
            if row[4].button("🗑️", key=f"ops_del_{t['id']}"):
                db.delete_task(t["id"])
                st.rerun()
        st.caption(f"{len(all_tasks)} tasks")

with tab_calendar:
    placeholder_feature(
        "📅", "Firm Calendar",
        "A shared calendar for court dates, client meetings, deadlines, and workflow milestones.",
        ["Add court dates, hearings, and filing deadlines",
         "Sync with Google Calendar, Outlook, or Apple Calendar",
         "Share calendars with team members",
         "Receive reminders for upcoming deadlines"],
        ["Shared firm calendar", "Per-matter calendar view",
         "Deadline sync with Deadline Calculator", "Calendar export (iCal)"],
    )

with tab_workflow:
    placeholder_feature(
        "🔁", "Workflow Templates",
        "Build reusable workflow templates for common matter types to standardise process.",
        ["Create step-by-step templates for common matter types",
         "Assign responsible lawyer/team to each step",
         "Auto-create tasks when a new matter is opened",
         "Track progress against standard workflow"],
        ["Workflow template library", "Matter progress tracker",
         "Automated task creation on matter open", "Workflow completion report"],
    )
