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
    if "status" in kwargs:
        try:
            m = get_matter(matter_id)
            if m:
                notify_matter_members(
                    matter_id, "matter_status_changed",
                    f"Matter status: {kwargs['status']}",
                    body=f"{m.get('ref', matter_id)}: {m.get('title', '')} → {kwargs['status']}",
                    exclude_id=_uid(),
                )
        except Exception:
            pass


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
    task = (resp.data or [{}])[0]
    assignee = kwargs.get("assigned_to")
    if task.get("id") and assignee and assignee != _uid():
        create_notification(
            assignee, "task_assigned",
            f"Task assigned: {kwargs.get('title', 'New task')}",
            body=f"Due: {kwargs.get('due_date', '—')} · Priority: {kwargs.get('priority', '—')}",
            matter_id=kwargs.get("matter_id"),
            related_id=task["id"],
        )
    return task


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
    q = get_db().table("time_entries").select("*, profiles!lawyer_id(full_name)").eq("organization_id", org)
    if matter_id:
        q = q.eq("matter_id", matter_id)
    rows = (q.order("entry_date", desc=True).execute()).data or []
    # Normalise: expose entry_date as "date" and profile name as "lawyer" for templates
    for r in rows:
        r.setdefault("date", r.get("entry_date", ""))
        r.setdefault("lawyer", (r.get("profiles") or {}).get("full_name", ""))
    return rows


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
    try:
        profile = get_db().table("profiles").select("email,full_name").eq("id", recipient_id).maybe_single().execute()
        if profile.data and profile.data.get("email"):
            from utils.email_utils import notify_user_email
            notify_user_email(
                to_email=profile.data["email"],
                notification_type=ntype,
                title=title,
                body=body,
            )
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


# ── Rwanda Law Library ────────────────────────────────────────────

_LAW_TABLE = "law_library"

def law_library_available() -> bool:
    try:
        get_db().table(_LAW_TABLE).select("id").limit(1).execute()
        return True
    except Exception:
        return False


def list_laws(search: str | None = None) -> list[dict]:
    org = _org()
    if not org:
        return []
    try:
        q = (get_db().table(_LAW_TABLE)
             .select("id,title,reference,category,year,file_name,created_at")
             .eq("organization_id", org))
        if search:
            q = q.ilike("title", f"%{search}%")
        return (q.order("title").execute()).data or []
    except Exception:
        return []


def get_law_text(law_id: str) -> str:
    try:
        resp = (get_db().table(_LAW_TABLE)
                .select("full_text").eq("id", law_id).maybe_single().execute())
        return (resp.data or {}).get("full_text", "")
    except Exception:
        return ""


def save_law(title: str, full_text: str, reference: str = "", category: str = "",
             year: int | None = None, file_name: str = "") -> bool:
    org = _org()
    if not org:
        return False
    try:
        get_db().table(_LAW_TABLE).insert({
            "organization_id": org,
            "title": title, "reference": reference,
            "category": category, "year": year,
            "full_text": full_text, "file_name": file_name,
            "uploaded_by": _uid(),
        }).execute()
        audit("LAW_UPLOADED", _LAW_TABLE, None, {"title": title})
        return True
    except Exception:
        return False


def delete_law(law_id: str) -> None:
    try:
        get_db().table(_LAW_TABLE).delete().eq("id", law_id).execute()
    except Exception:
        pass


# ── Document Templates ────────────────────────────────────────────

_TPL_TABLE = "document_templates"

def templates_available() -> bool:
    try:
        get_db().table(_TPL_TABLE).select("id").limit(1).execute()
        return True
    except Exception:
        return False

def save_template(name: str, category: str, jurisdiction: str,
                  body: str, notes: str = "") -> bool:
    org = _org()
    if not org:
        return False
    try:
        get_db().table(_TPL_TABLE).insert({
            "organization_id": org, "name": name,
            "category": category, "jurisdiction": jurisdiction,
            "body": body, "notes": notes, "created_by": _uid(),
        }).execute()
        return True
    except Exception:
        return False

def list_templates(category: str | None = None, search: str | None = None) -> list[dict]:
    org = _org()
    if not org:
        return []
    try:
        q = (get_db().table(_TPL_TABLE)
             .select("id,name,category,jurisdiction,notes,created_at")
             .eq("organization_id", org))
        if category:
            q = q.eq("category", category)
        if search:
            q = q.ilike("name", f"%{search}%")
        return (q.order("name").execute()).data or []
    except Exception:
        return []

def get_template_body(tpl_id: str) -> str:
    try:
        resp = (get_db().table(_TPL_TABLE)
                .select("body").eq("id", tpl_id).maybe_single().execute())
        return (resp.data or {}).get("body", "")
    except Exception:
        return ""

def delete_template(tpl_id: str) -> None:
    try:
        get_db().table(_TPL_TABLE).delete().eq("id", tpl_id).execute()
    except Exception:
        pass


# ── Clause Library (DB-backed) ─────────────────────────────────────

_CL_TABLE = "clause_library_db"

def clauses_db_available() -> bool:
    try:
        get_db().table(_CL_TABLE).select("id").limit(1).execute()
        return True
    except Exception:
        return False

def save_clause(title: str, category: str, jurisdiction: str,
                clause_text: str, notes: str = "", risk_level: str = "medium") -> bool:
    org = _org()
    if not org:
        return False
    try:
        get_db().table(_CL_TABLE).insert({
            "organization_id": org, "title": title,
            "category": category, "jurisdiction": jurisdiction,
            "clause_text": clause_text, "notes": notes,
            "risk_level": risk_level, "approved": False,
            "created_by": _uid(),
        }).execute()
        return True
    except Exception:
        return False

def list_clauses(search: str | None = None, category: str | None = None,
                 jurisdiction: str | None = None) -> list[dict]:
    org = _org()
    if not org:
        return []
    try:
        q = get_db().table(_CL_TABLE).select("*").eq("organization_id", org)
        if category:
            q = q.eq("category", category)
        if jurisdiction:
            q = q.eq("jurisdiction", jurisdiction)
        if search:
            q = q.ilike("title", f"%{search}%")
        return (q.order("title").execute()).data or []
    except Exception:
        return []

def update_clause_db(clause_id: str, **kwargs) -> None:
    try:
        get_db().table(_CL_TABLE).update(kwargs).eq("id", clause_id).execute()
    except Exception:
        pass

def delete_clause_db(clause_id: str) -> None:
    try:
        get_db().table(_CL_TABLE).delete().eq("id", clause_id).execute()
    except Exception:
        pass


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
    from datetime import timedelta
    fortnight = str(date.today() + timedelta(days=14))
    recent   = (db.table("matters").select("*").eq("organization_id", org).order("created_at", desc=True).limit(5).execute()).data or []
    od_tasks = (db.table("tasks").select("*").eq("organization_id", org).lt("due_date", today).neq("status", "completed").neq("status", "cancelled").order("due_date").limit(10).execute()).data or []
    upcoming = (db.table("tasks").select("*").eq("organization_id", org).gte("due_date", today).lte("due_date", fortnight).neq("status", "completed").neq("status", "cancelled").order("due_date").limit(8).execute()).data or []
    activity = []
    try:
        activity = (db.table("audit_logs").select("*").eq("organization_id", org).order("created_at", desc=True).limit(8).execute()).data or []
    except Exception:
        pass
    return {
        "active_matters": active,
        "total_clients": clients,
        "pending_tasks": pending,
        "overdue_tasks": overdue,
        "recent_matters": recent,
        "overdue_task_list": od_tasks,
        "upcoming_tasks": upcoming,
        "recent_activity": activity,
    }


# ── Mark entries billed ───────────────────────────────────────────

def mark_entries_billed(matter_id: str) -> int:
    """Mark all unbilled time entries for a matter as billed. Returns count updated."""
    org = _org()
    if not org:
        return 0
    try:
        result = (
            get_db().table("time_entries")
            .update({"billed": True})
            .eq("organization_id", org)
            .eq("matter_id", matter_id)
            .eq("billed", False)
            .execute()
        )
        return len(result.data or [])
    except Exception:
        return 0


# ── Billing analytics ─────────────────────────────────────────────

def billing_analytics() -> dict:
    """Revenue this month, WIP, top matters by value."""
    org = _org()
    if not org:
        return {}
    try:
        from datetime import datetime
        entries = (
            get_db().table("time_entries").select("*")
            .eq("organization_id", org).execute()
        ).data or []
        today = date.today()
        month_start = today.replace(day=1).isoformat()
        rev_month = sum(
            e["hours"] * (e.get("rate") or 0)
            for e in entries
            if e.get("billed") and str(e.get("entry_date", "") or "")[:7] == today.isoformat()[:7]
        )
        wip = sum(
            e["hours"] * (e.get("rate") or 0)
            for e in entries if not e.get("billed")
        )
        total_rev = sum(e["hours"] * (e.get("rate") or 0) for e in entries if e.get("billed"))

        matters_val: dict = {}
        for e in entries:
            mid = e.get("matter_id") or "general"
            matters_val.setdefault(mid, 0)
            matters_val[mid] += e["hours"] * (e.get("rate") or 0)

        matters_meta = {m["id"]: m for m in (
            get_db().table("matters").select("id,ref,title,status,matter_type")
            .eq("organization_id", org).execute()
        ).data or []}

        by_status: dict = {}
        by_type: dict = {}
        for m in matters_meta.values():
            s = m.get("status", "Unknown")
            t = m.get("matter_type", "Other") or "Other"
            by_status[s] = by_status.get(s, 0) + 1
            by_type[t]   = by_type.get(t, 0) + 1

        top_matters = sorted(
            [(mid, val) for mid, val in matters_val.items()],
            key=lambda x: -x[1]
        )[:5]
        top_matters_enriched = [
            {
                "id": mid,
                "ref":   matters_meta.get(mid, {}).get("ref", "—"),
                "title": matters_meta.get(mid, {}).get("title", "General")[:35],
                "value": val,
            }
            for mid, val in top_matters
        ]
        return {
            "revenue_month": rev_month,
            "wip": wip,
            "total_revenue": total_rev,
            "by_status": by_status,
            "by_type": by_type,
            "top_matters": top_matters_enriched,
        }
    except Exception:
        return {}


# ── Invoices ──────────────────────────────────────────────────────

_INV_TABLE = "invoices"

def invoices_available() -> bool:
    try:
        get_db().table(_INV_TABLE).select("id").limit(1).execute()
        return True
    except Exception:
        return False


def create_invoice(matter_id: str, invoice_number: str, client_name: str,
                   invoice_text: str, subtotal: float, vat_amount: float,
                   total_amount: float, terms: str = "", notes: str = "") -> dict | None:
    org = _org()
    if not org:
        return None
    try:
        result = get_db().table(_INV_TABLE).insert({
            "organization_id": org,
            "matter_id": matter_id,
            "invoice_number": invoice_number,
            "client_name": client_name,
            "invoice_text": invoice_text,
            "subtotal": subtotal,
            "vat_amount": vat_amount,
            "total_amount": total_amount,
            "terms": terms,
            "notes": notes,
            "status": "sent",
            "issued_date": str(date.today()),
            "created_by": _uid(),
        }).execute()
        return (result.data or [{}])[0]
    except Exception:
        return None


def list_invoices(matter_id: str | None = None) -> list[dict]:
    org = _org()
    if not org:
        return []
    try:
        q = get_db().table(_INV_TABLE).select("*").eq("organization_id", org)
        if matter_id:
            q = q.eq("matter_id", matter_id)
        return (q.order("issued_date", desc=True).execute()).data or []
    except Exception:
        return []


def update_invoice_status(invoice_id: str, status: str) -> None:
    try:
        get_db().table(_INV_TABLE).update({"status": status}).eq("id", invoice_id).execute()
    except Exception:
        pass


# ── Document versions ─────────────────────────────────────────────

_VER_TABLE = "document_versions"

def doc_versions_available() -> bool:
    try:
        get_db().table(_VER_TABLE).select("id").limit(1).execute()
        return True
    except Exception:
        return False


def add_document_version(doc_id: str, version_number: int, name: str = "",
                          notes: str = "", file_type: str = "",
                          file_size: int | None = None) -> dict | None:
    org = _org()
    if not org:
        return None
    try:
        result = get_db().table(_VER_TABLE).insert({
            "organization_id": org,
            "document_id": doc_id,
            "version_number": version_number,
            "name": name,
            "notes": notes,
            "file_type": file_type,
            "file_size": file_size,
            "uploaded_by": _uid(),
        }).execute()
        return (result.data or [{}])[0]
    except Exception:
        return None


def list_document_versions(doc_id: str) -> list[dict]:
    try:
        return (
            get_db().table(_VER_TABLE).select("*")
            .eq("document_id", doc_id)
            .order("version_number", desc=True)
            .execute()
        ).data or []
    except Exception:
        return []


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
