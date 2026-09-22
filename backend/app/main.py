import json
import queue
import threading
import uuid
from collections.abc import Iterator
from typing import Any

from fastapi import BackgroundTasks, Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from . import pipeline, progress, resumes
from .config import RESUME_DIR
from .db import get_db, init_db
from .llm import LLMUnavailable, provider_status
from .models import Candidate, SearchRun
from .schemas import (
    AnalyzeJobRequest,
    AnalyzeJobResponse,
    CandidateDetail,
    CandidateSummary,
    HiringCriteria,
    ResumeUploadResponse,
    RunProgress,
    StartSearchRequest,
    StartSearchResponse,
)

app = FastAPI(title="TalentScout AI", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "provider": provider_status()}


@app.post("/jobs/analyze", response_model=AnalyzeJobResponse)
def analyze_job(payload: AnalyzeJobRequest) -> AnalyzeJobResponse:
    if not payload.job_description.strip():
        raise HTTPException(status_code=422, detail="job_description must not be empty")
    try:
        criteria = pipeline.extract_criteria(payload.job_description, payload.filters)
    except (LLMUnavailable, ValueError) as exc:
        raise HTTPException(status_code=503, detail=f"Criteria extraction unavailable: {exc}") from exc
    return AnalyzeJobResponse(criteria=criteria)


@app.post("/search/start", response_model=StartSearchResponse)
def start_search(
    payload: StartSearchRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)
) -> StartSearchResponse:
    if not payload.job_description.strip():
        raise HTTPException(status_code=422, detail="job_description must not be empty")
    run = SearchRun(
        id=str(uuid.uuid4()),
        status="pending",
        stage="queued",
        job_description=payload.job_description,
        criteria=payload.criteria.model_dump() if payload.criteria else {},
        filters=payload.filters.model_dump(),
    )
    db.add(run)
    db.commit()
    background_tasks.add_task(_run_in_thread, run.id)
    return StartSearchResponse(run_id=run.id, status=run.status)


def _run_in_thread(run_id: str) -> None:
    threading.Thread(target=pipeline.run_search, args=(run_id,), daemon=True).start()


def _progress(run: SearchRun, db: Session) -> RunProgress:
    count = len(db.scalars(select(Candidate.id).where(Candidate.run_id == run.id)).all())
    return RunProgress(
        run_id=run.id,
        status=run.status,
        stage=run.stage,
        message=run.message,
        demo_data=bool(run.demo_data),
        error=run.error,
        criteria=run.criteria or {},
        candidate_count=count,
    )


@app.get("/search/{run_id}", response_model=RunProgress)
def get_run(run_id: str, db: Session = Depends(get_db)) -> RunProgress:
    run = db.get(SearchRun, run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="run not found")
    return _progress(run, db)


@app.get("/search/{run_id}/events")
def stream_events(run_id: str, db: Session = Depends(get_db)) -> StreamingResponse:
    if db.get(SearchRun, run_id) is None:
        raise HTTPException(status_code=404, detail="run not found")

    def event_stream() -> Iterator[str]:
        listener, replay = progress.subscribe(run_id)
        try:
            for event in replay:
                yield f"data: {json.dumps(event)}\n\n"
            while True:
                try:
                    event = listener.get(timeout=15)
                except queue.Empty:
                    yield ": keep-alive\n\n"
                    continue
                yield f"data: {json.dumps(event)}\n\n"
                if event.get("stage") in ("done", "failed"):
                    break
        finally:
            progress.unsubscribe(run_id, listener)

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


def _summary_fields(candidate: Candidate) -> dict[str, Any]:
    profile = candidate.profile or {}
    evaluation = candidate.evaluation or {}
    return {
        "id": candidate.id,
        "run_id": candidate.run_id,
        "name": candidate.name,
        "headline": candidate.headline,
        "fit_score": candidate.fit_score,
        "match_label": candidate.match_label,
        "demo_data": bool(candidate.demo_data),
        "top_skills": profile.get("skills", [])[:6],
        "projects": profile.get("projects", [])[:3],
        "location": profile.get("location", {}),
        "profile_urls": {k: v for k, v in (profile.get("profile_urls") or {}).items() if v},
        "reasoning_summary": evaluation.get("reasoning_summary", ""),
        "recruiter_recommendation": evaluation.get("recruiter_recommendation", ""),
        "confidence": evaluation.get("confidence", ""),
        "source_links": profile.get("source_links", []),
        "has_resume": bool(candidate.resume_text),
    }


@app.get("/candidates", response_model=list[CandidateSummary])
def list_candidates(
    run_id: str | None = None, min_score: float = 0, db: Session = Depends(get_db)
) -> list[CandidateSummary]:
    statement = select(Candidate).where(Candidate.fit_score >= min_score)
    if run_id:
        statement = statement.where(Candidate.run_id == run_id)
    candidates = db.scalars(statement.order_by(Candidate.fit_score.desc())).all()
    return [CandidateSummary(**_summary_fields(candidate)) for candidate in candidates]


@app.get("/candidates/{candidate_id}", response_model=CandidateDetail)
def get_candidate(candidate_id: str, db: Session = Depends(get_db)) -> CandidateDetail:
    candidate = db.get(Candidate, candidate_id)
    if candidate is None:
        raise HTTPException(status_code=404, detail="candidate not found")
    return CandidateDetail(
        **_summary_fields(candidate),
        profile=candidate.profile or {},
        evaluation=candidate.evaluation or {},
        resume_filename=candidate.resume_filename,
    )


@app.post("/resumes/upload", response_model=ResumeUploadResponse)
async def upload_resume(
    file: UploadFile = File(...),
    candidate_id: str | None = Form(default=None),
    run_id: str | None = Form(default=None),
    name: str | None = Form(default=None),
    db: Session = Depends(get_db),
) -> ResumeUploadResponse:
    content = await file.read()
    try:
        text = resumes.extract_text(file.filename or "resume", content)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    candidate = db.get(Candidate, candidate_id) if candidate_id else None
    if candidate_id and candidate is None:
        raise HTTPException(status_code=404, detail="candidate not found")
    if candidate is None:
        candidate = Candidate(
            id=str(uuid.uuid4()),
            run_id=run_id or "",
            name=name or (file.filename or "Uploaded resume"),
            headline="Recruiter-uploaded resume",
            profile={"name": name or file.filename, "source_links": [], "uncertainties": []},
            evaluation={},
        )
        db.add(candidate)

    stored_name = f"{candidate.id}_{file.filename}"
    (RESUME_DIR / stored_name).write_bytes(content)
    candidate.resume_text = text
    candidate.resume_filename = stored_name
    profile = dict(candidate.profile or {})
    profile["resume_url"] = f"/resumes/{candidate.id}"
    candidate.profile = profile
    db.commit()

    return ResumeUploadResponse(
        candidate_id=candidate.id,
        filename=file.filename or stored_name,
        characters_extracted=len(text),
        resume_url=f"/resumes/{candidate.id}",
    )


@app.get("/resumes/{candidate_id}")
def download_resume(candidate_id: str, db: Session = Depends(get_db)) -> FileResponse:
    candidate = db.get(Candidate, candidate_id)
    if candidate is None or not candidate.resume_filename:
        raise HTTPException(status_code=404, detail="resume not found")
    return FileResponse(RESUME_DIR / candidate.resume_filename, filename=candidate.resume_filename)


@app.get("/criteria/template", response_model=HiringCriteria)
def criteria_template() -> HiringCriteria:
    return HiringCriteria()
