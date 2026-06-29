---
name: safe-data-migration
description: >
  Procédure pour écrire une migration de données (RunPython) sûre et réversible sur le CRM Omeo.
  À utiliser dès qu'une migration contient une transformation de données, et pas seulement un
  changement de schéma.
---

# Migration de données sûre

Le projet compte ~174 migrations. Certaines migrations de données existantes ne sont pas idempotentes
et ont un reverse `pass` (ex. `product/migrations/0070_*`). Ne reproduis pas ces défauts.

## Règles

1. **Générer via `makemigrations`** — jamais éditer/créer un fichier de migration à la main pour le
   schéma. Une migration par feature, nommée avec un suffixe explicite.
2. **Pas de logique métier durable dans la migration** : importer les modèles via `apps.get_model()`
   (état historique), pas via un import direct du modèle (qui évoluera).
3. **Idempotence** : la migration doit pouvoir être rejouée sans créer de doublon. Utiliser
   `get_or_create`, `update_or_create`, ou une garde `if not Model.objects.filter(...).exists()`.
4. **Reverse réel** : fournir une fonction `reverse_code` qui défait proprement le changement.
   Éviter le `pass` muet, sauf si l'opération est intrinsèquement irréversible — et alors le
   documenter explicitement.
5. **Pas de perte silencieuse** : si des lignes sont exclues/ignorées (ex. `category__isnull`), les
   compter et les logger.
6. **Soft-delete** : se rappeler que `.delete()` archive ; pour purger réellement utiliser
   `force_delete()`. Attention aux suppressions en CASCADE (ex. supprimer un User efface ses
   Cases/Contracts).

## Procédure

1. Stabiliser d'abord les modèles, puis `makemigrations`.
2. Écrire la `RunPython` avec `apps.get_model()`, idempotente, avec reverse réel.
3. **Dry-run** sur une copie de données (jamais directement en prod). Utiliser `pull_db` pour une
   copie locale si besoin.
4. Test d'idempotence : appliquer deux fois ne change pas le résultat (déléguer à qa-tests).
5. Validation + revue **qa-tests** et **architecte-django** via **/omeo-review**. Un humain valide,
   et c'est un humain qui exécute la migration en production.
