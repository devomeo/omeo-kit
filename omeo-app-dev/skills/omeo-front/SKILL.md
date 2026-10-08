---
name: omeo-front
description: >
  Pièges front (Alpine 3.10.5, Tailwind compilé, JS statique) du CRM Omeo, et ce qui compte comme
  une vérification front. À utiliser dès qu'on écrit dans un gabarit HTML, un fichier de
  src/static/js/, ou qu'on ajoute des classes Tailwind.
---

# Écrire du front sans le refaire en revue

Quatre des erreurs du ticket #1485 (« Step Solutions V9 ») étaient côté front. Aucune n'était
visible dans les tests ; toutes l'étaient à l'écran.

## Avant d'écrire

1. **Chercher le natif d'abord** : défilement `overflow-x-auto` avec `scroll-snap`,
   `loading="lazy"`, `x-intersect` (plugin chargé dans `core/templates/core/js_dependencies.html`,
   déjà utilisé par les listes de contrats, d'affaires et de prospects), `details` / `summary`. Le
   natif apporte molette, trackpad, clavier et tactile sans code. L'attente du senior et sa preuve :
   `../../knowledge/senior-expectations.md`, entrée « Le natif du navigateur avant le JS ».
2. **Chercher un motif Alpine déjà présent** dans le projet avant d'en écrire un : `grep` du
   comportement voulu (`x-intersect`, `x-teleport`, `@click.outside`…) dans `src/apps/**/templates/`.
3. **Un composant de plus de quelques dizaines de lignes va dans un fichier statique**
   `src/static/js/<app>/<nom>.js`, sur le modèle de `src/static/js/case_builder/`. Les valeurs que
   seul Django connaît (`{% url %}`, `{% if perms %}`, `csrf_token`) passent par
   `{{ config|json_script:"<id>" }}`, lues avec `JSON.parse(document.getElementById('<id>').textContent)`.

## Pièges Alpine 3.10.5

- **`x-show` charge quand même ce qu'il cache** : une image dans un bloc `x-show` est téléchargée
  au rendu de la page. Pour différer le chargement, utiliser `<template x-if>`. **Mais** un
  `@click.outside` placé dans ce bloc reçoit le clic qui vient de l'ouvrir et le referme aussitôt :
  mettre `.stop` sur le déclencheur. Les deux vont ensemble.
- **Overlay `fixed` sous un parent `transform`** : il ne couvre plus l'écran. Le téléporter avec
  `<template x-teleport="body">`.
- **`$refs` dans `init()`** : ⚠️ non vérifié dans le dépôt, signalé par le ticket #1485. Une
  référence placée dans un `x-if` ou un `x-for` n'existe pas avant leur rendu. Ne pas s'y fier dans
  `init()` ; passer par `$nextTick` ou par l'événement qui suit le rendu.

Preuves, chemins et vérifications des deux premiers : `../../knowledge/case-steps.md`, entrées
« Un `@click.outside` dans un bloc `x-if`… » et « Un `fixed inset-0` placé sous un parent
`transform`… ». Les lire plutôt que les redécouvrir.

## CSS : Tailwind est compilé et versionné

`src/static/css/styles.css` est un fichier **compilé et commité**. Une classe Tailwind jamais
utilisée jusqu'ici n'y existe pas tant qu'il n'a pas été régénéré — elle est silencieusement sans
effet. Cas réel : `snap-*` et `disabled:opacity-30` absentes du CSS compilé.

- **Régénérer** : `npm run build:tailwind` dans `src/apps/theme/static_src/`, puis commiter
  `styles.css`. Le fichier doit finir par un retour à la ligne, sinon le hook pre-commit
  `end-of-file-fixer` le modifie et le commit échoue.
- **Ce que Tailwind lit** (rubrique `content` de `src/apps/theme/static_src/tailwind.config.js`) :
  tous les `templates/**/*.html` et `src/static/**/*.js`. **Pas les `.py`** (ligne commentée) :
  une classe écrite seulement dans du Python — `attrs={"class": …}` d'un widget, HTML construit
  côté serveur — n'est jamais générée. La reprendre dans un gabarit, ou en parler avant d'élargir
  la configuration.
- **Conflit de rebase sur `styles.css`** : ne pas choisir un côté. Prendre l'un ou l'autre, puis
  régénérer : le fichier n'est qu'une sortie.

## JS statique

- Tout ce qui déclenche un chargement serveur (déplacement de carte, filtres…) passe par **un
  seul** délai commun et **annule la requête précédente** (`AbortController`) : sinon une réponse
  lente écrase une réponse plus récente. Le test de `res.ok` et le debounce simple sont dans
  `docs/javascript-styleguide.md`.
- Aucune valeur venue de l'extérieur (API, base) dans `innerHTML` sans validation côté serveur
  (par exemple une classe énergétique limitée à A-G), avec un test qui le prouve.

## Vérification

Un comportement front n'est **vérifié** que dans le navigateur, **onglet au premier plan** : dans
un onglet en arrière-plan, les animations, `x-intersect` et les événements de défilement sont
suspendus, et un test peut passer à tort. Si la vérification n'a pas été faite ainsi, le dire
explicitement dans le compte rendu — un test de gabarit qui cherche une ligne n'en tient pas lieu
(voir la skill **omeo-validation**).
