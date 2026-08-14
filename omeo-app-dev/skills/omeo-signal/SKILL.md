---
name: omeo-signal
description: >
  Procédure pour ajouter ou modifier un signal Django sur le CRM Omeo sans créer d'effet de bord
  caché, de boucle ni de fuite de données. À utiliser sur tout diff touchant un signals.py,
  core/metrics.py, ou un apps.py qui enregistre des signaux.
---

# Ajouter ou modifier un signal

Les signaux produisent des effets invisibles depuis le code appelant. Six apps en déclarent :
`account`, `case`, `commission`, `contract`, `core`, `project`.

## Le point le plus important : tous les modèles sont déjà écoutés

`src/apps/core/signals.py:27` (`register_model_signals`) branche `post_save` **et** `post_delete`
sur **tous** les modèles retournés par `apps.get_models()`. Chaque nouveau modèle est donc
automatiquement instrumenté, sans que personne ne l'ait décidé.

Le handler (`core/signals.py:7`) construit ses propriétés ainsi :

```python
properties = {
    key: value
    for key, value in instance.__dict__.items()
    if not key.startswith("_")
}
```

**C'est une sérialisation en aveugle de tous les champs concrets du modèle**, envoyée à PostHog.
Le mot de passe haché du modèle `User` en fait partie.

Portée exacte, vérifiée : `POSTHOG_ENABLED = settings.STAGE == "live" and bool(POSTHOG_API_KEY)`
(`core/metrics.py:9`). L'envoi réseau n'a donc lieu qu'en production avec une clé configurée.
**Mais lorsque c'est désactivé, les mêmes propriétés partent dans les logs** via
`logger.debug(f"Properties: {properties}")` (`core/metrics.py:36`). Il n'existe pas de
configuration où ces données ne sortent nulle part.

**Conséquence pratique** : tout nouveau champ sensible ajouté à n'importe quel modèle aggrave
l'exposition, sans une ligne de code à écrire. Le signaler quand ça arrive.

## Règles

1. **La logique vit dans un service.** Le handler est un wrapper fin qui appelle
   `services.<fonction>(instance)`. Voir `docs/architecture.md`.
2. **Idempotence** : un handler peut se déclencher plusieurs fois. Protéger par `get_or_create`
   ou une garde d'état.
3. **Pas de boucle** : si le handler `save()` l'objet écouté, il se redéclenche. Utiliser
   `update_fields`, `QuerySet.update()`, ou une garde.
4. **Jamais de sérialisation en aveugle vers un service externe.** Lister explicitement les champs
   autorisés.
5. **Opérations en masse** : `bulk_create` / `bulk_update` **ne déclenchent pas** `post_save`. Un
   traitement qui repose sur un signal sera silencieusement ignoré en bulk — et à l'inverse, une
   boucle de `save()` sur un gros volume multiplie les appels PostHog.

## Procédure

1. Écrire la logique dans `services.py`.
2. Brancher le signal dans `signals.py`, enregistré via `apps.py::ready()`.
3. Tester le déclenchement, l'idempotence (rejouer ne duplique pas), et l'absence de fuite.
4. Validation : voir la skill **omeo-validation**.
