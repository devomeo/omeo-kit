---
name: onboarding-tour
description: >
  Parcours d'onboarding guidé d'un nouveau développeur sur le CRM Omeo. À utiliser quand un dev
  rejoint le projet ou veut une vue d'ensemble des zones sensibles et des conventions avant de
  contribuer.
---

# Onboarding développeur — Omeo.app

Objectif : rendre un nouveau développeur autonome et prudent, sans dépendre du développeur senior.

## 1. Lecture (dans cet ordre)

1. `docs/domain.md` — entités et vocabulaire métier (Affaire, Prime, Contrat, déballe…).
2. `docs/architecture.md` — ordre des couches, `AbstractModel`, permissions, tests.
3. `CLAUDE.md` — commandes, conventions strictes.
4. `docs/ai-agents.md` — bonnes pratiques d'intervention assistée.

## 2. Conventions à intégrer absolument

- PK = **UUID** partout. **Soft-delete** : `.delete()` archive (ne supprime pas).
- Logique métier **uniquement** dans `services.py`. Couches : schemas → services → api → tasks →
  signals → views → tests.
- Tests = fonctions, nommage `test_<fn>_<scénario>_<résultat>`. Env : `.env-dev`/`.env-test`.
- FR pour l'utilisateur, EN pour le code.

## 3. Les 5 zones sensibles (où l'on casse facilement)

1. **Accès aux données** : `has_perm` = niveau modèle seulement ; toujours filtrer par `owner`/`team`
   dans le service + test d'isolation. → skill `add-secure-endpoint`.
2. **Prix / primes / prêts** : calculs faux silencieux ; encodage `"l1-l2-l3-l4"`. → skill `add-business-calc`.
3. **Déballes versionnées** : chaque version est une offre distincte ; danger des managers `common`.
   → skill `touch-step-version`.
4. **Intégrations externes** : Yousign/Enedis/PVGIS/banques. → skill `external-integration`.
5. **Signaux** : effets de bord globaux (dont fuite PostHog à corriger). → skill `add-or-edit-signal`.

## 4. Mise en pratique

- Lancer les 5 commandes de validation pour voir l'état : `pytest`, `mypy src/`, `flake8`,
  `black --check .`, `isort --check-only .`.
- Premier exercice recommandé (faible risque) : ajouter un test d'isolation manquant sur un endpoint
  existant, en suivant `add-secure-endpoint` puis `/omeo-review`.

## 5. Réflexe permanent

Avant toute PR : `/omeo-review`. Les agents proposent, **l'humain valide et merge**.
