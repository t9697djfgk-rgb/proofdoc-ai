import streamlit as st
from utils.shared.sidebar import setup_page
from utils.shared.styles import slim_header, inject_css, section
from utils.auth import require_lawyer
import utils.database as db
from datetime import date

setup_page()
require_lawyer()
inject_css()
slim_header("🛡️", "Compliance Tools", "AML/KYC, privilege, data protection, and conflict monitoring")

st.markdown(
    '<div class="notice-box">🔐 Compliance data is processed in memory only and never used for AI training.</div>',
    unsafe_allow_html=True,
)

# Session state
for key, default in [
    ("aml_checks",  {}),
    ("priv_log",    []),
    ("gdpr_checks", {}),
    ("waivers",     []),
]:
    if key not in st.session_state:
        st.session_state[key] = default

tab_aml, tab_privilege, tab_gdpr, tab_conflict = st.tabs([
    "🏦 AML / KYC", "🔒 Privilege Register", "🛡️ Data Protection", "⚖️ Conflict Monitor",
])

# ══════════════════════════════════════════════════════════════════
# TAB 1 – AML / KYC
# ══════════════════════════════════════════════════════════════════
with tab_aml:
    AML_CHECKLISTS = {
        "Individual (low risk)": [
            "Verify full legal name against government-issued ID",
            "Confirm date of birth",
            "Obtain and verify residential address (utility bill / bank statement)",
            "Screen against PEP (Politically Exposed Persons) list",
            "Screen against sanctions lists (UN, EU, OFAC)",
            "Confirm source of funds for matter",
            "Confirm source of wealth (if required by matter value)",
            "Record-keeping: store copies of ID documents",
            "Complete client risk assessment form",
        ],
        "Individual (high risk / PEP)": [
            "Verify full legal name against government-issued ID",
            "Confirm date of birth",
            "Obtain and verify residential address (utility bill / bank statement)",
            "Screen against PEP list — CONFIRMED PEP",
            "Screen against sanctions lists (UN, EU, OFAC)",
            "Obtain senior management approval to act",
            "Enhanced due diligence: confirm current public roles/positions",
            "Confirm source of funds in detail (bank statements, payslips)",
            "Confirm source of wealth with documentary evidence",
            "Set up enhanced ongoing monitoring",
            "Record-keeping: store all EDD documentation",
            "Annual review of client risk rating",
        ],
        "Company (domestic)": [
            "Obtain certificate of incorporation",
            "Obtain memorandum and articles of association",
            "Verify registered office address",
            "Identify all directors — verify each with ID",
            "Identify ultimate beneficial owners (25%+ ownership)",
            "Screen all directors and UBOs against PEP/sanctions lists",
            "Obtain confirmation of principal business activities",
            "Confirm source of funds for matter",
            "Check company filing history (accounts, confirmation statements)",
            "Record-keeping: store corporate documents",
        ],
        "Company (foreign / offshore)": [
            "Obtain equivalent of certificate of incorporation",
            "Verify legal standing in country of incorporation",
            "Obtain constitutional documents",
            "Identify all directors — verify each with ID",
            "Identify ultimate beneficial owners (25%+ ownership)",
            "Screen all principals against PEP/sanctions lists",
            "Obtain senior management approval to act",
            "Obtain independent legal opinion on beneficial ownership if required",
            "Confirm source of funds with documentary evidence",
            "Set up enhanced ongoing monitoring",
            "Annual review of client risk rating",
        ],
        "Charity / NGO": [
            "Obtain charity registration number",
            "Verify charity register entry",
            "Obtain list of trustees / directors",
            "Identify beneficial owners or controlling parties",
            "Screen trustees against PEP/sanctions lists",
            "Confirm charitable purposes and activities",
            "Confirm source of funds (donations, grants)",
            "Assess risk of misuse for terrorist financing",
            "Record-keeping: store registration and governance documents",
        ],
    }

    section("🏦 AML / KYC Checklist")
    c1, c2, c3 = st.columns(3)
    client_type  = c1.selectbox("Client Type", list(AML_CHECKLISTS.keys()), key="aml_type")
    client_name  = c2.text_input("Client Name", placeholder="For your records", key="aml_client")
    matter_ref   = c3.text_input("Matter Reference", placeholder="e.g. MAT-2026-0001", key="aml_ref")

    items   = AML_CHECKLISTS[client_type]
    check_key = f"{client_type}_{client_name}"

    if check_key not in st.session_state.aml_checks:
        st.session_state.aml_checks[check_key] = {i: False for i in range(len(items))}

    checks = st.session_state.aml_checks[check_key]
    completed = sum(1 for v in checks.values() if v)
    total     = len(items)
    pct       = int(completed / total * 100) if total else 0

    # Progress bar
    bar_color = "#dc2626" if pct < 50 else ("#d97706" if pct < 100 else "#16a34a")
    st.markdown(
        f"""<div style="background:#f1f5f9;border-radius:8px;margin:0.75rem 0 1rem">
          <div style="background:{bar_color};width:{pct}%;height:8px;border-radius:8px;
                      transition:width 0.3s"></div>
        </div>
        <p style="font-size:0.82rem;color:{bar_color};font-weight:600;margin-bottom:0.75rem">
          {completed} / {total} items completed ({pct}%)</p>""",
        unsafe_allow_html=True,
    )

    for i, item in enumerate(items):
        done = st.checkbox(item, value=checks.get(i, False), key=f"aml_{check_key}_{i}")
        if done != checks.get(i, False):
            st.session_state.aml_checks[check_key][i] = done
            st.rerun()

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
    if pct == 100:
        st.success(f"✅ KYC complete for {client_name or 'client'}.")

    if st.button("🗑️ Reset Checklist", key="aml_reset"):
        st.session_state.aml_checks.pop(check_key, None)
        st.rerun()

    # Export checklist as text
    report = f"AML/KYC CHECKLIST\n{'='*45}\n"
    report += f"Client: {client_name or '—'}\nMatter: {matter_ref or '—'}\n"
    report += f"Type: {client_type}\nDate: {date.today()}\n\n"
    for i, item in enumerate(items):
        status = "✓" if checks.get(i) else "✗"
        report += f"[{status}] {item}\n"
    report += f"\n{completed}/{total} completed ({pct}%)\n"
    st.download_button(
        "⬇️ Export Checklist (.txt)", data=report,
        file_name=f"aml_kyc_{client_name or 'client'}_{date.today()}.txt",
        mime="text/plain", key="aml_dl",
    )

# ══════════════════════════════════════════════════════════════════
# TAB 2 – PRIVILEGE REGISTER
# ══════════════════════════════════════════════════════════════════
with tab_privilege:
    section("➕ Log Privileged Document")
    matters = db.list_matters()
    m_opts  = {"(No specific matter)": ""} | {
        f"{m['ref']}: {m['title'][:40]}": m["id"] for m in matters
    }
    with st.form("priv_form", clear_on_submit=True):
        p1, p2 = st.columns(2)
        p_doc     = p1.text_input("Document Name *", placeholder="e.g. Advice on liability — 12 May 2026")
        p_matter  = p2.selectbox("Matter", list(m_opts.keys()))
        p3, p4    = st.columns(2)
        p_type    = p3.selectbox("Privilege Type", [
            "Legal professional privilege (LPP)",
            "Litigation privilege",
            "Common interest privilege",
            "Without prejudice",
            "Attorney–client privilege",
        ])
        p_author  = p4.text_input("Author / Lawyer", placeholder="e.g. J. Smith")
        p_reason  = st.text_input("Basis for claim", placeholder="Legal advice sought by client re contract dispute")
        p5, p6    = st.columns(2)
        p_date    = p5.text_input("Document Date", value=str(date.today()))
        p_status  = p6.selectbox("Status", ["Claimed", "Reviewed — upheld", "Reviewed — waived", "Under review"])
        if st.form_submit_button("➕ Add to Register", type="primary"):
            if p_doc.strip():
                st.session_state.priv_log.append({
                    "document": p_doc.strip(), "matter": p_matter,
                    "priv_type": p_type, "author": p_author.strip(),
                    "reason": p_reason.strip(), "date": p_date,
                    "status": p_status, "logged": str(date.today()),
                })
                st.rerun()
            else:
                st.warning("Document name is required.")

    logs = st.session_state.priv_log
    if logs:
        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
        section(f"🔒 Privilege Register ({len(logs)} documents)")

        STATUS_CFG = {
            "Claimed":              ("#2563eb", "#eff6ff"),
            "Reviewed — upheld":    ("#16a34a", "#dcfce7"),
            "Reviewed — waived":    ("#dc2626", "#fef2f2"),
            "Under review":         ("#d97706", "#fffbeb"),
        }
        for i, entry in enumerate(logs):
            fg, bg = STATUS_CFG.get(entry["status"], ("#6b7280","#f1f5f9"))
            st.markdown(
                f"""<div style="background:#fff;border-radius:9px;padding:0.75rem 1rem;
                                margin-bottom:0.4rem;border:1px solid rgba(0,0,0,0.07);
                                border-left:4px solid {fg}">
                  <div style="display:flex;align-items:center;gap:0.5rem;flex-wrap:wrap">
                    <span style="font-weight:600;font-size:0.87rem;color:#1a2744">{entry['document']}</span>
                    <span style="background:{bg};color:{fg};font-size:0.7rem;font-weight:600;
                                 padding:0.15rem 0.45rem;border-radius:20px;margin-left:auto">
                      {entry['status']}</span>
                  </div>
                  <div style="margin-top:0.3rem;font-size:0.76rem;color:#6b7280;display:flex;gap:1rem;flex-wrap:wrap">
                    <span>🔐 {entry['priv_type']}</span>
                    <span>👤 {entry['author'] or '—'}</span>
                    <span>📅 {entry['date']}</span>
                    {'<span>📁 '+entry["matter"].split(":")[0]+'</span>' if entry["matter"] else ''}
                  </div>
                  {'<p style="margin:0.3rem 0 0;font-size:0.78rem;color:#374151">'+entry["reason"]+'</p>' if entry["reason"] else ''}
                </div>""",
                unsafe_allow_html=True,
            )
            if st.button("🗑️", key=f"del_priv_{i}"):
                st.session_state.priv_log.pop(i)
                st.rerun()

        csv  = "Document,Matter,Privilege Type,Author,Date,Status,Reason\n"
        csv += "\n".join(
            f'"{e["document"]}","{e["matter"]}","{e["priv_type"]}","{e["author"]}",{e["date"]},{e["status"]},"{e["reason"]}"'
            for e in logs
        )
        st.download_button(
            "⬇️ Export Register (.csv)", data=csv,
            file_name=f"privilege_register_{date.today()}.csv", mime="text/csv", key="priv_dl",
        )
    else:
        st.info("No privileged documents logged yet.")

# ══════════════════════════════════════════════════════════════════
# TAB 3 – DATA PROTECTION
# ══════════════════════════════════════════════════════════════════
with tab_gdpr:
    GDPR_SECTIONS = {
        "Lawful Basis & Transparency": [
            "Identified the lawful basis for processing each category of personal data",
            "Documented lawful basis in records of processing activities (ROPA)",
            "Privacy notice provided to clients at point of data collection",
            "Privacy notice covers all required GDPR/LGPD/PDPA elements",
            "Special category data (health, biometric) has additional safeguards",
        ],
        "Data Subject Rights": [
            "Process in place to handle Subject Access Requests (SARs) within 1 month",
            "Process to handle right to erasure requests",
            "Process to handle data portability requests",
            "Process to handle objections to processing",
            "Record kept of all DSR requests and responses",
        ],
        "Data Security": [
            "Personal data encrypted at rest",
            "Personal data encrypted in transit (TLS/SSL)",
            "Access controls limit personal data to authorised staff only",
            "Passwords/authentication for systems holding personal data",
            "Regular security testing or penetration testing conducted",
            "Data breach response plan documented and tested",
        ],
        "Third Parties & Transfers": [
            "Data processing agreements (DPAs) in place with all processors",
            "No personal data transferred outside jurisdiction without appropriate safeguard",
            "List of third-party processors maintained and reviewed",
        ],
        "Retention & Disposal": [
            "Retention policy defined per data category",
            "Retention periods communicated in privacy notice",
            "Secure disposal process for expired personal data",
            "Retention schedule reviewed annually",
        ],
        "Governance": [
            "Data Protection Officer (DPO) or responsible person nominated",
            "Records of Processing Activities (ROPA) maintained",
            "Data Protection Impact Assessments (DPIAs) conducted for high-risk processing",
            "Staff training on data protection completed",
            "Incident/breach log maintained",
        ],
    }

    section("🛡️ Data Protection Compliance Checklist")

    all_items = [(sec, item) for sec, items in GDPR_SECTIONS.items() for item in items]
    total     = len(all_items)
    completed = sum(1 for (sec, item) in all_items
                    if st.session_state.gdpr_checks.get(f"{sec}_{item}", False))
    pct = int(completed / total * 100) if total else 0

    bar_color = "#dc2626" if pct < 50 else ("#d97706" if pct < 100 else "#16a34a")
    st.markdown(
        f"""<div style="background:#f1f5f9;border-radius:8px;margin-bottom:0.5rem">
          <div style="background:{bar_color};width:{pct}%;height:8px;border-radius:8px"></div>
        </div>
        <p style="font-size:0.82rem;color:{bar_color};font-weight:600;margin-bottom:1rem">
          {completed}/{total} items completed ({pct}%)</p>""",
        unsafe_allow_html=True,
    )

    for sec_name, items in GDPR_SECTIONS.items():
        sec_done = sum(1 for item in items
                       if st.session_state.gdpr_checks.get(f"{sec_name}_{item}", False))
        st.markdown(
            f"""<div style="background:#1a2744;color:#fff;border-radius:8px;
                            padding:0.45rem 0.85rem;font-weight:600;font-size:0.83rem;
                            margin:0.75rem 0 0.35rem;display:flex;justify-content:space-between">
              <span>{sec_name}</span>
              <span style="opacity:0.7">{sec_done}/{len(items)}</span>
            </div>""",
            unsafe_allow_html=True,
        )
        for item in items:
            k = f"{sec_name}_{item}"
            val = st.checkbox(item, value=st.session_state.gdpr_checks.get(k, False),
                              key=f"gdpr_{k}")
            if val != st.session_state.gdpr_checks.get(k, False):
                st.session_state.gdpr_checks[k] = val
                st.rerun()

    if pct == 100:
        st.success("✅ All data protection items completed.")

    if st.button("🗑️ Reset Checklist", key="gdpr_reset"):
        st.session_state.gdpr_checks = {}
        st.rerun()

# ══════════════════════════════════════════════════════════════════
# TAB 4 – CONFLICT MONITOR
# ══════════════════════════════════════════════════════════════════
with tab_conflict:
    section("⚖️ Run Conflict Check")
    search_party = st.text_input(
        "Party name to screen",
        placeholder="e.g. Acme Corporation or John Smith",
        key="cf_party",
    )
    if st.button("🔍 Check for Conflicts", type="primary",
                 disabled=not search_party.strip(), key="cf_run"):
        name_l      = search_party.strip().lower()
        all_clients = db.list_clients()
        all_matters = db.list_matters()
        client_hits = [c for c in all_clients
                       if name_l in (c.get("name") or "").lower()
                       or name_l in (c.get("company_name") or "").lower()]
        matter_hits = [m for m in all_matters
                       if name_l in m["title"].lower()
                       or name_l in (m.get("opposing_party") or "").lower()]

        if client_hits or matter_hits:
            st.markdown(
                f"""<div style="background:#fef2f2;border-radius:10px;padding:1rem;
                                border-left:4px solid #dc2626;margin:0.75rem 0">
                  <p style="margin:0;font-weight:700;color:#dc2626">
                    ⚠️ Potential conflict found for "{search_party}"</p>
                </div>""",
                unsafe_allow_html=True,
            )
            if client_hits:
                st.markdown("**Matching clients:**")
                for c in client_hits:
                    st.markdown(
                        f'<div style="background:#fff;border-radius:7px;padding:0.5rem 0.85rem;'
                        f'margin-bottom:0.3rem;border:1px solid rgba(0,0,0,0.07)">'
                        f'🏢 <b>{c["name"]}</b> — {c.get("company_name") or "Individual"}'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
            if matter_hits:
                st.markdown("**Matching matters:**")
                for m in matter_hits:
                    st.markdown(
                        f'<div style="background:#fff;border-radius:7px;padding:0.5rem 0.85rem;'
                        f'margin-bottom:0.3rem;border:1px solid rgba(0,0,0,0.07)">'
                        f'📁 <b>{m.get("ref","")}</b>: {m["title"]} '
                        f'<span style="color:#6b7280">— {m.get("status","")}</span>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
        else:
            st.success(f"✅ No conflicts found for **\"{search_party}\"**.")

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    section("📋 Conflict Waiver Log")
    with st.form("waiver_form", clear_on_submit=True):
        w1, w2, w3 = st.columns(3)
        w_party   = w1.text_input("Party name *")
        w_matter  = w2.text_input("Matter reference")
        w_date    = w3.text_input("Waiver date", value=str(date.today()))
        w_notes   = st.text_input("Notes / consent basis",
                                   placeholder="Client confirmed no conflict / obtained waiver in writing")
        if st.form_submit_button("Add Waiver", type="primary"):
            if w_party.strip():
                st.session_state.waivers.append({
                    "party": w_party.strip(), "matter": w_matter.strip(),
                    "date": w_date, "notes": w_notes.strip(),
                })
                st.rerun()

    waivers = st.session_state.waivers
    if waivers:
        for w in waivers:
            st.markdown(
                f"""<div style="background:#f0fdf4;border-radius:8px;padding:0.65rem 0.9rem;
                                margin-bottom:0.35rem;border-left:3px solid #16a34a">
                  <span style="font-weight:600;font-size:0.87rem">✅ {w['party']}</span>
                  <span style="color:#6b7280;font-size:0.75rem;margin-left:0.75rem">
                    {w['matter'] or '—'} · {w['date']}</span>
                  {'<p style="margin:0.2rem 0 0;font-size:0.78rem;color:#374151">'+w["notes"]+'</p>' if w["notes"] else ''}
                </div>""",
                unsafe_allow_html=True,
            )
    else:
        st.caption("No conflict waivers recorded yet.")
