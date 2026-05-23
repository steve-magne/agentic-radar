---
name: ingest-url
description: Ingère une URL unique (article, vidéo YouTube, repo GitHub, tweet, thread Reddit/HN) dans Agentic Radar. Utilise ce skill quand l'utilisateur donne un lien à archiver/analyser dans la veille, par exemple "/ingest <url>" ou "regarde cet article et ajoute-le au radar".
---

# Skill : Ingest URL

Ce skill ingère manuellement une ressource dans le radar de veille.

## Quand l'utiliser

L'utilisateur fournit une URL et veut l'ajouter à la veille agentique :
- article de blog
- vidéo YouTube
- repo GitHub
- thread Reddit / HN
- post X/Twitter (texte fourni par l'utilisateur si l'URL ne se résout pas)

## Procédure

1. **Détecte le type de source** à partir du domaine :
   - `github.com/<owner>/<repo>` → github
   - `youtube.com/watch` ou `youtu.be/` → youtube
   - `reddit.com/r/.../comments/...` → reddit
   - `news.ycombinator.com/item?id=...` → hackernews
   - sinon → blog/article générique

2. **Récupère le contenu** :
   - github : `gh api repos/<owner>/<repo>` puis `gh api repos/<owner>/<repo>/readme --jq .download_url | xargs curl -sL | head -c 8192`
   - youtube : `yt-dlp --dump-json <url>` (titre, durée, description) + tente transcript via `yt-dlp --write-auto-sub --skip-download`. Si `yt-dlp` absent, prends juste les métadonnées affichées par WebFetch.
   - reddit : `curl -s -A "agentic-radar/1.0" <url>.json` puis prends `data.children[0].data`
   - hackernews : extrait l'id de l'URL, puis `curl -s https://hacker-news.firebaseio.com/v0/item/<id>.json`
   - blog : `python scripts/utils/fetch_url.py <url>` → renvoie titre + texte nettoyé (8 KB max)

3. **Analyse le contenu** :
   - choisis 1-4 tags pertinents depuis `config/tags.yml > categories`
   - estime complexity et importance (cf. `importance_scoring`)
   - rédige : TL;DR (1 phrase), 3 bullets techniques, 1 ligne cas d'usage

4. **Vérifie la non-duplication** : `grep -r "url: <URL>" content/sources/` — si trouvé, dis-le et propose à l'utilisateur de **rafraîchir** l'item existant plutôt que d'en créer un nouveau.

5. **Écris le markdown** dans `content/sources/YYYY-MM-DD-manual-<slug>.md` avec le frontmatter standard :

```yaml
---
source: github | youtube | reddit | hackernews | blog
url: <URL>
title: ...
collected_at: <ISO timestamp>
ingested_by: manual
tags: [...]
complexity: intermediate
importance: 7
---
```

6. **Affiche en sortie** : chemin du fichier créé + résumé en 3 lignes pour confirmer à l'utilisateur ce qui a été retenu.

## Note importante

Ne déclenche **pas** automatiquement `/digest` ni `/publish` — laisser cela à l'utilisateur. Ce skill ne fait qu'**ingérer** un item dans `content/sources/`.

L'item sera repris par le prochain `/digest`.
