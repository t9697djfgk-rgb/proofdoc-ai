import streamlit as st
from utils.shared.styles import inject_css, page_header, disclaimer, confidentiality_notice, privilege_warning, section, risk_badge
from utils.shared.sidebar import render_sidebar
from utils.shared.document_input import document_input_ui
from utils.shared.export_utils import download_json

st.set_page_config(page_title="Due Diligence Review · ProofDoc AI", page_icon="🔎", layout="wide")
inject_css()
api_key = render_sidebar("Due Diligence Review")
page_header("🔎", "Due Diligence Review", "Red-flag report across multiple legal and business documents")
disclaimer()
confidentiality_notice()
privilege_warning()

section("📎 Document Input")
st.caption("Upload or paste the combined text of all documents to review.")
text = document_input_ui("dd", paste_placeholder="Paste combined document text here…")

st.markdown("<br>", unsafe_allow_html=True)
c1, c2 = st.columns(2)
matter_type = c1.selectbox("Matter Type", [
    "M&A", "Investment", "Real estate", "Employment",
    "Compliance", "Litigation", "Anti-corruption", "General",
])
client_perspective = c2.text_input("Buyer / Client Perspective", placeholder="e.g. Acquiring company in M&A transaction")
key_concerns = st.text_area("Key Concerns", height=80,
                              placeholder="e.g. Change of control provisions, pending litigation, IP ownership…")

submit = st.button("🔎 Run Due Diligence Review", type="primary", disabled=not api_key)

if submit:
    if not text:
        st.warning("⚠️ Upload documents or paste text first.")
    else:
        from utils.due_diligence import DueDiligenceReview
        with st.spinner("Reviewing with Claude Opus 4.7…"):
            try:
                result = DueDiligenceReview(api_key).review(text, matter_type, client_perspective, key_concerns)
                st.session_state.dd_result = result
                st.success("✅ Due diligence review complete!")
            except Exception as exc:
                st.error(f"Review failed: {exc}")

if st.session_state.get("dd_result"):
    result = st.session_state.dd_result
    red_flags = result.get("red_flags", [])
    inventory = result.get("document_inventory", [])

    st.divider()
    section("📋 Executive Summary")
    st.markdown(result.get("executive_summary", ""))

    critical = sum(1 for r in red_flags if r.get("risk_level") in ("critical","high"))
    m1, m2, m3 = st.columns(3)
    m1.markdown(f'<div class="metric-card"><div class="val">{len(red_flags)}</div><div class="lbl">Red Flags</div></div>', unsafe_allow_html=True)
    m2.markdown(f'<div class="metric-card"><div class="val" style="color:#dc2626">{critical}</div><div class="lbl">High/Critical</div></div>', unsafe_allow_html=True)
    m3.markdown(f'<div class="metric-card"><div class="val">{len(inventory)}</div><div class="lbl">Documents Reviewed</div></div>', unsafe_allow_html=True)

    tabs = st.tabs(["🚩 Red Flags", "📂 Document Inventory", "⚖️ Obligations & Deadlines", "❓ Follow-Up Questions"])

    with tabs[0]:
        if red_flags:
            hdr = st.columns([2, 1.5, 1.5, 1, 2.5, 2])
            for col, lbl in zip(hdr, ["Issue", "Document", "Reference", "Level", "Why It Matters", "Action"]):
                col.markdown(f"**{lbl}**")
            st.divider()
            for f in red_flags:
                row = st.columns([2, 1.5, 1.5, 1, 2.5, 2])
                row[0].markdown(f.get("issue",""))
                row[1].markdown(f.get("document",""))
                row[2].markdown(f.get("section_or_reference",""))
                row[3].markdown(risk_badge(f.get("risk_level","medium")), unsafe_allow_html=True)
                row[4].markdown(f.get("why_it_matters",""))
                row[5].markdown(f.get("recommended_action",""))
                st.markdown('<hr style="margin:0.25rem 0;border-color:#f1f5f9">', unsafe_allow_html=True)
        else:
            st.info("No red flags identified.")

    with tabs[1]:
        for doc in inventory:
            st.markdown(f"**{doc.get('document_name','')}** ({doc.get('document_type','')}) — {doc.get('brief_summary','')}")

    with tabs[2]:
        obligations = result.get("key_obligations", [])
        deadlines = result.get("key_deadlines", [])
        missing = result.get("missing_documents", [])
        if obligations:
            st.markdown("**Key Obligations:**")
            for o in obligations: st.markdown(f"- {o}")
        if deadlines:
            st.markdown("**Key Deadlines:**")
            for d in deadlines: st.markdown(f"- {d}")
        if missing:
            st.markdown("**Missing Documents:**")
            for m in missing: st.warning(m)

    with tabs[3]:
        fqs = result.get("follow_up_questions", [])
        if fqs:
            for q in fqs: st.markdown(f"- {q}")
        else:
            st.caption("No follow-up questions identified.")

    st.markdown("<br>", unsafe_allow_html=True)
    c1, _, c3 = st.columns(3)
    with c1:
        download_json("📥 Download DD Report (.json)", result, "due_diligence_report.json", key="dd_dl")
    with c3:
        if st.button("🔄 Reset", use_container_width=True, key="dd_reset"):
            st.session_state.pop("dd_result", None)
            st.rerun()
