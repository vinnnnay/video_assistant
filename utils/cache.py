import json
from pathlib import Path
from typing import Optional

CACHE_DIR = Path(".cache")
CACHE_DIR.mkdir(exist_ok=True)


def cache_path(key: str) -> Path:
    safe = key.replace("/", "_")
    return CACHE_DIR / f"{safe}.json"


def get_cached_result(key: str) -> Optional[dict]:
    p = cache_path(key)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def set_cached_result(key: str, value: dict) -> None:
    p = cache_path(key)
    p.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
