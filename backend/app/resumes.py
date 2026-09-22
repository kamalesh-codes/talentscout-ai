import io

from pypdf import PdfReader


def extract_text(filename: str, content: bytes) -> str:
    lowered = filename.lower()
    if lowered.endswith(".pdf"):
        reader = PdfReader(io.BytesIO(content))
        pages = [page.extract_text() or "" for page in reader.pages]
        return " ".join(" ".join(pages).split())
    if lowered.endswith((".txt", ".md")):
        return " ".join(content.decode("utf-8", errors="ignore").split())
    raise ValueError("Unsupported resume format. Upload a PDF, TXT or MD file.")
