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

### Skills

| Skill | Quand |
|---|---|
| `omeo-preconditions` | avant d'écrire du code, quelle que soit la tâche |
| `omeo-validation` | avant de déclarer terminé, ou face à un échec local suspect |
| `omeo-endpoint` | création ou modification d'une route dans un `api.py` |
| `omeo-business-calc` | `product/`, `case/cart/`, `case/prime/`, `case/loan/` |
| `omeo-signal` | tout `signals.py`, `core/metrics.py`, `apps.py::ready()` |
| `omeo-step-version` | `case/steps/` — formulaires, managers, gabarits, `structures.py` |

### Registre — `knowledge/`

Ce que le code ne dit pas : comportements contre-intuitifs, dépendances invisibles, hypothèses
fausses déjà payées. Un fichier par domaine, **le vide est un état valide**.

Deux clauses gouvernent ce dossier, détaillées dans `knowledge/README.md` : la **clause
d'évolution** (une case vide qu'une situation permet de remplir doit l'être avant de clore la
tâche) et la **clause de preuve** (aucune entrée sans observation vérifiée). Elles se tiennent
en tension : sans la seconde, la première produit du remplissage spéculatif.

État actuel : `case-cart`, `case-steps` et `senior-expectations` sont nourris. Les autres domaines
restent à ouvrir au fil des rencontres.

## Reste à faire

- Hooks `PreToolUse` pour rendre les préconditions incontournables plutôt que consultables.
- Analyse de brief : séparer ce qui est décidable depuis le code de ce qui exige un arbitrage humain.
- Registres des autres apps, par ordre de rayon d'impact (`commission`, `sign`, `prime`,
  `contract`, `integration` d'abord).
- Deux ou trois agents à déclencheur, sur les seules questions falsifiables.
