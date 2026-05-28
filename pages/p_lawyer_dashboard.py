import streamlit as st
from utils.shared.sidebar import setup_page
from utils.shared.styles import inject_css, slim_header, currency_sym
from utils.auth import require_lawyer
import utils.database as db
from datetime import date


def _inject_bg() -> None:
    st.markdown("""
<style>
@keyframes dashFloatUp {
    0%   { transform:translateY(100vh) rotate(-8deg); opacity:0; }
    6%   { opacity:0.08; }
    94%  { opacity:0.08; }
    100% { transform:translateY(-60px) rotate(8deg); opacity:0; }
}
.dash-sym {
    position:fixed; bottom:-60px; pointer-events:none; z-index:1;
    color:#1a2744; user-select:none;
    animation:dashFloatUp linear infinite;
}
</style>

<svg xmlns="http://www.w3.org/2000/svg"
     style="position:fixed;inset:0;width:100vw;height:100vh;pointer-events:none;z-index:1">
  <defs><style>
    .nl{stroke:#1a2744;stroke-width:1;fill:none;animation:nlP ease-in-out infinite}
    .ng{fill:#c9a84c;animation:ndP ease-in-out infinite}
    .nn{fill:#1a2744;animation:ndP ease-in-out infinite}
    @keyframes ndP{0%,100%{opacity:.10}50%{opacity:.24}}
    @keyframes nlP{0%,100%{opacity:.05}50%{opacity:.13}}
  </style></defs>

  <!-- Top row connections -->
  <line class="nl" x1="8%"  y1="12%" x2="24%" y2="26%" style="animation-delay:.2s;animation-duration:4.1s"/>
  <line class="nl" x1="24%" y1="26%" x2="38%" y2="10%" style="animation-delay:.7s;animation-duration:5.2s"/>
  <line class="nl" x1="38%" y1="10%" x2="55%" y2="22%" style="animation-delay:1.3s;animation-duration:3.8s"/>
  <line class="nl" x1="55%" y1="22%" x2="70%" y2="12%" style="animation-delay:.4s;animation-duration:4.7s"/>
  <line class="nl" x1="70%" y1="12%" x2="84%" y2="28%" style="animation-delay:1.8s;animation-duration:4.3s"/>
  <line class="nl" x1="84%" y1="28%" x2="96%" y2="14%" style="animation-delay:.9s;animation-duration:5.0s"/>
  <!-- Top → Mid verticals -->
  <line class="nl" x1="8%"  y1="12%" x2="14%" y2="50%" style="animation-delay:.5s;animation-duration:4.6s"/>
  <line class="nl" x1="24%" y1="26%" x2="30%" y2="60%" style="animation-delay:1.1s;animation-duration:3.9s"/>
  <line class="nl" x1="55%" y1="22%" x2="50%" y2="56%" style="animation-delay:.3s;animation-duration:5.4s"/>
  <line class="nl" x1="70%" y1="12%" x2="66%" y2="54%" style="animation-delay:1.6s;animation-duration:4.2s"/>
  <line class="nl" x1="96%" y1="14%" x2="90%" y2="50%" style="animation-delay:.8s;animation-duration:3.7s"/>
  <!-- Mid row connections -->
  <line class="nl" x1="14%" y1="50%" x2="30%" y2="60%" style="animation-delay:1.4s;animation-duration:4.8s"/>
  <line class="nl" x1="30%" y1="60%" x2="50%" y2="56%" style="animation-delay:.6s;animation-duration:5.1s"/>
  <line class="nl" x1="50%" y1="56%" x2="66%" y2="54%" style="animation-delay:1.9s;animation-duration:3.6s"/>
  <line class="nl" x1="66%" y1="54%" x2="80%" y2="62%" style="animation-delay:.15s;animation-duration:4.4s"/>
  <line class="nl" x1="80%" y1="62%" x2="90%" y2="50%" style="animation-delay:1.2s;animation-duration:5.3s"/>
  <!-- Mid → Bottom verticals -->
  <line class="nl" x1="14%" y1="50%" x2="8%"  y2="80%" style="animation-delay:.45s;animation-duration:4.0s"/>
  <line class="nl" x1="30%" y1="60%" x2="26%" y2="84%" style="animation-delay:1.7s;animation-duration:4.5s"/>
  <line class="nl" x1="50%" y1="56%" x2="52%" y2="82%" style="animation-delay:.25s;animation-duration:5.5s"/>
  <line class="nl" x1="66%" y1="54%" x2="72%" y2="80%" style="animation-delay:1.05s;animation-duration:3.5s"/>
  <line class="nl" x1="90%" y1="50%" x2="94%" y2="80%" style="animation-delay:.65s;animation-duration:4.9s"/>
  <!-- Bottom row connections -->
  <line class="nl" x1="8%"  y1="80%" x2="26%" y2="84%" style="animation-delay:1.55s;animation-duration:4.6s"/>
  <line class="nl" x1="26%" y1="84%" x2="52%" y2="82%" style="animation-delay:.35s;animation-duration:5.0s"/>
  <line class="nl" x1="52%" y1="82%" x2="72%" y2="80%" style="animation-delay:1.85s;animation-duration:3.8s"/>
  <line class="nl" x1="72%" y1="80%" x2="94%" y2="80%" style="animation-delay:.75s;animation-duration:4.3s"/>

  <!-- Gold primary nodes -->
  <circle class="ng" cx="8%"  cy="12%" r="5" style="animation-delay:0s;animation-duration:3.0s"/>
  <circle class="ng" cx="55%" cy="22%" r="6" style="animation-delay:.6s;animation-duration:3.6s"/>
  <circle class="ng" cx="96%" cy="14%" r="4" style="animation-delay:1.2s;animation-duration:4.2s"/>
  <circle class="ng" cx="50%" cy="56%" r="5" style="animation-delay:.3s;animation-duration:2.8s"/>
  <circle class="ng" cx="52%" cy="82%" r="6" style="animation-delay:.9s;animation-duration:3.4s"/>
  <circle class="ng" cx="8%"  cy="80%" r="4" style="animation-delay:1.5s;animation-duration:3.8s"/>
  <!-- Navy secondary nodes -->
  <circle class="nn" cx="24%" cy="26%" r="3.5" style="animation-delay:.4s;animation-duration:4.5s"/>
  <circle class="nn" cx="38%" cy="10%" r="3"   style="animation-delay:1.1s;animation-duration:3.9s"/>
  <circle class="nn" cx="70%" cy="12%" r="4"   style="animation-delay:.7s;animation-duration:4.2s"/>
  <circle class="nn" cx="84%" cy="28%" r="3"   style="animation-delay:1.6s;animation-duration:3.5s"/>
  <circle class="nn" cx="14%" cy="50%" r="3.5" style="animation-delay:.2s;animation-duration:5.0s"/>
  <circle class="nn" cx="30%" cy="60%" r="3"   style="animation-delay:1.0s;animation-duration:4.4s"/>
  <circle class="nn" cx="66%" cy="54%" r="4"   style="animation-delay:.5s;animation-duration:3.9s"/>
  <circle class="nn" cx="80%" cy="62%" r="3"   style="animation-delay:1.4s;animation-duration:4.7s"/>
  <circle class="nn" cx="90%" cy="50%" r="3.5" style="animation-delay:.8s;animation-duration:3.6s"/>
  <circle class="nn" cx="26%" cy="84%" r="3"   style="animation-delay:1.3s;animation-duration:5.1s"/>
  <circle class="nn" cx="72%" cy="80%" r="4"   style="animation-delay:.1s;animation-duration:4.3s"/>
  <circle class="nn" cx="94%" cy="80%" r="3"   style="animation-delay:1.7s;animation-duration:3.7s"/>
</svg>

<!-- Floating legal + AI symbols -->
<span class="dash-sym" style="left:3%;font-size:1.6rem;animation-duration:22s;animation-delay:0s">§</span>
<span class="dash-sym" style="left:11%;font-size:1.1rem;animation-duration:18s;animation-delay:7s">⚖</span>
<span class="dash-sym" style="left:19%;font-size:1.3rem;animation-duration:26s;animation-delay:3s">¶</span>
<span class="dash-sym" style="left:28%;font-size:1.0rem;animation-duration:20s;animation-delay:11s">§</span>
<span class="dash-sym" style="left:37%;font-size:1.4rem;animation-duration:24s;animation-delay:2s">⚖</span>
<span class="dash-sym" style="left:46%;font-size:1.1rem;animation-duration:19s;animation-delay:9s">¶</span>
<span class="dash-sym" style="left:57%;font-size:1.5rem;animation-duration:23s;animation-delay:5s">§</span>
<span class="dash-sym" style="left:67%;font-size:1.2rem;animation-duration:21s;animation-delay:14s">⚖</span>
<span class="dash-sym" style="left:76%;font-size:1.0rem;animation-duration:25s;animation-delay:1s">¶</span>
<span class="dash-sym" style="left:85%;font-size:1.4rem;animation-duration:17s;animation-delay:8s">§</span>
<span class="dash-sym" style="left:93%;font-size:1.3rem;animation-duration:22s;animation-delay:4s">⚖</span>
    """, unsafe_allow_html=True)


setup_page()
user = require_lawyer()
inject_css()
_inject_bg()

first_name = user["full_name"].split()[0]
org_name   = user["organization_name"]
role_label = user["role"].title()

# ── Greeting ──────────────────────────────────────────────────────
today = date.today()
hour  = __import__("datetime").datetime.now().hour
greeting = "Good morning" if hour < 12 else ("Good afternoon" if hour < 17 else "Good evening")

_greet_col, _ref_col = st.columns([9, 1])
_greet_col.markdown(
    f"""
    <div style="margin-bottom:1.25rem">
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
_ref_col.markdown("<div style='height:1.1rem'></div>", unsafe_allow_html=True)
_dash_refresh = _ref_col.button("↻", key="dash_refresh", help="Refresh dashboard data",
                                 use_container_width=True)

# ── Load data ─────────────────────────────────────────────────────
_dash_loaded = st.session_state.get("_dash_loaded_key") == st.session_state.get("user", {}).get("id")
if not _dash_loaded:
    with st.spinner("Loading your dashboard…"):
        stats   = db.dashboard_stats()
        billing = db.billing_analytics()
        notifs  = db.list_notifications(limit=8)
    st.session_state["_dash_stats"]   = stats
    st.session_state["_dash_billing"] = billing
    st.session_state["_dash_notifs"]  = notifs
    st.session_state["_dash_loaded_key"] = st.session_state.get("user", {}).get("id")
else:
    stats   = st.session_state.get("_dash_stats",   {})
    billing = st.session_state.get("_dash_billing", {})
    notifs  = st.session_state.get("_dash_notifs",  [])

active_matters  = stats.get("active_matters", 0)
total_clients   = stats.get("total_clients",  0)
pending_tasks   = stats.get("pending_tasks",  0)
overdue_tasks   = stats.get("overdue_tasks",  0)
recent_matters  = stats.get("recent_matters", [])
overdue_list    = stats.get("overdue_task_list", [])
upcoming_tasks  = stats.get("upcoming_tasks", [])
recent_activity = stats.get("recent_activity", [])

rev_month = billing.get("revenue_month", 0)
wip       = billing.get("wip", 0)

if _dash_refresh:
    st.session_state.pop("_dash_loaded_key", None)
    st.rerun()

# ── KPI Cards (6 cards: 3+3) ──────────────────────────────────────
CARDS_ROW1 = [
    ("⚖️", "Active Matters", active_matters, "#1a2744", "#e8f0fe", None),
    ("👥", "Clients",        total_clients,  "#059669", "#ecfdf5", None),
    ("📋", "Pending Tasks",  pending_tasks,  "#d97706", "#fffbeb", None),
]
CARDS_ROW2 = [
    ("⚠️", "Overdue Tasks",     overdue_tasks,                  "#dc2626", "#fef2f2",
     "Needs attention" if overdue_tasks else "All on track"),
    ("💰", "Revenue This Month", f"{currency_sym()}{rev_month:,.0f}",  "#7c3aed", "#f5f3ff", None),
    ("⏳", "WIP (Unbilled)",     f"{currency_sym()}{wip:,.0f}",        "#0891b2", "#ecfeff", None),
]

for row in [CARDS_ROW1, CARDS_ROW2]:
    cols = st.columns(3, gap="small")
    for col, (icon, label, value, color, bg, note) in zip(cols, row):
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
    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

# ── Analytics Strip ────────────────────────────────────────────────
_by_status = billing.get("by_status", {})
_by_type   = billing.get("by_type", {})
_top_m     = billing.get("top_matters", [])
if _by_status or _top_m:
    with st.expander("📊 Practice Analytics", expanded=False):
        _ac1, _ac2, _ac3 = st.columns(3, gap="large")

        with _ac1:
            st.markdown(
                '<p style="font-size:0.75rem;font-weight:700;color:#1a2744;text-transform:uppercase;'
                'letter-spacing:0.05em;margin-bottom:0.5rem">📁 Matters by Status</p>',
                unsafe_allow_html=True,
            )
            _S_COLORS = {"Active": "#16a34a", "On Hold": "#d97706", "Closed": "#64748b", "Archived": "#94a3b8"}
            _total_m = sum(_by_status.values()) or 1
            for _s, _cnt in sorted(_by_status.items(), key=lambda x: -x[1]):
                _pct = _cnt / _total_m * 100
                _sc = _S_COLORS.get(_s, "#6b7280")
                st.markdown(
                    f'<div style="margin-bottom:.35rem">'
                    f'<div style="display:flex;justify-content:space-between;font-size:.8rem;margin-bottom:.15rem">'
                    f'<span style="color:#374151">{_s}</span><span style="font-weight:600;color:{_sc}">{_cnt}</span></div>'
                    f'<div style="background:#f1f5f9;border-radius:4px;height:6px">'
                    f'<div style="background:{_sc};width:{_pct:.0f}%;height:6px;border-radius:4px"></div></div></div>',
                    unsafe_allow_html=True,
                )

        with _ac2:
            st.markdown(
                '<p style="font-size:0.75rem;font-weight:700;color:#1a2744;text-transform:uppercase;'
                'letter-spacing:0.05em;margin-bottom:0.5rem">⚖️ Matters by Type</p>',
                unsafe_allow_html=True,
            )
            _total_t = sum(_by_type.values()) or 1
            for _t, _cnt in sorted(_by_type.items(), key=lambda x: -x[1])[:6]:
                _pct = _cnt / _total_t * 100
                st.markdown(
                    f'<div style="margin-bottom:.35rem">'
                    f'<div style="display:flex;justify-content:space-between;font-size:.8rem;margin-bottom:.15rem">'
                    f'<span style="color:#374151">{_t[:22]}</span><span style="font-weight:600;color:#1a2744">{_cnt}</span></div>'
                    f'<div style="background:#f1f5f9;border-radius:4px;height:6px">'
                    f'<div style="background:#c9a84c;width:{_pct:.0f}%;height:6px;border-radius:4px"></div></div></div>',
                    unsafe_allow_html=True,
                )

        with _ac3:
            st.markdown(
                '<p style="font-size:0.75rem;font-weight:700;color:#1a2744;text-transform:uppercase;'
                'letter-spacing:0.05em;margin-bottom:0.5rem">💰 Top Matters by Value</p>',
                unsafe_allow_html=True,
            )
            if _top_m:
                _max_v = max((m["value"] for m in _top_m), default=1) or 1
                for _tm in _top_m:
                    _pct = _tm["value"] / _max_v * 100
                    st.markdown(
                        f'<div style="margin-bottom:.35rem">'
                        f'<div style="display:flex;justify-content:space-between;font-size:.78rem;margin-bottom:.15rem">'
                        f'<span style="color:#374151">{_tm["ref"]} {_tm["title"][:18]}</span>'
                        f'<span style="font-weight:600;color:#059669">{currency_sym()}{_tm["value"]:,.0f}</span></div>'
                        f'<div style="background:#f1f5f9;border-radius:4px;height:6px">'
                        f'<div style="background:#059669;width:{_pct:.0f}%;height:6px;border-radius:4px"></div></div></div>',
                        unsafe_allow_html=True,
                    )
            else:
                st.caption("Log time entries to see revenue data.")

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

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

    # ── Upcoming deadlines ─────────────────────────────────────────
    st.markdown(
        '<p style="font-size:0.78rem;font-weight:700;color:#1a2744;text-transform:uppercase;'
        'letter-spacing:0.07em;margin-bottom:0.75rem">📅 Upcoming Deadlines (14 days)</p>',
        unsafe_allow_html=True,
    )
    if upcoming_tasks:
        for t in upcoming_tasks:
            _due_s = str(t.get("due_date", ""))[:10]
            try:
                import datetime as _dt3
                _days_left = (_dt3.date.fromisoformat(_due_s) - date.today()).days
                _dl_label = "Today" if _days_left == 0 else f"in {_days_left}d"
                _dl_color = "#7c3aed" if _days_left == 0 else ("#d97706" if _days_left <= 3 else "#059669")
            except Exception:
                _dl_label, _dl_color = _due_s, "#64748b"
            st.markdown(
                f"""<div style="background:#fff;border-radius:8px;padding:0.55rem 0.85rem;
                                margin-bottom:0.35rem;border:1px solid rgba(0,0,0,0.06);
                                border-left:3px solid {_dl_color};
                                display:flex;align-items:center;gap:0.75rem">
                  <div style="flex:1;min-width:0">
                    <p style="margin:0;font-size:0.84rem;font-weight:500;color:#1a1a2e">
                      {t.get('title','Untitled task')}</p>
                  </div>
                  <span style="font-size:0.7rem;font-weight:600;color:{_dl_color};
                               white-space:nowrap">{_dl_label}</span>
                </div>""",
                unsafe_allow_html=True,
            )
    else:
        st.markdown(
            '<div style="background:#f0fdf4;border-radius:8px;padding:0.75rem 1rem;'
            'border-left:3px solid #16a34a;color:#166534;font-size:0.85rem">'
            '📅 No deadlines in the next 14 days.</div>',
            unsafe_allow_html=True,
        )

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

# ── Recent Activity ───────────────────────────────────────────────
if recent_activity:
    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
    st.markdown(
        '<p style="font-size:0.78rem;font-weight:700;color:#1a2744;text-transform:uppercase;'
        'letter-spacing:0.07em;margin-bottom:0.75rem">🕐 Recent Activity</p>',
        unsafe_allow_html=True,
    )
    _ACT_ICONS = {
        "CREATE": "✨", "UPDATE": "✏️", "DELETE": "🗑️",
        "MATTER": "📁", "LOGIN": "🔐", "LOGOUT": "🚪",
        "UPLOAD": "📤", "DOWNLOAD": "📥",
    }
    act_cols = st.columns(2, gap="small")
    for i, a in enumerate(recent_activity):
        _root_a = a.get("action", "").split("_")[0].upper()
        _icon_a = _ACT_ICONS.get(_root_a, "•")
        _ts_a   = str(a.get("created_at", ""))[:16].replace("T", " ")
        _actor_a = a.get("actor_name", "System") or "System"
        act_cols[i % 2].markdown(
            f"""<div style="background:#fff;border-radius:8px;padding:0.5rem 0.75rem;
                            margin-bottom:0.35rem;border:1px solid rgba(0,0,0,0.06);
                            display:flex;align-items:center;gap:0.6rem">
              <span style="font-size:0.9rem">{_icon_a}</span>
              <div style="flex:1;min-width:0">
                <p style="margin:0;font-size:0.78rem;font-weight:600;color:#1a2744;
                          white-space:nowrap;overflow:hidden;text-overflow:ellipsis">
                  {a.get('action','')}</p>
                <p style="margin:0;font-size:0.7rem;color:#9ca3af">{_actor_a} · {_ts_a}</p>
              </div>
            </div>""",
            unsafe_allow_html=True,
        )
