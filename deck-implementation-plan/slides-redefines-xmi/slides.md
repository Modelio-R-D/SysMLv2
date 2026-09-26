---
marp: true
theme: docaposte
paginate: true
style: |
  section.dense table { font-size: 14px; line-height: 1.15; }
  section.dense th, section.dense td { padding: 2px 6px; }
  section.xdense table { font-size: 11.5px; line-height: 1.1; }
  section.xdense th, section.xdense td { padding: 1px 5px; }
---

<!-- _class: title -->

# Dérivation, sous-ensembles et redéfinitions

## Ce que les XMI normatifs expriment, et ce que la greffe Modelio peut en porter

À partir des XMI normatifs OMG · édition du 1er février 2025

---

<!-- _class: "section theme-mint" -->

# Partie 1

## Les trois mécanismes normatifs

---

# Trois relations différentes coexistent dans le métamodèle

| Marqueur XMI | Question sémantique | Ce qu'il exprime |
|---|---|---|
| `isDerived="true"` | Comment obtenir la valeur ? | La propriété est calculée plutôt que décrite comme valeur indépendante. |
| `<subsettedProperty>` | À quel ensemble appartient-elle ? | Les valeurs de la propriété sont contraintes par une propriété plus générale. |
| `<redefinedProperty>` | Quelle propriété héritée est spécialisée ? | Une propriété redéclare un contrat hérité, éventuellement plus étroit. |

Ces marqueurs peuvent se combiner. Aucun ne doit être déduit automatiquement des deux autres.

<div class="takeaway">« Dérivé », « sous-ensemble » et « redéfini » ne sont pas trois noms pour le même mécanisme.</div>

---

# `isDerived` dit que la valeur est une vue calculée

En KerML, les valeurs de `Type.feature` sont les propriétés de `Namespace.member` qui sont des `Feature` :

```text
Namespace.member : Element, zéro à plusieurs
Type.feature       : Feature, zéro à plusieurs  {derived, subset member}
```

Le rôle spécialisé se calcule à partir d'un contenu plus général ; il n'introduit pas, par définition, une seconde source de vérité.

<div class="takeaway">Une propriété dérivée peut être une projection filtrée, une union, ou un autre résultat défini par la sémantique du métamodèle.</div>

<!-- footer: OMG, KerML v1.0 XMI (2025-02-01), Type.feature -->
<!-- footer: "" -->

---

# `subsettedProperty` contraint les valeurs, pas leur mode de calcul

Le lien XMI exprime une inclusion d'ensembles de valeurs : les valeurs de `P` sont incluses dans celles de `Q`.

En KerML, `Relationship.source` et `Relationship.target` sont des sous-ensembles de `Relationship.relatedElement`. Ces extrémités sont déclarées comme propriétés non dérivées : leur appartenance à un sous-ensemble ne les rend pas automatiquement calculées.

```text
Relationship.relatedElement : Element, zéro à plusieurs
Relationship.source         : Element, zéro à plusieurs  {subset relatedElement}
Relationship.target         : Element, zéro à plusieurs  {subset relatedElement}
```

<div class="takeaway">Le sous-ensemble porte une contrainte d'appartenance. `isDerived` porte une information distincte sur la dérivation.</div>

<!-- footer: OMG, KerML v1.0 XMI (2025-02-01), Relationship.source/target -->
<!-- footer: "" -->

---

# Les XMI combinent souvent dérivation et sous-ensemble

| Métamodèle | Déclarations de propriété | Dérivées | Avec au moins un sous-ensemble | Les deux |
|---|---:|---:|---:|---:|
| KerML 1.0 | 313 | 199 | 166 | 128 |
| SysML 2.0 | 402 | 373 | 248 | 241 |

Il s'agit de comptages des déclarations XMI. Une propriété peut avoir plusieurs liens `subsettedProperty` : 207 liens KerML et 285 liens SysML.

KerML contient aussi **71 propriétés dérivées sans sous-ensemble** et **38 propriétés sous-ensembles non dérivées**. En SysML, on en compte respectivement **132** et **7**.

<div class="takeaway">Les annotations se recouvrent fortement, mais ne sont pas équivalentes : des propriétés sont dérivées sans sous-ensemble, et d'autres sous-ensembles ne sont pas dérivés.</div>

<!-- footer: Comptage direct des XMI OMG KerML 1.0 et SysML 2.0 (2025-02-01) -->
<!-- footer: "" -->

---

# KerML construit des vues de plus en plus spécialisées

<div class="two-col">
<div>

## Contenu général

`Namespace.member` fournit les membres d'un espace de noms.

`Type.feature` sélectionne les membres qui sont des `Feature` :

- dérivé ;
- sous-ensemble de `Namespace.member` ;
- type de valeur plus précis.

</div>
<div>

## Vue comportementale

`Behavior.step` sélectionne les features qui sont des `Step` :

- dérivé ;
- sous-ensemble de `Type.feature` ;
- à son tour, plus spécialisé par son type.

```text
Namespace.member
  ⊇ Type.feature
       ⊇ Behavior.step
```

</div>
</div>

Le générateur doit préserver ces relations de vue sans créer une copie indépendante du même contenu à chaque niveau.

<!-- footer: OMG, KerML v1.0 XMI, Type.feature et Behavior.step -->
<!-- footer: "" -->

---

# SysML organise les usages par sous-ensembles typés

Dans `Definition`, plusieurs propriétés dérivées découpent les usages par rôle :

```text
usage [Usage]
└── ownedUsage [Usage]
    ├── ownedOccurrence [OccurrenceUsage]
    │   ├── ownedAction [ActionUsage]
    │   └── ownedItem [ItemUsage]
    │       └── ownedPart [PartUsage]
    └── ...
```

Chaque sous-ensemble spécialisé précise le type des valeurs et réutilise le contenu du rôle plus général. Par exemple, `Definition.ownedAction` sous-ensemble `Definition.ownedOccurrence` ; `Definition.ownedPart` sous-ensemble `Definition.ownedItem`.

<div class="takeaway">Ces propriétés SysML sont des vues structurées du contenu de <code>Definition</code>, pas des listes indépendantes à synchroniser.</div>

<!-- footer: OMG, SysML v2.0 XMI, Definition.ownedUsage / ownedOccurrence / ownedAction / ownedItem / ownedPart -->
<!-- footer: "" -->

---

# `redefines` est un axe distinct, parfois combiné aux deux autres

Exemple SysML : `RequirementConstraintMembership.ownedConstraint` est :

- **dérivée** (`isDerived="true"`) ;
- **redéfinie** (`redefinedProperty` vers `FeatureMembership.ownedMemberFeature`) ;
- typée plus précisément `ConstraintUsage` plutôt que `Feature`.

Mais elle n'a pas besoin d'être sous-ensemble pour être dérivée ou redéfinie. Dans les deux XMI, `redefinedProperty` apparaît sur 79 liens KerML et 70 liens SysML ; c'est un lien séparé de `subsettedProperty`.

<div class="takeaway">Traiter séparément calcul, inclusion de valeurs et spécialisation héritée ; ensuite seulement appliquer leurs contraintes combinées.</div>

<!-- footer: OMG, SysML v2.0 XMI, RequirementConstraintMembership.ownedConstraint -->
<!-- footer: "" -->

---

# La composition ajoute encore une contrainte sémantique

SysML redéfinit `FeatureMembership.ownedMemberFeature : Feature [1]` par `RequirementConstraintMembership.ownedConstraint : ConstraintUsage [1]`.

Une règle OCL impose en plus :

```text
ownedConstraint.isComposite
```

KerML définit `Feature.isComposite` avec des effets sur le cycle de vie et l'exclusivité d'appartenance. La contrainte de composition ne découle ni de `isDerived` ni de `subsettedProperty`.

<div class="takeaway">Dans ces XMI, cette règle passe par <code>Feature.isComposite</code> et OCL, pas par un changement d'attribut UML <code>aggregation</code>.</div>

<!-- footer: OMG, KerML v1.0 XMI, Feature.isComposite ; SysML v2.0 XMI, RequirementConstraintMembership -->
<!-- footer: "" -->

---

<!-- _class: "section theme-poussin" -->

# Partie 2

## Ce qu'une génération fidèle doit préserver

---

# Séparer stockage, vues et contraintes

| Élément normatif | Décision de génération à vérifier |
|---|---|
| Propriété canonique stockée | Où se trouve l'unique source de vérité ? |
| Propriété `isDerived` | Quel calcul ou filtre produit sa valeur ? |
| Lien `subsettedProperty` | Comment la vue garantit-elle l'inclusion dans le rôle parent ? |
| Lien `redefinedProperty` | Quelles contraintes de type et de cardinalité sont resserrées ? |
| Règle OCL telle que `isComposite` | Où et sur quels chemins d'écriture la contrainte est-elle appliquée ? |

Les écritures inverses et les accesseurs hérités comptent aussi : valider uniquement le getter spécialisé ne garantit pas l'invariant.

---

# Une même valeur logique, plusieurs vues cohérentes

<div class="two-col">
<div>

## À éviter

- un champ par nom de propriété ;
- des listes redondantes pour chaque sous-ensemble ;
- une synchronisation implicite entre stockage parent et vues filles.

</div>
<div>

## À préserver

- le stockage canonique unique quand la norme décrit le même contenu ;
- les accesseurs dérivés et typés propres à chaque métaclasse ;
- les contraintes de sous-ensemble, redéfinition et composition.

</div>
</div>

<div class="takeaway">Générer les vues spécialisées sans perdre les contraintes, et sans transformer une relation logique en stockage dupliqué.</div>

---

<!-- _class: "section theme-coral" -->

# Partie 3

## Ce que nous ne pouvons pas exprimer aujourd'hui

---

# La règle d'indépendance de KerML

<div class="two-col">
<div>

## Le principe

KerML est la couche fondation. SysML est construit par-dessus.

<div class="box">
Une classe KerML ne doit <strong>jamais</strong> référencer une classe SysML. L'inverse est normal et attendu.
</div>

</div>
<div>

## Où ça coince

Dans la norme, 32 relations reliant une classe SysML à une classe KerML déclarent aussi leur <strong>navigation inverse</strong>, qui est portée par la classe KerML.

<div class="box y">
Exemple : <code>AttributeUsage.attributeDefinition : DataType</code> a pour inverse <code>DataType.definedAttribute : AttributeUsage</code> — une classe KerML qui pointe vers une classe SysML.
</div>

</div>
</div>

<div class="takeaway">Le sens « utile » de la relation est légitime. C'est son inverse, déclaré par la norme, qui viole l'indépendance de KerML.</div>

---

# Pourquoi retirer un bout force à retirer l'autre

<div class="two-col">
<div>

## La contrainte Modelio

Une association a toujours ses deux extrémités possédées par les deux classes reliées — règle `E211`.

<div class="box p">
Impossible de garder le bout SysML et de supprimer seulement le bout KerML : Modelio refuse structurellement une association à un seul bout.
</div>

</div>
<div>

## La conséquence

Supprimer le bout interdit supprime aussi le bout légitime.

<div class="box m">
Les 32 propriétés « aller » de la norme sont donc absentes de <code>reference/design</code>, et n'apparaîtront pas dans l'API générée.
</div>

</div>
</div>

<div class="takeaway">Ce n'est pas un oubli de la transformation : c'est le prix structurel, assumé, de l'indépendance de KerML.</div>

---

<!-- _class: dense -->

# Famille 1 — La chaîne de typage `Definition` / `Usage` (10)

| Propriété SysML absente | Type visé (KerML) | Card. | Inverse interdit (porté par KerML) |
|---|---|---|---|
| `Usage.definition` | `Classifier` | 0..* | `Classifier.definedUsage` |
| `AttributeUsage.attributeDefinition` | `DataType` | 0..* | `DataType.definedAttribute` |
| `OccurrenceUsage.occurrenceDefinition` | `Class` | 0..* | `Class.definedOccurrence` |
| `ItemUsage.itemDefinition` | `Structure` | 0..* | `Structure.definedItem` |
| `ConnectionUsage.connectionDefinition` | `AssociationStructure` | 0..* | `AssociationStructure.definedConnection` |
| `FlowUsage.flowDefinition` | `Interaction` | 0..* | `Interaction.definedFlow` |
| `ActionUsage.actionDefinition` | `Behavior` | 0..* | `Behavior.definedAction` |
| `StateUsage.stateDefinition` | `Behavior` | 0..* | `Behavior.definedState` |
| `CalculationUsage.calculationDefinition` | `Function` | 0..1 | `Function.definedCalculation` |
| `ConstraintUsage.constraintDefinition` | `Predicate` | 0..1 | `Predicate.definedConstraint` |

<div class="takeaway">« Quel type définit cet usage ? » — la question centrale du motif Definition/Usage, posée dix fois vers KerML.</div>

---

<!-- _class: xdense -->

# Famille 2 — Arguments et conditions typés `Expression` (17)

| Propriété SysML absente | Card. | Inverse interdit | Propriété SysML absente | Card. | Inverse interdit |
|---|---|---|---|---|---|
| `AcceptActionUsage.payloadArgument` | 0..1 | `Expression.acceptingActionUsage` | `SendActionUsage.payloadArgument` | 1..1 | `Expression.sendingActionUsage` |
| `AcceptActionUsage.receiverArgument` | 0..1 | `Expression.acceptActionUsage` | `SendActionUsage.receiverArgument` | 0..1 | `Expression.sendActionUsage` |
| `AnalysisCaseDefinition.resultExpression` | 0..1 | `Expression.analysisCaseDefintion` | `SendActionUsage.senderArgument` | 0..1 | `Expression.senderActionUsage` |
| `AnalysisCaseUsage.resultExpression` | 0..1 | `Expression.analysisCase` | `TerminateActionUsage.terminatedOccurrenceArgument` | 0..1 | `Expression.terminateActionUsage` |
| `AssignmentActionUsage.targetArgument` | 0..1 | `Expression.assignmentAction` | `TransitionUsage.guardExpression` | 0..* | `Expression.guardedTransition` |
| `AssignmentActionUsage.valueExpression` | 0..1 | `Expression.assigningAction` | `ViewDefinition.viewCondition` | 0..* | `Expression.owningViewDefinition` |
| `ForLoopActionUsage.seqArgument` | 1..1 | `Expression.forLoopAction` | `ViewUsage.viewCondition` | 0..* | `Expression.owningView` |
| `IfActionUsage.ifArgument` | 1..1 | `Expression.ifAction` | `WhileLoopActionUsage.untilArgument` | 0..1 | `Expression.untilLoopAction` |
| | | | `WhileLoopActionUsage.whileArgument` | 1..1 | `Expression.whileLoopAction` |

<div class="takeaway">Toutes désignent l'<code>Expression</code> KerML qui porte un argument, une garde ou une condition d'une construction SysML.</div>

---

<!-- _class: dense -->

# Famille 3 — Autres cibles KerML (5)

| Propriété SysML absente | Type visé (KerML) | Card. | Inverse interdit (porté par KerML) |
|---|---|---|---|
| `AssignmentActionUsage.referent` | `Feature` | 1..1 | `Feature.assignment` |
| `SatisfyRequirementUsage.satisfyingFeature` | `Feature` | 1..1 | `Feature.satisfiedRequirement` |
| `TransitionFeatureMembership.transitionFeature` | `Step` | 1..1 | `Step.transitionFeatureMembership` |
| `TransitionUsage.succession` | `Succession` | 1..1 | `Succession.linkedTransition` |
| `ViewUsage.exposedElement` | `Element` | 0..* | `Element.exposingView` |

`ViewUsage.exposedElement` est le cas cité en exemple dans `points-a-trancher.md` : la norme déclare le rôle inverse `exposingView` sur `Element`, la classe racine de KerML.

<div class="takeaway">Total des trois familles : <strong>10 + 17 + 5 = 32</strong> associations, vérifiées absentes de <code>reference/design</code> (aucune exception).</div>

---

# Ce qui est réellement perdu — et ce qui ne l'est pas

<div class="two-col">
<div>

## Aucune donnée stockée n'est perdue

Les **32 sont `isDerived="true"`** — sans exception vérifiée.

<div class="box">
Aucune ne porte de valeur propre : ce sont toutes des vues calculées. Ce qui disparaît est un <strong>raccourci de navigation typé</strong>, pas une information.
</div>

</div>
<div>

## Deux situations distinctes

<div class="box m">
<strong>19 sur 32</strong> se rattachent, directement ou en cascade, à une propriété KerML qui <strong>existe</strong> dans le design (<code>Feature.type</code>, <code>Namespace.member</code>, <code>Type.ownedFeature</code>…). La valeur reste atteignable par l'accesseur hérité.
</div>

<div class="box y">
<strong>13 sur 32</strong> n'ont ni <code>redefines</code> ni <code>subsets</code> : leur calcul est défini par OCL dans la norme, sans propriété héritée qui les porte.
</div>

</div>
</div>

<div class="takeaway">La perte réelle se concentre sur 13 propriétés — essentiellement les arguments d'actions — dont le calcul devrait être réimplémenté comme opération si l'on en a besoin.</div>

---

<!-- _class: dense -->

# Les 13 sans rattachement hérité

| Propriété | Famille |
|---|---|
| `AcceptActionUsage.payloadArgument`, `AcceptActionUsage.receiverArgument` | arguments d'action |
| `AssignmentActionUsage.targetArgument`, `AssignmentActionUsage.valueExpression` | arguments d'action |
| `ForLoopActionUsage.seqArgument`, `IfActionUsage.ifArgument` | arguments d'action |
| `SendActionUsage.payloadArgument`, `.receiverArgument`, `.senderArgument` | arguments d'action |
| `TerminateActionUsage.terminatedOccurrenceArgument` | arguments d'action |
| `WhileLoopActionUsage.untilArgument`, `.whileArgument` | arguments d'action |
| `SatisfyRequirementUsage.satisfyingFeature` | satisfaction d'exigence |

Ces propriétés sont calculées, dans la norme, à partir de la structure de paramètres de l'action — décrite en OCL, pas par un lien `subsets`/`redefines` vers une propriété héritée.

<div class="takeaway">Douze des treize concernent la lecture des arguments d'une action ; c'est un motif unique, pas treize problèmes indépendants.</div>

---

# Les options, et la décision à prendre

<div class="two-col">
<div>

## Ce qui reste possible

<div class="box">
<strong>Ne rien faire</strong> — accepter l'absence. Les 19 rattachées restent lisibles via l'accesseur KerML hérité.
</div>

<div class="box m">
<strong>Générer des opérations</strong> plutôt que des propriétés : un accesseur calculé côté SysML, sans association, donc sans bout inverse côté KerML.
</div>

</div>
<div>

## Ce qui n'est pas possible

<div class="box p">
Recréer les associations telles quelles : cela réintroduit exactement la dépendance KerML → SysML que la règle interdit.
</div>

<div class="box y">
Garder un seul bout : la règle <code>E211</code> de Modelio l'empêche structurellement.
</div>

</div>
</div>

<div class="takeaway">La piste « opération dérivée au lieu d'association » est la seule qui restaure la navigation sans casser l'indépendance de KerML — à arbitrer en équipe.</div>

---

<!-- _class: closing -->

# Dériver n'est pas stocker

## Et toute relation normative n'est pas portable telle quelle

KerML 1.0 · SysML 2.0 · 32 associations recensées
