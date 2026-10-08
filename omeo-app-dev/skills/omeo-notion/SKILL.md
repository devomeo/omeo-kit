---
name: omeo-notion
description: >
  Accès à l'espace Notion « App Oméo » : documentation détaillée de l'app par module, gestion de
  projet à tenir à jour pour CHAQUE tâche, et Documentation Dev (retours du senior, amélioration
  du plugin). À utiliser au début et à la fin de toute tâche sur le CRM Omeo, quand on demande
  « où on en est » sur une tâche, ou pour comprendre un module de l'app avant de le modifier.
---

# L'espace Notion « App Oméo »

Racine : [App Oméo](https://app.notion.com/p/3ec65dd62c8f8066bb98deb8b1bd274f). Trois parties, de
statut différent :

| Partie | Rôle | Obligation |
|---|---|---|
| Gestion de projet | une fiche par tâche, tenue à jour | **obligatoire, à chaque tâche** |
| Documentation | analyse détaillée de chaque module de l'app | à lire quand le module est touché |
| Documentation Dev | rétrospectives des revues du senior, améliorations du plugin | optionnel |

Ne pas confondre avec le QG Notion MC Groupe (skills `dev-app-qg`, `rituel-qg-groupe`) : pour le
CRM Omeo, c'est cet espace qui fait foi.

## 1. Gestion de projet — obligatoire

Base : [Gestion de projet](https://app.notion.com/p/3f265dd62c8f806db4e3dd195d776c26), source de
données `collection://3f265dd6-2c8f-80df-a287-000b2aa2fd80`.

**Les instructions de remplissage sont sur la page de la base et font foi.** Les lire avant la
première écriture de la session ; ce qui suit ne les remplace pas.

⚠️ Constaté le 2026-10-08 : le connecteur Notion ne renvoie pas ces instructions (le `fetch` de la
base ne rend que le schéma). Si elles restent introuvables, le dire au développeur et lui demander
de les coller, plutôt que de deviner une procédure. En attendant, prendre pour modèle une fiche
récente de la base (par exemple celle du ticket #1485).

**Au début de la tâche**

1. Chercher la fiche existante : par numéro de `Ticket`, sinon par `Nom`. Ne pas créer de doublon.
2. Si elle n'existe pas, la créer avec ses propriétés : `Nom`, `Brief` (une ou deux lignes, le
   détail va dans la page), `Ticket` (numéro seul, ex. `1485`), `Type` (`Bug`, `Évolution`,
   `Nouvelle fonctionnalité`), `Partie de l’app` (nom des apps Django touchées), `Propriétaire`,
   `Statut`.
3. Lire la fiche : brief, décisions déjà prises, points ouverts, retours de revue. Une décision
   consignée là ne se rediscute pas sans raison nouvelle.

**Pendant et à la fin**

- Tenir le `Statut` à jour : `Pas commencé`, `En cours`, `Attente de validation`, `Bloqué`,
  `Terminé` (avec `Terminé le`).
- Consigner dans la page ce qu'un développeur qui reprend la tâche doit savoir : ce qui a été
  livré, les décisions et leur raison, les retours du senior et leur traitement, les découvertes,
  les points ouverts, la validation effectuée — et ce qui n'a **pas** pu être vérifié.
- Mettre la fiche à jour **avant** de déclarer la tâche terminée, pas dans une session ultérieure.

## 2. Documentation — comprendre un module

[Documentation](https://app.notion.com/p/3eb65dd62c8f80d2b1d5ef101129d0e2) : une analyse par
module, souvent découpée en sous-pages (écrans et routes, règles métier, données, points de
vigilance).

| Module | Page |
|---|---|
| prospect (Prospecto) | [Prospecto Analyse](https://app.notion.com/p/3e565dd62c8f8028b158f65cdef024ce) |
| case | [Case Analyse](https://app.notion.com/p/3eb65dd62c8f81b6a09df8ec7e91db3f) |
| project | [Project Analyse](https://app.notion.com/p/3eb65dd62c8f819d80fff29055215c27) |
| crm (contacts) | [CRM Analyse](https://app.notion.com/p/3eb65dd62c8f815f8269d557c8ad9198) |
| product | [Product Analyse](https://app.notion.com/p/3eb65dd62c8f810882b4d819c6c81c8a) |
| contract | [Contract Analyse](https://app.notion.com/p/3eb65dd62c8f817e8fc0d56f11de994e) |
| sign | [Sign Analyse](https://app.notion.com/p/3eb65dd62c8f81e39907fe1555418ac9) |
| account | [Account Analyse](https://app.notion.com/p/3eb65dd62c8f81cd80f6e8bf62c1de31) |
| commission | [Commission Analyse](https://app.notion.com/p/3eb65dd62c8f818393c1ee27094dcebd) |
| dashboard | [Dashboard Analyse](https://app.notion.com/p/3eb65dd62c8f81bf88bff5fdcba4660a) |
| note | [Note Analyse](https://app.notion.com/p/3eb65dd62c8f812daa2cfe80bb74d570) |
| notification | [Notification Analyse](https://app.notion.com/p/3eb65dd62c8f81dd9a3ae175c144cc6d) |
| bilan | [Bilan Analyse](https://app.notion.com/p/3eb65dd62c8f81ee9f21dcfd83bc1bc1) |
| core | [Core Analyse](https://app.notion.com/p/3eb65dd62c8f81f4a3f3eff93163ef4d) |
| repair (dépannages) | [Repair Analyse](https://app.notion.com/p/3ec65dd62c8f819a8f62e2ffb903aa13) |
| schedule (rendez-vous) | [Schedule Analyse](https://app.notion.com/p/3ec65dd62c8f81dc89f8cb0b88df3521) |
| mcp (assistants IA) | [MCP Analyse](https://app.notion.com/p/3ec65dd62c8f810c9f64cc2f563b6358) |
| theme (styles) | [Theme Analyse](https://app.notion.com/p/3ec65dd62c8f81829761dde04437e858) |

Une analyse est une **photo datée** du code. En cas d'écart avec le code, **le code fait foi** :
le signaler au développeur, et ne pas corriger la page sans qu'il le demande.

## 3. Documentation Dev — optionnel

[Documentation Dev](https://app.notion.com/p/3f365dd62c8f804f9f69c240617844b3) : un rapport par
revue de MR, qui explique les retours du senior et pourquoi Claude ne les avait pas anticipés. La
page porte le prompt à utiliser pour en produire un nouveau. Ce qui est retenu pour le plugin va
dans [Améliorations plugin](https://app.notion.com/p/3f365dd62c8f8034ab29c53eb4e0829a).

Le remplir est **optionnel**. À ne pas confondre avec la **clause d'évolution** du registre
(`../../knowledge/README.md`), qui, elle, est obligatoire : un commentaire du senior qui révèle
une attente non écrite va dans `knowledge/senior-expectations.md`, rapport Notion ou pas.
