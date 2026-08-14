---
name: omeo-step-version
description: >
  Procédure pour modifier les étapes versionnées (déballes commerciales) du CRM Omeo sans casser
  une version en production ni perdre une donnée sur un PDF. À utiliser dès qu'on touche
  case/steps/forms/version_*.py, case/steps/managers/, case/steps/templates/case_steps/,
  ou case/steps/structures.py.
---

# Toucher aux étapes versionnées

## Règle d'or

Les versions pilotées par `case/steps/structures.py` sont des **déballes commerciales distinctes**.
Une version n'en remplace pas une autre : elles coexistent volontairement, chacune servant une
offre différente. **Ce n'est pas de la dette technique.** Ne jamais fusionner ni supprimer une
version pour simplifier.

## Avant d'écrire : lire la version active équivalente

Précondition non négociable, détaillée dans la skill **omeo-preconditions** : localiser la même
logique dans la dernière version active, l'ouvrir, et citer son `fichier:ligne` avant de proposer
une implémentation.

C'est la source d'erreur numéro un sur ce projet. Une logique écrite côté service alors que la
version précédente la traitait en template a déjà coûté une implémentation complète, un revert,
et deux allers-retours avec le senior.

## Le danger : les managers partagés `common`

`case/steps/managers/common.py` et `case/steps/forms/common.py` servent **toutes** les déballes.
Avant d'y toucher :

1. Lister les versions concernées (`grep` dans `structures.py` et les `version_*`).
2. Vérifier que chacune reste fonctionnelle.
3. Préférer une modification dans la version cible plutôt que dans `common`.

Symétriquement : **ne pas créer un gabarit versionné identique à celui de `common`**. La règle de
confinement d'une version vise l'emprunt à une *autre* version, pas la copie à l'identique. Un
template versionné sans différence sera supprimé en revue.

## Couplage formulaire ↔ PDF

`structures.py` associe un `structure_version` à un `pdf_version`, et plusieurs versions partagent
la même. Si un champ est ajouté à un formulaire mais que la `pdf_version` correspondante ne le lit
pas, **la donnée est perdue silencieusement sur le devis client**.

Après tout ajout de champ, dérouler la chaîne formulaire → service → `case/pdf/`.

## Réordonner des étapes

Vérifier deux choses, dans cet ordre :

1. **`active=False`** sur la structure. La position de l'affaire est stockée : sur une structure
   active, une permutation redirige les affaires en cours vers une autre étape.
2. **Aucune étape déplacée ne lit les données d'une étape devenue postérieure.** Un `grep` du slug
   de l'étape reculée dans les templates et managers de l'étape avancée suffit à trancher.

## Pièges de rendu et de validation

Consulter `knowledge/case-steps.md` avant de modifier un formulaire ou un template : le filtre
`default` de Django qui transforme `initial=0` en chaîne vide, l'option `(0, "")` qui rend
`required=True` inopérant, l'absence de garantie qu'une étape amont ait été enregistrée. Chacun
de ces points a déjà produit un bug sur ce projet.

## Procédure

1. Identifier la ou les versions concernées, et si `common` est touché.
2. Lire l'équivalent dans la dernière version active et le citer.
3. La logique va dans le service ; le formulaire reste présentation et validation.
4. Vérifier l'impact PDF.
5. Tests : couvrir chaque version impactée, cas nominal et cas d'erreur.
6. Validation : voir la skill **omeo-validation**.
