# Points à trancher — greffe SysML v2/KerML sur l'infrastructure Modelio

Document de travail préparant la demande d'Antonin : la liste des décisions sur lesquelles nous avons besoin d'un arbitrage, extraites du plan d'implémentation (`slides.md`). Chaque point renvoie à la partie du deck qui détaille le raisonnement et les exemples.

## 1. Point de greffe sur l'infrastructure

**Proposition** : le point de greffe est `ModelElement`. `KerML::Element` est renommé, dans `reference/design` uniquement, en `KerMLModelElement`, et étend directement `ModelElement`.

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

**Proposition** : ne pas réimplémenter dans `reference/design` ce que l'infrastructure Modelio fait déjà nativement :

| Concept KerML (nom qualifié) | Infrastructure Modelio (nom qualifié) | Traitement proposé | Achoppements |
|---|---|---|---|
| `KerML::Root::Annotations::Comment`, `KerML::Root::Annotations::Documentation` | `infrastructure::Note` | Mapper sur `Note` | (1) `Comment` a 3 formes textuelles (explicite avec `about`, implicite, avec `locale`) — `Note` devra porter la `locale` et la contrainte structurelle propre à `Documentation` (élément documenté = propriétaire). (2) Différence structurelle plus profonde : en SysML v2, un `Comment` peut être lié à **plusieurs** éléments à la fois (`about A, B`) ; en Modelio, une `Note` est **contenue** dans l'unique élément qu'elle documente (composition) |
| `KerML::Root::Dependencies::Dependency` | `infrastructure::Dependency` | Alias direct | (1) Le `Dependency` de Modelio peut porter des comportements/stéréotypes hérités du contexte UML — à vérifier qu'aucun ne s'applique par erreur à un lien KerML. (2) Pas de support n-aire côté Modelio : KerML permet `dependency X to Y, Z;` (un client, plusieurs fournisseurs, en une seule relation) ; Modelio ne représente qu'un lien binaire — une dépendance n-aire devra être décomposée en plusieurs `Dependency` binaires (`X->Y`, `X->Z`) |
| `SysML::Systems::Metadata::MetadataDefinition`, `SysML::Systems::Metadata::MetadataUsage` | `infrastructure::Stereotype` + `infrastructure::TaggedValue` | Mapper sur le sous-système Stereotype/TaggedValue | Le plus significatif des trois : un `MetadataUsage` s'attache à plusieurs cibles à la fois en une seule instance (`about A, B, C`). En Modelio, un `Stereotype` (définition) peut bien être appliqué à plusieurs éléments, mais **chaque application** (`ExtensionValue`) ne concerne qu'un seul élément de base |

*Noms qualifiés côté KerML/SysML vérifiés dans les XMI de spec (`KerML.xmi`/`SysML.xmi`). Côté Modelio, le préfixe de package (`infrastructure::`) est confirmé mais le chemin complet reste à valider une fois ScriptServer de nouveau accessible (hors ligne au moment de la rédaction).*

**Y a-t-il d'autres chevauchements ?** Relecture des 19 classes du package `infrastructure` (voir diagramme, Partie 2) face aux 182 classes de `reference/spec` : aucun autre chevauchement conceptuel net trouvé. Le reste du package infrastructure se répartit en (a) plomberie de support pour les 3 chevauchements ci-dessus — `NoteType`, `TagType`, `TagParameter`, `MetaclassReference` — à examiner au moment de l'implémentation mais pas des concepts KerML/SysML séparés, et (b) des concepts propres à Modelio sans équivalent KerML/SysML — `Resource`/`Document`/`AbstractResource` (pièces jointes), `ExternProcessor`/`ExternElement` (intégration outillage), `Profile` (regroupement de Stereotypes), `MethodologicalLink` (Dependency spécialisé). `AbstractProject` est déjà couvert au point 2.

**Question à trancher** : valide-t-on ces trois mappings (plutôt que de dupliquer ces concepts dans `reference/design`), et confirme-t-on qu'il n'y a pas de 4ᵉ chevauchement à traiter ?

*Réf. : Partie 3, slides « Trois chevauchements concrets » à « Chevauchement 3b ».*

---

## 4. Stratégie générale pour l'héritage multiple KerML → Java

**Constat** : 34 classes de `reference/spec` ont deux (ou trois) super-types directs — impossible à traduire tel quel en Java (une seule classe mère autorisée).

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

### Ce que porte l'axe délégué, cas par cas

**Design final, validé par génération réelle (SemGen + JavaDesigner)** : l'objet délégué n'est PAS une classe synthétique dédiée (un temps envisagée sous le nom `<AxeSecondaire>Behavior`, avec sa propre hiérarchie de généralisations pour couvrir tout l'héritage réel de l'axe secondaire). Sur suggestion d'Antonin, la classe primaire porte une référence composée vers **la vraie classe de l'axe secondaire elle-même** (ex. `AttributeDefinition.dataType : DataType`, en utilisant le `DataType` déjà modélisé, pas une classe `DataTypeBehavior` inventée).

**Un détour, corrigé** : la première implémentation de cette idée utilisait un `Attribute` composé (`AttributeDefinition.getOwnedAttribute()`) typé directement par la classe secondaire — plus simple à construire, mais **invalide pour SemGen/JavaDesigner en pratique**. Testé sur le vrai modèle KerML généré : `AttributeImpl.getClassifier`, `AssociationStructureImpl.getStructure` et 5 autres accesseurs échouent à la génération avec `"n'est pas un élément java valide ... vérifier le stéréotype <<JavaClass>>"`. Confirmé par sondage : `<<JavaClass>>` existe mais n'est utilisé par aucune classe du métamodèle Analyst réel (0 sur plusieurs milliers de nœuds), et — constat plus général — **toute référence inter-classes dans l'ensemble du modèle spec/design est modélisée par une `Association` UML, jamais par un `Attribute`** (`Attribute` n'y sert qu'aux types primitifs). Le mécanisme final remplace donc l'attribut composé par une **association composée** :
- Sur la classe primaire : un bout d'association nommé comme l'ancien attribut (ex. `dataType`), multiplicité `1..1`, agrégation `composite` (portée sur ce bout, celui du tout — cf. la convention déjà en usage pour toute composition dans ce modèle), stéréotype `Semantic`.
- Sur la classe secondaire : le bout opposé, multiplicité `0..1`, stéréotype `Semantic` (sans le stéréotype `Semantic` sur les deux bouts, JavaDesigner échoue avec l'avertissement « non semantic association/role » puis une `StringIndexOutOfBoundsException`). Ce bout opposé porte lui aussi un vrai nom (convention retenue : le nom de la classe primaire, en minuscule initiale, ex. `attributeDefinition`) — **jamais une chaîne vide**. Un bout `AssociationEnd` sans nom (`""`) fait planter SemGen/JavaDesigner avec la même `StringIndexOutOfBoundsException`, découvert après coup sur le vrai modèle KerML (33 cas concernés, dont le bout opposé de chacune des 33 associations composées avait été créé sans nom initialement) et confirmé en isolation sur un métamodèle jetable.
- Les deux bouts ont leur `Target`/`Source` explicitement renseignés (`AssociationEnd.setTarget()`/`setSource()` — une méthode réelle de l'API, distincte de `setOpposite()`, sans quoi Modelio affiche `<no type>` dans l'IHM même quand tout le reste est correct).
- Validé de bout en bout sur un métamodèle de test jetable (`SemGenTest`) avant application au vrai modèle, pour éviter des allers-retours coûteux sur `reference/design` : génération SemGen + JavaDesigner réussie (`GENERATION SUCCESSFUL`) avec ce patron exact.
- Autre pré-requis découvert au passage : toute classe générée doit porter **au moins une vraie `Generalization`**, même vers une classe étrangère au métamodèle (ex. `ModelElement`, infrastructure Modelio native) — une classe sans aucune généralisation fait planter `MetaclassLoadGenerator` avec la même `StringIndexOutOfBoundsException`. Dans `reference/design`, c'est déjà systématiquement le cas (toutes les classes descendent de `KerMLModelElement`/`ModelElement` ou `AbstractProject`), donc sans impact sur le script réel — mais un piège si on reproduit ce montage ailleurs sans y penser.
- **Validation finale sur le vrai modèle** : génération SemGen + JavaDesigner du composant `KerML` complet (81 métaclasses) réussie (`GENERATION SUCCESSFUL`), avec ce patron appliqué aux 33 cas réels.

**Correction annexe, découverte pendant cette validation — KerML ne doit référencer aucune classe SysML** : `reference/spec` (miroir fidèle des diagrammes de la spec) contenait 32 associations où une classe KerML possède un bout nommé (diagramme uniquement, ex. `Element.exposingView : ViewUsage`) pointant vers une classe SysML — jamais déclarées comme attribut formel dans le texte normatif KerML lui-même (vérifié par grep sur le texte intégral de la spec KerML), seulement visibles comme label de rôle sur le diagramme UML de la spec SysML (le côté formellement déclaré, ex. `/exposedElement : Element` sur `ViewUsage`, va bien dans le sens attendu SysML→KerML). Conceptuellement, KerML ne doit jamais référencer/générer quoi que ce soit vers SysML (couche fondation vs. couche construite dessus). Techniquement, Modelio impose qu'une association a toujours ses deux bouts possédés par deux classes différentes (règle `E211`) — impossible de « déplacer » la possession du bout côté KerML vers SysML sans casser structurellement l'association. Solution retenue : ces 32 associations diagramme-seul sont supprimées entièrement de `reference/design` (les deux bouts, `reference/spec` reste intouché) — aucune perte de contenu réellement spécifié, puisque rien n'était formellement déclaré côté KerML pour commencer.

Raisons de garder ce design malgré le détour :
- C'est la version la plus fidèle du patron cité au point 4 (*Replace Inheritance with Delegation* : détenir une référence vers une vraie instance du type délégué, pas construire une hiérarchie parallèle).
- Le risque de confusion évoqué initialement (un `DataTypeImpl` interne à `AttributeDefinitionImpl` serait-il confondu avec un vrai `DataType` du modèle utilisateur ?) ne se vérifie pas dans la pratique Modelio : la navigation générée est basée sur la possession par composition, pas sur un scan global par métaclasse — un délégué privé n'est atteignable qu'en passant par `AttributeDefinition` elle-même.
- Beaucoup plus simple à construire et à maintenir qu'une hiérarchie de classes déléguées : aucune classe supplémentaire, aucun choix entre dupliquer le délégué par cas ou le partager dans un package neutre — juste une association de plus, du même type que toutes les autres associations déjà présentes dans le modèle.

**Traçabilité** : chacune des 33 associations composées (34 cas moins les 2 exclus comme chevauchements, `MetadataDefinition`/`MetadataUsage`, plus le cas 22 `FlowUsage` qui en compte deux) porte une `Note` expliquant qu'elle ne provient pas de `reference/spec` mais a été ajoutée pour porter l'axe secondaire — attachée via `note.setSubject(boutPrimaire)`, visible directement sur le bout d'association côté classe primaire dans le modèle.

Liste des 33 références composées (primaire → nom du bout → type, `= vraie classe`) :

1. `Association.classifier : Classifier` — 2. `AssociationStructure.structure : Structure` — 3. `Connector.relationship : Relationship` — 4. `Flow.step : Step` — 5. `Interaction.association : Association` — 6. `MetadataFeature.annotatingElement : AnnotatingElement` — 7. `SuccessionFlow.succession : Succession` — 8. `ActionDefinition.behavior : Behavior` — 9. `ActionUsage.step : Step` — 10. `AssertConstraintUsage.invariant : Invariant` — 11. `AttributeDefinition.dataType : DataType` — 12. `BindingConnectorAsUsage.bindingConnector : BindingConnector` — 13. `CalculationDefinition.function : Function` — 14. `CalculationUsage.expression : Expression` — 15. `ConnectionDefinition.associationStructure : AssociationStructure` — 16. `ConnectionUsage.connectorAsUsage : ConnectorAsUsage` — 17. `ConnectorAsUsage.connector : Connector` — 18. `ConstraintDefinition.predicate : Predicate` — 19. `ConstraintUsage.booleanExpression : BooleanExpression` — 20. `ExhibitStateUsage.stateUsage : StateUsage` — 21. `FlowDefinition.interaction : Interaction` — 22. `FlowUsage.connectorAsUsage : ConnectorAsUsage` **et** `FlowUsage.flow : Flow` (seul cas à deux attributs composés) — 23. `IncludeUseCaseUsage.useCaseUsage : UseCaseUsage` — 24. `ItemDefinition.structure : Structure` — 25. `MembershipExpose.membershipImport : MembershipImport` — 26/27. `MetadataDefinition`/`MetadataUsage` : exclus (chevauchements, point 3) — 28. `NamespaceExpose.namespaceImport : NamespaceImport` — 29. `OccurrenceDefinition.class : Class` — 30. `PerformActionUsage.eventOccurrenceUsage : EventOccurrenceUsage` — 31. `PortDefinition.structure : Structure` — 32. `SatisfyRequirementUsage.assertConstraintUsage : AssertConstraintUsage` — 33. `SuccessionAsUsage.succession : Succession` — 34. `SuccessionFlowUsage.successionFlow : SuccessionFlow`.

Pour le contenu réel que chaque axe secondaire porte concrètement (attributs/opérations propres, le cas échéant), se référer directement à la classe elle-même dans `reference/spec`/`reference/design` — puisque le délégué EST cette classe, il n'y a plus de distinction à documenter séparément entre « délégué avec contenu réel » et « délégué marqueur pur » : c'est simplement la question de savoir si la classe secondaire a, par elle-même, des attributs/opérations propres dans la spec.

**Question à trancher** : valide-t-on la règle générale (point 4) et laisse-t-on les 34 cas en découler automatiquement, ou souhaitez-vous une revue cas par cas ? Si revue cas par cas : y a-t-il des cas qui vous semblent contestables à première vue ?

*Réf. : Partie 4, slides « Cas 1 · Association » à « Cas 34 · SuccessionFlowUsage », résumées dans « Au bilan : quelles classes deviennent des interfaces pures ».*

---

## 6. Prochaine grosse étape : le script de transformation `reference/spec` → `reference/design`

**Objectif** : une fois les points 1 à 5 tranchés, un script Jython construit `reference/design` automatiquement à partir de `reference/spec`, en appliquant mécaniquement les règles décidées plus haut plutôt que de recopier les 182 classes à la main.

**Structure des packages** : `reference` se subdivise en deux sous-packages — `reference/spec`, miroir UML pur de la spec SysML v2/KerML, sans aucun stéréotype SemGen, qui reste la référence de fidélité intouchée par le script ; et `reference/design`, le modèle prêt pour SemGen (patron de délégation appliqué, greffe sur l'infrastructure Modelio, chevauchements résolus, stéréotypes SemGen posés). Un package séparé au niveau racine, `implementation`, est réservé par convention au seul résultat de la chaîne de génération SemGen/JavaDesigner (`mm.api`/`mm.impl`) — il n'est jamais construit ni édité directement, il est produit en lançant SemGen puis JavaDesigner sur `reference/design`. La bascule de stéréotype (`Semantic` → `SemGenManual`, une fois par cas) se fait sur la classe source dans `reference/design` ; c'est ensuite dans le fichier `.java` généré pour cette classe, sous `implementation`, que l'axe secondaire est écrit à la main (cf. Points ouverts).

### SemGen : les stéréotypes et propriétés qu'on va appliquer

SemGen est l'outil interne Modelio qui génère `mm.api`/`mm.impl` à partir d'un métamodèle stéréotypé selon ses conventions (menu contextuel sur le composant métamodèle → SemGen → Generate Metamodel). Un second outil, JavaDesigner, prend ensuite `mm.api`/`mm.impl` pour produire le code Java définitif, packagé en plugin Eclipse. Ce que le script doit poser sur le modèle pour que cette chaîne fonctionne :

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

1. **Parcourir `reference/spec` intégralement** (182 classes, 209 généralisations, 351 associations) et créer, dans `reference/design`, une copie de chaque classe avec ses attributs et opérations propres — sans toucher au package `reference/spec` lui-même, qui reste la référence de fidélité.

2. **Appliquer les deux points de greffe** (points 1 et 2 ci-dessus, une fois validés) : renommer la classe `Element` en `KerMLModelElement` et la faire étendre `ModelElement` de l'infrastructure ; créer `SysMLProject` étendant `AbstractProject`.

3. **Appliquer les stéréotypes et propriétés SemGen** décrits ci-dessus, sur chaque classe/attribut/relation copiés dans `reference/design` :
   - Poser `SemGen::Metamodel` sur le composant racine du métamodèle `reference/design`, avec `Name`, `Id`, `Version`, `Provider`, `Production namespace`.
   - Pour chaque classe : `SemanticLinkMetaclass` si elle représente une relation (`Association`, `Connector`, `Dependency`, `Succession`, `Flow`…), sinon `Semantic`.
   - Sur chaque classe `Semantic` : cocher `structural.node` sauf si l'élément doit être persisté avec son parent (ex. attributs) ; cocher `semantic.orphans.allowed` uniquement sur `SysMLProject` lui-même, la racine.
   - Sur chaque attribut : poser le stéréotype `Semantic`, le type Java correspondant, et la valeur par défaut (`Value`) quand `reference/spec` en définit une.
   - Sur chaque rôle d'association (`AssociationEnd`) : pour une composition/agrégation, `structural.partOf`/`structural.isToDelete` sont implicites (rien à cocher) ; pour une association pure, `structural.partOf` du côté de la cardinalité la plus faible et `structural.isToDelete` au cas par cas. `persistency.optional` au cas par cas selon la cardinalité. `Semantic.link.source`/`Semantic.link.target` sur les rôles des classes `SemanticLinkMetaclass`.
   - Reporter la propriété `Abstract` déjà présente dans `reference/spec` (aucune décision nouvelle ici — juste la recopier).

4. **Court-circuiter les trois chevauchements** (point 3) : pour `Comment`, `Documentation`, `Dependency`, `MetadataDefinition` et `MetadataUsage`, ne pas créer de nouvelle classe dans `reference/design` — à la place, rediriger toute référence à ces concepts, partout où ils apparaissent dans les associations et généralisations copiées depuis `reference/spec`, vers les classes d'infrastructure correspondantes (`Note`, `Dependency`, `Stereotype`/`TaggedValue`). Concrètement : partout où une classe de `reference/spec` a un lien vers `Comment` par exemple, ce lien pointera vers `Note` dans `reference/design`.

5. **Résoudre les 34 cas d'héritage multiple** (points 4 et 5), pour chacune des 34 classes concernées. On ne modélise **ni les interfaces `mm.api` ni les classes `mm.impl`** — SemGen génère automatiquement, pour chaque classe stéréotypée `Semantic`/`SemanticLinkMetaclass`, son interface et sa classe d'implémentation. **Vérifié directement sur deux métamodèles déjà générés, indépendamment l'un de l'autre** : ArchiMate (12 classes inspectées à parts égales entre les deux stéréotypes — `Concept`, `Element`, `Relationship`, `Aggregation`, `Composition`…) et Modelio Analyst (21 classes — `AnalystProject`, `Requirement`, `Risk`, `Goal`, `KPI`, `Dictionary`…). Dans les deux cas, 0 interface sans son `XImpl` correspondant, et l'implémentation ajoute systématiquement deux classes internes de plus par concept, `XData` et `XSmClass`, elles aussi générées automatiquement (63 classes `mm.impl` pour 21 interfaces `mm.api` côté Analyst — exactement 3 pour 1). Le script n'a donc qu'à préparer la structure du modèle pour que ce mécanisme produise le bon résultat :
   - Ne garder qu'**une seule généralisation réelle** vers l'axe primaire (celui qui gagne `extends`) — c'est elle que SemGen traduira en héritage Java, aussi bien pour l'interface générée que pour la classe d'implémentation générée.
   - Pour chaque axe secondaire, ne rien modéliser côté relation dans `reference/design` — pas de généralisation, pas de `Realization`, aucun stéréotype SemGen ne sait exprimer « cette classe réalise aussi cette interface » (5 mécanismes testés en direct sur le modèle Modelio, tous négatifs — détail complet cf. Points ouverts). Comme l'axe secondaire est lui-même une classe déjà modélisée, SemGen génère déjà son interface et sa propre classe d'implémentation — rien de plus à créer à ce niveau dans `reference/design`. Le lien `implements Secondary` lui-même se fait plus tard, à la main, directement dans le fichier `.java` généré sous `implementation` (cf. Points ouverts pour la procédure complète) — ce n'est pas quelque chose que ce script produit.
   - Pour chacun des 32 cas traités (34 moins les 2 exclus comme chevauchements), ajouter dans `reference/design` une **association composée**, entre la classe primaire et l'axe secondaire lui-même (pas de classe déléguée synthétique — cf. point 5 « Ce que porte l'axe délégué », design final après correction d'un premier essai en `Attribute` invalide pour SemGen). Ajoutée uniformément, y compris pour les cas « marqueurs purs » (simplicité > micro-optimisation). Chaque association composée porte une `Note` (`note.setSubject(boutPrimaire)`) documentant qu'elle ne vient pas de `reference/spec` et à quel cas elle correspond — pour qu'on puisse la distinguer d'une association réelle de la spec en inspectant `reference/design`.
   - Gérer le cas particulier à 3 parents (`FlowUsage`, point 22) avec ses deux associations composées.

6. **Vérifier le résultat** : à la fin, comparer `reference/design` à `reference/spec` (mêmes 182 classes présentes, mêmes attributs/opérations, mêmes associations — modulo les redirections du point 3) pour s'assurer qu'aucune classe, attribut ou relation n'a été perdu en chemin. Même logique d'audit que celle déjà appliquée sur `reference/spec` lui-même (0 écart toléré par rapport à la source).

**Pourquoi un script plutôt qu'une transformation manuelle** : `reference/spec` compte 182 classes — refaire cette greffe à la main serait long et source d'erreurs, et surtout non reproductible si `reference/spec` est corrigé plus tard (coquilles, mises à jour de spec) ou si une des règles ci-dessus change. Un script réexécutable permet de régénérer `reference/design` à l'identique à chaque fois, à partir des mêmes règles.

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
  1. **Dans `reference/design`** : axe primaire = une seule généralisation UML réelle par classe (celle qui porte le plus d'attributs/opérations propres, cf. point 4), stéréotypée `Semantic` comme d'habitude — c'est ce que produit le script du point 6. Aucun lien modélisé pour l'axe secondaire (cf. ci-dessus).
  2. **Générer une première fois** `reference/design` vers `implementation` normalement (SemGen puis JavaDesigner) pour obtenir le squelette standard (`interface X extends Primary`, `class XImpl extends PrimaryImpl implements X`) — aucune intervention manuelle nécessaire à ce stade.
  3. **Basculer le stéréotype** sur la classe, dans `reference/design` : retirer `Semantic`, appliquer `SemGenManual`, sauvegarder. Contrairement aux étapes 2 et 5, celle-ci est scriptable en Jython (`element.addStereotype(...)`/`removeStereotype(...)`, déjà utilisées et confirmées cette session) — un script pourrait l'appliquer aux 34 cas d'un coup une fois leurs squelettes générés, sans passer par l'IHM à chaque fois.
  4. **Axe secondaire** : écrire à la main, une seule fois, directement dans le `XImpl.java` généré sous `implementation` — le petit objet délégué (cf. point 5) plus `implements Secondary` et les méthodes de délégation.
  5. **Optionnel, pour la traçabilité dans le modèle** : lancer un reverse JavaDesigner ciblé sur les composants `api`/`impl` (jamais sur un package englobant construit à la main) pour faire apparaître la relation dans le modèle (`getRealized()`).
  6. Ne plus jamais retoucher ce fichier à la main au-delà de l'étape 4 — confirmé qu'il survit aux régénérations futures des autres classes du métamodèle.
  7. Si l'axe primaire de ce cas doit changer plus tard : rebasculer temporairement sur `Semantic`, régénérer le squelette à neuf, rebasculer sur `SemGenManual`, réappliquer la modification manuelle.

  **Ce qui reste à vérifier** : si le déclenchement de SemGen, JavaDesigner et le reverse (étapes 2 et 5) sont eux aussi accessibles depuis Jython plutôt que seulement via les menus de l'IHM — non testé cette session. Si oui, l'ensemble de la procédure (hors l'écriture à la main de l'étape 4, intrinsèquement manuelle) deviendrait scriptable de bout en bout.

  Le modèle de test (`SemGenTest`) est laissé en l'état dans le modèle Modelio live comme preuve reproductible de ces résultats.
- *(à compléter — y a-t-il d'autres sujets qu'Antonin ou l'équipe voudront trancher qui ne sont pas dans cette liste ?)*
