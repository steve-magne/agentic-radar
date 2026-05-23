---
description: Lance le pipeline complet de veille (collecte → analyse → résumé → blog markdown) pour aujourd'hui ou la date passée en argument.
argument-hint: [YYYY-MM-DD]
---

Lance le skill `daily-digest` pour générer le digest agentique.

Date cible : `$ARGUMENTS` si non vide, sinon `$(date +%F)`.

Pipeline :
1. Crée `content/raw/<date>/` et `content/processed/<date>/`
2. Lance en parallèle les sub-agents `github-collector`, `youtube-collector`, `reddit-collector`, `hackernews-collector`
3. Exécute `python scripts/collectors/blogs_rss.py` pour les blogs RSS
4. Délègue à `content-analyzer` (tagging + détection de patterns)
5. Délègue à `summarizer` (résumés exécutifs)
6. Délègue à `blog-writer` (assemblage du digest final)

Affiche en sortie :
- chemin du digest généré
- nb d'items collectés / retenus
- top 3 + patterns détectés
