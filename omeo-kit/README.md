# omeo-kit

Plugin Claude Code pour le CRM **Omeo.app**. Il empaquète une équipe d'agents
spécialisés, des skills (procédures réutilisables) et des garde-fous automatiques
(hooks) dont le but unique est de **réduire la dépendance au développeur senior** :
permettre à n'importe quel développeur d'intervenir proprement, en sécurité et sans
régression.

## Philosophie

1. **Les agents amplifient des garde-fous explicites** — ils ne remplacent pas le
   jugement humain. Chaque agent s'appuie sur une règle écrite et un test vérifiable.
2. **Défense en profondeur** — une modification traverse plusieurs filtres : skill
   guidée → agents spécialisés → reviewer → hooks de validation → humain.
3. **L'humain merge, toujours** — les agents proposent, annotent, bloquent. Seul un
   humain valide et fusionne.

## Contenu

```
omeo-kit/
├── agents/        7 spécialistes (sécurité, métier, archi, front, QA, doc, reviewer)
├── skills/        7 procédures pas-à-pas (le "comment faire")
├── commands/      3 commandes d'orchestration (/omeo-review, /omeo-new-endpoint, /omeo-onboard)
└── hooks/         garde-fous automatiques (rappels sécurité, validation pré-merge)
```

## Commandes principales

| Commande | Rôle |
|----------|------|
| `/omeo-review` | Lance la revue multi-agents sur le diff courant et produit un verdict priorisé |
| `/omeo-new-endpoint` | Guide la création d'un endpoint API isolé et testé |
| `/omeo-onboard` | Parcours d'onboarding d'un nouveau développeur |

## Installation (local)

Référencer le dossier `omeo-kit/` comme plugin dans la configuration Claude Code de
l'équipe (marketplace locale ou chemin de plugin). Aucune action destructive : tous
les agents sont en lecture seule et proposent des changements, ils n'écrivent jamais
directement dans le dépôt.

## Déploiement progressif recommandé

1. **Socle** : écrire les tests d'isolation P0 + corriger la fuite PostHog avant tout.
2. **MVP** : `security-permissions` + `reviewer-final` + `/omeo-review` + hooks de validation.
3. **Métier** : `backend-metier`, `qa-tests`, skills prix/primes/migration.
4. **Complet** : `architecte-django`, `frontend-alpine`, `conventions-doc`, onboarding.
5. **Mesure** : suivre la part de PR validées sans intervention du senior.

## Référence

Ce plugin s'appuie sur la documentation existante du dépôt :
`docs/architecture.md`, `docs/domain.md`, `docs/ai-agents.md`, `CLAUDE.md`.
