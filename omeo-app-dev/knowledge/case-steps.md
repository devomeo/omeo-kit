# Pièges — case/steps, déballes versionnées

> Statut : fourni
> Dernière mise à jour : 2026-10-08

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

## Le PDF ne lit presque que l'étape `order` — vérifier avant de craindre une perte

**Où** : `src/apps/case/pdf/versions/version_3.py` et `pdf/versions/base.py`. `structures.py`
associe un `structure_version` à un `pdf_version` ; V6, V7, V8 et V9 partagent `pdf_version=3`.

**Preuve** : inventaire des accès `steps.*` dans `pdf/versions/` — la quasi-totalité porte sur
`steps.order.*`, plus `home.living_area`, `energy_consumption.living_area` et
`get_energy_display`. Recherche sur tout `src/apps/case/pdf/` : **zéro occurrence** de
`house_ratings`, `facade_paint`, `state_roof`, `number_occupants` ou `people`.

**À faire** : la règle « un champ non lu par la `pdf_version` est perdu » ne vaut que pour un
champ **destiné** au devis. Le devis restitue la commande et le financement, pas le diagnostic
de la maison. Avant de conclure à une perte, inventorier ce que la `pdf_version` lit réellement —
c'est une seule commande et ça évite un chantier inutile.

---

## L'Aperçu du dossier n'est pas versionné : il peut diverger de l'écran

**Où** : `src/apps/case/templates/case/overview.html:68` inclut
`case/templates/case/includes/savings.html` **sans aucune condition de version**, et cet include
envoie `people: this.case_data.steps.prime_setup.people` (ligne 48).

**Preuve** : constaté après le basculement de `people` vers `home.number_occupants` dans les trois
gabarits V9 (`solutions`, `solutions_choice`, `savings`). L'include partagé n'a pas suivi. Or
`people` alimente le forfait eau chaude de `ConsumptionCalcul.actual()` (108 kWh par personne en
électricité), donc un écart d'une personne change les économies affichées.

**À faire** : quand une source de donnée change dans les gabarits d'une version, vérifier les
includes **partagés** de l'Aperçu, pas seulement les gabarits de step. Et ne pas « réparer » un
include partagé par une expression de repli : la V6 et la V8 possèdent aussi `number_occupants`
mais calculent délibérément avec `prime_setup.people`. La correction propre est un include
versionné.

---

## Une `order_date` périmée survit à un changement de `order_date_choice`

**Où** : `src/apps/case/steps/forms/common.py` (`OrderForm.clean`) et les gabarits
`case_steps/*/order.html`, où l'input date est masqué par `x-show="order_date"` mais reste lié
par `x-model` et donc posté.

**Preuve** : sonde exécutée dans `tests/case/steps/` — un POST portant
`order_date_choice="created_at"` **et** `order_date="18/09/2026"` est valide, et
`cleaned_data["order_date"]` conserve le 18/09. `AbstractStepManager.save` écrit `cleaned_data`
tel quel dans `Step.data`, donc la date périmée est persistée.

**À faire** : côté lecture (PDF, Yousign), toujours piloter par `order_date_choice` et ne lire
`order_date` que pour les choix qui la portent (`today`, `other`). Lire `order_date` en premier
« si elle existe » ferait afficher une date abandonnée sur un BDC en « Date de création ».

---

## Un `@click.outside` dans un bloc `x-if` ouvert par un clic se referme sur ce même clic

**Où** : `case_steps/version_9/partials/product_carousel.html` — le plein écran du carrousel,
passé de `x-show` à `<template x-if="isFullScreen">` pour ne charger les images qu'à l'ouverture.

**Preuve** : constaté en recette le 2026-10-05 — au clic sur l'image principale, rien ne s'affichait.
Le gestionnaire de clic rend le bloc `x-if`, Alpine (3.10.5) l'initialise avant que le clic
atteigne `document`, et le `@click.outside` qu'il vient d'enregistrer reçoit ce même clic et
referme. Avec `x-show`, l'élément existait déjà mais caché, et `.outside` ignore un élément caché :
le problème n'apparaissait pas. Corrigé par `@click.stop` sur le déclencheur, vérifié dans le
navigateur (ouverture, flèches, bouton fermer, clic extérieur).

**À faire** : en remplaçant un `x-show` par un `x-if` pour économiser du chargement, vérifier
les `@click.outside` du bloc. Mettre `.stop` sur le clic qui l'ouvre.

---

## Un `fixed inset-0` placé sous un parent `transform` ne couvre plus l'écran

**Où** : `case_steps/version_9/solutions.html` — la piste de pagination animée par
`transform: translateX(...)`, qui contient les cards et donc le plein écran du carrousel
(`version_9/partials/product_carousel.html`).

**Preuve** : constaté en recette le 2026-10-05 — après l'ajout de la piste coulissante, l'image
cliquée restait « bloquée dans le carrousel ». Un ancêtre avec `transform` devient le bloc
conteneur des descendants `position: fixed`, et l'`overflow-hidden` de la piste les rognait.
Corrigé par `<template x-teleport="body">` (disponible dans Alpine 3.10.5) : vérifié dans le
navigateur, l'overlay est enfant de `<body>`, couvre 1920×936 sur un viewport de 1920×936, et
est retiré de `<body>` à la fermeture.

**À faire** : toute modale ou overlay `fixed` rendu dans un conteneur animé par `transform`
(ou `filter`, `perspective`) doit être téléporté vers `body`.

---

## `get_settings()` renvoie `None` au premier appel sur une base vide

**Où** : `src/apps/case/services.py:108` (`get_settings`), appelé par `SolutionsStepManager.setup()`
(`managers/version_9.py:181`).

**Preuve** : rendu de l'étape Solutions V9 via le client de test sans ligne `Settings` →
`AttributeError: 'NoneType' object has no attribute 'default_kwh_price'`. La fonction crée la
ligne mais renvoie la variable lue avant création.

**À faire** : dans un test qui rend une étape Solutions, créer `Settings.objects.create()` avant
la requête. Ne pas corriger la fonction dans une MR feature sans le signaler.
