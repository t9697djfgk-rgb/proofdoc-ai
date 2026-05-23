import streamlit as st
import json
from utils.shared.sidebar import setup_page
from utils.shared.styles import slim_header, section, group_header, placeholder_feature

setup_page()
slim_header("📋", "Audit Trail", "Processing logs, activity records, and user access history")

tab_session, tab_activity, tab_access = st.tabs([
    "📋 Session Audit Log",
    "📊 Activity Logs",
    "🔐 User Access Logs",
])

# ── Session Audit Log (functional) ───────────────────────────────
with tab_session:
    st.markdown(
        "Every document processed in this session is logged here with timestamps, "
        "actions, and AI confidence scores."
    )

    audit = st.session_state.get("last_audit", [])

    if audit:
        m1, m2, m3 = st.columns(3)
        actions = list({e.get("action","") for e in audit})
        confidence_vals = [e.get("confidence") for e in audit if e.get("confidence")]
        avg_conf = sum(confidence_vals) / len(confidence_vals) if confidence_vals else None
        m1.markdown(f'<div class="metric-card"><div class="val">{len(audit)}</div><div class="lbl">Log Entries</div></div>', unsafe_allow_html=True)
        m2.markdown(f'<div class="metric-card"><div class="val">{len(actions)}</div><div class="lbl">Unique Actions</div></div>', unsafe_allow_html=True)
        m3.markdown(f'<div class="metric-card"><div class="val">{f"{avg_conf:.1f}%" if avg_conf else "—"}</div><div class="lbl">Avg AI Confidence</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        section("📋 Log Entries")
        hdr = st.columns([2.5, 1.5, 2.5, 1])
        for col, lbl in zip(hdr, ["Timestamp", "Action", "File", "Confidence"]):
            col.markdown(f"**{lbl}**")
        st.divider()
        for entry in reversed(audit):
            row = st.columns([2.5, 1.5, 2.5, 1])
            row[0].text(entry.get("timestamp","")[:19])
            row[1].text(entry.get("action",""))
            row[2].text(entry.get("file","")[:40])
            cv = entry.get("confidence")
            row[3].text(f"{cv:.1f}%" if cv else "—")

        st.divider()
        c1, c2, _ = st.columns(3)
        with c1:
            st.download_button(
                "📥 Download Audit Report (JSON)",
                json.dumps(audit, indent=2),
                "proofdoc_audit.json",
                "application/json",
                use_container_width=True,
            )
        with c2:
            if st.button("🔄 Clear Session Log", use_container_width=True):
                st.session_state.pop("last_audit", None)
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        group_header("Privacy & Confidentiality")
        st.markdown(
            """
            - All documents are processed in memory and auto-deleted when the session ends
            - No document content is stored externally or used for AI training
            - Audit logs are session-only and cleared when you close the browser
            - For persistent audit logging, connect to your firm's logging infrastructure via Integrations
            """
        )
    else:
        st.markdown(
            '<div class="empty-list">'
            '📋 No processing activity in this session yet.<br>'
            '<small>Process a document to begin building the audit trail.</small>'
            '</div>',
            unsafe_allow_html=True,
        )
        st.page_link("pages/p_doc_convert.py", label="Go to Convert & Process →")

# ── Activity Logs (placeholder) ───────────────────────────────────
with tab_activity:
    placeholder_feature(
        "📊", "Activity Logs",
        "Persistent logs of all platform activity across all sessions and users.",
        ["View full history of all document processing across the firm",
         "Filter by user, matter, date range, and action type",
         "Export activity log for compliance reporting",
         "Set retention period for activity logs"],
        ["Full activity log with pagination", "Filtered views by user / matter / date",
         "CSV/PDF compliance export", "Activity report per user"],
    )

# ── User Access Logs (placeholder) ────────────────────────────────
with tab_access:
    placeholder_feature(
        "🔐", "User Access Logs",
        "Track who accessed which documents, matters, and sections, and when.",
        ["Log all user logins and page access events",
         "Identify unusual access patterns (off-hours, high volume)",
         "Track access to restricted matters or ethical-wall documents",
         "Generate user access report for security review"],
        ["User access history timeline", "Unusual access flag report",
         "Restricted matter access log", "Security review export"],
    )
