import re
from typing import Any

import httpx

from ..config import GITHUB_TOKEN, HTTP_TIMEOUT_SECONDS, USER_AGENT

API = "https://api.github.com"
PROFILE_PATH = re.compile(r"^/([A-Za-z0-9-]+)(?:/([A-Za-z0-9._-]+))?/?$")
RESERVED = {
    "orgs",
    "topics",
    "collections",
    "features",
    "marketplace",
    "sponsors",
    "explore",
    "settings",
    "about",
    "pricing",
    "search",
    "login",
}


def _headers() -> dict[str, str]:
    headers = {"Accept": "application/vnd.github+json", "User-Agent": USER_AGENT}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"
    return headers


def username_from_url(url: str) -> str:
    match = re.match(r"https?://(?:www\.)?github\.com(/.*)?$", url)
    if not match:
        return ""
    path_match = PROFILE_PATH.match(match.group(1) or "/")
    if not path_match:
        return ""
    username = path_match.group(1)
    return "" if username.lower() in RESERVED else username


def _get(path: str, params: dict[str, Any] | None = None) -> Any:
    try:
        response = httpx.get(
            f"{API}{path}", headers=_headers(), params=params, timeout=HTTP_TIMEOUT_SECONDS
        )
        response.raise_for_status()
    except httpx.HTTPError:
        return None
    return response.json()


def enrich_user(username: str, max_repos: int = 6) -> dict[str, Any] | None:
    """Fetch public profile, top repositories, languages and README excerpts."""
    user = _get(f"/users/{username}")
    if not isinstance(user, dict) or "login" not in user:
        return None

    repos = _get(
        f"/users/{username}/repos", {"sort": "pushed", "per_page": 30, "type": "owner"}
    )
    repos = repos if isinstance(repos, list) else []
    repos = [repo for repo in repos if not repo.get("fork")]
    repos.sort(key=lambda repo: repo.get("stargazers_count", 0), reverse=True)

    repo_records: list[dict[str, Any]] = []
    for repo in repos[:max_repos]:
        languages = _get(f"/repos/{username}/{repo['name']}/languages") or {}
        readme = _get(f"/repos/{username}/{repo['name']}/readme")
        readme_excerpt = ""
        if isinstance(readme, dict) and readme.get("download_url"):
            try:
                raw = httpx.get(
                    readme["download_url"], timeout=HTTP_TIMEOUT_SECONDS, headers=_headers()
                )
                readme_excerpt = " ".join(raw.text.split())[:1200] if raw.status_code == 200 else ""
            except httpx.HTTPError:
                readme_excerpt = ""
        repo_records.append(
            {
                "name": repo.get("name", ""),
                "description": repo.get("description") or "",
                "html_url": repo.get("html_url", ""),
                "stars": repo.get("stargazers_count", 0),
                "forks": repo.get("forks_count", 0),
                "topics": repo.get("topics", []),
                "primary_language": repo.get("language") or "",
                "languages": list(languages.keys()) if isinstance(languages, dict) else [],
                "pushed_at": repo.get("pushed_at", ""),
                "readme_excerpt": readme_excerpt,
            }
        )

    events = _get(f"/users/{username}/events/public", {"per_page": 30})
    recent_activity = []
    if isinstance(events, list):
        recent_activity = [
            {"type": event.get("type", ""), "repo": event.get("repo", {}).get("name", ""), "at": event.get("created_at", "")}
            for event in events[:10]
        ]

    return {
        "login": user.get("login", ""),
        "name": user.get("name") or "",
        "bio": user.get("bio") or "",
        "company": user.get("company") or "",
        "location": user.get("location") or "",
        "blog": user.get("blog") or "",
        "public_repos": user.get("public_repos", 0),
        "followers": user.get("followers", 0),
        "created_at": user.get("created_at", ""),
        "html_url": user.get("html_url", ""),
        "repositories": repo_records,
        "recent_activity": recent_activity,
    }


def rate_limited() -> bool:
    data = _get("/rate_limit")
    if not isinstance(data, dict):
        return True
    return data.get("resources", {}).get("core", {}).get("remaining", 0) <= 1
