# omeo-kit

Marketplace Claude Code **mc-groupe-plugins** + plugin **omeo-app-dev** pour le CRM
Django Omeo.app : hooks, skills et registre de pièges pour coder en sécurité et sans
régression, et réduire la dépendance au développeur senior.

## Installation (équipe)

```
/plugin marketplace add https://github.com/devomeo/omeo-kit.git
/plugin install omeo-app-dev@mc-groupe-plugins
```

## Mise à jour

```
claude plugin marketplace update mc-groupe-plugins
claude plugin update omeo-app-dev
```

Redémarrer Claude Code ensuite : le hook chargé en mémoire reste celui de la version
précédente tant que la session n'a pas été relancée.

## Publier une nouvelle version

1. Écrire dans **ce clone git**, jamais dans `~/.claude/plugins/cache/` — chaque version
   s'installe dans un dossier neuf, donc ce qui est écrit dans une copie installée est
   perdu sans avertissement à la mise à jour suivante.
2. Incrémenter la version dans `omeo-app-dev/.claude-plugin/plugin.json` **et** dans
   l'entrée du plugin au sein de `.claude-plugin/marketplace.json` — les deux doivent
   concorder.
3. `claude plugin validate .`
4. Commiter, puis `claude plugin tag` pour poser le tag `omeo-app-dev--v<version>`.
5. Pousser avec `git push --follow-tags`.

Voir `omeo-app-dev/README.md` pour le détail des hooks, skills et du registre.
