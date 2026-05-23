---
description: Affiche l'état du radar (dernier digest, nb d'items collectés, sources configurées, prochaine collecte planifiée).
---

Affiche un état synthétique du radar :

1. Dernier digest publié : `ls -1t content/blog/*-digest.md | head -1`
2. Nb total d'items dans `content/sources/` (par source : github, youtube, reddit, hn, blog, manual)
3. Nb d'items des 7 derniers jours
4. Sources configurées dans `config/sources.yml` (counts par catégorie)
5. Tâche planifiée Claude Code active si `mcp__scheduled-tasks__list_scheduled_tasks` est disponible
6. État de `gh auth status` et présence de `yt-dlp`

Sortie sous forme de tableau compact.
