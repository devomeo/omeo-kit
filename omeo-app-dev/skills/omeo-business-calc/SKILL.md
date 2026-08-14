---
name: omeo-business-calc
description: >
  Procédure pour ajouter ou modifier un calcul métier du CRM Omeo (prix, primes, prêts, panier)
  sans produire de montant faux silencieux. À utiliser sur tout changement dans product/,
  case/cart/, case/prime/, case/loan/.
---

# Modifier un calcul métier sans montant faux

Une erreur ici ne plante pas : elle sort un mauvais montant sur un devis client. C'est le mode de
défaillance le plus coûteux du projet, parce qu'il se relit bien.

## Encodages à connaître avant de toucher

**Prix par niveau** — `src/apps/product/utils.py:4` (`price_by_level`). Un prix est soit une valeur
unique (`"1200"`), soit des valeurs séparées par `-`, indexées par niveau de prime.

```python
prices = price.split("-")
return float(prices[level_code - 1])   # aucune borne
```

Deux dangers, tous deux vérifiés par lecture : un niveau supérieur au nombre de segments lève
`IndexError` ; et `level_code = 0` renvoie `prices[-1]`, c'est-à-dire **le dernier segment,
silencieusement**. La virgule décimale est gérée en amont (`replace(",", ".")`), pas la valeur
non numérique multi-segments.

**Grilles de primes** — `src/apps/case/prime/constants.py`, `DEFAULT_PRIME_GRID` (ligne 37) et
`ANAH_GRID` (ligne 149). Seuils de revenus croisés avec la taille du foyer. **Valeurs
réglementaires.**

**Formules produit** — champ `formula` sur le modèle `Variant` (`src/apps/product/models.py:281`,
et non sur `Product`), évalué par `src/apps/product/managers.py` après substitution des `{tokens}`.

**Prêts** — `src/apps/case/loan/banks/` contient `bnp.py` et `projexio.py`, taux et assurances en dur.

## Règles

- **Borner tout parsing `-`** : vérifier la longueur avant d'indexer, et ne jamais laisser passer
  un niveau à 0.
- **Un token de formule inconnu est remplacé par `0` sans erreur**
  (`product/managers.py:14`, `keywords_replacer`), et la branche générique d'évaluation est
  enveloppée dans un `try/except Exception`. Conséquence : **un 0 ne signifie pas « gratuit », il
  signifie le plus souvent « formulaire non rempli »**. Ne jamais afficher un tel 0 comme un
  montant sans s'être assuré que la configuration existe.
- **Toute valeur réglementaire modifiée exige sa source officielle et sa date d'effet**, énoncées
  dans la MR. Ne jamais inventer un seuil ni un taux. En cas d'ambiguïté, escalade humaine.
- **Renommer un champ d'un schéma de panier casse les paniers existants** : `Cart.products` et
  `Cart.packs` sont des `JSONField` figés au moment de la vente. Prévoir la rétro-compatibilité.
- **Ne pas réécrire un calcul de prix.** Instancier un `CartSchema` déclenche
  `PriceManager.compute` via un `@model_validator(mode="after")` (`case/cart/schemas.py:402`) et
  fournit TVA, pose et primes. Voir `knowledge/case-cart.md`.

## Tests de bord obligatoires

- **Prix** : 1 segment, 4 segments, niveau au-delà du nombre de segments, niveau 0, virgule
  décimale, valeur non numérique.
- **Primes** : revenu exactement au seuil, juste en dessous, juste au-dessus ; foyer à la taille
  maximale de la grille et au-delà.
- **Prêts** : durée extrême, apport nul, report.
- **Formules** : token absent du formulaire, division par zéro.

**Choisir les données de test d'après la production, pas d'après la commodité.** Quand un service
se ramifie selon la forme des données, vérifier la répartition réelle avant d'écrire le test — un
comptage sur `src/data.json` suffit souvent. Un jeu trop favorable a déjà rendu un test vert
pendant que l'endpoint tombait en 500 sur la majorité des produits.

## Validation

Voir la skill **omeo-validation**.
