"""Helpers partagés entre collecteurs."""

from __future__ import annotations

import hashlib
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CONFIG_DIR = ROOT / "config"
CONTENT_DIR = ROOT / "content"
SOURCES_DIR = CONTENT_DIR / "sources"

USER_AGENT = "agentic-radar/0.1 (+https://github.com/stevemagne/agentic-radar)"


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def url_hash(url: str) -> str:
    return hashlib.sha1(url.strip().lower().encode()).hexdigest()[:12]


def slugify(text: str, max_len: int = 60) -> str:
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[-\s]+", "-", text).strip("-")
    return text[:max_len] or "untitled"


def load_yaml(path: Path) -> dict:
    import yaml  # local import so script can run without yaml for --help

    with path.open() as f:
        return yaml.safe_load(f)


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_json(path: Path, data: Any) -> None:
    ensure_dir(path.parent)
    with path.open("w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def existing_urls() -> set[str]:
    """Collecte toutes les URLs déjà ingérées (frontmatter `url:`) pour dédoublonner."""
    urls = set()
    if not SOURCES_DIR.exists():
        return urls
    for md in SOURCES_DIR.glob("*.md"):
        try:
            text = md.read_text(errors="ignore")
        except OSError:
            continue
        for m in re.finditer(r"^url:\s*(.+)$", text, flags=re.MULTILINE):
            urls.add(m.group(1).strip())
    return urls


def http_get(url: str, *, timeout: float = 15.0, headers: dict | None = None, retries: int = 2):
    import httpx

    h = {"User-Agent": USER_AGENT}
    if headers:
        h.update(headers)
    last_exc: Exception | None = None
    for attempt in range(retries + 1):
        try:
            resp = httpx.get(url, timeout=timeout, headers=h, follow_redirects=True)
            if resp.status_code == 429:
                time.sleep(60)
                continue
            resp.raise_for_status()
            return resp
        except Exception as e:  # noqa: BLE001
            last_exc = e
            time.sleep(2 ** attempt)
    if last_exc:
        raise last_exc
    raise RuntimeError(f"Unreachable: {url}")
