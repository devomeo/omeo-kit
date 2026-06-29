---
description: Revue multi-agents du diff courant (sécurité, métier, archi, front, QA) → verdict priorisé
argument-hint: "[optionnel : chemin/fichier ou base de comparaison, ex. develop]"
allowed-tools: Read, Grep, Glob, Bash, Agent
---

Lance une revue complète du code en cours de modification sur le CRM Omeo.app, en orchestrant les
agents spécialisés du plugin, et produis un **verdict unique priorisé** destiné à l'humain.

## Étapes

1. **Déterminer le périmètre du diff.** Par défaut, comparer à `develop` (branche de base des
   features). Si un argument est fourni (`$ARGUMENTS`), l'utiliser comme base de comparaison ou
   restreindre au(x) fichier(s) indiqué(s). Utiliser `git diff` pour lister les fichiers touchés.
   Si le dépôt n'est pas un dépôt git exploitable, demander à l'utilisateur le périmètre à revoir.

2. **Lancer en parallèle les agents spécialisés pertinents** (et seulement ceux-là), selon les
   fichiers touchés. Émettre les appels d'agents dans un même message pour qu'ils s'exécutent
   concurremment :
   - `*/api.py`, `*/services.py`, `settings.py`, signaux, webhooks, intégrations → **security-permissions**
   - `product/`, `case/cart/`, `case/prime/`, `case/loan/`, calculs financiers → **backend-metier**
   - diff transverse, signaux, `case/steps/structures.py`, managers `common` → **architecte-django**
   - `*/templates/`, `src/static/js/`, `theme/` → **frontend-alpine**
   - tout service, migration de données, endpoint → **qa-tests**
   - conventions implicites / doc manquante → **conventions-doc**
   Ne pas lancer un agent hors de son périmètre (ex. pas de frontend-alpine sur un diff purement backend).

3. **Confier la synthèse à l'agent `reviewer-final`** en lui transmettant le périmètre du diff et les
   constats remontés par chaque agent spécialisé. Il agrège, dédoublonne et priorise (il ne relance
   pas d'agents).

4. **Restituer le verdict** au format de `reviewer-final` :
   - 🔴 Bloquants · 🟠 À corriger · 🟡 Suggestions · « À vérifier humainement »
   - chaque item : `fichier:ligne`, agent source, risque, correction, confiance (confirmé/à vérifier).

## Rappels

- Tout est en lecture seule : la revue **propose**, elle ne modifie ni ne merge rien.
- La décision finale et toute ambiguïté produit/réglementaire reviennent à l'humain.
