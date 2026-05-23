---
description: Publie le dernier digest (met à jour l'index et commit).
---

Utilise le skill `publish-blog` pour publier le digest le plus récent.

Étapes :
1. Identifier le dernier `content/blog/*-digest.md`
2. Mettre à jour `content/blog/README.md` (index chronologique inversé)
3. Afficher `git status` + `git diff --stat`
4. Demander confirmation à l'utilisateur
5. Si confirmé, commit (mais ne push pas automatiquement)
