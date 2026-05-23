"""Collecteur Reddit : top stories du jour des subreddits suivis (JSON public).

Usage:
    python scripts/collectors/reddit_feed.py --out content/raw/$(date +%F)/reddit.json
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "utils"))
from common import CONFIG_DIR, http_get, load_yaml, write_json  # noqa: E402


def fetch_sub(sub: str, limit: int) -> list[dict]:
    url = f"https://www.reddit.com/r/{sub}/top.json?t=day&limit={limit}"
    try:
        resp = http_get(url, headers={"Accept": "application/json"})
        data = resp.json()
    except Exception as e:  # noqa: BLE001
        print(f"[reddit] r/{sub} failed: {e}", file=sys.stderr)
        return []
    items: list[dict] = []
    for child in data.get("data", {}).get("children", []):
        d = child.get("data", {})
        if d.get("removed_by_category") or d.get("over_18"):
            continue
        items.append({
            "source": "reddit",
            "subreddit": sub,
            "title": d.get("title", ""),
            "score": d.get("score", 0),
            "num_comments": d.get("num_comments", 0),
            "url": f"https://www.reddit.com{d.get('permalink', '')}",
            "external_url": d.get("url_overridden_by_dest") or d.get("url"),
            "selftext_preview": (d.get("selftext") or "")[:500],
            "flair": d.get("link_flair_text") or "",
            "created_utc": datetime.fromtimestamp(d.get("created_utc", 0), tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "author": d.get("author") or "",
        })
    return items


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    args = p.parse_args()

    cfg = load_yaml(CONFIG_DIR / "sources.yml")["reddit"]
    min_score = cfg.get("min_score", 50)
    limit = cfg.get("per_sub_limit", 25)

    items: list[dict] = []
    for sub in cfg["subreddits"]:
        items += fetch_sub(sub, limit)

    items = [it for it in items if it["score"] >= min_score]

    out = Path(args.out)
    write_json(out, items)
    print(f"[reddit] wrote {len(items)} items to {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
