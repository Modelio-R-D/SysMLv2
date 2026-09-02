# Points à trancher — greffe SysML v2/KerML sur l'infrastructure Modelio

Document de travail préparant la demande d'Antonin : la liste des décisions sur lesquelles nous avons besoin d'un arbitrage, extraites du plan d'implémentation (`slides.md`). Chaque point renvoie à la partie du deck qui détaille le raisonnement et les exemples.

## 1. Point de greffe sur l'infrastructure

**Proposition** : le point de greffe est `ModelElement`. `KerML::Element` est renommé, dans `implementation` uniquement, en `KerMLModelElement`, et étend directement `ModelElement`.

**Pourquoi cette proposition** : c'est exactement le patron déjà utilisé par l'implémentation UML de Modelio (`UmlModelElement extends ModelElement`), c'est la convention établie.

**Question à trancher** : valide-t-on ce renommage et ce point de greffe ?

*Réf. : Partie 2, slides « Résolu : le point de greffe est ModelElement » à « Ce que ça change pour la greffe — et pour le nommage ».*

---

## 2. Point de greffe pour le projet

**Proposition** : `SysMLProject extends AbstractProject`, sur le même patron que `Project` (UML). Nommé côté SysML et non KerML — il n'y aura pas d'éditeur KerML autonome, seulement un éditeur SysML v2 ; KerML reste la couche fondationnelle greffée en interne, mais n'a pas sa propre surface de projet.

**Question à trancher** : valide-t-on ce nom et ce point de greffe, et le principe que KerML n'a pas besoin de sa propre surface de projet ?

*Réf. : Partie 2, slide « Ce que ça change pour la greffe — et pour le nommage ».*

---

## 3. Les trois chevauchements avec l'infrastructure Modelio

**Proposition** : ne pas réimplémenter dans `implementation` ce que l'infrastructure Modelio fait déjà nativement :

| Concept KerML (nom qualifié) | Infrastructure Modelio (nom qualifié) | Traitement proposé | Achoppements |
|---|---|---|---|
| `KerML::Root::Annotations::Comment`, `KerML::Root::Annotations::Documentation` | `infrastructure::Note` | Mapper sur `Note` | (1) `Comment` a 3 formes textuelles (explicite avec `about`, implicite, avec `locale`) — `Note` devra porter la `locale` et la contrainte structurelle propre à `Documentation` (élément documenté = propriétaire). (2) Différence structurelle plus profonde : en SysML v2, un `Comment` peut être lié à **plusieurs** éléments à la fois (`about A, B`) ; en Modelio, une `Note` est **contenue** dans l'unique élément qu'elle documente (composition) |
| `KerML::Root::Dependencies::Dependency` | `infrastructure::Dependency` | Alias direct | (1) Le `Dependency` de Modelio peut porter des comportements/stéréotypes hérités du contexte UML — à vérifier qu'aucun ne s'applique par erreur à un lien KerML. (2) Pas de support n-aire côté Modelio : KerML permet `dependency X to Y, Z;` (un client, plusieurs fournisseurs, en une seule relation) ; Modelio ne représente qu'un lien binaire — une dépendance n-aire devra être décomposée en plusieurs `Dependency` binaires (`X->Y`, `X->Z`) |
| `SysML::Systems::Metadata::MetadataDefinition`, `SysML::Systems::Metadata::MetadataUsage` | `infrastructure::Stereotype` + `infrastructure::TaggedValue` | Mapper sur le sous-système Stereotype/TaggedValue | Le plus significatif des trois : un `MetadataUsage` s'attache à plusieurs cibles à la fois en une seule instance (`about A, B, C`). En Modelio, un `Stereotype` (définition) peut bien être appliqué à plusieurs éléments, mais **chaque application** (`ExtensionValue`) ne concerne qu'un seul élément de base |

*Noms qualifiés côté KerML/SysML vérifiés dans les XMI de spec (`KerML.xmi`/`SysML.xmi`). Côté Modelio, le préfixe de package (`infrastructure::`) est confirmé mais le chemin complet reste à valider une fois ScriptServer de nouveau accessible (hors ligne au moment de la rédaction).*

**Y a-t-il d'autres chevauchements ?** Relecture des 19 classes du package `infrastructure` (voir diagramme, Partie 2) face aux 182 classes de `reference` : aucun autre chevauchement conceptuel net trouvé. Le reste du package infrastructure se répartit en (a) plomberie de support pour les 3 chevauchements ci-dessus — `NoteType`, `TagType`, `TagParameter`, `MetaclassReference` — à examiner au moment de l'implémentation mais pas des concepts KerML/SysML séparés, et (b) des concepts propres à Modelio sans équivalent KerML/SysML — `Resource`/`Document`/`AbstractResource` (pièces jointes), `ExternProcessor`/`ExternElement` (intégration outillage), `Profile` (regroupement de Stereotypes), `MethodologicalLink` (Dependency spécialisé). `AbstractProject` est déjà couvert au point 2.

**Question à trancher** : valide-t-on ces trois mappings (plutôt que de dupliquer ces concepts dans `implementation`), et confirme-t-on qu'il n'y a pas de 4ᵉ chevauchement à traiter ?

*Réf. : Partie 3, slides « Trois chevauchements concrets » à « Chevauchement 3b ».*

---

## 4. Stratégie générale pour l'héritage multiple KerML → Java

**Constat** : 34 classes de `reference` ont deux (ou trois) super-types directs — impossible à traduire tel quel en Java (une seule classe mère autorisée).

**Proposition** : pour chaque cas, l'axe qui appartient à la lignée **Definition/Usage** gagne toujours `extends` ; l'autre axe devient une interface `mm.api`, implémentée par délégation à un objet interne qui porte son état. Approche alignée sur un précédent MDE établi (flattening EMF/Ecore) et sur des patrons de refactoring connus (*Replace Inheritance with Delegation*, *Role Object*).

**Question à trancher** : valide-t-on ce principe général comme règle par défaut ?

*Réf. : Partie 4, slides « Java n'a pas d'héritage multiple » à « Ce n'est pas une approche ad hoc ».*

---

## 5. Les 34 résolutions individuelles

**Proposition** : chaque cas a déjà une résolution proposée (qui gagne `extends`, qui devient interface déléguée), détaillée slide par slide avec la description du concept, son chemin qualifié, et un exemple d'usage réel. Résumé des 34 cas :

| # | Classe | `extends` (axe primaire) | `implements` (axe délégué) |
|---|---|---|---|
| 1 | `Association` | `Relationship` | `Classifier` |
| 2 | `AssociationStructure` | `Association` | `Structure` |
| 3 | `Connector` | `Feature` | `Relationship` |
| 4 | `Flow` | `Connector` | `Step` |
| 5 | `Interaction` | `Behavior` | `Association` |
| 6 | `MetadataFeature` | `Feature` | `AnnotatingElement` |
| 7 | `SuccessionFlow` | `Flow` | `Succession` |
| 8 | `ActionDefinition` | `OccurrenceDefinition` | `Behavior` |
| 9 | `ActionUsage` | `OccurrenceUsage` | `Step` |
| 10 | `AssertConstraintUsage` | `ConstraintUsage` | `Invariant` |
| 11 | `AttributeDefinition` | `Definition` | `DataType` |
| 12 | `BindingConnectorAsUsage` | `ConnectorAsUsage` | `BindingConnector` |
| 13 | `CalculationDefinition` | `ActionDefinition` | `Function` |
| 14 | `CalculationUsage` | `ActionUsage` | `Expression` |
| 15 | `ConnectionDefinition` | `PartDefinition` | `AssociationStructure` |
| 16 | `ConnectionUsage` | `PartUsage` | `ConnectorAsUsage` |
| 17 | `ConnectorAsUsage` | `Usage` | `Connector` |
| 18 | `ConstraintDefinition` | `OccurrenceDefinition` | `Predicate` |
| 19 | `ConstraintUsage` | `OccurrenceUsage` | `BooleanExpression` |
| 20 | `ExhibitStateUsage` | `PerformActionUsage` | `StateUsage` |
| 21 | `FlowDefinition` | `ActionDefinition` | `Interaction` |
| 22 | `FlowUsage` *(3 parents)* | `ActionUsage` | `ConnectorAsUsage`, `Flow` |
| 23 | `IncludeUseCaseUsage` | `PerformActionUsage` | `UseCaseUsage` |
| 24 | `ItemDefinition` | `OccurrenceDefinition` | `Structure` |
| 25 | `MembershipExpose` | `Expose` | `MembershipImport` |
| 26 | `MetadataDefinition` | `ItemDefinition` | `Metaclass` |
| 27 | `MetadataUsage` | `ItemUsage` | `MetadataFeature` |
| 28 | `NamespaceExpose` | `Expose` | `NamespaceImport` |
| 29 | `OccurrenceDefinition` | `Definition` | `Class` |
| 30 | `PerformActionUsage` | `ActionUsage` | `EventOccurrenceUsage` |
| 31 | `PortDefinition` | `OccurrenceDefinition` | `Structure` |
| 32 | `SatisfyRequirementUsage` | `RequirementUsage` | `AssertConstraintUsage` |
| 33 | `SuccessionAsUsage` | `ConnectorAsUsage` | `Succession` |
| 34 | `SuccessionFlowUsage` | `FlowUsage` | `SuccessionFlow` |

*Cas 1–7 : noyau KerML. Cas 8–34 : niveau SysML. Détail complet (description du concept, chemin qualifié, exemple SysML v2) : Partie 4, slides « Cas 1 » à « Cas 34 ».*

### Ce que porte l'objet délégué, cas par cas

Convention de nommage : `<AxeSecondaire>Behavior` (ex. `DataTypeBehavior`, déjà montré Partie 4 « Approche recommandée »). Exception : cas 8, où l'axe secondaire s'appelle déjà `Behavior` — renommé `BehaviorRole` pour éviter la collision. Quand l'axe délégué est lui-même une classe à double statut (primaire dans son propre cas, déléguée ici), son objet délégué contient à son tour son propre délégué — chaîne indiquée ci-dessous par « → ».

1. **`Association`** délègue à **`ClassifierBehavior`** : porte la classification — les Features utilisées pour typer les choses ou leurs relations. `Classifier` n'a pas d'attribut propre listé dans `reference` ; c'est un rôle de typage pur.
2. **`AssociationStructure`** délègue à **`StructureBehavior`** : porte le rôle d'objet-lien structurel (« classe d'objets principalement structurels »), sans attribut propre listé. L'état réel de la relation reste porté par l'axe primaire (`Association`, lui-même `extends Relationship`).
3. **`Connector`** délègue à **`RelationshipBehavior`** : porte l'attribut `isImplied` et les opérations `libraryNamespace`, `path` — la mécanique de lien générique entre deux `Element`. Concrètement : `isImplied()` sur un `Connector` fait `return relationshipBehavior.isImplied();`.
4. **`Flow`** délègue à **`StepBehavior`** : porte l'ordonnancement temporel et la connectabilité par d'autres Flows (pas d'attribut propre listé — juste un comportement d'ordonnancement).
5. **`Interaction`** délègue à **`AssociationBehavior`**, qui délègue lui-même à **`ClassifierBehavior`** (cas 1) : porte la classification des liens entre objets aux comportements interdépendants. Chaîne de délégation à deux niveaux.
6. **`MetadataFeature`** délègue à **`AnnotatingElementBehavior`** : porte la description/métadonnée additionnelle attachée à l'Element annoté. Pas d'attribut propre listé sur `AnnotatingElement` — c'est `MetadataFeature` lui-même (l'axe primaire ici) qui porte les opérations concrètes (`evaluateFeature`, `isSemantic`, `isSyntactic`, `syntaxElement`).
7. **`SuccessionFlow`** délègue à **`SuccessionBehavior`** : porte l'exigence que les deux extrémités du lien surviennent séparément dans le temps (contrainte d'ordre, pas d'attribut propre listé).
8. **`ActionDefinition`** délègue à **`BehaviorRole`** : porte la décomposition en Steps et la paramétrabilité du comportement générique — ce qui permet à une `ActionDefinition` d'être invoquée avec des paramètres comme n'importe quel `Behavior`, sans que ce soit son identité structurelle première.
9. **`ActionUsage`** délègue à **`StepBehavior`** : porte l'ordonnancement dans le temps et la connectabilité par des Flows, exactement comme au cas 4 — pas d'attribut propre listé sur `Step` lui-même. (`ActionUsage` a par ailleurs ses propres opérations `inputParameters`, `argument`, `isSubactionUsage`, mais celles-ci sont portées par l'axe primaire `OccurrenceUsage`/`ActionUsage`, pas par le délégué `Step`.)
10. **`AssertConstraintUsage`** délègue à **`InvariantBehavior`** : porte l'attribut `isNegated` — l'assertion que la contrainte est vraie (ou fausse si niée) par défaut, en plus de la structure de contrainte héritée de l'axe primaire.
11. **`AttributeDefinition`** délègue à **`DataTypeBehavior`** : porte la classification par valeurs de données indistinguables sauf par leurs relations via Features (pas d'attribut propre listé — rôle de classification). C'est l'exemple déjà filé en détail Partie 4.
12. **`BindingConnectorAsUsage`** délègue à **`BindingConnectorBehavior`** : porte la contrainte que les deux extrémités liées identifient les mêmes valeurs (pas d'attribut propre listé — une contrainte de comportement, vérifiée à l'exécution/à la validation).
13. **`CalculationDefinition`** délègue à **`FunctionBehavior`** : porte l'attribut `isModelLevelEvaluable` et l'identification du paramètre de sortie comme résultat de la fonction.
14. **`CalculationUsage`** délègue à **`ExpressionBehavior`** : porte l'attribut `isModelLevelEvaluable` et les opérations `evaluate`, `checkCondition` — c'est concrètement ce qui permet d'évaluer le calcul et de lire son résultat unique.
15. **`ConnectionDefinition`** délègue à **`AssociationStructureBehavior`**, qui délègue lui-même à `Association` → `Relationship`/`Classifier` (cas 2 → cas 1) : porte le rôle d'objet-lien structurel en cascade à deux niveaux.
16. **`ConnectionUsage`** délègue à **`ConnectorAsUsageBehavior`**, qui délègue lui-même à `Usage` (attributs `isVariation`, `isReference`, `mayTimeVary` ; opérations `namingFeature`, `referencedFeatureTarget`) et à `Connector` (cas 17) : porte le rôle de connecteur complet en cascade.
17. **`ConnectorAsUsage`** délègue à **`ConnectorBehavior`** : porte les 9 attributs de `Feature` (`direction`, `isComposite`, `isDerived`, `isOrdered`, `isUnique`…) et les opérations de typage/redéfinition (`redefines`, `subsetsChain`, `typingFeatures`…), plus `isImplied`/`libraryNamespace`/`path` de `Relationship` en cascade (cas 3). C'est le délégué le plus chargé des 34 cas — ce backbone est réutilisé par 4 autres cas (12, 16, 22, 33).
18. **`ConstraintDefinition`** délègue à **`PredicateBehavior`** : porte l'évaluation à résultat booléen de multiplicité 1..1 (pas d'attribut propre listé).
19. **`ConstraintUsage`** délègue à **`BooleanExpressionBehavior`** : porte la condition logique typée par un `Predicate` (pas d'attribut propre listé — la logique d'évaluation vient de la cascade vers `Predicate`, cas 18).
20. **`ExhibitStateUsage`** délègue à **`StateUsageBehavior`** : porte l'attribut `isParallel` et l'opération `isSubstateUsage` — permet de savoir si l'état exhibé est parallèle à d'autres et s'il est lui-même un sous-état.
21. **`FlowDefinition`** délègue à **`InteractionBehavior`**, qui délègue lui-même à `Behavior` et `Association` → `Classifier` (cas 5 → cas 1) : porte le contexte d'interaction entre usages, en cascade à deux niveaux.
22. **`FlowUsage`** (3 parents) délègue à **deux objets** : `ConnectorAsUsageBehavior` (rôle de connecteur, cas 17, lui-même déjà chargé) et `FlowBehavior` (transfert de valeur + ordonnancement temporel, cas 4). Seul cas des 34 où l'impl porte deux champs délégués distincts au lieu d'un.
23. **`IncludeUseCaseUsage`** délègue à **`UseCaseUsageBehavior`** : porte le rôle d'usage typé par une `UseCaseDefinition` (pas d'attribut propre listé).
24. **`ItemDefinition`** délègue à **`StructureBehavior`** : porte le rôle d'objet structurel, identique au cas 2 (pas d'attribut propre listé).
25. **`MembershipExpose`** délègue à **`MembershipImportBehavior`** : porte l'opération `importedMemberships` — l'accès effectif au Membership importé/exposé.
26. **`MetadataDefinition`** délègue à **`MetaclassBehavior`** : porte le rôle de typage des `MetadataFeature` (pas d'attribut propre listé — c'est ce qui permet à une `MetadataDefinition` de servir de type à des métadonnées, comme un `Stereotype` Modelio).
27. **`MetadataUsage`** délègue à **`MetadataFeatureBehavior`**, qui porte lui-même les opérations `evaluateFeature`, `isSemantic`, `isSyntactic`, `syntaxElement` (état propre à `MetadataFeature`, cas 6, pas une cascade supplémentaire ici car `MetadataFeature` est l'axe primaire de son propre cas).
28. **`NamespaceExpose`** délègue à **`NamespaceImportBehavior`** : porte l'opération `importedMemberships`, symétrique au cas 25 mais pour un namespace entier plutôt qu'un membership unique.
29. **`OccurrenceDefinition`** délègue à **`ClassBehavior`** : porte la classification de choses distinguables sans égard à leurs relations via Features (pas d'attribut propre listé).
30. **`PerformActionUsage`** délègue à **`EventOccurrenceUsageBehavior`** : porte l'attribut `isReference` — le fait que l'usage représente une autre occurrence comme sous-occurrence référencée plutôt que composée.
31. **`PortDefinition`** délègue à **`StructureBehavior`** : identique aux cas 2 et 24, rôle d'objet structurel sans attribut propre.
32. **`SatisfyRequirementUsage`** délègue à **`AssertConstraintUsageBehavior`**, qui délègue lui-même à `Invariant` (attribut `isNegated`, cas 10) : porte l'assertion que l'exigence est satisfaite, en cascade.
33. **`SuccessionAsUsage`** délègue à **`SuccessionBehavior`** : identique au cas 7, exigence d'ordre temporel séparé entre les deux extrémités.
34. **`SuccessionFlowUsage`** délègue à **`SuccessionFlowBehavior`**, qui délègue lui-même à `Flow` → `Connector`/`Step` et à `Succession` (cas 7) : porte le rôle flux + ordre temporel, en cascade à deux niveaux — le cas le plus profondément délégué des 34.

**À noter pour les devs** : recompté précisément (attribut direct, opération directe, ou l'un des deux via une chaîne de cascade), le partage est quasi exactement à égalité, 17 contre 17 :

- **17 cas ont un délégué avec du contenu réel à porter** (au moins un attribut et/ou une opération, direct ou en cascade) : 3, 5 (→cascade), 10, 13, 14, 15 (→cascade), 16 (→cascade), 17 (→cascade), 20, 21 (→cascade), 22, 25, 27, 28, 30, 32 (→cascade), 34 (→cascade).
- **17 cas ont un délégué qui est un pur marqueur** — ni attribut ni opération listés dans `reference`, juste un rôle de classification ou une contrainte conceptuelle, sans champ ni méthode à recopier aujourd'hui : 1, 2, 4, 6, 7, 8, 9, 11, 12, 18, 19, 23, 24, 26, 29, 31, 33.

Pour ces 17 marqueurs, le délégué existe surtout pour que `implements X` compile proprement — il pourrait rester une classe quasi vide (ou même un singleton partagé, à voir en implémentation) tant que la spec KerML/SysML ne leur ajoute pas d'attribut propre. Pour les 17 autres, il porte un état ou un comportement réel à répercuter fidèlement.

**Question à trancher** : valide-t-on la règle générale (point 4) et laisse-t-on les 34 cas en découler automatiquement, ou souhaitez-vous une revue cas par cas ? Si revue cas par cas : y a-t-il des cas qui vous semblent contestables à première vue ?

*Réf. : Partie 4, slides « Cas 1 · Association » à « Cas 34 · SuccessionFlowUsage », résumées dans « Au bilan : quelles classes deviennent des interfaces pures ».*

---

## 6. Prochaine grosse étape : le script de transformation `reference` → `implementation`

**Objectif** : une fois les points 1 à 5 tranchés, un script Jython construit `implementation` automatiquement à partir de `reference`, en appliquant mécaniquement les règles décidées plus haut plutôt que de recopier les 182 classes à la main.

### SemGen : les stéréotypes et propriétés qu'on va appliquer

SemGen est l'outil interne Modelio qui génère `mm.api`/`mm.impl` à partir d'un métamodèle stéréotypé selon ses conventions (menu contextuel sur le composant métamodèle → SemGen → Generate Metamodel). Un second outil, Java Architect, prend ensuite `mm.api`/`mm.impl` pour produire le code Java définitif, packagé en plugin Eclipse. Ce que le script doit poser sur le modèle pour que cette chaîne fonctionne :

**Sur le composant racine du métamodèle** — stéréotype `SemGen::Metamodel` (porté par un composant UML, pas un package) : `Name`, `Id`, `Version` (pilote les scripts de migration), `Provider`/`Provider version`, `Production namespace` (le namespace Java racine généré, ex. `org.modelio.sysml2.metamodel`), et `Metamodel.isExtension` — à cocher systématiquement (confirmé par Cédric Marin) sur tout métamodèle destiné à SemGen.

**Sur chaque métaclasse** — l'un des deux stéréotypes suivants, jamais les deux :
- **`Semantic`** — sur les classes-concepts (la grande majorité de nos 182 classes : `PartDefinition`, `ActionUsage`, `AttributeDefinition`…).
- **`SemanticLinkMetaclass`** — sur les classes-relations (`Association`, `Connector`, `Dependency`, `Succession`, `Flow`… — recoupe largement le noyau KerML des cas 1 à 7).

**Propriétés sur les métaclasses `Semantic`** :
- `structural.node` — cochée = l'élément est un « grain » persisté dans son propre fichier ; non cochée = persisté avec son parent (cas des attributs, notes…). Jamais cochée sur une métaclasse abstraite.
- `semantic.orphans.allowed` — cochée = l'élément peut exister sans parent de composition. Réservée aux racines de métamodèle — c'est cette propriété qui, techniquement, définit qu'un élément est une racine (chez nous : `SysMLProject` lui-même, point 2 — sur le même principe qu'`ArchimateProject`, qui porte directement cette propriété plutôt qu'une sous-classe).

**Propriétés sur les attributs `Semantic`** : un type Java parmi un ensemble restreint (`String`, `Text`, `Boolean`, `Integer`, `Unsigned`, `Float`, ou un type énuméré — génère alors une classe enum Java dédiée), une multiplicité toujours 1 (contrairement aux relations), une valeur par défaut (`Value`). Deux propriétés historiques, confirmées par Cédric Marin comme non prises en compte par le moteur de génération actuel : `fpIndexed` (ajoutait un index sur l'attribut — désactivé aujourd'hui) et `EInoExternalize` (signifiait « transient »/non persisté — à ne jamais cocher, cette exclusion n'étant plus honorée par le moteur : la cocher ne rendrait pas l'attribut transient, contrairement à ce que son nom suggère).

**Propriétés sur les rôles d'association (`AssociationEnd`)** — nuance importante confirmée par Cédric Marin : `structural.partOf` et `structural.isToDelete` sont **implicites pour les compositions et agrégations** (le sens principal y est porté nativement par la sémantique de la relation) et ne deviennent réellement à renseigner explicitement que **pour les associations pures** :
- `structural.partOf` — sur lequel des deux rôles le champ est physiquement stocké. Convention pour une association pure : le rôle porté par la cardinalité la plus faible (souvent 1), pour éviter de stocker des dizaines de milliers de références côté « cible ».
- `structural.isToDelete` — suppression en cascade de l'élément lié. Pertinent surtout pour les associations pures (une composition/agrégation supprime déjà en cascade par nature).
- `persistency.optional` — la persistance n'est pas obligée de stocker dans ce sens ; optimisation pour les cardinalités très élevées côté opposé.
- `Semantic.link.source` / `Semantic.link.target` — sur une métaclasse `SemanticLinkMetaclass`, indique explicitement quel rôle est la source et lequel est la cible du lien, indépendamment du sens de la composition. Convention : un lien appartient par composition à sa source ; il existe de rares exceptions (ex. cité par Cédric Marin : `DataFlow`).

**La propriété `Abstract`** (onglet standard `UML - Class`, indépendante de tout profil) : cochée, aucune instance directe de la métaclasse ne peut être créée — génère une interface/classe Java abstraite. S'applique aussi aux relations : une relation abstraite ne donne lieu à aucun stockage réel, elle sert de « relation chapeau » dont d'autres relations concrètes sont des sous-ensembles (`is a subset of`). **Pourquoi ça nous concerne concrètement** : `ConnectorAsUsage` est la seule classe abstraite parmi les 34 cas d'héritage multiple (confirmé via `isIsAbstract()` sur le modèle réel) — le script devra reporter cette propriété.

**Correspondance résumée avec le code généré** — point de vigilance confirmé par Cédric Marin en relecture : la classe et l'API Java d'une métaclasse sont **toujours générées**, quelle que soit la valeur de ses propriétés SemGen. Ce que ces propriétés déterminent, c'est le mode de persistance et de stockage, pas l'existence du code généré (confirme, indépendamment, ce qu'on a vérifié en direct sur ArchiMate/Analyst) :

| Propriété SemGen | Effet réel |
|---|---|
| `structural.node` coché | Instance sauvegardée dans sa propre unité de persistance (fichier dédié), avec sa granularité Teamwork propre. Classe et API générées dans tous les cas. |
| `structural.node` non coché | Instance sauvegardée avec son élément parent (pas de fichier séparé). Classe générée normalement. |
| `semantic.orphans.allowed` | Autorise une instance à exister sans parent de composition (racines de métamodèle) ; sans cette propriété, l'API générée impose la présence d'un parent |
| `Metamodel.isExtension` | À cocher systématiquement sur tout métamodèle destiné à SemGen |
| Type d'attribut | Mappage direct vers le type Java ; énumération → classe enum Java dédiée |
| `Value` | Initialisation du champ Java avec la valeur par défaut |
| `structural.partOf` coché | Classe Java qui porte physiquement le champ de la relation. Optionnel pour composition/agrégation (implicite) ; à renseigner pour les associations pures |
| `structural.isToDelete` coché | Suppression en cascade de l'élément lié. Implicite pour composition/agrégation ; pertinent surtout pour les associations pures |
| `persistency.optional` | Optimisation de stockage pour les cardinalités très élevées |
| `Semantic.link.source`/`target` | Détermine l'accès Java à la source/cible du lien |
| `Abstract` coché | Classe/interface Java abstraite, sans instanciation directe |
| `fpIndexed` / `EInoExternalize` | Aucun effet — non honorées par le moteur de génération actuel. Ne jamais cocher `EInoExternalize` en pensant obtenir un attribut transient : ça ne le rend pas transient |

*Source : documentation technique SemGen (`SemGen_Outil.docx`), mise à jour par Cédric Marin après relecture — illustrée sur le métamodèle ArchiMate, déjà mature et conforme aux conventions.*

**Ce que le script va faire, dans l'ordre :**

1. **Parcourir `reference` intégralement** (182 classes, 209 généralisations, 351 associations) et créer, dans `implementation`, une copie de chaque classe avec ses attributs et opérations propres — sans toucher au package `reference` lui-même, qui reste la référence de fidélité.

2. **Appliquer les deux points de greffe** (points 1 et 2 ci-dessus, une fois validés) : renommer la classe `Element` en `KerMLModelElement` et la faire étendre `ModelElement` de l'infrastructure ; créer `SysMLProject` étendant `AbstractProject`.

3. **Appliquer les stéréotypes et propriétés SemGen** décrits ci-dessus, sur chaque classe/attribut/relation copiés dans `implementation` :
   - Poser `SemGen::Metamodel` sur le composant racine du métamodèle `implementation`, avec `Name`, `Id`, `Version`, `Provider`, `Production namespace`.
   - Pour chaque classe : `SemanticLinkMetaclass` si elle représente une relation (`Association`, `Connector`, `Dependency`, `Succession`, `Flow`…), sinon `Semantic`.
   - Sur chaque classe `Semantic` : cocher `structural.node` sauf si l'élément doit être persisté avec son parent (ex. attributs) ; cocher `semantic.orphans.allowed` uniquement sur `SysMLProject` lui-même, la racine.
   - Sur chaque attribut : poser le stéréotype `Semantic`, le type Java correspondant, et la valeur par défaut (`Value`) quand `reference` en définit une.
   - Sur chaque rôle d'association (`AssociationEnd`) : pour une composition/agrégation, `structural.partOf`/`structural.isToDelete` sont implicites (rien à cocher) ; pour une association pure, `structural.partOf` du côté de la cardinalité la plus faible et `structural.isToDelete` au cas par cas. `persistency.optional` au cas par cas selon la cardinalité. `Semantic.link.source`/`Semantic.link.target` sur les rôles des classes `SemanticLinkMetaclass`.
   - Reporter la propriété `Abstract` déjà présente dans `reference` (aucune décision nouvelle ici — juste la recopier).

4. **Court-circuiter les trois chevauchements** (point 3) : pour `Comment`, `Documentation`, `Dependency`, `MetadataDefinition` et `MetadataUsage`, ne pas créer de nouvelle classe dans `implementation` — à la place, rediriger toute référence à ces concepts, partout où ils apparaissent dans les associations et généralisations copiées depuis `reference`, vers les classes d'infrastructure correspondantes (`Note`, `Dependency`, `Stereotype`/`TaggedValue`). Concrètement : partout où une classe de `reference` a un lien vers `Comment` par exemple, ce lien pointera vers `Note` dans `implementation`.

5. **Résoudre les 34 cas d'héritage multiple** (points 4 et 5), pour chacune des 34 classes concernées. On ne modélise **ni les interfaces `mm.api` ni les classes `mm.impl`** — SemGen génère automatiquement, pour chaque classe stéréotypée `Semantic`/`SemanticLinkMetaclass`, son interface et sa classe d'implémentation. **Vérifié directement sur deux métamodèles déjà générés, indépendamment l'un de l'autre** : ArchiMate (12 classes inspectées à parts égales entre les deux stéréotypes — `Concept`, `Element`, `Relationship`, `Aggregation`, `Composition`…) et Modelio Analyst (21 classes — `AnalystProject`, `Requirement`, `Risk`, `Goal`, `KPI`, `Dictionary`…). Dans les deux cas, 0 interface sans son `XImpl` correspondant, et l'implémentation ajoute systématiquement deux classes internes de plus par concept, `XData` et `XSmClass`, elles aussi générées automatiquement (63 classes `mm.impl` pour 21 interfaces `mm.api` côté Analyst — exactement 3 pour 1). Le script n'a donc qu'à préparer la structure du modèle pour que ce mécanisme produise le bon résultat :
   - Ne garder qu'**une seule généralisation réelle** vers l'axe primaire (celui qui gagne `extends`) — c'est elle que SemGen traduira en héritage Java, aussi bien pour l'interface générée que pour la classe d'implémentation générée.
   - Pour chaque axe secondaire, remplacer la généralisation par la relation/le stéréotype SemGen approprié qui signale « cette classe réalise aussi cette interface » (le mécanisme précis reste à confirmer — cf. point ouvert ci-dessous ; ce qui est vérifié, c'est que l'interface+impl de l'axe secondaire existeront déjà, pas comment le lier depuis la classe primaire). Comme l'axe secondaire est lui-même une classe déjà modélisée, SemGen génère déjà son interface et sa propre classe d'implémentation — rien de plus à créer à ce niveau.
   - Pour porter l'état des 17 cas où l'axe secondaire a du contenu réel (point 5), ajouter dans `implementation` un **attribut composé**, sur la classe primaire, typé par l'axe secondaire lui-même. L'objet délégué est simplement une instance de la classe d'implémentation que SemGen a déjà générée pour cet axe secondaire (ex. `AttributeDefinitionImpl` porte un champ de type `DataType`, instancié via le `DataTypeImpl` que SemGen a généré pour la classe `DataType`). Pour les 17 cas « marqueurs purs », l'interface existe (générée automatiquement) mais l'attribut composé est superflu — la classe secondaire n'a rien à porter.
   - Gérer le cas particulier à 3 parents (`FlowUsage`, point 22) avec ses deux attributs composés.

6. **Vérifier le résultat** : à la fin, comparer `implementation` à `reference` (mêmes 182 classes présentes, mêmes attributs/opérations, mêmes associations — modulo les redirections du point 3) pour s'assurer qu'aucune classe, attribut ou relation n'a été perdu en chemin. Même logique d'audit que celle déjà appliquée sur `reference` lui-même (0 écart toléré par rapport à la source).

**Pourquoi un script plutôt qu'une transformation manuelle** : `reference` compte 182 classes — refaire cette greffe à la main serait long et source d'erreurs, et surtout non reproductible si `reference` est corrigé plus tard (coquilles, mises à jour de spec) ou si une des règles ci-dessus change. Un script réexécutable permet de régénérer `implementation` à l'identique à chaque fois, à partir des mêmes règles.

Ce point découle mécaniquement des points 1 à 5 — il est mentionné ici pour que l'équipe sache ce qui suit une fois ces points validés, et pour resituer l'effort restant : la partie modélisation/conception est faite, il reste l'implémentation outillée de ce qui a été décidé.

---

## Points ouverts / non couverts par le plan actuel

- **Mécanisme SemGen exact pour lier l'axe secondaire** : confirmé sur ArchiMate et Analyst (33 classes au total, section 6) que chaque classe stéréotypée génère bien son interface + son `XImpl` — ce point n'est plus en question. Reste ouvert : le moyen concret de dire « cette classe réalise aussi cette interface » sans généralisation UML classique. **Recherché sans succès dans le modèle Modelio live, sur trois métamodèles générés par SemGen** : le métamodèle `Infrastructure` lui-même (19 classes, `platform.core`), `archimate` (123 classes) et `analyst` (21 classes) — 163 classes au total, 0 classe à 2+ généralisations. Aucun des trois n'a jamais eu besoin de résoudre ce cas précis. `uml` a bien un dossier au même nom de convention (`uml.metamodel.api`/`uml.metamodel.impl`), mais les deux composants sont des coquilles vides (aucun package de namespace, aucune interface) — l'implémentation UML de Modelio n'est donc pas générée par SemGen, malgré l'héritage multiple réel d'UML (`Class`, `Property`…), et ne sert pas d'exemple exploitable. Il n'existe pas de précédent à copier dans cette installation.

  **Cédric Marin lui-même n'est pas certain du mécanisme** — sur sa suggestion, un modèle de test a été construit directement dans le profil `SemGenProfile` (module `SemGen`) pour trancher empiriquement plutôt que de deviner : `sysml2::modelio.sysml2::SemGenTest` avec `SemGenTestMetamodel` (Component, stéréotypé `Metamodel`), `TestPrimary`/`TestSecondary` (Class, stéréotypées `Semantic`), et `TestRealizesSecondary` — un `InformationFlow` de `TestPrimary` vers `TestSecondary` (les deux stéréotypes candidats du profil, `SemGenAllowedDependency` et `SemGenAllowedLink`, ciblent tous les deux `InformationFlow`, pas `Dependency`).

  **Résultat 1, testé sur les deux candidats — négatif pour les deux** : `SemGenAllowedDependency` génère sans erreur, mais `TestPrimaryImpl.getRealized()` ne montre que `TestPrimary` (l'interface générée pour sa propre classe) — pas `TestSecondary`. Reproduit deux fois à l'identique, ce n'est pas un hasard. `SemGenAllowedLink`, testé en substitution sur le même flux, fait planter le générateur (`NullPointerException` interne au moteur SemGen pendant « Preparing implementation classes for TestPrimary ») — pas une piste exploitable sans configuration supplémentaire inconnue.

  **Résultat 2, décisif — SemGen face à un vrai héritage multiple UML** : troisième test, ajout de `TestChild` avec deux vraies généralisations directes (`TestChild :> TestPrimary`, `TestChild :> TestSecondary`), pour voir si SemGen le résout tout seul (comme le flattening EMF). Génération réussie, sans erreur ni avertissement spécifique — mais **le deuxième parent est purement et simplement perdu** : l'interface générée `TestChild` n'étend que `TestPrimary` ; `TestChildImpl` n'étend que `TestPrimaryImpl` ; aucune trace de `TestSecondary`/`TestSecondaryImpl` nulle part, ni en `extends` ni en délégation. Contrairement à EMF (qui garde les deux parents sur l'interface et n'en perd qu'un côté impl), SemGen **supprime silencieusement** l'axe secondaire dès qu'un vrai héritage multiple lui est soumis, sans avertissement dédié (`TestPrimary`/`TestSecondary` avaient eu des warnings « no parent class » plus tôt dans le log ; `TestChild`, lui, n'en a eu aucun — SemGen était satisfait d'avoir trouvé « un » parent).

  **Résultat 3 — `Realization` UML classique, négatif** : quatrième test, `TestGrandchild` (généralisation réelle vers `TestPrimary` seulement) reçoit en plus un `ElementRealization` UML standard vers `TestSecondary`, sans aucun stéréotype SemGen dessus. Génération propre, aucune erreur. Résultat identique aux essais précédents : l'interface `TestGrandchild` n'étend que `TestPrimary`, `TestGrandchildImpl` n'étend que `TestPrimaryImpl`, et `getRealized()` sur `TestGrandchildImpl` ne montre que sa propre interface `TestGrandchild` — le `Realization` vers `TestSecondary` est purement et simplement ignoré par le générateur, comme s'il n'existait pas.

  **Résultat 4, corrigé — stéréotype `SemGenManual`, positif une fois isolé correctement** : un premier essai avec `SemGenManual` appliqué en plus de `Semantic` (toujours présent) n'a montré aucun effet — biais méthodologique identifié après coup : les deux stéréotypes actifs en même temps laissent `Semantic` dominer, donc ce premier essai ne testait rien de nouveau. Corrigé en retirant `Semantic` (ne laissant que `SemGenManual`) et en accédant directement aux fichiers `.java` générés sur disque (`JavaDesigner` écrit dans `$(Project)/../../eclipse`, chemin réel repéré et lisible directement) plutôt qu'en passant par le modèle. Plusieurs essais via ScriptServer ont d'abord donné des résultats contradictoires d'une régénération à l'autre (fichier intact, puis supprimé, puis régénéré — signe de désynchronisation entre l'état modifié via ScriptServer et le cache lu par la génération déclenchée depuis l'IHM). **Un test propre, refait entièrement depuis l'IHM (changement de stéréotype + sauvegarde + redémarrage complet de Modelio + génération, sans aucun script entre les deux) donne un résultat net et reproductible** : sur une régénération qui touche toutes les autres classes du métamodèle de test (nouveaux timestamps), les 4 fichiers de `TestGrandchild` restent strictement intacts, horodatage et contenu inchangés. **`SemGenManual`, une fois `Semantic` retiré de la classe, fait bien sortir cette classe du périmètre de génération — SemGen/JavaDesigner ne la touchent plus jamais.**

  **Piste complémentaire — la fonction « reverse » de JavaDesigner, confirmée fiable une fois correctement ciblée** : JavaDesigner sait relire un fichier `.java` écrit à la main et en extraire les relations vers le modèle. Testé en ajoutant `implements TestSecondary` à la main dans `TestGrandchildImpl.java` (classe déjà sortie du périmètre SemGen via `SemGenManual`), puis en lançant un reverse. Résultat : `TestGrandchildImpl.getRealized()` montre bien **`['TestGrandchild', 'TestSecondary']`** après coup — la relation est correctement extraite et réconciliée sur le même élément (`@objid` identique à celui du squelette généré, pas de doublon créé). **Premier essai lancé depuis le package conteneur `SemGenOutput`** (construit à la main plus tôt dans la session, pas une unité de génération réelle) : effet de bord sérieux, l'intégralité de l'arborescence générée s'est retrouvée réorganisée/aplatie à la racine de ce package. **Deuxième essai, refait sur un `SemGenOutput` vidé et régénéré à neuf, cette fois en lançant le reverse directement depuis les composants `api`/`impl` eux-mêmes** (les vraies unités que JavaDesigner gère, pas leur conteneur) : **aucun aplatissement, arborescence intacte, `TestGrandchildImpl`/`TestGrandchildData`/`TestGrandchildSmClass` toujours correctement imbriqués au même endroit que les autres classes**, et la relation `getRealized(): ['TestGrandchild', 'TestSecondary']` toujours correcte. Confirme que le problème initial était un mauvais périmètre de déclenchement (le conteneur artisanal `SemGenOutput`), pas un défaut de l'outil — **la fonction reverse de JavaDesigner est fiable et utilisable, à condition de la déclencher depuis les composants `api`/`impl` et jamais depuis un package englobant construit à la main**.

  **Conclusion, définitive** : SemGen lui-même ne sait exprimer aucune deuxième relation de réalisation par un mécanisme de modélisation classique — confirmé sur `SemGenAllowedDependency`, `SemGenAllowedLink`, une vraie double généralisation UML, et un `Realization` UML classique, quatre résultats négatifs. Mais deux mécanismes combinés résolvent le problème proprement : `SemGenManual` (seul, `Semantic` retiré) **sort la classe du périmètre de régénération**, protégeant tout code écrit à la main dans `XImpl` d'un écrasement automatique ; et la fonction **reverse** de JavaDesigner, correctement ciblée sur `api`/`impl`, permet en plus de faire remonter cette relation dans le modèle pour la traçabilité, sans effet de bord. La marche à suivre pour les 34 cas :
  1. **Axe primaire** : une seule généralisation UML réelle par classe (celle qui porte le plus d'attributs/opérations propres, cf. point 4), stéréotypée `Semantic` comme d'habitude — SemGen la génère automatiquement (`interface X extends Primary`, `class XImpl extends PrimaryImpl implements X`), aucune intervention manuelle nécessaire à ce stade.
  2. **Générer une première fois** normalement (SemGen puis JavaDesigner) pour obtenir le squelette standard.
  3. **Basculer le stéréotype** : retirer `Semantic`, appliquer `SemGenManual` sur la classe, sauvegarder.
  4. **Axe secondaire** : écrire à la main, une seule fois, directement dans `XImpl` — le petit objet délégué (cf. point 5) plus `implements Secondary` et les méthodes de délégation.
  5. **Optionnel, pour la traçabilité dans le modèle** : lancer un reverse JavaDesigner ciblé sur les composants `api`/`impl` (jamais sur un package englobant construit à la main) pour faire apparaître la relation dans le modèle (`getRealized()`).
  6. Ne plus jamais retoucher ce fichier à la main au-delà de l'étape 4 — confirmé qu'il survit aux régénérations futures des autres classes du métamodèle.
  7. Si l'axe primaire de ce cas doit changer plus tard : rebasculer temporairement sur `Semantic`, régénérer le squelette à neuf, rebasculer sur `SemGenManual`, réappliquer la modification manuelle.

  Le modèle de test (`SemGenTest`) est laissé en l'état dans le modèle Modelio live comme preuve reproductible de ces résultats.
- *(à compléter — y a-t-il d'autres sujets qu'Antonin ou l'équipe voudront trancher qui ne sont pas dans cette liste ?)*
