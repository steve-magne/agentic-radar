"""Collecteur Hacker News : top + new stories filtrées par mots-clés agentiques.

Usage:
    python scripts/collectors/hackernews.py --out content/raw/$(date +%F)/hackernews.json
"""

from __future__ import annotations

import argparse
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "utils"))
from common import CONFIG_DIR, http_get, load_yaml, write_json  # noqa: E402

API = "https://hacker-news.firebaseio.com/v0"
KNOWN_DOMAINS = {
    "anthropic.com", "openai.com", "arxiv.org", "github.com",
    "huggingface.co", "deepmind.google", "simonwillison.net",
    "blog.langchain.dev", "latent.space", "ai.googleblog.com",
}


def fetch_ids(story_type: str, limit: int) -> list[int]:
    url = f"{API}/{story_type}stories.json"
    resp = http_get(url)
    return resp.json()[:limit]


def fetch_item(item_id: int) -> dict | None:
    try:
        resp = http_get(f"{API}/item/{item_id}.json")
        return resp.json()
    except Exception as e:  # noqa: BLE001
        print(f"[hn] item {item_id} failed: {e}", file=sys.stderr)
        return None


def keep(item: dict, keywords: list[str]) -> bool:
    if not item or item.get("type") != "story":
        return False
    title = (item.get("title") or "").lower()
    if any(k.lower() in title for k in keywords):
        return True
    url = item.get("url") or ""
    if url:
        host = urlparse(url).netloc.lower().lstrip("www.")
        if any(host == d or host.endswith("." + d) for d in KNOWN_DOMAINS):
            return True
    return False


def normalize(item: dict) -> dict:
    return {
        "source": "hackernews",
        "hn_id": item["id"],
        "title": item.get("title", ""),
        "url": item.get("url") or f"https://news.ycombinator.com/item?id={item['id']}",
        "hn_url": f"https://news.ycombinator.com/item?id={item['id']}",
        "score": item.get("score", 0),
        "descendants": item.get("descendants", 0),
        "by": item.get("by", ""),
        "time": datetime.fromtimestamp(item.get("time", 0), tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    args = p.parse_args()

    cfg = load_yaml(CONFIG_DIR / "sources.yml")["hackernews"]
    keywords = cfg.get("keep_keywords", [])

    all_ids: list[int] = []
    for st in cfg.get("story_types", ["top", "new"]):
        all_ids += fetch_ids(st, cfg.get("per_type_limit", 100))
    all_ids = list(dict.fromkeys(all_ids))  # dedupe en gardant l'ordre

    items: list[dict] = []
    with ThreadPoolExecutor(max_workers=10) as pool:
        futures = {pool.submit(fetch_item, i): i for i in all_ids}
        for fut in as_completed(futures):
            item = fut.result()
            if item and keep(item, keywords):
                # Filtre additionnel sur score/discussions
                if item.get("score", 0) >= 50 or item.get("descendants", 0) >= 30:
                    items.append(normalize(item))

    items.sort(key=lambda x: x["score"], reverse=True)

    out = Path(args.out)
    write_json(out, items)
    print(f"[hn] wrote {len(items)} items to {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
