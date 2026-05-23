# Agentic Radar

Système de veille technologique **agentique** pour l'écosystème AI engineering, conçu avec les **capacités natives de Claude Code** :

- **Sub-agents** spécialisés (collecte, analyse, rédaction)
- **Agent Skills** réutilisables (ingestion, digest, publication)
- **Slash commands** pour pilotage manuel
- **Scheduled tasks** pour automatisation quotidienne

Aucune base de données. Tout est stocké en **markdown / YAML / JSON** dans le repo, lisible par humain et agent.

## Objectifs

Construire une mémoire vivante et croissante autour de :

- apprentissage continu (Claude Code, Codex, Antigravity, LLMs)
- veille technologique (frameworks, outils, protocoles : MCP, A2A)
- benchmark d'outils
- découverte de patterns agentiques
- capitalisation de connaissances
- création de contenu futur (blog)

## Architecture

```
agentic-radar/
├── .claude/
│   ├── agents/           # Sub-agents spécialisés
│   │   ├── github-collector.md
│   │   ├── youtube-collector.md
│   │   ├── reddit-collector.md
│   │   ├── hackernews-collector.md
│   │   ├── content-analyzer.md
│   │   ├── summarizer.md
│   │   └── blog-writer.md
│   ├── skills/           # Skills réutilisables
│   │   ├── ingest-url/
│   │   ├── daily-digest/
│   │   └── publish-blog/
│   └── commands/         # Slash commands
│       ├── ingest.md     # /ingest <url>
│       ├── digest.md     # /digest [date]
│       └── publish.md    # /publish
├── config/
│   ├── sources.yml       # Sources surveillées
│   ├── tags.yml          # Taxonomie de tags
│   └── channels.yml      # YouTube / Reddit / X
├── scripts/
│   ├── collectors/       # Collecteurs Python (API/RSS)
│   │   ├── github_trending.py
│   │   ├── youtube_feed.py
│   │   ├── reddit_feed.py
│   │   └── hackernews.py
│   └── utils/
│       ├── fetch_url.py  # Récupère contenu d'une URL
│       └── dedupe.py     # Dédoublonnage par hash d'URL
├── content/
│   ├── sources/          # Items bruts collectés (par source)
│   ├── raw/YYYY-MM-DD/   # Snapshot quotidien brut
│   ├── processed/        # Items analysés + taggés
│   └── blog/             # Articles markdown publiés
└── pyproject.toml
```

## Flux de données

### Flux automatique (quotidien)

```
scheduled-task → /digest
  ├─ github-collector   → content/raw/YYYY-MM-DD/github.json
  ├─ youtube-collector  → content/raw/YYYY-MM-DD/youtube.json
  ├─ reddit-collector   → content/raw/YYYY-MM-DD/reddit.json
  └─ hackernews-collector → content/raw/YYYY-MM-DD/hackernews.json
       │
       ▼
  content-analyzer  → content/processed/YYYY-MM-DD/items.md (tagged, scored)
       │
       ▼
  summarizer        → résumés courts/techniques par item
       │
       ▼
  blog-writer       → content/blog/YYYY-MM-DD-digest.md
```

### Flux manuel

```
/ingest <url>
  → fetch_url + content-analyzer + summarizer
  → content/sources/YYYY-MM-DD-<slug>.md
```

## Utilisation

### Manuelle (Claude Code)

```bash
# Ingérer un article ou une vidéo
/ingest https://www.anthropic.com/news/...

# Générer le digest du jour
/digest

# Publier le digest
/publish
```

### Automatique

Via **scheduled task** Claude Code (voir `config/schedule.yml`) ou GitHub Actions (`.github/workflows/daily_update.yml`).

## Stack

- **Python 3.12** + `uv` pour les collecteurs
- **gh CLI** pour GitHub
- **RSS / API publiques** pour YouTube, Reddit, HN
- **Claude Code** pour orchestration, analyse, rédaction

## Démarrage

```bash
uv sync
gh auth status              # GitHub CLI authentifié
python scripts/collectors/github_trending.py  # test collecteur
```

Puis dans Claude Code :

```
/digest
```
