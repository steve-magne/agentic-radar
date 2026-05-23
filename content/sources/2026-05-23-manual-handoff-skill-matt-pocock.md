---
source: youtube
url: https://www.youtube.com/watch?v=dtAJ2dOd3ko
title: "/handoff is my new favourite skill"
collected_at: 2026-05-23T16:51:14Z
ingested_by: manual
tags: [coding-agent, orchestration, skill-plugin]
complexity: intermediate
importance: 8
---

**TL;DR** : Matt Pocock présente `/handoff`, un skill Claude Code qui permet de transmettre le contexte d'une session à une nouvelle instance d'agent — solution élégante au problème de contexte saturé.

## Points clés

- `/handoff` génère un résumé structuré de la session en cours (état, décisions, prochaines étapes) et l'injecte dans une nouvelle session propre
- Évite le degradation de qualité liée au context window plein tout en préservant la continuité du travail
- Pattern applicable à des workflows longs (refactoring massif, feature multi-étapes) où l'agent doit "passer le relais" à lui-même

## Cas d'usage

Idéal pour les sessions de coding agent dépassant la fenêtre de contexte : refactorisations longues, migrations de codebase, ou tout flux multi-session nécessitant une continuité explicite.
