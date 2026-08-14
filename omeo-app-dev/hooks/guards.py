#!/usr/bin/env python3
"""Garde-fous omeo-app-dev.

Déclenché en PreToolUse sur Edit/Write/MultiEdit : injecte le contenu utile AVANT
l'écriture, plutôt que de nommer une skill après coup.

Silencieux quand aucune règle ne correspond. Ne bloque jamais.
"""

import json
import os
import re
import sys

PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KNOWLEDGE = os.path.join(PLUGIN_ROOT, "knowledge")


def source_knowledge():
    """Dossier knowledge du clone git, seul endroit où une écriture survit.

    Une copie installée vit dans plugins/cache/<marketplace>/<plugin>/<version>/ :
    chaque version obtient un nouveau dossier, donc tout ce qui y est écrit est
    perdu à la mise à jour suivante. La source est le clone git, sous
    plugins/marketplaces/<marketplace>/<plugin>/.
    """
    parts = PLUGIN_ROOT.split(os.sep)
    if len(parts) >= 5 and parts[-4] == "cache":
        candidate = os.sep.join(
            parts[:-4] + ["marketplaces", parts[-3], parts[-2], "knowledge"]
        )
        if os.path.isdir(candidate):
            return candidate
    return None


def registry(name):
    return os.path.join(KNOWLEDGE, name)


RULES = [
    {
        "match": r"/api\.py$",
        "skill": "omeo-app-dev:omeo-endpoint",
        "message": (
            "Route API. @has_perm(['<app>.<codename>']) est obligatoire sur toute route de "
            "données, ET le service doit filtrer par propriétaire — les deux, pas l'un ou "
            "l'autre. Un test d'isolation est requis : la fixture est api_client(router, "
            "user=...) et SANS argument user elle crée un superutilisateur, ce qui masque "
            "exactement ce que le test doit prouver.\n"
            "Ne pas justifier une route non protégée par la parité avec ses voisines : "
            "~42 routes sur 164 vivent dans des modules sans un seul has_perm, et c'est "
            "précisément le voisinage de case/*."
        ),
        "files": ["case-cart.md"],
    },
    {
        "match": r"/case/steps/(forms|managers|schemas)/version_\d+\.py$|/case/steps/structures\.py$",
        "skill": "omeo-app-dev:omeo-step-version",
        "message": (
            "Étape versionnée. Avant d'écrire : localiser la même logique dans la dernière "
            "version ACTIVE et citer son fichier:ligne. C'est la première cause de reprise en "
            "revue sur ce projet.\n"
            "Réordonner des étapes n'est sûr que si la structure est active=False, et si aucune "
            "étape déplacée ne lit les données d'une étape devenue postérieure.\n"
            "Vérifier aussi les includes NON versionnés de l'Aperçu : ils ne suivent pas un "
            "changement de source de donnée."
        ),
        "files": ["case-steps.md", "senior-expectations.md"],
    },
    {
        "match": r"/templates/case_steps/version_\d+/[\w-]+\.html$",
        "skill": "omeo-app-dev:omeo-step-version",
        "message": (
            "Gabarit d'étape versionné. S'il s'agit d'une création, le comparer d'abord à son "
            "équivalent dans case_steps/common/ : un gabarit versionné identique au partagé "
            "n'apporte rien et a déjà été supprimé en revue.\n"
            "Rappel de rendu : {{ field.value|default:\"\" }} applique le filtre Django à toute "
            "valeur falsy, donc initial=0 arrive dans Alpine comme une chaîne vide."
        ),
        "files": ["case-steps.md"],
    },
    {
        "match": r"/signals\.py$|/core/metrics\.py$",
        "skill": "omeo-app-dev:omeo-signal",
        "message": (
            "Signal. core/signals.py branche post_save ET post_delete sur TOUS les modèles, et "
            "le handler sérialise instance.__dict__ en aveugle vers PostHog (mot de passe haché "
            "du modèle User compris). Tout nouveau champ sensible aggrave l'exposition sans une "
            "ligne à écrire.\n"
            "La logique va dans un service ; le handler reste un wrapper fin. Vérifier "
            "l'idempotence et l'absence de boucle. bulk_create/bulk_update ne déclenchent pas "
            "post_save."
        ),
        "files": [],
    },
    {
        "match": r"/(product|case/cart|case/prime|case/loan)/.*\.py$",
        "skill": "omeo-app-dev:omeo-business-calc",
        "message": (
            "Calcul métier. Une erreur ici ne plante pas : elle sort un mauvais montant sur un "
            "devis client.\n"
            "price_by_level (product/utils.py:4) indexe sans borne : un niveau supérieur au "
            "nombre de segments lève IndexError, et un niveau à 0 renvoie SILENCIEUSEMENT le "
            "dernier segment.\n"
            "Un token de formule inconnu est remplacé par 0 sans erreur : un 0 signifie le plus "
            "souvent « formulaire non rempli », pas « gratuit ».\n"
            "Toute valeur réglementaire modifiée exige sa source officielle et sa date d'effet."
        ),
        "files": ["case-cart.md"],
    },
]

PRECONDITIONS = (
    "Préconditions — elles valent pour tout fichier, avant d'écrire :\n"
    "  1. Citer le fichier:ligne de l'équivalent dans la dernière version ACTIVE. "
    "C'est la première cause de reprise en revue sur ce projet : une logique écrite "
    "côté service alors que la version précédente la traitait en template a coûté une "
    "implémentation, un revert complet et deux allers-retours. Le lire comme modèle, "
    "mais aussi comme suspect : si le symptôme traverse une primitive existante, "
    "l'auditer AVANT de patcher autour — patcher autour d'un code supposé correct a "
    "déjà produit un moins bon correctif que l'audit.\n"
    "  2. Grepper tout identifiant nouveau. Sans précédent dans le dépôt, soit le "
    "concept existe sous un autre nom, soit on en introduit un — et cela se signale.\n"
    "  3. Si une fonction existante sert de modèle, la differ et justifier CHAQUE "
    "argument omis. Un `user` oublié en recopiant la mauvaise fonction a fait tomber "
    "un endpoint en 500 sur la majorité des produits réels.\n"
    "Procédure complète : skill omeo-app-dev:omeo-preconditions"
)

VALIDATION_HINT = (
    "Validation : la CI applique flake8 src/, black --check src/, isort --check-only src/ et "
    "pytest. Il n'y a AUCUN job mypy, et CLAUDE.md prescrit un périmètre différent de la CI. "
    "Valider sur le périmètre de la CI, jamais sur celui de la modification. "
    "Voir la skill omeo-app-dev:omeo-validation."
)


def main():
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    tool_input = payload.get("tool_input") or {}
    path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
    if not path:
        return 0

    normalized = path.replace(os.sep, "/")
    if "/src/apps/" not in normalized and "/tests/" not in normalized:
        return 0

    matched = [rule for rule in RULES if re.search(rule["match"], normalized)]
    if not matched:
        return 0

    lines = ["[omeo-app-dev]", "", PRECONDITIONS, "", "Applicable à ce fichier :", ""]
    seen_files = []
    for rule in matched:
        lines.append(rule["message"])
        lines.append("Procédure complète : skill %s" % rule["skill"])
        for name in rule["files"]:
            if name not in seen_files:
                seen_files.append(name)
        lines.append("")

    if seen_files:
        lines.append("Registre des pièges déjà payés (LIRE avant d'écrire) :")
        for name in seen_files:
            lines.append("  - %s" % registry(name))
        lines.append("")
        source = source_knowledge()
        if source:
            lines.append(
                "Clause d'évolution — si cette tâche fait découvrir un piège non "
                "consigné, l'ÉCRIRE dans le clone git, jamais dans les chemins "
                "ci-dessus : une copie installée est jetée à la mise à jour suivante."
            )
            lines.append("  écrire dans : %s" % source)
            lines.append(
                "  puis commiter et pousser, sinon la trouvaille reste locale et "
                "disparaît."
            )
            lines.append("")

    lines.append(VALIDATION_HINT)
    sys.stdout.write("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
