from urllib.parse import urlparse

from ddgs import DDGS

BLOCKED_HOSTS = {
    "facebook.com",
    "instagram.com",
    "x.com",
    "twitter.com",
}

# Job boards and aggregators describe vacancies, not candidates.
JOB_BOARD_MARKERS = (
    "indeed",
    "glassdoor",
    "ziprecruiter",
    "monster",
    "naukri",
    "dice.com",
    "lever.co",
    "greenhouse.io",
    "workable",
    "smartrecruiters",
    "recruitee",
    "jobvite",
    "builtin",
    "wellfound",
    "angel.co",
    "freehire",
    "jobs",
    "careers",
    "hiring",
    "remoteok",
    "weworkremotely",
    "upwork",
    "freelancer",
)

GATED_HOSTS = {"linkedin.com", "www.linkedin.com"}


def host_of(url: str) -> str:
    return (urlparse(url).hostname or "").lower()


def is_gated(url: str) -> bool:
    host = host_of(url)
    return any(host == gated or host.endswith("." + gated) for gated in GATED_HOSTS)


def is_job_posting(url: str) -> bool:
    host = host_of(url)
    if host.endswith("github.com") or host.endswith("github.io"):
        return False
    path = urlparse(url).path.lower()
    return any(marker in host for marker in JOB_BOARD_MARKERS) or any(
        segment in path for segment in ("/jobs/", "/job/", "/careers/", "/vacanc")
    )


def classify(url: str) -> str:
    host = host_of(url)
    if host.endswith("github.com"):
        return "github"
    if is_gated(url):
        return "linkedin"
    if host.endswith("github.io") or "portfolio" in url or host.count(".") <= 1:
        return "portfolio"
    if any(token in host for token in ("blog", "medium", "dev.to", "hashnode", "substack")):
        return "blog"
    return "web"


def search(queries: list[str], per_query: int = 8) -> list[dict[str, str]]:
    """Run DuckDuckGo searches and return de-duplicated, classified results."""
    seen: set[str] = set()
    results: list[dict[str, str]] = []
    with DDGS() as ddgs:
        for query in queries:
            try:
                hits = ddgs.text(query, max_results=per_query)
            except Exception:  # noqa: BLE001 - network/provider failures are non-fatal
                continue
            for hit in hits:
                url = hit.get("href") or ""
                host = host_of(url)
                if not url or url in seen or host in BLOCKED_HOSTS:
                    continue
                if is_job_posting(url) and not is_gated(url):
                    continue
                seen.add(url)
                results.append(
                    {
                        "query": query,
                        "title": hit.get("title", ""),
                        "url": url,
                        "snippet": hit.get("body", ""),
                        "source_type": classify(url),
                    }
                )
    return results
