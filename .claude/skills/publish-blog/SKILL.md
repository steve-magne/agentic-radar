---
name: publish-blog
description: Publie un digest généré (commit git + push optionnel) et met à jour l'index. À utiliser après /digest.
---

# Skill : Publish Blog

Commit et publie un digest généré dans `content/blog/`.

## Procédure

1. Identifie le digest le plus récent : `ls -1 content/blog/*-digest.md | sort | tail -1`.
2. Met à jour `content/blog/README.md` (index chronologique inversé). Format :

```markdown
# Agentic Radar — Archive

| Date | Items retenus | Top du jour |
|------|---------------|-------------|
| [2026-05-23](2026-05-23-digest.md) | 12 | Anthropic ships subagent v2 |
| ... |
```

3. Affiche un `git status` + `git diff --stat` pour montrer les changements.
4. **Demande confirmation** à l'utilisateur avant de commit (sauf si déclenché par scheduled task non-interactive — dans ce cas, commit directement avec le message `chore(radar): digest YYYY-MM-DD [auto]`).
5. Si confirmé :
   ```bash
   git add content/blog/ content/sources/ content/processed/ content/raw/
   git commit -m "feat(radar): digest YYYY-MM-DD - {nb} items"
   ```
6. Ne **push pas** automatiquement — propose à l'utilisateur de le faire.

## Garde-fous

- Si rien à committer, dis-le et arrête.
- Ne commit jamais de fichiers en dehors de `content/`.
