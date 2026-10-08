#!/usr/bin/env python3
"""Garde-fous omeo-app-dev.

Déclenché en PreToolUse sur Edit/Write/MultiEdit : injecte le contenu utile AVANT
l'écriture, plutôt que de nommer une skill après coup. Les règles portent sur le
chemin du fichier et, pour certaines, sur le contenu écrit. Aussi déclenché sur
Bash, pour la seule commande makemigrations.

Le message passe par hookSpecificOutput.additionalContext : en PreToolUse, un texte
brut sur stdout n'est montré qu'à l'utilisateur, jamais au modèle.

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


MIGRATION_MESSAGE = (
    "Migration. Une seule par app pour la fonctionnalité. Si l'app a déjà une migration propre "
    "à la branche (git diff --name-only origin/develop... -- src/apps/<app>/migrations/), la "
    "RÉGÉNÉRER au lieu d'en empiler une autre : supprimer le fichier, makemigrations <app> "
    "--name <suffixe>, black, puis makemigrations --check. Une migration de branche devenue "
    "sans objet se supprime. Ne jamais modifier une migration présente sur develop. Demander "
    "avant d'aligner la base locale : ses données de test peuvent être perdues."
)


SCRIPT_LINES_THRESHOLD = 30
SCRIPT_BLOCK = re.compile(r"<script\b[^>]*>(.*?)(?:</script>|$)", re.S | re.I)
EXTERNAL_HTTP = re.compile(r"\b(requests|httpx)\.")


def long_script(path, written, existing):
    return any(
        block.count("\n") > SCRIPT_LINES_THRESHOLD
        for block in SCRIPT_BLOCK.findall(written)
    )


def calls_external_api(path, written, existing):
    return bool(EXTERNAL_HTTP.search(written) or EXTERNAL_HTTP.search(existing))


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
            "précisément le voisinage de case/*.\n"
            "Avant une nouvelle route : chercher celle qui sert déjà la même ressource. Si "
            "elle existe, la faire évoluer et grepper son url_name dans tout src/, gabarits des "
            "AUTRES versions de déballe compris. Charger des éléments par identifiants est une "
            "route « detail » distincte, non paginée.\n"
            "@paginate change la réponse en {items, count} — tous les appelants sont à adapter. "
            "Un ?page_size= demandé par le client est ramené SILENCIEUSEMENT à 100 "
            "(NINJA_MAX_PER_PAGE_SIZE) : relever max_page_size sur la seule route concernée."
        ),
        "files": ["case-cart.md", "senior-expectations.md"],
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
        "match": r"/templates/case_steps/version_\d+/.+\.html$",
        "skill": "omeo-app-dev:omeo-step-version",
        "message": (
            "Gabarit d'étape versionné. S'il s'agit d'une création, le comparer d'abord à son "
            "équivalent dans case_steps/common/ : un gabarit versionné identique au partagé "
            "n'apporte rien et a déjà été supprimé en revue.\n"
            "Rappel de rendu : {{ field.value|default:\"\" }} applique le filtre Django à toute "
            "valeur falsy, donc initial=0 arrive dans Alpine comme une chaîne vide.\n"
            "Code copié d'une autre version : vérifier chaque paramètre, clé de contexte, "
            "méthode Alpine et bloc conditionnel hérité contre le StepsSchema de la version et "
            "par grep de ses usages. Ce qui n'y sert plus part, même si on ne l'a pas écrit."
        ),
        "files": ["case-steps.md", "senior-expectations.md"],
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
    {
        "match": r"/product/catalogs/.*\.py$",
        "skill": "omeo-app-dev:omeo-business-calc",
        "message": (
            "Grille tarifaire menuiserie. Les axes NE SONT PAS écrits : fetch_pricing indexe la "
            "matrice par position, et les bornes h_min/w_min déclarées au-dessus ne les "
            "décrivent pas. Le Fixe déclare h_min=800 pour une matrice qui commence à 400 — un "
            "fixe est facturé au prix d'un modèle 400 mm plus bas. Se fier à la matrice, jamais "
            "aux bornes.\n"
            "Après tout collage depuis Excel, recalculer colonne par colonne l'écart au prix "
            "d'achat : une colonne saine donne une constante, une colonne qui dérive est un "
            "collage raté. Deux colonnes sont restées à l'ancien tarif pendant huit mois sans "
            "qu'aucune pipeline ne bronche — AUCUN test ne vérifie une valeur de prix.\n"
            "40 des 84 matrices sont inatteignables (price_type != DEFAULT) : vérifier le "
            "price_type avant de s'alarmer d'une anomalie.\n"
            "Un changement ici est rétroactif sur tous les dossiers non validés, sans date "
            "d'effet."
        ),
        "files": ["product-catalogs.md"],
    },
    {
        "match": r"/models\.py$",
        "skill": None,
        "message": (
            "Modèle. (1) Hériter d'AbstractModel seulement si le code lit réellement son status "
            "(archivage, soft-delete) — sinon models.Model avec les seuls champs utiles ; un "
            "logement archivé restait affiché sur la carte Radar faute de filtre sur status. "
            "(2) Chaque champ ajouté doit avoir un lecteur qu'on sait citer, sinon ne pas "
            "l'ajouter. (3) Une valeur qui se déduit des autres champs est une @property ; un "
            "champ ne se justifie que pour filtrer/trier en base, figer une photo, ou un calcul "
            "coûteux. (4) Permissions : add_/change_/delete_/view_<modèle> de Django d'abord ; "
            "Meta.permissions seulement si aucune ne convient, et le justifier. (5) Index : "
            "seulement pour une requête qui existe dans le code, à citer. (6) __str__ lisible "
            "par un administrateur métier (une adresse, un nom), jamais une clé technique."
        ),
        "files": ["senior-expectations.md"],
    },
    {
        "match": r"/admin\.py$",
        "skill": None,
        "message": (
            "Admin. Ne pas ajouter de has_add_permission / has_change_permission / "
            "has_delete_permission qui renvoient False : les permissions Django standard "
            "décident déjà de l'accès. Retiré en revue (« à retirer, pas utile »)."
        ),
        "files": [],
    },
    {
        "match": r"/migrations/\d{4}_\w*\.py$",
        "skill": None,
        "message": MIGRATION_MESSAGE,
        "files": ["senior-expectations.md"],
    },
    {
        "match": r"/src/apps/.+\.py$",
        "when": calls_external_api,
        "skill": None,
        "message": (
            "Appel d'API externe. (1) Délai, erreur HTTP ou JSON illisible deviennent une "
            "exception métier dédiée (ex. AdemeAPIError), que la route transforme en 502, "
            "jamais en 500. (2) Si le code continue avec une valeur de repli, signaler la panne "
            "par sentry_sdk.capture_exception(exc) : jamais de panne avalée en silence. "
            "(3) Paramètres de requête échappés, jamais concaténés bruts dans une requête "
            "texte. (4) Réponse mal formée (champ manquant, type inattendu) → exception métier, "
            "pas KeyError. (5) Isoler l'appel HTTP dans une méthode dédiée du service : c'est "
            "le point qu'un test remplace pour faire tourner le vrai code, erreurs comprises."
        ),
        "files": [],
    },
    {
        "match": r"/tests/.+\.py$",
        "skill": None,
        "message": (
            "Test. (1) Pas de fonction locale qui fait Model.objects.create(...) : passer par "
            "les factories, en général tests/<app>/<app>_factories.py (et non factories.py "
            "comme l'écrit CLAUDE.md — quelques apps ont les deux, vérifier avec ls). Si la "
            "factory manque, l'y ajouter. (2) Aucun compteur ni état au niveau du module : un "
            "test donne le même résultat seul, en premier, en dernier ou en parallèle. (3) Une "
            "fixture qui modifie un état partagé (cache, réglage global) le remet en état avec "
            "yield. (4) Mocker la frontière externe — pour une API, une sous-classe du service "
            "qui redéfinit la méthode d'appel HTTP — jamais les fonctions internes du code "
            "testé, et ne jamais asserter la valeur que son propre mock renvoie. (5) Préférer un "
            "test de comportement (rendu, réponse d'API) à un test qui cherche une ligne dans "
            "le code source."
        ),
        "files": [],
    },
    {
        "match": r"/templates/.+\.html$",
        "when": long_script,
        "skill": "omeo-app-dev:omeo-front",
        "message": (
            "Bloc <script> de plus de %d lignes dans un gabarit. Un composant JS de cette taille "
            "va dans src/static/js/<app>/<nom>.js, sur le modèle de src/static/js/case_builder/. "
            "Les valeurs que seul Django connaît ({%% url %%}, {%% if perms %%}, csrf_token) "
            "passent par {{ config|json_script:\"<id>\" }} depuis la vue, puis "
            "JSON.parse(document.getElementById('<id>').textContent) dans le JS."
            % SCRIPT_LINES_THRESHOLD
        ),
        "files": [],
    },
    {
        "match": r"/templates/.+\.html$|/src/static/js/.+\.js$",
        "content": r"\b(touchstart|touchmove|touchend|wheel)\b|onTouch|translateX|@scroll|x-on:scroll",
        "skill": "omeo-app-dev:omeo-front",
        "message": (
            "Défilement, swipe ou glisser écrits en JS. Le défilement natif (overflow-x-auto "
            "avec scroll-snap) gère déjà molette, trackpad, clavier et tactile, et x-intersect "
            "(déjà utilisé pour les contrats et les prospects) couvre le chargement à "
            "l'affichage. Un swipe onTouchStart/onTouchEnd sur un conteneur déjà scrollable a "
            "été refusé en revue. Ne garder le JS que si le natif ne couvre pas le besoin, et "
            "le dire."
        ),
        "files": ["senior-expectations.md"],
    },
    {
        "match": r"/templates/.+\.html$|/src/static/js/.+\.js$|/src/apps/.+\.py$",
        "content": r"class=|classList|className|[\"']class[\"']\s*:",
        "skill": "omeo-app-dev:omeo-front",
        "message": (
            "Classes Tailwind. Une classe jamais utilisée jusqu'ici n'existe dans "
            "src/static/css/styles.css (compilé et versionné) qu'après régénération : npm run "
            "build:tailwind dans src/apps/theme/static_src/. snap-* et disabled:opacity-30 "
            "manquaient ainsi au CSS compilé. Tailwind lit les gabarits et src/static/**/*.js, "
            "PAS les .py : une classe écrite seulement dans du Python n'est jamais générée."
        ),
        "files": [],
    },
    {
        "match": r"/src/static/js/(?!leaflet/)[^/]+/.+\.js$",
        "skill": "omeo-app-dev:omeo-front",
        "message": (
            "JS statique. (1) Tout ce qui déclenche un chargement serveur (déplacement de carte, "
            "filtres…) passe par UN délai commun et annule la requête précédente "
            "(AbortController) : sinon une réponse lente écrase une plus récente. (2) Aucune "
            "valeur venue de l'extérieur (API, base) insérée dans innerHTML sans être validée "
            "côté serveur (ex. classe énergétique limitée à A-G), avec un test qui le prouve."
        ),
        "files": [],
    },
]

MIGRATION_COMMAND = re.compile(r"\bmakemigrations\b(?!.*--(check|dry-run))")

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


CONTEXT_LIMIT = 9500
WATCHED = ("/src/apps/", "/tests/", "/src/static/js/")


def written_content(tool_input):
    parts = [tool_input.get("content") or "", tool_input.get("new_string") or ""]
    for edit in tool_input.get("edits") or []:
        parts.append(edit.get("new_string") or "")
    return "\n".join(parts)


def existing_content(path):
    try:
        with open(path, encoding="utf-8") as handle:
            return handle.read()
    except (OSError, UnicodeDecodeError):
        return ""


def applies(rule, path, written, existing):
    if not re.search(rule["match"], path):
        return False
    if "content" in rule and not re.search(rule["content"], written):
        return False
    if "when" in rule and not rule["when"](path, written, existing):
        return False
    return True


def emit(text):
    if len(text) > CONTEXT_LIMIT:
        text = text[:CONTEXT_LIMIT] + "\n[…] message tronqué"
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "additionalContext": text,
            }
        },
        sys.stdout,
        ensure_ascii=False,
    )


def bash_guard(tool_input):
    command = tool_input.get("command") or ""
    if MIGRATION_COMMAND.search(command):
        emit("[omeo-app-dev]\n\n" + MIGRATION_MESSAGE)
    return 0


def main():
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    if not isinstance(payload, dict):
        return 0

    tool_input = payload.get("tool_input") or {}
    if payload.get("tool_name") == "Bash":
        return bash_guard(tool_input)

    path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
    if not path:
        return 0

    normalized = path.replace(os.sep, "/")
    if not any(part in normalized for part in WATCHED):
        return 0

    written = written_content(tool_input)
    existing = existing_content(path)
    matched = [rule for rule in RULES if applies(rule, normalized, written, existing)]
    if not matched:
        return 0

    lines = ["[omeo-app-dev]", "", PRECONDITIONS, "", "Applicable à ce fichier :", ""]
    seen_files = []
    seen_skills = []
    for rule in matched:
        lines.append(rule["message"])
        if rule["skill"] and rule["skill"] not in seen_skills:
            seen_skills.append(rule["skill"])
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
    emit("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
