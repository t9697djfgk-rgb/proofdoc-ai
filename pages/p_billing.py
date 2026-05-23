import streamlit as st
from utils.shared.sidebar import setup_page
from utils.shared.styles import slim_header, group_header, placeholder_feature

setup_page()
slim_header("💼", "Billing & Time", "Time tracking, expenses, invoicing, payments, and financial reporting")

tab_time, tab_invoices, tab_reports = st.tabs([
    "⏱️ Time Tracking", "🧾 Invoices & Payments", "📊 Reports",
])

with tab_time:
    group_header("Time & Expenses")
    c1, c2 = st.columns(2)
    with c1:
        placeholder_feature(
            "⏱️", "Time Tracking",
            "Record billable time directly against matters with task descriptions and rate codes.",
            ["Start a timer from any matter or task", "Record time entries manually with narrative",
             "Apply standard rate codes (partner, associate, paralegal)",
             "View time per matter, lawyer, and month"],
            ["Timesheet per lawyer", "Matter time summary",
             "Pre-billing report for client review", "WIP report"],
        )
    with c2:
        placeholder_feature(
            "💳", "Expenses",
            "Log and approve disbursements and expenses to be billed to clients.",
            ["Record expenses with receipt upload", "Link to matter and client",
             "Apply markup where applicable", "Approve expenses before billing"],
            ["Expense report per matter", "Client-ready disbursement schedule",
             "VAT/tax categorisation"],
        )

with tab_invoices:
    group_header("Invoices & Payments")
    c1, c2 = st.columns(2)
    with c1:
        placeholder_feature(
            "🧾", "Invoices",
            "Generate, send, and track professional invoices from matter time and expense records.",
            ["Auto-generate invoice from matter WIP",
             "Customise invoice with firm branding",
             "Send by email or download as PDF",
             "Track invoice status (sent, viewed, paid, overdue)"],
            ["Branded invoice PDF", "Invoice status dashboard",
             "Overdue invoice alerts", "Client invoice history"],
        )
    with c2:
        placeholder_feature(
            "💰", "Payments",
            "Record client payments, manage retainer accounts, and track outstanding balances.",
            ["Record payments against specific invoices",
             "Manage retainer deposits and draw-downs",
             "Track outstanding balances per client",
             "Reconcile with trust/client account"],
            ["Payment ledger per client", "Retainer balance report",
             "Outstanding receivables aging report"],
        )

with tab_reports:
    placeholder_feature(
        "📊", "Financial Reports",
        "Generate management reports on firm revenue, WIP, billing, and collection performance.",
        ["Generate revenue report by period, matter, and lawyer",
         "Track WIP and billing realisation rates",
         "Monitor lock-up (unbilled time and outstanding invoices)",
         "Export reports for accounts or management"],
        ["Revenue report (monthly/quarterly)", "WIP summary",
         "Collection rate by client and lawyer", "Management dashboard export (PDF/Excel)"],
    )
