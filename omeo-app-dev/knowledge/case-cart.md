# Pièges — case/cart, prix et primes

> Statut : fourni
> Dernière mise à jour : 2026-08-14

Lire `README.md` avant d'ajouter une entrée : clause d'évolution et clause de preuve.

---

## `get_default_price` explose si on ne lui passe pas `user`, sur la majorité des variantes

**Où** : `src/apps/product/services.py:361`, branche `except Price.DoesNotExist` ligne 378.

**Preuve** : `AttributeError: 'NoneType' object has no attribute 'has_perm'`, reproduit par un
test avec une variante dont le seul prix est de type `manager`. Mesure sur `src/data.json` :
**407 variantes sur 693 n'ont aucun prix `default` actif**, donc prennent cette branche. Les PAC
air/air réelles utilisent `mini`, `regular`, `reno`, `fair` — jamais `default`.

**À faire** : toujours passer `user` à `get_default_price` / `get_default_price_type`. Le modèle
correct est `CartStorageManager.add_default_products` (`case/cart/managers/storage.py:113`), pas
`assign_products_to_case` (`case/cart/services.py:39`) qui l'omet parce qu'il ne sert qu'à la V4.

---

## « Prix par défaut » ne veut pas dire `PriceType.DEFAULT`

**Où** : `src/apps/product/services.py:374-386`.

**Preuve** : quand aucun prix `default` n'existe, le repli exclut les types interdits à
l'utilisateur (`_RESTRICTED_PRICE_PERMS`) puis prend le premier restant.

**À faire** : comprendre que le montant obtenu **dépend des permissions du commercial connecté**.
Deux vendeurs sur la même affaire avec les mêmes produits peuvent voir deux chiffres différents.
Si un besoin exige un montant stable, le signaler au senior : ce n'est pas le comportement actuel.

---

## `sync_selected_by_ids` ne fait que filtrer — il n'ajoute jamais de produit

**Où** : `src/apps/case/cart/managers/storage.py:683`.

**Preuve** : lecture du corps (trois lignes, une compréhension de liste filtrante). Conséquence
observée : à l'étape Solutions, `cart.products` et `cart.amounts` restent vides, tout bloc qui
lit `case_data.cart.amounts` y affiche 0.

**À faire** : ne pas supposer qu'une sélection de produits alimente le panier. Les setups et les
montants n'apparaissent qu'à Solutions choisies, via `api:select_item`.

---

## `CartStorageManager.add_default` est inutilisable avant l'étape Aides

**Où** : `src/apps/case/cart/managers/storage.py:115` (et `:94` pour les packs).

**Preuve** : sonde exécutée en test — `AttributeError: 'NoneType' object has no attribute 'level'`.
`add_default_products` lit `self.case_schema.steps.prime_setup.level.level`, or `prime_setup` vaut
`None` tant que l'étape Aides n'a pas été enregistrée.

**À faire** : pour chiffrer avant Aides, construire le `SetupSchema` à la main avec `level=1`,
comme le fait `assign_products_to_case`. C'est la raison d'être de ce `level=1` en dur, ce n'est
pas un raccourci.

---

## `PriceManager.compute` exige un panier persisté et retombe silencieusement sur le niveau 1

**Où** : `src/apps/case/cart/managers/price.py:721`, puis `case/cart/services.py:136`.

**Preuve** : `get_prime_level_from_cart` fait `Cart.objects.get(pk=...)` puis
`Step.objects.get(slug="prime_setup")`, avec un `except Step.DoesNotExist` qui renvoie `level_1`.

**À faire** : deux `level` distincts cohabitent dans la chaîne — celui qui choisit **quel type de
prix** retenir (`get_default_price_type`) et celui qui applique `price_by_level` au montant. Ne pas
les confondre. Avant Aides, les deux valent 1.

---

## Instancier un `CartSchema` déclenche le calcul complet des montants

**Où** : `src/apps/case/cart/schemas.py:402`, `@model_validator(mode="after")`.

**Preuve** : lecture ; exploité pour chiffrer un panier en mémoire sans le sauvegarder.

**À faire** : s'en servir plutôt que de réécrire un calcul de prix. Construire un `CartSchema` avec
l'`id` du panier réel et des setups en mémoire suffit à obtenir TVA, pose et primes.

---

## Une formule sans données ne lève pas d'erreur, elle renvoie 0

**Où** : `src/apps/product/managers.py:14` (`keywords_replacer`).

**Preuve** : tout jeton absent du formulaire est remplacé par `"0"`, et la branche générique
d'évaluation est enveloppée dans un `try/except Exception`.

**À faire** : ne jamais interpréter un 0 comme « le produit est gratuit ». Un 0 signifie le plus
souvent que le formulaire de configuration n'a pas été rempli.

---

## Aucun contrôle de propriété sur `case_pk` dans toute la famille `case/*`

**Où** : `src/apps/case/cart/api.py`, et aussi `case/consumption`, `case/loan`, `case/prime`,
`case/investment`, `case/pvgis`, `case/builder`.

**Preuve** : comptage sur les 22 modules `api.py` du projet — **environ 42 routes sur 164 vivent
dans des modules sans un seul `@has_perm`**, et c'est exactement cette famille. En face, `product`
(32 routes), `crm`, `prospect`, `contract` sont couverts.

**À faire** : ne pas invoquer la parité avec les voisins pour justifier un nouvel endpoint non
protégé — le voisinage est précisément le sous-ensemble non couvert. Suivre la procédure endpoint,
pas la coutume locale.

---
