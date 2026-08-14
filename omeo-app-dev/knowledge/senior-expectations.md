# Attentes du développeur senior — y compris là où elles contredisent la doc

> Statut : partiel
> Dernière mise à jour : 2026-08-14

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
