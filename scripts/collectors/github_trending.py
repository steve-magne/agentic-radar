"""Collecteur GitHub : trending + recherches thématiques + awesome lists.

Usage:
    python scripts/collectors/github_trending.py --out content/raw/$(date +%F)/github.json
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Ajoute scripts/utils au path.
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "utils"))
from common import CONFIG_DIR, http_get, load_yaml, write_json  # noqa: E402


def gh(args: list[str]) -> str:
    """Exécute `gh` et retourne stdout (lève si échec)."""
    res = subprocess.run(
        ["gh", *args], capture_output=True, text=True, check=False
    )
    if res.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args)} failed: {res.stderr.strip()}")
    return res.stdout


def fetch_trending(languages: list[str], timeframes: list[str], min_stars_daily: int, min_stars_weekly: int) -> list[dict]:
    """Pas d'API officielle de trending. On utilise github.com/trending via HTML."""
    from bs4 import BeautifulSoup

    items: list[dict] = []
    for lang in languages:
        for tf in timeframes:
            url = f"https://github.com/trending/{lang}?since={tf}" if lang else f"https://github.com/trending?since={tf}"
            try:
                resp = http_get(url)
            except Exception as e:  # noqa: BLE001
                print(f"[trending] {url} failed: {e}", file=sys.stderr)
                continue
            soup = BeautifulSoup(resp.text, "lxml")
            min_stars = min_stars_daily if tf == "daily" else min_stars_weekly
            for art in soup.select("article.Box-row"):
                a = art.select_one("h2 a")
                if not a:
                    continue
                slug = a.get("href", "").strip("/")
                if "/" not in slug:
                    continue
                owner, name = slug.split("/", 1)
                desc_el = art.select_one("p")
                desc = desc_el.get_text(strip=True) if desc_el else ""
                lang_el = art.select_one('[itemprop="programmingLanguage"]')
                language = lang_el.get_text(strip=True) if lang_el else ""
                star_el = art.select_one('a[href$="/stargazers"]')
                stars = 0
                if star_el:
                    txt = star_el.get_text(strip=True).replace(",", "")
                    try:
                        stars = int(txt)
                    except ValueError:
                        stars = 0
                if stars < min_stars:
                    continue
                items.append({
                    "source": "github",
                    "subsource": f"trending-{tf}",
                    "url": f"https://github.com/{owner}/{name}",
                    "owner": owner,
                    "name": name,
                    "description": desc,
                    "language": language,
                    "stars": stars,
                })
    return items


def fetch_searches(searches: list[dict], days: int = 7) -> list[dict]:
    since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    items: list[dict] = []
    for s in searches:
        query = s["query"].replace("{since}", since)
        try:
            out = gh([
                "api", "-X", "GET", "search/repositories",
                "-f", f"q={query}",
                "-f", "sort=stars",
                "-f", "order=desc",
                "-f", "per_page=20",
            ])
        except Exception as e:  # noqa: BLE001
            print(f"[search] {query} failed: {e}", file=sys.stderr)
            continue
        try:
            data = json.loads(out)
        except json.JSONDecodeError:
            continue
        for repo in data.get("items", []):
            items.append({
                "source": "github",
                "subsource": "search",
                "label": s.get("label", ""),
                "url": repo["html_url"],
                "owner": repo["owner"]["login"],
                "name": repo["name"],
                "description": repo.get("description") or "",
                "language": repo.get("language") or "",
                "stars": repo.get("stargazers_count", 0),
                "forks": repo.get("forks_count", 0),
                "topics": repo.get("topics", []),
                "pushed_at": repo.get("pushed_at"),
            })
    return items


def fetch_awesome_updates(repos: list[str], days: int = 7) -> list[dict]:
    """Récupère les commits récents des awesome lists pour signaler des ajouts."""
    since = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
    items: list[dict] = []
    for slug in repos:
        try:
            out = gh([
                "api", "-X", "GET", f"repos/{slug}/commits",
                "-f", f"since={since}",
                "-f", "per_page=10",
            ])
            commits = json.loads(out)
        except Exception as e:  # noqa: BLE001
            print(f"[awesome] {slug} failed: {e}", file=sys.stderr)
            continue
        if not commits:
            continue
        items.append({
            "source": "github",
            "subsource": "awesome-list",
            "url": f"https://github.com/{slug}",
            "owner": slug.split("/")[0],
            "name": slug.split("/")[1],
            "description": f"{len(commits)} new commits in last {days}d",
            "language": "",
            "stars": 0,
            "recent_commits": [
                {
                    "sha": c["sha"][:7],
                    "message": (c.get("commit", {}).get("message") or "").split("\n")[0][:200],
                    "date": c.get("commit", {}).get("author", {}).get("date"),
                }
                for c in commits[:10]
            ],
        })
    return items


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--out", required=True)
    p.add_argument("--days", type=int, default=7)
    args = p.parse_args()

    cfg = load_yaml(CONFIG_DIR / "sources.yml")["github"]
    items: list[dict] = []

    print("[github] trending...", file=sys.stderr)
    items += fetch_trending(
        cfg["trending"]["languages"],
        cfg["trending"]["timeframes"],
        cfg["trending"]["min_stars_daily"],
        cfg["trending"]["min_stars_weekly"],
    )
    print(f"[github] trending: {len(items)} items", file=sys.stderr)

    print("[github] searches...", file=sys.stderr)
    items += fetch_searches(cfg.get("searches", []), days=args.days)

    print("[github] awesome lists...", file=sys.stderr)
    items += fetch_awesome_updates(cfg.get("awesome_lists", []), days=args.days)

    # Dédoublonne par URL en conservant le premier vu.
    seen: set[str] = set()
    deduped: list[dict] = []
    for it in items:
        if it["url"] in seen:
            continue
        seen.add(it["url"])
        deduped.append(it)

    out = Path(args.out)
    write_json(out, deduped)
    print(f"[github] wrote {len(deduped)} items to {out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
