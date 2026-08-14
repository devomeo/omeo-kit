# Pièges — case/steps, déballes versionnées

> Statut : fourni
> Dernière mise à jour : 2026-08-14

Lire `README.md` avant d'ajouter une entrée : clause d'évolution et clause de preuve.

---

## Le filtre `default` de Django transforme `initial=0` en chaîne vide côté Alpine

**Où** : les templates de step, `{% for field in form %}{{ field.name }}: '{{ field.value|default:"" }}'`.

**Preuve** : le filtre `default` de Django s'applique à toute valeur **falsy**, pas seulement à
`None`. Un `IntegerField(initial=0)` arrive donc dans l'état Alpine comme `''`.

**À faire** : c'est ce qui fait fonctionner les gardes `!this.form.x` et `x ||= …`. Ne pas les
« corriger » en croyant à un bug, et ne pas compter sur un `0` numérique côté JS.

---

## Un choix `(0, "")` rend la valeur « 0 » valide — `required=True` ne suffit pas

**Où** : les `ChoiceField` des formulaires de step.

**Preuve** : testé sur `number_occupants` — avec `(0, "")` en tête de liste, la soumission vide
passait la validation. Corrigé avec `("", "")` : vide rejeté, zéro rejeté, trois accepté.

**À faire** : pour forcer un choix réel, l'option neutre doit être `("", "")`.

---

## Aucune étape n'est garantie remplie, même les précédentes

**Où** : `src/apps/case/steps/views.py` (fonction `step`), et `case/steps/services.py:111`.

**Preuve** : la vue n'impose aucune complétion des étapes antérieures, et les lignes `Step` sont
créées paresseusement par un `get_or_create` **au moment de l'enregistrement**. Erreur rencontrée :
`'NoneType' object has no attribute 'consumptions'` en supposant l'inverse.

**À faire** : ne jamais présumer qu'une étape amont a été enregistrée. Vérifier l'existence avant
d'accéder à `case.steps.<slug>`.

---

## La résolution des formulaires et templates suit la version de l'affaire, pas celle du module

**Où** : `AbstractStepManager.get_form()` et la résolution `case_steps/version_{N}/{slug}.html`.

**Preuve** : la version utilisée est le `structure_version` de l'affaire, avec repli sur `common`.

**À faire** : un manager emprunté à `version_6` par une structure V9 rendra malgré tout les
gabarits et formulaires V9. Ne pas en déduire que le code est partagé.

---

## Créer un template versionné identique à `common` n'apporte rien et sera refusé en revue

**Où** : `case/steps/templates/case_steps/version_N/`.

**Preuve** : commentaire du senior — « Pas utile pour le moment puisque contenu identique, tu peux
supprimer le template version_9 ».

**À faire** : avant de créer un gabarit versionné, le comparer à celui de `common`. S'il n'en
diffère en rien, ne pas le créer. La règle de confinement V9 vise l'emprunt à une autre version,
pas la copie à l'identique.

---

## Réordonner les étapes dans `structures.py` n'est sûr que si la structure est inactive

**Où** : `src/apps/case/steps/structures.py`.

**Preuve** : la position de l'affaire est stockée ; sur une structure `active=True`, une
permutation redirige les affaires en cours vers une autre étape.

**À faire** : vérifier `active=False` avant toute permutation, et vérifier que les étapes
déplacées ne lisent pas les données d'une étape désormais postérieure. Exemple vécu : déplacer
Solutions avant Aides n'était possible qu'après avoir retiré la lecture de `prime_setup.people`
du template Solutions.

---

## `investment_capacity` ignore le paramètre `duration`

**Où** : service de calcul de la capacité d'investissement, qui lit `.years[1]`.

**Preuve** : vérifié empiriquement — le résultat vaut 50,88 pour des durées de 5, 10, 20 et 30.

**À faire** : ne pas exposer `duration` comme s'il agissait, et ne pas écrire de test qui
affirmerait une dépendance à la durée.

---

## Troncature côté Python contre arrondi côté JS : écarts de 1 €

**Où** : `DisplayCalcul.projection_consumption` (`int(...)`) contre `.toFixed(0)` dans les templates.

**Preuve** : constaté à l'écran — 43 780 € d'un côté, 43 781 € de l'autre pour la même valeur.

**À faire** : afficher une valeur déjà calculée côté serveur plutôt que de la recalculer en JS,
quand les deux doivent coïncider.

---

## Un champ ajouté à un formulaire n'atteint pas forcément le PDF

**Où** : `structures.py` associe un `structure_version` à un `pdf_version` ; V6, V7, V8 et V9
partagent `pdf_version=3`.

**Preuve** : règle documentée dans le plugin précédent, non contredite par le code.
⚠️ **non vérifié** sur les ajouts récents (`facade_paint` sur `HouseRatingsForm`, passage de
`number_occupants` en obligatoire) — la chaîne formulaire → service → PDF reste à contrôler.

**À faire** : après tout ajout de champ, vérifier que la `pdf_version` correspondante le lit,
sinon la donnée est perdue silencieusement sur le devis client.

---
