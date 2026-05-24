import streamlit as st
from utils.shared.sidebar import setup_page
from utils.shared.styles import slim_header, disclaimer, confidentiality_notice, section, risk_badge
from utils.shared.document_input import document_input_ui
from utils.shared.export_utils import download_json

from utils.auth import require_lawyer
api_key = setup_page()
require_lawyer()
slim_header("🏢", "Due Diligence Review", "Identify red flags and key risks across transaction documents")
disclaimer()
confidentiality_notice()

section("📎 Document Input")
text = document_input_ui("dd", paste_placeholder="Paste due diligence document, SPA, or disclosure letter here…")

st.markdown("<br>", unsafe_allow_html=True)
c1, c2, c3 = st.columns(3)
matter_type = c1.selectbox("Matter Type", [
    "M&A / Acquisition", "Joint venture", "Investment / Fundraising",
    "Real estate transaction", "Banking / Finance", "Commercial agreement", "Other",
])
client_perspective = c2.selectbox("Client Perspective", [
    "Buyer / Investor", "Seller / Target", "Lender", "Borrower", "Neutral review",
])
key_concerns = c3.text_input("Key Concerns", placeholder="e.g. IP ownership, regulatory exposure, pending litigation")

submit = st.button("🏢 Run Due Diligence Review", type="primary", disabled=not api_key)

if submit:
    if not text:
        st.warning("⚠️ Upload a document or paste text first.")
    else:
        from utils.due_diligence import DueDiligenceReview
        with st.spinner("Reviewing with Claude Opus 4.7…"):
            try:
                result = DueDiligenceReview(api_key).review(text, matter_type, client_perspective, key_concerns)
                st.session_state.dd_result = result
                st.success("✅ Review complete!")
            except Exception as exc:
                st.error(f"Review failed: {exc}")

if st.session_state.get("dd_result"):
    result = st.session_state.dd_result
    red_flags = result.get("red_flags", [])
    mat = result.get("matters_for_attention", [])

    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.markdown(f'<div class="metric-card"><div class="val" style="color:#dc2626">{len(red_flags)}</div><div class="lbl">Red Flags</div></div>', unsafe_allow_html=True)
    m2.markdown(f'<div class="metric-card"><div class="val" style="color:#d97706">{len(mat)}</div><div class="lbl">Matters for Attention</div></div>', unsafe_allow_html=True)
    m3.markdown(f'<div class="metric-card"><div class="val">{result.get("overall_risk","—")}</div><div class="lbl">Overall Risk</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"**Executive Summary:** {result.get('executive_summary','')}")

    if red_flags:
        st.markdown("<br>", unsafe_allow_html=True)
        section(f"🚨 Red Flags ({len(red_flags)})")
        SEV_CFG = {
            "critical": ("#dc2626", "#fef2f2", "🔴"),
            "high":     ("#ea580c", "#fff7ed", "🟠"),
            "medium":   ("#d97706", "#fffbeb", "🟡"),
            "low":      ("#059669", "#ecfdf5", "🟢"),
        }
        for rf in red_flags:
            sev = (rf.get("severity") or "medium").lower()
            fg, bg, icon = SEV_CFG.get(sev, ("#6b7280", "#f1f5f9", "⚪"))
            st.markdown(
                f"""<div style="background:{bg};border-radius:10px;padding:0.9rem 1rem;
                                margin-bottom:0.5rem;border-left:4px solid {fg}">
                  <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.4rem">
                    <span>{icon}</span>
                    <span style="font-size:0.72rem;font-weight:700;color:{fg};text-transform:uppercase;
                                 letter-spacing:0.04em">{rf.get('category','')}</span>
                    <span style="margin-left:auto">{risk_badge(sev)}</span>
                  </div>
                  <p style="margin:0;font-weight:600;color:#1a1a2e;font-size:0.88rem">{rf.get('issue','')}</p>
                  {'<p style="margin:0.35rem 0 0;font-size:0.82rem;color:#374151"><b>Implication:</b> '+rf.get('implication','')+'</p>' if rf.get('implication') else ''}
                  {'<p style="margin:0.25rem 0 0;font-size:0.82rem;color:#1a2744"><b>Recommendation:</b> '+rf.get('recommendation','')+'</p>' if rf.get('recommendation') else ''}
                </div>""",
                unsafe_allow_html=True,
            )

    if mat:
        st.markdown("<br>", unsafe_allow_html=True)
        section(f"⚠️ Matters for Attention ({len(mat)})")
        for m in mat:
            st.warning(m)

    for key, label in [("key_strengths", "✅ Key Strengths"), ("recommendations", "💡 Recommendations")]:
        items = result.get(key, [])
        if items:
            st.markdown("<br>", unsafe_allow_html=True)
            section(label)
            for item in items:
                st.markdown(f"- {item}")

    st.markdown("<br>", unsafe_allow_html=True)
    c1, _, c3 = st.columns(3)
    with c1:
        download_json("📥 Download DD Report (.json)", result, "due_diligence_report.json", key="dd_dl")
    with c3:
        if st.button("🔄 Reset", use_container_width=True, key="dd_reset"):
            st.session_state.pop("dd_result", None)
            st.rerun()
