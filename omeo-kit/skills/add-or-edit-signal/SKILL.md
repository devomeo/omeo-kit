---
name: add-or-edit-signal
description: >
  Procédure pour ajouter ou modifier un signal Django sur le CRM Omeo sans créer d'effet de bord
  caché, de boucle, ni de fuite de données. À utiliser sur tout diff touchant un signals.py ou
  core/signals.py / core/metrics.py.
---

# Ajouter ou modifier un signal

Les signaux créent des effets de bord invisibles depuis le code appelant. Sur Omeo, ils sont déjà
nombreux et l'un d'eux fuit des données.

## Contexte à connaître

- `core/signals.py::register_model_signals` branche `post_save`/`post_delete` sur **tous** les
  modèles pour envoyer un événement à PostHog. **Problème connu à corriger** : `handle_model_event`
  envoie `instance.__dict__` (sauf clés `_…`), donc des champs sensibles (ex. `password` du modèle
  `User`) partent vers PostHog. Tout nouveau champ sensible aggrave la fuite.
- `case/signals.py` crée un Projet quand une affaire passe à `signed`.
- `contract/signals.py` resynchronise une date à chaque save de Step (risque N+1 sur bulk).

## Règles

1. **La logique vit dans un service**, pas dans le handler. Le signal est un wrapper fin qui appelle
   `services.<fonction>(instance)` (cf. `docs/architecture.md`).
2. **Idempotence** : le handler peut se déclencher plusieurs fois — protéger contre les doublons
   (ex. `get_or_create`, garde `if not exists`).
3. **Pas de boucle** : si le handler `save()` l'objet écouté, il se re-déclenche. Utiliser
   `update_fields`, `QuerySet.update()`, ou une garde d'état.
4. **Pas de fuite** : ne jamais sérialiser `instance.__dict__` en aveugle vers un service externe.
   Lister explicitement les champs autorisés (allowlist), exclure tout champ sensible.
5. **Performance bulk** : attention aux `bulk_create`/`bulk_update` qui contournent ou multiplient
   les signaux.

## Procédure

1. Écrire/modifier la logique dans `services.py`.
2. Brancher le signal dans `signals.py`, l'enregistrer via `apps.py::ready()`.
3. Tester : déclenchement, idempotence (rejouer ne duplique pas), absence de fuite.
4. Documenter le signal dans le catalogue des effets de bord (agent conventions-doc).
5. Validation + revue **security-permissions** (fuite) et **architecte-django** (effet de bord) via
   **/omeo-review**. Un humain valide.
