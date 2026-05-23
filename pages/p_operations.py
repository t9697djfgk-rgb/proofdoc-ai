import streamlit as st
from utils.shared.sidebar import setup_page
from utils.shared.styles import slim_header, group_header, placeholder_feature

setup_page()
slim_header("📅", "Tasks & Calendar", "Manage tasks, deadlines, workflow templates, and firm calendar")

tab_tasks, tab_calendar, tab_workflow = st.tabs([
    "✅ Tasks", "📅 Calendar", "🔁 Workflow Templates",
])

with tab_tasks:
    group_header("Task Management")
    c_left, c_right = st.columns([3, 1])
    c_left.markdown("### My Tasks")
    if c_right.button("+ New Task", type="primary", use_container_width=True):
        st.info("Task creation requires a database — coming soon.")
    st.markdown(
        '<div class="empty-list" style="margin-top:1rem">'
        '✅ No tasks yet.<br>'
        '<small>Create tasks linked to matters and set due dates.</small>'
        '</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)
    placeholder_feature(
        "✅", "Task Management",
        "Create, assign, and track tasks linked to matters and documents.",
        ["Create tasks with due dates, priority, and assignee",
         "Link tasks to specific matters or documents",
         "Set recurring tasks and workflow reminders",
         "Track team task completion and workload"],
        ["Task list per matter", "Team workload view", "Overdue tasks alert",
         "Weekly task report"],
    )

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
