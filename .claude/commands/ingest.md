---
description: Ingère une URL (article, vidéo YouTube, repo GitHub, thread Reddit/HN) dans le radar de veille agentique.
argument-hint: <url>
---

Utilise le skill `ingest-url` pour ingérer l'URL suivante dans Agentic Radar : `$ARGUMENTS`.

Étapes :
1. Détecter le type de source
2. Récupérer le contenu (gh / yt-dlp / curl / scripts/utils/fetch_url.py)
3. Analyser, tagger, scorer
4. Vérifier la non-duplication contre `content/sources/`
5. Écrire le fichier markdown dans `content/sources/`

Affiche en sortie le chemin du fichier créé et un résumé de 3 lignes.
