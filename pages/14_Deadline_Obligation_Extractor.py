import streamlit as st
from utils.shared.styles import inject_css, page_header, disclaimer, section, risk_badge
from utils.shared.sidebar import render_sidebar
from utils.shared.document_input import document_input_ui
from utils.shared.export_utils import download_json, download_txt

st.set_page_config(page_title="Deadline Extractor · ProofDoc AI", page_icon="⏰", layout="wide")
inject_css()
api_key = render_sidebar("Deadline & Obligation Extractor")
page_header("⏰", "Deadline & Obligation Extractor", "Extract all obligations, deadlines, and compliance duties from legal documents")
disclaimer()

section("📎 Document Input")
text = document_input_ui("de", paste_placeholder="Paste your contract, court order, or regulation here…")

st.markdown("<br>", unsafe_allow_html=True)
c1, c2 = st.columns(2)
doc_type = c1.selectbox("Document Type", [
    "Contract", "Court order", "Regulation", "Policy",
    "Legal letter", "Settlement agreement", "Other",
])
party_perspective = c2.text_input("Party Perspective", placeholder="e.g. Service Provider, Buyer, Defendant")

submit = st.button("⏰ Extract Obligations & Deadlines", type="primary", disabled=not api_key)

if submit:
    if not text:
        st.warning("⚠️ Upload a document or paste text first.")
    else:
        from utils.deadline_extractor import DeadlineExtractor
        with st.spinner("Extracting with Claude Opus 4.7…"):
            try:
                result = DeadlineExtractor(api_key).extract(text, doc_type, party_perspective)
                st.session_state.de_result = result
                st.success("✅ Extraction complete!")
            except Exception as exc:
                st.error(f"Extraction failed: {exc}")

if st.session_state.get("de_result"):
    result = st.session_state.de_result
    obligations = result.get("obligations", [])
    deadlines = result.get("deadlines", [])
    unclear = result.get("unclear_deadlines", [])

    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.markdown(f'<div class="metric-card"><div class="val">{len(obligations)}</div><div class="lbl">Obligations</div></div>', unsafe_allow_html=True)
    m2.markdown(f'<div class="metric-card"><div class="val">{len(deadlines)}</div><div class="lbl">Deadlines</div></div>', unsafe_allow_html=True)
    m3.markdown(f'<div class="metric-card"><div class="val" style="color:#d97706">{len(unclear)}</div><div class="lbl">Unclear/Conditional</div></div>', unsafe_allow_html=True)

    if obligations:
        st.markdown("<br>", unsafe_allow_html=True)
        section(f"⚖️ Obligations ({len(obligations)})")
        hdr = st.columns([1.5, 3, 2, 1.5, 2, 1.5, 1])
        for col, lbl in zip(hdr, ["Responsible Party", "Obligation", "Trigger Event", "Deadline", "Consequence", "Source Clause", "Priority"]):
            col.markdown(f"**{lbl}**")
        st.divider()
        for ob in obligations:
            row = st.columns([1.5, 3, 2, 1.5, 2, 1.5, 1])
            row[0].markdown(ob.get("responsible_party",""))
            row[1].markdown(ob.get("obligation",""))
            row[2].markdown(ob.get("trigger_event",""))
            row[3].markdown(f"**{ob.get('deadline_or_date','')}**")
            row[4].markdown(ob.get("consequence",""))
            row[5].markdown(ob.get("source_clause",""))
            row[6].markdown(risk_badge(ob.get("priority","medium")), unsafe_allow_html=True)
            st.markdown('<hr style="margin:0.25rem 0;border-color:#f1f5f9">', unsafe_allow_html=True)

    if deadlines:
        st.markdown("<br>", unsafe_allow_html=True)
        section(f"📅 Deadlines ({len(deadlines)})")
        hdr2 = st.columns([2, 3, 2, 2, 1])
        for col, lbl in zip(hdr2, ["Date / Period", "Action Required", "Responsible Party", "Source Clause", "Priority"]):
            col.markdown(f"**{lbl}**")
        st.divider()
        for dl in deadlines:
            row = st.columns([2, 3, 2, 2, 1])
            row[0].markdown(f"**{dl.get('date_or_period','')}**")
            row[1].markdown(dl.get("action_required",""))
            row[2].markdown(dl.get("responsible_party",""))
            row[3].markdown(dl.get("source_clause",""))
            row[4].markdown(risk_badge(dl.get("priority","medium")), unsafe_allow_html=True)
            st.markdown('<hr style="margin:0.25rem 0;border-color:#f1f5f9">', unsafe_allow_html=True)

    if unclear:
        st.markdown("<br>", unsafe_allow_html=True)
        section("⚠️ Unclear / Conditional Deadlines")
        for u in unclear: st.warning(u)

    # Plain text export of deadline list
    dl_text = "\n".join(
        f"{dl.get('date_or_period','?')} — {dl.get('action_required','')} [{dl.get('responsible_party','')}]"
        for dl in deadlines
    )
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, _, c4 = st.columns(4)
    with c1:
        download_txt("📥 Export Deadlines (.txt)", dl_text, "deadlines.txt", key="de_txt")
    with c2:
        download_json("📊 Export Full Report (.json)", result, "obligations_report.json", key="de_json")
    with c4:
        if st.button("🔄 Reset", use_container_width=True, key="de_reset"):
            st.session_state.pop("de_result", None)
            st.rerun()
