---
name: add-secure-endpoint
description: >
  Procédure pas-à-pas pour ajouter ou modifier un endpoint API Ninja sur le CRM Omeo SANS créer
  de fuite de données entre utilisateurs. À utiliser dès qu'on crée/édite une route dans un
  fichier api.py exposant des données métier (Case, Contract, Contact, Cart, Repair, Bilan…).
---

# Ajouter un endpoint API isolé et testé

Le risque n°1 du projet est l'accès aux données d'un autre utilisateur. Suis ces étapes dans
l'ordre des couches (`schemas → services → api → tests`). Ne saute aucune étape.

## 1. Schéma (`schemas.py`)
Définir le schéma d'entrée (FilterSchema/Schema Ninja) et de sortie. Centraliser la validation ici.

## 2. Service (`services.py`) — c'est ici que se joue la sécurité
- La logique vit dans le service, jamais dans `api.py`.
- **Filtrer par propriétaire** : pour une liste, partir de `Model.objects.filter(owner=user)`.
- **Élargir à l'équipe UNIQUEMENT derrière une permission** : n'ajouter `owner__teams__name__in`
  que si `user.has_perm("<app>.view_team_<model>")`. Référence à copier : `case/services.py::get_cases`.
- **Accès par PK** : un `get_*_by_pk` qui ne re-vérifie pas la propriété NE DOIT PAS être exposé
  tel quel à un endpoint sans contrôle. Soit le service prend `user` et filtre, soit l'endpoint
  vérifie la propriété avant de retourner.

## 3. API (`api.py`)
- Handler fin : valider via schéma → appeler le service → retourner.
- **`@has_perm(["<app>.<codename>"])` obligatoire** sur tout endpoint de données. Choisir le bon
  codename selon l'action (`view_`, `add_`, `change_`, `delete_`, ou une permission custom).
- ⚠️ `has_perm` ne contrôle QUE le niveau modèle. Il NE remplace PAS le filtrage `owner`/`team`
  du service. Les deux sont nécessaires.
- `url_name="..."` obligatoire. IDs en query params (sauf exception assumée).

## 4. Test d'isolation (`tests/<app>/`) — OBLIGATOIRE, non négociable
En test l'auth est désactivée : utiliser `api_client_factory(user=<non-superuser>)`.
```python
def test_<endpoint>_other_owner_is_denied(api_client_factory, user, <model>_factory):
    other = <model>_factory()                 # appartient à un autre propriétaire
    client = api_client_factory(user=user)    # user sans view_all/view_team
    resp = client.get(f"/api/.../{other.pk}/")
    assert resp.status_code in (403, 404)     # jamais 200 avec les données d'autrui
```
Ajouter aussi un happy-path (le propriétaire accède bien à sa donnée).

## 5. Validation finale
```
set -a && source .env-test && set +a && pytest
mypy src/ && flake8 && black --check . && isort --check-only .
```

## 6. Revue
Lancer l'agent **security-permissions** puis **/omeo-review** avant la PR. Un humain valide le merge.
