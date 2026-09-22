from typing import Any, Literal

from pydantic import BaseModel, Field


class SearchFilters(BaseModel):
    location: str = ""
    minimum_years_experience: int | None = None
    work_mode: Literal["", "remote", "onsite", "hybrid"] = ""
    max_candidates: int = Field(default=5, ge=1, le=15)


class HiringCriteria(BaseModel):
    role_title: str = ""
    seniority: str = ""
    must_have_skills: list[str] = []
    preferred_skills: list[str] = []
    domain_experience: list[str] = []
    minimum_years_experience: int | None = None
    location_constraints: list[str] = []
    work_mode: str = ""
    responsibilities: list[str] = []
    nice_to_have: list[str] = []
    disqualifiers: list[str] = []


class AnalyzeJobRequest(BaseModel):
    job_description: str
    filters: SearchFilters = SearchFilters()


class AnalyzeJobResponse(BaseModel):
    criteria: HiringCriteria
    demo_data: bool = False


class StartSearchRequest(BaseModel):
    job_description: str
    criteria: HiringCriteria | None = None
    filters: SearchFilters = SearchFilters()


class StartSearchResponse(BaseModel):
    run_id: str
    status: str


class RunProgress(BaseModel):
    run_id: str
    status: str
    stage: str
    message: str
    demo_data: bool
    error: str = ""
    criteria: dict[str, Any] = {}
    candidate_count: int = 0


class CandidateSummary(BaseModel):
    id: str
    run_id: str
    name: str
    headline: str
    fit_score: float
    match_label: str
    demo_data: bool
    top_skills: list[dict[str, Any]] = []
    projects: list[dict[str, Any]] = []
    location: dict[str, Any] = {}
    profile_urls: dict[str, str] = {}
    reasoning_summary: str = ""
    recruiter_recommendation: str = ""
    confidence: str = ""
    source_links: list[str] = []
    has_resume: bool = False


class CandidateDetail(CandidateSummary):
    profile: dict[str, Any] = {}
    evaluation: dict[str, Any] = {}
    resume_filename: str = ""


class ResumeUploadResponse(BaseModel):
    candidate_id: str
    filename: str
    characters_extracted: int
    resume_url: str
