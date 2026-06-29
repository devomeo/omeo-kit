---
name: touch-step-version
description: >
  Procédure pour modifier les étapes (Steps) versionnées du CRM Omeo en toute sécurité. À utiliser
  dès qu'on touche case/steps/forms/version_*.py, case/steps/managers/, case/steps/structures.py,
  ou un manager partagé common. Évite de casser une déballe commerciale ou un PDF.
---

# Toucher aux étapes versionnées (déballes)

## Règle d'or à comprendre avant tout

Les versions de Steps (`version_1.py` … `version_8.py`, pilotées par `case/steps/structures.py`)
sont des **déballes commerciales distinctes**. Une version **n'en remplace pas** une autre : elles
coexistent volontairement, chacune servant une offre commerciale différente. **Ce n'est PAS de la
dette technique à nettoyer.** Ne jamais supprimer/fusionner une version sous prétexte de simplifier.

## Le vrai danger : les managers partagés `common`

`case/steps/managers/common.py` et `case/steps/forms/common.py` sont utilisés par TOUTES les
déballes. **Toute modification de `common` impacte simultanément toutes les versions.**

Avant de modifier `common` :
1. Lister les versions qui utilisent l'élément modifié (`grep` dans `structures.py` et les `version_*`).
2. Vérifier que chaque version concernée reste fonctionnelle après le changement.
3. Préférer, si possible, une modification dans la version cible plutôt que dans `common`.

## Couplage formulaire ↔ PDF

`structures.py` associe un `structure_version` à un `pdf_version`. Si tu ajoutes un champ à un
formulaire mais que la version PDF correspondante ne le lit pas → **perte de données silencieuse**
sur le devis. Vérifie toujours la chaîne form → service → génération PDF (`case/pdf/`).

## Procédure

1. Identifier la/les version(s) concernée(s) et si `common` est touché.
2. Modifier dans la couche service ; le formulaire reste de la présentation/validation.
3. Vérifier l'impact PDF (champ bien repris dans la bonne `pdf_version`).
4. Tests : couvrir chaque version impactée (happy-path + cas d'erreur).
5. Validation : `pytest`, `mypy src/`, `flake8`, `black --check .`, `isort --check-only .`.
6. Revue : **architecte-django** + **/omeo-review**. Un humain valide.
