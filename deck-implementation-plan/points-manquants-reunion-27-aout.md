# Points Manquants — Réunion 27 août 2026

Document synthétisant les **points de discussion et décisions** de la réunion du 27 août (avec Antonin, Cédric, Juan, Bilal, Fadwa, Laurent) qui **ne sont pas couverts** dans le document `points-a-trancher.md`.

**Note** : Ce document n'est pas exhaustif mais énumère les lacunes principales identifiées lors de l'analyse.

---

## 1. Problème de cardinalité sur Comments/Documentation

**Situation** : 
- En **SysML v2/KerML**, un `Comment` peut être lié à **plusieurs éléments** à la fois (ex. : `about ItemA, PartB`)
- En **Modelio**, une `Note` est **toujours contenue dans un seul élément** (composition 1..1)

**Conséquence** : 
- Ce n'est pas une simple différence terminologique, c'est une **différence structurelle profonde**
- Un utilisateur ne peut pas modéliser un commentaire attaché à 2 choses en même temps (il faut dupliquer ou trouver une workaround)

**Statut dans points-a-trancher.md** : Mentionné en partie (point 3, achoppement 1), mais pas mis en avant comme un **blocage potentiel** d'implémentation.

**À décider** : 
- Comment on représente cette multiplicité en Modelio ? (duplication des comments ? relation n-aire à part ?)
- Quel impact sur l'éditeur graphique et l'UX ?

---

## 2. Propriété `locale` sur Comments/Documentation

**Situation** : 
- En SysML v2, les `Comment` et `Documentation` peuvent porter une propriété `locale` pour l'**internationalisation** (ex. : `locale = "fr"`)
- En Modelio, les Notes n'ont pas nativement ce concept

**Conséquence** : 
- Il faut étendre la Note Modelio pour porter cet attribut
- Ou accepter de perdre cette fonctionnalité d'internationalisation au premier cycle

**Statut dans points-a-trancher.md** : Pas mentionné.

**À décider** : 
- Support de `locale` dès le départ, ou repoussé ?
- Si supporté, où/comment le stocker ?

---

## 3. Décision architecturale : Accepter les adaptations (pas 100% de fidélité)

**Énoncé par Antonin** (minute 21:25+) : 

> « On ne vise pas du 100% implémentation du Métamodèle SysML pour ces concepts-là qui sont de très haut niveau. On se permet de les rattacher aux concepts métier dans Modelio. »

> « Si le besoin métier est bien couvert par ce qui existe dans le Modelio, le concept sort du Métamodèle SysML et on garde celui de Modelio. »

**Implication majeure** : 
- C'est un **principe de décision** explicite : si `MetadataDefinition` de SysML v2 ≈ `Stereotype + PropertyTable` de Modelio, **on utilise Modelio et on sort SysML du métamodèle `implementation`**
- Cela signifie que le **code généré ne sera pas 100% conforme à la spec SysML v2**, mais **fonctionnellement équivalent**

**Statut dans points-a-trancher.md** : Implicite (point 3, principe du mapping), mais **pas énoncé clairement comme une décision acceptée**.

**À formaliser** : 
- Ajouter explicitement dans la spec que "conformité à 100% n'est pas un objectif"
- Documenter les compromis acceptés avec justification métier

---

## 4. Problème de mapping texte ↔ modèle

**Énoncé par Antonin** (minute 23:30+) : 

> « À partir du moment où on fait une adaptation et qu'on ne supporte pas le métamodèle SysML tel qu'il existe de base, il ne va pas y avoir de mapping direct entre le langage écrit et la représentation du modèle qu'on a dans Modelio. »

**Conséquence** : 
- Si on mapping `MetadataDefinition` → `Stereotype`, la syntaxe textuelle SysML v2 qui dit "metadata" doit être **traduite/interprétée** en "stereotype" pour être stockée/lue
- Il faut un **traducteur/parser** entre les deux représentations
- **Les noms changent** : ce qui s'appelle "metadata" à l'écrit s'appelle "stereotype" en modèle

**Statut dans points-a-trancher.md** : Pas mentionné.

**À anticiper** : 
- Comment le moteur de parsing SysML v2 textuel gère-t-il ces mappings ?
- Qui implémente ce traducteur ?
- Documentation du mapping concept-to-concept pour l'équipe de parsing

---

## 5. Limitation SemGen : bloque sur héritage multiple

**Énoncé par Cédric Marin** (minute 28:02+) : 

> « Si SemGen voit qu'il y a un héritage multiple de base, je crois qu'il bloque. »

**Impact** : 
- Le script `reference` → `implementation` (point 6 dans points-a-trancher.md) qui doit appliquer les 34 résolutions d'héritage multiple **ne pourra pas fonctionner si on essaie de créer des classes avec 2 super-types** (même pas à titre intermédiaire)
- Il faut mettre en place le pattern Delegation **dans le modèle directement**, avant de le passer à SemGen

**Statut dans points-a-trancher.md** : Le pattern Delegation est proposé (point 4 & 5), mais **pas clair que c'est une contrainte de SemGen, pas un choix de design**.

**À clarifier** : 
- Le script de transformation doit générer des classes avec `implements` seulement (pas `extends` double)
- Ou il faut contribuer à SemGen pour le rendre capable de gérer l'héritage multiple

---

## 6. Proposition : Contribution à SemGen pour automatiser l'héritage multiple

**Énoncé par Juan Cadavid** (minute 29:37+) : 

> « Moi je serai ravi de contribuer à SemGen parce que je pense que c'est un outil très puissant [...] on pourrait faire évoluer SemGen pour le traiter automatiquement. »

**Réponse d'Antonin** : 

> « Sachant que Cédric a raison, on pourrait faire évoluer SemGen éventuellement pour le traiter automatiquement. Mais est-ce que c'est pertinent de le faire ? »

**Implication** : 
- Contribuer à SemGen pour que le pattern Delegation soit appliqué automatiquement (plutôt que 34 cas à la main) serait une **amélioration à long terme**
- Mais ce n'est pas décidé aujourd'hui

**Statut dans points-a-trancher.md** : Pas mentionné.

**À décider** : 
- Y consacrer du temps pour la contribution SemGen, ou faire les 34 cas manuellement ?
- Quel coût/bénéfice ?

---

## 7. Documentation Fadwa sur SemGen existe et nécessite révision

**Énoncé par Juan** (minute 29:37+) : 

> « Fadwa elle a fait une super documentation qu'après elle peut nous présenter [...] Cédric, elle t'a demandé si tu pouvais valider un peu la documentation qu'elle a fait. »

**Réponse de Cédric** : 

> « Ah oui, j'ai passé ça, j'ai eu 12 »  [probablement : "j'ai eu du mal à vérifier"]

**Implication** : 
- Il y a une documentation interne sur SemGen rédigée par Fadwa
- Elle nécessite une **validation/révision par Cédric Marin** (expert SemGen)
- Cette documentation sera cruciale pour la phase d'implémentation

**Statut dans points-a-trancher.md** : Pas mentionné.

**À faire** : 
- Récupérer la doc Fadwa sur SemGen
- Terminer la validation par Cédric
- L'intégrer dans la spec globale

---

## 8. Format de livrable : Document de spec plutôt que tickets Jira

**Énoncé par Antonin** (minute 3:58+) : 

> « Un document de spec en tout cas, oui. Je suis pas sûr que passer par des fichiers Jira ce soit utile parce que c'est chiant à manipuler. Plutôt il nous faut un document de spec basé sur ça, oui on est d'accord. »

**Conséquence** : 
- Plutôt que créer 200 tickets Jira pour chaque aspect, **faire un document de spec unifié et exécutable**
- Ce document deviendra la **source de vérité** pour l'implémentation

**Statut dans points-a-trancher.md** : Pas mentionné.

**À organiser** : 
- Qui rédige la spec complète ?
- Quel template/structure ?
- Comment la maintenir à jour pendant l'implémentation ?

---

## 9. Besoin d'exemples concrets pour chaque concept complexe

**Énoncé par Bilal Said** (minute 34:44+) : 

> « Sur chaque point rien que là jusque là dans 23 slides tu as évoqué plein plein de concepts et je pense qu'y a qu'y a moyen de faire de la réflexion sur chacun. Pourquoi ils ont fait ça de cette manière-là ? Est-ce qu'ils auraient pu faire autrement ? Faut se donner des exemples à chaque fois [...] »

**Exemple donné** : Le concept `subset` — Bilal cite l'exemple métier **équipe/joueurs/capitaine** : un capitaine est un joueur particulier de l'équipe, à une époque donnée, ce qui crée une relation `subset` entre `capitaineship` et `membership`.

**Implication** : 
- Chaque concept complexe (subset, redefinition, etc.) doit avoir des **exemples métier concrets** pour être compris
- Pas assez de lire la spec formelle, il faut comprendre **pourquoi** ça a été conçu ainsi
- Ça aide à vérifier si on a bien supporté les cas d'usage

**Statut dans points-a-trancher.md** : Pas mentionné.

**À mettre en place** : 
- Ajouter des exemples métier (SysML v2 ou du domaine ingénierie système) pour chaque concept clé
- Chaque exemple doit montrer comment on le représente dans Modelio

---

## 10. Problème UX/IHM : Users cherchent "metadata" pas "property table"

**Énoncé par Fadwa** (minute 33:48+) : 

> « Moi j'ai juste un petit appréhension. Enfin c'est bien de réutiliser tout ce qu'on a mais l'utilisateur il va être un peu perdu parce que il va chercher metadata, il va pas penser à property table tu vois, il veut créer un metadata, ça serait bien que ça soit la même metadata. »

**Implication** : 
- Si on mappe `MetadataUsage` → `PropertyTable`, l'utilisateur Modelio cherchera "metadata" dans l'interface, pas "property table"
- Il faut une **vue/dialogue IHM dédiée** qui parle le langage SysML v2 même si en arrière-plan on utilise les PropertyTable de Modelio

**Réponse d'Antonin** : 

> « C'est des cas où si on considère que la fonctionnalité est déjà couverte par Modelio [...] Soit en terme DIHm, on peut renommer quelques IHM quand on est en conformité. »

**Statut dans points-a-trancher.md** : Pas mentionné.

**À designer** : 
- Créer une vue IHM spécifique pour la création/édition de métadonnées en langage SysML v2
- Ou adapter les dialogues existants (PropertyTable) pour parler le langage métier

---

## 11. Possibilité de renommer/adapter les concepts dans l'IHM après implémentation

**Énoncé par Cédric Marin & Antonin** (minute 34:08+) : 

> **Cédric** : « Ah bah si tu si tu fais une interface spécifique système après tu fais ce que tu veux dans. »
> 
> **Juan** : « On peut avoir développé une vue de propriété spécifique si jamais le truc change et que du coup on va appeler ça c'est tout. »

**Implication** : 
- L'implémentation interne peut réutiliser PropertyTable de Modelio
- Mais on peut créer une **vue/interface dédiée** qui présente ça sous le nom "Metadata" ou autre terme SysML v2
- Cela permet de réutiliser sans "trahir" l'UX

**Statut dans points-a-trancher.md** : Pas mentionné.

**À anticiper** : 
- Budget IHM pour créer des vues spécifiques SysML v2
- Mapping entre termes SysML v2 et termes Modelio dans l'IHM

---

## 12. Syntaxe n-aire non supportée pour Dependency dans Modelio

**Énoncé par Antonin** (minute 7:37+) : 

> « Tu traduis par 2 dépendances chez nous. Faut voir ça comme ça. »

**Contexte** : 
- SysML v2 permet : `dependency X to Y, Z;` (un client, plusieurs fournisseurs)
- Modelio ne supporte que des liens binaires
- **Solution** : décomposer en 2 dépendances : `X->Y` et `X->Z`

**Conséquence** : 
- La **syntaxe textuelle** doit supporter la notation `X to Y, Z` et la transformer en dépendances binaires
- **Cédric** précise (minute 7:25+) : « On n'a pas. On a sabré. Simplifier ? »
- = Modelio n'a pas la syntaxe complète n-aire, juste binaire

**Statut dans points-a-trancher.md** : Mentionné (point 3, achoppement 2), mais pas très explicite sur **le parsing textuel**.

**À clarifier** : 
- Qui implémente le parser qui transforme n-aire → binaire ?
- La transformation est-elle réversible (bidirectionnelle) pour le roundtrip ?

---

## 13. Feedback de Bilal : Nécessité d'avancer prudemment avec des exemples

**Énoncé par Bilal Said** (minute 32:16+) : 

> « J'ai plein de questions qui tournent dans ma tête effectivement, mais j'attends que ça avance aussi. C'est bien de réutiliser un maximum. Si de mon côté [...] on arrive à supporter quand même un maximum de concepts, de leur richesse, de leur vraie sémantique côté SML, ça me facilitera la tâche [...] parce que je pourrais éventuellement réutiliser certains des parsers. »

**Implication** : 
- L'équipe de parsing SysML v2 textuel (dont Bilal) dépend des décisions Modelio
- Il faut que le **mapping concept-to-concept** soit clair et stable
- Chaque adaptation qui sort du métamodèle SysML rend le parsing plus compliqué

**Statut dans points-a-trancher.md** : Pas mentionné.

**À organiser** : 
- **Communication régulière** entre l'équipe Modelio et l'équipe parsing
- Documenter le mapping pour que le parsing puisse faire les bonnes traductions
- Ne pas faire de surprises architecturales après coup

---

## 14. Chronologie et dépendance des travaux

**Énoncé par Juan Cadavid** (minute 30:01+) : 

> « Je vais prendre note de tout ce qu'on a décidé aujourd'hui et on peut continuer à après je vais voir notre dispo pour demain pour la semaine prochaine. Mais oui il y a des décisions qui va prendre pour pouvoir continuer puis ne pas se louper. »

**Implication** : 
- Il y a des **points de synchronisation** critiques
- Certaines décisions bloquent d'autres travaux
- Le calendrier pour décembre est serré

**À organiser** : 
- Créer un **diagramme de dépendances** entre les tâches
- Identifier les **points de synchronisation** avec l'équipe parsing (Bilal)
- Planifier les **réunions de review** des décisions

---

## 15. Feedback supplémentaire : Documenter les difficultés et les mappings non-évidents

**Énoncé par Bilal Said** (minute 38:55+) : 

> « Toute difficulté d'ailleurs. Oui, juste une petite toute dernière remarque : toute difficulté, toute décision qui n'est pas évidente, straightforward, facile. Tout mapping qui n'était compliqué, qui n'était pas facile à faire, et cetera. C'est super. »

**Implication** : 
- Documenter **les choix difficiles** et pourquoi on a choisi cette solution
- Rendre visible **les compromis acceptés**
- Cela aidera le parsing et les outils ultérieurs à comprendre les intentions

**Statut dans points-a-trancher.md** : Partiellement (explications pour les chevauchements), mais pas systématique.

**À formalize** : 
- Ajouter une section "Difficultés et justifications" pour chaque point de mapping
- Ex. : "Pourquoi nous avons choisi PropertyTable plutôt que TaggedValue ?"

---

## Résumé des lacunes principales

| # | Lacune | Priorité | Impact |
|---|---|---|---|
| 1 | Cardinalité multiple sur Comments (A, B) vs Note (1) | Haute | Bloquant pour la modélisation |
| 2 | Propriété `locale` sur Comments | Moyenne | Feature supplémentaire |
| 3 | Décision : accepter adaptations (pas 100% fidèle) | **CRITIQUE** | Architectural |
| 4 | Mapping texte ↔ modèle & traducteur | Haute | Dépend le parsing |
| 5 | Limitation SemGen sur héritage multiple | Haute | Bloquant pour génération code |
| 6 | Contribution à SemGen pour automatiser | Moyenne | Nice-to-have, optimisation |
| 7 | Documentation Fadwa sur SemGen (révision) | Moyenne | Information critique |
| 8 | Format spec document (pas Jira) | Média | Processus projet |
| 9 | Exemples métier concrets pour chaque concept | Moyenne | Compréhension & validation |
| 10 | UX/IHM : metadata vs property table | Moyenne | User experience |
| 11 | Adapter IHM avec termes SysML v2 | Média | User experience |
| 12 | Parsing n-aire → binaire pour Dependency | Moyenne | Parsing textuel |
| 13 | Communication Modelio ↔ Parsing | **CRITIQUE** | Synchronisation travaux |
| 14 | Diagramme dépendances tâches & synchro | Média | Planification projet |
| 15 | Documenter difficultés & compromis | Média | Clarté architecturale |

---

## Prochaines étapes recommandées

1. ✅ **Valider la décision CRITIQUE** : "Accepter les adaptations, pas 100% fidélité" → formaliser explicitement
2. ✅ **Résoudre les problèmes de cardinalité** : comment supporter comments multi-éléments en Modelio ?
3. ✅ **Organiser communication Modelio ↔ Parsing** : réunions hebdomadaires ou documents partagés ?
4. ✅ **Terminer révision doc Fadwa** sur SemGen
5. ✅ **Créer exemples métier** pour chaque concept clé (responsable : ?)
6. ✅ **Valider le mapping concept-to-concept** avec Bilal & équipe parsing
7. ✅ **Planifier contribution à SemGen** ou accepter les 34 cas manuels
8. ✅ **Designer l'IHM SysML v2** pour les cas de mapping (metadata, etc.)

