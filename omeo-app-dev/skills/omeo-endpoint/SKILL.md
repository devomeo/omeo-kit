---
name: omeo-endpoint
description: >
  Procédure pour ajouter ou modifier une route API Ninja sur le CRM Omeo sans créer de fuite de
  données entre utilisateurs. À utiliser dès qu'on crée ou édite une route dans un fichier api.py
  exposant des données métier (Case, Cart, Contract, Contact, Repair, Bilan, Commission…).
  Remplace add-secure-endpoint d'omeo-kit.
---

# Ajouter une route API isolée et testée

Suivre l'ordre des couches : `schemas → services → api → tests`.

## 0. L'argument de parité ne vaut pas ici

Avant tout : **ne pas justifier une route non protégée par le fait que ses voisines ne le sont pas.**

Mesure sur les 22 modules `api.py` du dépôt : environ **42 routes sur 164 vivent dans des modules
sans un seul `@has_perm`**, et ce n'est pas réparti au hasard — c'est `case/cart`, `case/consumption`,
`case/loan`, `case/prime`, `case/investment`, `case/pvgis`, `case/builder` et `notification`. En
face, `product` (32 routes), `crm`, `prospect`, `contract`, `project` sont couverts.

Le voisinage d'une nouvelle route de `case/*` est donc précisément le sous-ensemble non couvert.
S'y aligner reconduit le trou au lieu de le combler.

## 1. Schéma (`schemas.py`)

Schéma d'entrée et de sortie. Toute la validation est centralisée ici.

Pour un paramètre de requête recevant une liste jointe par virgules, reprendre le validateur
existant plutôt que d'en inventer un : `ConsumptionMultipleSchema.clean_selected_items`
(`case/consumption/schemas/calculs.py:66`).

## 2. Service (`services.py`) — c'est là que se joue la sécurité

La logique vit dans le service, jamais dans `api.py`.

- **Filtrer par propriétaire** : pour une liste, partir de `Model.objects.filter(owner=user)`.
- **Élargir à l'équipe uniquement derrière une permission.** Référence exacte à copier —
  `case/services.py:87` (`get_cases`) :

```python
if user.has_perm("case.view_team_case") and user.teams.exists() and not user.is_superuser:
    teams = user.teams.values_list("name", flat=True)
    query &= Q(owner=user) | Q(owner__teams__name__in=[teams])
elif not user.has_perm("case.view_all_case"):
    query &= Q(owner=user)
```

- **Accès par PK** : un `get_*_by_pk` qui ne revérifie pas la propriété ne doit pas être exposé
  tel quel. Soit le service prend `user` et filtre, soit la route vérifie avant de retourner.
- **Un `case_pk` reçu en paramètre est une donnée d'entrée non fiable**, même si l'appel provient
  d'un template de step : rien n'empêche de le remplacer.

## 3. API (`api.py`)

Handler fin : valider via le schéma, appeler le service, retourner.

```python
@router.get("/…/", response=…Schema, url_name="…", tags=["…"])
@has_perm(["<app>.<codename>"])
def ma_route(request, data: MonSchema = Query(...)):
    return services.mon_service(**data.dict(), user=request.user)
```

- **`@has_perm([...])` sur toute route de données.** `core/permissions.py:7` lève 401 si non
  authentifié, 403 si la permission manque.
- `has_perm` ne contrôle **que** le niveau modèle. Il ne remplace pas le filtrage propriétaire du
  service. Les deux sont nécessaires.
- Codenames réels du projet, à imiter : `case.view_case`, `case.sign_case`, et les permissions
  personnalisées de type `case.create_version_9`.
- `url_name=` obligatoire, IDs en query params.
- **Passer `user=request.user` au service** dès que celui-ci résout un prix, une permission ou une
  donnée filtrée. Un `user` oublié ne provoque pas toujours une 403 : il peut faire tomber le
  service en 500 (voir `../../knowledge/case-cart.md`, entrée `get_default_price`).

## 4. Test d'isolation — obligatoire

`STAGE = "pytest"` dans `tests/settings.py`, et le contournement `if settings.STAGE == "local"`
de `has_perm` **ne s'applique donc pas en test**. L'authentification de l'API Ninja est désactivée
en pytest, mais le décorateur, lui, s'applique : les assertions 401/403 fonctionnent.

La fixture s'appelle **`api_client`** (`tests/conftest.py:132`) — *il n'existe pas de
`api_client_factory`*. C'est une factory : `api_client(router, user=None)`, et **sans `user` elle
crée un superutilisateur**, qui passe toutes les permissions et masque donc exactement ce que le
test doit prouver.

```python
@pytest.mark.django_db
def test_<route>_autre_proprietaire_est_refuse(api_client, user, case_factory):
    autre = case_factory()                      # appartient à quelqu'un d'autre
    client = api_client(router, user=user)      # utilisateur sans view_all / view_team

    response = client.get(f"/…/?case_pk={autre.pk}")

    assert response.status_code in (403, 404)   # jamais 200 avec les données d'autrui
```

Ajouter systématiquement le happy-path : le propriétaire accède bien à sa donnée.

**Piège de données de test** : quand le service se ramifie selon la forme des données, tester la
branche que prennent les données de production, pas celle qui est commode à construire. Un jeu de
test trop favorable a déjà laissé passer une 500 sur la majorité des produits réels.

## 5. Validation

Voir la skill **omeo-validation**. Ne pas recopier de commandes ici : celles de `CLAUDE.md`
divergent de la CI.

## 6. Revue

Relire le diff contre les points 0 à 4. Un humain valide le merge.
