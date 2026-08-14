# Registre des pièges — mode d'emploi

Ce dossier contient ce que **le code ne dit pas** : les comportements contre-intuitifs, les
dépendances invisibles et les hypothèses fausses qui ont déjà coûté du temps ou produit un bug.

Un fichier par domaine. Il est normal que certains soient vides.

## Ce qui n'a rien à faire ici

- Ce qui est déjà dans `CLAUDE.md` (ordre des couches, conventions de nommage, commandes).
- Ce qui se lit directement dans le code en ouvrant le fichier.
- Une intention, une préférence de style, une idée de refactoring.

Si une entrée est déductible d'une lecture normale du code, elle n'apporte rien et elle dilue
le reste. Le registre ne vaut que par sa densité.

## Clause d'évolution — obligatoire

**Le vide est un état valide, pas un état final.**

Dès qu'une situation rencontrée en cours de travail permet de remplir une case vide, elle
**doit** être remplie dans la foulée, avant de clore la tâche. Ne pas attendre une session
dédiée : le savoir se perd entre deux sessions.

Déclencheurs qui obligent à écrire une entrée :

- un bug reproduit dont la cause n'était pas lisible dans le code ;
- une hypothèse de départ contredite par les faits ;
- un commentaire du développeur senior qui révèle une attente non écrite ;
- un chiffre mesuré sur les données réelles qui change une décision ;
- une piste envisagée puis écartée pour une raison structurelle — l'écarter une fois suffit,
  la prochaine session ne doit pas refaire l'enquête.

## Où écrire — la partie qui décide si ça sert à quelque chose

Le plugin existe en deux exemplaires sur une machine :

```
~/.claude/plugins/marketplaces/<marketplace>/<plugin>/     ← clone git : LA SOURCE
~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/  ← copie installée : JETABLE
```

**Écrire toujours dans le clone git.** Chaque version s'installe dans un dossier neuf : ce qui
est écrit dans une copie installée est perdu à la mise à jour suivante, sans erreur ni
avertissement. Le chemin que le hook affiche sert à **lire** ; il rappelle lui-même où écrire.

Une entrée n'est acquise pour l'équipe qu'une fois **commitée et poussée**. Tant qu'elle reste
dans le clone local, elle ne vaut que pour une machine.

Séquence, à faire dans la foulée de la tâche :

1. écrire l'entrée dans `<clone git>/knowledge/<domaine>.md` ;
2. commiter et pousser ;
3. incrémenter la version dans `.claude-plugin/plugin.json` **et** dans l'entrée du plugin
   au sein de `marketplace.json` si l'ajout est significatif — les deux doivent concorder,
   `claude plugin validate` le vérifie.

Ne jamais laisser de modification non commitée dans le clone : c'est un dépôt git, et une mise
à jour de la marketplace peut échouer dessus.

## Clause de preuve — tout aussi obligatoire

**Mieux vaut du vide que du faux.** Une entrée n'est admise que si elle repose sur une
observation vérifiée, jamais sur une lecture rapide ou une déduction plausible.

Preuve recevable :

- un test qui échoue puis passe ;
- une erreur reproduite avec son message et sa ligne ;
- une mesure sur les données (`src/data.json`, la base) avec la commande utilisée ;
- une citation explicite du senior ;
- un `file:line` que l'on a réellement ouvert.

Preuve non recevable : « il semble que », « probablement », un raisonnement par analogie avec
un autre module, un comportement supposé d'une bibliothèque.

Dans le doute, écrire l'entrée en la marquant `⚠️ non vérifié` avec ce qui reste à confirmer.
Une incertitude déclarée est utile ; une certitude fabriquée fait perdre plus de temps que
le silence.

## Format d'une entrée

Voir `_template.md`. Chaque entrée porte :

- **Le piège** en une phrase, à l'indicatif, orientée conséquence.
- **Où** : `fichier:ligne`.
- **Preuve** : comment on le sait.
- **À faire** : la conduite à tenir.

## Maintenance

Une entrée dont le code a changé doit être corrigée ou supprimée, pas laissée en l'état.
Un registre qui ment est pire qu'un registre vide — c'est la seule règle qui prime sur
la clause d'évolution.
