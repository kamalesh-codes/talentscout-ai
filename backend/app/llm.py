import json
import re
from typing import Any

import httpx

from .config import AGENT_MODEL, LLM_TIMEOUT_SECONDS, OLLAMA_URL, SCORING_MODEL

THINK_BLOCK = re.compile(r"<think>.*?</think>", re.DOTALL)


class LLMUnavailable(RuntimeError):
    """Raised when the local Ollama provider cannot serve a request."""


def available_models() -> list[str]:
    try:
        response = httpx.get(f"{OLLAMA_URL}/api/tags", timeout=5)
        response.raise_for_status()
    except httpx.HTTPError:
        return []
    return [model["name"] for model in response.json().get("models", [])]


def provider_status() -> dict[str, Any]:
    models = available_models()
    names = {name.split(":")[0] for name in models}
    return {
        "ollama_reachable": bool(models),
        "models": models,
        "agent_model": AGENT_MODEL,
        "scoring_model": SCORING_MODEL,
        "agent_model_ready": AGENT_MODEL.split(":")[0] in names,
        "scoring_model_ready": SCORING_MODEL.split(":")[0] in names,
    }


def generate(
    model: str,
    prompt: str,
    system: str = "",
    temperature: float = 0.2,
    json_mode: bool = False,
) -> str:
    payload: dict[str, Any] = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": temperature},
    }
    if system:
        payload["system"] = system
    if json_mode:
        payload["format"] = "json"
    try:
        response = httpx.post(
            f"{OLLAMA_URL}/api/generate", json=payload, timeout=LLM_TIMEOUT_SECONDS
        )
        response.raise_for_status()
    except httpx.HTTPError as exc:
        raise LLMUnavailable(f"Ollama request failed for {model}: {exc}") from exc
    return response.json().get("response", "")


def strip_reasoning(text: str) -> str:
    return THINK_BLOCK.sub("", text).strip()


def parse_json(text: str) -> Any:
    """Extract the first JSON object or array from a model response."""
    cleaned = strip_reasoning(text)
    cleaned = re.sub(r"^```(?:json)?|```$", "", cleaned.strip(), flags=re.MULTILINE).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    for opening, closing in (("{", "}"), ("[", "]")):
        start = cleaned.find(opening)
        end = cleaned.rfind(closing)
        if start != -1 and end > start:
            try:
                return json.loads(cleaned[start : end + 1])
            except json.JSONDecodeError:
                continue
    raise ValueError("Model response did not contain valid JSON")


def generate_json(
    model: str, prompt: str, system: str = "", temperature: float = 0.1, attempts: int = 2
) -> Any:
    """Generate and parse JSON, retrying with Ollama's grammar-constrained JSON mode.

    Reasoning models emit prose around their JSON, so the first attempt stays free-form
    (their <think> blocks are stripped) and the retry constrains decoding to JSON.
    """
    last_error: ValueError | None = None
    for attempt in range(attempts):
        raw = generate(
            model,
            prompt,
            system=system,
            temperature=temperature,
            json_mode=attempt > 0,
        )
        try:
            return parse_json(raw)
        except ValueError as exc:
            last_error = exc
    raise last_error or ValueError("Model response did not contain valid JSON")
