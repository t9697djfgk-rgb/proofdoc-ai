import streamlit as st
from utils.shared.sidebar import setup_page
from utils.shared.styles import slim_header, inject_css, section
from utils.auth import require_admin
import utils.database as db
from utils import rwanda_laws as rl

setup_page()
user = require_admin()
inject_css()

slim_header("🛡️", "Admin Panel", f"{user['organization_name']} — user management, law database, audit")

# ── Stats banner ──────────────────────────────────────────────────
stats = db.dashboard_stats()
all_profiles = db.list_profiles(active_only=False)
active_users = sum(1 for p in all_profiles if p.get("is_active"))
s1, s2, s3, s4 = st.columns(4)
for col, icon, label, value, color, bg in [
    (s1, "👥", "Team Members",  active_users,                         "#1a2744", "#e8f0fe"),
    (s2, "⚖️", "Active Matters", stats.get("active_matters", 0),      "#059669", "#ecfdf5"),
    (s3, "🏢", "Clients",        stats.get("total_clients", 0),        "#d97706", "#fffbeb"),
    (s4, "📋", "Pending Tasks",  stats.get("pending_tasks", 0),        "#7c3aed", "#f5f3ff"),
]:
    col.markdown(
        f"""<div style="background:{bg};border-radius:12px;padding:0.9rem 1rem;
                        border-left:4px solid {color}">
          <p style="margin:0;font-size:0.72rem;font-weight:600;color:#6b7280;
                    text-transform:uppercase;letter-spacing:.05em">{icon} {label}</p>
          <p style="margin:0.2rem 0 0;font-size:1.8rem;font-weight:700;color:{color}">{value}</p>
        </div>""",
        unsafe_allow_html=True,
    )
st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

tab_users, tab_org, tab_laws, tab_audit = st.tabs([
    "👥 Users", "🏢 Organisation", "📚 Rwanda Laws", "📋 Audit Log",
])

# ── Users ─────────────────────────────────────────────────────────
with tab_users:
    section("👥 Team Members")
    profiles = all_profiles  # loaded above for stats
    ROLE_ICONS = {"admin": "🛡️", "lawyer": "⚖️", "staff": "👤", "client": "🏢", "intern": "🎓"}

    if profiles:
        for p in profiles:
            if p["id"] == user["id"]:
                continue
            is_active = p.get("is_active", True)
            role      = p.get("role", "staff")
            bg        = "#fff" if is_active else "#fafafa"
            border    = "rgba(0,0,0,0.07)" if is_active else "#e5e7eb"
            c_main, c_role, c_actions = st.columns([4, 2, 2])
            c_main.markdown(
                f"""<div style="background:{bg};border-radius:10px;padding:0.75rem 1rem;
                               border:1px solid {border};box-shadow:0 1px 4px rgba(0,0,0,0.04)">
                  <div style="display:flex;align-items:center;gap:0.5rem">
                    <span style="font-size:1.3rem">{ROLE_ICONS.get(role,'👤')}</span>
                    <div>
                      <p style="margin:0;font-weight:600;color:#1a2744;font-size:0.88rem">
                        {p.get('full_name','')}</p>
                      <p style="margin:0;font-size:0.75rem;color:#6b7280">{p.get('email','')}</p>
                      {'<p style="margin:0;font-size:0.72rem;color:#9ca3af">'+p.get('title','')+'</p>' if p.get('title') else ''}
                    </div>
                    <span style="margin-left:auto;font-size:0.7rem;font-weight:600;
                                 background:{'#dcfce7' if is_active else '#f1f5f9'};
                                 color:{'#16a34a' if is_active else '#94a3b8'};
                                 padding:0.15rem 0.5rem;border-radius:20px">
                      {'Active' if is_active else 'Inactive'}</span>
                  </div>
                </div>""",
                unsafe_allow_html=True,
            )
            ROLES = ["admin", "lawyer", "staff", "intern", "client"]
            new_role = c_role.selectbox(
                "Role", ROLES, index=ROLES.index(role) if role in ROLES else 1,
                key=f"role_{p['id']}", label_visibility="collapsed",
            )
            if new_role != role:
                db.get_db().table("profiles").update({"role": new_role}).eq("id", p["id"]).execute()
                st.rerun()
            ba, bb = c_actions.columns(2)
            if ba.button("Deactivate" if is_active else "Reactivate",
                         key=f"tog_{p['id']}", use_container_width=True):
                from utils.auth import deactivate_user
                deactivate_user(p["id"])
                st.rerun()
            st.markdown("<div style='height:0.25rem'></div>", unsafe_allow_html=True)
    else:
        st.caption("No team members yet.")

    st.markdown("<br>", unsafe_allow_html=True)
    section("➕ Add New User")
    with st.form("add_user_form"):
        c1, c2 = st.columns(2)
        new_name  = c1.text_input("Full Name *", key="au_name")
        new_email = c2.text_input("Email *",     key="au_email")
        c3, c4    = st.columns(2)
        new_role  = c3.selectbox("Role *", ["lawyer", "staff", "intern", "client", "admin"], key="au_role")
        new_title = c4.text_input("Title (optional)", placeholder="e.g. Associate", key="au_title")
        new_pw    = st.text_input("Temporary Password *", type="password",
                                   help="User should change this on first login", key="au_pw")
        if st.form_submit_button("Create User", type="primary"):
            if not new_name.strip() or not new_email.strip() or not new_pw:
                st.warning("Name, email and password are required.")
            elif len(new_pw) < 8:
                st.warning("Password must be at least 8 characters.")
            else:
                from utils.auth import create_user
                result = create_user(
                    email=new_email.strip(), password=new_pw,
                    full_name=new_name.strip(), role=new_role,
                    org_id=user["organization_id"], title=new_title.strip(),
                )
                if result["ok"]:
                    st.success(f"✅ User {new_name} created. Share credentials securely.")
                    st.rerun()
                else:
                    st.error(f"❌ {result['error']}")

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    section("🔑 Reset User Password")
    all_p = [p for p in profiles if p["id"] != user["id"]]
    if all_p:
        opts = {f"{p['full_name']} ({p['email']})": p for p in all_p}
        c1, c2, c3 = st.columns([3, 2, 1])
        sel   = c1.selectbox("Select user", list(opts.keys()), key="mgmt_sel",
                              label_visibility="collapsed")
        new_reset_pw = c2.text_input("New password", type="password", key="mgmt_reset_pw",
                                     label_visibility="collapsed", placeholder="New password (min 8 chars)")
        if c3.button("Reset", key="mgmt_reset_btn", use_container_width=True) and new_reset_pw:
            if len(new_reset_pw) < 8:
                st.warning("Min 8 characters.")
            else:
                from utils.auth import reset_password
                r = reset_password(opts[sel]["id"], new_reset_pw)
                if r["ok"]:
                    st.success("✅ Password reset.")
                else:
                    st.error(r["error"])

# ── Organisation ──────────────────────────────────────────────────
with tab_org:
    org_resp = db.get_db().table("organizations").select("*").eq("id", user["organization_id"]).maybe_single().execute()
    org = org_resp.data or {}
    section("🏢 Organisation Details")
    with st.form("org_form"):
        c1, c2 = st.columns(2)
        org_name  = c1.text_input("Firm Name",    value=org.get("name",""),    key="org_name")
        org_email = c2.text_input("Email",         value=org.get("email",""),   key="org_email")
        org_phone = c1.text_input("Phone",         value=org.get("phone",""),   key="org_phone")
        org_addr  = c2.text_input("Address",       value=org.get("address",""), key="org_addr")
        if st.form_submit_button("Save Changes", type="primary"):
            db.get_db().table("organizations").update({
                "name": org_name, "email": org_email,
                "phone": org_phone, "address": org_addr,
            }).eq("id", user["organization_id"]).execute()
            st.success("✅ Organisation details updated.")
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    c1.metric("Subscription Plan",   org.get("subscription_plan","starter").title())
    c2.metric("Subscription Status", org.get("subscription_status","active").title())

# ── Rwanda Laws Database ──────────────────────────────────────────
with tab_laws:
    tab_l1, tab_l2, tab_l3 = st.tabs(["📋 Law Database", "➕ Import / Add Law", "🔍 Browse Official Site"])

    with tab_l1:
        section("📚 Stored Laws")
        laws = rl.list_laws(status="in_force")
        pending = rl.list_laws(status="pending_review")
        if pending:
            st.warning(f"⚠️ {len(pending)} law(s) pending review in the admin queue.")
            for law in pending:
                c1, c2, c3 = st.columns([4, 2, 1])
                c1.markdown(f"**{law['title']}**")
                c2.caption(law.get("source_url",""))
                if c3.button("Approve", key=f"approve_{law['id']}"):
                    rl.update_law_status(law["id"], "in_force")
                    st.rerun()
            st.divider()
        if laws:
            cats = sorted({l.get("category","other") for l in laws})
            cat_filter = st.selectbox("Filter by category", ["All"] + cats, key="law_cat")
            shown = laws if cat_filter == "All" else [l for l in laws if l.get("category") == cat_filter]
            h = st.columns([4, 2, 2, 1])
            for col, lbl in zip(h, ["Title", "Number", "Category", "Actions"]):
                col.markdown(f"**{lbl}**")
            st.divider()
            for law in shown:
                r = st.columns([4, 2, 2, 1])
                r[0].markdown(f"[{law['title'][:55]}]({law.get('source_url','')})")
                r[1].text(law.get("law_number","—") or "—")
                r[2].text((law.get("category","") or "").title())
                if r[3].button("🗑️", key=f"del_law_{law['id']}", help="Delete law"):
                    rl.delete_law(law["id"])
                    st.rerun()
        else:
            st.info("No laws in database yet. Use the Import tab to add laws.")

    with tab_l2:
        c_imp, c_man = st.columns(2, gap="large")

        with c_imp:
            section("🌐 Import from amategeko.gov.rw")
            st.markdown("Paste a URL from the official Rwanda laws portal to import a law automatically.")
            with st.form("import_law_form"):
                law_url = st.text_input("Law URL *", placeholder="https://amategeko.gov.rw/law/...", key="il_url")
                law_cat = st.selectbox("Category *", [
                    "criminal", "civil", "commercial", "constitutional",
                    "labour", "tax", "family", "land", "procedure", "other",
                ], key="il_cat")
                if st.form_submit_button("Import Law", type="primary"):
                    if not law_url.strip().startswith("http"):
                        st.warning("Enter a valid URL.")
                    else:
                        with st.spinner("Fetching from official source…"):
                            result = rl.import_law_from_url(law_url.strip(), law_cat)
                        if result["ok"]:
                            st.success(f"✅ Imported: **{result['title']}** ({result['articles']} articles)")
                        else:
                            st.error(f"❌ {result['error']}")

        with c_man:
            section("✍️ Add Law Manually")
            with st.form("manual_law_form"):
                ml_title   = st.text_input("Law Title *",  key="ml_t")
                ml_number  = st.text_input("Law Number",   placeholder="No. 12/2023", key="ml_n")
                ml_cat     = st.selectbox("Category", [
                    "criminal","civil","commercial","constitutional",
                    "labour","tax","family","land","procedure","other",
                ], key="ml_cat")
                ml_summary = st.text_area("Summary",       height=80, key="ml_s")
                ml_url     = st.text_input("Source URL",   placeholder="https://amategeko.gov.rw/…", key="ml_u")
                ml_date    = st.text_input("In-Force Date (YYYY-MM-DD)", key="ml_d")
                ml_status  = st.selectbox("Status", ["in_force","pending_review"], key="ml_st")
                if st.form_submit_button("Add Law", type="primary"):
                    if not ml_title.strip():
                        st.warning("Title is required.")
                    else:
                        result = rl.add_law_manually(
                            title=ml_title.strip(), law_number=ml_number.strip(),
                            category=ml_cat, summary=ml_summary.strip(),
                            source_url=ml_url.strip(),
                            in_force_date=ml_date.strip() or None,
                            status=ml_status,
                        )
                        if result["ok"]:
                            st.success("✅ Law added to database.")
                            st.rerun()
                        else:
                            st.error(f"❌ {result['error']}")

    with tab_l3:
        section("🔍 Browse Official Rwanda Laws")
        st.markdown("Browse the official list of in-force laws from [amategeko.gov.rw](https://amategeko.gov.rw/laws/in-force/1).")
        page_num = st.number_input("Page", min_value=1, value=1, step=1, key="rl_page")
        if st.button("Load List", key="rl_load"):
            with st.spinner("Fetching official law list…"):
                law_list = rl.fetch_inforce_law_list(page_num)
            if law_list:
                st.success(f"Found {len(law_list)} laws on page {page_num}")
                for item in law_list:
                    c1, c2 = st.columns([5, 1])
                    c1.markdown(f"[{item['title'][:80]}]({item['url']})")
                    if c2.button("Import", key=f"quick_imp_{hash(item['url'])}"):
                        st.session_state["quick_import_url"] = item["url"]
                        st.rerun()
            else:
                st.info("No laws found on this page, or the site is unreachable.")
        if st.session_state.get("quick_import_url"):
            url = st.session_state.pop("quick_import_url")
            with st.spinner(f"Importing {url[:60]}…"):
                result = rl.import_law_from_url(url)
            if result["ok"]:
                st.success(f"✅ Imported: {result['title']}")
            else:
                st.error(f"❌ {result['error']}")

# ── Audit Log ─────────────────────────────────────────────────────
with tab_audit:
    section("📋 Audit Log")
    org_id = user["organization_id"]
    logs_resp = (
        db.get_db().table("audit_logs")
        .select("*")
        .eq("organization_id", org_id)
        .order("created_at", desc=True)
        .limit(200)
        .execute()
    )
    logs = logs_resp.data or []
    if logs:
        c1, c2 = st.columns(2)
        action_filter = c1.selectbox("Filter by action", ["All"] + sorted({l["action"] for l in logs}), key="al_act")
        actor_filter  = c2.selectbox("Filter by actor",  ["All"] + sorted({l.get("actor_name","") for l in logs if l.get("actor_name")}), key="al_actor")
        shown = [
            l for l in logs
            if (action_filter == "All" or l["action"] == action_filter)
            and (actor_filter == "All" or l.get("actor_name") == actor_filter)
        ]
        st.caption(f"Showing {len(shown)} of {len(logs)} entries")
        st.divider()
        h = st.columns([2, 2, 2, 3])
        for col, lbl in zip(h, ["Time", "Actor", "Action", "Resource"]):
            col.markdown(f"**{lbl}**")
        st.divider()
        for l in shown:
            r = st.columns([2, 2, 2, 3])
            r[0].caption(str(l.get("created_at",""))[:16].replace("T"," "))
            r[1].text(l.get("actor_name","—") or "—")
            r[2].markdown(f"`{l.get('action','')}`")
            r[3].text(f"{l.get('resource_type','')} {l.get('resource_id','')[:12] if l.get('resource_id') else ''}")
    else:
        st.info("No audit log entries yet.")
