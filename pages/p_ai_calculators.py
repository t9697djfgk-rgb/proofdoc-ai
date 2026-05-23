import streamlit as st
from utils.shared.sidebar import setup_page
from utils.shared.styles import slim_header, group_header, placeholder_feature

setup_page()
slim_header("🧮", "Calculators", "Court deadlines, limitation periods, interest, and damages calculators")
st.markdown(
    '<div class="disclaimer-box">ℹ️ <strong>Disclaimer:</strong> Calculators provide estimates only. '
    "Always verify deadlines and limitation periods with a qualified lawyer and official court rules.</div>",
    unsafe_allow_html=True,
)

group_header("Deadlines & Limitation Periods")
c1, c2 = st.columns(2)
with c1:
    placeholder_feature(
        "📅", "Court Deadline Calculator",
        "Calculate procedural deadlines based on court rules, event dates, and jurisdiction.",
        ["Enter trigger date (filing, service, judgment)", "Select jurisdiction and court type",
         "Calculator applies correct rule for working vs. calendar days",
         "See all upcoming deadlines on a timeline"],
        ["Deadline calendar with all key dates", "Working-day adjusted dates",
         "Exportable deadline schedule", "Matter calendar integration"],
    )
with c2:
    placeholder_feature(
        "⏳", "Limitation Period Calculator",
        "Calculate when a limitation period expires based on cause of action and jurisdiction.",
        ["Select cause of action (contract, tort, fraud, etc.)", "Enter accrual date",
         "Select jurisdiction", "Account for suspension events (minority, disability)"],
        ["Limitation expiry date", "Relevant statutory provision",
         "Warning if expiry is within 30/60/90 days", "Summary report"],
    )

st.markdown("<br>", unsafe_allow_html=True)
group_header("Financial Calculators")
c3, c4 = st.columns(2)
with c3:
    placeholder_feature(
        "💰", "Interest Calculator",
        "Calculate pre-judgment and post-judgment interest for litigation and debt recovery.",
        ["Enter principal amount and applicable rate",
         "Select interest type (simple, compound, statutory rate)",
         "Enter start and end dates", "Account for partial payments"],
        ["Interest calculation breakdown", "Day-by-day accrual table",
         "Total sum (principal + interest)", "Export for pleadings or settlement"],
    )
with c4:
    placeholder_feature(
        "⚖️", "Damages Calculator",
        "Estimate damages across common claim types with structured heads of loss.",
        ["Select claim type (personal injury, contract, negligence)",
         "Enter each head of loss with supporting details",
         "Apply deductions (contributory negligence, mitigation)",
         "Generate schedule of loss"],
        ["Schedule of loss (Word/PDF)", "Summary total per head of loss",
         "Deductions applied clearly", "Schedule ready for pleadings or mediation"],
    )
