import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.getenv("TALENTSCOUT_DATA_DIR", BASE_DIR / "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
RESUME_DIR = DATA_DIR / "resumes"
RESUME_DIR.mkdir(parents=True, exist_ok=True)

DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR / 'talentscout.db'}")

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
AGENT_MODEL = os.getenv("AGENT_MODEL", "qwen2.5")
SCORING_MODEL = os.getenv("SCORING_MODEL", "deepseek-r1")
LLM_TIMEOUT_SECONDS = float(os.getenv("LLM_TIMEOUT_SECONDS", "600"))

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
MAX_PAGES_PER_CANDIDATE = int(os.getenv("MAX_PAGES_PER_CANDIDATE", "4"))
EVIDENCE_CHAR_BUDGET = int(os.getenv("EVIDENCE_CHAR_BUDGET", "8000"))
HTTP_TIMEOUT_SECONDS = float(os.getenv("HTTP_TIMEOUT_SECONDS", "20"))
USER_AGENT = "TalentScoutAI/0.1 (compliant public-source research; contact: recruiter)"
