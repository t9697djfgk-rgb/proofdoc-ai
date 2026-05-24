import streamlit as st
import json
from utils.shared.sidebar import setup_page
from utils.shared.styles import slim_header, section
from utils.auth import require_lawyer
import utils.database as db

api_key = setup_page()
user = require_lawyer()

slim_header("📋", "Audit Trail", "Activity records, access history, and processing logs")

tab_activity, tab_session = st.tabs(["📊 Activity Log", "📋 Session Log"])

# ── Activity Log (Supabase audit_logs) ───────────────────────────
with tab_activity:
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
        # Stats banner
        unique_actors = len({l.get("actor_name", "") for l in logs if l.get("actor_name")})
        unique_actions = len({l.get("action", "") for l in logs})
        st.markdown(
            f"""<div style="display:flex;gap:1rem;margin-bottom:1.2rem;flex-wrap:wrap">
              <div style="flex:1;min-width:120px;background:#f0f4ff;border-radius:10px;padding:.8rem 1rem;
                          border-left:4px solid #1a2744;text-align:center">
                <div style="font-size:1.5rem;font-weight:700;color:#1a2744">{len(logs)}</div>
                <div style="font-size:.72rem;color:#64748b;text-transform:uppercase;letter-spacing:.05em">Total Entries</div>
              </div>
              <div style="flex:1;min-width:120px;background:#f0fdf4;border-radius:10px;padding:.8rem 1rem;
                          border-left:4px solid #16a34a;text-align:center">
                <div style="font-size:1.5rem;font-weight:700;color:#15803d">{unique_actors}</div>
                <div style="font-size:.72rem;color:#64748b;text-transform:uppercase;letter-spacing:.05em">Unique Actors</div>
              </div>
              <div style="flex:1;min-width:120px;background:#fffbeb;border-radius:10px;padding:.8rem 1rem;
                          border-left:4px solid #d97706;text-align:center">
                <div style="font-size:1.5rem;font-weight:700;color:#b45309">{unique_actions}</div>
                <div style="font-size:.72rem;color:#64748b;text-transform:uppercase;letter-spacing:.05em">Action Types</div>
              </div>
              <div style="flex:1;min-width:120px;background:#fef2f2;border-radius:10px;padding:.8rem 1rem;
                          border-left:4px solid #dc2626;text-align:center">
                <div style="font-size:1.5rem;font-weight:700;color:#b91c1c">{str(logs[0].get("created_at",""))[:10]}</div>
                <div style="font-size:.72rem;color:#64748b;text-transform:uppercase;letter-spacing:.05em">Latest Entry</div>
              </div>
            </div>""",
            unsafe_allow_html=True,
        )

        # Filters
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

        st.caption(f"Showing **{len(shown)}** of {len(logs)} entries")
        st.markdown("<br>", unsafe_allow_html=True)

        # Action colour map
        ACTION_COLORS = {
            "LOGIN":     ("#16a34a", "#f0fdf4"),
            "LOGOUT":    ("#64748b", "#f8fafc"),
            "CREATE":    ("#2563eb", "#eff6ff"),
            "UPDATE":    ("#d97706", "#fffbeb"),
            "DELETE":    ("#dc2626", "#fef2f2"),
            "UPLOAD":    ("#7c3aed", "#f5f3ff"),
            "DOWNLOAD":  ("#0891b2", "#ecfeff"),
            "VIEW":      ("#475569", "#f1f5f9"),
        }

        for l in shown:
            action = l.get("action", "")
            action_root = action.split("_")[0].upper()
            fg, bg = ACTION_COLORS.get(action_root, ("#1a2744", "#f1f5f9"))
            ts = str(l.get("created_at", ""))[:16].replace("T", " ")
            actor = l.get("actor_name", "System") or "System"
            res_type = l.get("resource_type", "") or ""
            res_id = l.get("resource_id") or ""
            meta = l.get("metadata") or {}

            st.markdown(
                f"""<div style="background:{bg};border-radius:8px;padding:.65rem 1rem;
                              margin-bottom:.35rem;border-left:3px solid {fg};
                              display:flex;align-items:center;gap:1rem;flex-wrap:wrap">
                  <span style="font-size:.7rem;font-weight:700;color:{fg};
                               background:white;padding:.2rem .6rem;border-radius:20px;
                               border:1px solid {fg};white-space:nowrap">{action}</span>
                  <span style="font-size:.82rem;font-weight:600;color:#1a2744">{actor}</span>
                  <span style="font-size:.78rem;color:#64748b">{res_type} {res_id[:10] if res_id else ""}</span>
                  <span style="margin-left:auto;font-size:.72rem;color:#94a3b8;white-space:nowrap">{ts}</span>
                </div>""",
                unsafe_allow_html=True,
            )
            if meta and st.button("···", key=f"al_meta_{l['id']}", help="Show metadata"):
                st.session_state[f"al_show_{l['id']}"] = not st.session_state.get(f"al_show_{l['id']}", False)
            if st.session_state.get(f"al_show_{l['id']}"):
                st.code(json.dumps(meta, indent=2), language="json")

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

# ── Session Log (in-memory) ───────────────────────────────────────
with tab_session:
    section("📋 This Session's Processing Log")
    st.markdown("Documents processed with AI tools in this session are logged here.")

    audit = st.session_state.get("last_audit", [])
    if audit:
        confidence_vals = [e.get("confidence") for e in audit if e.get("confidence")]
        avg_conf = sum(confidence_vals) / len(confidence_vals) if confidence_vals else None
        actions = list({e.get("action", "") for e in audit})

        st.markdown(
            f"""<div style="display:flex;gap:1rem;margin-bottom:1.2rem;flex-wrap:wrap">
              <div style="flex:1;min-width:100px;background:#f0f4ff;border-radius:10px;
                          padding:.8rem 1rem;border-left:4px solid #1a2744;text-align:center">
                <div style="font-size:1.4rem;font-weight:700;color:#1a2744">{len(audit)}</div>
                <div style="font-size:.72rem;color:#64748b;text-transform:uppercase;letter-spacing:.05em">Log Entries</div>
              </div>
              <div style="flex:1;min-width:100px;background:#f5f3ff;border-radius:10px;
                          padding:.8rem 1rem;border-left:4px solid #7c3aed;text-align:center">
                <div style="font-size:1.4rem;font-weight:700;color:#6d28d9">{len(actions)}</div>
                <div style="font-size:.72rem;color:#64748b;text-transform:uppercase;letter-spacing:.05em">Unique Actions</div>
              </div>
              <div style="flex:1;min-width:100px;background:#f0fdf4;border-radius:10px;
                          padding:.8rem 1rem;border-left:4px solid #16a34a;text-align:center">
                <div style="font-size:1.4rem;font-weight:700;color:#15803d">{f"{avg_conf:.0f}%" if avg_conf else "—"}</div>
                <div style="font-size:.72rem;color:#64748b;text-transform:uppercase;letter-spacing:.05em">Avg Confidence</div>
              </div>
            </div>""",
            unsafe_allow_html=True,
        )

        for entry in reversed(audit):
            ts = entry.get("timestamp", "")[:16]
            action = entry.get("action", "")
            fname = entry.get("file", "")[:50]
            cv = entry.get("confidence")
            conf_str = f"{cv:.0f}%" if cv else "—"
            conf_color = "#16a34a" if cv and cv >= 80 else "#d97706" if cv else "#94a3b8"

            st.markdown(
                f"""<div style="background:#f8fafc;border-radius:8px;padding:.6rem 1rem;
                              margin-bottom:.3rem;border-left:3px solid #c9a84c;
                              display:flex;align-items:center;gap:1rem;flex-wrap:wrap">
                  <span style="font-size:.7rem;background:#1a2744;color:white;padding:.2rem .5rem;
                               border-radius:4px;white-space:nowrap">{action}</span>
                  <span style="font-size:.82rem;color:#334155">{fname}</span>
                  <span style="margin-left:auto;font-size:.78rem;font-weight:700;color:{conf_color}">{conf_str}</span>
                  <span style="font-size:.72rem;color:#94a3b8;white-space:nowrap">{ts}</span>
                </div>""",
                unsafe_allow_html=True,
            )

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
