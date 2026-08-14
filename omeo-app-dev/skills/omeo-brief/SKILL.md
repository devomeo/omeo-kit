---
name: omeo-brief
description: >
  Analyser un brief avant d'écrire la moindre ligne, pour séparer ce qui est décidable en lisant
  le code de ce qui exige un arbitrage humain. À utiliser à la réception d'un brief, d'une carte
  Notion, d'une liste de modifications, ou de toute demande de plus d'un fichier sur le CRM Omeo.
---

# Analyser un brief avant d'écrire

Un brief contient toujours des points qu'aucune lecture du code ne peut trancher. Les découvrir
au jour 6 coûte des allers-retours ; les poser au jour 1 ne coûte rien.

## Deux erreurs symétriques

**Décider seul ce que seul un humain peut trancher** produit du travail plausible et faux — le
pire type d'erreur, parce qu'il se relit bien.

**Demander ce que le code répond déjà** fait perdre du temps à l'humain et signale qu'on n'a pas
cherché. Sur ce projet, la question « le calcul va-t-il en template ou en back ? » avait l'air
d'un arbitrage : la version précédente y répondait, en template, depuis toujours. Elle n'aurait
jamais dû être posée — elle aurait dû être lue.

La valeur de cette analyse tient à la netteté de la frontière, pas au nombre de questions.

## Étape 1 — vérifier les affirmations factuelles du brief

**Un brief peut se tromper sur l'application.** Ce n'est ni rare ni grave, mais agir dessus l'est.

Cas réels : « cette valeur vient de la step CEE » — elle venait de la step Aides. « Dans la step
solution choisie » — il s'agissait de la step Solutions. Une feature décrite comme existante
s'est révélée ne pas exister du tout.

Pour chaque affirmation du brief portant sur le code — un nom d'étape, un champ, un mécanisme
supposé exister — la vérifier avant d'en tirer quoi que ce soit. Une affirmation fausse
confirmée tôt est une information utile, pas un reproche.

## Étape 2 — trancher ce qui est décidable, en lisant

À résoudre par la lecture, **jamais** en posant la question :

- comment la dernière version active traite le même besoin (précondition n°1, voir la skill
  `omeo-preconditions`) ;
- si un mécanisme existe déjà — chercher avant de conclure qu'il faut le créer ;
- si une donnée est disponible à l'étape visée, et depuis quand elle est renseignée ;
- ce qu'une `pdf_version` lit réellement ;
- les noms de champs, l'ordre des étapes, les sources de données.

## Étape 3 — isoler ce qui exige un arbitrage

Un point n'est pas décidable dès qu'il relève d'une de ces catégories :

**Un chiffre du brief contredit le code.** Lequel fait foi ? Exemple vécu : le brief annonçait
« ~17 % du prix matériel », le code applique `× 1.27` sur le matériel **posé**. Deux écarts en
un — le coefficient et l'assiette — et aucune lecture ne dit lequel est juste.

**Le périmètre.** Une demande peut ne pas relever de la tâche. Une feature du brief V9 s'est
révélée ne pas être à traiter du tout après question au senior.

**Un placement défendable de plusieurs façons.** Un bloc demandé sur un écran où la donnée
nécessaire n'existe pas encore : la contrainte technique se lit, mais le choix entre déplacer le
bloc, changer sa source ou l'abandonner est un choix produit.

**Une valeur réglementaire.** Seuil de prime, taux, barème : source officielle et date d'effet
exigées, jamais d'invention.

**La portée entre versions.** Le changement vaut-il pour la version cible seulement, ou aussi
pour les versions actives ? Toucher à une version active a des conséquences en production ; la
réponse n'est pas dans le code.

**Deux consignes du projet qui se contredisent.** Les signaler, ne pas arbitrer seul.

## Étape 4 — livrer la sortie

Une liste courte. Pour chaque point :

- la question, formulée de façon à pouvoir être tranchée par oui/non ou par un choix ;
- ce qui a été tenté pour la résoudre sans humain, et pourquoi ça ne suffit pas ;
- une recommandation quand elle existe — un arbitrage est plus rapide qu'une question ouverte ;
- ce que ça bloque, et ce que ça ne bloque pas.

## Étape 5 — ne pas attendre la réponse

**Une question n'est bloquante que si aucune interprétation ne permet d'avancer sans risque.**

Faire d'abord tout ce qui n'en dépend pas. Pour le reste, énoncer l'hypothèse retenue et
continuer, en la signalant. Réserver l'arrêt complet aux cas où se tromper rendrait le travail
inutilisable ou dangereux.

## Contrôle final

Si l'analyse ne produit **aucune** question sur un brief de plus de deux ou trois modifications,
c'est probablement qu'elle n'a pas été faite : relire en cherchant les chiffres, les périmètres
et les placements. Si elle en produit plus de cinq, plusieurs sont sans doute décidables par
lecture — les reprendre.
