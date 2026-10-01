# Propriétés dérivées : proposition pour `reference/design`

**Document de décision pour le chef de produit Modelio et le lead développeur, WIP (2026-09-29).** Objectif : choisir entre trois stratégies pour conserver dans `reference/design` les propriétés dérivées de `reference/spec` (miroir des XMI KerML 1.0 et SysML 2.0), sans créer de stockage Java dupliqué. La préférence proposée dans ce document est la **Proposition B**. Les attributs scalaires dérivés suivent la même décision.

## Table des matières

- [Propriétés dérivées : proposition pour `reference/design`](#propriétés-dérivées--proposition-pour-referencedesign)
  - [Table des matières](#table-des-matières)
  - [1. Le sens de « dérivé »](#1-le-sens-de--dérivé-)
    - [1.1 Exemple 1 : `subsettedProperty`](#11-exemple-1--subsettedproperty)
    - [1.2 Exemple 2 : `redefinedProperty`](#12-exemple-2--redefinedproperty)
    - [1.3 Exemple 3 : combinaison des mécanismes](#13-exemple-3--combinaison-des-mécanismes)
  - [2. Proposition A : propriétés dérivées calculées par SemGen](#2-proposition-a--propriétés-dérivées-calculées-par-semgen)
    - [2.1 Stéréotype `DerivedComputed`](#21-stéréotype-derivedcomputed)
    - [2.2 Stéréotype `DerivedSubset`](#22-stéréotype-derivedsubset)
    - [2.3 Stéréotype `DerivedRedefinition`](#23-stéréotype-derivedredefinition)
    - [2.4 Règle de génération Java](#24-règle-de-génération-java)
  - [3. Proposition B : ne générer que les propriétés non dérivées](#3-proposition-b--ne-générer-que-les-propriétés-non-dérivées)
    - [3.1 Bibliothèque commune de navigation et de calcul](#31-bibliothèque-commune-de-navigation-et-de-calcul)
      - [3.1.1 Contrat de base](#311-contrat-de-base)
      - [3.1.2 Fonctions essentielles](#312-fonctions-essentielles)
      - [3.1.3 Exemple `Behavior.step`](#313-exemple-behaviorstep)
      - [3.1.4 Règles de qualité](#314-règles-de-qualité)
  - [4. Proposition C : traitement au cas par cas](#4-proposition-c--traitement-au-cas-par-cas)
  - [5. Résumé et critères de choix](#5-résumé-et-critères-de-choix)
  - [6. Préserver l'indépendance de KerML](#6-préserver-lindépendance-de-kerml)
  - [7. Périmètre, inventaire et décisions](#7-périmètre-inventaire-et-décisions)
    - [7.1 Méthode de l'inventaire cible](#71-méthode-de-linventaire-cible)
    - [7.2 Inventaire des 291 propriétés dérivées à annoter](#72-inventaire-des-291-propriétés-dérivées-à-annoter)
      - [7.2.1 KerML](#721-kerml)
      - [7.2.2 SysML](#722-sysml)
    - [7.3 Points de discussion](#73-points-de-discussion)

## 1. Le sens de « dérivé »

Dans la norme, `isDerived=true` signifie que la valeur se déduit d'autres éléments du modèle. Elle ne constitue pas, à elle seule, un deuxième stockage à synchroniser. `subsettedProperty` indique une inclusion de valeurs; `redefinedProperty` indique une spécialisation héritée. Ces trois relations ne sont pas interchangeables, et un lien `subsets` ne fournit pas automatiquement l'algorithme de calcul.

### 1.1 Exemple 1 : `subsettedProperty`

`KerML::Kernel::Behaviors::Behavior.step` (KerML 1.0 XMI) :

```xml
<packagedElement xmi:id="Kernel-Behaviors-Behavior" xmi:type="uml:Class" name="Behavior">
  <ownedAttribute xmi:id="Kernel-Behaviors-Behavior-step" xmi:type="uml:Property" isDerived="true" name="step">
  <association xmi:idref="Kernel-Behaviors-A_step_featuringBehavior"/>
  <lowerValue xmi:id="Kernel-Behaviors-Behavior-step-lowerValue" xmi:type="uml:LiteralInteger" name=""/>
  <ownedComment xmi:id="Kernel-Behaviors-Behavior-step-_comment.0" xmi:type="uml:Comment"
      body="&lt;p&gt;The &lt;code&gt;Steps&lt;/code&gt; that make up this &lt;code&gt;Behavior&lt;/code&gt;.&lt;/p&gt;">
    <annotatedElement xmi:idref="Kernel-Behaviors-Behavior-step"/>
  </ownedComment>
  <subsettedProperty xmi:idref="Core-Types-Type-feature"/>
  <type xmi:idref="Kernel-Behaviors-Step"/>
  <upperValue xmi:id="Kernel-Behaviors-Behavior-step-upperValue" xmi:type="uml:LiteralUnlimitedNatural" name="" value="-1"/>
  </ownedAttribute>
</packagedElement>
```

La propriété ciblée `Core-Types-Type-feature` est elle-même dérivée dans le même XMI :

```xml
<packagedElement xmi:id="Core-Types-Type" xmi:type="uml:Class" name="Type">
  <ownedAttribute xmi:id="Core-Types-Type-feature" xmi:type="uml:Property" isDerived="true" isOrdered="true" name="feature">
  <association xmi:idref="Core-Types-A_typeWithFeature_feature"/>
  <lowerValue xmi:id="Core-Types-Type-feature-lowerValue" xmi:type="uml:LiteralInteger" name=""/>
  <ownedComment xmi:id="Core-Types-Type-feature-_comment.0" xmi:type="uml:Comment"
      body="&lt;p&gt;The &lt;code&gt;ownedMemberFeatures&lt;/code&gt; of the &lt;code&gt;featureMemberships&lt;/code&gt; of this &lt;code&gt;Type&lt;/code&gt;.&lt;/p&gt;">
    <annotatedElement xmi:idref="Core-Types-Type-feature"/>
  </ownedComment>
  <subsettedProperty xmi:idref="Root-Namespaces-Namespace-member"/>
  <type xmi:idref="Core-Features-Feature"/>
  <upperValue xmi:id="Core-Types-Type-feature-upperValue" xmi:type="uml:LiteralUnlimitedNatural" name="" value="-1"/>
  </ownedAttribute>
</packagedElement>
```

La propriété ciblée par `Type.feature` est elle aussi dérivée :

```xml
<packagedElement xmi:id="Root-Namespaces-Namespace" xmi:type="uml:Class" name="Namespace">
  <ownedAttribute xmi:id="Root-Namespaces-Namespace-membership" xmi:type="uml:Property" isDerived="true" isDerivedUnion="true" isOrdered="true" name="membership">
    <association xmi:idref="Root-Namespaces-A_membership_membershipNamespace"/>
    <lowerValue xmi:id="Root-Namespaces-Namespace-membership-lowerValue" xmi:type="uml:LiteralInteger" name=""/>
    <ownedComment xmi:id="Root-Namespaces-Namespace-membership-_comment.0" xmi:type="uml:Comment"
        body="&lt;p&gt;All &lt;code&gt;Memberships&lt;/code&gt; in this &lt;code&gt;Namespace&lt;/code&gt;, including (at least) the union of &lt;code&gt;ownedMemberships&lt;/code&gt; and &lt;code&gt;importedMemberships&lt;/code&gt;.&lt;/p&gt;">
      <annotatedElement xmi:idref="Root-Namespaces-Namespace-membership"/>
    </ownedComment>
    <type xmi:idref="Root-Namespaces-Membership"/>
    <upperValue xmi:id="Root-Namespaces-Namespace-membership-upperValue" xmi:type="uml:LiteralUnlimitedNatural" name="" value="-1"/>
  </ownedAttribute>
  <ownedAttribute xmi:id="Root-Namespaces-Namespace-member" xmi:type="uml:Property" isDerived="true" isOrdered="true" name="member">
    <association xmi:idref="Root-Namespaces-A_member_namespace"/>
    <lowerValue xmi:id="Root-Namespaces-Namespace-member-lowerValue" xmi:type="uml:LiteralInteger" name=""/>
    <ownedComment xmi:id="Root-Namespaces-Namespace-member-_comment.0" xmi:type="uml:Comment"
        body="&lt;p&gt;The set of all member &lt;code&gt;Elements&lt;/code&gt; of this &lt;code&gt;Namespace&lt;/code&gt;, which are the &lt;code&gt;memberElements&lt;/code&gt; of all &lt;code&gt;memberships&lt;/code&gt; of the &lt;code&gt;Namespace&lt;/code&gt;.&lt;/p&gt;">
      <annotatedElement xmi:idref="Root-Namespaces-Namespace-member"/>
    </ownedComment>
    <type xmi:idref="Root-Elements-Element"/>
    <upperValue xmi:id="Root-Namespaces-Namespace-member-upperValue" xmi:type="uml:LiteralUnlimitedNatural" name="" value="-1"/>
  </ownedAttribute>
</packagedElement>
```

Chaque `Membership` porte ensuite l'élément qui devient membre :

```xml
<packagedElement xmi:id="Root-Namespaces-Membership" xmi:type="uml:Class" name="Membership">
  <ownedAttribute xmi:id="Root-Namespaces-Membership-memberElement" xmi:type="uml:Property" name="memberElement">
    <association xmi:idref="Root-Namespaces-A_memberElement_membership"/>
    <lowerValue xmi:id="Root-Namespaces-Membership-memberElement-lowerValue" xmi:type="uml:LiteralInteger" name="" value="1"/>
    <ownedComment xmi:id="Root-Namespaces-Membership-memberElement-_comment.0" xmi:type="uml:Comment"
        body="&lt;p&gt;The &lt;code&gt;Element&lt;/code&gt; that becomes a &lt;code&gt;member&lt;/code&gt; of the &lt;code&gt;membershipOwningNamespace&lt;/code&gt; due to this &lt;code&gt;Membership&lt;/code&gt;.&lt;/p&gt;">
      <annotatedElement xmi:idref="Root-Namespaces-Membership-memberElement"/>
    </ownedComment>
    <redefinedProperty xmi:idref="Root-Elements-Relationship-target"/>
    <type xmi:idref="Root-Elements-Element"/>
    <upperValue xmi:id="Root-Namespaces-Membership-memberElement-upperValue" xmi:type="uml:LiteralUnlimitedNatural" name="" value="1"/>
  </ownedAttribute>
</packagedElement>
```

![Chaîne de dérivation de `Behavior.step`](media/exemple-1-chaine-derivation.png)

Lecture : `Namespace.membership` est elle-même dérivée (`isDerived="true"`) et déclarée comme union dérivée (`isDerivedUnion="true"`) des memberships possédées et importées. La formule de dérivation de `Namespace.member` part ensuite de cette collection dérivée et suit `Membership.memberElement`. Le commentaire XMI de `Namespace.member` le dit explicitement : « the `memberElements` of all `memberships` ».

Ainsi, `Behavior.step` est dérivée (`isDerived="true"`) et **sous-ensemble** de `Type.feature` (`<subsettedProperty xmi:idref="Core-Types-Type-feature"/>`). `Type.feature` est lui-même dérivé et sous-ensemble de `Namespace.member`, qui est également dérivé. Le lien `subsettedProperty` exprime donc une inclusion dans une chaîne de trois vues dérivées : `Behavior.step` → `Type.feature` → `Namespace.member` → `Membership.memberElement`. Il ne fournit pas, à lui seul, l'algorithme qui calcule ces collections.

Le chemin complet de calcul est plus long que cette première chaîne. Les propriétés marquées `isDerived="true"` sont les vues calculées; les feuilles sans cet attribut sont les données ou paramètres qui alimentent effectivement le calcul :

```text
Behavior.step [dérivée]
  -> Type.feature [dérivée]
    -> Namespace.member [dérivée]
      -> Membership.memberElement [NON dérivée]
      -> Namespace.membership [dérivée]
        -> Namespace.ownedMembership [dérivée]
          -> Element.ownedRelationship [NON dérivée]
          -> filtre : relationships qui sont des Memberships 
        -> Namespace.importedMembership [dérivée]
          -> Namespace.ownedImport [dérivée]
            -> Element.ownedRelationship [NON dérivée]
            -> filtre : relationships qui sont des Imports
          -> Import.importedMemberships(...) [dérivée]
             -> NamespaceImport.importedNamespace [NON dérivée]
             -> MembershipImport.importedMembership [NON dérivée]
```

La chaîne doit être lue ainsi : `Namespace.membership` est l'union dérivée de `ownedMembership` et `importedMembership`. La branche locale sélectionne dans `Element.ownedRelationship` les relations qui sont des `Membership`. La branche importée sélectionne les `Import` dans la même collection source, puis demande à chaque `Import` les memberships à importer. Pour un `NamespaceImport`, la source est `importedNamespace` et l'opération XMI est `importedNamespace.visibleMemberships(excluded, isRecursive, isImportAll)`. Pour un `MembershipImport`, la source est directement `importedMembership`.

Les paramètres `Import.visibility`, `Import.isRecursive` et `Import.isImportAll` sont eux aussi non dérivés : ils contrôlent quelles memberships visibles sont retenues et si la recherche est récursive. Le XMI montre donc deux catégories distinctes : `subsettedProperty` décrit les inclusions entre vues, tandis que les propriétés sans `isDerived` (`Element.ownedRelationship`, `Membership.memberElement`, `NamespaceImport.importedNamespace`, `MembershipImport.importedMembership` et les paramètres de l'import) constituent les points où l'information est effectivement portée. `Namespace.ownedMembership`, `Namespace.ownedImport` et `Namespace.importedMembership`, eux, restent des vues dérivées.

### 1.2 Exemple 2 : `redefinedProperty`

`KerML::Kernel::Behaviors::Step.parameter` (KerML 1.0 XMI) :

```xml
<packagedElement xmi:id="Kernel-Behaviors-Step" xmi:type="uml:Class" name="Step">
  <ownedAttribute xmi:id="Kernel-Behaviors-Step-parameter" xmi:type="uml:Property" isDerived="true" isOrdered="true" name="parameter">
  <association xmi:idref="Kernel-Behaviors-A_parameter_parameteredStep"/>
  <lowerValue xmi:id="Kernel-Behaviors-Step-parameter-lowerValue" xmi:type="uml:LiteralInteger" name=""/>
  <ownedComment xmi:id="Kernel-Behaviors-Step-parameter-_comment.0" xmi:type="uml:Comment"
      body="&lt;p&gt;The &lt;code&gt;parameters&lt;/code&gt; of this &lt;code&gt;Step&lt;/code&gt;, which are defined as its &lt;code&gt;directedFeatures&lt;/code&gt;, whose values are passed into and/or out of a performance of the &lt;code&gt;Step&lt;/code&gt;.&lt;/p&gt;">
    <annotatedElement xmi:idref="Kernel-Behaviors-Step-parameter"/>
  </ownedComment>
  <redefinedProperty xmi:idref="Core-Types-Type-directedFeature"/>
  <type xmi:idref="Core-Features-Feature"/>
  <upperValue xmi:id="Kernel-Behaviors-Step-parameter-upperValue" xmi:type="uml:LiteralUnlimitedNatural" name="" value="-1"/>
  </ownedAttribute>
</packagedElement>
```

Lecture : `Step.parameter` **redéfinit** `Type.directedFeature` (`<redefinedProperty idref="Core-Types-Type-directedFeature"/>`). Une redéfinition spécialise une propriété héritée avec un type ou un rôle plus précis (ici, restreint aux `Feature` typés `directedFeature` dans le contexte d'un `Step`) — c'est un mécanisme d'héritage, pas seulement d'inclusion de valeurs comme `subsets`.

### 1.3 Exemple 3 : combinaison des mécanismes

`SysML::Systems::Actions::ActionUsage.actionDefinition` (SysML 2.0 XMI), qui redéfinit à la fois une propriété SysML et une propriété KerML :

```xml
<packagedElement xmi:id="Systems-Actions-ActionUsage" xmi:type="uml:Class" name="ActionUsage">
  <ownedAttribute xmi:id="Systems-Actions-ActionUsage-actionDefinition" xmi:type="uml:Property" isDerived="true" isOrdered="true" name="actionDefinition">
  <association xmi:idref="Systems-Actions-A_actionDefinition_definedAction"/>
  <lowerValue xmi:id="Systems-Actions-ActionUsage-actionDefinition-lowerValue" xmi:type="uml:LiteralInteger" name=""/>
  <ownedComment xmi:id="Systems-Actions-ActionUsage-actionDefinition-_comment.0" xmi:type="uml:Comment"
      body="&lt;p&gt;The &lt;code&gt;Behaviors&lt;/code&gt; that are the &lt;code&gt;types&lt;/code&gt; of this &lt;code&gt;ActionUsage&lt;/code&gt;. Nominally, these would be &lt;code&gt;ActionDefinitions&lt;/code&gt;, but other kinds of Kernel &lt;code&gt;Behaviors&lt;/code&gt; are also allowed, to permit use of &lt;code&gt;Behaviors&lt;/code&gt; from the Kernel Model Libraries.&lt;/p&gt;">
    <annotatedElement xmi:idref="Systems-Actions-ActionUsage-actionDefinition"/>
  </ownedComment>
  <redefinedProperty href="https://www.omg.org/spec/KerML/20250201/KerML.xmi#Kernel-Behaviors-Step-behavior"/>
  <redefinedProperty xmi:idref="Systems-Occurrences-OccurrenceUsage-occurrenceDefinition"/>
  <type href="https://www.omg.org/spec/KerML/20250201/KerML.xmi#Kernel-Behaviors-Behavior"/>
  <upperValue xmi:id="Systems-Actions-ActionUsage-actionDefinition-upperValue" xmi:type="uml:LiteralUnlimitedNatural" name="" value="-1"/>
  </ownedAttribute>
</packagedElement>
```

Lecture : `ActionUsage.actionDefinition` est dérivée et porte **deux** `redefinedProperty` : une référence `href` traversant le fichier XMI KerML (`Step.behavior`), et une référence `xmi:idref` interne au fichier SysML (`OccurrenceUsage.occurrenceDefinition`). C'est exactement le motif déjà repéré dans les 34 cas d'héritage multiple : une même propriété SysML spécialise à la fois son axe KerML hérité et son axe SysML hérité. Aucune formule OCL n'accompagne ce lien — `redefinedProperty` documente une relation de spécialisation, pas un algorithme de calcul.

Ces trois exemples motivent la mise en garde du paragraphe précédent : la présence d'un `subsets`/`redefines` normatif renseigne sur *la place* de la propriété dans la hiérarchie, jamais sur *comment* la calculer.

## 2. Proposition A : propriétés dérivées calculées par SemGen

Dans le scénario étudié ici, `reference/design` conserve toutes les propriétés dérivées de `reference/spec`, avec leur `isDerived`, leurs `subsettedProperty` et leurs `redefinedProperty`. Le modèle de conception ne masque donc pas la structure normative et ne supprime pas les associations. Il ajoute en revanche des informations de génération destinées à SemGen : une propriété dérivée ne doit pas devenir un second stockage Java simplement parce qu'elle est navigable dans le métamodèle.

L'objectif est double :

1. conserver dans `design` la surface normative complète, pour que les relations, les types et l'héritage restent inspectables;
2. demander à SemGen de générer une opération ou un accès calculé, mais ni champ `Data` ni descripteur de valeur stockée pour une propriété dérivée.

Cette proposition traite donc séparément la sémantique du modèle et la politique de génération. `isDerived=true` reste la source normative; les nouveaux stéréotypes documentent comment SemGen doit exploiter cette information.

### 2.1 Stéréotype `DerivedComputed`

À appliquer à chaque propriété dérivée, avec des tagged values permettant de décrire le calcul :

| Tagged value proposé | Rôle |
|---|---|
| `calculationKind` | `ocl`, `navigation`, `union`, `custom` ou autre stratégie supportée par SemGen |
| `calculationExpression` | expression OCL ou expression de navigation normative |
| `calculationOperation` | opération Java ou service à appeler lorsque le calcul ne tient pas dans une expression |
| `resultType` | type et multiplicité du résultat calculé |
| `storagePolicy` | valeur imposée à `none` pour interdire le stockage dupliqué |
| `apiPolicy` | génération d'un getter calculé, d'une opération ou d'une API interne |

Le contrat minimal de `DerivedComputed` serait : SemGen génère la signature publique et son calcul, mais ne génère jamais de champ persistant pour la propriété. Si la méthode de calcul n'est pas encore renseignée, SemGen doit produire une erreur de validation explicite plutôt qu'un champ de secours silencieux.

La source du calcul doit être explicitement attribuée : soit une expression extraite de la norme XMI/OCL, soit une expression renseignée dans `reference/design`, soit une opération validée manuellement. L'inventaire ne constitue pas à lui seul une implémentation. Chaque propriété doit donc passer par une validation avant génération : résolution des propriétés de base, vérification des types et multiplicités, test du calcul sur des instances et contrôle de l'absence de stockage secondaire.

### 2.2 Stéréotype `DerivedSubset`

À appliquer lorsqu'une propriété porte `subsettedProperty`. Il compléterait la relation UML/XMI par les informations nécessaires à la génération :

| Tagged value proposé | Rôle |
|---|---|
| `baseProperty` | propriété de base restreinte, résolue depuis `subsettedProperty` |
| `subsetCondition` | condition de filtrage, par exemple type, prédicat OCL ou sélection de membership |
| `subsetExpression` | expression complète calculant le sous-ensemble |
| `storagePolicy` | `none`, hérité de `DerivedComputed` |

`DerivedSubset` ne doit pas être interprété comme un stockage de la sous-propriété. Il décrit le calcul de la projection à partir de la propriété de base. Dans l'exemple `Behavior.step`, `baseProperty` serait `Type.feature` et `subsetCondition` exprimerait la sélection des `Step`.

### 2.3 Stéréotype `DerivedRedefinition`

À appliquer lorsqu'une propriété porte `redefinedProperty`. Il expliciterait la propriété héritée et le contrat de spécialisation :

| Tagged value proposé | Rôle |
|---|---|
| `baseProperty` | propriété ou propriétés redéfinies, résolues depuis les références XMI |
| `redefinitionCondition` | condition qui précise ou remplace le calcul hérité |
| `redefinitionExpression` | calcul effectif de la propriété redéfinie |
| `inheritCalculation` | indique si le calcul hérité est réutilisé avant spécialisation |
| `storagePolicy` | `none`, sauf décision explicite contraire pour une propriété non dérivée |

Pour `ActionUsage.actionDefinition`, `baseProperty` contiendrait les deux propriétés référencées par les deux `redefinedProperty` du XMI, l'une KerML et l'autre SysML. Cette information doit rester distincte de `DerivedSubset` : redéfinir une propriété est une spécialisation d'héritage, pas une simple inclusion de valeurs.

### 2.4 Règle de génération Java

SemGen devrait appliquer la règle suivante avant de créer `Data`, `SmAttribute` ou un accesseur :

```text
if property.isDerived:
  require DerivedComputed
  forbid stored field and stored-value descriptor
  generate calculation API from DerivedComputed/DerivedSubset/DerivedRedefinition
else:
  generate ordinary storage according to the existing policy
```

Cette règle conserve les getters utiles, évite le stockage dupliqué et rend les lacunes visibles au moment de la génération. Elle doit s'appliquer aux extrémités d'association comme aux cinq attributs scalaires dérivés (`KerMLModelElement.isLibraryElement`, `Type.isConjugated`, `Function.isModelLevelEvaluable`, `Expression.isModelLevelEvaluable` et `Usage.isReference`).

Les annotations ne remplacent pas les règles normatives : elles les rendent exploitables par SemGen. Une propriété sans expression de calcul vérifiée ne doit pas être transformée automatiquement en champ, car ce choix change la sémantique et crée un état concurrent de la vue dérivée.

## 3. Proposition B : ne générer que les propriétés non dérivées

La proposition B consiste à ne générer aucun attribut dérivé dans l'API Java. SemGen générerait uniquement les propriétés qui ne portent pas `isDerived=true`; les propriétés dérivées resteraient dans le métamodèle et dans `reference/design`, mais ne deviendraient ni champs, ni descripteurs de stockage, ni getters dédiés.

Dans cette option, le client de l'API doit parcourir lui-même l'infrastructure normative non dérivée conservée. Les propriétés dérivées comme `Namespace.membership`, `Namespace.ownedMembership` et `Namespace.importedMembership` ne sont pas disponibles comme getters dédiés. Par exemple, un client qui possède un `Behavior` et veut retrouver ses `Step` doit partir des relations possédées (`Element.ownedRelationship`), sélectionner les `Membership`, lire leur `Membership.memberElement`, puis traiter séparément les `Import` et leurs memberships importées. La forme conceptuelle est :

```text
Behavior
  -> Element.ownedRelationship [non dérivée]
  -> sélection des Membership et des Import
  -> Membership.memberElement
  -> filtrage des éléments de type Step
  -> traitement des memberships importées selon les règles d'Import
```

Cette option fait sens si l'infrastructure de base est considérée comme l'API stable. Pour éviter que chaque client réimplémente les mêmes parcours, nous développerions **en dehors de SemGen** une bibliothèque commune de navigation et de calcul : memberships locales et importées, imports récursifs, visibilité, héritage, subsetting et redefinition. Les clients appelleraient cette bibliothèque plutôt que de recopier la logique. SemGen resterait limité à la génération des propriétés non dérivées et du stockage de base.

La proposition B doit donc être accompagnée de cette bibliothèque commune, de sa documentation normative et de tests d'instances. L'absence de getters dérivés ne supprime pas la complexité : elle la centralise dans un composant maîtrisé hors SemGen, au lieu de la disperser dans chaque client.

### 3.1 Bibliothèque commune de navigation et de calcul

Cette bibliothèque serait développée à la main, en dehors de SemGen, au-dessus des propriétés non dérivées générées par SemGen. Elle ne créerait aucun champ miroir et ne modifierait pas le modèle : chaque fonction reconstruirait une vue à partir des relations et éléments déjà stockés.

#### 3.1.1 Contrat de base

Le contrat minimal serait :

```text
derivedValue(element, property) -> valeur calculée, jamais stockée
```

La bibliothèque devrait garantir que deux appels successifs reflètent le même état du modèle, et que toute mutation passe par les propriétés de base. Elle ne devrait pas maintenir de cache persistant sans mécanisme explicite d'invalidation.

#### 3.1.2 Fonctions essentielles

| Fonction | Responsabilité |
|---|---|
| `ownedRelationships(namespace)` | Retourner les relations possédées à partir de `Element.ownedRelationship`. |
| `ownedMemberships(namespace)` | Filtrer les relations possédées pour conserver les `Membership`. |
| `ownedImports(namespace)` | Filtrer les relations possédées pour conserver les `Import`. |
| `importedMemberships(namespace, options)` | Parcourir les imports, appliquer visibilité, récursivité et `isImportAll`, puis éviter les cycles. |
| `memberships(namespace, options)` | Unionner memberships possédées et importées, sans dupliquer les éléments. |
| `memberElements(memberships)` | Projeter chaque `Membership` vers `Membership.memberElement`. |
| `members(namespace, options)` | Calculer `Namespace.member` à partir de `memberships` puis `memberElements`. |
| `filterByType(elements, type)` | Sélectionner les éléments correspondant à un métamodèle, par exemple les `Step`. |
| `subsets(values, baseProperty, condition)` | Calculer une propriété restreinte à partir de sa propriété de base et de sa condition. |
| `redefines(value, baseProperty, condition)` | Appliquer le contrat d'une propriété redéfinie sans créer une seconde valeur stockée. |
| `resolveKerMLReference(reference)` | Résoudre une référence SysML vers KerML sans créer d'association inverse dans KerML. |

#### 3.1.3 Exemple `Behavior.step`

Le client ou la bibliothèque pourrait exposer une fonction de confort, mais son implémentation resterait un parcours de l'infrastructure :

```text
behaviorSteps(behavior) =
  filterByType(
    members(behavior, imports = true, recursive = true),
    Step
  )
```

`behaviorSteps` n'est pas un getter généré par SemGen et ne stocke aucun résultat. C'est une fonction de bibliothèque qui centralise le calcul de `Behavior.step`, y compris les memberships importées et les options de visibilité.

#### 3.1.4 Règles de qualité

La bibliothèque devra être testée sur les cas qui rendent la Proposition B risquée : imports récursifs et cycles, visibilité, héritage, memberships dupliquées, subsetting multiple, redefinitions multiples, références SysML→KerML et mutations du modèle après un premier calcul. Ces tests sont indispensables pour que l'API d'infrastructure reste une alternative crédible aux getters dérivés.

## 4. Proposition C : traitement au cas par cas

La proposition C consiste à décider, pour chaque propriété dérivée, entre :

- générer un getter calculé;
- ne générer que l'infrastructure et laisser le client parcourir les relations;
- fournir une opération spécialisée écrite ou validée manuellement;
- refuser la génération tant que la règle normative n'est pas formalisée;
- traiter séparément les propriétés qui traversent la frontière KerML/SysML.

Cette option permet de respecter au plus près les besoins réels des clients et les difficultés propres à chaque propriété. Elle permet aussi de distinguer proprement un simple sous-ensemble d'une propriété dérivée par OCL, une redéfinition héritée, une union de memberships ou une relation SysML→KerML.

Son coût est toutefois très élevé : il faut analyser, spécifier, implémenter et tester les centaines de propriétés dérivées, puis maintenir ces décisions lorsque les XMI, SemGen ou les contrats d'API évoluent. Sans grille de décision et sans automatisation, la proposition C risque de devenir un chantier long et hétérogène.

## 5. Résumé et critères de choix

<table>
<thead>
<tr><th>Critère</th><th style="background-color: #e8f5e9;">Proposition A<br>getters calculés</th><th style="background-color: #f1f8e9;">Proposition B<br>infrastructure seule</th><th style="background-color: #ffebee;">Proposition C<br>cas par cas</th></tr>
</thead>
<tbody>
<tr><th>Fidélité de l'API normative</th><td style="background-color: #c8e6c9;">Forte si les expressions de calcul sont correctement renseignées</td><td style="background-color: #ffebee;">Forte au niveau du métamodèle, faible au niveau de l'ergonomie client</td><td style="background-color: #c8e6c9;">Potentiellement maximale, propriété par propriété</td></tr>
<tr><th>Stockage Java dupliqué</th><td style="background-color: #c8e6c9;">Évité par la règle SemGen proposée</td><td style="background-color: #c8e6c9;">Évité par construction</td><td style="background-color: #c8e6c9;">Évité si chaque décision l'interdit explicitement</td></tr>
<tr><th>Effort initial SemGen</th><td style="background-color: #ffcdd2;">Important : nouveau support des stéréotypes et du calcul</td><td style="background-color: #dcedc8;">Faible à moyen : exclure les dérivés de la génération</td><td style="background-color: #ffcdd2;">Très important : orchestration et support de nombreux cas</td></tr>
<tr><th>Effort côté client</th><td style="background-color: #c8e6c9;">Faible : getters calculés disponibles</td><td style="background-color: #ffcdd2;">Élevé : parcours des memberships, imports et relations à réimplémenter</td><td style="background-color: #ffebee;">Variable selon la décision retenue</td></tr>
<tr><th>Risque d'incohérence entre clients</th><td style="background-color: #c8e6c9;">Faible si SemGen centralise le calcul</td><td style="background-color: #dcedc8;">Faible à moyen si la bibliothèque commune est correctement testée</td><td style="background-color: #ffebee;">Moyen, dépendant de la qualité de chaque implémentation</td></tr>
<tr><th>Gestion de KerML/SysML</th><td style="background-color: #c8e6c9;">Contrôlable avec des liens unidirectionnels</td><td style="background-color: #c8e6c9;">Naturellement contrôlable si seules les infrastructures nécessaires sont exposées</td><td style="background-color: #ffebee;">À décider pour chaque relation</td></tr>
<tr><th>Délai de mise en œuvre</th><td style="background-color: #ffcdd2;">Moyen à long</td><td style="background-color: #dcedc8;">Le plus court</td><td style="background-color: #ffcdd2;">Le plus long</td></tr>
</tbody>
</table>

La préférence proposée est la **Proposition B**, sous réserve d'accepter l'investissement dans la bibliothèque commune et son contrat d'API. Le choix peut s'appuyer sur cinq critères prioritaires :

1. **Ergonomie client** : les consommateurs ont-ils besoin de getters comme `Behavior.step`, ou peuvent-ils dépendre de parcours d'infrastructure ?
2. **Complétude normative** : dispose-t-on d'une expression de calcul vérifiée pour la propriété, y compris les imports, l'héritage et l'OCL ?
3. **Coût de SemGen** : veut-on investir dans un moteur de calcul et des stéréotypes, ou limiter SemGen à la génération du stockage non dérivé ? La préférence B choisit la seconde option.
4. **Stabilité de l'API** : préfère-t-on centraliser les décisions dans le générateur ou exposer l'infrastructure aux clients ?
5. **Indépendance des métamodèles** : le calcul traverse-t-il KerML et SysML sans créer d'association inverse dans KerML ?

## 6. Préserver l'indépendance de KerML

La conservation des propriétés dérivées dans `reference/design` ne doit pas conduire à conserver toutes les associations entre packages KerML et SysML. Ces deux décisions sont indépendantes : une propriété SysML peut rester décrite dans le modèle SysML et être calculée à partir d'une relation KerML, sans que le métamodèle KerML contienne une association inverse vers SysML.

L'exemple représentatif est `SysML::Usage.definition`. Dans le XMI SysML, cette propriété est dérivée, redéfinit `KerML::Feature.type` et est typée par `KerML::Classifier`. Si l'association `Usage.definition` est matérialisée des deux côtés dans le modèle de conception, le générateur peut produire une référence depuis `Usage` vers `Classifier` et, par effet de l'association opposée, une référence depuis `Classifier` vers `Usage`. KerML devient alors dépendant d'une notion SysML, ce qui contredit son rôle de noyau indépendant.

La règle proposée est donc :

```text
KerML -> KerML : association conservée dans le métamodèle KerML
SysML -> SysML : association conservée dans le métamodèle SysML
SysML -> KerML : référence calculée ou lien de génération unidirectionnel
KerML -> SysML : aucune association normative ni accesseur inverse
```

Pour `Usage.definition`, SemGen pourrait générer le getter calculé du côté SysML à partir de `Feature.type`, avec une projection vers les `Classifier` attendues, mais ne devrait pas créer de propriété `usages` ou `definedUsages` dans `Classifier`/KerML. Le lien entre les deux métamodèles serait conservé comme référence XMI, tagged value ou contrat de calcul, pas comme association navigable réciproque.

Cette contrainte s'applique aux 32 relations SysML/KerML concernées par l'indépendance des packages. Elles doivent être traitées séparément des 291 propriétés dérivées : les stéréotypes `DerivedComputed`, `DerivedSubset` et `DerivedRedefinition` décrivent le calcul d'une propriété; une règle d'architecture `KerMLIndependent` doit en plus interdire la création d'une association inverse dans KerML.

## 7. Périmètre, inventaire et décisions

### 7.1 Méthode de l'inventaire cible

Les 291 entrées ci-dessous constituent d'abord un inventaire de cadrage : elles montrent l'ampleur du périmètre des propriétés dérivées d'association à conserver dans `reference/design`. Elles viennent du miroir normatif `reference/spec`, regroupées par package, classe propriétaire et rôle opposé. Dans un premier temps, la table sert à mesurer et discuter le problème; elle pourra ensuite guider l'implémentation et les tests de la bibliothèque commune de la Proposition B.

La table est groupée par package normatif puis classe propriétaire. Chaque rôle est à conserver dans `design` avec `isDerived=true`; les annotations `DerivedComputed`, `DerivedSubset` et/ou `DerivedRedefinition` préciseront son calcul et sa politique de génération. `Element` normatif est nommé `KerMLModelElement` dans `design`.

### 7.2 Inventaire des 291 propriétés dérivées à annoter

La quatrième colonne est semi-formelle. `subset(X.y)` indique une restriction à la propriété de base `X.y`; `redefine(X.y)` indique une spécialisation héritée; `union(...)` et `navigate(...)` décrivent un parcours de relations; `filter(...)` ajoute une condition de sélection. Une expression `derive(...)` signifie que le XMI identifie la propriété mais que son algorithme doit encore être formalisé. Ces notations décrivent le point de départ ou le calcul proposé : elles ne remplacent pas la validation OCL et les tests d'instances.

#### 7.2.1 KerML

| Package normatif | Classe propriétaire | Propriété dérivée | Relation normative / calcul proposé |
|---|---|---|---|
| Core.Classifiers | Classifier | `ownedSubclassification` | subset(Type.ownedSpecialization) |
| Core.Classifiers | Subclassification | `owningClassifier` | redefine(Specialization.owningType) |
| Core.Features | CrossSubsetting | `crossingFeature` | redefine(Subsetting.owningFeature) + redefine(Subsetting.subsettingFeature) |
| Core.Features | EndFeatureMembership | `ownedMemberFeature` | redefine(FeatureMembership.ownedMemberFeature) |
| Core.Features | Feature | `associationWithEnd` | derive(Feature.associationWithEnd) |
| Core.Features | Feature | `chainingFeature` | navigate(A_chainingFeature_chainedFeature -> Feature.chainingFeature) |
| Core.Features | Feature | `crossFeature` | navigate(A_crossFeature_featureCrossing -> Feature.crossFeature) |
| Core.Features | Feature | `endOwningType` | subset(A_endFeature_typeWithEndFeature.typeWithEndFeature) + subset(Feature.owningType) |
| Core.Features | Feature | `featureTarget` | navigate(A_featureTarget_baseFeature -> Feature.featureTarget) |
| Core.Features | Feature | `featuringType` | navigate(A_featuringType_featureOfType -> Feature.featuringType) |
| Core.Features | Feature | `ownedCrossSubsetting` | subset(Feature.ownedSubsetting) |
| Core.Features | Feature | `ownedFeatureChaining` | subset(Element.ownedRelationship) + subset(A_source_sourceRelationship.sourceRelationship) |
| Core.Features | Feature | `ownedFeatureInverting` | subset(A_invertingFeatureInverting_featureInverted.invertingFeatureInverting) + subset(Element.ownedRelationship) |
| Core.Features | Feature | `ownedRedefinition` | subset(Feature.ownedSubsetting) |
| Core.Features | Feature | `ownedReferenceSubsetting` | subset(Feature.ownedSubsetting) |
| Core.Features | Feature | `ownedSubsetting` | subset(Type.ownedSpecialization) + subset(A_subsettingFeature_subsetting.subsetting) |
| Core.Features | Feature | `ownedTypeFeaturing` | subset(A_featureOfType_typeFeaturing.typeFeaturing) + subset(Element.ownedRelationship) |
| Core.Features | Feature | `ownedTyping` | subset(Type.ownedSpecialization) + subset(A_typing_typedFeature.typing) |
| Core.Features | Feature | `owningFeatureMembership` | subset(Element.owningMembership) |
| Core.Features | Feature | `owningType` | subset(Feature.featuringType) + subset(A_typeWithFeature_feature.typeWithFeature) + subset(Element.owningNamespace) |
| Core.Features | Feature | `type` | navigate(A_typedFeature_type -> Feature.type) |
| Core.Features | Feature | `typeWithInput` | derive(Feature.typeWithInput) |
| Core.Features | Feature | `valuation` | derive(Feature.valuation) |
| Core.Features | FeatureChaining | `featureChained` | subset(Relationship.owningRelatedElement) + redefine(Relationship.source) |
| Core.Features | FeatureInverting | `owningFeature` | subset(FeatureInverting.featureInverted) + subset(Relationship.owningRelatedElement) |
| Core.Features | FeatureMembership | `ownedMemberFeature` | redefine(OwningMembership.ownedMemberElement) |
| Core.Features | FeatureMembership | `owningType` | subset(A_featureMembership_type.type) + redefine(Membership.membershipOwningNamespace) |
| Core.Features | FeatureTyping | `owningFeature` | subset(FeatureTyping.typedFeature) + redefine(Specialization.owningType) |
| Core.Features | ReferenceSubsetting | `referencingFeature` | redefine(Subsetting.owningFeature) + redefine(Subsetting.subsettingFeature) |
| Core.Features | Subsetting | `owningFeature` | subset(Subsetting.subsettingFeature) + redefine(Specialization.owningType) |
| Core.Features | TypeFeaturing | `owningFeatureOfType` | subset(Relationship.owningRelatedElement) + subset(TypeFeaturing.featureOfType) |
| Core.Types | Conjugation | `owningType` | subset(Conjugation.conjugatedType) + subset(Relationship.owningRelatedElement) |
| Core.Types | Differencing | `typeDifferenced` | subset(Relationship.owningRelatedElement) + redefine(Relationship.source) |
| Core.Types | Disjoining | `owningType` | subset(Relationship.owningRelatedElement) + subset(Disjoining.typeDisjoined) |
| Core.Types | Intersecting | `typeIntersected` | subset(Relationship.owningRelatedElement) + redefine(Relationship.source) |
| Core.Types | Specialization | `owningType` | subset(Relationship.owningRelatedElement) + subset(Specialization.specific) |
| Core.Types | Type | `differencingType` | navigate(A_differencingType_differencedType -> Type.differencingType) |
| Core.Types | Type | `directedFeature` | subset(Type.feature) |
| Core.Types | Type | `endFeature` | subset(Type.feature) |
| Core.Types | Type | `feature` | Type.featureMembership -> FeatureMembership.ownedMemberFeature |
| Core.Types | Type | `featureMembership` | navigate(A_featureMembership_type -> Type.featureMembership) |
| Core.Types | Type | `inheritedMembership` | subset(Namespace.membership) |
| Core.Types | Type | `input` | subset(Type.directedFeature) |
| Core.Types | Type | `intersectingType` | navigate(A_intersectingType_intersectedType -> Type.intersectingType) |
| Core.Types | Type | `multiplicity` | subset(Namespace.ownedMember) |
| Core.Types | Type | `output` | subset(Type.directedFeature) |
| Core.Types | Type | `ownedConjugator` | subset(A_conjugatedType_conjugator.conjugator) + subset(Element.ownedRelationship) |
| Core.Types | Type | `ownedDifferencing` | subset(A_source_sourceRelationship.sourceRelationship) + subset(Element.ownedRelationship) |
| Core.Types | Type | `ownedDisjoining` | subset(Element.ownedRelationship) + subset(A_disjoiningTypeDisjoining_typeDisjoined.disjoiningTypeDisjoining) |
| Core.Types | Type | `ownedEndFeature` | subset(Type.endFeature) + subset(Type.ownedFeature) |
| Core.Types | Type | `ownedFeature` | subset(Namespace.ownedMember) |
| Core.Types | Type | `ownedFeatureMembership` | subset(Namespace.ownedMembership) + subset(Type.featureMembership) |
| Core.Types | Type | `ownedIntersecting` | subset(A_source_sourceRelationship.sourceRelationship) + subset(Element.ownedRelationship) |
| Core.Types | Type | `ownedSpecialization` | subset(Element.ownedRelationship) + subset(A_specific_specialization.specialization) |
| Core.Types | Type | `ownedUnioning` | subset(Element.ownedRelationship) + subset(A_source_sourceRelationship.sourceRelationship) |
| Core.Types | Type | `unioningType` | navigate(A_unioningType_unionedType -> Type.unioningType) |
| Core.Types | Unioning | `typeUnioned` | subset(Relationship.owningRelatedElement) + redefine(Relationship.source) |
| Kernel.Associations | Association | `associationEnd` | redefine(Type.endFeature) |
| Kernel.Associations | Association | `relatedType` | redefine(Relationship.relatedElement) |
| Kernel.Associations | Association | `sourceType` | subset(Association.relatedType) + redefine(Relationship.source) |
| Kernel.Associations | Association | `targetType` | subset(Association.relatedType) + redefine(Relationship.target) |
| Kernel.Associations | Association | `typedConnector` | derive(Association.typedConnector) |
| Kernel.Behaviors | Behavior | `parameter` | redefine(Type.directedFeature) |
| Kernel.Behaviors | Behavior | `step` | subset(Type.feature) -> filter(type=Step) |
| Kernel.Behaviors | Step | `behavior` | subset(Feature.type) |
| Kernel.Behaviors | Step | `parameter` | redefine(Type.directedFeature) |
| Kernel.Connectors | Connector | `association` | redefine(Feature.type) |
| Kernel.Connectors | Connector | `connectorEnd` | redefine(Type.endFeature) |
| Kernel.Connectors | Connector | `defaultFeaturingType` | navigate(A_defaultFeaturingType_featuredConnector -> Connector.defaultFeaturingType) |
| Kernel.Connectors | Connector | `relatedFeature` | redefine(Relationship.relatedElement) |
| Kernel.Connectors | Connector | `sourceFeature` | subset(Connector.relatedFeature) + redefine(Relationship.source) |
| Kernel.Connectors | Connector | `targetFeature` | subset(Connector.relatedFeature) + redefine(Relationship.target) |
| Kernel.Expressions | BooleanExpression | `predicate` | redefine(Expression.function) |
| Kernel.Expressions | Expression | `conditionedPackage` | derive(Expression.conditionedPackage) |
| Kernel.Expressions | Expression | `function` | redefine(Step.behavior) |
| Kernel.Expressions | Expression | `result` | subset(Type.output) + subset(Step.parameter) |
| Kernel.Expressions | FeatureChainExpression | `targetFeature` | subset(Namespace.member) |
| Kernel.Expressions | FeatureReferenceExpression | `referent` | subset(Namespace.member) |
| Kernel.Expressions | InstantiationExpression | `argument` | navigate(A_argument_instantiation -> InstantiationExpression.argument) |
| Kernel.Expressions | InstantiationExpression | `instantiatedType` | subset(Namespace.member) |
| Kernel.Expressions | MetadataAccessExpression | `referencedElement` | subset(Namespace.member) |
| Kernel.FeatureValues | FeatureValue | `featureWithValue` | subset(Membership.membershipOwningNamespace) |
| Kernel.FeatureValues | FeatureValue | `value` | redefine(OwningMembership.ownedMemberElement) |
| Kernel.Functions | Function | `expression` | subset(Behavior.step) |
| Kernel.Functions | Function | `result` | subset(Type.output) + subset(Behavior.parameter) |
| Kernel.Functions | ParameterMembership | `ownedMemberParameter` | redefine(FeatureMembership.ownedMemberFeature) |
| Kernel.Functions | ResultExpressionMembership | `ownedResultExpression` | redefine(FeatureMembership.ownedMemberFeature) |
| Kernel.Interactions | Flow | `flowEnd` | subset(Connector.connectorEnd) |
| Kernel.Interactions | Flow | `interaction` | redefine(Connector.association) + redefine(Step.behavior) |
| Kernel.Interactions | Flow | `payloadFeature` | subset(Type.ownedFeature) |
| Kernel.Interactions | Flow | `payloadType` | navigate(A_payloadType_flowForPayloadType -> Flow.payloadType) |
| Kernel.Interactions | Flow | `sourceOutputFeature` | navigate(A_sourceOutputFeature_flowFromOutput -> Flow.sourceOutputFeature) |
| Kernel.Interactions | Flow | `targetInputFeature` | navigate(A_targetInputFeature_flowToInput -> Flow.targetInputFeature) |
| Kernel.Interactions | FlowEnd | `featuringFlow` | derive(FlowEnd.featuringFlow) |
| Kernel.Metadata | MetadataFeature | `metaclass` | subset(Feature.type) |
| Kernel.Packages | ElementFilterMembership | `condition` | redefine(OwningMembership.ownedMemberElement) |
| Kernel.Packages | Package | `filterCondition` | subset(Namespace.ownedMember) |
| Root.Annotations | AnnotatingElement | `annotation` | subset(A_source_sourceRelationship.sourceRelationship) |
| Root.Annotations | AnnotatingElement | `ownedAnnotatingRelationship` | subset(AnnotatingElement.annotation) + subset(Element.ownedRelationship) |
| Root.Annotations | AnnotatingElement | `owningAnnotatingRelationship` | subset(Element.owningRelationship) + subset(AnnotatingElement.annotation) |
| Root.Annotations | Annotation | `annotatingElement` | redefine(Relationship.source) |
| Root.Annotations | Annotation | `ownedAnnotatingElement` | subset(Annotation.annotatingElement) + subset(Relationship.ownedRelatedElement) |
| Root.Annotations | Annotation | `owningAnnotatedElement` | subset(Annotation.annotatedElement) + subset(Relationship.owningRelatedElement) |
| Root.Annotations | Annotation | `owningAnnotatingElement` | subset(Annotation.annotatingElement) + subset(Relationship.owningRelatedElement) |
| Root.Annotations | TextualRepresentation | `representedElement` | subset(Element.owner) + redefine(AnnotatingElement.annotatedElement) |
| Root.Elements | Import | `importOwningNamespace` | subset(Relationship.owningRelatedElement) + redefine(Relationship.source) |
| Root.Elements | Import | `importedElement` | navigate(A_importedElement_membershipImport -> Import.importedElement) |
| Root.Elements | KerMLModelElement (`Element` dans `spec`) | `ownedAnnotation` | derive(KerMLModelElement.ownedAnnotation) |
| Root.Elements | KerMLModelElement (`Element` dans `spec`) | `ownedElement` | derive(KerMLModelElement.ownedElement) |
| Root.Elements | KerMLModelElement (`Element` dans `spec`) | `owner` | derive(KerMLModelElement.owner) |
| Root.Elements | KerMLModelElement (`Element` dans `spec`) | `owningMembership` | derive(KerMLModelElement.owningMembership) |
| Root.Elements | KerMLModelElement (`Element` dans `spec`) | `owningNamespace` | derive(KerMLModelElement.owningNamespace) |
| Root.Elements | KerMLModelElement (`Element` dans `spec`) | `textualRepresentation` | derive(KerMLModelElement.textualRepresentation) |
| Root.Elements | Relationship | `relatedElement` | navigate(A_relatedElement_relationship -> Relationship.relatedElement) |
| Root.Namespaces | Membership | `membershipOwningNamespace` | subset(A_membership_membershipNamespace.membershipNamespace) + subset(Relationship.owningRelatedElement) + redefine(Relationship.source) |
| Root.Namespaces | Namespace | `import` | derive(Namespace.import) |
| Root.Namespaces | Namespace | `importedMembership` | subset(Namespace.membership) |
| Root.Namespaces | Namespace | `member` | Namespace.membership -> Membership.memberElement |
| Root.Namespaces | Namespace | `membership` | union(Namespace.ownedMembership, Namespace.importedMembership) |
| Root.Namespaces | Namespace | `ownedImport` | subset(Element.ownedRelationship) + subset(A_source_sourceRelationship.sourceRelationship) |
| Root.Namespaces | Namespace | `ownedMember` | subset(Namespace.member) |
| Root.Namespaces | Namespace | `ownedMembership` | subset(Namespace.membership) + subset(A_source_sourceRelationship.sourceRelationship) + subset(Element.ownedRelationship) |
| Root.Namespaces | OwningMembership | `ownedMemberElement` | subset(Relationship.ownedRelatedElement) + redefine(Membership.memberElement) |

#### 7.2.2 SysML

| Package normatif | Classe propriétaire | Propriété dérivée | Relation normative / calcul proposé |
|---|---|---|---|
| Systems.Actions | AcceptActionUsage | `payloadParameter` | subset(Usage.nestedReference) + subset(KerML::Step.parameter) |
| Systems.Actions | ActionDefinition | `action` | subset(KerML::Behavior.step) + subset(Definition.usage) |
| Systems.Actions | ForLoopActionUsage | `loopVariable` | navigate(A_loopVariable_forLoopAction -> ForLoopActionUsage.loopVariable) |
| Systems.Actions | IfActionUsage | `elseAction` | navigate(A_elseAction_ifElseAction -> IfActionUsage.elseAction) |
| Systems.Actions | IfActionUsage | `thenAction` | navigate(A_thenAction_ifThenAction -> IfActionUsage.thenAction) |
| Systems.Actions | LoopActionUsage | `bodyAction` | navigate(A_bodyAction_loopAction -> LoopActionUsage.bodyAction) |
| Systems.Actions | PerformActionUsage | `performedAction` | redefine(EventOccurrenceUsage.eventOccurrence) |
| Systems.Allocations | AllocationDefinition | `allocation` | subset(Definition.usage) |
| Systems.Allocations | AllocationDefinition | `definedAllocation` | derive(AllocationDefinition.definedAllocation) |
| Systems.Allocations | AllocationUsage | `allocationDefinition` | redefine(ConnectionUsage.connectionDefinition) |
| Systems.AnalysisCases | AnalysisCaseUsage | `analysisCaseDefinition` | redefine(CaseUsage.caseDefinition) |
| Systems.Calculations | CalculationDefinition | `calculation` | subset(ActionDefinition.action) + subset(KerML::Function.expression) |
| Systems.Calculations | CalculationUsage | `calculationOwningDefinition` | derive(CalculationUsage.calculationOwningDefinition) |
| Systems.Cases | CaseDefinition | `actorParameter` | subset(KerML::Behavior.parameter) + subset(Definition.usage) |
| Systems.Cases | CaseDefinition | `objectiveRequirement` | subset(Definition.usage) |
| Systems.Cases | CaseDefinition | `subjectParameter` | subset(KerML::Behavior.parameter) + subset(Definition.usage) |
| Systems.Cases | CaseUsage | `actorParameter` | subset(KerML::Step.parameter) + subset(Usage.usage) |
| Systems.Cases | CaseUsage | `caseDefinition` | redefine(CalculationUsage.calculationDefinition) |
| Systems.Cases | CaseUsage | `caseOwningUsage` | derive(CaseUsage.caseOwningUsage) |
| Systems.Cases | CaseUsage | `objectiveRequirement` | subset(Usage.usage) |
| Systems.Cases | CaseUsage | `subjectParameter` | subset(KerML::Step.parameter) + subset(Usage.usage) |
| Systems.Cases | ObjectiveMembership | `ownedObjectiveRequirement` | redefine(KerML::FeatureMembership.ownedMemberFeature) |
| Systems.Connections | ConnectionDefinition | `connectionEnd` | redefine(KerML::Association.associationEnd) |
| Systems.Constraints | AssertConstraintUsage | `assertedConstraint` | navigate(A_assertedConstraint_constraintAssertion -> AssertConstraintUsage.assertedConstraint) |
| Systems.Constraints | ConstraintUsage | `constraintAssertion` | derive(ConstraintUsage.constraintAssertion) |
| Systems.DefinitionAndUsage | Definition | `directedUsage` | subset(KerML::Type.directedFeature) + subset(Definition.usage) |
| Systems.DefinitionAndUsage | Definition | `ownedAction` | subset(Definition.ownedOccurrence) |
| Systems.DefinitionAndUsage | Definition | `ownedAllocation` | subset(Definition.ownedConnection) |
| Systems.DefinitionAndUsage | Definition | `ownedAnalysisCase` | subset(Definition.ownedCase) |
| Systems.DefinitionAndUsage | Definition | `ownedAttribute` | subset(Definition.ownedUsage) |
| Systems.DefinitionAndUsage | Definition | `ownedCalculation` | subset(Definition.ownedAction) |
| Systems.DefinitionAndUsage | Definition | `ownedCase` | subset(Definition.ownedCalculation) |
| Systems.DefinitionAndUsage | Definition | `ownedConcern` | subset(Definition.ownedRequirement) |
| Systems.DefinitionAndUsage | Definition | `ownedConnection` | subset(Definition.ownedUsage) |
| Systems.DefinitionAndUsage | Definition | `ownedConstraint` | subset(Definition.ownedOccurrence) |
| Systems.DefinitionAndUsage | Definition | `ownedEnumeration` | subset(Definition.ownedAttribute) |
| Systems.DefinitionAndUsage | Definition | `ownedFlow` | subset(Definition.ownedConnection) |
| Systems.DefinitionAndUsage | Definition | `ownedInterface` | subset(Definition.ownedConnection) |
| Systems.DefinitionAndUsage | Definition | `ownedItem` | subset(Definition.ownedOccurrence) |
| Systems.DefinitionAndUsage | Definition | `ownedOccurrence` | subset(Definition.ownedUsage) |
| Systems.DefinitionAndUsage | Definition | `ownedPart` | subset(Definition.ownedItem) |
| Systems.DefinitionAndUsage | Definition | `ownedPort` | subset(Definition.ownedUsage) |
| Systems.DefinitionAndUsage | Definition | `ownedReference` | subset(Definition.ownedUsage) |
| Systems.DefinitionAndUsage | Definition | `ownedRendering` | subset(Definition.ownedPart) |
| Systems.DefinitionAndUsage | Definition | `ownedRequirement` | subset(Definition.ownedConstraint) |
| Systems.DefinitionAndUsage | Definition | `ownedState` | subset(Definition.ownedAction) |
| Systems.DefinitionAndUsage | Definition | `ownedTransition` | subset(Definition.ownedUsage) |
| Systems.DefinitionAndUsage | Definition | `ownedUsage` | subset(KerML::Type.ownedFeature) + subset(Definition.usage) |
| Systems.DefinitionAndUsage | Definition | `ownedUseCase` | subset(Definition.ownedCase) |
| Systems.DefinitionAndUsage | Definition | `ownedVerificationCase` | subset(Definition.ownedCase) |
| Systems.DefinitionAndUsage | Definition | `ownedView` | subset(Definition.ownedPart) |
| Systems.DefinitionAndUsage | Definition | `ownedViewpoint` | subset(Definition.ownedRequirement) |
| Systems.DefinitionAndUsage | Definition | `usage` | subset(KerML::Type.feature) |
| Systems.DefinitionAndUsage | Definition | `variant` | subset(KerML::Namespace.ownedMember) |
| Systems.DefinitionAndUsage | Definition | `variantMembership` | subset(KerML::Namespace.ownedMembership) |
| Systems.DefinitionAndUsage | ReferenceUsage | `forLoopAction` | derive(ReferenceUsage.forLoopAction) |
| Systems.DefinitionAndUsage | ReferenceUsage | `owningAcceptActionUsage` | derive(ReferenceUsage.owningAcceptActionUsage) |
| Systems.DefinitionAndUsage | Usage | `directedUsage` | subset(KerML::Type.directedFeature) + subset(Usage.usage) |
| Systems.DefinitionAndUsage | Usage | `flowDefinitionWithEnd` | derive(Usage.flowDefinitionWithEnd) |
| Systems.DefinitionAndUsage | Usage | `nestedAction` | subset(Usage.nestedOccurrence) |
| Systems.DefinitionAndUsage | Usage | `nestedAllocation` | subset(Usage.nestedConnection) |
| Systems.DefinitionAndUsage | Usage | `nestedAnalysisCase` | subset(Usage.nestedCase) |
| Systems.DefinitionAndUsage | Usage | `nestedAttribute` | subset(Usage.nestedUsage) |
| Systems.DefinitionAndUsage | Usage | `nestedCalculation` | subset(Usage.nestedAction) |
| Systems.DefinitionAndUsage | Usage | `nestedCase` | subset(Usage.nestedCalculation) |
| Systems.DefinitionAndUsage | Usage | `nestedConcern` | subset(Usage.nestedRequirement) |
| Systems.DefinitionAndUsage | Usage | `nestedConnection` | subset(Usage.nestedUsage) |
| Systems.DefinitionAndUsage | Usage | `nestedConstraint` | subset(Usage.nestedOccurrence) |
| Systems.DefinitionAndUsage | Usage | `nestedEnumeration` | subset(Usage.nestedAttribute) |
| Systems.DefinitionAndUsage | Usage | `nestedFlow` | subset(Usage.nestedConnection) |
| Systems.DefinitionAndUsage | Usage | `nestedInterface` | subset(Usage.nestedConnection) |
| Systems.DefinitionAndUsage | Usage | `nestedItem` | subset(Usage.nestedOccurrence) |
| Systems.DefinitionAndUsage | Usage | `nestedOccurrence` | subset(Usage.nestedUsage) |
| Systems.DefinitionAndUsage | Usage | `nestedPart` | subset(Usage.nestedItem) |
| Systems.DefinitionAndUsage | Usage | `nestedPort` | subset(Usage.nestedUsage) |
| Systems.DefinitionAndUsage | Usage | `nestedReference` | subset(Usage.nestedUsage) |
| Systems.DefinitionAndUsage | Usage | `nestedRendering` | subset(Usage.nestedPart) |
| Systems.DefinitionAndUsage | Usage | `nestedRequirement` | subset(Usage.nestedConstraint) |
| Systems.DefinitionAndUsage | Usage | `nestedState` | subset(Usage.nestedAction) |
| Systems.DefinitionAndUsage | Usage | `nestedTransition` | subset(Usage.nestedUsage) |
| Systems.DefinitionAndUsage | Usage | `nestedUsage` | subset(KerML::Type.ownedFeature) + subset(Usage.usage) |
| Systems.DefinitionAndUsage | Usage | `nestedUseCase` | subset(Usage.nestedCase) |
| Systems.DefinitionAndUsage | Usage | `nestedVerificationCase` | subset(Usage.nestedCase) |
| Systems.DefinitionAndUsage | Usage | `nestedView` | subset(Usage.nestedPart) |
| Systems.DefinitionAndUsage | Usage | `nestedViewpoint` | subset(Usage.nestedRequirement) |
| Systems.DefinitionAndUsage | Usage | `owningDefinition` | subset(KerML::Feature.owningType) + subset(A_usage_featuringDefinition.featuringDefinition) |
| Systems.DefinitionAndUsage | Usage | `owningUsage` | subset(KerML::Feature.owningType) |
| Systems.DefinitionAndUsage | Usage | `usage` | subset(KerML::Type.feature) |
| Systems.DefinitionAndUsage | Usage | `variant` | subset(KerML::Namespace.ownedMember) |
| Systems.DefinitionAndUsage | Usage | `variantMembership` | subset(KerML::Namespace.ownedMembership) |
| Systems.DefinitionAndUsage | VariantMembership | `ownedVariantUsage` | redefine(KerML::OwningMembership.ownedMemberElement) |
| Systems.Enumerations | EnumerationDefinition | `enumeratedValue` | redefine(Definition.variant) |
| Systems.Enumerations | EnumerationUsage | `enumerationDefinition` | redefine(AttributeUsage.attributeDefinition) |
| Systems.Flows | FlowDefinition | `flowEnd` | redefine(KerML::Association.associationEnd) |
| Systems.Interfaces | InterfaceDefinition | `interfaceEnd` | redefine(ConnectionDefinition.connectionEnd) |
| Systems.Interfaces | InterfaceUsage | `interfaceDefinition` | redefine(ConnectionUsage.connectionDefinition) |
| Systems.Interfaces | InterfaceUsage | `interfaceOwningDefinition` | derive(InterfaceUsage.interfaceOwningDefinition) |
| Systems.Occurrences | EventOccurrenceUsage | `eventOccurrence` | navigate(A_eventOccurrence_referencingOccurrence -> EventOccurrenceUsage.eventOccurrence) |
| Systems.Occurrences | OccurrenceUsage | `individualDefinition` | subset(OccurrenceUsage.occurrenceDefinition) |
| Systems.Occurrences | OccurrenceUsage | `referencingOccurrence` | derive(OccurrenceUsage.referencingOccurrence) |
| Systems.Parts | PartUsage | `partDefinition` | subset(ItemUsage.itemDefinition) |
| Systems.Ports | ConjugatedPortDefinition | `originalPortDefinition` | redefine(KerML::Element.owningNamespace) |
| Systems.Ports | ConjugatedPortDefinition | `ownedPortConjugator` | redefine(KerML::Type.ownedConjugator) |
| Systems.Ports | ConjugatedPortTyping | `portDefinition` | navigate(A_portDefinition_conjugatedPortTyping -> ConjugatedPortTyping.portDefinition) |
| Systems.Ports | PortConjugation | `conjugatedPortDefinition` | redefine(KerML::Conjugation.owningType) |
| Systems.Ports | PortDefinition | `conjugatedPortDefinition` | subset(KerML::Namespace.ownedMember) |
| Systems.Ports | PortUsage | `interfaceDefinitionWithEnd` | derive(PortUsage.interfaceDefinitionWithEnd) |
| Systems.Ports | PortUsage | `portDefinition` | redefine(OccurrenceUsage.occurrenceDefinition) |
| Systems.Requirements | ActorMembership | `ownedActorParameter` | redefine(KerML::ParameterMembership.ownedMemberParameter) |
| Systems.Requirements | ConcernUsage | `concernDefinition` | redefine(RequirementUsage.requirementDefinition) |
| Systems.Requirements | ConcernUsage | `framingRequirementDefinition` | derive(ConcernUsage.framingRequirementDefinition) |
| Systems.Requirements | FramedConcernMembership | `ownedConcern` | redefine(RequirementConstraintMembership.ownedConstraint) |
| Systems.Requirements | FramedConcernMembership | `referencedConcern` | redefine(RequirementConstraintMembership.referencedConstraint) |
| Systems.Requirements | RequirementConstraintMembership | `ownedConstraint` | redefine(KerML::FeatureMembership.ownedMemberFeature) |
| Systems.Requirements | RequirementConstraintMembership | `referencedConstraint` | navigate(A_referencedConstraint_referencingConstraintMembership -> RequirementConstraintMembership.referencedConstraint) |
| Systems.Requirements | RequirementDefinition | `actorParameter` | subset(KerML::Behavior.parameter) + subset(Definition.usage) |
| Systems.Requirements | RequirementDefinition | `assumedConstraint` | subset(KerML::Type.ownedFeature) |
| Systems.Requirements | RequirementDefinition | `definedRequirement` | derive(RequirementDefinition.definedRequirement) |
| Systems.Requirements | RequirementDefinition | `framedConcern` | subset(RequirementDefinition.requiredConstraint) |
| Systems.Requirements | RequirementDefinition | `requiredConstraint` | subset(KerML::Type.ownedFeature) |
| Systems.Requirements | RequirementDefinition | `stakeholderParameter` | subset(KerML::Behavior.parameter) + subset(Definition.usage) |
| Systems.Requirements | RequirementDefinition | `subjectParameter` | subset(KerML::Behavior.parameter) + subset(Definition.usage) |
| Systems.Requirements | RequirementUsage | `actorParameter` | subset(KerML::Step.parameter) + subset(Usage.usage) |
| Systems.Requirements | RequirementUsage | `assumedConstraint` | subset(KerML::Type.ownedFeature) |
| Systems.Requirements | RequirementUsage | `framedConcern` | subset(RequirementUsage.requiredConstraint) |
| Systems.Requirements | RequirementUsage | `requiredConstraint` | subset(KerML::Type.ownedFeature) |
| Systems.Requirements | RequirementUsage | `requirementDefinition` | redefine(ConstraintUsage.constraintDefinition) |
| Systems.Requirements | RequirementUsage | `stakeholderParameter` | subset(KerML::Step.parameter) + subset(Usage.usage) |
| Systems.Requirements | RequirementUsage | `subjectParameter` | subset(KerML::Step.parameter) + subset(Usage.usage) |
| Systems.Requirements | SatisfyRequirementUsage | `satisfiedRequirement` | redefine(AssertConstraintUsage.assertedConstraint) |
| Systems.Requirements | StakeholderMembership | `ownedStakeholderParameter` | redefine(KerML::ParameterMembership.ownedMemberParameter) |
| Systems.Requirements | SubjectMembership | `ownedSubjectParameter` | redefine(KerML::ParameterMembership.ownedMemberParameter) |
| Systems.States | ExhibitStateUsage | `exhibitedState` | redefine(PerformActionUsage.performedAction) |
| Systems.States | StateDefinition | `doAction` | navigate(A_doAction_activeStateDefintion -> StateDefinition.doAction) |
| Systems.States | StateDefinition | `entryAction` | navigate(A_entryAction_enteredStateDefinition -> StateDefinition.entryAction) |
| Systems.States | StateDefinition | `exitAction` | navigate(A_exitAction_exitedStateDefinition -> StateDefinition.exitAction) |
| Systems.States | StateDefinition | `state` | subset(ActionDefinition.action) |
| Systems.States | StateSubactionMembership | `action` | redefine(KerML::FeatureMembership.ownedMemberFeature) |
| Systems.States | StateUsage | `doAction` | navigate(A_doAction_activeState -> StateUsage.doAction) |
| Systems.States | StateUsage | `entryAction` | navigate(A_entryAction_enteredState -> StateUsage.entryAction) |
| Systems.States | StateUsage | `exitAction` | navigate(A_exitAction_exitedState -> StateUsage.exitAction) |
| Systems.States | TransitionUsage | `effectAction` | subset(KerML::Type.feature) |
| Systems.States | TransitionUsage | `source` | navigate(A_source_outgoingTransition -> TransitionUsage.source) |
| Systems.States | TransitionUsage | `target` | navigate(A_target_incomingTransition -> TransitionUsage.target) |
| Systems.States | TransitionUsage | `triggerAction` | subset(KerML::Type.ownedFeature) |
| Systems.UseCases | IncludeUseCaseUsage | `useCaseIncluded` | redefine(PerformActionUsage.performedAction) |
| Systems.UseCases | UseCaseDefinition | `includedUseCase` | navigate(A_includedUseCase_includingUseCaseDefinition -> UseCaseDefinition.includedUseCase) |
| Systems.UseCases | UseCaseUsage | `includedUseCase` | navigate(A_includedUseCase_includingUseCase -> UseCaseUsage.includedUseCase) |
| Systems.UseCases | UseCaseUsage | `useCaseDefinition` | redefine(CaseUsage.caseDefinition) |
| Systems.VerificationCases | RequirementVerificationMembership | `ownedRequirement` | redefine(RequirementConstraintMembership.ownedConstraint) |
| Systems.VerificationCases | RequirementVerificationMembership | `verifiedRequirement` | redefine(RequirementConstraintMembership.referencedConstraint) |
| Systems.VerificationCases | VerificationCaseDefinition | `verifiedRequirement` | navigate(A_verifiedRequirement_verifyingCaseDefinition -> VerificationCaseDefinition.verifiedRequirement) |
| Systems.VerificationCases | VerificationCaseUsage | `verificationCaseDefinition` | subset(CaseUsage.caseDefinition) |
| Systems.VerificationCases | VerificationCaseUsage | `verifiedRequirement` | navigate(A_verifiedRequirement_verifyingCase -> VerificationCaseUsage.verifiedRequirement) |
| Systems.Views | RenderingDefinition | `rendering` | subset(Definition.usage) |
| Systems.Views | RenderingUsage | `renderingDefinition` | redefine(PartUsage.partDefinition) |
| Systems.Views | RenderingUsage | `viewRenderingMembership` | derive(RenderingUsage.viewRenderingMembership) |
| Systems.Views | ViewDefinition | `satisfiedViewpoint` | subset(Definition.ownedRequirement) |
| Systems.Views | ViewDefinition | `view` | subset(Definition.usage) |
| Systems.Views | ViewDefinition | `viewRendering` | navigate(A_viewRendering_renderingOwningViewDefinition -> ViewDefinition.viewRendering) |
| Systems.Views | ViewRenderingMembership | `ownedRendering` | redefine(KerML::FeatureMembership.ownedMemberFeature) |
| Systems.Views | ViewRenderingMembership | `referencedRendering` | navigate(A_referencedRendering_referencingRenderingMembership -> ViewRenderingMembership.referencedRendering) |
| Systems.Views | ViewUsage | `satisfiedViewpoint` | subset(Usage.nestedRequirement) |
| Systems.Views | ViewUsage | `viewDefinition` | redefine(PartUsage.partDefinition) |
| Systems.Views | ViewUsage | `viewRendering` | navigate(A_viewRendering_renderingOwningView -> ViewUsage.viewRendering) |
| Systems.Views | ViewpointDefinition | `viewpointStakeholder` | navigate(A_viewpointStakeholder_viewpointDefinitionForStakeholder -> ViewpointDefinition.viewpointStakeholder) |
| Systems.Views | ViewpointUsage | `viewpointDefinition` | redefine(RequirementUsage.requirementDefinition) |
| Systems.Views | ViewpointUsage | `viewpointStakeholder` | navigate(A_viewpointStakeholder_viewpointForStakeholder -> ViewpointUsage.viewpointStakeholder) |




### 7.3 Points de discussion

1. Quels noms définitifs retenir pour les stéréotypes `DerivedComputed`, `DerivedSubset` et `DerivedRedefinition` ?
2. Quels langages et formes de calcul SemGen doit-il accepter dans `calculationExpression` : OCL, navigation typée, opération Java ou combinaison contrôlée ?
3. Comment représenter plusieurs `subsettedProperty` ou `redefinedProperty` tout en conservant une expression de calcul non ambiguë ?
4. Quelle règle de validation doit empêcher la génération d'un champ Java lorsqu'une propriété porte `isDerived=true` ?
5. Quel contrat doit fournir la bibliothèque commune de navigation hors SemGen pour `Behavior.step`, les memberships importées, l'héritage et les imports récursifs ?
6. Quels tests d'instances et de mutations doivent garantir que cette bibliothèque restitue les vues dérivées sans stockage secondaire ?
7. Quelles sont les cinq expressions de calcul normatives à formaliser en priorité pour les attributs scalaires dérivés ?

**Sources de vérification :** XMI OMG KerML 1.0 / SysML 2.0 (édition 2025-02-01) dans `specs/omg-xmi/`, notamment les déclarations `isDerived`, `subsettedProperty`, `redefinedProperty` et les expressions OCL associées. La liste des 291 rôles est utilisée ici comme périmètre normatif à annoter; la proposition SemGen et la règle d'indépendance KerML restent à implémenter et à valider par génération Java, tests d'instances et contrôle des dépendances de packages.