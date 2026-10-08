# omeo-app-dev

Garde-fous, préconditions et registre de pièges pour développer sur le CRM Omeo.app.

Autonome : ne dépend d'aucun autre plugin.

## Le parti pris

**Empêcher pendant l'écriture plutôt que relire après.**

Sur un échantillon réel de six reprises demandées en revue, **une seule** relevait d'un problème
qu'une relecture attrape (un couplage mal choisi). Les cinq autres étaient des préalables non
tenus : ne pas avoir lu la version précédente, avoir inventé un identifiant, avoir omis un
argument en recopiant une fonction, avoir validé sur un périmètre plus étroit que la CI, avoir
tranché seul un conflit entre deux consignes.

Le poids du plugin est donc mis sur les préconditions et le savoir accumulé, pas sur des agents
relecteurs.

## Ce que ce plugin ne contient pas

Il ne redit ni `CLAUDE.md`, ni `docs/` (1802 lignes, dont `ai-agents.md`, `architecture.md`,
`domain.md`, `python-styleguide.md`). Ces documents sont la source de vérité et sont déjà lus.

**Toute ligne de ce plugin doit être quelque chose qui n'est ni dans `CLAUDE.md`, ni dans `docs/`,
ni lisible en ouvrant le fichier concerné.** Une skill redondante coûte de l'attention sans
apporter d'information — c'est ce qui rendait le plugin précédent contre-productif quand on
l'imposait en début de session.

Seule exception assumée : `knowledge/senior-expectations.md`, qui documente les points où la
pratique du senior **contredit** la doc écrite. Ce n'est pas de la redite, c'est un arbitrage.

## Contenu

### Hooks — `hooks/guards.py`

En `PreToolUse` sur `Edit`/`Write`/`MultiEdit` : le contenu utile est injecté **avant**
l'écriture, pas après. C'est la différence décisive avec le plugin précédent, dont le hook
`PostToolUse` se contentait de **nommer** une skill — nommée trois fois, jamais ouverte.

Quinze règles. Déclenchées sur le chemin du fichier : route API, étape versionnée, gabarit
d'étape versionné, signal, calcul métier, grille tarifaire de catalogue, modèle, admin, migration,
test, JS statique. Déclenchées sur le contenu écrit : appel d'API externe, bloc `<script>` long
dans un gabarit, défilement ou swipe écrit en JS, classes Tailwind. Chaque message porte le piège
concret, pas un renvoi. Le hook fournit aussi le **chemin absolu** des fichiers du registre à lire.

Le message passe par `hookSpecificOutput.additionalContext` : en `PreToolUse`, un texte brut sur
stdout n'est montré qu'à l'utilisateur, jamais au modèle (c'était le cas jusqu'à la 0.5.0).

Également déclenché sur `Bash`, pour la seule commande `makemigrations` : les migrations sont
générées en ligne de commande, jamais écrites à la main.

Silencieux quand aucune règle ne correspond, et ne bloque jamais. Robuste à une entrée vide ou
invalide.

### Hook de début de session — `hooks/session_start.py`

En `SessionStart`, et seulement dans le dépôt du CRM (présence de `src/manage.py` et
`src/apps/case/`) : trois lignes qui rappellent que la fiche de la tâche dans la gestion de projet
Notion se lit au début et se met à jour avant de déclarer terminé. C'est la seule chose injectée
en début de session : une obligation de suivi, pas une procédure — les procédures restent dans les
skills, chargées quand elles servent.

### Skills

| Skill | Quand |
|---|---|
| `omeo-notion` | début et fin de chaque tâche — gestion de projet, documentation de l'app, Documentation Dev |
| `omeo-brief` | à la réception d'un brief, avant toute lecture de code approfondie |
| `omeo-preconditions` | avant d'écrire du code, quelle que soit la tâche |
| `omeo-validation` | avant de déclarer terminé, ou face à un échec local suspect |
| `omeo-endpoint` | création ou modification d'une route dans un `api.py` |
| `omeo-business-calc` | `product/`, `case/cart/`, `case/prime/`, `case/loan/` — dont `product/catalogs/` |
| `omeo-signal` | tout `signals.py`, `core/metrics.py`, `apps.py::ready()` |
| `omeo-step-version` | `case/steps/` — formulaires, managers, gabarits, `structures.py` |
| `omeo-front` | gabarits HTML, `src/static/js/`, classes Tailwind — Alpine, CSS compilé, vérification à l'écran |

### Registre — `knowledge/`

Ce que le code ne dit pas : comportements contre-intuitifs, dépendances invisibles, hypothèses
fausses déjà payées. Un fichier par domaine, **le vide est un état valide**.

Deux clauses gouvernent ce dossier, détaillées dans `knowledge/README.md` : la **clause
d'évolution** (une case vide qu'une situation permet de remplir doit l'être avant de clore la
tâche) et la **clause de preuve** (aucune entrée sans observation vérifiée). Elles se tiennent
en tension : sans la seconde, la première produit du remplissage spéculatif.

État actuel : `case-cart`, `case-steps`, `product-catalogs` et `senior-expectations` sont nourris.
Les autres domaines restent à ouvrir au fil des rencontres.

## Reste à faire
- Registres des autres apps, par ordre de rayon d'impact (`commission`, `sign`, `prime`,
  `contract`, `integration` d'abord).
- Deux ou trois agents à déclencheur, sur les seules questions falsifiables.
