"""Realistic, clearly-labelled demo candidates used when online retrieval is unavailable."""

from typing import Any

DEMO_CANDIDATES: list[dict[str, Any]] = [
    {
        "profile": {
            "name": "Priya Raghavan",
            "headline": "Backend engineer building Python data platforms",
            "location": {
                "value": "Bengaluru, India",
                "source_url": "https://github.com/demo-priya",
                "confidence": "verified",
            },
            "profile_urls": {
                "github": "https://github.com/demo-priya",
                "portfolio": "https://demo-priya.dev",
                "blog": "https://demo-priya.dev/blog",
                "linkedin": "https://www.linkedin.com/in/demo-priya",
            },
            "skills": [
                {
                    "name": "Python",
                    "evidence": "Primary language in 9 public repositories, including a streaming ETL framework.",
                    "source_url": "https://github.com/demo-priya",
                    "confidence": "high",
                },
                {
                    "name": "FastAPI",
                    "evidence": "Authored 'fastapi-ingest', a service template with 410 stars.",
                    "source_url": "https://github.com/demo-priya/fastapi-ingest",
                    "confidence": "high",
                },
                {
                    "name": "PostgreSQL",
                    "evidence": "Blog post on partitioning strategies for 2TB event tables.",
                    "source_url": "https://demo-priya.dev/blog/partitioning",
                    "confidence": "medium",
                },
            ],
            "projects": [
                {
                    "name": "fastapi-ingest",
                    "description": "Production template for high-throughput ingestion APIs.",
                    "technologies": ["Python", "FastAPI", "Kafka", "PostgreSQL"],
                    "impact": "410 stars, used as reference architecture in two conference talks.",
                    "source_url": "https://github.com/demo-priya/fastapi-ingest",
                }
            ],
            "experience": {
                "summary": "Public activity spans 6 years of backend and data-platform work.",
                "years": 6,
                "confidence": "inferred",
            },
            "domain_experience": ["Data platforms", "Fintech"],
            "resume_url": "",
            "source_links": [
                "https://github.com/demo-priya",
                "https://demo-priya.dev",
                "https://demo-priya.dev/blog/partitioning",
            ],
            "uncertainties": ["Current employer unknown: not stated on any public source."],
        },
        "evaluation": {
            "fit_score": 86,
            "match_label": "Strong Match",
            "must_have_status": {
                "matched": ["Python", "FastAPI"],
                "missing": [],
                "unknown": ["Team leadership experience"],
            },
            "strengths": [
                {
                    "point": "Deep FastAPI experience",
                    "evidence": "Maintains a widely-used FastAPI ingestion template.",
                    "source_url": "https://github.com/demo-priya/fastapi-ingest",
                }
            ],
            "gaps_or_unknowns": ["No public evidence of leading a team."],
            "reasoning_summary": "Must-have Python and FastAPI requirements are backed by maintained public repositories; leadership signals are absent rather than negative.",
            "recruiter_recommendation": "Prioritize",
            "confidence": "high",
        },
    },
    {
        "profile": {
            "name": "Daniel Okafor",
            "headline": "Full-stack engineer, React and Python",
            "location": {"value": "", "source_url": "", "confidence": "unknown"},
            "profile_urls": {
                "github": "https://github.com/demo-danielo",
                "portfolio": "https://danielokafor.demo",
                "blog": "",
                "linkedin": "",
            },
            "skills": [
                {
                    "name": "React",
                    "evidence": "Portfolio lists three shipped React dashboards with public demos.",
                    "source_url": "https://danielokafor.demo",
                    "confidence": "medium",
                },
                {
                    "name": "Python",
                    "evidence": "Four public repositories using Flask and pandas.",
                    "source_url": "https://github.com/demo-danielo",
                    "confidence": "medium",
                },
            ],
            "projects": [
                {
                    "name": "ops-dashboard",
                    "description": "Realtime operations dashboard with websocket updates.",
                    "technologies": ["React", "TypeScript", "Flask"],
                    "impact": "Public demo, 48 stars.",
                    "source_url": "https://github.com/demo-danielo/ops-dashboard",
                }
            ],
            "experience": {
                "summary": "Public repositories date back roughly 3 years.",
                "years": 3,
                "confidence": "inferred",
            },
            "domain_experience": ["Internal tooling"],
            "resume_url": "",
            "source_links": ["https://github.com/demo-danielo", "https://danielokafor.demo"],
            "uncertainties": [
                "Location unknown: no public source states it.",
                "Years of professional experience inferred from repository history only.",
            ],
        },
        "evaluation": {
            "fit_score": 61,
            "match_label": "Potential Match",
            "must_have_status": {
                "matched": ["Python", "React"],
                "missing": [],
                "unknown": ["Cloud infrastructure experience"],
            },
            "strengths": [
                {
                    "point": "Ships end-to-end products",
                    "evidence": "Operations dashboard with public demo and source.",
                    "source_url": "https://github.com/demo-danielo/ops-dashboard",
                }
            ],
            "gaps_or_unknowns": ["No public cloud/infrastructure evidence."],
            "reasoning_summary": "Solid full-stack evidence at mid level; depth on scale and infrastructure is not publicly demonstrated.",
            "recruiter_recommendation": "Review",
            "confidence": "medium",
        },
    },
    {
        "profile": {
            "name": "Mara Lindqvist",
            "headline": "ML engineer focused on retrieval systems",
            "location": {
                "value": "Stockholm, Sweden",
                "source_url": "https://github.com/demo-mara",
                "confidence": "verified",
            },
            "profile_urls": {
                "github": "https://github.com/demo-mara",
                "portfolio": "",
                "blog": "https://maralind.demo/notes",
                "linkedin": "https://www.linkedin.com/in/demo-mara",
            },
            "skills": [
                {
                    "name": "Python",
                    "evidence": "Primary language across retrieval and evaluation repositories.",
                    "source_url": "https://github.com/demo-mara",
                    "confidence": "high",
                },
                {
                    "name": "Vector search",
                    "evidence": "Blog series benchmarking HNSW and IVF indexes.",
                    "source_url": "https://maralind.demo/notes/hnsw",
                    "confidence": "high",
                },
            ],
            "projects": [
                {
                    "name": "rag-eval",
                    "description": "Evaluation harness for retrieval-augmented pipelines.",
                    "technologies": ["Python", "FAISS", "Ollama"],
                    "impact": "Cited in two open-source RAG projects.",
                    "source_url": "https://github.com/demo-mara/rag-eval",
                }
            ],
            "experience": {
                "summary": "Public ML work since 2019.",
                "years": 5,
                "confidence": "inferred",
            },
            "domain_experience": ["Search", "Applied ML"],
            "resume_url": "",
            "source_links": ["https://github.com/demo-mara", "https://maralind.demo/notes"],
            "uncertainties": ["Backend API experience not publicly evidenced."],
        },
        "evaluation": {
            "fit_score": 48,
            "match_label": "Partial Match",
            "must_have_status": {
                "matched": ["Python"],
                "missing": [],
                "unknown": ["FastAPI", "Production backend ownership"],
            },
            "strengths": [
                {
                    "point": "Strong applied ML and retrieval depth",
                    "evidence": "Maintains an RAG evaluation harness used by other projects.",
                    "source_url": "https://github.com/demo-mara/rag-eval",
                }
            ],
            "gaps_or_unknowns": ["No public FastAPI or service-ownership evidence."],
            "reasoning_summary": "Relevant adjacent expertise, but the core backend must-haves are unevidenced rather than contradicted.",
            "recruiter_recommendation": "Review",
            "confidence": "medium",
        },
    },
]
