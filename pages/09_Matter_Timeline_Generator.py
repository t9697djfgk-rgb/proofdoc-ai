import streamlit as st
from utils.shared.styles import inject_css, page_header, disclaimer, section, risk_badge
from utils.shared.sidebar import render_sidebar
from utils.shared.document_input import document_input_ui
from utils.shared.export_utils import download_json, download_txt

st.set_page_config(page_title="Matter Timeline · ProofDoc AI", page_icon="📅", layout="wide")
inject_css()
api_key = render_sidebar("Matter Timeline Generator")
page_header("📅", "Matter Timeline Generator", "Extract chronological events from legal documents")
disclaimer()

section("📎 Document Input")
text = document_input_ui("tl", paste_placeholder="Paste case documents, correspondence, or witness statements here…")

st.markdown("<br>", unsafe_allow_html=True)
c1, c2 = st.columns(2)
matter_type = c1.selectbox("Matter Type", [
    "Litigation", "Arbitration", "Criminal case", "Contract dispute",
    "Employment dispute", "Investigation", "Compliance matter", "Other",
])
date_format = c2.selectbox("Date Format Preference", ["DD Month YYYY", "MM/DD/YYYY", "YYYY-MM-DD", "As found in document"])

submit = st.button("📅 Generate Timeline", type="primary", disabled=not api_key)

if submit:
    if not text:
        st.warning("⚠️ Upload a document or paste text first.")
    else:
        from utils.timeline_generator import TimelineGenerator
        with st.spinner("Extracting timeline with Claude Opus 4.7…"):
            try:
                result = TimelineGenerator(api_key).generate(text, matter_type, date_format)
                st.session_state.tl_result = result
                st.success("✅ Timeline generated!")
            except Exception as exc:
                st.error(f"Generation failed: {exc}")

if st.session_state.get("tl_result"):
    result = st.session_state.tl_result
    timeline = result.get("timeline", [])
    undated = result.get("undated_events", [])
    conflicts = result.get("conflicting_dates", [])
    questions = result.get("missing_questions", [])

    st.divider()
    m1, m2, m3 = st.columns(3)
    m1.markdown(f'<div class="metric-card"><div class="val">{len(timeline)}</div><div class="lbl">Dated Events</div></div>', unsafe_allow_html=True)
    m2.markdown(f'<div class="metric-card"><div class="val">{len(undated)}</div><div class="lbl">Undated Events</div></div>', unsafe_allow_html=True)
    m3.markdown(f'<div class="metric-card"><div class="val" style="color:#d97706">{len(conflicts)}</div><div class="lbl">Date Conflicts</div></div>', unsafe_allow_html=True)

    if timeline:
        st.markdown("<br>", unsafe_allow_html=True)
        section(f"🗓️ Chronological Timeline ({len(timeline)} events)")
        hdr = st.columns([1.5, 3, 1.5, 2, 2.5, 1])
        for col, lbl in zip(hdr, ["Date", "Event", "Source", "People/Entities", "Legal Relevance", "Confidence"]):
            col.markdown(f"**{lbl}**")
        st.divider()
        for ev in timeline:
            row = st.columns([1.5, 3, 1.5, 2, 2.5, 1])
            row[0].markdown(f"**{ev.get('date','')}**")
            row[1].markdown(ev.get("event",""))
            row[2].markdown(ev.get("source_reference",""))
            row[3].markdown(", ".join(ev.get("people_or_entities",[])))
            row[4].markdown(ev.get("legal_relevance",""))
            conf = ev.get("confidence","medium")
            conf_cls = {"high":"risk-low","medium":"risk-medium","low":"risk-high"}.get(conf,"risk-medium")
            row[5].markdown(f'<span class="{conf_cls}">{conf}</span>', unsafe_allow_html=True)
            st.markdown('<hr style="margin:0.25rem 0;border-color:#f1f5f9">', unsafe_allow_html=True)

    if undated:
        st.markdown("<br>", unsafe_allow_html=True)
        section("❓ Undated Events")
        for u in undated: st.markdown(f"- {u}")

    if conflicts:
        st.markdown("<br>", unsafe_allow_html=True)
        section("⚠️ Conflicting Dates")
        for c in conflicts: st.warning(c)

    if questions:
        st.markdown("<br>", unsafe_allow_html=True)
        section("❓ Missing Chronology Questions")
        for q in questions: st.markdown(f"- {q}")

    # Export as text timeline
    tl_text = "\n".join(
        f"{ev.get('date','?')} — {ev.get('event','')} [{ev.get('source_reference','')}]"
        for ev in timeline
    )
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, _, c4 = st.columns(4)
    with c1:
        download_txt("📥 Export Timeline (.txt)", tl_text, "timeline.txt", key="tl_txt")
    with c2:
        download_json("📊 Export Full Data (.json)", result, "timeline_report.json", key="tl_json")
    with c4:
        if st.button("🔄 Reset", use_container_width=True, key="tl_reset"):
            st.session_state.pop("tl_result", None)
            st.rerun()
