---
name: daily-digest
description: Orchestre le pipeline complet de veille pour générer le digest du jour (collecte → analyse → résumé → blog). À utiliser pour /digest, déclenché manuellement ou via scheduled task.
---

# Skill : Daily Digest

Pipeline complet de génération du digest quotidien Agentic Radar.

## Procédure

Exécute strictement les étapes suivantes, en délégant à des sub-agents quand indiqué.

### 1. Préparation

```bash
DATE=$(date +%F)
mkdir -p content/raw/$DATE content/processed/$DATE
```

### 2. Collecte (en parallèle quand possible)

Délègue à 4 sub-agents :

- `github-collector` → écrit `content/sources/$DATE-github-*.md`
- `youtube-collector` → écrit `content/sources/$DATE-youtube-*.md`
- `reddit-collector` → écrit `content/sources/$DATE-reddit-*.md`
- `hackernews-collector` → écrit `content/sources/$DATE-hn-*.md`

Lance ces 4 agents **en parallèle** (1 seul message, 4 tool calls).

### 3. Blogs RSS

Exécute :

```bash
python scripts/collectors/blogs_rss.py --out content/raw/$DATE/blogs.json
```

Puis pour chaque entrée pertinente (filtrée par mots-clés agentiques), crée `content/sources/$DATE-blog-<slug>.md` avec le format standard.

### 4. Analyse

Délègue à `content-analyzer` — il lit tous les `content/sources/$DATE-*.md` et écrit :
- `content/processed/$DATE/analysis.md`
- `content/processed/$DATE/index.json`

### 5. Résumés

Délègue à `summarizer` — produit `content/processed/$DATE/summaries.md`.

### 6. Blog

Délègue à `blog-writer` — produit `content/blog/$DATE-digest.md`.

### 7. Rapport final

Affiche à l'utilisateur :
- chemin du digest généré
- nb d'items collectés / retenus
- top 3 items (titre + lien)
- patterns détectés

## Garde-fous

- Si **aucun** item n'est collecté (problème réseau, gh non authentifié), stoppe avec un message d'erreur clair et ne génère pas de blog vide.
- Si un collecteur échoue, continue avec les autres et mentionne l'échec dans le rapport final.
- Ne supprime jamais `content/sources/*.md` d'autres dates — seule la date du jour est en cours d'édition.

## Idempotence

Si `/digest` est relancé le même jour :
- les collecteurs doivent **dédoublonner** par URL avant d'écrire (déjà géré par chaque collecteur).
- `content/blog/$DATE-digest.md` est **écrasé** par la nouvelle version (volontaire).
