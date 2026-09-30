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

## WIP · Sémantique normative et prise en charge par Modelio

État WIP : 27 septembre 2026 · XMI source : 1er février 2025

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

`ViewUsage.exposedElement` est le cas cité en exemple dans `WIP-2026-09-26-points-a-trancher.md` : la norme déclare le rôle inverse `exposingView` sur `Element`, la classe racine de KerML.

<div class="takeaway">Les trois tableaux listent les <strong>32</strong> associations (10 + 17 + 5) : toutes sont absentes de <code>reference/design</code> et ne sont donc pas générées dans l'API actuelle.</div>

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

<!-- _class: dense -->

# Exemple complet : `PumpControl` (1/2) — contexte, réception, envoi et affectation

La suite du même modèle est sur la diapositive suivante. Les bibliothèques standard `Actions` et `Requirements` sont supposées disponibles.

```sysml
package PumpControl {
  item def Command;

  part def Pump {
    attribute flowRate : Integer;
    attribute pressure : Integer;
    attribute maxPressure : Integer;
  }

  part def ControlStation;
  action def ProcessWorkflow;

  requirement def MinimumFlow {
    subject pump : Pump;
    attribute minimumFlow : Integer;
    require constraint {
      pump.flowRate >= minimumFlow
    }
  }

  part def PumpSystem {
    part pump : Pump;
    satisfy requirement flowCheck : MinimumFlow by pump {
      :>> minimumFlow = 12;
    }
  }

  action def PumpCycle {
    in part pump : Pump;
    in part controlStation : ControlStation;
    in item expectedCommand : Command;
    in item pendingCommands : Command[0..*];
    in attribute targetFlow : Integer;
    in attribute stopRequested : Boolean;
    action process : ProcessWorkflow;

    action receive
      accept command : Command = expectedCommand via controlStation;
    first receive;
    then send receive.command via controlStation to pump;
    then assign pump.flowRate := targetFlow;
```

Dans ce premier morceau : `payloadArgument` ← `expectedCommand`, `receiverArgument` ← `controlStation`; le `send` donne `payloadArgument` ← `receive.command`, `senderArgument` ← `controlStation`, `receiverArgument` ← `pump`; l’affectation donne `targetArgument` ← `pump` et `valueExpression` ← `targetFlow`.

---

<!-- _class: dense -->

# Exemple complet : `PumpControl` (2/2) — conditions, boucles, terminaison

Suite directe de `PumpCycle` commencée sur la diapositive précédente; les accolades ferment l’action et le package.

```sysml
    then if pump.pressure > pump.maxPressure {
      assign pump.flowRate := 0;
    } else {
      assign pump.flowRate := targetFlow;
    }

    then for command : Command in pendingCommands {
      send command via controlStation to pump;
    }

    then while pump.pressure > 0 {
      assign pump.flowRate := 0;
    } until stopRequested;

    then terminate process;
  }
}
```

| Usage SysML | Propriété dérivée | Expression retrouvée |
|---|---|---|
| `if pump.pressure > pump.maxPressure` | `ifArgument` | `pump.pressure > pump.maxPressure` |
| `for command : Command in pendingCommands` | `seqArgument` | `pendingCommands` |
| `while pump.pressure > 0 ... until stopRequested` | `whileArgument` / `untilArgument` | `pump.pressure > 0` / `stopRequested` |
| `terminate process` | `terminatedOccurrenceArgument` | `process` |
| `satisfy requirement ... by pump` | `satisfyingFeature` | `pump`, liée au `subjectParameter` |

Le `satisfy requirement` du premier morceau crée le binding entre son `subjectParameter` et `pump`; la propriété dérivée retrouve cette Feature en suivant ce `BindingConnector`.

<div class="takeaway">Les 13 propriétés sont des vues sur les Expressions, paramètres et bindings écrits ici; elles ne sont pas des champs supplémentaires.</div>

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

<!-- _class: "section theme-violet" -->

# Partie 4

## Ce que la génération produit aujourd'hui

---

<!-- _class: dense -->

# La génération suit cinq contrôles, de `reference/design` au runtime

1. **Préparer le modèle** — vérifier les notes SemGen de redéfinition contre le XMI normatif, les valeurs initiales et la navigabilité des extrémités dérivées.
2. **Lancer le préflight** — bloquer les directives fausses ou les défauts du modèle ; journaliser les redéfinitions correctes qui ne peuvent pas partager leur stockage.
3. **Générer dans l'ordre** — produire KerML, puis SysML en consommant KerML comme dépendance. SemGen génère les API et implémentations.
4. **Compiler** — vérifier les 705 sources générées contre Modelio 7.0 : 1 242 fichiers `.class`, zéro erreur.
5. **Valider au runtime** — charger les métamodèles dans Modelio, créer des instances et lire leurs propriétés. **Cette étape reste à faire.**

<div class="takeaway">`GENERATION SUCCESSFUL` n'est pas le verdict final : la compilation valide la forme du code, pas son comportement dans Modelio.</div>

---

<!-- _class: dense -->

# `isDerived` n'a pas le même effet sur un attribut et une association

| Propriété `Semantic` | Stockage généré | API générée | Résultat |
|---|---|---|---|
| `Attribute` avec `isDerived=true` | Champ `Data` et descripteur `SmAttribute` | Getter et setter en API/Impl | Traité comme stocké ; SemGen n'évalue pas l'OCL de dérivation. |
| `AssociationEnd` avec `isDerived=true` | Pas de champ `Data` ni de `SmDependency` | Les accesseurs peuvent rester générés si le rôle est navigable | Sans règle de calcul, l'accès peut lever `UnsupportedOperationException`. |

Dans la source vérifiée (SemGen 4.0.21 / semgenerator 1.4.18), `storedAttributes()` ne filtre pas `isDerived`; les générateurs d'associations, eux, le testent explicitement. Rendre une extrémité dérivée non navigable retire aussi son raccourci d'API.

<div class="takeaway">Le marqueur <code>isDerived</code> reste dans le modèle, mais le chemin de génération des attributs ne le consulte pas : SemGen produit du stockage, pas le calcul.</div>

---

<!-- _class: dense -->

# Cinq attributs dérivés normatifs sont marqués dans `reference/design`

| Métamodèle | Attributs marqués dérivés par la phase 30 |
|---|---|
| KerML | `KerMLModelElement.isLibraryElement`, `Type.isConjugated`, `Function.isModelLevelEvaluable`, `Expression.isModelLevelEvaluable` |
| SysML | `Usage.isReference` |

La phase 30 a copié le marqueur `isDerived=true` du XMI normatif et n'a pas inventé de valeur initiale : ces valeurs sont calculées selon la norme.

Mais SemGen 4.0.21 / semgenerator 1.4.18 génère quand même leur champ `Data`, leur descripteur `SmAttribute` et les accesseurs. Le champ n'a pas de valeur initiale et aucun OCL n'est exécuté : la compilation ne valide donc pas leur comportement.

<div class="takeaway">C'est un écart concret de génération sur cinq attributs. Il faut soit implémenter leur calcul, soit adapter le générateur sans supprimer le stockage avant d'avoir une règle de calcul.</div>

---

<!-- _class: dense -->

# Les cinq règles normatives sont connues, mais pas toutes sous forme d'OCL

| Attribut dérivé | Définition normative |
|---|---|
| `KerMLModelElement.isLibraryElement` | `libraryNamespace() <> null`. |
| `Type.isConjugated` | Le type a un `ownedConjugator` (critère donné en prose; `ownedConjugator` est la conjugaison possédée). |
| `Function.isModelLevelEvaluable` | Vrai pour les fonctions désignées dans la Kernel Functions Library; faux pour les autres. Le texte renvoie aux listes normatives, pas à une formule générale. |
| `Expression.isModelLevelEvaluable` | `modelLevelEvaluable(Set(Element){})` : évaluation récursive définie par opérations OCL et spécialisée selon le type d'expression. |
| `Usage.isReference` | `not isComposite`. |

La norme décrit donc ce qu'il faut calculer. L'écart est dans SemGen : ces règles ne sont pas traduites en accesseurs calculés pour les attributs.

**Vérification live Modelio (2026-09-28)** : les Notes directes des cinq attributs sont présentes et concordantes entre `reference/spec` et `reference/design`. Elles décrivent leur sens, mais ne contiennent pas les corps OCL complets; ceux-ci restent dans les sources normatives et ne sont pas portés comme calculs par le modèle généré.

<!-- footer: KerML 8.3.3.1.4 / 8.3.4.7.3-7.4 / 8.4.4.9.8 ; SysML 8.3.13.2.4 -->
<!-- footer: "" -->

---

<!-- _class: dense -->

# `SemGenManual` seul ne rend pas ces attributs calculés

- Dans la version vérifiée, `SemGenManual` préserve les éléments manuels du code généré pendant le nettoyage; ce n'est pas un mode de génération pour une propriété dérivée.
- Tant que l'attribut source reste `Semantic`, les générateurs actuels émettent encore son champ `Data`, son descripteur `SmAttribute` et getter/setter.
- Ajouter `SemGenManual` à l'attribut ne supprime donc ni le stockage ni le setter, et ne produit pas son calcul normatif.

<div class="box y">
Piste manuelle possible, mais non validée : empêcher le chemin de stockage automatique, puis fournir un getter calculé qui survit aux régénérations. Il faut encore définir le point d'extension et vérifier que l'API générée reste cohérente.
</div>

<div class="takeaway">Statut WIP : aucun calcul manuel des cinq attributs n'est actuellement livré.</div>

---

<!-- _class: dense -->

# Le composant et chaque métaclasse portent leur contrat SemGen

| Porteur | Stéréotype / propriété | Effet |
|---|---|---|
| Composant du métamodèle | `Metamodel` : `id`, `name`, `version`, `provider`, `providerversion`, `production.namespace` | Identifie le métamodèle et ses packages de sortie. |
| Composant du métamodèle | `Metamodel.isExtension` | À activer pour ce métamodèle Modelio. |
| Métaclasse | `Semantic` ou `SemanticLinkMetaclass` | Distingue un concept d'une métaclasse de relation. |
| Métaclasse | `Abstract` (UML) | Génère une classe/interface abstraite. |
| Métaclasse `Semantic` | `Semantic.structural.node` | Marque un nœud CMS, persisté dans son propre fichier ; ne pas cocher sur une classe abstraite. |
| Racine | `Semantic.orphans.allowed` | Autorise les instances sans propriétaire de composition (chemin Toutatis). |

Ces marqueurs ne remplacent pas les propriétés UML : ils indiquent à SemGen comment générer et persister le métamodèle.

---

<!-- _class: dense -->

# Les tags des propriétés règlent stockage et directives du noyau

| Porteur | Tag | Effet dans SemGen |
|---|---|---|
| Attribut `Semantic` | `Semantic` + type, multiplicité, valeur initiale | Champ de données, `SmAttribute`, getter/setter ; les attributs générés ici sont scalaires. |
| Attribut `Semantic` | `Semantic.fpIndexed` | Traduit en `SmDirective.FPINDEXED`. |
| Extrémité d'association | `Semantic.structural.partOf` | Émet `SmDirective.SMCDPARTOF` pour placer le stockage sur cette extrémité. |
| Extrémité d'association | `Semantic.structural.isToDelete` | Émet `SmDirective.SMCDTODELETE` (suppression en cascade). |
| Extrémité d'association | `Semantic.persistency.optional` | Émet `SmDirective.SMCDDYNAMIC`. |
| Lien sémantique | `Semantic.link.source` / `Semantic.link.target` | Émet les directives source/cible en mode Toutatis. |

Les directives de composition/agrégation sont aussi déduites de l'agrégation UML. `EInoExternalize` n'a pas de mapping SemGen observé dans la version vérifiée : ne pas en déduire un attribut transient.

---

<!-- _class: dense -->

# Les notes du modèle ne disaient pas toujours ce que dit la norme

Le générateur ne lit pas le XMI. Il lit une ligne de texte posée sur chaque propriété du modèle — par exemple `Redefines (per normative XMI): Relationship.target` — et la traite comme un **ordre** : « range cette propriété dans l'emplacement de stockage de cette autre propriété ».

Une ligne fausse produit donc l'une de deux choses :

<div class="two-col">
<div>

<div class="box p">
Elle nomme une propriété <strong>qui n'existe pas</strong>. Le générateur s'arrête. Toute la génération est bloquée — visible, donc réparable.
</div>

</div>
<div>

<div class="box y">
Elle nomme une propriété <strong>qui existe mais n'est pas la bonne</strong>. Rien ne casse. L'API générée partage simplement le mauvais emplacement. <strong>Silencieux.</strong>
</div>

</div>
</div>

<div class="takeaway">Une note fausse du second type ne se voit ni à la génération, ni à la compilation — seulement en relisant le XMI, propriété par propriété.</div>

---

<!-- _class: dense -->

# Six passes de nettoyage : 15 notes fausses

| Phase | Ce qui était écrit | Ce que dit réellement le XMI | Nb |
|---|---|---|---|
| **24** | 4 notes pointaient vers la chaîne d'**appartenance** (`...OwningDefinition`) | Elles relèvent de la chaîne de **typage** (`Usage.definition` → `Feature.type`) — deux chaînes qui ne partagent qu'un fragment de nom | **4** |
| **26** | 5 notes déduites mécaniquement de celles de la phase 24 | La règle de déduction était juste, la donnée d'entrée était fausse : les 5 le sont donc aussi | **5** |
| **27** | 6 notes `Redefines ... sourceRelationship` | Le XMI déclare un `<subsettedProperty>`, **jamais** un `<redefinedProperty>` | **6** |
| 25 | 2 notes visant une propriété absente du modèle | Jamais fausses : leur cible, `ConnectionUsage.connectionDefinition`, fait partie des 32 absentes. Réécrites en prose. | 2 |
| 28 | 2 propriétés `owned*` non marquées composites | Elles redéfinissent un emplacement composite : elles doivent porter la même agrégation | 2 |
| 29 | 3 notes nommaient **deux** cibles aboutissant à deux emplacements différents | Un stockage ne peut pas être à deux endroits à la fois | 3 |

<div class="takeaway">Les 6 de la phase 27 étaient <strong>acceptées</strong> par le générateur : cinq d'entre elles portaient même, juste au-dessus, la ligne <code>Subsets</code> correcte qui les contredisait. Elles seraient parties en production. Leçon retenue : vérifier une note contre le XMI, jamais contre une autre note.</div>

---

# Le générateur distingue désormais le défaut de la limite

Auparavant, toute difficulté produisait le même résultat : un arrêt, et zéro classe générée. Deux situations très différentes étaient confondues.

<div class="two-col">
<div>

## Défaut — arrêt maintenu

<div class="box p">
Une note nomme une propriété inexistante, est mal formée, boucle sur elle-même, ou fusionne deux stockages indépendants.
</div>

Générer à partir de métadonnées fausses produit une API silencieusement fausse. C'est pire que ne rien générer.

</div>
<div>

## Limite — dégradation

<div class="box m">
La redéfinition est réelle et correcte, mais les deux propriétés ne peuvent pas partager un emplacement en toute sécurité.
</div>

La propriété garde alors son propre emplacement, et le cas est **journalisé**. Le modèle est correct ; c'est le schéma de partage de stockage qui atteint sa limite.

</div>
</div>

<div class="takeaway">Le coût est précis et petit : <strong>8 propriétés restent dupliquées</strong>. Les 165 autres sont dédupliquées. Avant ce découpage, les 173 l'étaient toutes.</div>

---

<!-- _class: dense -->

# Pour les extrémités d'association, aucune propriété dérivée n'est générée

Les trois premières parties posent la question ; voici la réponse retenue.

Une extrémité d'association dérivée n'a **pas de stockage** — c'est sa définition même. Le générateur ne produisait donc aucun emplacement pour elle, tout en produisant des accesseurs qui le réclamaient. Résultat : d'abord 99 erreurs de compilation, puis 291 méthodes qui lèvent une exception dès qu'on les appelle.

<div class="two-col">
<div>

<div class="box y">
<strong>Calculer les valeurs n'est pas possible depuis ce modèle.</strong> La norme énonce ces dérivations en OCL et en prose, pas sous une forme mécanisable.
</div>

</div>
<div>

<div class="box p">
Les notes <code>Subsets</code> du modèle, seule source à partir de laquelle une union dérivée pourrait être reconstituée, sont <strong>démontrablement incomplètes</strong> : <code>Element.owner</code> en recense <strong>0</strong> là où le XMI en déclare <strong>2</strong>.
</div>

</div>
</div>

<div class="takeaway">Se fonder sur ces notes aurait transformé quatre unions dérivées manuelles en champs stockés — deux sources de vérité pour dire où vit un élément. Le risque est plus grand que le service rendu.</div>

---

<!-- _class: dense -->

# Phase 33 : 291 extrémités dérivées de `spec` rendues non navigables dans `design`

Dans `reference/spec`, les déclarations normatives restent intactes. Dans `reference/design`, la phase 33 conserve les associations et le marqueur `isDerived`, mais passe `isNavigable` à `false` sur les 291 extrémités dérivées. Les 262 extrémités navigables restantes forment le stockage conservé.

<div class="two-col">
<div>

## Pourquoi « non navigable » et non « supprimée »

Supprimer était l'idée de départ, et elle est dangereuse.

<div class="box p">
Les deux extrémités d'une association sont logées dans un seul élément : supprimer l'une emporte l'autre. Supprimer <code>Definition.ownedPort</code> détruirait <code>PortUsage.portOwningDefinition</code>, qui est <strong>stockée</strong> et porteuse.
</div>

</div>
<div>

## Pourquoi toutes, et pas un sous-ensemble

85 d'entre elles ressemblent à de simples rôles inverses qu'on pourrait plutôt **démarquer** comme dérivés.

<div class="box y">
Mais ce tri dépend précisément des notes <code>Subsets</code> qui viennent d'être prouvées peu fiables. Un changement uniforme n'a besoin d'aucun classement et ne peut pas se tromper de cette façon-là.
</div>

</div>
</div>

Le marquage « non navigable » produit exactement le même résultat généré — tous les générateurs de SemGen testent ce drapeau — tout en laissant l'association et son côté stocké intacts. **Il est réversible d'un seul drapeau**, le jour où quelqu'un décide quelles commodités méritent une vraie règle de dérivation.

---

<!-- _class: dense -->

# Ce qui survit, et ce qui est réellement perdu

<div class="two-col">
<div>

## Survit : toute la structure

L'ossature `Relationship` / `Membership` / `Specialization` sur laquelle KerML est bâti.

<div class="box">
<code>ownedRelationship</code>, <code>owningRelationship</code>, <code>Relationship.source</code>, <code>Relationship.target</code>, <code>OwningMembership.ownedMemberElement</code>.
</div>

Chaque accesseur retiré était une **vue** au-dessus de cette ossature. Aucune structure ne devient inexprimable.

</div>
<div>

## Perdu : le raccourci

<div class="box y">
Atteindre les ports d'une <code>Definition</code> passe désormais par un saut explicite à travers la relation, au lieu de <code>definition.getOwnedPort()</code>.
</div>

C'est un coût réel, délibérément accepté — sachant que ces accesseurs **ne fonctionnaient pas non plus** avant ce changement : ils levaient une exception.

</div>
</div>

<div class="takeaway">Un <code>ConjugatedPortDefinition</code> se trouve toujours par <code>ownedRelationship</code> → <code>OwningMembership</code> → <code>ownedMemberElement</code> ; un typage toujours par <code>ownedRelationship</code> → <code>FeatureTyping</code> → <code>target</code>.</div>

---

<!-- _class: dense -->

# Résultat : les deux métamodèles génèrent, et le Java compile

<div class="two-col">
<div>

<div class="stat-box"><span class="number">705</span><span class="label">fichiers Java générés</span></div>

<div class="stat-box"><span class="number">0</span><span class="label">erreur de compilation</span></div>

</div>
<div>

`sysml.metamodel.api` (180 fichiers) et `sysml.metamodel.impl` (525), compilés contre Modelio 7.0.0 → **1242 fichiers `.class`**.

<div class="box m">
<strong>Chaque accesseur de propriété de l'API générée est adossé à un stockage réel.</strong> Plus aucun ne lève d'exception.
</div>

</div>
</div>

| Ce qui lève encore une exception | Nb | Pourquoi c'est légitime |
|---|---:|---|
| Corps d'opérations (`path`, `evaluate`, `effectiveName`…) | 151 | Comportement à écrire à la main. Une implémentation posée là survit aux régénérations. |
| `createData` / `createImpl` | 16 | Sur des métaclasses abstraites. Une métaclasse abstraite ne s'instancie pas. |
| Extrémités d'association dérivées | **0** | Retirées de la génération. |

---

# Ce que compiler ne prouve pas

<div class="box p">
Le code n'a <strong>jamais été exécuté</strong>. Aucune instance créée, aucune propriété lue, aucune session Modelio n'a chargé ce métamodèle. C'est le prochain jalon réel.
</div>

<div class="two-col">
<div>

## Points ouverts connus

- **8 membres restent dupliqués** — les 7 dont l'extrémité opposée ne fait que sous-ensembler, plus `OwningMembership.ownedMemberElement`, une vraie question de modélisation.
- **11 classes à composition multiple** : le générateur en choisit une, décidant seul de l'arbre de contenance.

</div>
<div>

## Et une commodité perdue, assumée

<div class="box y">
Les 291 accesseurs dérivés ne reviendront que si quelqu'un écrit, propriété par propriété, la règle de calcul que la norme n'exprime qu'en OCL.
</div>

Rien n'empêche de le faire plus tard, et au cas par cas : c'est un drapeau par propriété.

</div>
</div>

---

<!-- _class: closing -->

# Dériver n'est pas stocker

## 291 extrémités dérivées écartées ; les attributs dérivés ne sont pas calculés

KerML 1.0 · SysML 2.0 · 32 associations recensées · 291 vues dérivées écartées
