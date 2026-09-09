# Pièges — product/catalogs, prix menuiserie

> Statut : fourni
> Dernière mise à jour : 2026-09-09

Lire `README.md` avant d'ajouter une entrée : clause d'évolution et clause de preuve.

Périmètre : les 11 fichiers de `src/apps/product/catalogs/` (`window_bb/bc/cc`, `glass_bb/bc/cc`,
`door_bb/bc/cc`, `roof_window`, `shutter`) et leur mise à jour depuis le tarif fournisseur.

---

## Aucun coefficient ni aucune marge n'existe dans l'app : les prix sont calculés dans Excel et collés en dur

**Où** : `src/apps/product/catalogs/*.py`, et `convert_grid_list.ipynb` à la racine du dépôt.

**Preuve** : `grep -rnE "\b(627|696|3150)\b" --include="*.py" src/ | grep -v catalogs/` → aucune
occurrence. Les 4 enregistrements `product.price` rattachés aux produits fenêtre ont `price`,
`price_installation` et `area` à `None` (mesure sur `src/data.json`). Le notebook ne fait que
`pbpaste` → `int()` → `pbcopy` : il ne calcule rien, et convertit en `0` tout ce qui n'est pas un
entier.

**À faire** : ne pas chercher le coefficient dans le code, l'admin ou la base — il n'y est pas.
La formule vit dans un classeur Excel hors dépôt. Pour la connaître, ouvrir le classeur en mode
formules (`data_only=False`) : les blocs de prix de vente y sont de vraies formules
(`=(B3+12+140)*3.73`), pas des constantes.

---

## Pour vérifier une grille, l'écart au prix d'achat doit être constant sur toute une colonne

**Où** : `src/apps/product/catalogs/window_bb.py` et voisins.

**Preuve** : sur « Fenêtre 1 ouvrant » blanc, `prix_du_code − 3 × achat_fournisseur` vaut
exactement `660` sur les **148 cellules** de la grille. Avec un multiplicateur faux l'écart dérive
au lieu d'être constant (×2 : 753 → 827 ; ×4 : 567 → 493). C'est ce test qui a isolé deux colonnes
corrompues au milieu de 3 200 valeurs justes.

**À faire** : après tout collage, recalculer cet écart **colonne par colonne**. Une colonne saine
donne une constante ; une colonne qui dérive est un collage raté. Ne pas se contenter d'un
sondage sur quelques cellules.

---

## Un collage partiel laisse une colonne à l'ancien tarif, et rien ne le signale

**Où** : `window_bb.py` / `Fixe`, 21ᵉ colonne (largeur 2400) ; `window_bc.py` / `Fixe`, 19ᵉ colonne
(largeur 2200).

**Preuve** : `git show 5db6f9e5^:src/apps/product/catalogs/window_bb.py` — les 22 valeurs de ces
deux colonnes étaient identiques, au chiffre près, à celles d'avant le commit `5db6f9e5`
(22 janvier 2026) qui a pourtant divisé toutes les grilles Normal par `7/6`. La sélection Excel
n'avait pas couvert toute la largeur. Ces prix sont restés faux **huit mois** en production, sans
qu'aucune pipeline ne bronche.

**À faire** : compter les colonnes de la sélection avant de copier, et vérifier après collage que
la grille entière suit la même règle. Le mode de défaillance n'est pas « tout faux », c'est
« une colonne oubliée ».

---

## Le convertisseur décale silencieusement une ligne trouée en son milieu

**Où** : `convert_grid_list.ipynb`, première cellule — `row = [convert_to_int(v) for v in line.split()]`.

**Preuve** : logique du notebook exécutée telle quelle. Entrée `"954\t\t966\t978"` → sortie
`[954, 966, 978, 0]` : `split()` sans argument fusionne les séparateurs consécutifs, donc `966`
prend la place du trou et la ligne est décalée d'un cran. Même effet avec un séparateur de
milliers : `"1 044"` produit deux entiers, `1` et `44`.

**À faire** : n'accepter des trous qu'en **fin** de ligne (ils deviennent des `0`, ce qui est le
comportement voulu). Formater la zone copiée en nombre brut, sans séparateur de milliers et sans
décimale.

---

## Les bornes `h_min`/`w_min` déclarées ne décrivent pas la matrice — c'est la matrice qui fait foi

**Où** : `window_bb/bc/cc.py` — `Fixe` déclare `h_min=800, h_max=2900, w_min=600, w_max=3000` pour
une matrice de 16×21. Aussi `Porte-fenêtre 1 ouvrant` (6×4 déclaré, matrice 5×5),
`Porte-fenêtre 2 ouvrants` (6×7 déclaré, matrice 5×11), `door_*/Porte d'entrée Réno` (7 lignes
déclarées, matrice 8).

**Preuve** : `catalogs/schemas.py:32` génère les axes par `range(h_min, h_max + 1, 100)`, et
`fetch_pricing` indexe la matrice **par position dans cette liste**. Le tarif fournisseur donne
H 400→1900 × L 400→2400 pour le Fixe, soit exactement 16×21. Conséquence : un fixe est facturé au
prix d'un modèle **400 mm plus bas et 200 mm plus étroit**, et toute hauteur ≥ 2400 sort de la
matrice et renvoie `0` (`catalogs/__init__.py:116`).

**À faire** : aligner toute comparaison et toute correction sur la **position dans la matrice**,
jamais sur les bornes déclarées. Un test « nombre de bornes déclarées == taille de la matrice »
attraperait ces incohérences ; il n'existe pas.

---

## 40 des 84 matrices sont inatteignables : `Mini` et `Réno` sont du code mort

**Où** : `src/apps/product/catalogs/__init__.py:46`.

**Preuve** : `build_catalog_name` ne retient que `item.price_type == PriceType.DEFAULT`, et c'est
la seule source des choix de modèle, aussi bien pour le formulaire panier
(`case/cart/forms.py:173`) que pour l'API (`product/services.py:519`). Comptage par AST sur les
11 fichiers : **84 matrices, dont 44 en `default`** — les 40 autres ne peuvent pas être
sélectionnées.

**À faire** : ne pas les mettre à jour « par cohérence » sans arbitrage explicite, et ne pas
s'alarmer d'une anomalie de prix qui n'y vit que. Vérifier d'abord le `price_type`.

---

## `valid_catalog_price` ne contrôle que la première configuration

**Où** : `src/apps/case/cart/managers/storage.py:530`.

**Preuve** : le `return amount != 0` est **à l'intérieur** de la boucle
`for key, value in form_data.items()` ouverte ligne 522. La méthode rend donc son verdict sur la
première configuration et ignore les suivantes. Elle est le seul garde-fou côté ajout au panier
(`case/cart/services.py:539`).

**À faire** : ne pas compter sur une case à `0` pour bloquer une vente. Elle ne protège que la
première configuration d'un ajout multiple ; au-delà, une ligne à **0 €** part au devis.

---

## Aucun test ne vérifie une valeur de prix : la CI reste verte quoi qu'on colle

**Où** : `tests/product/`, `tests/case/cart/`.

**Preuve** : **3 202 prix modifiés** dans 6 fichiers de catalogue, puis `tests/product` +
`tests/case/cart` → **215 passés**, suite complète → **1 726 passés**, zéro échec lié. Les
5 fichiers de tests qui mentionnent `catalog` n'exercent que la mécanique de lecture.

**À faire** : ne jamais conclure d'une CI verte qu'un lot de prix est bon. La seule vérification
qui vaut est la comparaison de la grille au tarif, entrée n° 2 de ce fichier.

---

## Changer un prix de catalogue est rétroactif sur tous les dossiers non validés

**Où** : `src/apps/case/cart/schemas.py:435` (`compute_amounts`).

**Preuve** : `@model_validator(mode="after")` — toute instanciation de `CartSchema` relance
`PriceManager.compute`, qui relit la matrice directement dans le code Python
(`case/cart/managers/price.py:106`). Il n'existe aucune date d'effet dans le système. Les projets
déjà validés sont figés dans `Project.cart_snapshot` et ne bougent pas.

**À faire** : annoncer la bascule dans la MR. Le jour du déploiement, tout devis en cours non
validé change de montant, y compris ceux déjà présentés au client.

---

## Les primes menuiserie ne dépendent pas du prix — inutile de refaire l'enquête

**Où** : enregistrements `prime.prime` des produits `window_bb/bc/cc`.

**Preuve** : mesure sur `src/data.json` — la formule de prime des trois produits fenêtre est
`{single_glazed_replaced}*{level}`, sans jeton `{price}`. Les produits `door_*` n'ont aucune prime
rattachée.

**À faire** : un changement de prix menuiserie n'a aucun effet sur les primes. Le vérifier reste
sain, mais l'investigation est déjà faite.

---

## L'imposte ne suit pas la règle des autres grilles

**Où** : `window_bb/bc/cc.py` et `glass_bb/bc/cc.py`, entrées `Imposte`.

**Preuve** : dans le classeur fournisseur, l'onglet `Imposte` porte `=(C3+267)*0.41` puis `=C49*3`,
là où les autres onglets portent `=(B3+…)*3.73`. Cet onglet est aussi le seul dont les **3 lignes
par hauteur** sont les trois couleurs (blanc, couleur 1 face, couleur 2 faces), au lieu d'un
onglet par couleur. Vérifié : les 251 cellules de chaque couleur correspondent trait pour trait.
En prime, `Imposte` et `Imposte Mini` sont la **même grille** dans les trois `window_*`.

**À faire** : ne pas appliquer aux impostes le coefficient des autres grilles, et ne pas chercher
un onglet « Imposte couleur » — il n'existe pas.

---
