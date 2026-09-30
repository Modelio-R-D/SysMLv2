---
marp: true
theme: docaposte
paginate: true
---

<!-- _class: title -->

# Stockage et surface d'API du métamodèle SysML v2

## ARCHIVE HISTORIQUE · Instantané du 22 septembre 2026

Juan Cadavid · 22 septembre 2026 · archivé le 26 septembre 2026

---

# Trois réserves de relecture, toutes corrigées en direct

<div class="two-col">
<div>

## Ce qui était reproché

1. **`{structural.node}` sur toutes les métaclasses** — chaque élément de modèle dans son propre fichier
2. **`KerMLModelElement`** redéfinit `Name`, porte `elementId` en plus de l'UUID natif
3. **Stockage dupliqué** — `SmDependency ownedElementDep` **et** `ownedRelationshipDep`

</div>
<div>

## Ce qui a été fait

1. Liste blanche de **28 grains** de persistance au lieu de 163
2. Les deux attributs dupliqués **supprimés**, mapping natif documenté
3. Stockage canonique unique, l'union devient **dérivée**

</div>
</div>

<div class="takeaway">Les trois points sont fermés, vérifiés sur le modèle live, et rejoués dans les scripts de transformation pour survivre à une régénération complète.</div>

---

<!-- _class: "section theme-mint" -->

# La décision de conception

## Où stocker les collections

---

# Décision : stocker sur la métaclasse la plus haute qui définit la collection

<div class="two-col">
<div>

## Le patron de la norme

KerML multiplie les unions dérivées et leurs sous-ensembles concrets :

```
Element
  /ownedElement      (union dérivée)
  ownedRelationship  (subsets, stocké)

Type
  /ownedSpecialization
Namespace
  /ownedMember
```

Recopié tel quel, **chaque niveau stocke la même chose**.

</div>
<div>

## La règle retenue

<div class="box">
La collection est <strong>stockée une seule fois</strong>, sur la métaclasse la plus abstraite qui la définit.
</div>

<div class="box m">
Les vues spécialisées (unions, sous-ensembles, redéfinitions) sont <strong>dérivées</strong> : elles filtrent le contenu hérité, sans stockage propre.
</div>

<div class="box y">
Les filles ne redéclarent jamais un stockage pour un contenu que le parent porte déjà.
</div>

</div>
</div>

<div class="takeaway">Une seule source de vérité par collection. Pas de synchronisation à maintenir, pas de double comptage en mémoire ni en persistance.</div>

---

# Traduction concrète dans Modelio

<div class="two-col">
<div>

## Ce que Modelio sait exprimer

| Concept UML | Modelio |
|---|---|
| `isDerived` | ✅ `AssociationEnd.setIsDerived()` |
| `isDerivedUnion` | ❌ absent |
| `subsettedProperty` | ❌ absent |
| `redefinedProperty` | ❌ absent |

Pour une **union/sous-ensemble**, le drapeau `isDerived` suffit — c'est le cas traité ci-dessus.

Pour une **redéfinition restrictive** (type, multiplicité), `isDerived` ne dit rien : problème distinct, détaillé plus loin.

</div>
<div>

## L'effet sur la génération

<div class="box">
<strong>Rôle non dérivé</strong> → champ physique dans <code>XData</code>, <code>SmDependency</code> enregistrée, persistance réelle.
</div>

<div class="box m">
<strong>Rôle dérivé</strong> → aucun champ, aucune <code>SmDependency</code>, accesseur calculé uniquement.
</div>

</div>
</div>

<div class="takeaway">Conserver fidèlement le <code>isDerived</code> normatif suffit pour les unions et sous-ensembles — pas pour les redéfinitions restrictives, qui restent un problème ouvert.</div>

---

# Résultat mesuré sur `KerMLModelElement`

<div class="two-col">
<div>

## Avant

```java
SmDependency ownedElementDep;
SmDependency ownedRelationshipDep;
```

Deux dépendances stockées pour le même contenu — l'exemple exact cité en relecture.

</div>
<div>

## Après

```
KerMLModelElementData
  mOwnedRelationship   ← stocké
  (pas de mOwnedElement)
```

`ownedElement` est dérivé : getter calculé, **zéro stockage**.

</div>
</div>

<div class="stat-box"><span class="number">291</span><span class="label">rôles repassés en dérivé sur 548 appariés sans ambiguïté</span></div>

---

# Effet de bord bienvenu : la génération est deux fois plus rapide

<div class="two-col">
<div>

## Temps de génération KerML

| Run | Durée |
|---|---|
| Avant correctifs | 21 min 37 s |
| Après correctifs | **11 min 30 s** |

81 métaclasses, `GENERATION SUCCESSFUL` dans les deux cas.

</div>
<div>

## Pourquoi

<div class="box">
123 des 250 rôles KerML sont désormais dérivés.
</div>

<div class="box m">
Chacun n'émet plus ni champ <code>Data</code>, ni classe <code>SmDependency</code>, ni code de chargement.
</div>

</div>
</div>

<div class="takeaway">La règle de stockage ne sert pas qu'à la propreté du modèle : elle réduit de moitié le coût de chaque cycle de génération.</div>

---

<!-- _class: dense -->

# Sur le volume de getters/setters : les chiffres réels

| Mesure | Valeur | Lecture |
|---|---|---|
| Classes générées | 1 728 | dont seulement 171 sont l'API réelle |
| Interfaces `mm.api` | 171 | une par métaclasse |
| Opérations d'API | 1 355 | ~8 par métaclasse |
| Opérations d'implémentation | 2 209 | inclut l'aplatissement des parents secondaires |
| Getters (toutes classes) | 5 293 | |
| **Setters (toutes classes)** | **1 195** | 4,4× moins que les getters |
| Classes `SmDependency` | 767 | plomberie Modelio, pas notre API |
| Classes `SmAttribute` | 94 | idem |

<div class="takeaway">L'essentiel du volume n'est pas notre API mais la machinerie interne Modelio (<code>Data</code>, <code>SmClass</code>, <code>SmDependency</code>) que tout métamodèle génère. Sur 1 728 classes, 171 seulement sont exposées.</div>

---

# Pourquoi il y a peu de setters, contrairement à l'impression initiale

<div class="two-col">
<div>

## Règles effectives de SemGen

- Rôle **multiple** → getter + getter filtré, **aucun setter**
- Rôle **simple** → getter + setter
- Rôle **dérivé** → accesseur calculé, pas de stockage

</div>
<div>

## Vérifié sur le modèle généré

```
KerMLModelElement
  getOwnedElement()
  getOwnedRelationship()
```

<div class="box m">
Aucun <code>setOwnedElement()</code>, aucun <code>setOwnedRelationship()</code>.
</div>

</div>
</div>

<div class="takeaway">Les collections ne sont jamais remplacées en bloc : elles se manipulent par la liste vivante retournée par le getter — convention Modelio native.</div>

---

<!-- _class: "section theme-poussin" -->

# Un problème distinct, non résolu

## Les redéfinitions restrictives (`redefines`)

---

# Redéfinir, ce n'est pas dériver

<div class="two-col">
<div>

## Ce qu'on vient de voir

Union dérivée + sous-ensemble stocké : **même contenu, deux vues**.

`isDerived` suffit — Modelio sait l'exprimer nativement.

</div>
<div>

## Un autre cas, dans la même norme

Une **redéfinition** restreint le **type ou la multiplicité** d'une propriété héritée, en gardant la **même identité de stockage**.

```
Relationship
  target : KerMLModelElement [0..*]

Specialization :> Relationship
  general : Type [1..1]  {redefines target}
```

`general` n'ajoute pas de contenu : il **restreint** `target`.

</div>
</div>

<div class="takeaway">Un même mécanisme normatif, deux besoins de génération opposés — dériver un filtre n'est pas restreindre un contrat.</div>

---

# Pourquoi le stockage partagé ne suffit pas

<div class="two-col">
<div>

## Ce qu'on veut

<div class="box">
**Un seul champ physique** partagé entre `target` et `general` — pas de doublon, pas de désynchronisation.
</div>

</div>
<div>

## Ce que ça casse si on s'arrête là

<div class="box y">
Rien n'empêche d'écrire, via <strong>l'accesseur hérité non restreint</strong>, une valeur qui viole la contrainte du côté restreint.
</div>

<div class="box m">
Exemple réel du modèle : <code>Membership.memberElement</code> restreint <code>Relationship.target</code> — n'importe quel code touchant <code>target</code> directement contourne la restriction de <code>memberElement</code>.
</div>

</div>
</div>

<div class="takeaway">Partager le stockage est nécessaire mais pas suffisant : il faut aussi empêcher l'écriture par le mauvais accesseur.</div>

---

# Le risque concret : l'écriture par le mauvais bout

<div class="two-col">
<div>

## Le piège

Une association a **deux extrémités**. Valider seulement le côté restreint ne protège pas contre une écriture depuis l'**extrémité opposée**.

</div>
<div>

## Illustration

```
CommandeProfessionnelle.client
  redefines Commande.client
  : ClientProfessionnel [1..1]
```

Un `Client` ordinaire peut encore faire :

```
client.commandes.add(commandeProfessionnelle)
```

— ce qui viole la contrainte, **sans jamais appeler le setter restreint**.

</div>
</div>

<div class="takeaway">La validation doit s'exécuter avant toute mutation touchant la propriété, quel que soit le sens d'où elle vient — pas seulement au niveau du setter généré.</div>

---

<!-- _class: dense -->

# Ce n'est pas un cas rare — mesuré sur `reference/design`

| Mesure | Valeur |
|---|---|
| Extrémités d'association dans `reference/design` | 556 |
| Redéfinitions déclarées (note normative XMI) résolues | 90 |
| **Dont restrictives** (type, multiplicité, agrégation ou dérivation différents) | **79** |
| Partageables telles quelles (même forme des deux côtés) | 11 |

<div class="stat-box"><span class="number">79/90</span><span class="label">redéfinitions réelles sont restrictives — pas l'exception, la norme</span></div>

<div class="takeaway">Le patron <code>Relationship.source/target</code> → concret (<code>Specialization</code>, <code>Membership</code>, <code>Subsetting</code>, <code>FeatureTyping</code>, <code>Association</code>, <code>Connector</code>…) est la façon dont KerML modélise ses propres relations. Ce n'est pas un détail d'implémentation, c'est le squelette du métamodèle.</div>

---

# Ce que Modelio ne donne pas gratuitement

<div class="two-col">
<div>

## Rappel de la contrainte outillage

`redefinedProperty` est **absent** de l'API Modelio (cf. tableau plus tôt). La seule trace disponible est une **note texte** libre sur chaque propriété.

</div>
<div>

## Conséquence

<div class="box y">
Cette note doit être <strong>interprétée par du code</strong> pour retrouver la propriété canonique — et elle peut être <strong>obsolète</strong> : 2 notes trouvées référencent encore <code>Element</code>, renommé en <code>KerMLModelElement</code> il y a plusieurs semaines.
</div>

</div>
</div>

<div class="takeaway">Le pont entre la norme et Modelio est un texte libre, pas un lien natif vérifié par l'outil — chaque évolution du modèle peut le rendre silencieusement faux.</div>

---

# Où en est le correctif

<div class="two-col">
<div>

## Fait et testé

<div class="box">
Résolution du stockage canonique à partir des notes — ambiguïtés, cycles et incohérences de type/multiplicité rejetés plutôt qu'ignorés.
</div>

<div class="box m">
Contrôleur de mutation, vue à collection contrainte, générateur de code d'interception — chacun testé isolément (56 tests, 0 échec).
</div>

</div>
<div>

## Pas encore fait

<div class="box y">
Rien de tout ça n'est <strong>branché</strong> sur la génération réelle de KerML/SysML.
</div>

<div class="box p">
Décider <em>quelles</em> métaclasses ont besoin du contrôleur, et avec quelle contrainte effective, reste une question de conception ouverte — pas de la plomberie restante.
</div>

</div>
</div>

<div class="takeaway">Le préflight actuel refuse déjà, proprement, toute redéfinition restrictive plutôt que de générer du code silencieusement faux — mais 79 associations réelles restent bloquées par ce refus.</div>

---

# 79 cas ne sont pas 79 problèmes différents

<div class="two-col">
<div>

## Ce que le préflight fait aujourd'hui

Il rejette **tout** écart de forme, sans distinction.

```
Relationship.target
  : KerMLModelElement [0..*]

Specialization.general
  : Type [1..1]  {redefines target}
```

`Type` est un sous-type de `KerMLModelElement`, `1..1` ⊆ `0..*` — c'est une **restriction valide**, pas une erreur.

</div>
<div>

## Le vrai problème à résoudre

<div class="box">
Distinguer une <strong>restriction valide</strong> d'une <strong>vraie incompatibilité</strong> (comme les 2 notes obsolètes citant <code>Element</code>).
</div>

<div class="box m">
Cette seule distinction change la nature du problème : pas 79 cas à traiter un par un, une règle de génération à corriger.
</div>

</div>
</div>

<div class="takeaway">La plupart des 79 « échecs » sont des restrictions normatives légitimes — le préflight ne sait juste pas encore faire la différence.</div>

---

<!-- _class: dense -->

# Proposition en 6 étapes

| # | Étape | Nouveau ? |
|---|---|---|
| 1 | Redéfinir la règle de préflight : accepter une restriction valide (sous-type + multiplicité incluse), rejeter le reste comme aujourd'hui | ✅ nouveau |
| 2 | Stockage canonique partagé — inchangé | déjà fait |
| 3 | Brancher `AssociationGuardCode` sur les classes concernées, contrainte calculée depuis leur propre type/multiplicité déclarés | ✅ nouveau |
| 4 | Empiler les gardes à travers l'héritage (`super.validateAssociation(...)` puis restriction propre) — cohérent car une redéfinition ne fait que restreindre davantage | patron déjà écrit |
| 5 | Cas des redéfinitions dérivées (`isDerived` change) — accesseur calculé, pas de garde | ✅ nouveau, plus petit |
| 6 | Valider sur un métamodèle jetable avant toute génération réelle | discipline déjà en place |

<div class="takeaway">Seules les étapes 1 et 3 sont vraiment nouvelles. Le reste réutilise ce qui est déjà écrit, compilé et testé.</div>

---

<!-- _class: "section theme-mint" -->

# Étapes 1 et 3 : faites et testées

## Expliquées simplement, avec l'exemple réel

---

# Un exemple concret, pour bien comprendre

<div class="two-col">
<div>

## Avant

`Relationship.target` accepte n'importe quoi (`KerMLModelElement`), en nombre illimité.

`Specialization.general` restreint : un seul élément, et ce doit être un `Type`.

<div class="box y">
Avant aujourd'hui : SemGen refusait de générer ce cas, point final.
</div>

</div>
<div>

## Après l'étape 1

SemGen accepte la restriction et partage **une seule case mémoire** entre les deux propriétés — ça, c'était déjà fait avant aujourd'hui.

<div class="box p">
Mais rien n'empêche encore d'écrire, via l'accesseur large (<code>target</code>), une valeur qui n'est pas un <code>Type</code> — la case est partagée, pas encore protégée.
</div>

</div>
</div>

<div class="takeaway">Partager la case mémoire ne suffit pas : il faut aussi surveiller tout ce qui essaie d'y écrire, par n'importe quel chemin.</div>

---

# L'étape 3, expliquée simplement : un garde-fou automatique

<div class="two-col">
<div>

## Ce qui est généré en plus

Pour chaque classe qui restreint une propriété (comme <code>Specialization</code>), SemGen génère maintenant 4 petites méthodes de contrôle.

Modelio les appelle **automatiquement**, à chaque fois que quelque chose essaie d'ajouter, d'enlever ou de remplacer une valeur dans la case partagée — <strong>peu importe par où ça arrive</strong>.

</div>
<div>

## Ce que fait chaque contrôle

<div class="box">
Une question simple : <em>« cette nouvelle valeur respecte-t-elle la règle plus stricte de cette classe précise ? »</em>
</div>

<div class="box y">
Si non : refus immédiat, <strong>avant</strong> que quoi que ce soit soit écrit. Le modèle ne se retrouve jamais dans un état incohérent.
</div>

</div>
</div>

<div class="takeaway">Ça bloque aussi le cas de l'écriture par le mauvais bout de l'association (<code>client.commandes.add(...)</code>) — pas seulement l'écriture directe.</div>

---

# Empiler les restrictions : une classe, puis sa sous-classe

<div class="two-col">
<div>

## Le cas à traiter

Une classe `B` restreint déjà une propriété. Sa sous-classe `C` la restreint **encore plus**.

</div>
<div>

## La solution retenue

<div class="box m">
<code>C</code> ne récrit pas tout : elle ajoute juste un petit bout de code qui dit <em>« vérifie d'abord la règle de <code>B</code>, puis vérifie en plus ma propre règle, plus stricte »</em>.
</div>

<div class="box">
Sûr par construction : une redéfinition ne fait jamais que restreindre davantage — jamais l'inverse.
</div>

</div>
</div>

<div class="takeaway">Une seule case mémoire, un seul jeu de contrôles empilés — pas une usine à gaz par classe.</div>

---

<!-- _class: dense -->

# Ce qui a été vérifié — pas juste rapporté

| Vérification | Résultat |
|---|---|
| Code généré relu directement (pas seulement le rapport qui le décrit) | ✅ conforme à ce qui précède |
| Suite de tests complète, relancée indépendamment | ✅ **80 tests, 0 échec** |
| Branchement réel confirmé dans `ImplGenerator.java` | ✅ `doGenerateAssociationGuards(cs)` bien appelé |
| Une classe partagée par génération (pas une copie par métaclasse) | ✅ vérifié dans le code |

<div class="takeaway">Cette fois, contrairement aux deux briques précédentes (stockage canonique, classe de support), le code est réellement branché sur la génération — pas seulement écrit et testé à côté.</div>

---

# Ce que « fait et testé » ne veut pas dire

<div class="two-col">
<div>

## Une décision déjà prise

<div class="box y">
L'étape 1 change le comportement de génération sur <strong>toute</strong> la surface des redéfinitions — c'est toujours un arbitrage d'équipe, même si le code existe déjà.
</div>

</div>
<div>

## Une garantie de résultat

<div class="box p">
<code>Type</code> sous-type de <code>KerMLModelElement</code> est vérifié <strong>au cas par cas</strong>, pas supposé vrai partout — pas encore confronté au modèle réel.
</div>

<div class="box">
Les propriétés dérivées (858 appels vers 397 accesseurs absents, audit antérieur) restent un chantier distinct de l'étape 5.
</div>

</div>
</div>

<div class="takeaway">Cette limite a depuis été levée — la suite montre ce qui s'est passé en confrontant tout ça au vrai modèle.</div>

---

<!-- _class: "section theme-mint" -->

# Confronté au vrai modèle

## Ce qui a changé en le testant pour de vrai

---

# Une erreur trouvée dans la règle elle-même

<div class="two-col">
<div>

## Ce qui restait strict, à raison

La règle de l'étape 1 exige toujours que <strong>l'extrémité opposée</strong> (l'autre bout de la même association) reste identique entre la propriété qui restreint et celle qu'elle restreint.

</div>
<div>

## Le problème, avec l'exemple réel

<code>Specialization.general</code> a pour opposé réel <code>Type.generalization</code> — <strong>pas</strong> <code>Specialization.specific</code>, comme ce document le supposait à tort plus haut.

<div class="box y">
Comparer <code>Type.generalization</code> directement à l'opposé de <code>Relationship.target</code> ne peut jamais correspondre — ce sont deux propriétés différentes.
</div>

</div>
</div>

<div class="takeaway">Testé sur les 90 vrais cas : les 90 étaient rejetés. Pas une règle trop stricte — une question mal posée.</div>

---

# La bonne question, et la correction

<div class="two-col">
<div>

## La question à poser

Pas « ces deux opposés sont-ils le même objet ? » mais « <strong>redéfinissent-ils la même chose</strong> ? »

</div>
<div>

## Le calcul, correctement posé

<code>Type.generalization</code> redéfinit-il l'opposé de <code>Relationship.target</code> ? En remontant la même logique déjà utilisée ailleurs dans le code : oui, exactement.

<div class="box">
Corrigé le jour même, retesté indépendamment : <strong>83 tests, 0 échec</strong>.
</div>

</div>
</div>

<div class="takeaway">Une vraie erreur de conception, pas une faute de code — seule la confrontation au modèle réel pouvait la révéler.</div>

---

# Le code corrigé, puis un trou dans la documentation du modèle

<div class="two-col">
<div>

## Après la correction du code

Toujours seulement <strong>1 cas sur 90</strong> accepté. Pas un bug cette fois — une information manquante.

</div>
<div>

## Ce qui manquait

Seul le sens « <code>general</code> redéfinit <code>target</code> » était noté. Personne n'avait aussi noté le fait symétrique côté opposé (<code>generalization</code> redéfinit l'opposé de <code>target</code>).

<div class="box m">
Pas une supposition : si <code>general</code> redéfinit <code>target</code>, alors <code>generalization</code> — son vrai opposé structurel — <strong>doit</strong> redéfinir l'opposé de <code>target</code>. Aucune autre possibilité cohérente.
</div>

</div>
</div>

<div class="takeaway">Un script (<code>phase15</code>) a ajouté cette note manquante partout où elle l'était réellement, sans toucher à rien d'autre : <strong>88 notes ajoutées</strong>, une seule transaction, commit et sauvegarde confirmés.</div>

---

# Un deuxième problème, trouvé en revérifiant — pas en espérant

<div class="two-col">
<div>

## Ce qu'une revérification immédiate a trouvé

<div class="box y">
17 des 88 notes ajoutées désignaient en fait <strong>la même classe</strong>, pas une classe ancêtre — le code réel qui lit ces notes ne cherche jamais que chez les ancêtres.
</div>

</div>
<div>

## La conséquence évitée

Ces 17 notes n'auraient pas juste été ignorées : elles auraient fait <strong>planter</strong> la génération réelle — et comme la classe concernée est la racine dont tout hérite, ç'aurait bloqué la génération entière, pas juste 17 cas.

</div>
</div>

<div class="takeaway">Corrigé le jour même de la même façon : un second script (<code>phase16</code>) a retiré <strong>exactement ces 17 lignes</strong>, restituant chaque note à son état d'avant — rien d'autre touché.</div>

---

<!-- _class: dense -->

# Le résultat final, réel

| Mesure | Valeur |
|---|---|
| Paires de redéfinition avec une note, après correction | 161 |
| **Désormais acceptées comme restriction légitime** | **124** |
| Encore rejetées, et pourquoi | 37 (voir ci-dessous) |

<div class="stat-box"><span class="number">124/161</span><span class="label">contre 1 avant la correction — la plus grande validation réelle de tout cet effort</span></div>

<div class="takeaway">Les 37 restants se répartissent en 3 groupes compris, aucun n'est une surprise : à détailler ensuite.</div>

---

# Les 37 restants, expliqués simplement

<div class="two-col">
<div>

## 13 + 9 cas : déjà connus

<div class="box">
<strong>13</strong> : la propriété qui restreint est calculée, celle qu'elle restreint est stockée — dans le mauvais sens. Chantier séparé, déjà identifié (étape 5).
</div>

<div class="box m">
<strong>9</strong> : la restriction change vraiment le mode de possession (référence simple → composition). Une vraie différence de conception de la norme, volontairement laissée de côté.
</div>

</div>
<div>

## 15 cas : une vraie limite du format

<div class="box y">
L'opposé qui manque encore vit sur <strong>la même classe</strong>, pas un ancêtre — exactement le problème des 17 notes retirées. Le format de note actuel ne peut pas exprimer ce cas.
</div>

<div class="box p">
Pas corrigeable automatiquement de la même façon — une décision de conception à prendre, pas un script de plus.
</div>

</div>
</div>

<div class="takeaway">Rien ici n'est une surprise ou un échec caché — chaque cas restant est compris et classé.</div>

---

# Ce que ça prouve — et ce que ça ne prouve pas

<div class="two-col">
<div>

## Prouvé

<div class="box">
La règle corrigée tient sur les <strong>vraies</strong> données KerML/SysML, pas seulement sur des exemples inventés — la validation la plus solide obtenue jusqu'ici.
</div>

</div>
<div>

## Pas prouvé

<div class="box p">
Aucune génération réelle n'a encore eu lieu. Le branchement de l'étape 3 n'a été exercé sur aucun de ces 124 cas réels.
</div>

</div>
</div>

<div class="takeaway">Toujours la même règle qu'au premier jour : une vraie génération reste la décision de l'utilisateur.</div>

---

<!-- _class: "section theme-poussin" -->

# Où en est le plan

---

<!-- _class: dense -->

# État d'avancement

| # | Étape | État |
|---|---|---|
| 1 | Point de greffe infrastructure (`KerMLModelElement`, `SysMLProject`) | ✅ fait |
| 2 | Chevauchements (`Note`, `Dependency`, métadonnées) | ✅ tranché |
| 3 | Héritage multiple — correctif SemGen `4.0.02` | ✅ validé |
| 4 | Transformation `reference/spec` → `reference/design` | ✅ 12 phases |
| 5 | Doublons `KerMLModelElement` (`name`, `elementId`) | ✅ corrigé |
| 6 | Granularité `structural.node` (28 grains) | ✅ corrigé |
| 7 | Stockage canonique des collections (291 rôles dérivés) | ✅ corrigé |
| 8 | Documentation SemGen/Javadoc (935 notes) | ✅ copiée |
| 9 | **Génération KerML** — 81 métaclasses | ✅ `GENERATION SUCCESSFUL` |
| 10 | **Génération SysML** — 97 métaclasses | 🔁 retry après correctif enum |
| 11 | Génération Java (JavaDesigner) | ⏳ ensuite |
| 12 | Bibliothèques normatives (Kernel + Systems Model Library) | ❌ non commencé |
| 13 | Redéfinitions restrictives — 79/90 réelles bloquées par le préflight | 🔁 outillage testé, non branché |

---

# Les trois prochaines étapes

<div class="two-col">
<div>

## Immédiat

<div class="box">
<strong>1. Relancer SysML</strong> — le premier run ne sélectionnait que 86 métaclasses : un littéral vide excluait les 11 éléments de <code>Requirements</code>. Le modèle est nettoyé et SemGen 4.0.03 bloque désormais ce défaut avant génération.
</div>

<div class="box m">
<strong>2. Lancer JavaDesigner</strong> sur <code>api</code>/<code>impl</code> pour produire le plugin Eclipse.
</div>

</div>
<div>

## Ensuite

<div class="box y">
<strong>3. Bibliothèques normatives</strong> — sans <code>Base::Anything</code>, <code>Parts::Part</code>, etc. instanciés, aucun modèle SysML v2 ne peut satisfaire les contraintes <code>specializesFromLibrary(...)</code>.
</div>

<div class="box p">
C'est le prochain vrai chantier de conception, pas un simple reste d'outillage.
</div>

</div>
</div>

<div class="takeaway">Les erreurs <code>Attribute X has no initial value</code> restantes sont délibérées : la norme ne fixe aucune valeur par défaut sur ces attributs. Elles ne bloquent pas la génération.</div>

---

# Ce qui reste ouvert côté outillage

<div class="two-col">
<div>

## Réduction possible

123 rôles KerML dérivés émettent encore, chacun, un getter **et** un getter filtré dans l'API.

Levier : `DependencyHelper` de SemGen, pas notre modèle.

</div>
<div>

## Chantier noyau Modelio 7

La substituabilité polymorphique réelle (`instanceof DataType`) suppose un `MClass`/`SmClass` multi-parent.

Positionné comme un changement de version majeure.

</div>
</div>

<div class="takeaway">Notre périmètre de modélisation est désormais clos. Les gains restants relèvent du générateur et du noyau, à arbitrer avec l'équipe outillage.</div>

---

<!-- _class: closing -->

# Discussion

Questions et retours bienvenus.
