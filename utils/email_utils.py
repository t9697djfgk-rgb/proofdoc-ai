"""
Email notification utility.
Configure SMTP credentials in .streamlit/secrets.toml:

[email]
smtp_host     = "smtp.gmail.com"
smtp_port     = 587
smtp_user     = "your@email.com"
smtp_password = "your-app-password"
sender_email  = "noreply@yourlawfirm.com"
sender_name   = "eLawFirm"
"""
from __future__ import annotations


def send_email(to_email: str, subject: str, body_text: str,
               body_html: str = "") -> bool:
    """
    Send a notification email via SMTP (STARTTLS).
    Returns True on success, False if not configured or on error.
    """
    import smtplib
    from email.message import EmailMessage
    try:
        import streamlit as st
        cfg = st.secrets.get("email", {})
    except Exception:
        cfg = {}

    host     = cfg.get("smtp_host", "")
    port     = int(cfg.get("smtp_port", 587))
    user     = cfg.get("smtp_user", "")
    password = cfg.get("smtp_password", "")
    sender   = cfg.get("sender_email", user)
    name     = cfg.get("sender_name", "eLawFirm")

    if not (host and user and password and to_email):
        return False

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"]    = f"{name} <{sender}>"
    msg["To"]      = to_email
    msg.set_content(body_text)
    if body_html:
        msg.add_alternative(body_html, subtype="html")

    try:
        with smtplib.SMTP(host, port, timeout=10) as smtp:
            smtp.starttls()
            smtp.login(user, password)
            smtp.send_message(msg)
        return True
    except Exception:
        return False


def notify_user_email(to_email: str, notification_type: str,
                      title: str, body: str = "",
                      matter_ref: str = "") -> bool:
    """Send a templated notification email for common event types."""
    _SUBJECT_MAP = {
        "task_assigned":         "Task assigned to you",
        "matter_status_changed": "Matter status updated",
        "new_message":           "New message in matter discussion",
        "document_uploaded":     "New document uploaded",
        "invoice_ready":         "Invoice ready for review",
    }
    subject = _SUBJECT_MAP.get(notification_type, title)
    if matter_ref:
        subject = f"[{matter_ref}] {subject}"

    body_text = f"{title}\n\n{body}\n\n---\neLawFirm · This is an automated notification."
    body_html = (
        f"<div style='font-family:sans-serif;max-width:560px;margin:auto'>"
        f"<div style='background:#1a2744;color:white;padding:1rem 1.5rem;border-radius:8px 8px 0 0'>"
        f"<h2 style='margin:0;font-size:1.1rem'>⚖️ eLawFirm</h2></div>"
        f"<div style='background:#fff;padding:1.5rem;border:1px solid #e5e7eb;border-top:none;"
        f"border-radius:0 0 8px 8px'>"
        f"<h3 style='color:#1a2744;margin-top:0'>{title}</h3>"
        f"<p style='color:#374151'>{body}</p>"
        f"{'<p style=\"color:#6b7280;font-size:0.85rem\">Matter: ' + matter_ref + '</p>' if matter_ref else ''}"
        f"<hr style='border:none;border-top:1px solid #e5e7eb'>"
        f"<p style='color:#9ca3af;font-size:0.8rem'>This is an automated notification from eLawFirm. "
        f"Do not reply to this email.</p></div></div>"
    )
    return send_email(to_email, subject, body_text, body_html)
