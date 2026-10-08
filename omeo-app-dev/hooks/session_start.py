#!/usr/bin/env python3
"""Rappel de début de session omeo-app-dev.

Déclenché en SessionStart : dans le dépôt du CRM Omeo seulement, rappelle que la
fiche de la tâche dans la gestion de projet Notion se lit au début et se met à jour
avant de déclarer la tâche terminée. Silencieux partout ailleurs. Ne bloque jamais.
"""

import json
import os
import sys

REMINDER = (
    "[omeo-app-dev] Gestion de projet Notion — obligatoire pour CHAQUE tâche sur le CRM Omeo : "
    "retrouver ou créer la fiche de la tâche dans la base « Gestion de projet » "
    "(https://app.notion.com/p/3f265dd62c8f806db4e3dd195d776c26) en suivant les instructions "
    "de cette page, la lire avant d'écrire du code, et la mettre à jour (statut, livré, "
    "décisions, points ouverts) avant de déclarer la tâche terminée. Documentation de l'app "
    "par module et Documentation Dev : skill omeo-app-dev:omeo-notion."
)


def is_crm_repo(cwd):
    return os.path.isfile(os.path.join(cwd, "src", "manage.py")) and os.path.isdir(
        os.path.join(cwd, "src", "apps", "case")
    )


def main():
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    if not isinstance(payload, dict):
        return 0

    cwd = payload.get("cwd") or os.getcwd()
    if not is_crm_repo(cwd):
        return 0

    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": REMINDER,
            }
        },
        sys.stdout,
        ensure_ascii=False,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
