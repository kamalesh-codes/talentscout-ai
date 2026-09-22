# TalentScout AI

Evidence-backed candidate discovery for recruiters. Paste a job description; a local **Qwen 2.5** agent
extracts hiring criteria, plans DuckDuckGo searches, and gathers public evidence (GitHub public API,
portfolios, engineering blogs). **DeepSeek R1** then produces an explainable fit score per candidate.

- Backend: Python + FastAPI + SQLite (SQLAlchemy)
- Frontend: React + Vite + Tailwind CSS
- Model provider: Ollama (`qwen2.5` for research, `deepseek-r1` for scoring)

## Compliance model

- Public, non-gated sources only. `robots.txt` is honoured on every fetch.
- LinkedIn is never scraped: discovered result URLs are stored and shown as a "View profile" link only.
- Resumes are only downloaded when a page explicitly offers a directly linked public document; otherwise
  the source link is recorded. Recruiters can also upload resumes directly.
- Every claim keeps its source URL; unsupported facts are marked unknown instead of guessed.
- Protected characteristics are never inferred or used in ranking. Scores are recommendations only.

## Running locally

```bash
# 1. Models (Ollama must be installed and running)
ollama pull qwen2.5
ollama pull deepseek-r1

# 2. Backend
cd backend
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/uvicorn app.main:app --reload --port 8000

# 3. Frontend
cd frontend
npm install
npm run dev   # http://localhost:5173
```

`GET /health` reports whether Ollama and both models are reachable.

### Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `OLLAMA_URL` | `http://127.0.0.1:11434` | Ollama endpoint |
| `AGENT_MODEL` | `qwen2.5` | Research/extraction model |
| `SCORING_MODEL` | `deepseek-r1` | Evaluation model |
| `GITHUB_TOKEN` | *(empty)* | Raises the GitHub public API rate limit from 60 to 5000 req/h |
| `MAX_PAGES_PER_CANDIDATE` | `4` | Page-fetch budget per candidate lead |
| `DATABASE_URL` | `sqlite:///backend/data/talentscout.db` | Demo database |

On a small CPU-only machine the 7B defaults are slow (roughly a minute per model call, and the two models
do not fit in memory at once). For a responsive demo use smaller tags:

```bash
AGENT_MODEL=qwen2.5:3b SCORING_MODEL=deepseek-r1:1.5b .venv/bin/uvicorn app.main:app --port 8000
```

If Ollama is unreachable or no public evidence can be retrieved, the run falls back to realistic mock
candidates that are clearly labelled **Demo data** in the UI and in the API (`demo_data: true`).

## API

| Endpoint | Purpose |
| --- | --- |
| `POST /jobs/analyze` | Job description + filters → structured hiring criteria |
| `POST /search/start` | Starts the sourcing workflow in the background, returns `run_id` |
| `GET /search/{run_id}` | Poll run status/stage |
| `GET /search/{run_id}/events` | Server-Sent Events stream of progress |
| `GET /candidates?run_id=&min_score=` | Ranked candidate records |
| `GET /candidates/{id}` | Detailed profile, evidence and evaluation |
| `POST /resumes/upload` | Upload a resume (PDF/TXT/MD), extract text, attach to a candidate |
| `GET /resumes/{candidate_id}` | Download an uploaded resume |

## Pipeline stages

`extracting_criteria` → `creating_search_strategy` → `searching_public_sources` →
`analyzing_projects_and_profiles` → `ranking_candidates` → `done`

Each stage is streamed to the intake page over SSE, with polling as a fallback.
