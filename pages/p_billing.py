import streamlit as st
from utils.shared.sidebar import setup_page
from utils.shared.styles import slim_header, group_header, section, placeholder_feature
from utils.auth import require_lawyer
import utils.database as db

setup_page()
user = require_lawyer()
slim_header("💼", "Billing & Time", "Time tracking, expenses, invoicing, payments, and financial reporting")

tab_time, tab_invoices, tab_reports = st.tabs([
    "⏱️ Time Tracking", "🧾 Invoices & Payments", "📊 Reports",
])

# ── Time Tracking ─────────────────────────────────────────────────
with tab_time:
    group_header("Log Time")
    matters = db.list_matters(status="Active")
    matter_options = {"(No matter / General)": ""} | {f"{m['ref']}: {m['title'][:40]}": m["id"] for m in matters}

    with st.form("billing_time", clear_on_submit=True):
        c1, c2 = st.columns(2)
        bt_matter = c1.selectbox("Matter", list(matter_options.keys()), key="bt_m")
        bt_date   = c2.text_input("Date (YYYY-MM-DD)", value=str(__import__("datetime").date.today()), key="bt_d")
        c3, c4, c5 = st.columns(3)
        bt_hours  = c3.number_input("Hours", min_value=0.25, step=0.25, value=1.0, key="bt_h")
        bt_rate   = c4.number_input("Rate (£/hr)", min_value=0.0, step=50.0, value=250.0, key="bt_r")
        bt_desc   = c5.text_input("Description *", placeholder="e.g. Drafting NDA, client call", key="bt_desc")
        if st.form_submit_button("＋ Log Time", type="primary"):
            if not bt_desc.strip():
                st.warning("⚠️ Description is required.")
            else:
                db.add_time_entry(
                    matter_id=matter_options.get(bt_matter) or None,
                    hours=bt_hours,
                    description=bt_desc.strip(),
                    rate=bt_rate,
                    entry_date=bt_date.strip(),
                )
                st.success(f"✅ {bt_hours}h logged.")
                st.rerun()

    # Time entries table
    entries = db.list_time_entries()
    if entries:
        st.markdown("<br>", unsafe_allow_html=True)
        section(f"📋 All Time Entries ({len(entries)})")

        # Summary stats
        total_h   = sum(e["hours"] for e in entries)
        total_val = sum(e["hours"] * (e["rate"] or 0) for e in entries)
        unbilled  = sum(e["hours"] * (e["rate"] or 0) for e in entries if not e.get("billed"))

        m1, m2, m3 = st.columns(3)
        m1.metric("Total Hours", f"{total_h:.2f} h")
        m2.metric("Total Value",  f"£{total_val:,.2f}")
        m3.metric("Unbilled WIP", f"£{unbilled:,.2f}")

        st.divider()
        h = st.columns([1.5, 3, 1.5, 1.5, 1.5, 1.5])
        for col, lbl in zip(h, ["Date", "Description", "Lawyer", "Hours", "Rate", "Value"]):
            col.markdown(f"**{lbl}**")
        st.divider()
        for e in entries:
            row = st.columns([1.5, 3, 1.5, 1.5, 1.5, 1.5])
            row[0].text(e["date"])
            row[1].text(e["description"] or "—")
            row[2].text(e["lawyer"] or "—")
            row[3].text(f"{e['hours']:.2f}h")
            row[4].text(f"£{(e['rate'] or 0):.0f}")
            row[5].text(f"£{e['hours'] * (e['rate'] or 0):,.2f}")
    else:
        st.markdown('<div class="empty-list">No time entries yet. Log your first entry above.</div>',
                    unsafe_allow_html=True)

# ── Invoices & Payments ───────────────────────────────────────────
with tab_invoices:
    group_header("Generate Invoice")
    matters_all = db.list_matters()
    inv_options = {"Select matter": ""} | {f"{m['ref']}: {m['title'][:40]}": m["id"] for m in matters_all}
    inv_matter  = st.selectbox("Matter to Invoice", list(inv_options.keys()), key="inv_m")

    selected_mid = inv_options.get(inv_matter, "")
    if selected_mid:
        entries = db.list_time_entries(selected_mid)
        unbilled_entries = [e for e in entries if not e.get("billed")]
        matter = db.get_matter(selected_mid)

        if unbilled_entries:
            total_fees = sum(e["hours"] * (e["rate"] or 0) for e in unbilled_entries)
            total_hrs  = sum(e["hours"] for e in unbilled_entries)

            st.markdown(f"**{len(unbilled_entries)} unbilled entries** — {total_hrs:.2f}h — £{total_fees:,.2f}")

            c1, c2, c3 = st.columns(3)
            inv_client = c1.text_input("Client Name", placeholder="Invoice addressee", key="inv_cl")
            inv_ref    = c2.text_input("Invoice Number", value=f"INV-{__import__('datetime').date.today().strftime('%Y%m%d')}-001", key="inv_ref")
            inv_vat    = c3.number_input("VAT Rate (%)", min_value=0.0, max_value=30.0, value=20.0, step=5.0, key="inv_vat")
            inv_terms  = st.text_input("Payment Terms", value="Payment due within 30 days", key="inv_terms")
            inv_notes  = st.text_area("Additional Notes", height=60, key="inv_notes")

            if st.button("🧾 Generate Invoice", type="primary", key="inv_gen"):
                vat_amount = total_fees * inv_vat / 100
                total_inc_vat = total_fees + vat_amount
                today = str(__import__("datetime").date.today())

                lines = [
                    f"INVOICE",
                    f"{'='*50}",
                    f"Invoice No.:  {inv_ref}",
                    f"Date:         {today}",
                    f"",
                    f"FROM: eLawFirm Law Firm",
                    f"TO:   {inv_client or 'Client'}",
                    f"RE:   Matter {matter.get('ref','')} — {matter.get('title','')}",
                    f"",
                    f"{'='*50}",
                    f"{'DATE':<14} {'DESCRIPTION':<30} {'HRS':>6} {'RATE':>10} {'AMOUNT':>12}",
                    f"{'-'*50}",
                ]
                for e in unbilled_entries:
                    amt = e["hours"] * (e["rate"] or 0)
                    lines.append(f"{e['date']:<14} {(e['description'] or '')[:30]:<30} {e['hours']:>6.2f} £{(e['rate'] or 0):>8.2f} £{amt:>10,.2f}")
                lines += [
                    f"{'-'*50}",
                    f"{'SUBTOTAL':>50} £{total_fees:>10,.2f}",
                    f"{'VAT (' + str(inv_vat) + '%)':>50} £{vat_amount:>10,.2f}",
                    f"{'TOTAL DUE':>50} £{total_inc_vat:>10,.2f}",
                    f"",
                    f"{inv_terms}",
                ]
                if inv_notes.strip():
                    lines += [f"", f"Notes: {inv_notes}"]

                invoice_text = "\n".join(lines)
                st.session_state.inv_preview = invoice_text
                st.rerun()

        else:
            st.info("ℹ️ No unbilled time entries for this matter.")

    if st.session_state.get("inv_preview"):
        st.divider()
        section("🧾 Invoice Preview")
        st.code(st.session_state.inv_preview, language=None)
        c1, c2 = st.columns(2)
        c1.download_button("📥 Download Invoice (.txt)", st.session_state.inv_preview,
                           "invoice.txt", "text/plain", use_container_width=True, key="inv_dl")
        if c2.button("🔄 Clear Preview", use_container_width=True, key="inv_clr"):
            st.session_state.pop("inv_preview", None)
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    group_header("Payments & Expenses")
    c1, c2 = st.columns(2)
    with c1:
        placeholder_feature(
            "💰", "Payment Recording",
            "Record client payments and track outstanding balances per matter.",
            ["Record payment against invoice", "Manage retainer deposits",
             "Track outstanding balances", "Reconcile with client account"],
            ["Payment ledger", "Outstanding receivables", "Retainer balance report"],
        )
    with c2:
        placeholder_feature(
            "💳", "Expenses & Disbursements",
            "Log and approve disbursements to be billed to clients.",
            ["Record expenses with receipt upload", "Link to matter and client",
             "Apply markup where applicable", "Approve before billing"],
            ["Expense report", "Disbursement schedule", "VAT categorisation"],
        )

# ── Reports ───────────────────────────────────────────────────────
with tab_reports:
    group_header("Financial Summary")

    all_entries = db.list_time_entries()
    if all_entries:
        import json as _json
        total_h    = sum(e["hours"] for e in all_entries)
        total_val  = sum(e["hours"] * (e["rate"] or 0) for e in all_entries)
        unbilled   = sum(e["hours"] * (e["rate"] or 0) for e in all_entries if not e.get("billed"))
        billed     = total_val - unbilled

        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Total Hours",    f"{total_h:.2f} h")
        m2.metric("Total Value",     f"£{total_val:,.2f}")
        m3.metric("Billed",          f"£{billed:,.2f}")
        m4.metric("WIP (Unbilled)",  f"£{unbilled:,.2f}")

        # Per-lawyer summary
        lawyers = {}
        for e in all_entries:
            ln = e.get("lawyer") or "Unassigned"
            lawyers.setdefault(ln, {"hours": 0, "value": 0})
            lawyers[ln]["hours"] += e["hours"]
            lawyers[ln]["value"] += e["hours"] * (e["rate"] or 0)

        section("👩‍⚖️ Summary by Lawyer")
        lh = st.columns([3, 1.5, 2])
        for col, lbl in zip(lh, ["Lawyer", "Hours", "Value"]): col.markdown(f"**{lbl}**")
        st.divider()
        for name, data in sorted(lawyers.items(), key=lambda x: -x[1]["value"]):
            lr = st.columns([3, 1.5, 2])
            lr[0].text(name)
            lr[1].text(f"{data['hours']:.2f} h")
            lr[2].text(f"£{data['value']:,.2f}")

        # Per-matter summary
        matters_time = {}
        for e in all_entries:
            mid = e.get("matter_id") or "General"
            matters_time.setdefault(mid, {"hours": 0, "value": 0})
            matters_time[mid]["hours"] += e["hours"]
            matters_time[mid]["value"] += e["hours"] * (e["rate"] or 0)

        section("📁 Summary by Matter")
        all_matters = {m["id"]: f"{m['ref']}: {m['title'][:30]}" for m in db.list_matters()}
        mh = st.columns([3, 1.5, 2])
        for col, lbl in zip(mh, ["Matter", "Hours", "Value"]): col.markdown(f"**{lbl}**")
        st.divider()
        for mid, data in sorted(matters_time.items(), key=lambda x: -x[1]["value"]):
            mr = st.columns([3, 1.5, 2])
            mr[0].text(all_matters.get(mid, mid))
            mr[1].text(f"{data['hours']:.2f} h")
            mr[2].text(f"£{data['value']:,.2f}")

        # Export
        st.markdown("<br>", unsafe_allow_html=True)
        report_lines = [
            "BILLING REPORT",
            "=" * 40,
            f"Total Hours: {total_h:.2f}h",
            f"Total Value: £{total_val:,.2f}",
            f"Billed: £{billed:,.2f}",
            f"WIP (Unbilled): £{unbilled:,.2f}",
            "",
            "BY LAWYER:",
        ]
        for name, data in lawyers.items():
            report_lines.append(f"  {name}: {data['hours']:.2f}h  £{data['value']:,.2f}")
        st.download_button("📥 Export Report (.txt)", "\n".join(report_lines),
                           "billing_report.txt", "text/plain", key="br_exp")
    else:
        st.markdown('<div class="empty-list">No time entries yet. Log time in the Time Tracking tab.</div>',
                    unsafe_allow_html=True)
