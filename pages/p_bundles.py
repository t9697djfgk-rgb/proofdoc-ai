import streamlit as st
from utils.shared.sidebar import setup_page
from utils.shared.styles import slim_header, inject_css, section
from utils.auth import require_lawyer
import utils.database as db
from datetime import date

setup_page()
require_lawyer()
inject_css()
slim_header("📦", "Trial Bundles", "Build court bundles, exhibit lists, and witness schedules")

# ── Session state ─────────────────────────────────────────────────
for key, default in [
    ("bun_matter_id",  None),
    ("bun_sections",   {
        "A – Core Documents":  [],
        "B – Witness Statements": [],
        "C – Exhibits":        [],
        "D – Correspondence":  [],
        "E – Expert Reports":  [],
        "F – Authorities":     [],
    }),
    ("bun_exhibits",  []),
    ("bun_witnesses", []),
]:
    if key not in st.session_state:
        st.session_state[key] = default

tab_bundle, tab_exhibits, tab_witnesses = st.tabs([
    "📦 Bundle Builder", "📋 Exhibit List", "🧑‍⚖️ Witness List",
])

# ═══════════════════════════════════════════════════════════════════
# TAB 1 – BUNDLE BUILDER
# ═══════════════════════════════════════════════════════════════════
with tab_bundle:
    matters = db.list_matters(status="Active")
    if not matters:
        st.info("No active matters found. Create a matter first.")
        st.stop()

    matter_opts = {f"{m.get('ref','')} – {m['title'][:45]}": m["id"] for m in matters}
    sel_label = st.selectbox("Select matter for this bundle", list(matter_opts.keys()),
                             key="bun_matter_sel")
    sel_id = matter_opts[sel_label]
    if sel_id != st.session_state.bun_matter_id:
        st.session_state.bun_matter_id = sel_id
        for sec in st.session_state.bun_sections:
            st.session_state.bun_sections[sec] = []

    docs = db.list_documents(matter_id=sel_id)
    doc_map = {d["name"]: d["id"] for d in docs}

    if not docs:
        st.info("No documents in this matter yet. Upload documents via the Document Library.")
    else:
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        section("📂 Assign Documents to Bundle Sections")
        st.caption("Each document can appear in multiple sections. Click Save after each section.")

        for sec_name in st.session_state.bun_sections:
            current = st.session_state.bun_sections[sec_name]
            # Convert stored IDs back to names for display
            current_names = [n for n, i in doc_map.items() if i in current]
            chosen = st.multiselect(
                sec_name, list(doc_map.keys()),
                default=current_names,
                key=f"sec_{sec_name}",
            )
            st.session_state.bun_sections[sec_name] = [doc_map[n] for n in chosen]

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        section("📑 Bundle Index")

        total_pages = 1
        any_docs = False
        for sec_name, doc_ids in st.session_state.bun_sections.items():
            if not doc_ids:
                continue
            any_docs = True
            st.markdown(
                f"<div style='background:#1a2744;color:#fff;padding:0.45rem 0.85rem;"
                f"border-radius:8px;font-weight:600;font-size:0.85rem;margin:0.6rem 0 0.3rem'>"
                f"{sec_name}</div>",
                unsafe_allow_html=True,
            )
            sec_docs = [d for d in docs if d["id"] in doc_ids]
            for i, d in enumerate(sec_docs, 1):
                pg_ref = f"p.{total_pages}"
                st.markdown(
                    f"<div style='display:flex;padding:0.35rem 0.85rem;border-bottom:"
                    f"1px solid #f0ede6;font-size:0.84rem'>"
                    f"<span style='flex:1;color:#374151'>{i}. {d['name']}</span>"
                    f"<span style='color:#9ca3af;margin-left:1rem'>{pg_ref}</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
                total_pages += max(1, round((d.get("file_size") or 100000) / 3000))

        if any_docs:
            index_text = f"TRIAL BUNDLE INDEX\nMatter: {sel_label}\nPrepared: {date.today()}\n\n"
            page = 1
            for sec, ids in st.session_state.bun_sections.items():
                if not ids:
                    continue
                index_text += f"\n{sec}\n{'─'*40}\n"
                for d in [x for x in docs if x["id"] in ids]:
                    index_text += f"  {d['name']:<50} p.{page}\n"
                    page += max(1, round((d.get("file_size") or 100000) / 3000))
            st.download_button(
                "⬇️ Download Bundle Index (.txt)", data=index_text,
                file_name=f"bundle_index_{date.today()}.txt", mime="text/plain",
                type="primary", key="dl_index",
            )
        else:
            st.caption("No documents assigned yet. Use the multiselects above to build your bundle.")

# ═══════════════════════════════════════════════════════════════════
# TAB 2 – EXHIBIT LIST
# ═══════════════════════════════════════════════════════════════════
with tab_exhibits:
    section("➕ Add Exhibit")
    with st.form("add_exhibit_form", clear_on_submit=True):
        e1, e2, e3 = st.columns(3)
        ex_ref  = e1.text_input("Exhibit Ref *", placeholder="EX-001")
        ex_desc = e2.text_input("Description *", placeholder="Contract dated 1 Jan 2024")
        ex_date = e3.text_input("Date (YYYY-MM-DD)", placeholder="2024-01-01")
        e4, e5 = st.columns(2)
        ex_party  = e4.text_input("Party introducing", placeholder="Claimant / Respondent")
        ex_status = e5.selectbox("Status", ["Agreed", "Disputed", "Not yet served", "Pending"])
        ex_bundle = st.text_input("Bundle page ref", placeholder="B/45")
        if st.form_submit_button("＋ Add Exhibit", type="primary"):
            if ex_ref.strip() and ex_desc.strip():
                st.session_state.bun_exhibits.append({
                    "ref": ex_ref.strip(), "description": ex_desc.strip(),
                    "date": ex_date.strip(), "party": ex_party.strip(),
                    "status": ex_status, "bundle_ref": ex_bundle.strip(),
                })
                st.rerun()
            else:
                st.warning("Exhibit reference and description are required.")

    exhibits = st.session_state.bun_exhibits
    if exhibits:
        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
        section(f"📋 Exhibit List ({len(exhibits)} exhibits)")

        STATUS_COLOR = {
            "Agreed":          ("#16a34a", "#dcfce7"),
            "Disputed":        ("#dc2626", "#fef2f2"),
            "Not yet served":  ("#d97706", "#fffbeb"),
            "Pending":         ("#6b7280", "#f1f5f9"),
        }
        h = st.columns([1, 3.5, 1.5, 1.5, 1.5, 0.5])
        for col, lbl in zip(h, ["Ref", "Description", "Date", "Party", "Status", ""]):
            col.markdown(f"**{lbl}**")
        st.divider()
        for i, ex in enumerate(exhibits):
            fg, bg = STATUS_COLOR.get(ex["status"], ("#6b7280", "#f1f5f9"))
            r = st.columns([1, 3.5, 1.5, 1.5, 1.5, 0.5])
            r[0].markdown(f"**{ex['ref']}**")
            r[1].text(ex["description"][:55])
            r[2].text(ex.get("date") or "—")
            r[3].text(ex.get("party") or "—")
            r[4].markdown(
                f"<span style='background:{bg};color:{fg};font-size:0.72rem;font-weight:600;"
                f"padding:0.2rem 0.5rem;border-radius:20px'>{ex['status']}</span>",
                unsafe_allow_html=True,
            )
            if r[5].button("🗑️", key=f"del_ex_{i}"):
                st.session_state.bun_exhibits.pop(i)
                st.rerun()

        # Export
        csv = "Ref,Description,Date,Party introducing,Status,Bundle Ref\n"
        csv += "\n".join(
            f"{e['ref']},{e['description']},{e.get('date','')},{e.get('party','')},{e['status']},{e.get('bundle_ref','')}"
            for e in exhibits
        )
        st.download_button(
            "⬇️ Download Exhibit List (.csv)", data=csv,
            file_name=f"exhibit_list_{date.today()}.csv", mime="text/csv",
            key="dl_exhibits",
        )
    else:
        st.markdown(
            '<div style="background:#fff;border-radius:10px;padding:1.5rem;text-align:center;'
            'border:1px dashed #d1cfc8;color:#9ca3af;font-size:0.88rem;margin-top:1rem">'
            '📋 No exhibits yet. Use the form above to add exhibits.</div>',
            unsafe_allow_html=True,
        )

# ═══════════════════════════════════════════════════════════════════
# TAB 3 – WITNESS LIST
# ═══════════════════════════════════════════════════════════════════
with tab_witnesses:
    section("➕ Add Witness")
    with st.form("add_witness_form", clear_on_submit=True):
        w1, w2, w3 = st.columns(3)
        w_name  = w1.text_input("Full Name *", placeholder="John Smith")
        w_role  = w2.selectbox("Role", ["Claimant", "Respondent", "Expert", "Fact Witness", "Character Witness", "Other"])
        w_party = w3.text_input("Party", placeholder="Claimant / Respondent")
        w2b, w3b, w4b = st.columns(3)
        w_time  = w2b.text_input("Est. time in chief", placeholder="2 hours")
        w_cross = w3b.text_input("Est. cross-exam time", placeholder="1 hour")
        w_order = w4b.number_input("Trial order", min_value=1, step=1, value=len(st.session_state.bun_witnesses)+1)
        w_topics = st.text_area("Key topics / issues", height=60, placeholder="Separate topics with commas or new lines")
        if st.form_submit_button("＋ Add Witness", type="primary"):
            if w_name.strip():
                st.session_state.bun_witnesses.append({
                    "name": w_name.strip(), "role": w_role, "party": w_party.strip(),
                    "time_chief": w_time.strip(), "time_cross": w_cross.strip(),
                    "order": int(w_order), "topics": w_topics.strip(),
                })
                st.session_state.bun_witnesses.sort(key=lambda x: x["order"])
                st.rerun()
            else:
                st.warning("Witness name is required.")

    witnesses = st.session_state.bun_witnesses
    if witnesses:
        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
        section(f"🧑‍⚖️ Witness Schedule ({len(witnesses)} witnesses)")

        for w in witnesses:
            st.markdown(
                f"""
                <div style="background:#fff;border-radius:10px;padding:0.9rem 1rem;
                            margin-bottom:0.5rem;border:1px solid rgba(0,0,0,0.07);
                            border-left:4px solid #1a2744;box-shadow:0 1px 4px rgba(0,0,0,0.05)">
                  <div style="display:flex;align-items:center;gap:0.75rem;flex-wrap:wrap">
                    <span style="font-weight:700;color:#1a2744;font-size:0.95rem">
                      #{w['order']} — {w['name']}</span>
                    <span style="background:#e8f0fe;color:#1a2744;font-size:0.72rem;
                                 font-weight:600;padding:0.15rem 0.5rem;border-radius:20px">
                      {w['role']}</span>
                    {'<span style="color:#6b7280;font-size:0.8rem">'+w['party']+'</span>' if w['party'] else ''}
                  </div>
                  <div style="margin-top:0.4rem;display:flex;gap:1.5rem;flex-wrap:wrap;font-size:0.8rem;color:#6b7280">
                    {'<span>📍 In chief: '+w['time_chief']+'</span>' if w['time_chief'] else ''}
                    {'<span>⚔️ Cross: '+w['time_cross']+'</span>' if w['time_cross'] else ''}
                  </div>
                  {'<p style="margin:0.35rem 0 0;font-size:0.8rem;color:#374151">Topics: '+w['topics']+'</p>' if w['topics'] else ''}
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Export
        txt = f"WITNESS SCHEDULE\nPrepared: {date.today()}\n\n"
        txt += f"{'#':<4} {'Name':<30} {'Role':<20} {'Party':<20} {'In Chief':<15} {'Cross':<12}\n"
        txt += "─" * 100 + "\n"
        for w in witnesses:
            txt += (f"{w['order']:<4} {w['name']:<30} {w['role']:<20} "
                    f"{w.get('party',''):<20} {w.get('time_chief',''):<15} {w.get('time_cross',''):<12}\n")
            if w.get("topics"):
                txt += f"     Topics: {w['topics']}\n"
        st.download_button(
            "⬇️ Download Witness Schedule (.txt)", data=txt,
            file_name=f"witness_schedule_{date.today()}.txt", mime="text/plain",
            key="dl_witnesses",
        )

        if st.button("🗑️ Clear All Witnesses", key="clear_witnesses"):
            st.session_state.bun_witnesses = []
            st.rerun()
    else:
        st.markdown(
            '<div style="background:#fff;border-radius:10px;padding:1.5rem;text-align:center;'
            'border:1px dashed #d1cfc8;color:#9ca3af;font-size:0.88rem;margin-top:1rem">'
            '🧑‍⚖️ No witnesses yet. Use the form above to build your witness schedule.</div>',
            unsafe_allow_html=True,
        )
