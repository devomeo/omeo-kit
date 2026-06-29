---
description: Guide la création d'un endpoint API Ninja isolé et testé, puis le fait auditer
argument-hint: "<description de l'endpoint : ressource, action, paramètres>"
allowed-tools: Read, Grep, Glob, Bash, Agent, Skill
---

Aide à créer un nouvel endpoint API sur le CRM Omeo.app **sans fuite de données entre utilisateurs**
(risque n°1 du projet). L'objectif décrit par l'utilisateur : `$ARGUMENTS`.

## Étapes

1. **Appliquer la procédure `add-secure-endpoint`** (skill du plugin) : suivre l'ordre des couches
   schemas → services → api → tests, avec filtrage `owner`/`team` dans le service, `@has_perm` sur
   l'endpoint, `url_name`, et un **test d'isolation obligatoire** (utilisateur A ≠ données de B).
   Référence de bon filtrage à copier : `case/services.py::get_cases`.

2. **Proposer le code** des 4 couches (schéma, service, handler API, tests) prêt à relire — ne rien
   merger.

3. **Faire auditer** par l'agent `security-permissions`, puis demander à l'utilisateur de lancer
   `/omeo-review` avant la PR.

4. **Rappeler la validation** : `pytest`, `mypy src/`, `flake8`, `black --check .`, `isort --check-only .`.

## Rappel

L'humain valide et merge. Pour toute ambiguïté (la ressource est-elle partagée à l'échelle entreprise,
comme les contacts, ou isolée par propriétaire ?), poser la question plutôt que supposer.
