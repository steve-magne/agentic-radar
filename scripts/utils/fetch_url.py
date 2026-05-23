"""Récupère et nettoie le contenu textuel d'une URL (article, page web).

Usage:
    python scripts/utils/fetch_url.py <url>

Sortie JSON sur stdout :
    {"url": "...", "title": "...", "text": "...", "site": "...", "byline": "..."}
"""

from __future__ import annotations

import argparse
import json
import sys

from common import http_get


def extract(url: str, max_chars: int = 8192) -> dict:
    resp = http_get(url)
    html = resp.text
    try:
        from readability import Document  # type: ignore
        from bs4 import BeautifulSoup

        doc = Document(html)
        title = doc.short_title()
        soup = BeautifulSoup(doc.summary(), "lxml")
        text = " ".join(soup.get_text(" ", strip=True).split())[:max_chars]
    except Exception:
        # Fallback minimal sans readability
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html, "lxml")
        title = (soup.title.string if soup.title else url).strip()
        text = " ".join(soup.get_text(" ", strip=True).split())[:max_chars]

    site = ""
    try:
        from urllib.parse import urlparse

        site = urlparse(url).netloc
    except Exception:
        pass
    return {"url": url, "title": title, "text": text, "site": site}


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("url")
    p.add_argument("--max-chars", type=int, default=8192)
    args = p.parse_args()
    data = extract(args.url, args.max_chars)
    json.dump(data, sys.stdout, ensure_ascii=False, indent=2)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
