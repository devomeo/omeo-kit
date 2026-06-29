---
description: Parcours d'onboarding d'un nouveau développeur sur le CRM Omeo (lecture, conventions, zones sensibles)
argument-hint: "[optionnel : domaine d'intérêt, ex. primes, signatures, panier]"
allowed-tools: Read, Grep, Glob, Bash, Agent, Skill
---

Accompagne l'onboarding d'un développeur sur le CRM Omeo.app afin qu'il devienne autonome sans
dépendre du développeur senior. Domaine d'intérêt éventuel : `$ARGUMENTS`.

## Étapes

1. **Dérouler la skill `onboarding-tour`** : ordre de lecture (`docs/domain.md` → `docs/architecture.md`
   → `CLAUDE.md` → `docs/ai-agents.md`), conventions clés (UUID, soft-delete, couches, tests, FR/EN),
   et les 5 zones sensibles avec leur skill associée.

2. **Si un domaine est précisé** (`$ARGUMENTS`), faire intervenir l'agent `conventions-doc` pour une
   visite guidée ciblée des fichiers pertinents (modèles, services, constants) et des pièges propres
   à ce domaine.

3. **Proposer un premier exercice à faible risque** : typiquement ajouter un test d'isolation manquant
   sur un endpoint existant, encadré par la skill `add-secure-endpoint` puis `/omeo-review`.

4. **Pointer les réflexes permanents** : lancer les 5 commandes de validation, et toujours `/omeo-review`
   avant une PR. Les agents proposent, l'humain valide et merge.
