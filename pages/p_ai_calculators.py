import streamlit as st
from datetime import date, timedelta
from utils.shared.sidebar import setup_page
from utils.shared.styles import slim_header, group_header, section

from utils.auth import require_lawyer
api_key = setup_page()
require_lawyer()
slim_header("🧮", "Calculators", "Court deadlines, limitation periods, interest, and damages calculators")
st.markdown(
    '<div class="disclaimer-box">ℹ️ <strong>Disclaimer:</strong> Calculators provide estimates only. '
    "Always verify deadlines and limitation periods with a qualified lawyer and official court rules.</div>",
    unsafe_allow_html=True,
)

group_header("Deadlines & Limitation Periods")

calc1, calc2 = st.tabs(["📅 Court Deadline Calculator", "⏳ Limitation Period Calculator"])

# ── 1. Court Deadline Calculator ──────────────────────────────────
with calc1:
    st.markdown("Calculate procedural deadlines based on trigger date, jurisdiction, and event type.")
    c1, c2, c3 = st.columns(3)
    trigger_date   = c1.date_input("Trigger Date", value=date.today(), key="cdc_td")
    jurisdiction   = c2.selectbox("Jurisdiction", ["England & Wales", "Scotland", "Northern Ireland",
                                                     "United States", "Rwanda", "International / Other"], key="cdc_jur")
    event_type     = c3.selectbox("Event Type", [
        "Service of claim form", "Service of defence", "Service of reply",
        "Summary judgment application", "Filing of appeal", "Service of order",
        "Expert report exchange", "Witness statement exchange", "Trial preparation",
    ], key="cdc_ev")

    # Deadline rules (simplified; always recommend verifying against CPR/court rules)
    _RULES = {
        "Service of claim form":          {"calendar": 4, "working": False, "note": "CPR 7.5 — 4 months from issue (within jurisdiction)"},
        "Service of defence":             {"calendar": 14, "working": False, "note": "CPR 15.4 — 14 days from service of particulars"},
        "Service of reply":               {"calendar": 14, "working": False, "note": "CPR 15.8 — 14 days from service of defence"},
        "Summary judgment application":   {"calendar": 14, "working": True,  "note": "CPR 24.4 — hearing at least 14 days' notice"},
        "Filing of appeal":               {"calendar": 21, "working": False, "note": "CPR 52.12 — 21 days from decision"},
        "Service of order":               {"calendar": 7,  "working": True,  "note": "Standard — 7 working days from sealing"},
        "Expert report exchange":         {"calendar": 0,  "working": False, "note": "Set by court directions order — enter court order date"},
        "Witness statement exchange":     {"calendar": 0,  "working": False, "note": "Set by court directions order — enter court order date"},
        "Trial preparation":              {"calendar": 0,  "working": False, "note": "Varies — check court directions"},
    }

    rule = _RULES.get(event_type, {"calendar": 0, "working": False, "note": "Check relevant court rules"})
    days = rule["calendar"]

    additional_days = st.number_input("Override / Additional Days", min_value=0, value=days, step=1, key="cdc_days",
                                      help="Edit if your court order specifies a different period")

    if additional_days > 0:
        if rule["working"]:
            # Count working days (Mon–Fri, no public holidays approximation)
            d = trigger_date
            counted = 0
            while counted < additional_days:
                d += timedelta(days=1)
                if d.weekday() < 5:
                    counted += 1
            deadline_date = d
            day_type = "working days"
        else:
            deadline_date = trigger_date + timedelta(days=additional_days)
            day_type = "calendar days"

        today = date.today()
        days_remaining = (deadline_date - today).days

        st.divider()
        m1, m2, m3 = st.columns(3)
        m1.metric("Trigger Date",    trigger_date.strftime("%d %b %Y"))
        m2.metric("Deadline",        deadline_date.strftime("%d %b %Y"))
        if days_remaining < 0:
            m3.metric("Status", "OVERDUE", delta=f"{abs(days_remaining)} days ago", delta_color="inverse")
        elif days_remaining <= 7:
            m3.metric("Days Remaining", days_remaining, delta="URGENT", delta_color="inverse")
        else:
            m3.metric("Days Remaining", days_remaining)

        st.info(f"ℹ️ **Rule:** {rule['note']} ({additional_days} {day_type})")

        # Timeline display
        section("📅 Deadline Timeline")
        milestones = [
            (trigger_date, "Trigger Date", "#16a34a"),
            (trigger_date + timedelta(days=max(1, additional_days // 4)), "25% mark", "#64748b"),
            (trigger_date + timedelta(days=max(1, additional_days // 2)), "50% mark", "#64748b"),
            (deadline_date - timedelta(days=max(1, additional_days // 7)), "1 week warning", "#d97706"),
            (deadline_date, "DEADLINE", "#dc2626"),
        ]
        for d_date, label, color in milestones:
            remaining = (d_date - today).days
            if remaining < 0:
                status_txt, status_color = "✅ Passed", "#16a34a"
            elif remaining <= 7:
                status_txt, status_color = f"⚠️ {remaining}d", "#dc2626"
            else:
                status_txt, status_color = f"{remaining}d remaining", "#64748b"
            st.markdown(
                f'<div style="background:white;border:1px solid #e2e8f0;border-radius:8px;'
                f'padding:.55rem 1rem;margin-bottom:.3rem;display:flex;align-items:center;gap:1rem;flex-wrap:wrap">'
                f'<div style="width:10px;height:10px;background:{color};border-radius:50%;flex-shrink:0"></div>'
                f'<span style="font-weight:700;color:#1a2744;font-size:.85rem">{d_date.strftime("%d %b %Y")}</span>'
                f'<span style="font-size:.82rem;color:#475569">{label}</span>'
                f'<span style="margin-left:auto;font-size:.8rem;font-weight:600;color:{status_color}">{status_txt}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # Export
        st.markdown("<br>", unsafe_allow_html=True)
        export_text = (
            f"Court Deadline Calculation\n"
            f"Event: {event_type}\nJurisdiction: {jurisdiction}\n"
            f"Trigger: {trigger_date}\nPeriod: {additional_days} {day_type}\n"
            f"Deadline: {deadline_date}\nDays remaining: {days_remaining}\n"
            f"Rule: {rule['note']}"
        )
        st.download_button("📥 Export Deadline (.txt)", export_text,
                           "deadline.txt", "text/plain", key="cdc_exp")
    else:
        st.info("ℹ️ Enter or set a day count above to calculate the deadline.")

# ── 2. Limitation Period Calculator ──────────────────────────────
with calc2:
    st.markdown("Calculate when a limitation period expires based on cause of action and jurisdiction.")
    c1, c2, c3 = st.columns(3)
    accrual_date   = c1.date_input("Cause of Action Accrual Date", value=date.today() - timedelta(days=365), key="lp_ad")
    lp_jurisdiction= c2.selectbox("Jurisdiction", ["England & Wales", "Scotland", "Rwanda",
                                                     "United States (Federal)", "Other"], key="lp_jur")
    cause_of_action= c3.selectbox("Cause of Action", [
        "Simple contract",
        "Specialty / deed",
        "Tort (general)",
        "Personal injury",
        "Latent damage (negligence)",
        "Fraud / deliberate concealment",
        "Recovery of land",
        "Enforcement of judgment",
    ], key="lp_coa")

    # Limitation periods (England & Wales — Limitation Act 1980 simplified)
    _LP = {
        "England & Wales": {
            "Simple contract":             (6,   "years", "Limitation Act 1980, s.5"),
            "Specialty / deed":            (12,  "years", "Limitation Act 1980, s.8"),
            "Tort (general)":              (6,   "years", "Limitation Act 1980, s.2"),
            "Personal injury":             (3,   "years", "Limitation Act 1980, s.11"),
            "Latent damage (negligence)":  (6,   "years", "Limitation Act 1980, s.14A (6yr primary / 3yr secondary from knowledge)"),
            "Fraud / deliberate concealment": (6,"years", "Limitation Act 1980, s.32 — runs from discovery"),
            "Recovery of land":            (12,  "years", "Limitation Act 1980, s.15"),
            "Enforcement of judgment":     (6,   "years", "Limitation Act 1980, s.24"),
        },
        "Scotland": {
            "Simple contract":             (5,   "years", "Prescription and Limitation (Scotland) Act 1973, s.6"),
            "Specialty / deed":            (20,  "years", "Long negative prescription — 20 years"),
            "Tort (general)":              (5,   "years", "Prescription and Limitation (Scotland) Act 1973"),
            "Personal injury":             (3,   "years", "Prescription and Limitation (Scotland) Act 1973, s.17"),
            "Latent damage (negligence)":  (5,   "years", "Prescription Act 1973 — 5 years from knowledge"),
            "Fraud / deliberate concealment": (5,"years", "Runs from discovery"),
            "Recovery of land":            (20,  "years", "Long negative prescription"),
            "Enforcement of judgment":     (20,  "years", "Long negative prescription"),
        },
        "Rwanda": {
            "Simple contract":             (5,   "years", "Rwandan Civil Code — 5 years general"),
            "Specialty / deed":            (5,   "years", "Rwandan Civil Code"),
            "Tort (general)":              (3,   "years", "Rwandan Civil Code — 3 years"),
            "Personal injury":             (3,   "years", "Rwandan Civil Code"),
            "Latent damage (negligence)":  (3,   "years", "Rwandan Civil Code"),
            "Fraud / deliberate concealment": (3,"years", "Rwandan Civil Code — from discovery"),
            "Recovery of land":            (10,  "years", "Rwandan land law"),
            "Enforcement of judgment":     (10,  "years", "Rwandan Civil Code"),
        },
    }

    lp_key = lp_jurisdiction if lp_jurisdiction in _LP else "England & Wales"
    lp_data = _LP[lp_key].get(cause_of_action, (6, "years", "Check applicable statute"))
    lp_years, _, lp_authority = lp_data

    # Suspension adjustments
    st.markdown("**Suspension / Extension Factors (optional)**")
    s1, s2 = st.columns(2)
    minority_years  = s1.number_input("Claimant was minor for (years after accrual)", min_value=0, max_value=18, value=0, step=1, key="lp_min")
    extension_years = s2.number_input("Other extension (years)", min_value=0, value=0, step=1, key="lp_ext",
                                       help="e.g. for disability, fraud discovery delay")

    effective_start = accrual_date + timedelta(days=365 * minority_years)
    expiry_date     = effective_start + timedelta(days=365 * (lp_years + extension_years))
    today           = date.today()
    days_left       = (expiry_date - today).days

    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.metric("Accrual Date",  accrual_date.strftime("%d %b %Y"))
    m2.metric("Expiry Date",   expiry_date.strftime("%d %b %Y"))
    if days_left < 0:
        m3.metric("Status", "EXPIRED", delta=f"{abs(days_left)} days ago", delta_color="inverse")
    elif days_left <= 90:
        m3.metric("Days Remaining", days_left, delta="URGENT", delta_color="inverse")
    else:
        m3.metric("Days Remaining", days_left)

    st.info(f"ℹ️ **Period:** {lp_years} years — {lp_authority}")
    if minority_years or extension_years:
        st.info(f"ℹ️ Extensions applied: {minority_years}yr minority + {extension_years}yr other = {minority_years + extension_years}yr total extension")
    if days_left <= 30:
        st.error("🚨 URGENT: Limitation expires within 30 days — issue proceedings immediately.")
    elif days_left <= 90:
        st.warning("⚠️ Limitation expires within 90 days — prepare proceedings now.")

    export_lp = (
        f"Limitation Period Calculation\n"
        f"Cause of Action: {cause_of_action}\nJurisdiction: {lp_jurisdiction}\n"
        f"Accrual Date: {accrual_date}\nLimitation Period: {lp_years} years\n"
        f"Authority: {lp_authority}\nExpiry: {expiry_date}\nDays remaining: {days_left}\n"
    )
    st.download_button("📥 Export (.txt)", export_lp, "limitation.txt", "text/plain", key="lp_exp")

st.markdown("<br>", unsafe_allow_html=True)
group_header("Financial Calculators")
fin1, fin2 = st.tabs(["💰 Interest Calculator", "⚖️ Damages Calculator"])

# ── 3. Interest Calculator ────────────────────────────────────────
with fin1:
    st.markdown("Calculate pre-judgment and post-judgment interest for litigation and debt recovery.")
    c1, c2, c3 = st.columns(3)
    principal   = c1.number_input("Principal Amount (£)", min_value=0.0, value=10000.0, step=100.0, key="ic_princ")
    annual_rate = c2.number_input("Annual Interest Rate (%)", min_value=0.0, value=8.0, step=0.25, key="ic_rate",
                                   help="UK Judgments Act 1838 rate = 8%. Current Bank of England base rate varies.")
    interest_type = c3.selectbox("Interest Type", ["Simple", "Compound"], key="ic_type")

    c4, c5 = st.columns(2)
    start_date  = c4.date_input("Start Date", value=date.today() - timedelta(days=365), key="ic_sd")
    end_date    = c5.date_input("End Date",   value=date.today(), key="ic_ed")

    if end_date > start_date and principal > 0:
        days_count = (end_date - start_date).days
        daily_rate = annual_rate / 100 / 365

        if interest_type == "Simple":
            interest = principal * daily_rate * days_count
        else:
            interest = principal * ((1 + annual_rate / 100) ** (days_count / 365) - 1)

        total = principal + interest

        st.divider()
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Principal",    f"£{principal:,.2f}")
        m2.metric("Interest",     f"£{interest:,.2f}")
        m3.metric("Total",        f"£{total:,.2f}")
        m4.metric("Days",         f"{days_count} days")

        st.info(f"ℹ️ {interest_type} interest at {annual_rate}% p.a. over {days_count} days")

        export_ic = (
            f"Interest Calculation\n"
            f"Principal: £{principal:,.2f}\nRate: {annual_rate}% p.a. ({interest_type})\n"
            f"Period: {start_date} to {end_date} ({days_count} days)\n"
            f"Interest: £{interest:,.2f}\nTotal (principal + interest): £{total:,.2f}"
        )
        st.download_button("📥 Export (.txt)", export_ic, "interest_calc.txt", "text/plain", key="ic_exp")
    else:
        st.info("Enter a principal amount and valid date range to calculate interest.")

# ── 4. Damages Calculator ─────────────────────────────────────────
with fin2:
    st.markdown("Build a schedule of loss by entering each head of damage.")
    st.markdown("**Heads of Loss**")

    if "damages_items" not in st.session_state:
        st.session_state.damages_items = []

    with st.form("add_damage", clear_on_submit=True):
        d1, d2, d3 = st.columns(3)
        d_head  = d1.selectbox("Head of Loss", [
            "General damages (pain & suffering)", "Loss of earnings (past)",
            "Loss of earnings (future)", "Medical expenses", "Property damage",
            "Loss of profit", "Wasted expenditure", "Consequential loss",
            "Repair costs", "Diminution in value", "Other",
        ], key="d_head")
        d_amount = d2.number_input("Amount (£)", min_value=0.0, value=0.0, step=100.0, key="d_amount")
        d_notes  = d3.text_input("Notes", placeholder="Supporting details", key="d_notes")
        if st.form_submit_button("＋ Add Item"):
            if d_amount > 0:
                st.session_state.damages_items.append({"head": d_head, "amount": d_amount, "notes": d_notes})

    if st.session_state.damages_items:
        c1, c2 = st.columns(2)
        contrib_pct = c1.number_input("Contributory Negligence Deduction (%)", min_value=0.0, max_value=100.0, value=0.0, step=5.0, key="d_contrib")
        discount_pct = c2.number_input("Ogden / Other Discount (%)", min_value=0.0, max_value=50.0, value=0.0, step=2.5, key="d_disc")

        total_gross = sum(i["amount"] for i in st.session_state.damages_items)
        contrib_deduct = total_gross * contrib_pct / 100
        after_contrib  = total_gross - contrib_deduct
        disc_deduct    = after_contrib * discount_pct / 100
        net_damages    = after_contrib - disc_deduct

        st.divider()
        section("📋 Schedule of Loss")
        for i, item in enumerate(st.session_state.damages_items):
            del_col, card_col = st.columns([0.08, 0.92])
            with card_col:
                notes_html = f'<span style="font-size:.78rem;color:#64748b">{item["notes"]}</span>' if item.get("notes") else ""
                st.markdown(
                    f'<div style="background:#f8fafc;border-radius:8px;padding:.6rem 1rem;'
                    f'margin-bottom:.3rem;display:flex;align-items:center;gap:1rem;flex-wrap:wrap;'
                    f'border-left:3px solid #c9a84c">'
                    f'<span style="flex:1;font-size:.85rem;color:#1a2744;font-weight:500">{item["head"]}</span>'
                    f'{notes_html}'
                    f'<span style="font-weight:700;color:#1a2744;font-size:.9rem;flex-shrink:0">£{item["amount"]:,.2f}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            with del_col:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🗑️", key=f"del_d_{i}"):
                    st.session_state.damages_items.pop(i)
                    st.rerun()

        st.divider()
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Gross Damages",          f"£{total_gross:,.2f}")
        m2.metric(f"Contributory ({contrib_pct}%)", f"− £{contrib_deduct:,.2f}")
        m3.metric(f"Discount ({discount_pct}%)",    f"− £{disc_deduct:,.2f}")
        m4.metric("**NET DAMAGES**",        f"£{net_damages:,.2f}")

        lines = ["Schedule of Loss\n" + "="*40]
        for item in st.session_state.damages_items:
            lines.append(f"{item['head']}: £{item['amount']:,.2f}  {item['notes']}")
        lines += [
            f"\nGross damages: £{total_gross:,.2f}",
            f"Contributory negligence ({contrib_pct}%): − £{contrib_deduct:,.2f}",
            f"Discount ({discount_pct}%): − £{disc_deduct:,.2f}",
            f"NET DAMAGES: £{net_damages:,.2f}",
        ]
        st.download_button("📥 Export Schedule (.txt)", "\n".join(lines),
                           "schedule_of_loss.txt", "text/plain", key="d_exp")
        if st.button("🗑️ Clear All Items", key="d_clear"):
            st.session_state.damages_items = []
            st.rerun()
    else:
        st.markdown('<div class="empty-list">Add heads of loss above to build your schedule.</div>', unsafe_allow_html=True)
