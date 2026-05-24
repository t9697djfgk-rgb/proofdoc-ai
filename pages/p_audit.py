import streamlit as st
import json
from utils.shared.sidebar import setup_page
from utils.shared.styles import slim_header, section
from utils.auth import require_lawyer
import utils.database as db

setup_page()
user = require_lawyer()

slim_header("📋", "Audit Trail", "Activity records, access history, and processing logs")

tab_activity, tab_session = st.tabs(["📊 Activity Log", "📋 Session Log"])

# ── Activity Log (Supabase audit_logs) ───────────────────────────
with tab_activity:
    section("📊 Platform Activity Log")

    org_id = user["organization_id"]
    logs_resp = (
        db.get_db().table("audit_logs")
        .select("*")
        .eq("organization_id", org_id)
        .order("created_at", desc=True)
        .limit(500)
        .execute()
    )
    logs = logs_resp.data or []

    if logs:
        c1, c2, c3 = st.columns(3)
        action_filter = c1.selectbox(
            "Filter by action",
            ["All"] + sorted({l["action"] for l in logs}),
            key="al_act",
        )
        actor_filter = c2.selectbox(
            "Filter by actor",
            ["All"] + sorted({l.get("actor_name", "") for l in logs if l.get("actor_name")}),
            key="al_actor",
        )
        res_filter = c3.selectbox(
            "Resource type",
            ["All"] + sorted({l.get("resource_type", "") for l in logs if l.get("resource_type")}),
            key="al_res",
        )

        shown = [
            l for l in logs
            if (action_filter == "All" or l["action"] == action_filter)
            and (actor_filter == "All" or l.get("actor_name") == actor_filter)
            and (res_filter == "All" or l.get("resource_type") == res_filter)
        ]

        m1, m2, m3 = st.columns(3)
        m1.metric("Total Entries", len(logs))
        m2.metric("Filtered", len(shown))
        m3.metric("Unique Actors", len({l.get("actor_name","") for l in shown if l.get("actor_name")}))
        st.divider()

        h = st.columns([2, 2, 2, 3, 1])
        for col, lbl in zip(h, ["Time", "Actor", "Action", "Resource", "Details"]):
            col.markdown(f"**{lbl}**")
        st.divider()

        for l in shown:
            r = st.columns([2, 2, 2, 3, 1])
            r[0].caption(str(l.get("created_at", ""))[:16].replace("T", " "))
            r[1].text(l.get("actor_name", "—") or "—")
            r[2].markdown(f"`{l.get('action', '')}`")
            rid = l.get("resource_id") or ""
            r[3].text(f"{l.get('resource_type','')} {rid[:12] if rid else ''}")
            meta = l.get("metadata") or {}
            if meta and r[4].button("···", key=f"al_meta_{l['id']}", help="Show details"):
                st.session_state[f"al_show_{l['id']}"] = not st.session_state.get(f"al_show_{l['id']}", False)
            if st.session_state.get(f"al_show_{l['id']}"):
                st.code(json.dumps(meta, indent=2), language="json")

        st.caption(f"Showing {len(shown)} of {len(logs)} entries")

        st.markdown("<br>", unsafe_allow_html=True)
        dl_data = json.dumps(shown, indent=2, default=str)
        st.download_button(
            "📥 Export Filtered Log (JSON)",
            dl_data,
            "audit_log.json",
            "application/json",
        )
    else:
        st.info("No audit log entries yet. Activity is recorded as users interact with the platform.")

# ── Session Log (in-memory, unchanged) ───────────────────────────
with tab_session:
    section("📋 This Session's Processing Log")
    st.markdown(
        "Documents processed with AI tools in this session are logged here."
    )

    audit = st.session_state.get("last_audit", [])
    if audit:
        m1, m2, m3 = st.columns(3)
        actions = list({e.get("action", "") for e in audit})
        confidence_vals = [e.get("confidence") for e in audit if e.get("confidence")]
        avg_conf = sum(confidence_vals) / len(confidence_vals) if confidence_vals else None
        m1.metric("Log Entries", len(audit))
        m2.metric("Unique Actions", len(actions))
        m3.metric("Avg AI Confidence", f"{avg_conf:.1f}%" if avg_conf else "—")

        st.markdown("<br>", unsafe_allow_html=True)
        h = st.columns([2.5, 1.5, 2.5, 1])
        for col, lbl in zip(h, ["Timestamp", "Action", "File", "Confidence"]):
            col.markdown(f"**{lbl}**")
        st.divider()
        for entry in reversed(audit):
            row = st.columns([2.5, 1.5, 2.5, 1])
            row[0].text(entry.get("timestamp", "")[:19])
            row[1].text(entry.get("action", ""))
            row[2].text(entry.get("file", "")[:40])
            cv = entry.get("confidence")
            row[3].text(f"{cv:.1f}%" if cv else "—")

        st.divider()
        c1, c2, _ = st.columns(3)
        c1.download_button(
            "📥 Download Session Log (JSON)",
            json.dumps(audit, indent=2),
            "elawfirm_session_audit.json",
            "application/json",
            use_container_width=True,
        )
        if c2.button("🔄 Clear Session Log", use_container_width=True):
            st.session_state.pop("last_audit", None)
            st.rerun()
    else:
        st.markdown(
            '<div style="text-align:center;color:#94a3b8;padding:2rem">'
            '📋 No processing activity in this session yet.<br>'
            '<small>Process a document to begin building the log.</small>'
            '</div>',
            unsafe_allow_html=True,
        )
        st.page_link("pages/p_doc_convert.py", label="Go to Convert & Process →")
