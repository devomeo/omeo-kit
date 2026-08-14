---
name: omeo-validation
description: >
  Commandes de validation réellement appliquées par la CI du CRM Omeo, et écarts connus avec
  l'environnement local. À utiliser avant de déclarer une tâche terminée, avant un commit, ou
  dès qu'un échec local semble sans rapport avec la modification en cours.
---

# Valider comme la CI, pas comme on croit

`CLAUDE.md` prescrit un jeu de commandes qui **ne correspond pas** à ce que la CI applique.
Suivre `CLAUDE.md` à la lettre produit aujourd'hui trois faux signaux. Ce document fait foi.

## Ce que la CI exige réellement

Source : `.gitlab-ci.yml`.

```bash
flake8 src/
black --check src/
isort --check-only src/
coverage run -m pytest --tb=short
```

**Il n'y a aucun job mypy.** Des erreurs mypy préexistantes traînent dans le dépôt ; elles ne
bloquent rien et ne doivent pas être corrigées à l'occasion d'une MR feature.

## Écarts locaux connus — ne pas s'y user

| Symptôme local | Cause | Conduite |
|---|---|---|
| `mypy` s'arrête sur `Could not find the GDAL library` | GDAL absent en local | Ne pas insister ; contourner avec `django_settings_module = tests.settings` dans une copie de `mypy.ini` si un contrôle ponctuel est vraiment nécessaire |
| `black --check .` signale 2 fichiers | `tests/project/test_signals.py` et `tests/account/test_api.py`, préexistants et hors périmètre CI | Ignorer ; valider sur `src/` |
| `tests/commission` ne se collecte pas | `ModuleNotFoundError: No module named 'psycopg'` en local | Exclure du run local, la CI l'exécute |
| Échecs dans `tests/bilan`, `tests/case/builder`, `tests/case/pdf` | Fichiers de tests **non suivis** par git, propres au poste | Vérifier `git status` avant de conclure à une régression |

## Le piège de périmètre

Valider `src/apps/<mon_app>` pendant que la CI valide `src/` a déjà laissé passer une pipeline
rouge (trois `F811` après une résolution de conflit). **Le périmètre de validation doit être celui
de la CI, jamais celui de la modification.**

## Commande locale complète

```bash
set -a && source .env-test && set +a

DJANGO_SETTINGS_MODULE=tests.settings PYTHONPATH=src:src/apps:. \
  poetry run python -m pytest tests/ -q -p no:warnings

poetry run flake8 src/
poetry run black --check src/
poetry run isort --check-only src/
```

Si un fichier de test a été ajouté, le passer aussi à `flake8` / `black` / `isort` même s'il est
hors `src/` : la cohérence du dépôt le vaut, mais un échec sur un fichier préexistant qu'on n'a
pas touché n'est pas un motif pour élargir la MR.

## Avant de déclarer terminé

1. Les commandes CI ci-dessus passent.
2. Les échecs restants sont **nommés** et rattachés à un écart connu du tableau, ou prouvés
   préexistants (`git stash` puis relance).
3. Un échec qu'on ne sait pas expliquer n'est jamais « sans rapport ». Le prouver ou le corriger.
