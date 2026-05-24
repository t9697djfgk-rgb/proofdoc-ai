"""
Rwanda Laws Database — import, store, search, and cite in-force laws.
Source: https://amategeko.gov.rw/laws/in-force
Only laws confirmed as "in force" are used in AI responses.
"""
import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime


_HEADERS = {"User-Agent": "eLawFirm Legal Research Tool / research@elawfirm.ai"}
_BASE = "https://amategeko.gov.rw"
_LIST_URL = f"{_BASE}/laws/in-force/1"


def get_db():
    from utils.database import get_db as _db
    return _db()


# ── List / Search Laws ─────────────────────────────────────────────

def list_laws(status: str = "in_force", category: str | None = None,
              limit: int = 100) -> list[dict]:
    q = get_db().table("laws").select("id,title,law_number,category,status,summary,source_url,in_force_date,last_checked")
    q = q.eq("status", status)
    if category:
        q = q.eq("category", category)
    return (q.order("title").limit(limit).execute()).data or []


def search_laws(query: str, status: str = "in_force") -> list[dict]:
    """Full-text search across law titles, summaries, and article content."""
    db = get_db()
    query_lower = query.lower()
    # Search titles + summaries
    laws = (
        db.table("laws")
        .select("id,title,law_number,category,status,summary,source_url,in_force_date")
        .eq("status", status)
        .execute()
    ).data or []
    matches = [
        l for l in laws
        if query_lower in (l.get("title") or "").lower()
        or query_lower in (l.get("summary") or "").lower()
    ]
    # Also search article content
    art_resp = (
        db.table("law_articles")
        .select("law_id,article_number,title,content")
        .ilike("content", f"%{query}%")
        .limit(20)
        .execute()
    ).data or []
    art_law_ids = {a["law_id"] for a in art_resp}
    for l in laws:
        if l["id"] in art_law_ids and l not in matches:
            matches.append(l)
    return matches[:20]


def get_law(law_id: str) -> dict | None:
    resp = get_db().table("laws").select("*").eq("id", law_id).maybe_single().execute()
    return resp.data


def get_law_articles(law_id: str) -> list[dict]:
    return (
        get_db().table("law_articles")
        .select("*").eq("law_id", law_id).order("article_number").execute()
    ).data or []


def get_citations_for_topic(topic: str, max_results: int = 5) -> list[dict]:
    """Returns structured citations suitable for AI context injection."""
    laws = search_laws(topic)[:max_results]
    citations = []
    for law in laws:
        articles = get_law_articles(law["id"])[:3]
        citations.append({
            "title": law.get("title", ""),
            "law_number": law.get("law_number", ""),
            "category": law.get("category", ""),
            "status": law.get("status", "in_force"),
            "source_url": law.get("source_url", ""),
            "in_force_date": law.get("in_force_date", ""),
            "last_checked": law.get("last_checked", ""),
            "relevant_articles": [
                {
                    "article": a.get("article_number", ""),
                    "title": a.get("title", ""),
                    "excerpt": (a.get("content") or "")[:400],
                }
                for a in articles
            ],
        })
    return citations


def build_citation_context(topic: str) -> str:
    """Returns a text block to inject into AI prompts for Rwanda law context."""
    citations = get_citations_for_topic(topic)
    if not citations:
        return ""
    lines = [
        "VERIFIED RWANDA LAWS (in force only — from amategeko.gov.rw):",
        "Use ONLY these laws. Do NOT invent citations.",
        "",
    ]
    for c in citations:
        lines.append(f"LAW: {c['title']}")
        if c["law_number"]:
            lines.append(f"  Number: {c['law_number']}")
        lines.append(f"  Status: {c['status'].upper()}")
        lines.append(f"  Source: {c['source_url']}")
        lines.append(f"  Last verified: {c['last_checked']}")
        for a in c["relevant_articles"]:
            lines.append(f"  Article {a['article']}: {a['title']}")
            lines.append(f"    {a['excerpt']}")
        lines.append("")
    return "\n".join(lines)


# ── Import a law from URL ──────────────────────────────────────────

def import_law_from_url(url: str, category: str = "other",
                         force_status: str = "in_force") -> dict:
    """
    Fetches a law page from amategeko.gov.rw, parses it, and saves to DB.
    Returns {"ok": True, "law_id": "..."} or {"ok": False, "error": "..."}.
    Only call this for verified in-force laws.
    """
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")

        title = _extract_title(soup)
        law_number = _extract_law_number(soup, title)
        summary = _extract_summary(soup)
        articles = _extract_articles(soup)
        raw_content = soup.get_text(separator="\n", strip=True)[:50000]
        in_force_date = _extract_date(soup)

        db = get_db()

        # Check duplicate
        existing = db.table("laws").select("id").eq("source_url", url).execute()
        if existing.data:
            law_id = existing.data[0]["id"]
            db.table("laws").update({
                "title": title, "law_number": law_number, "category": category,
                "summary": summary, "raw_content": raw_content, "status": force_status,
                "in_force_date": in_force_date, "last_checked": datetime.utcnow().isoformat(),
            }).eq("id", law_id).execute()
        else:
            law_resp = db.table("laws").insert({
                "title": title, "law_number": law_number, "category": category,
                "status": force_status, "summary": summary,
                "source_url": url, "raw_content": raw_content,
                "in_force_date": in_force_date,
                "last_checked": datetime.utcnow().isoformat(),
            }).execute()
            law_id = law_resp.data[0]["id"]

            if articles:
                art_rows = [
                    {"law_id": law_id, "article_number": a["number"],
                     "title": a["title"], "content": a["content"]}
                    for a in articles
                ]
                db.table("law_articles").insert(art_rows).execute()

        return {"ok": True, "law_id": law_id, "title": title, "articles": len(articles)}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def add_law_manually(title: str, law_number: str, category: str, summary: str,
                     source_url: str, in_force_date: str | None = None,
                     status: str = "in_force") -> dict:
    try:
        db = get_db()
        resp = db.table("laws").insert({
            "title": title, "law_number": law_number, "category": category,
            "status": status, "summary": summary, "source_url": source_url,
            "in_force_date": in_force_date,
            "last_checked": datetime.utcnow().isoformat(),
        }).execute()
        return {"ok": True, "law_id": resp.data[0]["id"]}
    except Exception as e:
        return {"ok": False, "error": str(e)}


def delete_law(law_id: str) -> None:
    get_db().table("laws").delete().eq("id", law_id).execute()


def update_law_status(law_id: str, status: str) -> None:
    get_db().table("laws").update({
        "status": status, "last_checked": datetime.utcnow().isoformat(),
    }).eq("id", law_id).execute()


# ── Scrape the in-force law list from amategeko.gov.rw ────────────

def fetch_inforce_law_list(page: int = 1) -> list[dict]:
    """
    Returns a list of {"title": ..., "url": ..., "preview": ...}
    from the official in-force laws index page.
    Call import_law_from_url() on each URL to fully import.
    """
    try:
        url = f"{_BASE}/laws/in-force/{page}"
        resp = requests.get(url, headers=_HEADERS, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        results = []
        for link in soup.select("a[href*='/law/']"):
            href = link.get("href", "")
            if not href:
                continue
            full_url = href if href.startswith("http") else _BASE + href
            text = link.get_text(strip=True)
            if text and len(text) > 5:
                results.append({"title": text, "url": full_url})
        return results
    except Exception:
        return []


# ── Private parsers ────────────────────────────────────────────────

def _extract_title(soup: BeautifulSoup) -> str:
    for sel in ["h1", ".law-title", ".page-title", "title"]:
        el = soup.select_one(sel)
        if el:
            return el.get_text(strip=True)[:500]
    return "Untitled Law"


def _extract_law_number(soup: BeautifulSoup, title: str) -> str:
    m = re.search(r"N[°o]?\s*[\d./\-]+(?:/\w+)+", title)
    if m:
        return m.group()
    for el in soup.select(".law-number, .reference, .gazette"):
        t = el.get_text(strip=True)
        if t:
            return t[:100]
    return ""


def _extract_summary(soup: BeautifulSoup) -> str:
    for sel in [".law-summary", ".description", ".abstract", ".intro", "p"]:
        el = soup.select_one(sel)
        if el:
            text = el.get_text(strip=True)
            if len(text) > 30:
                return text[:1000]
    return ""


def _extract_articles(soup: BeautifulSoup) -> list[dict]:
    articles = []
    for el in soup.select(".article, .section, [id^='article'], [id^='art']"):
        num_el = el.select_one(".article-number, .article-num, h3, h4")
        num = num_el.get_text(strip=True) if num_el else ""
        title_el = el.select_one(".article-title, h4, strong")
        art_title = title_el.get_text(strip=True) if title_el else ""
        content = el.get_text(separator=" ", strip=True)[:2000]
        if content:
            articles.append({"number": num, "title": art_title, "content": content})
    return articles[:200]


def _extract_date(soup: BeautifulSoup) -> str | None:
    for el in soup.select(".date, .in-force-date, time"):
        text = el.get_text(strip=True)
        m = re.search(r"\d{4}-\d{2}-\d{2}", text)
        if m:
            return m.group()
    return None
