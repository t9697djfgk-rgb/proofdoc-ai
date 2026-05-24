import streamlit as st
import datetime
from utils.shared.sidebar import setup_page
from utils.shared.styles import slim_header, inject_css, section
from utils.auth import require_lawyer
import utils.database as db

setup_page()
user = require_lawyer()
inject_css()
slim_header("📅", "Tasks & Calendar", "Manage tasks, deadlines, and team workload")

STATUS_OPTS   = ["pending", "in_progress", "completed", "cancelled"]
STATUS_LABELS = {"pending": "Pending", "in_progress": "In Progress",
                 "completed": "Completed", "cancelled": "Cancelled"}
STATUS_CFG    = {
    "pending":     ("#d97706", "#fffbeb"),
    "in_progress": ("#2563eb", "#eff6ff"),
    "completed":   ("#16a34a", "#dcfce7"),
    "cancelled":   ("#94a3b8", "#f1f5f9"),
}
PRIORITY_OPTS = ["high", "medium", "low"]
PRIORITY_CFG  = {"high": ("🔴","#dc2626"), "medium": ("🟡","#d97706"), "low": ("🟢","#16a34a")}

# ── Built-in workflow templates ────────────────────────────────────
BUILTIN_TEMPLATES = {
    "Commercial Dispute": [
        "Conduct initial client interview",
        "Review all relevant documents and evidence",
        "Prepare case chronology",
        "Run conflict check",
        "Issue client engagement letter",
        "Assess limitation period",
        "Draft letter before action",
        "Prepare mediation brief",
        "File court proceedings",
        "Prepare trial bundle",
    ],
    "Corporate M&A": [
        "Review heads of terms / LOI",
        "Prepare due diligence request list",
        "Conduct legal due diligence",
        "Draft due diligence report",
        "Negotiate SPA / transaction documents",
        "Obtain regulatory approvals",
        "Satisfy conditions precedent",
        "Prepare completion checklist",
        "Completion and post-completion filings",
    ],
    "Employment Matter": [
        "Initial client consultation",
        "Obtain employment contract and policies",
        "Review ACAS / statutory framework",
        "Advise on merits and prospects",
        "Draft without prejudice correspondence",
        "Prepare ET1 / response",
        "Disclose documents",
        "Exchange witness statements",
        "Prepare for hearing",
    ],
    "Property Transaction": [
        "Receive and review title documents",
        "Raise enquiries with seller's solicitors",
        "Review searches",
        "Report to client on title",
        "Draft transfer deed / lease",
        "Obtain client approval of documents",
        "Exchange contracts",
        "Complete transaction",
        "Register title at land registry",
    ],
}

if "wf_templates" not in st.session_state:
    st.session_state.wf_templates = {}  # custom templates only

tab_tasks, tab_calendar, tab_workflow = st.tabs([
    "✅ Tasks", "📅 Deadlines", "🔁 Workflow Templates",
])

# ══════════════════════════════════════════════════════════════════
# TAB 1 – TASKS
# ══════════════════════════════════════════════════════════════════
with tab_tasks:
    fc1, fc2, fc3, _ = st.columns([1, 1, 1, 1])
    f_status   = fc1.selectbox("Status",   ["All"] + [STATUS_LABELS[s] for s in STATUS_OPTS], key="t_status")
    f_priority = fc2.selectbox("Priority", ["All", "High", "Medium", "Low"], key="t_priority")

    status_arg = None
    if f_status != "All":
        status_arg = {v: k for k, v in STATUS_LABELS.items()}[f_status]

    all_tasks = db.list_tasks(status=status_arg)
    if f_priority != "All":
        all_tasks = [t for t in all_tasks if (t.get("priority") or "").lower() == f_priority.lower()]

    with st.expander("＋ Add Task"):
        lawyers     = db.list_lawyers()
        lawyer_opts = {"(Unassigned)": None} | {p["full_name"]: p["id"] for p in lawyers}
        matters     = db.list_matters(status="Active")
        matter_opts = {"(No matter)": None} | {f"{m['ref']}: {m['title'][:35]}": m["id"] for m in matters}
        with st.form("ops_new_task", clear_on_submit=True):
            ot1, ot2, ot3 = st.columns(3)
            ot_title    = ot1.text_input("Task *", key="ot_t")
            ot_priority = ot2.selectbox("Priority", PRIORITY_OPTS, key="ot_p")
            ot_due      = ot3.text_input("Due (YYYY-MM-DD)", key="ot_d",
                                          placeholder=str(datetime.date.today()))
            ota, otb = st.columns(2)
            ot_assign = ota.selectbox("Assign to", list(lawyer_opts.keys()), key="ot_a")
            ot_matter = otb.selectbox("Matter", list(matter_opts.keys()), key="ot_m")
            if st.form_submit_button("＋ Add Task", type="primary"):
                if ot_title.strip():
                    db.create_task(
                        title=ot_title.strip(), priority=ot_priority,
                        due_date=ot_due.strip() or None,
                        assigned_to=lawyer_opts[ot_assign],
                        matter_id=matter_opts[ot_matter],
                        status="pending",
                    )
                    st.rerun()
                else:
                    st.warning("Title is required.")

    today = datetime.date.today()
    if not all_tasks:
        st.markdown(
            '<div style="text-align:center;color:#94a3b8;padding:2rem">'
            '✅ No tasks found.</div>',
            unsafe_allow_html=True,
        )
    else:
        overdue_count = 0
        for t in all_tasks:
            status   = t.get("status", "pending")
            pri      = (t.get("priority") or "medium").lower()
            due_str  = str(t.get("due_date") or "")[:10]
            pri_icon, pri_color = PRIORITY_CFG.get(pri, ("⚪", "#6b7280"))
            st_fg, st_bg = STATUS_CFG.get(status, ("#6b7280", "#f1f5f9"))

            is_overdue = False
            if due_str and status not in ("completed", "cancelled"):
                try:
                    if datetime.date.fromisoformat(due_str) < today:
                        is_overdue = True
                        overdue_count += 1
                except ValueError:
                    pass

            assigned = (t.get("profiles") or {}).get("full_name", "")
            matter_ref = ""
            if t.get("matters"):
                matter_ref = t["matters"].get("ref", "")

            card_col, ctrl_col = st.columns([7, 3])
            card_col.markdown(
                f"""<div style="background:#fff;border-radius:9px;padding:0.65rem 1rem;
                               border:1px solid rgba(0,0,0,0.07);
                               border-left:4px solid {'#dc2626' if is_overdue else st_fg};
                               box-shadow:0 1px 3px rgba(0,0,0,0.05)">
                  <div style="display:flex;align-items:center;gap:0.5rem;flex-wrap:wrap">
                    <span style="font-size:0.85rem;font-weight:600;color:#1a2744">{t['title']}</span>
                    {'<span style="font-size:0.7rem;color:#6b7280">· '+matter_ref+'</span>' if matter_ref else ''}
                    <span style="margin-left:auto;background:{st_bg};color:{st_fg};font-size:0.68rem;
                                 font-weight:600;padding:0.15rem 0.45rem;border-radius:20px">{STATUS_LABELS.get(status,status)}</span>
                  </div>
                  <div style="margin-top:0.25rem;display:flex;gap:1rem;font-size:0.73rem;color:#9ca3af;flex-wrap:wrap">
                    <span>{pri_icon} {pri.title()}</span>
                    {'<span>📅 '+('<b style="color:#dc2626">'+due_str+' overdue</b>' if is_overdue else due_str)+'</span>' if due_str else ''}
                    {'<span>👤 '+assigned+'</span>' if assigned else ''}
                  </div>
                </div>""",
                unsafe_allow_html=True,
            )
            c1, c2 = ctrl_col.columns([3, 1])
            new_s = c1.selectbox(
                "", STATUS_OPTS, index=STATUS_OPTS.index(status) if status in STATUS_OPTS else 0,
                format_func=lambda s: STATUS_LABELS.get(s, s),
                key=f"ops_ts_{t['id']}", label_visibility="collapsed",
            )
            if new_s != status:
                db.update_task(t["id"], status=new_s)
                st.rerun()
            if c2.button("🗑️", key=f"ops_del_{t['id']}"):
                db.delete_task(t["id"])
                st.rerun()

        st.caption(f"{len(all_tasks)} tasks"
                   + (f" · ⚠️ {overdue_count} overdue" if overdue_count else " · ✅ none overdue"))

# ══════════════════════════════════════════════════════════════════
# TAB 2 – DEADLINES CALENDAR
# ══════════════════════════════════════════════════════════════════
with tab_calendar:
    today      = datetime.date.today()
    all_tasks  = db.list_tasks()
    due_tasks  = [t for t in all_tasks if t.get("due_date") and
                  t.get("status") not in ("completed", "cancelled")]

    overdue = sorted(
        [t for t in due_tasks if datetime.date.fromisoformat(str(t["due_date"])[:10]) < today],
        key=lambda x: x["due_date"],
    )
    next7  = [t for t in due_tasks if today <= datetime.date.fromisoformat(str(t["due_date"])[:10]) <= today + datetime.timedelta(days=6)]
    next30 = [t for t in due_tasks if today + datetime.timedelta(days=7) <= datetime.date.fromisoformat(str(t["due_date"])[:10]) <= today + datetime.timedelta(days=30)]

    # Summary row
    c1, c2, c3, c4 = st.columns(4)
    for col, icon, label, value, color, bg in [
        (c1, "🔴", "Overdue",    len(overdue), "#dc2626", "#fef2f2"),
        (c2, "🟡", "Next 7 days", len(next7),  "#d97706", "#fffbeb"),
        (c3, "🔵", "Next 30 days",len(next30), "#2563eb", "#eff6ff"),
        (c4, "✅", "Total Active", len(due_tasks), "#1a2744", "#e8f0fe"),
    ]:
        col.markdown(
            f"""<div style="background:{bg};border-radius:10px;padding:0.75rem 1rem;
                            border-left:4px solid {color}">
              <p style="margin:0;font-size:0.72rem;font-weight:600;color:#6b7280;
                        text-transform:uppercase">{icon} {label}</p>
              <p style="margin:0.2rem 0 0;font-size:1.6rem;font-weight:700;color:{color}">{value}</p>
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    def _task_row(t, color):
        due = str(t["due_date"])[:10]
        try:
            days = (datetime.date.fromisoformat(due) - today).days
        except Exception:
            days = 0
        label = (f"**{abs(days)}d overdue**" if days < 0
                 else "Today" if days == 0
                 else "Tomorrow" if days == 1
                 else f"in {days}d")
        pri = (t.get("priority") or "medium").lower()
        icon = {"high":"🔴","medium":"🟡","low":"🟢"}.get(pri,"⚪")
        st.markdown(
            f"""<div style="display:flex;align-items:center;gap:0.75rem;padding:0.5rem 0.75rem;
                            background:#fff;border-radius:8px;margin-bottom:0.3rem;
                            border-left:3px solid {color};border:1px solid rgba(0,0,0,0.06)">
              <span style="font-size:0.85rem;flex:1;color:#1a2744">{t['title']}</span>
              <span style="font-size:0.73rem;color:#6b7280">{due}</span>
              <span style="font-size:0.73rem;color:{color};font-weight:600">{label}</span>
              <span>{icon}</span>
            </div>""",
            unsafe_allow_html=True,
        )

    if overdue:
        section(f"🔴 Overdue ({len(overdue)})")
        for t in overdue:
            _task_row(t, "#dc2626")
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    if next7:
        section(f"🟡 Next 7 Days ({len(next7)})")
        for t in sorted(next7, key=lambda x: x["due_date"]):
            _task_row(t, "#d97706")
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    if next30:
        section(f"🔵 Next 30 Days ({len(next30)})")
        for t in sorted(next30, key=lambda x: x["due_date"]):
            _task_row(t, "#2563eb")

    if not overdue and not next7 and not next30:
        st.success("✅ No upcoming or overdue deadlines in the next 30 days.")

# ══════════════════════════════════════════════════════════════════
# TAB 3 – WORKFLOW TEMPLATES
# ══════════════════════════════════════════════════════════════════
with tab_workflow:
    all_templates = {**BUILTIN_TEMPLATES, **st.session_state.wf_templates}

    col_list, col_detail = st.columns([2, 3], gap="large")

    with col_list:
        section("📋 Templates")
        if "wf_selected" not in st.session_state:
            st.session_state.wf_selected = list(all_templates.keys())[0]

        for name in all_templates:
            is_custom = name in st.session_state.wf_templates
            selected  = st.session_state.wf_selected == name
            bg = "#1a2744" if selected else "#fff"
            fg = "#fff"    if selected else "#1a2744"
            tag = " <small style='color:#c9a84c'>(custom)</small>" if is_custom else ""
            st.markdown(
                f"""<div style="background:{bg};color:{fg};border-radius:8px;
                               padding:0.6rem 0.85rem;margin-bottom:0.3rem;cursor:pointer;
                               border:1px solid {'#1a2744' if selected else 'rgba(0,0,0,0.08)'}">
                  <span style="font-size:0.85rem;font-weight:{'600' if selected else '400'}">{name}</span>{tag}
                  <span style="float:right;font-size:0.72rem;opacity:0.7">{len(all_templates[name])} steps</span>
                </div>""",
                unsafe_allow_html=True,
            )
            if st.button("Select", key=f"wf_sel_{name}", use_container_width=True,
                         type="primary" if selected else "secondary"):
                st.session_state.wf_selected = name
                st.rerun()

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        section("➕ Create Custom Template")
        with st.form("new_template_form", clear_on_submit=True):
            t_name  = st.text_input("Template name *", placeholder="e.g. Immigration Appeal")
            t_steps = st.text_area("Steps (one per line) *", height=120,
                                    placeholder="Step 1\nStep 2\nStep 3…")
            if st.form_submit_button("Save Template", type="primary"):
                if t_name.strip() and t_steps.strip():
                    steps = [s.strip() for s in t_steps.strip().split("\n") if s.strip()]
                    st.session_state.wf_templates[t_name.strip()] = steps
                    st.session_state.wf_selected = t_name.strip()
                    st.rerun()
                else:
                    st.warning("Name and at least one step are required.")

    with col_detail:
        sel = st.session_state.get("wf_selected")
        if sel and sel in all_templates:
            steps = all_templates[sel]
            section(f"📋 {sel}")
            for i, step in enumerate(steps, 1):
                st.markdown(
                    f"""<div style="display:flex;align-items:center;gap:0.75rem;
                                    padding:0.55rem 0.85rem;background:#fff;
                                    border-radius:8px;margin-bottom:0.3rem;
                                    border:1px solid rgba(0,0,0,0.07)">
                      <span style="background:#1a2744;color:#fff;border-radius:50%;
                                   width:22px;height:22px;display:flex;align-items:center;
                                   justify-content:center;font-size:0.72rem;font-weight:700;
                                   flex-shrink:0">{i}</span>
                      <span style="font-size:0.85rem;color:#374151">{step}</span>
                    </div>""",
                    unsafe_allow_html=True,
                )

            st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
            section("⚡ Apply to Matter")
            matters = db.list_matters(status="Active")
            if matters:
                m_opts = {f"{m['ref']} – {m['title'][:40]}": m["id"] for m in matters}
                a1, a2, a3 = st.columns([3, 2, 1])
                apply_m   = a1.selectbox("Matter", list(m_opts.keys()), key="wf_apply_m",
                                          label_visibility="collapsed")
                apply_pri = a2.selectbox("Priority", ["high","medium","low"], index=1,
                                          key="wf_apply_pri", label_visibility="collapsed")
                if a3.button("Apply ✓", type="primary", key="wf_apply_btn", use_container_width=True):
                    mid = m_opts[apply_m]
                    for step in steps:
                        db.create_task(title=step, matter_id=mid, priority=apply_pri,
                                        status="pending")
                    st.success(f"✅ {len(steps)} tasks created in {apply_m.split('–')[0].strip()}.")
                    st.rerun()
            else:
                st.info("No active matters to apply this template to.")

            if sel in st.session_state.wf_templates:
                if st.button("🗑️ Delete this template", key="wf_del"):
                    del st.session_state.wf_templates[sel]
                    st.session_state.wf_selected = list(BUILTIN_TEMPLATES.keys())[0]
                    st.rerun()
