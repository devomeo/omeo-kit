---
name: add-business-calc
description: >
  Procédure pour ajouter ou modifier un calcul métier du CRM Omeo (prix, primes/subventions,
  prêts, panier) sans produire de montant faux silencieux. À utiliser sur tout changement dans
  product/, case/cart/, case/prime/, case/loan/.
---

# Modifier un calcul métier en sécurité

Une erreur ici ne plante pas : elle génère un mauvais montant sur un devis client. Procède avec
des garde-bornes et des tests de bord systématiques.

## 1. Comprendre les encodages avant de toucher

- **Prix `"l1-l2-l3-l4"`** : un prix est soit une valeur unique (`"1200"`), soit 4 valeurs par
  niveau de prime séparées par `-`. Parsing : `product/utils.py::price_by_level`. Il fait
  `split("-")[level-1]` **sans borne** → IndexError possible.
- **Grilles de primes** : `case/prime/constants.py` (`DEFAULT_PRIME_GRID`, `ANAH_GRID`) — seuils de
  revenus × taille de foyer → niveau (1–4). **Valeurs réglementaires.**
- **Formules produit** : champ `formula` (admin, `product/models.py:275`) évalué par
  `product/managers.py` (`eval` après substitution des `{tokens}`).
- **Prêts** : taux/assurances en dur (`case/loan/banks/projexio.py`, BNP).

## 2. Règles à appliquer

- **Toujours border un parsing `-`** : vérifier la longueur avant d'indexer, prévoir un fallback,
  gérer la virgule décimale et la valeur non numérique.
- **Modifier une valeur réglementaire (seuil de prime, taux) ⇒ citer la source officielle et la
  date d'effet** dans le commentaire/la PR. Ne jamais inventer une valeur.
- **Token de formule inconnu** = remplacé par `0` silencieusement → calcul faussé. Vérifier que
  tous les tokens existent dans le formulaire.
- **Schéma de panier** : renommer/changer un champ Pydantic casse les paniers existants — prévoir
  la rétro-compat ou une migration de données.

## 3. Tests de bord OBLIGATOIRES (déléguer à l'agent qa-tests si besoin)

- Prix : 1 segment, 4 segments, niveau hors bornes, virgule, valeur non numérique.
- Primes : revenu exactement au seuil, juste sous/au-dessus, foyer à la taille max et au-delà.
- Prêts : durée extrême, apport nul, report.
- Formules : token inconnu, division par zéro.

## 4. Validation
`pytest`, `mypy src/`, `flake8`, `black --check .`, `isort --check-only .`

## 5. Revue
Lancer **backend-metier** puis **/omeo-review**. Un humain valide. Pour toute ambiguïté
réglementaire, escalade humaine obligatoire.
