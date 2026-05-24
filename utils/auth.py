import os
import streamlit as st
from supabase import create_client, Client


def _secret(key: str) -> str:
    val = os.environ.get(key, "")
    if val:
        return val
    try:
        return st.secrets[key]
    except Exception:
        return ""


def _service_client() -> Client:
    url = _secret("SUPABASE_URL")
    key = _secret("SUPABASE_SERVICE_KEY")
    if not url or not key:
        raise RuntimeError("SUPABASE_URL or SUPABASE_SERVICE_KEY not set in environment.")
    return create_client(url, key)


def get_supabase() -> Client:
    return _service_client()


# ── Sign in ────────────────────────────────────────────────────────

def sign_in(email: str, password: str) -> dict:
    try:
        url  = _secret("SUPABASE_URL")
        anon = _secret("SUPABASE_ANON_KEY")
        if not url or not anon:
            return {"ok": False, "error": f"Server config missing — SUPABASE_URL={'✓' if url else '✗'}, SUPABASE_ANON_KEY={'✓' if anon else '✗'}. Add them in Railway → Variables."}
        client = create_client(url, anon)
        resp = client.auth.sign_in_with_password({"email": email, "password": password})
        if not resp.user:
            return {"ok": False, "error": "Invalid email or password."}
        return _load_profile(resp.user.id)
    except Exception as e:
        msg = str(e)
        if "Invalid login" in msg or "invalid_credentials" in msg:
            return {"ok": False, "error": "Invalid email or password."}
        return {"ok": False, "error": f"Auth error: {msg}"}


def _load_profile(auth_user_id: str) -> dict:
    db = get_supabase()
    resp = (
        db.table("profiles")
        .select("*, organizations(name, slug, subscription_plan)")
        .eq("id", auth_user_id)
        .maybe_single()
        .execute()
    )
    profile = resp.data
    if not profile:
        return {"ok": False, "error": "Account not configured. Contact your administrator."}
    if not profile.get("is_active", True):
        return {"ok": False, "error": "Your account has been deactivated."}
    org = profile.get("organizations") or {}
    st.session_state.user = {
        "id": profile["id"],
        "email": profile["email"],
        "full_name": profile.get("full_name", ""),
        "role": profile["role"],
        "title": profile.get("title", ""),
        "organization_id": profile.get("organization_id"),
        "organization_name": org.get("name", ""),
        "organization_slug": org.get("slug", ""),
        "subscription_plan": org.get("subscription_plan", "starter"),
    }
    return {"ok": True, "user": st.session_state.user}


# ── Register a new law firm ────────────────────────────────────────

def register_firm(firm_name: str, email: str, password: str, full_name: str) -> dict:
    try:
        db = get_supabase()
        slug = _slugify(firm_name)
        existing = db.table("organizations").select("id").eq("slug", slug).execute()
        if existing.data:
            slug = f"{slug}-{len(existing.data) + 1}"

        org_resp = db.table("organizations").insert({
            "name": firm_name, "slug": slug, "email": email,
        }).execute()
        org_id = org_resp.data[0]["id"]

        auth_resp = db.auth.admin.create_user({
            "email": email, "password": password, "email_confirm": True,
        })
        uid = auth_resp.user.id

        db.table("profiles").insert({
            "id": uid, "organization_id": org_id,
            "email": email, "full_name": full_name, "role": "admin",
        }).execute()

        return sign_in(email, password)
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ── Admin: create a user inside an org ────────────────────────────

def create_user(email: str, password: str, full_name: str,
                role: str, org_id: str, title: str = "") -> dict:
    try:
        db = get_supabase()
        existing = db.table("profiles").select("id").eq("email", email).execute()
        if existing.data:
            return {"ok": False, "error": "A user with this email already exists."}
        auth_resp = db.auth.admin.create_user({
            "email": email, "password": password, "email_confirm": True,
        })
        uid = auth_resp.user.id
        db.table("profiles").insert({
            "id": uid, "organization_id": org_id,
            "email": email, "full_name": full_name,
            "role": role, "title": title,
        }).execute()
        return {"ok": True, "user_id": uid}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def deactivate_user(user_id: str) -> dict:
    try:
        get_supabase().table("profiles").update({"is_active": False}).eq("id", user_id).execute()
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def reset_password(user_id: str, new_password: str) -> dict:
    try:
        get_supabase().auth.admin.update_user_by_id(user_id, {"password": new_password})
        return {"ok": True}
    except Exception as e:
        return {"ok": False, "error": str(e)}


# ── Session helpers ────────────────────────────────────────────────

def sign_out():
    st.session_state.pop("user", None)


def get_current_user() -> dict | None:
    return st.session_state.get("user")


def require_auth() -> dict:
    user = get_current_user()
    if not user:
        st.switch_page("pages/p_login.py")
        st.stop()
    return user


def require_role(*roles: str) -> dict:
    user = require_auth()
    if user["role"] not in roles:
        st.error("⛔ You don't have permission to access this page.")
        st.stop()
    return user


def require_lawyer() -> dict:
    return require_role("admin", "lawyer", "staff", "intern")


def require_admin() -> dict:
    return require_role("admin")


def is_firm_user() -> bool:
    u = get_current_user()
    return bool(u and u["role"] in ("admin", "lawyer", "staff", "intern"))


def is_client() -> bool:
    u = get_current_user()
    return bool(u and u["role"] == "client")


def is_admin() -> bool:
    u = get_current_user()
    return bool(u and u["role"] == "admin")


def can_see_internals() -> bool:
    return is_firm_user()


# ── Utilities ──────────────────────────────────────────────────────

def _slugify(text: str) -> str:
    import re
    return re.sub(r"[^a-z0-9-]", "-", text.lower().replace("&", "and"))[:50].strip("-")
