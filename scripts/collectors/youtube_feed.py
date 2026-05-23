"""Collecteur YouTube : nouvelles vidéos des chaînes suivies (via RSS public).

Pas de clé API requise.

Usage:
    python scripts/collectors/youtube_feed.py --since 1d --out content/raw/$(date +%F)/youtube.json
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "utils"))
from common import CONFIG_DIR, http_get, load_yaml, write_json  # noqa: E402

RSS_URL = "https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"


def parse_duration(seconds_str: str) -> int:
    try:
        return int(seconds_str)
    except (ValueError, TypeError):
        return 0


def fetch_channel(channel_id: str, name: str, since: datetime) -> list[dict]:
    import feedparser

    url = RSS_URL.format(channel_id=channel_id)
    try:
        resp = http_get(url)
    except Exception as e:  # noqa: BLE001
        print(f"[youtube] {name} ({channel_id}) failed: {e}", file=sys.stderr)
        return []
    feed = feedparser.parse(resp.text)
    items: list[dict] = []
    for entry in feed.entries:
        published = entry.get("published_parsed")
        if not published:
            continue
        published_dt = datetime(*published[:6], tzinfo=timezone.utc)
        if published_dt < since:
            continue
        video_id = entry.get("yt_videoid") or entry.get("id", "").split(":")[-1]
        title = entry.get("title", "")
        desc = ""
        media = entry.get("media_group") or {}
        if isinstance(media, dict):
            desc = media.get("media_description", "") or ""
        if not desc:
            # feedparser ouvre parfois la description ailleurs
            desc = entry.get("summary", "") or ""
        items.append({
            "source": "youtube",
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "video_id": video_id,
            "title": title,
            "channel": name,
            "channel_id": channel_id,
            "published_at": published_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "description_preview": desc[:500],
        })
    return items


def keep_item(item: dict, keywords: list[str]) -> bool:
    haystack = (item["title"] + " " + item.get("description_preview", "")).lower()
    return any(k.lower() in haystack for k in keywords)


def parse_since(since: str) -> datetime:
    m = re.fullmatch(r"(\d+)([dh])", since.strip())
    if not m:
        raise ValueError(f"--since must be like '1d' or '12h', got {since!r}")
    n, unit = int(m.group(1)), m.group(2)
    delta = timedelta(days=n) if unit == "d" else timedelta(hours=n)
    return datetime.now(timezone.utc) - delta


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    p.add_argument("--since", default="2d")
    p.add_argument("--all", action="store_true", help="don't filter by keep_keywords")
    args = p.parse_args()

    cfg = load_yaml(CONFIG_DIR / "sources.yml")["youtube"]
    since = parse_since(args.since)
    keywords = cfg.get("keep_keywords", [])

    items: list[dict] = []
    for ch in cfg["channels"]:
        items += fetch_channel(ch["channel_id"], ch["name"], since)

    if not args.all and keywords:
        items = [it for it in items if keep_item(it, keywords)]

    out = Path(args.out)
    write_json(out, items)
    print(f"[youtube] wrote {len(items)} items to {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
