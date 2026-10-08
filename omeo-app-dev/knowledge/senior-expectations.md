# Attentes du développeur senior — y compris là où elles contredisent la doc

> Statut : partiel
> Dernière mise à jour : 2026-10-08

Lire `README.md` avant d'ajouter une entrée : clause d'évolution et clause de preuve.

Ce fichier consigne ce que le senior applique en revue et qui **n'est écrit nulle part**, ou qui
**contredit** `CLAUDE.md` ou `docs/`. En cas de conflit, c'est ce fichier qui l'emporte — mais
toute entrée doit citer sa preuve.

---

## Aucun commentaire dans le code — contredit `docs/code-review.md`

**Preuve** : consigne explicite et répétée — « Même à l'avenir, je veux que tu arrêtes de mettre
des commentaires ». Elle couvre aussi toute référence à un numéro de MR dans le code.

**Ce que dit la doc** : `docs/code-review.md` demande « Add comments for complex logic ».

**À faire** : ne pas ajouter de commentaire. Si une ligne a besoin d'être expliquée, c'est la
ligne qu'il faut changer. Le signal en revue est direct : un « c'est quoi ? » sur un identifiant
ou une ligne signifie que le code n'est pas lisible, pas qu'il manque un commentaire.

---

## Pas de nouvelle abstraction dans une MR feature

**Preuve** : consigne du senior après revue — reproduire le motif en place, **même dupliqué** ; la
déduplication fait l'objet d'une MR dédiée.

**À faire** : ne pas introduire de helper, de flag ou de couche partagée « tant qu'on y est ». Un
helper privé de module est acceptable s'il imite un motif déjà présent dans le même fichier
(`case/cart/services.py` en contient plusieurs : `_normalize_amount`, `_collect_cart_products`).

**Frontière de la règle — important** : elle interdit d'introduire une abstraction nouvelle
**par-dessus du code existant**. Elle n'autorise pas à laisser **deux méthodes identiques qu'on
vient d'écrire soi-même** dans la même MR.

**Preuve de la frontière** : sur une autre MR du même projet (Bilan V4), le senior a demandé de
factoriser deux managers dont les `save` et `next_step_url` étaient strictement identiques et
tous deux introduits par la MR. Les deux consignes ne se contredisent pas — l'une porte sur
l'existant qu'on ne touche pas, l'autre sur ce qu'on ajoute.

En cas de doute sur le côté de la frontière où l'on se trouve : le signaler plutôt que trancher.

**Ce qui n'est pas une abstraction** : une route dédiée à un usage distinct. La règle avait été
opposée à la création d'une route « detail » à côté d'une liste paginée ; le senior l'a demandée
(voir l'entrée « Une route par usage »).

---

## Pas de vocabulaire inventé

**Preuve** : `usesParentConsumption`, introduit pour exprimer une distinction absente du reste du
code. Commentaire du senior : « c'est quoi ». Supprimé.

**À faire** : `grep` tout identifiant nouveau avant de l'écrire. S'il n'a aucun précédent, soit le
concept existe sous un autre nom, soit on introduit un concept nouveau — et cela se signale.

---

## Le calcul d'affichage va dans le template, pas dans le back

**Preuve** : sur le préremplissage de la capacité d'investissement, commentaire du senior
« Pourquoi ne pas le faire au niveau du template ? », puis la ligne écrite par lui :
`this.form.investment_capacity ||= this.investment_capacity.amount.toFixed(0)`. La V6 le faisait
déjà en template.

**Limite à connaître** : ça ne s'applique qu'à ce qui est **calculable côté client**. Un montant
qui exige les prix n'est pas dans ce cas — `ProductListSchema` (`product/schemas.py:84`) n'expose
aucun prix, donc l'endpoint est obligatoire. Le dire d'emblée si la question revient.

---

## Un garde sur une valeur « qui ne devrait pas arriver vide » sera questionné

**Preuve** : commentaire du senior sur un garde de nullité — « Pareil, pas sûr que ça arrive vide ».

**À faire** : avant d'écrire un garde défensif, être capable de citer le chemin de code exact qui
produit la valeur vide. Si on ne le trouve pas, retirer le garde. Si on le trouve, l'énoncer —
et envisager que le vrai correctif soit en amont, dans le typage du schéma.

---

## Le mécanisme d'un nouveau document ne doit pas dépendre de celui du bon de commande

**Preuve** : commentaire du senior sur le PDF Tour de la maison — « Le mécanisme de génération de
ce document ne devrait pas être lié à celui du BDC ».

**À faire** : quand un livrable nouveau ressemble à un livrable existant, choisir sa dépendance
d'après ce qu'il **est**, pas d'après le chemin d'implémentation le plus court. Un document qui
n'est pas un bon de commande n'a pas à partager son cycle de vie.

---

## Ne pas créer un gabarit versionné identique à `common`

**Preuve** : commentaire du senior — « Pas utile pour le moment puisque contenu identique, tu peux
supprimer le template version_9 ».

**À faire** : comparer avant de créer. Voir la skill **omeo-step-version**.

---

## Ce qu'une version a hérité de sa copie et qui n'y sert plus doit partir

**Preuve** : commentaire du senior sur `version_9/solutions.html`, ligne `survey: "{{ survey_filters|safe }}"`
— « Plus la peine sur cette version ». La V9 n'a pas d'étape `survey` (`schemas/version_9.py`,
`StepsSchema`), le paramètre partait donc toujours vide. Il venait de la copie V6. Consigne
confirmée par le développeur : « je ne veux pas de code mort, si qqch ne sert plus dans cette
version, on le retire ».

**À faire** : en réécrivant un bloc d'une version copiée, vérifier chaque paramètre, clé de
contexte, méthode Alpine et bloc conditionnel contre le `StepsSchema` de la version et par `grep`
des usages. Le même héritage V6 contenait un bouton vers l'étape `survey` (manager introuvable,
`get_step_manager` renvoie `None`) et deux méthodes Alpine jamais appelées. Retirer, dans le
périmètre des fichiers touchés, même ce qu'on n'a pas écrit.

---

## Permissions Django par défaut d'abord, permission maison seulement si aucune ne convient

**Preuve** : MR Radar, retour 1 — « Je ne vois pas l'intérêt de créer 2 permissions ; Django en
crée 4 par défaut. Tu peux utiliser view_radartarget et change_radartarget ».

**À faire** : Django crée `add_`, `change_`, `delete_` et `view_<modèle>` pour chaque modèle. Les
utiliser en priorité (`view_radartarget` pour « accéder au Radar », `change_radartarget` pour
« corriger un statut »). Une entrée `Meta.permissions` reste légitime quand le droit ne correspond
à aucune des quatre actions — exemple en place : `view_team_marker` et `view_all_marker` sur
`Marker`, qui ne sont pas un simple « voir un marqueur ». Dans ce cas, le justifier dans le compte
rendu.

---

## Une valeur qui se déduit des autres champs est une `@property`, pas un champ

**Preuve** : MR Radar, retour 4 — « do_not_revisit est toujours recalculé depuis status ==
REFUSED et jamais écrit ailleurs. Une @property ne suffirait-elle pas ? »

**À faire** : si une valeur se déduit entièrement des champs du même objet, en faire une
`@property`. Un champ stocké se désynchronise (oubli, modification par l'admin), coûte une
colonne et une migration. Un champ ne se justifie que si la valeur sert à **filtrer ou trier en
base** (une `@property` est inutilisable dans `.filter()` / `.order_by()`), si c'est une **photo à
un instant** qui ne doit pas suivre les autres champs, ou si le calcul est **coûteux**. Le dire
dans ce cas.

---

## `AbstractModel` seulement si le soft-delete sert — contredit `CLAUDE.md`

**Preuve** : MR Radar, retour 2. Un logement archivé depuis l'admin restait affiché sur la carte :
le modèle héritait d'`AbstractModel`, donc d'un `status` d'archivage, que le code Radar ne
filtrait jamais.

**Ce que dit la doc** : `CLAUDE.md` — « All models inherit from `AbstractModel` » ; idem
`docs/architecture.md` et `docs/domain.md`.

**À faire** : hériter d'`AbstractModel` seulement si le code lit réellement `status` (archivage,
soft-delete). Sinon `models.Model` avec les seuls champs utiles. Si l'on hérite quand même,
chaque requête de lecture doit filtrer les archivés.

---

## Les imports vont en haut du fichier, jamais dans une fonction — contredit `docs/architecture.md`

**Preuve** : MR Radar, retour 35 — « Il faut faire attention à pas d'import dans les fonctions ».

**Ce que dit la doc** : l'exemple de signal de `docs/architecture.md` importe le service dans le
handler. Du code de `develop` fait de même (`build_team_marker_recap`, `dashboard/services.py`).

**À faire** : tout import ajouté va en haut du fichier, trié par `isort`, tests compris. Ne pas
recopier les imports locaux du voisinage, ni les déplacer s'ils sont hors périmètre. Seule
exception : `import <app>.signals` dans `apps.py::ready()`, que Django impose. Si l'import en haut
provoque une vraie erreur d'import circulaire, ne pas le remettre dans la fonction en silence : le
signaler avec le message d'erreur.

---

## Étendre la route existante plutôt que d'en créer une parallèle

**Preuve** : ticket #1485, retour 1. Une route `items_page` doublait `items_list`. Le senior :
« Pourquoi ne pas mettre la pagination dans item_list directement, avec un page_size=20 par
défaut ? », puis « Tu peux mettre à jour les autres versions ? ».

**À faire** : une ressource, une route, qu'on fait évoluer — en mettant à jour ses appelants,
**y compris dans les autres versions de déballe**. La règle de confinement d'une version porte sur
les fichiers d'étapes versionnés, pas sur une API partagée. Procédure : skill **omeo-endpoint**,
section « Avant de créer une route ».

---

## Une route par usage : liste paginée d'un côté, chargement par identifiants de l'autre

**Preuve** : ticket #1485, retour 3. Les produits sélectionnés étaient chargés par
`items_list?items_pk=`. Le senior : « Je suis partagé, sur avoir un endpoint detail à la place »,
puis « Oui, mais uniquement pour le detail ».

**À faire** : parcourir un catalogue (liste filtrée, paginée) et charger des éléments précis par
leurs identifiants (« detail », non paginée) sont deux routes. Sinon le chargement par
identifiants dépend de la pagination et peut être tronqué.

---

## Le natif du navigateur avant le JS

**Preuve** : ticket #1485, retour 4. Un swipe écrit à la main (`onTouchStart` / `onTouchEnd`) et
une piste `translateX`. Le senior : « Quel est l'intérêt de onTouchStart / onTouchEnd ? Le
conteneur est déjà scrollable nativement avec snap ».

**À faire** : avant d'écrire un gestionnaire JS, chercher l'équivalent natif — défilement
(`overflow-x-auto`) avec `scroll-snap`, `loading="lazy"`, `x-intersect` (déjà utilisé pour les
contrats et les prospects), `details` / `summary`. Le natif apporte molette, trackpad, clavier et
tactile sans code à maintenir.

---

## Une migration de la branche se régénère, elle ne s'empile pas

**Preuve** : consigne d'Ethan (08/10/2026). Sur la MR Radar, `prospect/0015_radar.py` a été
régénérée à chaque changement de modèle (retours 2, 4, 5, 6, 8, 9), et
`notification/0009_radar_recap_schedule.py` supprimée quand le mail Radar séparé a disparu
(retour 19).

**Ce que dit déjà la doc** : une migration par fonctionnalité (`CLAUDE.md`), un fichier par app
dans une MR (`docs/code-review.md`). Ce qui suit est la façon de s'y tenir quand le modèle bouge.

**À faire** : si l'app a déjà une migration propre à la branche
(`git diff --name-only origin/develop... -- src/apps/<app>/migrations/`), ne pas en ajouter une
autre : supprimer le fichier, relancer `python src/manage.py makemigrations <app> --name <suffixe>`,
passer `black`, vérifier avec `makemigrations --check`. Une migration de branche devenue sans
objet se supprime au lieu d'être annulée par une autre. Ne jamais modifier une migration présente
sur `develop` : elle est peut-être appliquée en production. La migration régénérée est déjà
marquée appliquée en base locale : demander au développeur avant de l'aligner, ses données de test
peuvent être perdues.

---
