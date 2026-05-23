"""Collecteur Blogs : flux RSS / Atom des blogs engineering AI.

Usage:
    python scripts/collectors/blogs_rss.py --out content/raw/$(date +%F)/blogs.json
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "utils"))
from common import CONFIG_DIR, http_get, load_yaml, write_json  # noqa: E402


def fetch_feed(name: str, url: str, since: datetime) -> list[dict]:
    import feedparser

    try:
        resp = http_get(url)
    except Exception as e:  # noqa: BLE001
        print(f"[blogs] {name} ({url}) failed: {e}", file=sys.stderr)
        return []
    feed = feedparser.parse(resp.text)
    items: list[dict] = []
    for entry in feed.entries:
        pub = entry.get("published_parsed") or entry.get("updated_parsed")
        if not pub:
            continue
        pub_dt = datetime(*pub[:6], tzinfo=timezone.utc)
        if pub_dt < since:
            continue
        summary = entry.get("summary") or entry.get("description") or ""
        items.append({
            "source": "blog",
            "blog": name,
            "title": entry.get("title", ""),
            "url": entry.get("link", ""),
            "published_at": pub_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "summary_preview": summary[:1000],
            "author": entry.get("author", ""),
        })
    return items


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    p.add_argument("--days", type=int, default=3)
    args = p.parse_args()

    cfg = load_yaml(CONFIG_DIR / "sources.yml").get("blogs", {})
    since = datetime.now(timezone.utc) - timedelta(days=args.days)

    items: list[dict] = []
    for feed in cfg.get("rss", []):
        items += fetch_feed(feed["name"], feed["url"], since)

    out = Path(args.out)
    write_json(out, items)
    print(f"[blogs] wrote {len(items)} items to {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
