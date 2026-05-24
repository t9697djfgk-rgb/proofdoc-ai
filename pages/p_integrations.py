"""
p_integrations.py — Integrations page for eLawFirm.
Outer tabs: Communication, Storage, E-Signature, Productivity, Legal Research, Finance, Automation & Security.
Inner bottom tabs (page level): Connected, Request Integration.
"""
from __future__ import annotations

import base64
import json
import time
from datetime import datetime, timezone, timedelta

import streamlit as st

from utils.shared.sidebar import setup_page
from utils.shared.styles import inject_css, slim_header, section
from utils.auth import require_lawyer, get_current_user

# ── page bootstrap ──────────────────────────────────────────────────────────
api_key = setup_page()
user = require_lawyer()
slim_header("🔗", "Integrations", "Connect eLawFirm to your tools")
inject_css()

# ── session-state init ───────────────────────────────────────────────────────
for _k in [
    "int_email", "int_gcal", "int_gdrive", "int_onedrive", "int_dropbox",
    "int_docusign", "int_adobe", "int_westlaw", "int_lexisnexis",
    "int_xero", "int_qbo", "int_zapier", "int_make", "int_saml",
    "int_requests",
]:
    if _k not in st.session_state:
        st.session_state[_k] = None if _k != "int_requests" else []

# OneDrive device-code flow state
if "od_device_info" not in st.session_state:
    st.session_state.od_device_info = None
if "zapier_history" not in st.session_state:
    st.session_state.zapier_history = []
if "make_history" not in st.session_state:
    st.session_state.make_history = []

# ── helper: status badge HTML ────────────────────────────────────────────────
def _badge(key: str) -> str:
    configured = st.session_state.get(key) is not None
    if configured:
        return '<span style="font-size:.68rem;font-weight:700;color:#16a34a;background:#f0fdf4;padding:.15rem .5rem;border-radius:20px;border:1px solid #16a34a40">● Connected</span>'
    return '<span style="font-size:.68rem;font-weight:700;color:#94a3b8;background:#f1f5f9;padding:.15rem .5rem;border-radius:20px;border:1px solid #94a3b840">◌ Not Configured</span>'


def _card_header(icon: str, name: str, key: str) -> None:
    st.markdown(
        f"""<div style="display:flex;align-items:center;gap:.8rem;margin-bottom:.6rem">
          <span style="font-size:1.6rem">{icon}</span>
          <div>
            <div style="font-weight:700;color:#1a2744;font-size:.95rem">{name}</div>
            {_badge(key)}
          </div>
        </div>""",
        unsafe_allow_html=True,
    )


def _features(*bullets: str) -> None:
    items = "".join(f"<li style='font-size:.78rem;color:#475569;margin:.1rem 0'>{b}</li>" for b in bullets)
    st.markdown(f"<ul style='margin:.3rem 0 .7rem;padding-left:1.1rem'>{items}</ul>", unsafe_allow_html=True)


def _card_wrap_open(key: str) -> None:
    configured = st.session_state.get(key) is not None
    border_color = "#16a34a" if configured else "#e2e8f0"
    st.markdown(
        f'<div style="background:white;border:1px solid #e2e8f0;border-radius:12px;'
        f'padding:1.1rem 1.2rem;margin-bottom:.8rem;border-top:3px solid {border_color}">',
        unsafe_allow_html=True,
    )


def _card_wrap_close() -> None:
    st.markdown("</div>", unsafe_allow_html=True)


# ── stats banner ─────────────────────────────────────────────────────────────
INT_KEYS = [
    "int_email", "int_gcal", "int_gdrive", "int_onedrive", "int_dropbox",
    "int_docusign", "int_adobe", "int_westlaw", "int_lexisnexis",
    "int_xero", "int_qbo", "int_zapier", "int_make", "int_saml",
]
TOTAL = 14
connected_count = sum(1 for k in INT_KEYS if st.session_state.get(k) is not None)
available_count = TOTAL  # all are available to configure
coming_soon = 0

st.markdown(
    f"""<div style="display:flex;gap:1rem;margin-bottom:1.2rem;flex-wrap:wrap">
      <div style="flex:1;min-width:120px;background:#f0f4ff;border-radius:10px;padding:.8rem 1rem;
                  border-left:4px solid #1a2744;text-align:center">
        <div style="font-size:1.4rem;font-weight:700;color:#1a2744">{TOTAL}</div>
        <div style="font-size:.72rem;color:#64748b;text-transform:uppercase;letter-spacing:.05em">Total</div>
      </div>
      <div style="flex:1;min-width:120px;background:#f0fdf4;border-radius:10px;padding:.8rem 1rem;
                  border-left:4px solid #16a34a;text-align:center">
        <div style="font-size:1.4rem;font-weight:700;color:#15803d">{connected_count}</div>
        <div style="font-size:.72rem;color:#64748b;text-transform:uppercase;letter-spacing:.05em">Connected</div>
      </div>
      <div style="flex:1;min-width:120px;background:#ecfeff;border-radius:10px;padding:.8rem 1rem;
                  border-left:4px solid #0891b2;text-align:center">
        <div style="font-size:1.4rem;font-weight:700;color:#0e7490">{available_count}</div>
        <div style="font-size:.72rem;color:#64748b;text-transform:uppercase;letter-spacing:.05em">Available Now</div>
      </div>
      <div style="flex:1;min-width:120px;background:#f1f5f9;border-radius:10px;padding:.8rem 1rem;
                  border-left:4px solid #94a3b8;text-align:center">
        <div style="font-size:1.4rem;font-weight:700;color:#475569">{coming_soon}</div>
        <div style="font-size:.72rem;color:#64748b;text-transform:uppercase;letter-spacing:.05em">Coming Soon</div>
      </div>
    </div>""",
    unsafe_allow_html=True,
)

# ── outer tabs ───────────────────────────────────────────────────────────────
(
    tab_comm, tab_store, tab_esign, tab_prod,
    tab_legal, tab_fin, tab_auto,
    tab_connected, tab_request,
) = st.tabs([
    "📧 Communication", "💾 Storage", "✍️ E-Signature", "📅 Productivity",
    "⚖️ Legal Research", "💰 Finance", "⚙️ Automation & Security",
    "✅ Connected", "💡 Request Integration",
])

# ═══════════════════════════════════════════════════════════════════════════
# TAB 1 — COMMUNICATION
# ═══════════════════════════════════════════════════════════════════════════
with tab_comm:

    # ── Email ──────────────────────────────────────────────────────────────
    section("📧 Email (SMTP)")
    _card_wrap_open("int_email")
    _card_header("📧", "Email (SMTP / Outlook)", "int_email")
    _features(
        "Send documents to clients from within eLawFirm",
        "Automated matter notifications and deadline reminders",
        "Signature request emails and client updates",
    )
    with st.expander("⚙️ Configure Email"):
        c1, c2 = st.columns(2)
        em_host = c1.text_input("SMTP Host", placeholder="smtp.gmail.com", key="cfg_em_host",
                                value=(st.session_state.int_email or {}).get("host", ""))
        em_port = c2.text_input("SMTP Port", placeholder="587", key="cfg_em_port",
                                value=str((st.session_state.int_email or {}).get("port", "")))
        c3, c4 = st.columns(2)
        em_user = c3.text_input("SMTP Username", placeholder="you@gmail.com", key="cfg_em_user",
                                value=(st.session_state.int_email or {}).get("user", ""))
        em_pass = c4.text_input("SMTP Password / App Password", type="password", key="cfg_em_pass")
        em_from = st.text_input("Sender Email", placeholder="noreply@yourfirm.com", key="cfg_em_from",
                                value=(st.session_state.int_email or {}).get("sender", ""))
        st.caption("💡 For Gmail, use an App Password (not your regular password). Enable 2FA first, then create an App Password at myaccount.google.com/apppasswords.")
        bs1, bs2 = st.columns(2)
        if bs1.button("💾 Save Email Config", key="save_email"):
            if em_host and em_port and em_user:
                st.session_state.int_email = {
                    "host": em_host, "port": int(em_port or "587"),
                    "user": em_user, "password": em_pass or (st.session_state.int_email or {}).get("password", ""),
                    "sender": em_from or em_user,
                }
                st.success("✅ Email configuration saved.")
                st.rerun()
            else:
                st.warning("Please fill in at least host, port, and username.")
        if bs2.button("🧪 Test Email Connection", key="test_email"):
            cfg = st.session_state.int_email
            if cfg:
                try:
                    import smtplib
                    from email.mime.text import MIMEText
                    current = get_current_user() or {}
                    to_addr = current.get("email", cfg["user"])
                    msg = MIMEText("This is a test email from eLawFirm.", "plain")
                    msg["Subject"] = "eLawFirm — Test Email"
                    msg["From"] = cfg["sender"]
                    msg["To"] = to_addr
                    with smtplib.SMTP(cfg["host"], cfg["port"], timeout=10) as server:
                        server.ehlo()
                        server.starttls()
                        server.login(cfg["user"], cfg["password"])
                        server.sendmail(cfg["sender"], [to_addr], msg.as_string())
                    st.success(f"✅ Test email sent to {to_addr}.")
                except Exception as e:
                    st.error(f"❌ Connection failed: {e}")
            else:
                st.warning("Save email configuration first.")

    # Send test email action (if configured)
    if st.session_state.int_email:
        st.markdown("**Actions**")
        with st.form("email_send_form"):
            to_email = st.text_input("Send To", value=(get_current_user() or {}).get("email", ""))
            subject = st.text_input("Subject", value="Document from eLawFirm")
            body = st.text_area("Message Body", height=80)
            if st.form_submit_button("📤 Send Email"):
                try:
                    import smtplib
                    from email.mime.text import MIMEText
                    cfg = st.session_state.int_email
                    msg = MIMEText(body, "plain")
                    msg["Subject"] = subject
                    msg["From"] = cfg["sender"]
                    msg["To"] = to_email
                    with smtplib.SMTP(cfg["host"], cfg["port"], timeout=10) as srv:
                        srv.ehlo(); srv.starttls()
                        srv.login(cfg["user"], cfg["password"])
                        srv.sendmail(cfg["sender"], [to_email], msg.as_string())
                    st.success(f"✅ Email sent to {to_email}.")
                except Exception as e:
                    st.error(f"❌ {e}")
    _card_wrap_close()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Calendar ───────────────────────────────────────────────────────────
    section("📅 Calendar Sync")
    _card_wrap_open("int_gcal")
    _card_header("📅", "Google Calendar / Outlook Calendar", "int_gcal")
    _features(
        "Sync court deadlines and task due dates automatically",
        "Create calendar events from matter tasks",
        "Download ICS file for any calendar app",
    )
    with st.expander("⚙️ Configure Calendar"):
        cal_provider = st.radio("Calendar Provider", ["Google Calendar", "Outlook / Microsoft 365"],
                                key="cal_provider", horizontal=True)

        if cal_provider == "Google Calendar":
            st.markdown("**Step 1 — Enter Google OAuth credentials**")
            gc_id = st.text_input("Google Client ID", key="cfg_gc_id",
                                  value=(st.session_state.int_gcal or {}).get("client_id", ""))
            gc_secret = st.text_input("Google Client Secret", type="password", key="cfg_gc_secret")
            if st.button("🔗 Get Auth URL", key="gc_auth_url_btn"):
                if gc_id:
                    from utils.integrations import gdrive_auth_url
                    # Reuse Google OAuth (same endpoint, Calendar scope)
                    from urllib.parse import urlencode
                    params = {
                        "client_id": gc_id, "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
                        "response_type": "code",
                        "scope": "https://www.googleapis.com/auth/calendar",
                        "access_type": "offline", "prompt": "consent",
                    }
                    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode(params)
                    st.session_state["gc_pending_id"] = gc_id
                    st.session_state["gc_pending_secret"] = gc_secret
                    st.info(f"**Step 2 — Open this URL, authorize, copy the code:**\n\n{url}")
                else:
                    st.warning("Enter your Client ID first.")

            gc_code = st.text_input("**Step 3 — Paste authorization code here**", key="cfg_gc_code")
            if st.button("🔄 Exchange Code (Google Calendar)", key="gc_exchange_btn"):
                pending_id = st.session_state.get("gc_pending_id", gc_id)
                pending_secret = st.session_state.get("gc_pending_secret", gc_secret)
                if pending_id and gc_code:
                    import requests as _req
                    r = _req.post("https://oauth2.googleapis.com/token", data={
                        "client_id": pending_id, "client_secret": pending_secret,
                        "code": gc_code.strip(), "redirect_uri": "urn:ietf:wg:oauth:2.0:oob",
                        "grant_type": "authorization_code",
                    }, timeout=15)
                    data = r.json()
                    if "access_token" in data:
                        st.session_state.int_gcal = {
                            "provider": "google", "client_id": pending_id,
                            "access_token": data["access_token"],
                            "refresh_token": data.get("refresh_token", ""),
                        }
                        st.success("✅ Google Calendar connected!")
                        st.rerun()
                    else:
                        st.error(f"❌ {data.get('error_description', data.get('error', 'Token exchange failed'))}")
                else:
                    st.warning("Enter Client ID and the authorization code.")

        else:  # Outlook device code
            od_cal_id = st.text_input("Microsoft App (Client) ID", key="cfg_od_cal_id",
                                      value=(st.session_state.int_gcal or {}).get("client_id", ""))
            od_cal_tenant = st.text_input("Tenant", value="common", key="cfg_od_cal_tenant")
            if st.button("📱 Start Device Auth", key="od_cal_dev_btn"):
                if od_cal_id:
                    from utils.integrations import onedrive_device_code
                    result = onedrive_device_code(od_cal_id, od_cal_tenant)
                    if "error" in result:
                        st.error(f"❌ {result['error']}")
                    else:
                        st.session_state["od_cal_device"] = result
                        st.session_state["od_cal_id_pending"] = od_cal_id
                        st.session_state["od_cal_tenant_pending"] = od_cal_tenant
                        st.info(
                            f"**Go to:** {result['verification_uri']}\n\n"
                            f"**Enter code:** `{result['user_code']}`\n\n"
                            "Then click the button below."
                        )
                else:
                    st.warning("Enter your Microsoft App ID.")

            if st.session_state.get("od_cal_device"):
                if st.button("✅ I've authorized — get token", key="od_cal_poll_btn"):
                    from utils.integrations import onedrive_poll_token
                    dev = st.session_state["od_cal_device"]
                    result = onedrive_poll_token(
                        st.session_state.get("od_cal_id_pending", od_cal_id),
                        dev["device_code"],
                        st.session_state.get("od_cal_tenant_pending", od_cal_tenant),
                    )
                    if "access_token" in result:
                        st.session_state.int_gcal = {
                            "provider": "outlook",
                            "client_id": st.session_state.get("od_cal_id_pending", od_cal_id),
                            "access_token": result["access_token"],
                        }
                        st.session_state.od_cal_device = None
                        st.success("✅ Outlook Calendar connected!")
                        st.rerun()
                    else:
                        st.error(f"❌ {result.get('error', 'Token poll failed')}")

    if st.session_state.int_gcal:
        st.markdown("**Actions**")
        ac1, ac2 = st.columns(2)
        if ac1.button("📅 Sync Upcoming Deadlines", key="cal_sync_btn"):
            try:
                from utils import database as db
                from utils.integrations import google_calendar_create, outlook_calendar_create
                tasks = db.list_tasks(status="pending") or []
                now = datetime.now(timezone.utc)
                synced = 0
                for t in tasks:
                    due = t.get("due_date") or t.get("deadline")
                    if not due:
                        continue
                    try:
                        due_dt = datetime.fromisoformat(str(due).replace("Z", "+00:00"))
                    except Exception:
                        continue
                    if due_dt < now:
                        continue
                    start_iso = due_dt.isoformat()
                    end_iso = (due_dt + timedelta(hours=1)).isoformat()
                    cfg = st.session_state.int_gcal
                    if cfg["provider"] == "google":
                        google_calendar_create(cfg["access_token"], t.get("title", "Task"),
                                               start_iso, end_iso, description=t.get("description", ""))
                    else:
                        outlook_calendar_create(cfg["access_token"], t.get("title", "Task"),
                                                start_iso, end_iso, description=t.get("description", ""))
                    synced += 1
                st.success(f"✅ Synced {synced} upcoming task(s) to calendar.")
            except Exception as e:
                st.error(f"❌ Sync failed: {e}")

        if ac2.button("📥 Download ICS File", key="cal_ics_btn"):
            try:
                from utils import database as db
                from utils.integrations import make_ics
                tasks = db.list_tasks(status="pending") or []
                events = []
                now = datetime.now(timezone.utc)
                for t in tasks:
                    due = t.get("due_date") or t.get("deadline")
                    if not due:
                        continue
                    try:
                        due_dt = datetime.fromisoformat(str(due).replace("Z", "+00:00"))
                    except Exception:
                        continue
                    if due_dt < now:
                        continue
                    events.append({
                        "title": t.get("title", "Task"),
                        "start": due_dt.isoformat(),
                        "end": (due_dt + timedelta(hours=1)).isoformat(),
                        "description": t.get("description", ""),
                        "location": "",
                    })
                ics_bytes = make_ics(events)
                st.download_button("⬇️ Download ICS", ics_bytes, "elawfirm_deadlines.ics",
                                   "text/calendar", key="dl_ics")
            except Exception as e:
                st.error(f"❌ {e}")
    _card_wrap_close()


# ═══════════════════════════════════════════════════════════════════════════
# TAB 2 — STORAGE
# ═══════════════════════════════════════════════════════════════════════════
with tab_store:

    # ── Google Drive ───────────────────────────────────────────────────────
    section("📁 Google Drive")
    _card_wrap_open("int_gdrive")
    _card_header("📁", "Google Drive", "int_gdrive")
    _features(
        "Browse and download files from Google Drive",
        "Upload documents and AI-generated outputs directly",
        "Organise files per matter using folder IDs",
    )
    with st.expander("⚙️ Configure Google Drive"):
        gd_id = st.text_input("Google Client ID", key="cfg_gd_id",
                              value=(st.session_state.int_gdrive or {}).get("client_id", ""))
        gd_secret = st.text_input("Google Client Secret", type="password", key="cfg_gd_secret")
        gd_folder = st.text_input("Default Folder ID (optional)", key="cfg_gd_folder",
                                  value=(st.session_state.int_gdrive or {}).get("folder_id", ""))
        st.caption("💡 Create a Google Cloud project at console.cloud.google.com, enable the Drive API, and create OAuth 2.0 credentials of type 'Desktop app'.")

        if st.button("🔗 Step 1: Get Auth URL", key="gd_url_btn"):
            if gd_id:
                from utils.integrations import gdrive_auth_url
                url = gdrive_auth_url(gd_id, gd_secret)
                st.session_state["gd_pending_id"] = gd_id
                st.session_state["gd_pending_secret"] = gd_secret
                st.session_state["gd_pending_folder"] = gd_folder
                st.info(f"**Open this URL, authorize, copy the code:**\n\n{url}")
            else:
                st.warning("Enter your Client ID first.")

        gd_code = st.text_input("Step 2: Paste authorization code", key="cfg_gd_code")
        if st.button("🔄 Exchange Code", key="gd_exchange_btn"):
            pid = st.session_state.get("gd_pending_id", gd_id)
            psec = st.session_state.get("gd_pending_secret", gd_secret)
            if pid and gd_code:
                from utils.integrations import gdrive_exchange_code
                result = gdrive_exchange_code(pid, psec, gd_code)
                if "access_token" in result:
                    st.session_state.int_gdrive = {
                        "client_id": pid,
                        "access_token": result["access_token"],
                        "refresh_token": result.get("refresh_token", ""),
                        "folder_id": st.session_state.get("gd_pending_folder", gd_folder),
                    }
                    st.success("✅ Google Drive connected!")
                    st.rerun()
                else:
                    st.error(f"❌ {result.get('error', 'Token exchange failed')}")
            else:
                st.warning("Enter Client ID and the authorization code.")

    if st.session_state.int_gdrive:
        st.markdown("**Actions**")
        act1, act2 = st.columns(2)
        if act1.button("📂 Browse Drive", key="gd_browse_btn"):
            from utils.integrations import gdrive_list
            cfg = st.session_state.int_gdrive
            files = gdrive_list(cfg["access_token"], folder_id=cfg.get("folder_id", ""))
            if files and "error" in (files[0] if files else {}):
                st.error(f"❌ {files[0]['error']}")
            else:
                if files:
                    import pandas as pd
                    st.dataframe(pd.DataFrame(files)[["name", "mimeType", "modifiedTime", "size"]], use_container_width=True)
                else:
                    st.info("No files found.")

        with act2.expander("⬆️ Upload to Drive"):
            up_text = st.text_area("File content (text)", key="gd_up_text")
            up_name = st.text_input("Filename", value="document.txt", key="gd_up_name")
            if st.button("Upload", key="gd_upload_btn"):
                if up_text:
                    from utils.integrations import gdrive_upload
                    cfg = st.session_state.int_gdrive
                    res = gdrive_upload(cfg["access_token"], up_name,
                                        up_text.encode(), "text/plain", cfg.get("folder_id", ""))
                    if "error" in res:
                        st.error(f"❌ {res['error']}")
                    else:
                        st.success(f"✅ Uploaded: [View in Drive]({res['url']})")
                else:
                    st.warning("Enter some text to upload.")
    _card_wrap_close()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── OneDrive ───────────────────────────────────────────────────────────
    section("☁️ OneDrive")
    _card_wrap_open("int_onedrive")
    _card_header("☁️", "OneDrive / SharePoint", "int_onedrive")
    _features(
        "Sync firm documents with Microsoft cloud storage",
        "Upload documents directly from eLawFirm",
        "Browse and access matter files from OneDrive",
    )
    with st.expander("⚙️ Configure OneDrive"):
        od_id = st.text_input("Microsoft App (Client) ID", key="cfg_od_id",
                              value=(st.session_state.int_onedrive or {}).get("client_id", ""))
        od_tenant = st.text_input("Tenant", value=(st.session_state.int_onedrive or {}).get("tenant", "common"), key="cfg_od_tenant")
        st.caption("💡 Register an app at portal.azure.com > App registrations. Set Mobile/desktop platform and add Files.ReadWrite permission.")

        if st.button("📱 Start Device Auth", key="od_dev_btn"):
            if od_id:
                from utils.integrations import onedrive_device_code
                result = onedrive_device_code(od_id, od_tenant)
                if "error" in result:
                    st.error(f"❌ {result['error']}")
                else:
                    st.session_state.od_device_info = result
                    st.session_state["od_pending_id"] = od_id
                    st.session_state["od_pending_tenant"] = od_tenant
            else:
                st.warning("Enter your App Client ID first.")

        if st.session_state.od_device_info:
            dev = st.session_state.od_device_info
            st.markdown(
                f"""<div style="background:#ecfeff;border:1px solid #a5f3fc;border-radius:8px;padding:.9rem 1.1rem;margin:.6rem 0">
                  <strong style="color:#0e7490">Authorize OneDrive Access</strong><br>
                  <span style="font-size:.85rem;color:#164e63">
                    1. Go to <strong>{dev['verification_uri']}</strong><br>
                    2. Enter code: <code style="font-size:1.1rem;font-weight:700">{dev['user_code']}</code><br>
                    3. Sign in with your Microsoft account, then click below.
                  </span>
                </div>""",
                unsafe_allow_html=True,
            )
            if st.button("✅ I've authorized — get token", key="od_poll_btn"):
                from utils.integrations import onedrive_poll_token
                result = onedrive_poll_token(
                    st.session_state.get("od_pending_id", od_id),
                    dev["device_code"],
                    st.session_state.get("od_pending_tenant", od_tenant),
                )
                if "access_token" in result:
                    st.session_state.int_onedrive = {
                        "client_id": st.session_state.get("od_pending_id", od_id),
                        "tenant": st.session_state.get("od_pending_tenant", od_tenant),
                        "access_token": result["access_token"],
                        "refresh_token": result.get("refresh_token", ""),
                    }
                    st.session_state.od_device_info = None
                    st.success("✅ OneDrive connected!")
                    st.rerun()
                elif result.get("error") == "authorization_pending":
                    st.warning("⏳ Authorization still pending. Please complete authorization in the browser first.")
                else:
                    st.error(f"❌ {result.get('error', 'Token poll failed')}")

    if st.session_state.int_onedrive:
        st.markdown("**Actions**")
        oda1, oda2 = st.columns(2)
        if oda1.button("📂 Browse OneDrive", key="od_browse_btn"):
            from utils.integrations import onedrive_list
            cfg = st.session_state.int_onedrive
            files = onedrive_list(cfg["access_token"])
            if files and "error" in (files[0] if files else {}):
                st.error(f"❌ {files[0]['error']}")
            else:
                if files:
                    import pandas as pd
                    st.dataframe(pd.DataFrame(files)[["name", "size", "lastModifiedDateTime"]], use_container_width=True)
                else:
                    st.info("No files found.")

        with oda2.expander("⬆️ Upload to OneDrive"):
            od_up_text = st.text_area("File content (text)", key="od_up_text")
            od_up_name = st.text_input("Filename", value="document.txt", key="od_up_name")
            od_up_path = st.text_input("Folder path", value="/eLawFirm", key="od_up_path")
            if st.button("Upload", key="od_upload_btn"):
                if od_up_text:
                    from utils.integrations import onedrive_upload
                    cfg = st.session_state.int_onedrive
                    res = onedrive_upload(cfg["access_token"], od_up_name,
                                          od_up_text.encode(), od_up_path)
                    if "error" in res:
                        st.error(f"❌ {res['error']}")
                    else:
                        url = res.get("url", "")
                        st.success(f"✅ Uploaded!" + (f" [View]({url})" if url else ""))
                else:
                    st.warning("Enter some text to upload.")
    _card_wrap_close()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Dropbox ────────────────────────────────────────────────────────────
    section("📦 Dropbox")
    _card_wrap_open("int_dropbox")
    _card_header("📦", "Dropbox", "int_dropbox")
    _features(
        "Import documents from your Dropbox account",
        "Auto-save AI outputs to a Dropbox folder",
        "Share documents via Dropbox links",
    )
    with st.expander("⚙️ Configure Dropbox"):
        db_token = st.text_input("Dropbox Access Token", type="password", key="cfg_db_token",
                                 value=(st.session_state.int_dropbox or {}).get("access_token", ""))
        db_folder = st.text_input("Default Folder Path", value=(st.session_state.int_dropbox or {}).get("folder_path", "/eLawFirm"),
                                  key="cfg_db_folder")
        st.caption("💡 Create an app at dropbox.com/developers > App Console. Use 'Scoped access', generate a long-lived access token.")
        dbb1, dbb2 = st.columns(2)
        if dbb1.button("💾 Save Dropbox Config", key="save_dropbox"):
            if db_token:
                st.session_state.int_dropbox = {"access_token": db_token, "folder_path": db_folder}
                st.success("✅ Dropbox configuration saved.")
                st.rerun()
            else:
                st.warning("Enter your access token.")
        if dbb2.button("🧪 Test Connection", key="test_dropbox"):
            if db_token:
                from utils.integrations import dropbox_list
                files = dropbox_list(db_token, "")
                if files and "error" in (files[0] if files else {}):
                    st.error(f"❌ {files[0]['error']}")
                else:
                    st.success(f"✅ Connected. Found {len(files)} item(s) at root.")
            else:
                st.warning("Save configuration first.")

    if st.session_state.int_dropbox:
        st.markdown("**Actions**")
        dba1, dba2 = st.columns(2)
        if dba1.button("📂 Browse Dropbox", key="db_browse_btn"):
            from utils.integrations import dropbox_list
            cfg = st.session_state.int_dropbox
            files = dropbox_list(cfg["access_token"], "")
            if files and "error" in (files[0] if files else {}):
                st.error(f"❌ {files[0]['error']}")
            elif files:
                import pandas as pd
                st.dataframe(pd.DataFrame(files)[["name", "size", ".tag"]], use_container_width=True)
            else:
                st.info("No files found.")

        with dba2.expander("⬆️ Upload to Dropbox"):
            db_up_text = st.text_area("File content (text)", key="db_up_text")
            db_up_name = st.text_input("Filename", value="document.txt", key="db_up_name")
            if st.button("Upload", key="db_upload_btn"):
                if db_up_text:
                    from utils.integrations import dropbox_upload
                    cfg = st.session_state.int_dropbox
                    res = dropbox_upload(cfg["access_token"], db_up_name,
                                         db_up_text.encode(), cfg.get("folder_path", "/"))
                    if "error" in res:
                        st.error(f"❌ {res['error']}")
                    else:
                        url = res.get("url", "")
                        st.success(f"✅ Uploaded to `{res['path']}`." + (f" [Share Link]({url})" if url else ""))
                else:
                    st.warning("Enter some text to upload.")
    _card_wrap_close()


# ═══════════════════════════════════════════════════════════════════════════
# TAB 3 — E-SIGNATURE
# ═══════════════════════════════════════════════════════════════════════════
with tab_esign:

    # ── DocuSign ───────────────────────────────────────────────────────────
    section("✍️ DocuSign")
    _card_wrap_open("int_docusign")
    _card_header("✍️", "DocuSign", "int_docusign")
    _features(
        "Send documents for legally binding electronic signature",
        "Real-time envelope status tracking",
        "View all envelopes and completion status",
    )
    with st.expander("⚙️ Configure DocuSign"):
        ds_token = st.text_input("Access Token", type="password", key="cfg_ds_token",
                                 value=(st.session_state.int_docusign or {}).get("access_token", ""))
        ds_account = st.text_input("Account ID", key="cfg_ds_account",
                                   value=(st.session_state.int_docusign or {}).get("account_id", ""))
        ds_base = st.text_input("Base URL", value=(st.session_state.int_docusign or {}).get("base_url", "https://na4.docusign.net"),
                                key="cfg_ds_base")
        st.caption("💡 Get credentials at admindemo.docusign.com (sandbox) or app.docusign.com. Go to Admin > Integrations > Apps and Keys.")
        dsb1, dsb2 = st.columns(2)
        if dsb1.button("💾 Save DocuSign Config", key="save_docusign"):
            if ds_token and ds_account:
                st.session_state.int_docusign = {
                    "access_token": ds_token, "account_id": ds_account, "base_url": ds_base
                }
                st.success("✅ DocuSign configuration saved.")
                st.rerun()
            else:
                st.warning("Enter access token and account ID.")
        if dsb2.button("🧪 Test Connection", key="test_docusign"):
            if ds_token and ds_account:
                from utils.integrations import docusign_list_envelopes
                envs = docusign_list_envelopes(ds_token, ds_account, ds_base)
                if envs and "error" in (envs[0] if envs else {}):
                    st.error(f"❌ {envs[0]['error']}")
                else:
                    st.success(f"✅ Connected. Found {len(envs)} envelope(s).")
            else:
                st.warning("Save configuration first.")

    if st.session_state.int_docusign:
        st.markdown("**Actions**")
        with st.expander("📤 Send for Signature"):
            with st.form("ds_send_form"):
                ds_doc_name = st.text_input("Document Name", value="Document.pdf")
                ds_doc_text = st.text_area("Document Content (will be encoded as PDF placeholder)", height=100)
                ds_signer_email = st.text_input("Signer Email")
                ds_signer_name = st.text_input("Signer Name")
                ds_subject = st.text_input("Email Subject", value="Please sign this document")
                if st.form_submit_button("✉️ Send Envelope"):
                    if ds_doc_text and ds_signer_email and ds_signer_name:
                        doc_b64 = base64.b64encode(ds_doc_text.encode()).decode()
                        from utils.integrations import docusign_send_envelope
                        cfg = st.session_state.int_docusign
                        res = docusign_send_envelope(cfg["access_token"], cfg["account_id"],
                                                      cfg["base_url"], ds_doc_name, doc_b64,
                                                      ds_signer_email, ds_signer_name, ds_subject)
                        if "error" in res:
                            st.error(f"❌ {res['error']}")
                        else:
                            st.success(f"✅ Envelope sent! ID: `{res['envelope_id']}` — Status: {res['status']}")
                    else:
                        st.warning("Fill in all fields.")

        if st.button("📋 Track Envelopes", key="ds_track_btn"):
            from utils.integrations import docusign_list_envelopes
            cfg = st.session_state.int_docusign
            envs = docusign_list_envelopes(cfg["access_token"], cfg["account_id"], cfg["base_url"])
            if envs and "error" in (envs[0] if envs else {}):
                st.error(f"❌ {envs[0]['error']}")
            elif envs:
                STATUS_COLORS = {"sent": "#0891b2", "completed": "#16a34a", "voided": "#dc2626",
                                  "declined": "#d97706", "delivered": "#7c3aed"}
                for e in envs:
                    color = STATUS_COLORS.get(e["status"], "#64748b")
                    st.markdown(
                        f"""<div style="background:#f8fafc;border-radius:8px;padding:.6rem 1rem;
                                      margin:.3rem 0;border-left:3px solid {color}">
                          <strong style="color:#1a2744">{e['subject'] or '(no subject)'}</strong>
                          <span style="float:right;font-size:.75rem;color:{color};font-weight:600">{e['status'].upper()}</span><br>
                          <span style="font-size:.75rem;color:#64748b">ID: {e['envelope_id']} · Created: {str(e['created'])[:10]}</span>
                        </div>""",
                        unsafe_allow_html=True,
                    )
            else:
                st.info("No envelopes found.")
    _card_wrap_close()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Adobe Sign ─────────────────────────────────────────────────────────
    section("✒️ Adobe Sign")
    _card_wrap_open("int_adobe")
    _card_header("✒️", "Adobe Sign", "int_adobe")
    _features(
        "Send documents via Adobe Sign e-signature workflow",
        "Multi-signatory support and audit certificate",
        "Track agreement status in real time",
    )
    with st.expander("⚙️ Configure Adobe Sign"):
        ab_token = st.text_input("Access Token", type="password", key="cfg_ab_token",
                                 value=(st.session_state.int_adobe or {}).get("access_token", ""))
        st.caption("💡 Get access from sign.adobe.com > Account > Adobe Sign API. Generate an integration key under API Information.")
        abb1, abb2 = st.columns(2)
        if abb1.button("💾 Save Adobe Sign Config", key="save_adobe"):
            if ab_token:
                st.session_state.int_adobe = {"access_token": ab_token}
                st.success("✅ Adobe Sign configuration saved.")
                st.rerun()
            else:
                st.warning("Enter access token.")
        if abb2.button("🧪 Test Connection", key="test_adobe"):
            if ab_token:
                from utils.integrations import adobe_sign_list
                agreements = adobe_sign_list(ab_token)
                if agreements and "error" in (agreements[0] if agreements else {}):
                    st.error(f"❌ {agreements[0]['error']}")
                else:
                    st.success(f"✅ Connected. Found {len(agreements)} agreement(s).")
            else:
                st.warning("Save configuration first.")

    if st.session_state.int_adobe:
        st.markdown("**Actions**")
        with st.expander("📤 Send for Signature"):
            with st.form("ab_send_form"):
                ab_doc_name = st.text_input("Document Name", value="Document.pdf")
                ab_doc_text = st.text_area("Document Content", height=100)
                ab_signer_email = st.text_input("Signer Email")
                ab_signer_name = st.text_input("Signer Name")
                ab_message = st.text_input("Message to Signer", value="Please review and sign this document.")
                if st.form_submit_button("✉️ Send Agreement"):
                    if ab_doc_text and ab_signer_email and ab_signer_name:
                        doc_b64 = base64.b64encode(ab_doc_text.encode()).decode()
                        from utils.integrations import adobe_sign_send
                        cfg = st.session_state.int_adobe
                        res = adobe_sign_send(cfg["access_token"], ab_doc_name, doc_b64,
                                              ab_signer_email, ab_signer_name, ab_message)
                        if "error" in res:
                            st.error(f"❌ {res['error']}")
                        else:
                            st.success(f"✅ Agreement sent! ID: `{res['agreement_id']}` — Status: {res['status']}")
                    else:
                        st.warning("Fill in all fields.")

        if st.button("📋 View Agreements", key="ab_list_btn"):
            from utils.integrations import adobe_sign_list
            cfg = st.session_state.int_adobe
            agreements = adobe_sign_list(cfg["access_token"])
            if agreements and "error" in (agreements[0] if agreements else {}):
                st.error(f"❌ {agreements[0]['error']}")
            elif agreements:
                STATUS_COLORS = {"IN_PROCESS": "#0891b2", "SIGNED": "#16a34a",
                                  "CANCELLED": "#dc2626", "EXPIRED": "#d97706"}
                for a in agreements:
                    color = STATUS_COLORS.get(a["status"], "#64748b")
                    st.markdown(
                        f"""<div style="background:#f8fafc;border-radius:8px;padding:.6rem 1rem;
                                      margin:.3rem 0;border-left:3px solid {color}">
                          <strong style="color:#1a2744">{a['name']}</strong>
                          <span style="float:right;font-size:.75rem;color:{color};font-weight:600">{a['status']}</span><br>
                          <span style="font-size:.75rem;color:#64748b">ID: {a['agreement_id']} · Created: {str(a['created'])[:10]}</span>
                        </div>""",
                        unsafe_allow_html=True,
                    )
            else:
                st.info("No agreements found.")
    _card_wrap_close()


# ═══════════════════════════════════════════════════════════════════════════
# TAB 4 — PRODUCTIVITY
# ═══════════════════════════════════════════════════════════════════════════
with tab_prod:

    # ── Microsoft Word / DOCX ─────────────────────────────────────────────
    section("📝 Microsoft Word (DOCX Export)")
    _card_wrap_open("int_word")  # No real credential needed
    st.markdown(
        """<div style="display:flex;align-items:center;gap:.8rem;margin-bottom:.6rem">
          <span style="font-size:1.6rem">📝</span>
          <div>
            <div style="font-weight:700;color:#1a2744;font-size:.95rem">Microsoft Word / Office 365</div>
            <span style="font-size:.68rem;font-weight:700;color:#0891b2;background:#ecfeff;padding:.15rem .5rem;border-radius:20px;border:1px solid #0891b240">◎ Available — No credentials needed</span>
          </div>
        </div>""",
        unsafe_allow_html=True,
    )
    _features(
        "Export any document text as a .docx Word file",
        "Basic markdown formatting preserved (headings, bullets, bold)",
        "For Office 365 cloud sync, connect OneDrive above",
    )
    st.markdown("**Export to DOCX**")
    with st.form("word_export_form"):
        wd_title = st.text_input("Document Title", placeholder="e.g. Contract Agreement")
        wd_text = st.text_area("Paste document content (plain text or markdown)", height=200,
                               placeholder="Enter or paste the document content here...")
        wd_format = st.radio("Format", ["Plain text", "Markdown"], horizontal=True)
        if st.form_submit_button("📄 Generate DOCX"):
            if wd_text:
                from utils.integrations import text_to_docx, markdown_to_docx
                if wd_format == "Markdown":
                    docx_bytes = markdown_to_docx(wd_text, title=wd_title)
                else:
                    docx_bytes = text_to_docx(wd_text, title=wd_title)
                if docx_bytes:
                    safe_name = (wd_title.strip().replace(" ", "_") or "document") + ".docx"
                    st.download_button("⬇️ Download DOCX", docx_bytes, safe_name,
                                       "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                       key="dl_docx")
                    st.success("✅ DOCX ready for download.")
            else:
                st.warning("Enter some document content first.")

    st.markdown(
        '<div style="background:#eff6ff;border:1px solid #bfdbfe;border-left:4px solid #3b82f6;'
        'border-radius:8px;padding:.7rem 1rem;margin-top:.8rem;font-size:.83rem;color:#1e40af">'
        'ℹ️ For <strong>Office 365 cloud sync</strong> (open in Word online, co-authoring), '
        'connect your <strong>OneDrive</strong> account in the Storage tab first, then upload your DOCX there.'
        '</div>',
        unsafe_allow_html=True,
    )
    _card_wrap_close()


# ═══════════════════════════════════════════════════════════════════════════
# TAB 5 — LEGAL RESEARCH
# ═══════════════════════════════════════════════════════════════════════════
with tab_legal:

    JURISDICTIONS = [
        "", "US Federal", "US - California", "US - New York", "US - Texas",
        "UK", "EU", "Canada", "Australia", "Rwanda", "South Africa", "Kenya",
    ]

    # ── Westlaw ────────────────────────────────────────────────────────────
    section("⚖️ Westlaw")
    _card_wrap_open("int_westlaw")
    _card_header("⚖️", "Westlaw", "int_westlaw")
    _features(
        "Search case law, statutes, and regulations",
        "Pull verified citations directly into your research",
        "Filter by jurisdiction and publication type",
    )
    st.markdown(
        '<div style="background:#fffbeb;border:1px solid #fde68a;border-left:4px solid #d97706;'
        'border-radius:8px;padding:.7rem 1rem;margin-bottom:.7rem;font-size:.83rem;color:#92400e">'
        '⚠️ <strong>Subscription required.</strong> Westlaw API access requires an active Westlaw subscription '
        'and API credentials from <strong>Thomson Reuters</strong>. Contact your Thomson Reuters account representative.'
        '</div>',
        unsafe_allow_html=True,
    )
    with st.expander("⚙️ Configure Westlaw"):
        wl_key = st.text_input("Westlaw API Key", type="password", key="cfg_wl_key",
                               value=(st.session_state.int_westlaw or {}).get("api_key", ""))
        st.caption("💡 Obtain your API key from the Westlaw Developer Portal or via your Thomson Reuters account.")
        wlb1, wlb2 = st.columns(2)
        if wlb1.button("💾 Save Westlaw Config", key="save_westlaw"):
            if wl_key:
                st.session_state.int_westlaw = {"api_key": wl_key}
                st.success("✅ Westlaw configuration saved.")
                st.rerun()
            else:
                st.warning("Enter your API key.")
        if wlb2.button("🧪 Test Connection", key="test_westlaw"):
            if wl_key:
                from utils.integrations import westlaw_search
                results = westlaw_search(wl_key, "contract formation", max_results=1)
                if results and "error" in (results[0] if results else {}):
                    st.error(f"❌ {results[0]['error']}")
                else:
                    st.success(f"✅ Connected. Test query returned {len(results)} result(s).")
            else:
                st.warning("Save configuration first.")

    if st.session_state.int_westlaw:
        st.markdown("**Search Westlaw**")
        with st.form("wl_search_form"):
            wl_q = st.text_input("Search Query", placeholder="e.g. breach of contract damages foreseeability")
            wl_j = st.selectbox("Jurisdiction (optional)", JURISDICTIONS)
            wl_n = st.slider("Max Results", 1, 20, 10)
            if st.form_submit_button("🔍 Search Westlaw"):
                if wl_q:
                    from utils.integrations import westlaw_search
                    cfg = st.session_state.int_westlaw
                    with st.spinner("Searching Westlaw..."):
                        results = westlaw_search(cfg["api_key"], wl_q, wl_j, wl_n)
                    if results and "error" in (results[0] if results else {}):
                        st.error(f"❌ {results[0]['error']}")
                    elif results:
                        for r in results:
                            url_link = f" — [View]({r['url']})" if r.get("url") else ""
                            st.markdown(
                                f"""<div style="background:#f8fafc;border-radius:8px;padding:.7rem 1rem;
                                              margin:.3rem 0;border-left:3px solid #1a2744">
                                  <strong style="color:#1a2744">{r.get('title', '—')}</strong>
                                  <span style="font-size:.75rem;color:#64748b;margin-left:.5rem">{r.get('citation', '')}</span>
                                  <p style="font-size:.82rem;color:#475569;margin:.3rem 0 0">{r.get('excerpt', '')[:300]}</p>
                                </div>""",
                                unsafe_allow_html=True,
                            )
                    else:
                        st.info("No results found.")
                else:
                    st.warning("Enter a search query.")
    _card_wrap_close()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── LexisNexis ─────────────────────────────────────────────────────────
    section("📚 LexisNexis")
    _card_wrap_open("int_lexisnexis")
    _card_header("📚", "LexisNexis", "int_lexisnexis")
    _features(
        "Search case law, statutes, and secondary sources",
        "Access LexisNexis+ curated legal research",
        "Filter results by jurisdiction and content type",
    )
    st.markdown(
        '<div style="background:#fffbeb;border:1px solid #fde68a;border-left:4px solid #d97706;'
        'border-radius:8px;padding:.7rem 1rem;margin-bottom:.7rem;font-size:.83rem;color:#92400e">'
        '⚠️ <strong>Subscription required.</strong> LexisNexis API access requires a LexisNexis+ '
        'subscription with API access enabled. Contact <strong>LexisNexis</strong> for developer credentials.'
        '</div>',
        unsafe_allow_html=True,
    )
    with st.expander("⚙️ Configure LexisNexis"):
        ln_key = st.text_input("LexisNexis API Key", type="password", key="cfg_ln_key",
                               value=(st.session_state.int_lexisnexis or {}).get("api_key", ""))
        st.caption("💡 Obtain your API key from the LexisNexis Developer Portal at developer.lexisnexis.com.")
        lnb1, lnb2 = st.columns(2)
        if lnb1.button("💾 Save LexisNexis Config", key="save_lexisnexis"):
            if ln_key:
                st.session_state.int_lexisnexis = {"api_key": ln_key}
                st.success("✅ LexisNexis configuration saved.")
                st.rerun()
            else:
                st.warning("Enter your API key.")
        if lnb2.button("🧪 Test Connection", key="test_lexisnexis"):
            if ln_key:
                from utils.integrations import lexisnexis_search
                results = lexisnexis_search(ln_key, "negligence", max_results=1)
                if results and "error" in (results[0] if results else {}):
                    st.error(f"❌ {results[0]['error']}")
                else:
                    st.success(f"✅ Connected. Test query returned {len(results)} result(s).")
            else:
                st.warning("Save configuration first.")

    if st.session_state.int_lexisnexis:
        st.markdown("**Search LexisNexis**")
        with st.form("ln_search_form"):
            ln_q = st.text_input("Search Query", placeholder="e.g. negligence duty of care reasonable foreseeability")
            ln_j = st.selectbox("Jurisdiction (optional)", JURISDICTIONS, key="ln_j")
            ln_n = st.slider("Max Results", 1, 20, 10, key="ln_n")
            if st.form_submit_button("🔍 Search LexisNexis"):
                if ln_q:
                    from utils.integrations import lexisnexis_search
                    cfg = st.session_state.int_lexisnexis
                    with st.spinner("Searching LexisNexis..."):
                        results = lexisnexis_search(cfg["api_key"], ln_q, ln_j, ln_n)
                    if results and "error" in (results[0] if results else {}):
                        st.error(f"❌ {results[0]['error']}")
                    elif results:
                        for r in results:
                            st.markdown(
                                f"""<div style="background:#f8fafc;border-radius:8px;padding:.7rem 1rem;
                                              margin:.3rem 0;border-left:3px solid #7c3aed">
                                  <strong style="color:#1a2744">{r.get('title', '—')}</strong>
                                  <span style="font-size:.75rem;color:#64748b;margin-left:.5rem">{r.get('citation', '')}</span>
                                  <p style="font-size:.82rem;color:#475569;margin:.3rem 0 0">{r.get('excerpt', '')[:300]}</p>
                                </div>""",
                                unsafe_allow_html=True,
                            )
                    else:
                        st.info("No results found.")
                else:
                    st.warning("Enter a search query.")
    _card_wrap_close()


# ═══════════════════════════════════════════════════════════════════════════
# TAB 6 — FINANCE
# ═══════════════════════════════════════════════════════════════════════════
with tab_fin:

    # ── Xero ───────────────────────────────────────────────────────────────
    section("💰 Xero")
    _card_wrap_open("int_xero")
    _card_header("💰", "Xero", "int_xero")
    _features(
        "Export invoices and time entries to Xero",
        "Sync client billing data automatically",
        "View and manage Xero invoices from eLawFirm",
    )
    with st.expander("⚙️ Configure Xero"):
        xr_id = st.text_input("Xero Client ID", key="cfg_xr_id",
                              value=(st.session_state.int_xero or {}).get("client_id", ""))
        xr_secret = st.text_input("Xero Client Secret", type="password", key="cfg_xr_secret")
        xr_redirect = st.text_input("Redirect URI", value="https://app.elaw.firm/callback", key="cfg_xr_redirect")
        st.caption("💡 Register your app at developer.xero.com. Set redirect URI to match what you enter here.")

        if st.button("🔗 Step 1: Get Xero Auth URL", key="xr_url_btn"):
            if xr_id:
                from utils.integrations import xero_auth_url
                url = xero_auth_url(xr_id, xr_redirect)
                st.session_state["xr_pending_id"] = xr_id
                st.session_state["xr_pending_secret"] = xr_secret
                st.session_state["xr_pending_redirect"] = xr_redirect
                st.info(f"**Open this URL and authorize:**\n\n{url}")
            else:
                st.warning("Enter Xero Client ID first.")

        xr_code = st.text_input("Step 2: Paste authorization code from redirect URL", key="cfg_xr_code")
        if st.button("🔄 Exchange Code", key="xr_exchange_btn"):
            pid = st.session_state.get("xr_pending_id", xr_id)
            psec = st.session_state.get("xr_pending_secret", xr_secret)
            predir = st.session_state.get("xr_pending_redirect", xr_redirect)
            if pid and xr_code:
                from utils.integrations import xero_exchange_code, xero_get_tenants
                result = xero_exchange_code(pid, psec, xr_code, predir)
                if "access_token" in result:
                    tenants = xero_get_tenants(result["access_token"])
                    st.session_state.int_xero = {
                        "client_id": pid, "access_token": result["access_token"],
                        "refresh_token": result.get("refresh_token", ""),
                        "tenants": tenants,
                        "tenant_id": tenants[0]["tenantId"] if tenants and "tenantId" in tenants[0] else "",
                    }
                    st.success(f"✅ Xero connected! Found {len(tenants)} organisation(s).")
                    st.rerun()
                else:
                    st.error(f"❌ {result.get('error', 'Token exchange failed')}")
            else:
                st.warning("Enter Client ID and authorization code.")

        # Tenant selector (if connected)
        if st.session_state.int_xero and st.session_state.int_xero.get("tenants"):
            tenants = st.session_state.int_xero["tenants"]
            tenant_names = [t["tenantName"] for t in tenants if "tenantName" in t]
            if tenant_names:
                sel = st.selectbox("Select Organisation", tenant_names, key="xr_tenant_sel")
                if st.button("Use This Organisation", key="xr_tenant_btn"):
                    for t in tenants:
                        if t.get("tenantName") == sel:
                            st.session_state.int_xero["tenant_id"] = t["tenantId"]
                            st.success(f"✅ Using organisation: {sel}")
                            st.rerun()

    if st.session_state.int_xero:
        st.markdown("**Actions**")
        xra1, xra2 = st.columns(2)
        if xra1.button("📤 Export Invoices to Xero", key="xr_export_btn"):
            try:
                from utils import database as db
                from utils.integrations import xero_create_invoice
                invoices = db.list_invoices() or []
                cfg = st.session_state.int_xero
                tid = cfg.get("tenant_id", "")
                exported = 0
                errors = []
                for inv in invoices[:10]:
                    line_items = [{"description": inv.get("description", "Legal Services"),
                                   "quantity": 1, "unit_amount": float(inv.get("amount", 0))}]
                    due = inv.get("due_date") or (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
                    res = xero_create_invoice(cfg["access_token"], tid,
                                              inv.get("client_name", "Client"), line_items,
                                              str(due)[:10], inv.get("invoice_number", f"INV-{inv.get('id', '')}"))
                    if "error" in res:
                        errors.append(res["error"])
                    else:
                        exported += 1
                if errors:
                    st.warning(f"⚠️ Exported {exported}, {len(errors)} error(s): {errors[0]}")
                else:
                    st.success(f"✅ Exported {exported} invoice(s) to Xero.")
            except Exception as e:
                st.error(f"❌ {e}")

        if xra2.button("📋 View Xero Invoices", key="xr_list_btn"):
            from utils.integrations import xero_list_invoices
            cfg = st.session_state.int_xero
            invoices = xero_list_invoices(cfg["access_token"], cfg.get("tenant_id", ""))
            if invoices and "error" in (invoices[0] if invoices else {}):
                st.error(f"❌ {invoices[0]['error']}")
            elif invoices:
                import pandas as pd
                st.dataframe(pd.DataFrame(invoices)[["invoice_number", "contact", "amount", "status", "due_date"]], use_container_width=True)
            else:
                st.info("No invoices found.")
    _card_wrap_close()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── QuickBooks ─────────────────────────────────────────────────────────
    section("💳 QuickBooks Online")
    _card_wrap_open("int_qbo")
    _card_header("💳", "QuickBooks Online", "int_qbo")
    _features(
        "Export invoices to QuickBooks automatically",
        "Sync client and billing data across platforms",
        "View QuickBooks invoices from eLawFirm",
    )
    with st.expander("⚙️ Configure QuickBooks"):
        qb_id = st.text_input("QuickBooks Client ID", key="cfg_qb_id",
                              value=(st.session_state.int_qbo or {}).get("client_id", ""))
        qb_secret = st.text_input("QuickBooks Client Secret", type="password", key="cfg_qb_secret")
        qb_redirect = st.text_input("Redirect URI", placeholder="https://yourapp.com/callback", key="cfg_qb_redirect",
                                    value=(st.session_state.int_qbo or {}).get("redirect_uri", ""))
        st.caption("💡 Create an app at developer.intuit.com. Use OAuth 2.0 with the Accounting scope.")

        if st.button("🔗 Step 1: Get QuickBooks Auth URL", key="qb_url_btn"):
            if qb_id and qb_redirect:
                from utils.integrations import qbo_auth_url
                url = qbo_auth_url(qb_id, qb_redirect)
                st.session_state["qb_pending_id"] = qb_id
                st.session_state["qb_pending_secret"] = qb_secret
                st.session_state["qb_pending_redirect"] = qb_redirect
                st.info(f"**Open this URL and authorize:**\n\n{url}")
            else:
                st.warning("Enter Client ID and Redirect URI first.")

        qb_code = st.text_input("Step 2: Paste authorization code", key="cfg_qb_code")
        qb_realm = st.text_input("Step 2b: Paste Realm ID (from redirect URL)", key="cfg_qb_realm",
                                 value=(st.session_state.int_qbo or {}).get("realm_id", ""))
        if st.button("🔄 Exchange Code", key="qb_exchange_btn"):
            pid = st.session_state.get("qb_pending_id", qb_id)
            psec = st.session_state.get("qb_pending_secret", qb_secret)
            predir = st.session_state.get("qb_pending_redirect", qb_redirect)
            if pid and qb_code and qb_realm:
                from utils.integrations import qbo_exchange_code
                result = qbo_exchange_code(pid, psec, qb_code, predir)
                if "access_token" in result:
                    st.session_state.int_qbo = {
                        "client_id": pid, "access_token": result["access_token"],
                        "refresh_token": result.get("refresh_token", ""),
                        "realm_id": qb_realm, "redirect_uri": predir,
                    }
                    st.success("✅ QuickBooks connected!")
                    st.rerun()
                else:
                    st.error(f"❌ {result.get('error', 'Token exchange failed')}")
            else:
                st.warning("Enter Client ID, authorization code, and Realm ID.")

    if st.session_state.int_qbo:
        st.markdown("**Actions**")
        qba1, qba2 = st.columns(2)
        if qba1.button("📤 Export Invoices to QuickBooks", key="qb_export_btn"):
            try:
                from utils import database as db
                from utils.integrations import qbo_create_invoice
                invoices = db.list_invoices() or []
                cfg = st.session_state.int_qbo
                exported = 0
                errors = []
                for inv in invoices[:10]:
                    line_items = [{"description": inv.get("description", "Legal Services"),
                                   "quantity": 1, "unit_amount": float(inv.get("amount", 0))}]
                    due = inv.get("due_date") or (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
                    res = qbo_create_invoice(cfg["access_token"], cfg["realm_id"],
                                             inv.get("client_name", "Client"), line_items,
                                             str(due)[:10],
                                             inv.get("invoice_number", f"INV-{inv.get('id', '')}"))
                    if "error" in res:
                        errors.append(res["error"])
                    else:
                        exported += 1
                if errors:
                    st.warning(f"⚠️ Exported {exported}, {len(errors)} error(s): {errors[0]}")
                else:
                    st.success(f"✅ Exported {exported} invoice(s) to QuickBooks.")
            except Exception as e:
                st.error(f"❌ {e}")

        if qba2.button("📋 View QuickBooks Invoices", key="qb_list_btn"):
            from utils.integrations import qbo_list_invoices
            cfg = st.session_state.int_qbo
            invoices = qbo_list_invoices(cfg["access_token"], cfg["realm_id"])
            if invoices and "error" in (invoices[0] if invoices else {}):
                st.error(f"❌ {invoices[0]['error']}")
            elif invoices:
                import pandas as pd
                st.dataframe(pd.DataFrame(invoices)[["doc_number", "customer", "amount", "balance", "due_date"]], use_container_width=True)
            else:
                st.info("No invoices found.")
    _card_wrap_close()


# ═══════════════════════════════════════════════════════════════════════════
# TAB 7 — AUTOMATION & SECURITY
# ═══════════════════════════════════════════════════════════════════════════
with tab_auto:

    # ── Zapier ────────────────────────────────────────────────────────────
    section("🔌 Zapier")
    _card_wrap_open("int_zapier")
    _card_header("🔌", "Zapier", "int_zapier")
    _features(
        "Trigger custom Zapier workflows from eLawFirm events",
        "Connect to 5,000+ apps with no-code automation",
        "Log trigger history for audit purposes",
    )
    with st.expander("⚙️ Configure Zapier"):
        zp_url = st.text_input("Zapier Webhook URL", key="cfg_zp_url",
                               value=(st.session_state.int_zapier or {}).get("webhook_url", ""),
                               placeholder="https://hooks.zapier.com/hooks/catch/...")
        st.caption("💡 In Zapier, create a Zap with 'Webhooks by Zapier' as the trigger, choose 'Catch Hook', copy the webhook URL.")
        zpb1, zpb2 = st.columns(2)
        if zpb1.button("💾 Save Zapier Config", key="save_zapier"):
            if zp_url:
                st.session_state.int_zapier = {"webhook_url": zp_url}
                st.success("✅ Zapier configuration saved.")
                st.rerun()
            else:
                st.warning("Enter webhook URL.")
        if zpb2.button("🧪 Test Webhook", key="test_zapier"):
            if zp_url:
                from utils.integrations import webhook_test
                res = webhook_test(zp_url)
                if res.get("success"):
                    st.success(f"✅ Webhook responded in {res['latency_ms']}ms (HTTP {res['status_code']}).")
                else:
                    _zp_err = res.get("error") or f"HTTP {res.get('status_code', '?')}"
                    st.error(f"❌ Webhook test failed: {_zp_err}")
            else:
                st.warning("Save configuration first.")

    if st.session_state.int_zapier:
        st.markdown("**Actions**")
        EVENT_TYPES = ["matter_created", "invoice_sent", "task_overdue", "document_uploaded", "client_added"]
        zp_event = st.selectbox("Event Type", EVENT_TYPES, key="zp_event_sel")
        zp_payload_preview = {
            "event": zp_event,
            "source": "eLawFirm",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "data": {"firm": "eLawFirm", "triggered_by": (user or {}).get("email", "")},
        }
        with st.expander("📋 Payload Preview"):
            st.json(zp_payload_preview)

        if st.button("⚡ Trigger Zapier Event", key="zp_trigger_btn"):
            from utils.integrations import zapier_trigger
            cfg = st.session_state.int_zapier
            res = zapier_trigger(cfg["webhook_url"], zp_event, zp_payload_preview["data"])
            if res.get("success"):
                st.success(f"✅ Zapier triggered successfully (HTTP {res['status_code']}).")
                st.session_state.zapier_history.insert(0, {
                    "event": zp_event,
                    "time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "status": "success",
                })
            else:
                _zp_tr_err = res.get("error") or f"HTTP {res.get('status_code', '?')}"
                st.error(f"❌ {_zp_tr_err}")
                st.session_state.zapier_history.insert(0, {
                    "event": zp_event,
                    "time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "status": "failed",
                })

        if st.session_state.zapier_history:
            section("📜 Recent Trigger History")
            for h in st.session_state.zapier_history[:5]:
                color = "#16a34a" if h["status"] == "success" else "#dc2626"
                st.markdown(
                    f'<div style="background:#f8fafc;border-radius:6px;padding:.4rem .8rem;margin:.2rem 0;'
                    f'border-left:3px solid {color};font-size:.8rem">'
                    f'<strong>{h["event"]}</strong> · {h["time"]} · '
                    f'<span style="color:{color}">{h["status"]}</span></div>',
                    unsafe_allow_html=True,
                )
    _card_wrap_close()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Make ──────────────────────────────────────────────────────────────
    section("🔄 Make (Integromat)")
    _card_wrap_open("int_make")
    _card_header("🔄", "Make (Integromat)", "int_make")
    _features(
        "Trigger Make scenarios from eLawFirm events",
        "Connect to hundreds of apps via Make's visual editor",
        "Log trigger history for audit purposes",
    )
    with st.expander("⚙️ Configure Make"):
        mk_url = st.text_input("Make Webhook URL", key="cfg_mk_url",
                               value=(st.session_state.int_make or {}).get("webhook_url", ""),
                               placeholder="https://hook.eu1.make.com/...")
        st.caption("💡 In Make, add a 'Webhooks > Custom webhook' module as the trigger, create a webhook, copy the URL.")
        mkb1, mkb2 = st.columns(2)
        if mkb1.button("💾 Save Make Config", key="save_make"):
            if mk_url:
                st.session_state.int_make = {"webhook_url": mk_url}
                st.success("✅ Make configuration saved.")
                st.rerun()
            else:
                st.warning("Enter webhook URL.")
        if mkb2.button("🧪 Test Webhook", key="test_make"):
            if mk_url:
                from utils.integrations import webhook_test
                res = webhook_test(mk_url)
                if res.get("success"):
                    st.success(f"✅ Webhook responded in {res['latency_ms']}ms (HTTP {res['status_code']}).")
                else:
                    _mk_err = res.get("error") or f"HTTP {res.get('status_code', '?')}"
                    st.error(f"❌ Test failed: {_mk_err}")
            else:
                st.warning("Save configuration first.")

    if st.session_state.int_make:
        st.markdown("**Actions**")
        mk_payload = {
            "source": "eLawFirm",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "triggered_by": (user or {}).get("email", ""),
            "event": "manual_trigger",
        }
        with st.expander("📋 Payload Preview"):
            st.json(mk_payload)

        if st.button("⚡ Trigger Make Scenario", key="mk_trigger_btn"):
            from utils.integrations import make_trigger
            cfg = st.session_state.int_make
            res = make_trigger(cfg["webhook_url"], mk_payload)
            if res.get("success"):
                st.success(f"✅ Make scenario triggered (HTTP {res['status_code']}).")
                st.session_state.make_history.insert(0, {
                    "time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "status": "success",
                })
            else:
                _mk_tr_err = res.get("error") or f"HTTP {res.get('status_code', '?')}"
                st.error(f"❌ {_mk_tr_err}")
                st.session_state.make_history.insert(0, {
                    "time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
                    "status": "failed",
                })

        if st.session_state.make_history:
            section("📜 Recent Trigger History")
            for h in st.session_state.make_history[:5]:
                color = "#16a34a" if h["status"] == "success" else "#dc2626"
                st.markdown(
                    f'<div style="background:#f8fafc;border-radius:6px;padding:.4rem .8rem;margin:.2rem 0;'
                    f'border-left:3px solid {color};font-size:.8rem">'
                    f'{h["time"]} · <span style="color:{color}">{h["status"]}</span></div>',
                    unsafe_allow_html=True,
                )
    _card_wrap_close()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── SSO / SAML ────────────────────────────────────────────────────────
    section("🔐 Single Sign-On (SSO / SAML 2.0)")
    _card_wrap_open("int_saml")
    _card_header("🔐", "Single Sign-On (SSO / SAML 2.0)", "int_saml")
    _features(
        "SAML 2.0 SSO with Azure AD, Okta, Google Workspace",
        "Download SP metadata XML for your identity provider",
        "Test SAML responses and validate user attributes",
    )
    with st.expander("⚙️ Configure SSO / SAML"):
        sm_idp = st.text_input("IdP SSO URL", key="cfg_sm_idp",
                               value=(st.session_state.int_saml or {}).get("idp_sso_url", ""),
                               placeholder="https://login.microsoftonline.com/.../saml2")
        sm_entity = st.text_input("SP Entity ID", key="cfg_sm_entity",
                                  value=(st.session_state.int_saml or {}).get("sp_entity_id", ""),
                                  placeholder="https://app.elaw.firm")
        sm_acs = st.text_input("ACS URL (Assertion Consumer Service)", key="cfg_sm_acs",
                               value=(st.session_state.int_saml or {}).get("acs_url", ""),
                               placeholder="https://app.elaw.firm/auth/saml/callback")
        sm_cert = st.text_area("IdP Certificate (PEM, optional — for response validation)", key="cfg_sm_cert",
                               value=(st.session_state.int_saml or {}).get("idp_cert", ""), height=80)
        sm_sp_cert = st.text_area("SP Certificate (PEM, optional — for metadata)", key="cfg_sm_sp_cert", height=80)

        smb1, smb2 = st.columns(2)
        if smb1.button("💾 Save SSO Config", key="save_saml"):
            if sm_idp and sm_entity and sm_acs:
                st.session_state.int_saml = {
                    "idp_sso_url": sm_idp, "sp_entity_id": sm_entity,
                    "acs_url": sm_acs, "idp_cert": sm_cert, "sp_cert": sm_sp_cert,
                }
                st.success("✅ SSO configuration saved.")
                st.rerun()
            else:
                st.warning("Enter IdP SSO URL, SP Entity ID, and ACS URL.")

        if smb2.button("📥 Download SP Metadata XML", key="saml_metadata_btn"):
            if sm_entity and sm_acs:
                from utils.integrations import saml_generate_metadata
                xml_str = saml_generate_metadata(sm_entity, sm_acs, sm_sp_cert)
                st.download_button("⬇️ Download metadata.xml", xml_str.encode(),
                                   "elawfirm_sp_metadata.xml", "application/xml", key="dl_metadata")
            else:
                st.warning("Enter SP Entity ID and ACS URL first.")

        st.markdown("---")
        st.markdown("**🧪 Test SAML Response**")
        sm_resp = st.text_area("Paste base64-encoded SAML response here", key="cfg_sm_resp", height=100)
        if st.button("Parse SAML Response", key="saml_parse_btn"):
            if sm_resp:
                from utils.integrations import saml_parse_response
                parsed = saml_parse_response(sm_resp.strip(), sm_cert)
                if "error" in parsed:
                    st.error(f"❌ {parsed['error']}")
                else:
                    st.success(f"✅ Parsed successfully!")
                    st.json({"email": parsed["email"], "name": parsed["name"],
                             "attributes": parsed["attributes"]})
            else:
                st.warning("Paste a SAML response first.")

    # Setup instructions
    with st.expander("📖 Setup Instructions — Azure AD"):
        st.markdown("""
**Steps to configure Azure AD SSO:**

1. Go to **Azure Portal** → Azure Active Directory → Enterprise Applications → New Application → Create your own
2. Select **Integrate any other application you don't find in the gallery**
3. Go to **Single Sign-On** → **SAML**
4. Set **Identifier (Entity ID)** to your SP Entity ID above
5. Set **Reply URL (ACS URL)** to your ACS URL above
6. Download the **Certificate (Base64)** and paste into IdP Certificate above
7. Copy the **Login URL** into IdP SSO URL above
8. Upload the SP Metadata XML (download above) or enter values manually
""")

    with st.expander("📖 Setup Instructions — Okta"):
        st.markdown("""
**Steps to configure Okta SSO:**

1. Go to **Okta Admin Console** → Applications → Create App Integration → SAML 2.0
2. Set **Single sign on URL** to your ACS URL
3. Set **Audience URI (SP Entity ID)** to your SP Entity ID
4. Under **Attribute Statements**, add: `email` → `user.email`, `name` → `user.displayName`
5. Complete setup, go to **Sign On tab** → **View Setup Instructions**
6. Copy the **Identity Provider Single Sign-On URL** → paste as IdP SSO URL
7. Download the **X.509 Certificate** → paste as IdP Certificate
""")

    with st.expander("📖 Setup Instructions — Google Workspace"):
        st.markdown("""
**Steps to configure Google Workspace SSO:**

1. Go to **Google Admin Console** → Apps → Web and Mobile Apps → Add App → Add custom SAML app
2. Download the **IdP metadata** or note the SSO URL and certificate
3. Set **ACS URL** to your ACS URL above
4. Set **Entity ID** to your SP Entity ID above
5. Add attribute mappings: `email` → Basic Information > Primary Email
6. Assign users/groups to the app
7. Paste the Google SSO URL and certificate into the configuration above
""")

    if st.session_state.int_saml:
        st.markdown("**Actions**")
        if st.button("🔗 Generate Auth Request URL", key="saml_auth_req_btn"):
            from utils.integrations import saml_generate_auth_request
            cfg = st.session_state.int_saml
            result = saml_generate_auth_request(cfg["idp_sso_url"], cfg["sp_entity_id"], cfg["acs_url"])
            if "error" in result:
                st.error(f"❌ {result['error']}")
            else:
                st.info(f"**SAML Auth Request URL:**\n\n{result['redirect_url']}\n\n*Request ID: `{result['request_id']}`*")
    _card_wrap_close()


# ═══════════════════════════════════════════════════════════════════════════
# TAB 8 — CONNECTED
# ═══════════════════════════════════════════════════════════════════════════
with tab_connected:
    INT_DISPLAY = [
        ("int_email",       "📧", "Email (SMTP)",             "Communication"),
        ("int_gcal",        "📅", "Calendar",                 "Communication"),
        ("int_gdrive",      "📁", "Google Drive",             "Storage"),
        ("int_onedrive",    "☁️", "OneDrive",                 "Storage"),
        ("int_dropbox",     "📦", "Dropbox",                  "Storage"),
        ("int_docusign",    "✍️", "DocuSign",                 "E-Signature"),
        ("int_adobe",       "✒️", "Adobe Sign",               "E-Signature"),
        ("int_westlaw",     "⚖️", "Westlaw",                  "Legal Research"),
        ("int_lexisnexis",  "📚", "LexisNexis",               "Legal Research"),
        ("int_xero",        "💰", "Xero",                     "Finance"),
        ("int_qbo",         "💳", "QuickBooks Online",        "Finance"),
        ("int_zapier",      "🔌", "Zapier",                   "Automation"),
        ("int_make",        "🔄", "Make (Integromat)",        "Automation"),
        ("int_saml",        "🔐", "SSO / SAML",               "Security"),
    ]
    connected_items = [(k, icon, name, cat) for (k, icon, name, cat) in INT_DISPLAY
                       if st.session_state.get(k) is not None]

    if connected_items:
        section(f"✅ {len(connected_items)} Active Connection{'s' if len(connected_items) != 1 else ''}")
        for (k, icon, name, cat) in connected_items:
            st.markdown(
                f"""<div style="background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;
                              padding:.9rem 1.1rem;margin-bottom:.5rem;
                              display:flex;align-items:center;gap:1rem">
                  <span style="font-size:1.4rem">{icon}</span>
                  <div style="flex:1">
                    <div style="font-weight:700;color:#1a2744">{name}</div>
                    <div style="font-size:.78rem;color:#16a34a">● Connected</div>
                  </div>
                  <span style="font-size:.75rem;background:#dcfce7;color:#15803d;padding:.2rem .7rem;
                               border-radius:20px;border:1px solid #86efac">{cat}</span>
                </div>""",
                unsafe_allow_html=True,
            )
            if st.button(f"🔌 Disconnect {name}", key=f"disc_{k}"):
                st.session_state[k] = None
                st.rerun()
    else:
        st.markdown(
            '<div style="text-align:center;color:#94a3b8;padding:3rem">'
            '🔗 No integrations configured yet.<br>'
            '<small>Use the category tabs above to configure each integration.</small>'
            '</div>',
            unsafe_allow_html=True,
        )


# ═══════════════════════════════════════════════════════════════════════════
# TAB 9 — REQUEST INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════
with tab_request:
    section("💡 Request an Integration")
    st.markdown("Don't see the tool you use? Let us know — we prioritise integrations based on demand.")
    st.markdown("<br>", unsafe_allow_html=True)

    CATEGORIES_REQ = sorted({cat for (_, _, _, cat) in [
        ("", "", "", "Communication"), ("", "", "", "Storage"), ("", "", "", "E-Signature"),
        ("", "", "", "Productivity"), ("", "", "", "Legal Research"), ("", "", "", "Finance"),
        ("", "", "", "Automation"), ("", "", "", "Security"), ("", "", "", "Other"),
    ]})

    with st.form("int_request_form", clear_on_submit=True):
        rq1, rq2 = st.columns(2)
        req_name = rq1.text_input("Integration / Tool Name *", placeholder="e.g. Clio, NetDocuments, Sage, PracticePanther")
        req_cat = rq2.selectbox("Category", CATEGORIES_REQ)
        req_use = st.text_area("How would you use it? *", height=80,
                               placeholder="Describe the workflow — what would you import/export, how often, for what tasks?")
        req_priority = st.radio("Priority for your firm",
                                ["Nice to have", "Would save significant time", "Blocking — we need this now"],
                                horizontal=True)
        if st.form_submit_button("📨 Submit Request", type="primary"):
            if req_name.strip() and req_use.strip():
                st.session_state.int_requests.append({
                    "name": req_name.strip(), "category": req_cat,
                    "use_case": req_use.strip(), "priority": req_priority,
                })
                st.success(f"✅ Request for **{req_name}** submitted — thank you! We'll prioritise based on demand.")
            else:
                st.warning("Please fill in the tool name and use case.")

    if st.session_state.int_requests:
        st.markdown("<br>", unsafe_allow_html=True)
        section(f"📋 Your Requests ({len(st.session_state.int_requests)})")
        for req in st.session_state.int_requests:
            priority_color = {
                "Blocking — we need this now": "#dc2626",
                "Would save significant time": "#d97706",
                "Nice to have": "#64748b",
            }.get(req["priority"], "#64748b")
            st.markdown(
                f"""<div style="background:#f8fafc;border-radius:8px;padding:.7rem 1rem;
                              margin-bottom:.35rem;border-left:3px solid {priority_color}">
                  <div style="font-weight:700;color:#1a2744">{req['name']}
                    <span style="font-size:.72rem;color:#64748b;font-weight:400;margin-left:.5rem">{req['category']}</span>
                  </div>
                  <div style="font-size:.8rem;color:#475569;margin-top:.2rem">{req['use_case'][:120]}{"…" if len(req['use_case']) > 120 else ""}</div>
                  <div style="font-size:.72rem;color:{priority_color};margin-top:.2rem">{req['priority']}</div>
                </div>""",
                unsafe_allow_html=True,
            )
