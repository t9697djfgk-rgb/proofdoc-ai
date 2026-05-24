import streamlit as st
from utils.shared.sidebar import setup_page
from utils.shared.styles import slim_header, section

setup_page()
slim_header("🚀", "Getting Started", "Set up your workspace in a few simple steps")

# ── Step state ─────────────────────────────────────────────────────
if "onb_step" not in st.session_state:
    st.session_state.onb_step = 1

STEPS = [
    ("🏢", "Organisation",   "Confirm your firm details"),
    ("👤", "Your Profile",   "Set your role and display name"),
    ("⚖️", "First Matter",   "Create your first matter"),
    ("🔑", "AI Tools",       "Connect your API key"),
    ("✅", "All Done",       "You're ready to go"),
]
TOTAL = len(STEPS)
current = st.session_state.onb_step

# ── Progress bar ───────────────────────────────────────────────────
progress_pct = int((current - 1) / (TOTAL - 1) * 100)
st.markdown(
    f"<div style='background:#e5e7eb;border-radius:99px;height:8px;margin-bottom:1.5rem'>"
    f"<div style='background:linear-gradient(90deg,#1a2744,#c9a84c);border-radius:99px;"
    f"height:100%;width:{progress_pct}%;transition:width .4s'></div></div>",
    unsafe_allow_html=True,
)

# ── Step indicators ────────────────────────────────────────────────
cols = st.columns(TOTAL)
for i, (icon, label, _) in enumerate(STEPS, 1):
    done = i < current
    active = i == current
    bg = "#1a2744" if active else ("#c9a84c" if done else "#f3f4f6")
    fc = "#fff" if (active or done) else "#6b7280"
    bd = "#1a2744" if active else ("#c9a84c" if done else "#e5e7eb")
    cols[i-1].markdown(
        f"<div style='text-align:center;padding:0.5rem 0'>"
        f"<div style='display:inline-flex;align-items:center;justify-content:center;"
        f"width:2.2rem;height:2.2rem;border-radius:50%;background:{bg};"
        f"border:2px solid {bd};color:{fc};font-size:1rem;margin-bottom:0.25rem'>"
        f"{'✓' if done else icon}</div>"
        f"<div style='font-size:0.72rem;color:{'#1a2744' if active else '#6b7280'};"
        f"font-weight:{'600' if active else '400'}'>{label}</div></div>",
        unsafe_allow_html=True,
    )

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

# ── Step panels ────────────────────────────────────────────────────
user = st.session_state.get("user", {})

if current == 1:
    section("🏢 Organisation Details")
    st.markdown(
        "<div style='background:linear-gradient(135deg,#f0f4ff,#f8fafc);border:1px solid #c7d2fe;"
        "border-radius:10px;padding:1rem 1.25rem;margin-bottom:1rem'>"
        "This workspace is configured for your organisation. "
        "Below is a summary of your account settings.</div>",
        unsafe_allow_html=True,
    )
    col1, col2 = st.columns(2)
    col1.text_input("Organisation Name", value=user.get("organization_name", ""), disabled=True, key="onb_org_name")
    col2.text_input("Your Role", value=(user.get("role") or "").title(), disabled=True, key="onb_role")
    st.info("ℹ️ Organisation settings can be changed by an Admin in **Settings → Organisation**.")

elif current == 2:
    section("👤 Your Profile")
    full_name = st.text_input("Display Name", value=user.get("full_name", ""), key="onb_fullname")
    title_val = st.text_input("Job Title (optional)", value=user.get("title", ""), key="onb_title",
                               placeholder="e.g. Senior Associate, Partner")
    if st.session_state.get("onb_profile_saved"):
        st.success("✅ Profile updated!")
    if st.button("Save Profile", type="primary", key="onb_save_profile"):
        if full_name.strip():
            try:
                from utils import database as db
                db.get_db().table("profiles").update({
                    "full_name": full_name.strip(),
                    "title": title_val.strip() or None,
                }).eq("id", user["id"]).execute()
                st.session_state.user["full_name"] = full_name.strip()
                st.session_state.user["title"] = title_val.strip() or None
                st.session_state.onb_profile_saved = True
                st.rerun()
            except Exception as exc:
                st.error(f"Could not save: {exc}")
        else:
            st.warning("Please enter a display name.")

elif current == 3:
    section("⚖️ Create Your First Matter")
    st.markdown("Matters are the core of your workspace — each case, transaction, or project lives here.")
    existing = []
    try:
        from utils import database as db
        existing = db.list_matters()
    except Exception:
        pass
    if existing:
        st.success(f"✅ You already have {len(existing)} matter(s). You're all set for this step!")
    else:
        with st.form("onb_matter_form"):
            m_title = st.text_input("Matter Title *", placeholder="e.g. Smith v Jones — Contract Dispute")
            m_ref   = st.text_input("Reference Number", placeholder="e.g. 2026/001")
            m_type  = st.selectbox("Matter Type", ["litigation", "corporate", "conveyancing", "family",
                                                    "employment", "criminal", "immigration", "other"])
            m_juris = st.text_input("Jurisdiction", placeholder="e.g. England & Wales")
            submitted = st.form_submit_button("Create Matter", type="primary", use_container_width=True)
            if submitted:
                if not m_title.strip():
                    st.error("Matter title is required.")
                else:
                    try:
                        db.create_matter(
                            title=m_title.strip(),
                            reference_number=m_ref.strip() or None,
                            matter_type=m_type,
                            jurisdiction=m_juris.strip() or None,
                            status="active",
                        )
                        st.success("✅ Matter created!")
                        st.session_state.onb_step = 4
                        st.rerun()
                    except Exception as exc:
                        st.error(f"Failed: {exc}")

elif current == 4:
    section("🔑 Connect AI Tools")
    st.markdown(
        "ProofDoc AI tools use **Claude Opus 4.7** — Anthropic's most capable model. "
        "Your API key is stored only in your session and is never saved to the database."
    )
    try:
        import os
        key_found = os.environ.get("ANTHROPIC_API_KEY") or st.secrets.get("ANTHROPIC_API_KEY")
    except Exception:
        key_found = None
    if key_found:
        st.success("✅ API key is already configured in your environment. AI tools are ready!")
    else:
        st.markdown(
            "<div style='background:#fffbeb;border:1px solid #fde68a;border-radius:8px;"
            "padding:0.85rem 1rem;margin-bottom:1rem'>"
            "1. Go to <b>console.anthropic.com</b> and create an API key.<br>"
            "2. Paste it in the sidebar field labelled <b>Anthropic API Key</b>.<br>"
            "3. The key persists for your session and is cleared on sign-out.</div>",
            unsafe_allow_html=True,
        )
        st.info("You can skip this step and add the key later from the sidebar.")

elif current == 5:
    st.markdown(
        "<div style='text-align:center;padding:2rem 1rem'>"
        "<div style='font-size:3.5rem'>🎉</div>"
        "<h2 style='color:#1a2744;font-family:Playfair Display,serif;margin:.5rem 0'>You're all set!</h2>"
        "<p style='color:#6b7280;font-size:1rem'>Your workspace is ready. Here's a quick tour of what you can do.</p>"
        "</div>",
        unsafe_allow_html=True,
    )
    c1, c2, c3 = st.columns(3)
    cards = [
        ("📁", "Matters", "Create and manage cases, track status, add team members."),
        ("🤖", "AI Tools", "Draft documents, review contracts, research case law."),
        ("💼", "Billing", "Log time, generate invoices, export as PDF."),
    ]
    for col, (icon, title, desc) in zip([c1, c2, c3], cards):
        col.markdown(
            f"<div style='background:#f8fafc;border:1px solid #e5e7eb;border-radius:10px;"
            f"padding:1.25rem;text-align:center;height:130px'>"
            f"<div style='font-size:1.8rem'>{icon}</div>"
            f"<b style='color:#1a2744'>{title}</b>"
            f"<p style='color:#6b7280;font-size:0.8rem;margin-top:.4rem'>{desc}</p></div>",
            unsafe_allow_html=True,
        )
    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    st.session_state.onb_completed = True

# ── Navigation buttons ─────────────────────────────────────────────
st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)
nav1, nav2, nav3 = st.columns([1, 3, 1])

if current > 1:
    if nav1.button("← Back", use_container_width=True, key="onb_back"):
        st.session_state.onb_step -= 1
        st.rerun()

if current < TOTAL:
    label = "Next →" if current < TOTAL - 1 else "Finish →"
    if nav3.button(label, type="primary", use_container_width=True, key="onb_next"):
        st.session_state.onb_step += 1
        st.rerun()
elif current == TOTAL:
    if nav3.button("Go to Dashboard →", type="primary", use_container_width=True, key="onb_done"):
        st.switch_page("pages/p_lawyer_dashboard.py")
