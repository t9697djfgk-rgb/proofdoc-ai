import streamlit as st
import datetime
from utils.shared.sidebar import setup_page
from utils.shared.styles import slim_header, inject_css, section
from utils.auth import require_lawyer
import utils.database as db

setup_page()
user = require_lawyer()
inject_css()
slim_header("💼", "Billing & Time", "Time tracking, expenses, invoicing, and financial reporting")

# Session state for expenses (no DB table — stored per session)
if "expenses" not in st.session_state:
    st.session_state.expenses = []

tab_time, tab_expenses, tab_invoices, tab_reports = st.tabs([
    "⏱️ Time Tracking", "💳 Expenses", "🧾 Invoices", "📊 Reports",
])

# ══════════════════════════════════════════════════════════════════
# TAB 1 – TIME TRACKING
# ══════════════════════════════════════════════════════════════════
with tab_time:
    matters = db.list_matters(status="Active")
    matter_options = {"(No matter / General)": ""} | {
        f"{m['ref']}: {m['title'][:40]}": m["id"] for m in matters
    }

    section("Log Time")
    with st.form("billing_time", clear_on_submit=True):
        c1, c2 = st.columns(2)
        bt_matter = c1.selectbox("Matter", list(matter_options.keys()), key="bt_m")
        bt_date   = c2.text_input("Date", value=str(datetime.date.today()), key="bt_d")
        c3, c4, c5 = st.columns(3)
        bt_hours = c3.number_input("Hours", min_value=0.25, step=0.25, value=1.0, key="bt_h")
        bt_rate  = c4.number_input("Rate (£/hr)", min_value=0.0, step=50.0, value=250.0, key="bt_r")
        bt_desc  = c5.text_input("Description *", placeholder="e.g. Drafting NDA", key="bt_desc")
        if st.form_submit_button("＋ Log Time", type="primary"):
            if not bt_desc.strip():
                st.warning("Description is required.")
            else:
                db.add_time_entry(
                    matter_id=matter_options.get(bt_matter) or None,
                    hours=bt_hours, description=bt_desc.strip(),
                    rate=bt_rate, entry_date=bt_date.strip(),
                )
                st.rerun()

    entries = db.list_time_entries()
    if entries:
        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

        total_h   = sum(e["hours"] for e in entries)
        total_val = sum(e["hours"] * (e.get("rate") or 0) for e in entries)
        unbilled  = sum(e["hours"] * (e.get("rate") or 0) for e in entries if not e.get("billed"))

        c1, c2, c3 = st.columns(3)
        for col, label, value, color, bg in [
            (c1, "Total Hours",  f"{total_h:.2f} h",     "#1a2744", "#e8f0fe"),
            (c2, "Total Value",  f"£{total_val:,.2f}",   "#059669", "#ecfdf5"),
            (c3, "Unbilled WIP", f"£{unbilled:,.2f}",    "#d97706", "#fffbeb"),
        ]:
            col.markdown(
                f"""<div style="background:{bg};border-radius:10px;padding:0.75rem 1rem;
                                border-left:4px solid {color}">
                  <p style="margin:0;font-size:0.72rem;font-weight:600;color:#6b7280;
                            text-transform:uppercase">{label}</p>
                  <p style="margin:0.2rem 0 0;font-size:1.5rem;font-weight:700;color:{color}">{value}</p>
                </div>""",
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
        section(f"📋 Time Entries ({len(entries)})")

        h = st.columns([1.5, 3, 1.5, 1, 1.2, 1.5])
        for col, lbl in zip(h, ["Date", "Description", "Lawyer", "Hours", "Rate", "Value"]):
            col.markdown(f"**{lbl}**")
        st.divider()
        for e in entries:
            row = st.columns([1.5, 3, 1.5, 1, 1.2, 1.5])
            row[0].caption(str(e.get("entry_date") or e.get("date",""))[:10])
            row[1].text((e.get("description") or "—")[:45])
            row[2].caption(e.get("lawyer") or e.get("profiles", {}).get("full_name","—") or "—")
            row[3].text(f"{e['hours']:.2f}h")
            row[4].text(f"£{(e.get('rate') or 0):.0f}")
            row[5].markdown(
                f"<span style='font-weight:600;color:#1a2744'>"
                f"£{e['hours'] * (e.get('rate') or 0):,.2f}</span>",
                unsafe_allow_html=True,
            )
    else:
        st.info("No time entries yet.")

# ══════════════════════════════════════════════════════════════════
# TAB 2 – EXPENSES
# ══════════════════════════════════════════════════════════════════
with tab_expenses:
    section("➕ Log Expense / Disbursement")
    matters_all = db.list_matters()
    exp_matter_opts = {"(No matter)": ""} | {
        f"{m['ref']}: {m['title'][:35]}": m["id"] for m in matters_all
    }
    with st.form("expense_form", clear_on_submit=True):
        e1, e2, e3 = st.columns(3)
        ex_desc    = e1.text_input("Description *", placeholder="e.g. Court filing fee")
        ex_amount  = e2.number_input("Amount (£)", min_value=0.0, step=1.0, value=0.0)
        ex_date    = e3.text_input("Date", value=str(datetime.date.today()))
        e4, e5, e6 = st.columns(3)
        ex_cat     = e4.selectbox("Category", [
            "Court fees", "Counsel fees", "Expert fees", "Travel",
            "Searches / filings", "Photocopying", "Postage", "Other",
        ])
        ex_matter  = e5.selectbox("Matter", list(exp_matter_opts.keys()))
        ex_billed  = e6.checkbox("Billable to client", value=True)
        if st.form_submit_button("＋ Add Expense", type="primary"):
            if not ex_desc.strip() or ex_amount <= 0:
                st.warning("Description and amount are required.")
            else:
                st.session_state.expenses.append({
                    "description": ex_desc.strip(),
                    "amount": ex_amount,
                    "date": ex_date,
                    "category": ex_cat,
                    "matter_id": exp_matter_opts[ex_matter],
                    "matter_label": ex_matter,
                    "billable": ex_billed,
                })
                st.rerun()

    expenses = st.session_state.expenses
    if expenses:
        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

        total_exp    = sum(e["amount"] for e in expenses)
        billable_exp = sum(e["amount"] for e in expenses if e.get("billable"))

        c1, c2 = st.columns(2)
        c1.markdown(
            f"""<div style="background:#f5f3ff;border-radius:10px;padding:0.75rem 1rem;
                            border-left:4px solid #7c3aed">
              <p style="margin:0;font-size:0.72rem;font-weight:600;color:#6b7280;
                        text-transform:uppercase">Total Expenses</p>
              <p style="margin:0.2rem 0 0;font-size:1.5rem;font-weight:700;color:#7c3aed">£{total_exp:,.2f}</p>
            </div>""",
            unsafe_allow_html=True,
        )
        c2.markdown(
            f"""<div style="background:#ecfdf5;border-radius:10px;padding:0.75rem 1rem;
                            border-left:4px solid #059669">
              <p style="margin:0;font-size:0.72rem;font-weight:600;color:#6b7280;
                        text-transform:uppercase">Billable to Clients</p>
              <p style="margin:0.2rem 0 0;font-size:1.5rem;font-weight:700;color:#059669">£{billable_exp:,.2f}</p>
            </div>""",
            unsafe_allow_html=True,
        )

        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
        section(f"💳 Expense Log ({len(expenses)})")
        h = st.columns([1.5, 3, 1.5, 1.5, 1, 0.5])
        for col, lbl in zip(h, ["Date", "Description", "Category", "Matter", "Amount", ""]):
            col.markdown(f"**{lbl}**")
        st.divider()
        for i, ex in enumerate(expenses):
            r = st.columns([1.5, 3, 1.5, 1.5, 1, 0.5])
            r[0].caption(str(ex.get("date",""))[:10])
            r[1].text(ex["description"][:40])
            r[2].caption(ex.get("category",""))
            r[3].caption((ex.get("matter_label","")[:25]) if ex.get("matter_label") != "(No matter)" else "—")
            r[4].markdown(
                f"<span style='font-weight:600;color:#{'7c3aed' if ex.get('billable') else '6b7280'}'>"
                f"£{ex['amount']:,.2f}</span>",
                unsafe_allow_html=True,
            )
            if r[5].button("🗑️", key=f"del_exp_{i}"):
                st.session_state.expenses.pop(i)
                st.rerun()

        csv = "Date,Description,Category,Matter,Amount,Billable\n"
        csv += "\n".join(
            f"{e['date']},{e['description']},{e['category']},{e.get('matter_label','')},{e['amount']},{e['billable']}"
            for e in expenses
        )
        st.download_button("⬇️ Export Expenses (.csv)", data=csv,
                           file_name=f"expenses_{datetime.date.today()}.csv",
                           mime="text/csv", key="dl_expenses")
    else:
        st.info("No expenses logged yet.")

# ══════════════════════════════════════════════════════════════════
# TAB 3 – INVOICES
# ══════════════════════════════════════════════════════════════════
with tab_invoices:
    matters_all = db.list_matters()
    inv_options = {"Select matter": ""} | {
        f"{m['ref']}: {m['title'][:40]}": m["id"] for m in matters_all
    }
    inv_matter  = st.selectbox("Matter to Invoice", list(inv_options.keys()), key="inv_m")
    selected_mid = inv_options.get(inv_matter, "")

    if selected_mid:
        entries = db.list_time_entries(selected_mid)
        unbilled = [e for e in entries if not e.get("billed")]
        matter   = db.get_matter(selected_mid)

        if unbilled:
            total_fees = sum(e["hours"] * (e.get("rate") or 0) for e in unbilled)
            total_hrs  = sum(e["hours"] for e in unbilled)

            c1, c2 = st.columns(2)
            c1.markdown(
                f"""<div style="background:#eff6ff;border-radius:10px;padding:0.75rem 1rem;
                                border-left:4px solid #2563eb">
                  <p style="margin:0;font-size:0.72rem;font-weight:600;color:#6b7280;
                            text-transform:uppercase">Unbilled Entries</p>
                  <p style="margin:0.2rem 0 0;font-size:1.5rem;font-weight:700;color:#2563eb">
                    {len(unbilled)} entries · {total_hrs:.2f}h</p>
                </div>""",
                unsafe_allow_html=True,
            )
            c2.markdown(
                f"""<div style="background:#ecfdf5;border-radius:10px;padding:0.75rem 1rem;
                                border-left:4px solid #059669">
                  <p style="margin:0;font-size:0.72rem;font-weight:600;color:#6b7280;
                            text-transform:uppercase">Total Fees</p>
                  <p style="margin:0.2rem 0 0;font-size:1.5rem;font-weight:700;color:#059669">
                    £{total_fees:,.2f}</p>
                </div>""",
                unsafe_allow_html=True,
            )

            st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
            f1, f2, f3 = st.columns(3)
            inv_client = f1.text_input("Client Name", placeholder="Invoice addressee", key="inv_cl")
            inv_ref    = f2.text_input("Invoice Number",
                                        value=f"INV-{datetime.date.today().strftime('%Y%m%d')}-001",
                                        key="inv_ref")
            inv_vat    = f3.number_input("VAT (%)", min_value=0.0, max_value=30.0,
                                          value=0.0, step=5.0, key="inv_vat")
            inv_terms  = st.text_input("Payment Terms", value="Payment due within 30 days", key="inv_t")
            inv_notes  = st.text_area("Notes (optional)", height=60, key="inv_n")

            if st.button("🧾 Generate Invoice", type="primary", key="inv_gen"):
                vat_amt    = total_fees * inv_vat / 100
                total_incl = total_fees + vat_amt
                today_str  = str(datetime.date.today())
                lines = [
                    "INVOICE",
                    "=" * 55,
                    f"Invoice No.:  {inv_ref}",
                    f"Date:         {today_str}",
                    "",
                    f"FROM: {user.get('organization_name','eLawFirm')}",
                    f"TO:   {inv_client or 'Client'}",
                    f"RE:   {matter.get('ref','')} — {matter.get('title','')}",
                    "",
                    "=" * 55,
                    f"{'DATE':<14}{'DESCRIPTION':<28}{'HRS':>6}  {'RATE':>9}  {'AMOUNT':>11}",
                    "-" * 55,
                ]
                for e in unbilled:
                    amt = e["hours"] * (e.get("rate") or 0)
                    desc = (e.get("description") or "")[:27]
                    lines.append(
                        f"{str(e.get('entry_date') or e.get('date',''))[:10]:<14}"
                        f"{desc:<28}{e['hours']:>6.2f}  "
                        f"£{(e.get('rate') or 0):>8.2f}  £{amt:>9,.2f}"
                    )
                lines += [
                    "-" * 55,
                    f"{'Subtotal':<49} £{total_fees:>9,.2f}",
                ]
                if inv_vat > 0:
                    lines.append(f"{'VAT ('+str(int(inv_vat))+'%)':<49} £{vat_amt:>9,.2f}")
                lines += [
                    f"{'TOTAL DUE':<49} £{total_incl:>9,.2f}",
                    "",
                    inv_terms,
                ]
                if inv_notes.strip():
                    lines += ["", f"Notes: {inv_notes}"]
                st.session_state.inv_preview = "\n".join(lines)
                st.rerun()
        else:
            st.info("No unbilled time entries for this matter.")

    if st.session_state.get("inv_preview"):
        st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
        section("🧾 Invoice Preview")
        st.markdown(
            f"""<div style="background:#fff;border-radius:12px;padding:1.5rem;
                            border:1px solid rgba(0,0,0,0.08);font-family:monospace;
                            font-size:0.82rem;white-space:pre;overflow-x:auto;
                            box-shadow:0 2px 8px rgba(0,0,0,0.06)">
              {st.session_state.inv_preview}
            </div>""",
            unsafe_allow_html=True,
        )
        c1, c2, c3 = st.columns(3)
        c1.download_button(
            "⬇️ Download (.txt)", st.session_state.inv_preview,
            "invoice.txt", "text/plain", use_container_width=True, key="inv_dl",
        )
        with c2:
            from utils.shared.export_utils import download_pdf
            download_pdf(
                "📄 Download (.pdf)", st.session_state.inv_preview,
                "invoice.pdf", title="Invoice", key="inv_dl_pdf",
            )
        if c3.button("🗑️ Clear", use_container_width=True, key="inv_clr"):
            st.session_state.pop("inv_preview", None)
            st.rerun()

# ══════════════════════════════════════════════════════════════════
# TAB 4 – REPORTS
# ══════════════════════════════════════════════════════════════════
with tab_reports:
    all_entries = db.list_time_entries()
    if not all_entries:
        st.info("No time entries yet. Log time in the Time Tracking tab.")
        st.stop()

    total_h   = sum(e["hours"] for e in all_entries)
    total_val = sum(e["hours"] * (e.get("rate") or 0) for e in all_entries)
    unbilled  = sum(e["hours"] * (e.get("rate") or 0) for e in all_entries if not e.get("billed"))
    billed    = total_val - unbilled

    c1, c2, c3, c4 = st.columns(4)
    for col, label, value, color, bg in [
        (c1, "Total Hours",   f"{total_h:.2f} h",  "#1a2744", "#e8f0fe"),
        (c2, "Total Value",   f"£{total_val:,.2f}", "#059669", "#ecfdf5"),
        (c3, "Billed",        f"£{billed:,.2f}",    "#2563eb", "#eff6ff"),
        (c4, "WIP Unbilled",  f"£{unbilled:,.2f}",  "#d97706", "#fffbeb"),
    ]:
        col.markdown(
            f"""<div style="background:{bg};border-radius:10px;padding:0.75rem 1rem;
                            border-left:4px solid {color}">
              <p style="margin:0;font-size:0.72rem;font-weight:600;color:#6b7280;
                        text-transform:uppercase">{label}</p>
              <p style="margin:0.2rem 0 0;font-size:1.4rem;font-weight:700;color:{color}">{value}</p>
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    col_l, col_r = st.columns(2, gap="large")
    with col_l:
        section("👩‍⚖️ By Lawyer")
        lawyers = {}
        for e in all_entries:
            ln = e.get("lawyer") or (e.get("profiles") or {}).get("full_name","") or "Unassigned"
            lawyers.setdefault(ln, {"hours": 0, "value": 0})
            lawyers[ln]["hours"] += e["hours"]
            lawyers[ln]["value"] += e["hours"] * (e.get("rate") or 0)

        for name, data in sorted(lawyers.items(), key=lambda x: -x[1]["value"]):
            pct = (data["value"] / total_val * 100) if total_val else 0
            st.markdown(
                f"""<div style="background:#fff;border-radius:8px;padding:0.65rem 0.85rem;
                               margin-bottom:0.35rem;border:1px solid rgba(0,0,0,0.07)">
                  <div style="display:flex;justify-content:space-between;align-items:center">
                    <span style="font-size:0.85rem;font-weight:600;color:#1a2744">{name}</span>
                    <span style="font-size:0.85rem;font-weight:700;color:#059669">£{data['value']:,.2f}</span>
                  </div>
                  <div style="display:flex;justify-content:space-between;margin-top:0.2rem">
                    <span style="font-size:0.73rem;color:#6b7280">{data['hours']:.2f}h</span>
                    <span style="font-size:0.73rem;color:#9ca3af">{pct:.1f}% of total</span>
                  </div>
                  <div style="background:#f1f5f9;border-radius:4px;height:4px;margin-top:0.4rem">
                    <div style="background:#1a2744;width:{pct:.1f}%;height:4px;border-radius:4px"></div>
                  </div>
                </div>""",
                unsafe_allow_html=True,
            )

    with col_r:
        section("📁 By Matter")
        all_matters = {m["id"]: f"{m['ref']}: {m['title'][:25]}" for m in db.list_matters()}
        matters_t   = {}
        for e in all_entries:
            mid = e.get("matter_id") or "General"
            matters_t.setdefault(mid, {"hours": 0, "value": 0})
            matters_t[mid]["hours"] += e["hours"]
            matters_t[mid]["value"] += e["hours"] * (e.get("rate") or 0)

        for mid, data in sorted(matters_t.items(), key=lambda x: -x[1]["value"]):
            label = all_matters.get(mid, "General / No matter")
            pct   = (data["value"] / total_val * 100) if total_val else 0
            st.markdown(
                f"""<div style="background:#fff;border-radius:8px;padding:0.65rem 0.85rem;
                               margin-bottom:0.35rem;border:1px solid rgba(0,0,0,0.07)">
                  <div style="display:flex;justify-content:space-between;align-items:center">
                    <span style="font-size:0.82rem;font-weight:600;color:#1a2744">{label}</span>
                    <span style="font-size:0.85rem;font-weight:700;color:#059669">£{data['value']:,.2f}</span>
                  </div>
                  <div style="display:flex;justify-content:space-between;margin-top:0.2rem">
                    <span style="font-size:0.73rem;color:#6b7280">{data['hours']:.2f}h</span>
                    <span style="font-size:0.73rem;color:#9ca3af">{pct:.1f}%</span>
                  </div>
                  <div style="background:#f1f5f9;border-radius:4px;height:4px;margin-top:0.4rem">
                    <div style="background:#c9a84c;width:{pct:.1f}%;height:4px;border-radius:4px"></div>
                  </div>
                </div>""",
                unsafe_allow_html=True,
            )

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
    report_lines = [
        "BILLING REPORT", "=" * 40,
        f"Generated: {datetime.date.today()}",
        f"Total Hours: {total_h:.2f}h",
        f"Total Value: £{total_val:,.2f}",
        f"Billed: £{billed:,.2f}",
        f"WIP (Unbilled): £{unbilled:,.2f}",
        "", "BY LAWYER:",
    ]
    for name, data in lawyers.items():
        report_lines.append(f"  {name}: {data['hours']:.2f}h  £{data['value']:,.2f}")
    st.download_button(
        "⬇️ Export Report (.txt)", "\n".join(report_lines),
        f"billing_report_{datetime.date.today()}.txt", "text/plain", key="br_exp",
    )
