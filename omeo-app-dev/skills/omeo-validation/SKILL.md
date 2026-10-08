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

## Un test prouve un comportement, pas la présence d'une ligne

Préférer un test qui vérifie un **comportement** — le rendu d'une page, la réponse d'une route — à
un test qui cherche une chaîne dans le code source ou le gabarit. Réserver ce dernier à un bug
déjà rencontré, pour l'empêcher de revenir.

> Cas réel (ticket #1485) : neuf tests de gabarit ne vérifiaient que la présence de lignes. Les
> deux bugs du plein écran ont été trouvés à l'écran, pas par les tests.

## Passe de consolidation — relire son propre diff d'un bloc

Les commandes ci-dessus attrapent les erreurs de forme, pas les erreurs **d'accumulation**.

Une tâche se construit tour après tour. La duplication, le câblage redondant et le code mort ne
s'introduisent à aucun instant précis : ils s'installent entre deux demandes. Au moment d'écrire
le deuxième fichier, rien ne signale qu'il répète le premier. C'est ce qu'un relecteur qui
découvre le diff entier voit immédiatement, et que l'écriture au fil de l'eau ne voit jamais.

Avant de rendre la main, lire le diff complet de la branche **en une fois** — pas fichier par
fichier — et chercher :

- **de la duplication introduite par soi-même** : deux méthodes identiques écrites dans la même
  tâche se factorisent tout de suite. C'est différent d'une abstraction nouvelle par-dessus du
  code existant, qui elle est interdite en MR feature (voir `../../knowledge/senior-expectations.md`) ;
- **du câblage redondant** : un appel ajouté « par sécurité » alors qu'un événement existant le
  déclenchait déjà. Tracer le câblage en place avant d'ajouter le sien ;
- **du code mort** : garde, état ou variable devenus inutiles au fil des itérations ;
- **des incohérences entre fichiers** : même donnée lue depuis deux sources, même valeur arrondie
  de deux façons ;
- **les corrections antérieures qui n'auraient pas survécu** : sur une longue session, un revert
  ou une réécriture peut réintroduire un bug déjà corrigé. Vérifier que les correctifs du début
  sont toujours en place.

## Symptôme ou cause ?

Avant d'accepter un correctif : **explique-t-il tout le comportement observé, ou le fait-il
seulement disparaître ?**

Un correctif qui consiste à ajouter un rafraîchissement, un `upsert`, un garde ou un second appel
est un signal : la cause est probablement en amont. Remonter avant de valider.

## Troisième itération sur un même écran : repartir du besoin

C'est la même question que la précédente, à l'échelle d'une conception plutôt que d'un correctif.
La passe de consolidation trouve ce qui est redondant dans le diff ; elle ne demande pas si le
mécanisme lui-même est le bon.

Dès la troisième itération sur un même écran ou un même comportement, s'arrêter et :

1. reformuler le besoin final, tel qu'il est maintenant connu ;
2. décrire le mécanisme le plus simple qui le couvre — en commençant par le natif du navigateur
   (voir la skill **omeo-front**) ;
3. lister ce qui, dans le code actuel, n'est plus nécessaire avec ce mécanisme ;
4. proposer la refonte avant de continuer à empiler.

> Cas réel (ticket #1485) : pagination animée, puis swipe manuel, puis défilement natif sur
> téléphone, puis boutons — quatre mécanismes superposés, que le défilement natif seul remplaçait.

Voir aussi « Modèle à reproduire, mais aussi suspect possible » dans la skill
**omeo-preconditions** : auditer ce qu'on a déjà écrit vaut autant que d'auditer l'existant.

## Avant de déclarer terminé

1. Les commandes CI ci-dessus passent.
2. Les échecs restants sont **nommés** et rattachés à un écart connu du tableau, ou prouvés
   préexistants (`git stash` puis relance).
3. Un échec qu'on ne sait pas expliquer n'est jamais « sans rapport ». Le prouver ou le corriger.
4. La passe de consolidation a été faite sur le diff complet.
5. Un comportement front a été vérifié dans le navigateur, onglet au premier plan — sinon le dire
   (voir la skill **omeo-front**).
6. La fiche de la tâche dans la gestion de projet Notion est à jour : statut, livré, décisions,
   points ouverts, validation — y compris ce qui n'a pas pu être vérifié (skill **omeo-notion**).
7. Ce que le diff ne rend pas évident est dit explicitement. Un relecteur qui demande « c'est
   quoi ? » ou qui signale un point déjà traité indique que le diff ne se lisait pas seul.
