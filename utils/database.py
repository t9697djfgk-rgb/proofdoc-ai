"""
Multi-tenant database layer — Supabase PostgreSQL.
All functions automatically scope to the current user's organization.
Clients are additionally scoped to their assigned matters only.
"""
import streamlit as st
from datetime import date


def get_db():
    from utils.auth import get_supabase
    return get_supabase()


def _org() -> str | None:
    return st.session_state.get("user", {}).get("organization_id")


def _uid() -> str | None:
    return st.session_state.get("user", {}).get("id")


def _role() -> str:
    return st.session_state.get("user", {}).get("role", "")


def _client_matter_ids() -> list[str]:
    resp = get_db().table("matter_members").select("matter_id").eq("profile_id", _uid()).execute()
    return [r["matter_id"] for r in (resp.data or [])]


# ── Init (no-op — schema created via sql/schema.sql in Supabase) ──

def init_db():
    pass


# ── Matters ────────────────────────────────────────────────────────

def list_matters(status: str | None = None) -> list[dict]:
    org = _org()
    if not org:
        return []
    db = get_db()
    if _role() == "client":
        ids = _client_matter_ids()
        if not ids:
            return []
        q = db.table("matters").select("*").in_("id", ids)
    else:
        q = db.table("matters").select("*").eq("organization_id", org)
    if status:
        q = q.eq("status", status)
    return (q.order("created_at", desc=True).execute()).data or []


def get_matter(matter_id: str) -> dict | None:
    resp = get_db().table("matters").select("*").eq("id", matter_id).maybe_single().execute()
    return resp.data


def create_matter(**kwargs) -> dict | None:
    org = _org()
    if not org:
        return None
    uid = _uid()
    resp = get_db().table("matters").insert({"organization_id": org, "created_by": uid, **kwargs}).execute()
    matter = (resp.data or [{}])[0]
    if matter.get("id") and uid:
        get_db().table("matter_members").insert({
            "matter_id": matter["id"], "profile_id": uid,
            "role": "lead_lawyer", "added_by": uid,
        }).execute()
    audit("MATTER_CREATED", "matter", matter.get("id"), {"title": kwargs.get("title")})
    return matter


def update_matter(matter_id: str, **kwargs) -> None:
    get_db().table("matters").update(kwargs).eq("id", matter_id).execute()
    audit("MATTER_UPDATED", "matter", matter_id, kwargs)


def delete_matter(matter_id: str) -> None:
    get_db().table("matters").delete().eq("id", matter_id).execute()
    audit("MATTER_DELETED", "matter", matter_id)


# ── Matter Members ─────────────────────────────────────────────────

def get_matter_members(matter_id: str) -> list[dict]:
    resp = (
        get_db().table("matter_members")
        .select("*, profiles(id, full_name, email, role, title)")
        .eq("matter_id", matter_id)
        .execute()
    )
    return resp.data or []


def add_matter_member(matter_id: str, profile_id: str, role: str = "lawyer") -> None:
    get_db().table("matter_members").upsert({
        "matter_id": matter_id, "profile_id": profile_id,
        "role": role, "added_by": _uid(),
    }).execute()
    audit("MEMBER_ADDED", "matter", matter_id, {"profile_id": profile_id, "role": role})


def remove_matter_member(matter_id: str, profile_id: str) -> None:
    get_db().table("matter_members").delete().eq("matter_id", matter_id).eq("profile_id", profile_id).execute()


def is_matter_member(matter_id: str) -> bool:
    uid = _uid()
    if not uid:
        return False
    resp = get_db().table("matter_members").select("id").eq("matter_id", matter_id).eq("profile_id", uid).execute()
    return bool(resp.data)


# ── Clients ────────────────────────────────────────────────────────

def list_clients(active_only: bool = True) -> list[dict]:
    org = _org()
    if not org:
        return []
    q = get_db().table("clients").select("*").eq("organization_id", org)
    if active_only:
        q = q.eq("is_active", True)
    return (q.order("name").execute()).data or []


def get_client(client_id: str) -> dict | None:
    resp = get_db().table("clients").select("*").eq("id", client_id).maybe_single().execute()
    return resp.data


def create_client(**kwargs) -> dict | None:
    org = _org()
    if not org:
        return None
    resp = get_db().table("clients").insert({"organization_id": org, **kwargs}).execute()
    return (resp.data or [{}])[0]


def update_client(client_id: str, **kwargs) -> None:
    get_db().table("clients").update(kwargs).eq("id", client_id).execute()


# ── Users / Profiles ───────────────────────────────────────────────

def list_profiles(role: str | None = None, active_only: bool = True) -> list[dict]:
    org = _org()
    if not org:
        return []
    q = get_db().table("profiles").select("*").eq("organization_id", org)
    if role:
        q = q.eq("role", role)
    if active_only:
        q = q.eq("is_active", True)
    return (q.order("full_name").execute()).data or []


def get_profile(profile_id: str) -> dict | None:
    resp = get_db().table("profiles").select("*").eq("id", profile_id).maybe_single().execute()
    return resp.data


def list_lawyers() -> list[dict]:
    org = _org()
    if not org:
        return []
    resp = (
        get_db().table("profiles").select("*")
        .eq("organization_id", org)
        .in_("role", ["admin", "lawyer"])
        .eq("is_active", True)
        .order("full_name")
        .execute()
    )
    return resp.data or []


# ── Documents ──────────────────────────────────────────────────────

def list_documents(matter_id: str | None = None, visibility: str | None = None) -> list[dict]:
    org = _org()
    if not org:
        return []
    q = get_db().table("documents").select("*, profiles(full_name)").eq("organization_id", org)
    if matter_id:
        q = q.eq("matter_id", matter_id)
    if _role() == "client":
        q = q.in_("visibility", ["shared_with_client", "client_upload", "final"])
    elif visibility:
        q = q.eq("visibility", visibility)
    return (q.order("created_at", desc=True).execute()).data or []


def add_document(name: str, matter_id: str | None = None, file_path: str | None = None,
                 file_type: str | None = None, file_size: int | None = None,
                 visibility: str = "internal", description: str = "") -> dict | None:
    org = _org()
    if not org:
        return None
    resp = get_db().table("documents").insert({
        "organization_id": org, "matter_id": matter_id, "uploaded_by": _uid(),
        "name": name, "file_path": file_path, "file_type": file_type,
        "file_size": file_size, "visibility": visibility, "description": description,
    }).execute()
    doc = (resp.data or [{}])[0]
    audit("DOCUMENT_UPLOADED", "document", doc.get("id"), {"name": name, "visibility": visibility})
    return doc


def update_document_visibility(doc_id: str, visibility: str) -> None:
    get_db().table("documents").update({"visibility": visibility}).eq("id", doc_id).execute()
    audit("DOCUMENT_VISIBILITY_CHANGED", "document", doc_id, {"visibility": visibility})


def delete_document(doc_id: str) -> None:
    get_db().table("documents").delete().eq("id", doc_id).execute()


# ── Messages ───────────────────────────────────────────────────────

def list_messages(matter_id: str, page: int = 1, page_size: int = 50) -> list[dict]:
    offset = (page - 1) * page_size
    q = (
        get_db().table("messages")
        .select("*, profiles(full_name, role, title), message_attachments(*)")
        .eq("matter_id", matter_id)
    )
    if _role() == "client":
        q = q.eq("message_type", "client_visible")
    return (q.order("created_at").range(offset, offset + page_size - 1).execute()).data or []


def send_message(matter_id: str, body: str, message_type: str = "client_visible") -> dict | None:
    org = _org()
    if not org:
        return None
    if _role() == "client":
        message_type = "client_visible"
    resp = get_db().table("messages").insert({
        "organization_id": org, "matter_id": matter_id,
        "sender_id": _uid(), "sender_role": _role(),
        "message_type": message_type, "body": body,
    }).execute()
    msg = (resp.data or [{}])[0]
    audit("MESSAGE_SENT", "message", msg.get("id"), {"matter_id": matter_id, "type": message_type})
    return msg


def add_message_attachment(message_id: str, file_name: str, file_path: str,
                            file_type: str, file_size: int, document_id: str | None = None) -> None:
    get_db().table("message_attachments").insert({
        "message_id": message_id, "document_id": document_id,
        "file_name": file_name, "file_path": file_path,
        "file_type": file_type, "file_size": file_size, "uploaded_by": _uid(),
    }).execute()
    audit("ATTACHMENT_UPLOADED", "message", message_id, {"file_name": file_name})


def mark_messages_read(matter_id: str) -> None:
    uid = _uid()
    if not uid:
        return
    msgs = list_messages(matter_id, page_size=200)
    records = [{"message_id": m["id"], "profile_id": uid} for m in msgs]
    if records:
        get_db().table("message_reads").upsert(records).execute()


def unread_message_count(matter_id: str) -> int:
    uid = _uid()
    if not uid:
        return 0
    msgs = list_messages(matter_id, page_size=500)
    read_resp = get_db().table("message_reads").select("message_id").eq("profile_id", uid).execute()
    read_ids = {r["message_id"] for r in (read_resp.data or [])}
    return sum(1 for m in msgs if m["id"] not in read_ids and m["sender_id"] != uid)


# ── Tasks ──────────────────────────────────────────────────────────

def list_tasks(matter_id: str | None = None, status: str | None = None,
               assigned_to: str | None = None) -> list[dict]:
    org = _org()
    if not org:
        return []
    q = get_db().table("tasks").select("*, profiles!assigned_to(full_name)").eq("organization_id", org)
    if matter_id:
        q = q.eq("matter_id", matter_id)
    if status:
        q = q.eq("status", status)
    if assigned_to:
        q = q.eq("assigned_to", assigned_to)
    return (q.order("due_date").execute()).data or []


def create_task(**kwargs) -> dict | None:
    org = _org()
    if not org:
        return None
    resp = get_db().table("tasks").insert({"organization_id": org, "created_by": _uid(), **kwargs}).execute()
    return (resp.data or [{}])[0]


def update_task(task_id: str, **kwargs) -> None:
    get_db().table("tasks").update(kwargs).eq("id", task_id).execute()


def delete_task(task_id: str) -> None:
    get_db().table("tasks").delete().eq("id", task_id).execute()


# ── Notes ──────────────────────────────────────────────────────────

def list_notes(matter_id: str) -> list[dict]:
    return (
        get_db().table("notes")
        .select("*, profiles!author_id(full_name)")
        .eq("matter_id", matter_id)
        .order("created_at", desc=True)
        .execute()
    ).data or []


def add_note(matter_id: str, body: str, title: str = "", author_id: str | None = None) -> None:
    get_db().table("notes").insert({
        "organization_id": _org(), "matter_id": matter_id,
        "author_id": author_id or _uid(), "title": title, "body": body,
    }).execute()


# ── Time Entries ───────────────────────────────────────────────────

def list_time_entries(matter_id: str | None = None) -> list[dict]:
    org = _org()
    if not org:
        return []
    q = get_db().table("time_entries").select("*").eq("organization_id", org)
    if matter_id:
        q = q.eq("matter_id", matter_id)
    return (q.order("entry_date", desc=True).execute()).data or []


def add_time_entry(matter_id: str | None, hours: float, description: str,
                   rate: float = 0.0, lawyer: str = "", entry_date: str | None = None) -> None:
    get_db().table("time_entries").insert({
        "organization_id": _org(), "matter_id": matter_id, "lawyer_id": _uid(),
        "description": description, "hours": hours, "rate": rate,
        "entry_date": entry_date or str(date.today()),
    }).execute()


# ── Notifications ──────────────────────────────────────────────────

def list_notifications(limit: int = 30) -> list[dict]:
    uid = _uid()
    if not uid:
        return []
    return (
        get_db().table("notifications").select("*")
        .eq("recipient_id", uid)
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    ).data or []


def unread_notification_count() -> int:
    uid = _uid()
    if not uid:
        return 0
    resp = (
        get_db().table("notifications").select("id", count="exact")
        .eq("recipient_id", uid).eq("is_read", False).execute()
    )
    return resp.count or 0


def mark_notifications_read() -> None:
    uid = _uid()
    if uid:
        get_db().table("notifications").update({"is_read": True}).eq("recipient_id", uid).eq("is_read", False).execute()


def create_notification(recipient_id: str, ntype: str, title: str,
                        body: str = "", matter_id: str | None = None,
                        related_id: str | None = None) -> None:
    org = _org()
    if not org or not recipient_id:
        return
    try:
        get_db().table("notifications").insert({
            "organization_id": org, "recipient_id": recipient_id,
            "type": ntype, "title": title, "body": body,
            "matter_id": matter_id, "related_id": related_id,
        }).execute()
    except Exception:
        pass


def notify_matter_members(matter_id: str, ntype: str, title: str, body: str = "",
                           exclude_id: str | None = None, lawyers_only: bool = False) -> None:
    for m in get_matter_members(matter_id):
        if m["profile_id"] == exclude_id:
            continue
        if lawyers_only and m["role"] not in ("lead_lawyer", "lawyer", "staff", "admin"):
            continue
        create_notification(m["profile_id"], ntype, title, body, matter_id)


# ── Dashboard stats ────────────────────────────────────────────────

def dashboard_stats() -> dict:
    org = _org()
    if not org:
        return {}
    db = get_db()
    today = str(date.today())
    active   = db.table("matters").select("id", count="exact").eq("organization_id", org).eq("status", "Active").execute().count or 0
    clients  = db.table("clients").select("id", count="exact").eq("organization_id", org).eq("is_active", True).execute().count or 0
    pending  = db.table("tasks").select("id", count="exact").eq("organization_id", org).eq("status", "pending").execute().count or 0
    overdue  = db.table("tasks").select("id", count="exact").eq("organization_id", org).lt("due_date", today).neq("status", "completed").execute().count or 0
    recent   = (db.table("matters").select("*").eq("organization_id", org).order("created_at", desc=True).limit(5).execute()).data or []
    od_tasks = (db.table("tasks").select("*").eq("organization_id", org).lt("due_date", today).neq("status", "completed").order("due_date").limit(10).execute()).data or []
    return {
        "active_matters": active,
        "total_clients": clients,
        "pending_tasks": pending,
        "overdue_tasks": overdue,
        "upcoming_deadlines": overdue,
        "recent_matters": recent,
        "overdue_task_list": od_tasks,
    }


# ── Audit log ──────────────────────────────────────────────────────

def audit(action: str, resource_type: str = "", resource_id: str | None = None,
          details: dict | None = None) -> None:
    user = st.session_state.get("user", {})
    try:
        get_db().table("audit_logs").insert({
            "organization_id": _org(), "actor_id": _uid(),
            "actor_name": user.get("full_name", ""),
            "action": action, "resource_type": resource_type,
            "resource_id": resource_id, "details": details or {},
        }).execute()
    except Exception:
        pass
