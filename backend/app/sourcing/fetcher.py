from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser

import httpx
from bs4 import BeautifulSoup

from ..config import HTTP_TIMEOUT_SECONDS, USER_AGENT
from .websearch import is_gated

_robots_cache: dict[str, RobotFileParser | None] = {}
DOCUMENT_TYPES = ("application/pdf", "application/msword", "text/plain")


def _robots_for(url: str) -> RobotFileParser | None:
    parsed = urlparse(url)
    origin = f"{parsed.scheme}://{parsed.netloc}"
    if origin in _robots_cache:
        return _robots_cache[origin]
    parser = RobotFileParser()
    try:
        response = httpx.get(
            urljoin(origin, "/robots.txt"),
            timeout=HTTP_TIMEOUT_SECONDS,
            headers={"User-Agent": USER_AGENT},
            follow_redirects=True,
        )
        parser.parse(response.text.splitlines() if response.status_code == 200 else [])
    except httpx.HTTPError:
        parser = None
    _robots_cache[origin] = parser
    return parser


def allowed(url: str) -> bool:
    """Public pages only: never gated sites, and always honour robots.txt."""
    if is_gated(url):
        return False
    parser = _robots_for(url)
    if parser is None:
        return True
    return parser.can_fetch(USER_AGENT, url)


def fetch_page(url: str, max_chars: int = 6000) -> dict[str, str]:
    if not allowed(url):
        return {"url": url, "status": "skipped_not_permitted", "text": "", "content_type": ""}
    try:
        response = httpx.get(
            url,
            timeout=HTTP_TIMEOUT_SECONDS,
            headers={"User-Agent": USER_AGENT},
            follow_redirects=True,
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        return {"url": url, "status": f"error: {exc.__class__.__name__}", "text": "", "content_type": ""}

    content_type = response.headers.get("content-type", "").split(";")[0].strip()
    if content_type not in ("text/html", "application/xhtml+xml", "text/plain"):
        return {"url": url, "status": "skipped_binary", "text": "", "content_type": content_type}

    soup = BeautifulSoup(response.text, "html.parser")
    for tag in soup(["script", "style", "noscript", "nav", "footer"]):
        tag.decompose()
    text = " ".join(soup.get_text(" ").split())
    return {
        "url": url,
        "status": "ok",
        "content_type": content_type,
        "title": (soup.title.get_text().strip() if soup.title else ""),
        "text": text[:max_chars],
    }


def find_public_resume_link(page_url: str) -> str:
    """Return a directly linked, explicitly public resume document URL, else empty string."""
    if not allowed(page_url):
        return ""
    try:
        response = httpx.get(
            page_url,
            timeout=HTTP_TIMEOUT_SECONDS,
            headers={"User-Agent": USER_AGENT},
            follow_redirects=True,
        )
        response.raise_for_status()
    except httpx.HTTPError:
        return ""
    if response.headers.get("content-type", "").split(";")[0].strip() != "text/html":
        return ""
    soup = BeautifulSoup(response.text, "html.parser")
    for anchor in soup.find_all("a", href=True):
        label = anchor.get_text(" ").strip().lower()
        href = urljoin(page_url, anchor["href"])
        looks_like_resume = any(word in label for word in ("resume", "cv", "curriculum vitae"))
        downloadable = href.lower().endswith((".pdf", ".doc", ".docx")) or anchor.has_attr("download")
        if looks_like_resume and downloadable and allowed(href):
            return href
    return ""
