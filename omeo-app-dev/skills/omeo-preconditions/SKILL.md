---
name: omeo-preconditions
description: >
  Les trois vérifications à effectuer AVANT d'écrire du code sur le CRM Omeo. À utiliser dès
  qu'on s'apprête à ajouter une logique dans une version de déballe, à créer un identifiant, ou
  à s'inspirer d'une fonction existante. Ce sont des préalables, pas une revue.
---

# Trois préconditions, avant la première ligne

Ces trois règles couvrent la majorité des reprises demandées en revue sur ce projet. Elles
s'appliquent **avant** d'écrire, pas après. Une revue ne les rattrape pas : elle lit ce qui a été
écrit, jamais le chemin qui n'a pas été pris.

## 1. Lire l'équivalent existant, et le citer

Avant d'écrire une logique dans une version de déballe (`version_N`), localiser la même logique
dans la dernière version **active** et l'ouvrir.

Sortie attendue : un `fichier:ligne`, énoncé explicitement, avant de proposer une implémentation.

Si l'équivalent n'existe pas, le dire — c'est une information en soi, et souvent le signe qu'il
faut poser une question plutôt qu'inventer.

> Cas réel : le préremplissage de la capacité d'investissement a été écrit côté service alors que
> la V6 le faisait en template depuis toujours. Coût : une implémentation, un crash, un revert
> complet, deux allers-retours, et le senior finissant par écrire lui-même la ligne.

## 2. Aucun identifiant nouveau sans précédent

Avant de nommer une variable, un champ, un flag ou une méthode : `grep` le nom dans le dépôt.

S'il n'existe nulle part, deux possibilités seulement — soit le concept existe déjà sous un autre
nom qu'il faut trouver et réutiliser, soit on introduit un concept nouveau, et cela se signale
explicitement avant de le faire.

> Cas réel : `usesParentConsumption`, inventé pour exprimer une distinction que le reste du code
> n'exprime nulle part. Commentaire du senior : « c'est quoi ». Supprimé.

Corollaire déjà tranché par le senior : dans une MR feature, on **reproduit le motif en place,
même dupliqué**. La déduplication fait l'objet d'une MR dédiée.

## 3. Copier une fonction impose de la differ

Quand on s'inspire d'une fonction existante, comparer ligne à ligne la version écrite et son
modèle, et **justifier chaque écart** — en particulier chaque argument omis.

> Cas réel : `_default_setup` a été calqué sur `assign_products_to_case`, qui n'a pas d'argument
> `user`. Le bon modèle était `add_default_products`, qui en a un. L'argument manquant a fait
> tomber l'endpoint en 500 sur la majorité des produits réels, et les tests ne l'ont pas vu parce
> qu'ils utilisaient les seules données qui empruntent l'autre branche.

Corollaire sur les tests : quand un service se ramifie selon la forme des données, **tester la
branche que prennent les données de production**, pas celle qui est commode à construire. Vérifier
la répartition réelle dans `src/data.json` quand c'est possible.

## Signalement plutôt qu'arbitrage

Quand deux consignes du projet se contredisent, le dire au lieu de trancher seul.

> Cas réel : la règle de confinement V9 (« tout gabarit appartient à `version_9` ») contre la règle
> de non-duplication. Le conflit a été résolu silencieusement en faveur de la première, ce qui a
> produit un template identique à `common`, supprimé en revue.
