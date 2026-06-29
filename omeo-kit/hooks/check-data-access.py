#!/usr/bin/env python3
"""omeo-kit — rappel sécurité non bloquant.

Hook PostToolUse : après chaque édition d'un fichier sensible (api.py, signals.py,
settings.py), injecte un rappel des réflexes de sécurité dans le contexte de l'agent.
Ne bloque JAMAIS l'édition : en cas d'erreur, sort silencieusement avec le code 0.
"""
import json
import sys


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return  # entrée illisible : ne rien faire, ne pas bloquer

    tool_input = payload.get("tool_input") or {}
    file_path = (tool_input.get("file_path") or "").replace("\\", "/")

    reminder = None
    if file_path.endswith("/api.py") or file_path.endswith("api.py"):
        reminder = (
            "Rappel omeo-kit (sécurité) : cet endpoint expose-t-il des données ? "
            "Si oui → @has_perm(['app.codename']) + filtrage owner/team dans le service "
            "(cf. case/services.py::get_cases) + un test d'isolation (utilisateur A ≠ "
            "données de B). has_perm ne contrôle QUE le niveau modèle, pas la propriété "
            "de l'objet. Voir la skill add-secure-endpoint, puis /omeo-review."
        )
    elif file_path.endswith("signals.py"):
        reminder = (
            "Rappel omeo-kit (effets de bord) : logique dans un service, idempotence, "
            "pas de boucle de save, et ne jamais sérialiser instance.__dict__ vers un "
            "service externe (fuite PostHog connue). Voir la skill add-or-edit-signal."
        )
    elif file_path.endswith("settings.py"):
        reminder = (
            "Rappel omeo-kit (config) : attention à CORS_ALLOW_ALL_ORIGINS, au fallback "
            "SECRET_KEY, et à toute route ajoutée à LOGIN_EXEMPT_URLS (surface publique)."
        )

    if reminder:
        print(
            json.dumps(
                {
                    "hookSpecificOutput": {
                        "hookEventName": "PostToolUse",
                        "additionalContext": reminder,
                    }
                }
            )
        )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        pass  # garde-fou ultime : ne jamais faire échouer le hook
    sys.exit(0)
