---
name: external-integration
description: >
  Procédure et runbook pour ajouter ou modifier une intégration externe du CRM Omeo (Yousign,
  Enedis, PVGIS, banques/prêts, géocodage). À utiliser sur tout diff dans sign/backends.py,
  case/enedis/, case/pvgis/, case/loan/banks/, ou un appel à une API tierce.
---

# Intégrer ou modifier une API externe

Les intégrations cassent quand l'API tierce change ou tombe. Le code existant a des faiblesses
connues (pas de retry, `print` au lieu de log, token sans expiration). Applique ces standards.

## Intégrations existantes (points de vigilance)

| Intégration | Fichier | Vigilance connue |
|-------------|---------|------------------|
| Yousign (signature) | `sign/backends.py` | `print()` au lieu de log ; pas de retry ; pas de validation de taille de fichier |
| Enedis (conso) | `case/enedis/backends.py` | token caché sans gestion d'expiration ; format de date non validé |
| PVGIS (solaire) | `case/pvgis/backends.py` | API publique sans clé (rate-limit) ; pertes (`loss`) en dur |
| Prêts | `case/loan/banks/projexio.py`, BNP | taux/assurances en dur, non datés |
| Géocodage | `crm/services.py` (geopy/Nominatim) | rate limiter à respecter ; flag `untraceable` jamais re-essayé |

## Standards à appliquer

1. **Logging, pas `print`** : utiliser le logger Django / Sentry, jamais `print()` (perdu en prod).
2. **Timeout explicite** sur chaque requête HTTP.
3. **Gestion d'erreur typée** : lever une exception de domaine dédiée (pas un `Exception` générique),
   pour que l'appelant distingue erreur réseau / erreur métier / indisponibilité.
4. **Token/auth** : tracer l'expiration, ré-authentifier si 401 ; ne pas supposer un token éternel.
5. **Validation des entrées** envoyées à l'API (format de date, taille de fichier, bornes lat/lon).
6. **Secrets** : via variables d'environnement uniquement (jamais en dur), documentés dans `SETUP.md`.
7. **Taux/valeurs externes** : si en dur, les dater et prévoir leur mise à jour ; idéalement config.
8. **Webhook entrant** (ex. Yousign) : vérifier la signature/authenticité de la requête.

## Procédure

1. Logique d'appel dans un `backends.py`/service dédié ; l'API/le service Omeo reste fin.
2. Appliquer les 8 standards ci-dessus.
3. Tester avec l'API tierce **mockée** (jamais d'appel réseau réel en test).
4. Mettre à jour/écrire le runbook de l'intégration (agent conventions-doc).
5. Validation + revue **security-permissions** (secrets, webhook) et **backend-metier** (si calcul,
   ex. prêts) via **/omeo-review**. Un humain valide.
