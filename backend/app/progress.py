import queue
import threading
from typing import Any

STAGES = [
    "extracting_criteria",
    "creating_search_strategy",
    "searching_public_sources",
    "analyzing_projects_and_profiles",
    "ranking_candidates",
    "done",
]

_lock = threading.Lock()
_queues: dict[str, list[queue.Queue]] = {}
_history: dict[str, list[dict[str, Any]]] = {}


def subscribe(run_id: str) -> tuple[queue.Queue, list[dict[str, Any]]]:
    with _lock:
        listener: queue.Queue = queue.Queue()
        _queues.setdefault(run_id, []).append(listener)
        return listener, list(_history.get(run_id, []))


def unsubscribe(run_id: str, listener: queue.Queue) -> None:
    with _lock:
        listeners = _queues.get(run_id, [])
        if listener in listeners:
            listeners.remove(listener)


def publish(run_id: str, event: dict[str, Any]) -> None:
    with _lock:
        _history.setdefault(run_id, []).append(event)
        listeners = list(_queues.get(run_id, []))
    for listener in listeners:
        listener.put(event)


def history(run_id: str) -> list[dict[str, Any]]:
    with _lock:
        return list(_history.get(run_id, []))
