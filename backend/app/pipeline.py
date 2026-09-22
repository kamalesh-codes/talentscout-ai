import json
import uuid
from typing import Any

from sqlalchemy.orm import Session

from . import prompts
from .config import AGENT_MODEL, EVIDENCE_CHAR_BUDGET, MAX_PAGES_PER_CANDIDATE, SCORING_MODEL
from .db import SessionLocal
from .demo_data import DEMO_CANDIDATES
from .llm import LLMUnavailable, generate_json
from .models import Candidate, SearchRun
from .progress import publish
from .schemas import HiringCriteria, SearchFilters
from .sourcing import fetcher, github, websearch

EMPTY_CRITERIA = HiringCriteria().model_dump()


def _emit(db: Session, run: SearchRun, stage: str, message: str, **extra: Any) -> None:
    run.stage = stage
    run.message = message
    db.commit()
    publish(run.id, {"stage": stage, "message": message, "status": run.status, **extra})


def extract_criteria(job_description: str, filters: SearchFilters) -> HiringCriteria:
    data = generate_json(
        AGENT_MODEL,
        prompts.CRITERIA_PROMPT.format(
            filters=filters.model_dump_json(), job_description=job_description[:8000]
        ),
        system=prompts.AGENT_SYSTEM,
    )
    criteria = HiringCriteria.model_validate({**EMPTY_CRITERIA, **(data if isinstance(data, dict) else {})})
    if filters.location and filters.location not in criteria.location_constraints:
        criteria.location_constraints.append(filters.location)
    if filters.work_mode:
        criteria.work_mode = filters.work_mode
    if filters.minimum_years_experience is not None:
        criteria.minimum_years_experience = filters.minimum_years_experience
    return criteria


def build_queries(criteria: HiringCriteria, count: int = 6) -> list[str]:
    data = generate_json(
        AGENT_MODEL,
        prompts.QUERY_PROMPT.format(count=count, criteria=criteria.model_dump_json(indent=2)),
        system=prompts.AGENT_SYSTEM,
        temperature=0.4,
    )
    queries = data.get("queries", []) if isinstance(data, dict) else data
    return [query for query in queries if isinstance(query, str) and query.strip()][:count]


def _cluster_key(result: dict[str, str]) -> str:
    login = github.username_from_url(result["url"])
    if login:
        return f"github:{login.lower()}"
    return f"site:{websearch.host_of(result['url'])}"


def cluster_results(results: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    clusters: dict[str, list[dict[str, str]]] = {}
    for result in results:
        clusters.setdefault(_cluster_key(result), []).append(result)
    ranked = sorted(
        clusters.items(),
        key=lambda item: (item[0].startswith("github:"), len(item[1])),
        reverse=True,
    )
    return dict(ranked)


def gather_evidence(key: str, hits: list[dict[str, str]]) -> dict[str, Any]:
    evidence: dict[str, Any] = {
        "search_results": hits,
        "github": None,
        "pages": [],
        "linkedin_urls": [],
        "resume_links": [],
        "notes": [],
    }

    if key.startswith("github:"):
        login = key.split(":", 1)[1]
        enriched = github.enrich_user(login)
        if enriched:
            evidence["github"] = enriched
        else:
            evidence["notes"].append(
                f"GitHub public API data unavailable for {login} (rate limit or private/missing account); "
                "falling back to the public profile page."
            )
            page = fetcher.fetch_page(f"https://github.com/{login}")
            if page["status"] == "ok" and page["text"]:
                evidence["pages"].append(page)

    pages_fetched = 0
    for hit in hits:
        url = hit["url"]
        if websearch.is_gated(url):
            evidence["linkedin_urls"].append(url)
            evidence["notes"].append(
                "LinkedIn result recorded as a link only; gated content was not accessed."
            )
            continue
        if pages_fetched >= MAX_PAGES_PER_CANDIDATE or hit["source_type"] == "github":
            continue
        page = fetcher.fetch_page(url)
        pages_fetched += 1
        if page["status"] == "ok" and page["text"]:
            evidence["pages"].append(page)
            resume_link = fetcher.find_public_resume_link(url)
            if resume_link:
                evidence["resume_links"].append(resume_link)
        else:
            evidence["notes"].append(f"{url}: {page['status']}")
    return evidence


def build_profile(criteria: HiringCriteria, evidence: dict[str, Any]) -> dict[str, Any]:
    profile = generate_json(
        AGENT_MODEL,
        prompts.PROFILE_PROMPT.format(
            criteria=criteria.model_dump_json(indent=2),
            evidence=json.dumps(evidence, indent=2)[:EVIDENCE_CHAR_BUDGET],
        ),
        system=prompts.AGENT_SYSTEM,
    )
    if not isinstance(profile, dict) or not profile.get("name"):
        raise ValueError("agent returned an unusable profile")

    urls = profile.setdefault("profile_urls", {})
    if evidence["linkedin_urls"] and not urls.get("linkedin"):
        urls["linkedin"] = evidence["linkedin_urls"][0]
    if evidence["github"] and not urls.get("github"):
        urls["github"] = evidence["github"]["html_url"]
    if evidence["resume_links"] and not profile.get("resume_url"):
        profile["resume_url"] = evidence["resume_links"][0]

    known = {url for url in profile.get("source_links", []) if isinstance(url, str)}
    known.update(hit["url"] for hit in evidence["search_results"])
    profile["source_links"] = sorted(known)
    profile.setdefault("uncertainties", []).extend(evidence["notes"])
    return profile


def evaluate(job_description: str, criteria: HiringCriteria, profile: dict[str, Any]) -> dict[str, Any]:
    evaluation = generate_json(
        SCORING_MODEL,
        prompts.SCORING_PROMPT.format(
            job_description=job_description[:6000],
            criteria=criteria.model_dump_json(indent=2),
            candidate=json.dumps(profile, indent=2)[:10000],
        ),
        system=prompts.SCORING_SYSTEM,
    )
    if not isinstance(evaluation, dict):
        raise ValueError("scoring model returned an unusable evaluation")
    evaluation["fit_score"] = max(0, min(100, int(float(evaluation.get("fit_score", 0)))))
    return evaluation


def _store(db: Session, run: SearchRun, profile: dict[str, Any], evaluation: dict[str, Any], demo: bool) -> Candidate:
    candidate = Candidate(
        id=str(uuid.uuid4()),
        run_id=run.id,
        name=profile.get("name", ""),
        headline=profile.get("headline", ""),
        profile=profile,
        evaluation=evaluation,
        fit_score=float(evaluation.get("fit_score", 0)),
        match_label=evaluation.get("match_label", ""),
        demo_data=int(demo),
    )
    db.add(candidate)
    db.commit()
    return candidate


def _load_demo(db: Session, run: SearchRun, limit: int, reason: str) -> None:
    run.demo_data = 1
    _emit(db, run, "ranking_candidates", f"Using demo data: {reason}", demo_data=True)
    for entry in DEMO_CANDIDATES[:limit]:
        profile = dict(entry["profile"], id=str(uuid.uuid4()))
        candidate = _store(db, run, profile, entry["evaluation"], demo=True)
        publish(
            run.id,
            {
                "stage": "candidate_ready",
                "message": f"Demo candidate {candidate.name} ({candidate.fit_score})",
                "candidate_id": candidate.id,
                "demo_data": True,
            },
        )


def run_search(run_id: str) -> None:
    db = SessionLocal()
    run = db.get(SearchRun, run_id)
    if run is None:
        db.close()
        return
    run.status = "running"
    filters = SearchFilters.model_validate(run.filters or {})
    limit = filters.max_candidates

    try:
        if run.criteria:
            criteria = HiringCriteria.model_validate(run.criteria)
            _emit(db, run, "extracting_criteria", "Using criteria supplied by the recruiter")
        else:
            _emit(db, run, "extracting_criteria", "Extracting hiring criteria with qwen2.5")
            criteria = extract_criteria(run.job_description, filters)
            run.criteria = criteria.model_dump()
            db.commit()

        _emit(db, run, "creating_search_strategy", "Generating diversified search queries")
        queries = build_queries(criteria)
        publish(run.id, {"stage": "creating_search_strategy", "message": "Search queries ready", "queries": queries})

        _emit(db, run, "searching_public_sources", f"Searching DuckDuckGo with {len(queries)} queries")
        results = websearch.search(queries)
        clusters = cluster_results(results)
        _emit(
            db,
            run,
            "analyzing_projects_and_profiles",
            f"Analyzing {min(len(clusters), limit * 2)} candidate leads from {len(results)} public results",
        )

        stored = 0
        seen_names: set[str] = set()
        for key, hits in list(clusters.items())[: limit * 3]:
            if stored >= limit:
                break
            evidence = gather_evidence(key, hits)
            if not evidence["github"] and not evidence["pages"]:
                continue
            try:
                profile = build_profile(criteria, evidence)
            except (LLMUnavailable, ValueError) as exc:
                publish(run.id, {"stage": "analyzing_projects_and_profiles", "message": f"Skipped {key}: {exc}"})
                continue

            fingerprint = (profile.get("name", "") or key).strip().lower()
            if fingerprint in seen_names or fingerprint in ("", "unknown"):
                continue
            seen_names.add(fingerprint)

            publish(
                run.id,
                {"stage": "ranking_candidates", "message": f"Scoring {profile.get('name', key)} with deepseek-r1"},
            )
            try:
                evaluation = evaluate(run.job_description, criteria, profile)
            except (LLMUnavailable, ValueError) as exc:
                publish(run.id, {"stage": "ranking_candidates", "message": f"Scoring failed for {key}: {exc}"})
                continue

            profile["id"] = str(uuid.uuid4())
            candidate = _store(db, run, profile, evaluation, demo=False)
            stored += 1
            publish(
                run.id,
                {
                    "stage": "candidate_ready",
                    "message": f"{candidate.name} scored {candidate.fit_score}",
                    "candidate_id": candidate.id,
                },
            )

        if stored == 0:
            _load_demo(db, run, limit, "no public candidate evidence could be retrieved")

        run.status = "completed"
        _emit(db, run, "done", "Ranking complete", demo_data=bool(run.demo_data))
    except LLMUnavailable as exc:
        run.error = str(exc)
        _load_demo(db, run, limit, "the local Ollama models are unavailable")
        run.status = "completed"
        _emit(db, run, "done", "Ranking complete (demo data)", demo_data=True)
    except Exception as exc:  # noqa: BLE001 - surface any failure to the recruiter
        run.status = "failed"
        run.error = f"{exc.__class__.__name__}: {exc}"
        _emit(db, run, "failed", run.error)
    finally:
        db.commit()
        db.close()
