# Points à trancher — greffe SysML v2/KerML sur l'infrastructure Modelio

> **État actuel 2026-09-16** — Les généralisations multiples réelles sont désormais conservées dans `reference/design`. SemGen `4.0.02` / `semgenerator 1.4.02` génère avec succès KerML (81 métaclasses) et SysML (97 métaclasses) dans `modelio.sysml2::implementation`. Les sections décrivant la délégation manuelle ou les associations composées sont historiques.

> **Mise à jour 2026-09-22** — Les trois retours de Cédric Marin sur `reference/design` sont corrigés en direct et dans la transformation : granularité `structural.node`, doublons de `KerMLModelElement`, et stockage des associations dérivées. Voir point 7.

Document de travail préparant la demande d'Antonin : la liste des décisions sur lesquelles nous avons besoin d'un arbitrage, extraites du plan d'implémentation (`slides.md`). Chaque point renvoie à la partie du deck qui détaille le raisonnement et les exemples.

## 1. Point de greffe sur l'infrastructure

**État vérifié dans le modèle généré** : `KerML::Element` est renommé, dans `reference/design` uniquement, en `KerMLModelElement`. Le Java généré l'intègre via `ecore::EObject` et `mapi::MObject` côté API, puis `KerMLModelElementImpl` via `SmObjectImpl` côté implémentation. `ModelElement` n'est pas la super-classe directe du résultat actuel.

**Distinction importante** : le patron `UmlModelElement extends ModelElement` reste un précédent Modelio, mais ce n'est pas la chaîne effectivement produite pour KerML. Toute évolution vers `ModelElement` devra être décidée séparément et ne doit pas être supposée par les scripts.

**Décision actuelle** : conserver la chaîne générée et documentée ci-dessus ; ne pas modifier le point de greffe pendant la restauration de l'héritage multiple.

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

*Noms qualifiés côté KerML/SysML vérifiés dans les XMI de spec (`KerML-v1.0-20250201.xmi`/`SysML-v2.0-20250201.xmi`). Côté Modelio, le préfixe de package (`infrastructure::`) est confirmé mais le chemin complet reste à valider une fois ScriptServer de nouveau accessible (hors ligne au moment de la rédaction).*

**Y a-t-il d'autres chevauchements ?** Relecture des 19 classes du package `infrastructure` (voir diagramme, Partie 2) face aux 182 classes de `reference/spec` : aucun autre chevauchement conceptuel net trouvé. Le reste du package infrastructure se répartit en (a) plomberie de support pour les 3 chevauchements ci-dessus — `NoteType`, `TagType`, `TagParameter`, `MetaclassReference` — à examiner au moment de l'implémentation mais pas des concepts KerML/SysML séparés, et (b) des concepts propres à Modelio sans équivalent KerML/SysML — `Resource`/`Document`/`AbstractResource` (pièces jointes), `ExternProcessor`/`ExternElement` (intégration outillage), `Profile` (regroupement de Stereotypes), `MethodologicalLink` (Dependency spécialisé). `AbstractProject` est déjà couvert au point 2.

**Question à trancher** : valide-t-on ces trois mappings (plutôt que de dupliquer ces concepts dans `reference/design`), et confirme-t-on qu'il n'y a pas de 4ᵉ chevauchement à traiter ?

*Réf. : Partie 3, slides « Trois chevauchements concrets » à « Chevauchement 3b ».*

---

## 4. Stratégie générale pour l'héritage multiple KerML → Java

**État actuel** : les 34 classes de `reference/spec` ont deux (ou trois) super-types directs. Le correctif SemGen `4.0.01` / `semgenerator 1.4.01` conserve désormais tous les parents dans les interfaces générées et aplatit les membres des parents secondaires dans l'implémentation Java. La contrainte Java reste valable pour une classe concrète (`extends` unique), mais elle ne justifie plus de déformer le métamodèle source.

**Décision** : conserver les généralisations UML réelles dans `reference/design`. SemGen choisit l'axe primaire pour `extends` dans `mm.impl`, expose tous les parents sur `mm.api`, puis aplatit les membres des axes secondaires dans l'implémentation. Les associations composées ajoutées uniquement pour contourner l'ancien SemGen doivent être supprimées lors de la régénération de `reference/design`.

**Réserve** : cette stratégie a été validée sur le probe multi-parent et sur la génération KerML complète (81 métaclasses, `GENERATION SUCCESSFUL`). Les experts Toutatis et la persistance multi-parent restent à vérifier séparément.

*Réf. : Partie 4, slides « Java n'a pas d'héritage multiple » à « Ce n'est pas une approche ad hoc ».*

---

## 5. Les 34 résolutions individuelles

**Trace historique** : le tableau ci-dessous conserve les axes primaire/secondaire identifiés pendant l'étude. Il ne décrit plus une transformation par délégation dans `reference/design` : les deux généralisations doivent maintenant être conservées dans le modèle source.

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

### Ancienne résolution par association composée (historique)

La section suivante documente l'ancien contournement, validé avant le correctif SemGen. Elle sert à expliquer les associations composées actuellement présentes dans `reference/design` et à guider leur suppression. Elle n'est plus une cible de conception.

**Historique** : l'objet délégué n'était pas une classe synthétique dédiée; l'ancienne solution ajoutait une référence composée vers la vraie classe secondaire. Cette solution n'est plus utilisée depuis le correctif SemGen.

**Un détour, corrigé** : la première implémentation de cette idée utilisait un `Attribute` composé (`AttributeDefinition.getOwnedAttribute()`) typé directement par la classe secondaire — plus simple à construire, mais **invalide pour SemGen/JavaDesigner en pratique**. Testé sur le vrai modèle KerML généré : `AttributeImpl.getClassifier`, `AssociationStructureImpl.getStructure` et 5 autres accesseurs échouent à la génération avec `"n'est pas un élément java valide ... vérifier le stéréotype <<JavaClass>>"`. Confirmé par sondage : `<<JavaClass>>` existe mais n'est utilisé par aucune classe du métamodèle Analyst réel (0 sur plusieurs milliers de nœuds), et — constat plus général — **toute référence inter-classes dans l'ensemble du modèle spec/design est modélisée par une `Association` UML, jamais par un `Attribute`** (`Attribute` n'y sert qu'aux types primitifs). Le mécanisme final remplace donc l'attribut composé par une **association composée** :
- Sur la classe primaire : un bout d'association nommé comme l'ancien attribut (ex. `dataType`), multiplicité `1..1`, agrégation `composite` (portée sur ce bout, celui du tout — cf. la convention déjà en usage pour toute composition dans ce modèle), stéréotype `Semantic`.
- Sur la classe secondaire : le bout opposé, multiplicité `0..1`, stéréotype `Semantic` (sans le stéréotype `Semantic` sur les deux bouts, JavaDesigner échoue avec l'avertissement « non semantic association/role » puis une `StringIndexOutOfBoundsException`). Ce bout opposé porte lui aussi un vrai nom (convention retenue : le nom de la classe primaire, en minuscule initiale, ex. `attributeDefinition`) — **jamais une chaîne vide**. Un bout `AssociationEnd` sans nom (`""`) fait planter SemGen/JavaDesigner avec la même `StringIndexOutOfBoundsException`, découvert après coup sur le vrai modèle KerML (33 cas concernés, dont le bout opposé de chacune des 33 associations composées avait été créé sans nom initialement) et confirmé en isolation sur un métamodèle jetable.
- Les deux bouts ont leur `Target`/`Source` explicitement renseignés (`AssociationEnd.setTarget()`/`setSource()` — une méthode réelle de l'API, distincte de `setOpposite()`, sans quoi Modelio affiche `<no type>` dans l'IHM même quand tout le reste est correct).
- Validé de bout en bout sur un métamodèle de test jetable (`SemGenTest`) avant application au vrai modèle, pour éviter des allers-retours coûteux sur `reference/design` : génération SemGen + JavaDesigner réussie (`GENERATION SUCCESSFUL`) avec ce patron exact.
- Autre pré-requis découvert au passage : toute classe générée doit porter **au moins une vraie `Generalization`**, même vers une classe étrangère au métamodèle (ex. `ModelElement`, infrastructure Modelio native) — une classe sans aucune généralisation fait planter `MetaclassLoadGenerator` avec la même `StringIndexOutOfBoundsException`. Dans `reference/design`, c'est déjà systématiquement le cas (toutes les classes descendent de `KerMLModelElement`/`ModelElement` ou `AbstractProject`), donc sans impact sur le script réel — mais un piège si on reproduit ce montage ailleurs sans y penser.
- **Validation finale sur le vrai modèle** : génération SemGen + JavaDesigner du composant `KerML` complet (81 métaclasses) réussie (`GENERATION SUCCESSFUL`), avec ce patron appliqué aux 33 cas réels.

**Correction annexe, découverte pendant cette validation — KerML ne doit référencer aucune classe SysML** : `reference/spec` (miroir fidèle des diagrammes de la spec) contenait 32 associations où une classe KerML possède un bout nommé (diagramme uniquement, ex. `Element.exposingView : ViewUsage`) pointant vers une classe SysML — jamais déclarées comme attribut formel dans le texte normatif KerML lui-même (vérifié par grep sur le texte intégral de la spec KerML), seulement visibles comme label de rôle sur le diagramme UML de la spec SysML (le côté formellement déclaré, ex. `/exposedElement : Element` sur `ViewUsage`, va bien dans le sens attendu SysML→KerML). Conceptuellement, KerML ne doit jamais référencer/générer quoi que ce soit vers SysML (couche fondation vs. couche construite dessus). Techniquement, Modelio impose qu'une association a toujours ses deux bouts possédés par deux classes différentes (règle `E211`) — impossible de « déplacer » la possession du bout côté KerML vers SysML sans casser structurellement l'association. Solution retenue : ces 32 associations diagramme-seul sont supprimées entièrement de `reference/design` (les deux bouts, `reference/spec` reste intouché) — aucune perte de contenu réellement spécifié, puisque rien n'était formellement déclaré côté KerML pour commencer.

**Recensement complet (2026-09-26)** : les 32 sont maintenant énumérées, classées en trois familles et analysées dans le support dédié [`WIP-2026-09-27-redefines-xmi/`](WIP-2026-09-27-redefines-xmi/slides.md) (partie 3). Vérifié en direct sur le modèle : 316 associations dans `reference/spec`, dont exactement **32** franchissent la frontière SysML → KerML, et **toutes les 32 sont absentes de `reference/design`** (aucune exception, aucun reste). Point important pour l'arbitrage : les 32 sont **toutes** `isDerived="true"` — aucune donnée stockée n'est perdue, seulement des raccourcis de navigation typés. 19 d'entre elles restent atteignables via une propriété KerML héritée qui existe bien dans le design (`Feature.type`, `Namespace.member`, `Type.ownedFeature`…) ; les 13 autres n'ont ni `redefines` ni `subsets` et devraient être réimplémentées comme opérations calculées si on en a besoin (12 des 13 sont la lecture des arguments d'une action — un motif unique, pas treize problèmes distincts).

Raisons de garder ce design malgré le détour :
- C'est la version la plus fidèle du patron cité au point 4 (*Replace Inheritance with Delegation* : détenir une référence vers une vraie instance du type délégué, pas construire une hiérarchie parallèle).
- Le risque de confusion évoqué initialement (un `DataTypeImpl` interne à `AttributeDefinitionImpl` serait-il confondu avec un vrai `DataType` du modèle utilisateur ?) ne se vérifie pas dans la pratique Modelio : la navigation générée est basée sur la possession par composition, pas sur un scan global par métaclasse — un délégué privé n'est atteignable qu'en passant par `AttributeDefinition` elle-même.
- Beaucoup plus simple à construire et à maintenir qu'une hiérarchie de classes déléguées : aucune classe supplémentaire, aucun choix entre dupliquer le délégué par cas ou le partager dans un package neutre — juste une association de plus, du même type que toutes les autres associations déjà présentes dans le modèle.

**Traçabilité** : chacune des 33 associations composées (34 cas moins les 2 exclus comme chevauchements, `MetadataDefinition`/`MetadataUsage`, plus le cas 22 `FlowUsage` qui en compte deux) porte une `Note` expliquant qu'elle ne provient pas de `reference/spec` mais a été ajoutée pour porter l'axe secondaire — attachée via `note.setSubject(boutPrimaire)`, visible directement sur le bout d'association côté classe primaire dans le modèle.

Liste des 33 références composées (primaire → nom du bout → type, `= vraie classe`) :

1. `Association.classifier : Classifier` — 2. `AssociationStructure.structure : Structure` — 3. `Connector.relationship : Relationship` — 4. `Flow.step : Step` — 5. `Interaction.association : Association` — 6. `MetadataFeature.annotatingElement : AnnotatingElement` — 7. `SuccessionFlow.succession : Succession` — 8. `ActionDefinition.behavior : Behavior` — 9. `ActionUsage.step : Step` — 10. `AssertConstraintUsage.invariant : Invariant` — 11. `AttributeDefinition.dataType : DataType` — 12. `BindingConnectorAsUsage.bindingConnector : BindingConnector` — 13. `CalculationDefinition.function : Function` — 14. `CalculationUsage.expression : Expression` — 15. `ConnectionDefinition.associationStructure : AssociationStructure` — 16. `ConnectionUsage.connectorAsUsage : ConnectorAsUsage` — 17. `ConnectorAsUsage.connector : Connector` — 18. `ConstraintDefinition.predicate : Predicate` — 19. `ConstraintUsage.booleanExpression : BooleanExpression` — 20. `ExhibitStateUsage.stateUsage : StateUsage` — 21. `FlowDefinition.interaction : Interaction` — 22. `FlowUsage.connectorAsUsage : ConnectorAsUsage` **et** `FlowUsage.flow : Flow` (seul cas à deux attributs composés) — 23. `IncludeUseCaseUsage.useCaseUsage : UseCaseUsage` — 24. `ItemDefinition.structure : Structure` — 25. `MembershipExpose.membershipImport : MembershipImport` — 26/27. `MetadataDefinition`/`MetadataUsage` : exclus (chevauchements, point 3) — 28. `NamespaceExpose.namespaceImport : NamespaceImport` — 29. `OccurrenceDefinition.class : Class` — 30. `PerformActionUsage.eventOccurrenceUsage : EventOccurrenceUsage` — 31. `PortDefinition.structure : Structure` — 32. `SatisfyRequirementUsage.assertConstraintUsage : AssertConstraintUsage` — 33. `SuccessionAsUsage.succession : Succession` — 34. `SuccessionFlowUsage.successionFlow : SuccessionFlow`.

Pour le contenu réel que chaque axe secondaire porte concrètement (attributs/opérations propres, le cas échéant), se référer directement à la classe elle-même dans `reference/spec`/`reference/design` — puisque le délégué EST cette classe, il n'y a plus de distinction à documenter séparément entre « délégué avec contenu réel » et « délégué marqueur pur » : c'est simplement la question de savoir si la classe secondaire a, par elle-même, des attributs/opérations propres dans la spec.

**Réserve de Cédric Marin sur ce design** : multiplication des éléments de modèle, coût mémoire/perf, absence de contrôles de cohérence entre les deux objets, besoin d'une façade — le même mur que l'implémentation UML2 de Modelio il y a 15 ans. Traité en détail, avec exemples chiffrés et recommandation en 3 temps, dans `WIP-2026-09-16-limitation-heritage-multiple-semgen.md` et son support de présentation (`ARCHIVE-HISTORIQUE-2026-09-11-heritage-multiple/`) — document séparé destiné à cette discussion précise, ce point 5 restant le journal technique des essais/décisions. **Suite donnée** : présenté à Cédric, qui a transmis le code source de SemGen. Correctif choisi, implémenté et compilé (`SemGen_4.0.00.jmdac`) — détail technique dans `ARCHIVE-HISTORIQUE-2026-09-10-semgen-patch-heritage-multiple.md`. Projet de test local isolé (consigne Antonin) en place, stéréotypes SemGen appliqués sur un métamodèle de test reprenant `FlowUsage`-like `TestChild` (2 parents réels) ; prochaine étape : lancer `Generate Metamodel` dessus pour la première validation réelle. Suivi détaillé, vivant, dans `WIP-2026-09-16-limitation-heritage-multiple-semgen.md`.

**Statut** : les 34 cas sont conservés comme généralisations réelles et validés par génération. Le tableau reste une trace de l'analyse des axes primaire/secondaire, pas une procédure de délégation.

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

2. **Appliquer les deux points de greffe** : renommer la classe `Element` en `KerMLModelElement`, conserver la chaîne d'intégration générée `EObject`/`MObject`/`SmObjectImpl`, et créer `SysMLProject` étendant `AbstractProject`.

3. **Appliquer les stéréotypes et propriétés SemGen** décrits ci-dessus, sur chaque classe/attribut/relation copiés dans `reference/design` :
   - Poser `SemGen::Metamodel` sur le composant racine du métamodèle `reference/design`, avec `Name`, `Id`, `Version`, `Provider`, `Production namespace`.
   - Pour chaque classe : `SemanticLinkMetaclass` si elle représente une relation (`Association`, `Connector`, `Dependency`, `Succession`, `Flow`…), sinon `Semantic`.
  - Sur les classes `Semantic` : cocher `structural.node` uniquement sur `SysMLProject`, `Package`/`LibraryPackage` et les 25 `Definition` concrètes présentes dans `reference/design`. Les usages, expressions, relations, memberships, multiplicités et autres détails restent persistés avec leur conteneur. Cocher `semantic.orphans.allowed` uniquement sur `SysMLProject` lui-même, la racine.
   - Sur chaque attribut : poser le stéréotype `Semantic`, le type Java correspondant, et la valeur par défaut (`Value`) quand `reference/spec` en définit une.
   - Sur chaque rôle d'association (`AssociationEnd`) : pour une composition/agrégation, `structural.partOf`/`structural.isToDelete` sont implicites (rien à cocher) ; pour une association pure, `structural.partOf` du côté de la cardinalité la plus faible et `structural.isToDelete` au cas par cas. `persistency.optional` au cas par cas selon la cardinalité. `Semantic.link.source`/`Semantic.link.target` sur les rôles des classes `SemanticLinkMetaclass`.
   - Reporter la propriété `Abstract` déjà présente dans `reference/spec` (aucune décision nouvelle ici — juste la recopier).

4. **Court-circuiter les trois chevauchements** (point 3) : pour `Comment`, `Documentation`, `Dependency`, `MetadataDefinition` et `MetadataUsage`, ne pas créer de nouvelle classe dans `reference/design` — à la place, rediriger toute référence à ces concepts, partout où ils apparaissent dans les associations et généralisations copiées depuis `reference/spec`, vers les classes d'infrastructure correspondantes (`Note`, `Dependency`, `Stereotype`/`TaggedValue`). Concrètement : partout où une classe de `reference/spec` a un lien vers `Comment` par exemple, ce lien pointera vers `Note` dans `reference/design`.

5. **Conserver les 34 cas d'héritage multiple** (points 4 et 5), pour chacune des classes concernées. On ne modélise **ni les interfaces `mm.api` ni les classes `mm.impl`** — SemGen génère automatiquement ces éléments. Le script doit recopier toutes les généralisations réelles de `reference/spec`; SemGen conserve les parents dans l'API et aplatit les membres secondaires dans l'implémentation. Les associations composées de l'ancien contournement doivent être supprimées.
   - Ne créer aucune association composée technique pour représenter un parent secondaire. Les généralisations réelles suffisent; SemGen conserve les parents dans l'API et aplatit les membres secondaires dans l'implémentation.

6. **Vérifier le résultat** : à la fin, comparer `reference/design` à `reference/spec` (mêmes 182 classes présentes, mêmes attributs/opérations, mêmes associations — modulo les redirections du point 3) pour s'assurer qu'aucune classe, attribut ou relation n'a été perdu en chemin. Même logique d'audit que celle déjà appliquée sur `reference/spec` lui-même (0 écart toléré par rapport à la source).

**Pourquoi un script plutôt qu'une transformation manuelle** : `reference/spec` compte 182 classes — refaire cette greffe à la main serait long et source d'erreurs, et surtout non reproductible si `reference/spec` est corrigé plus tard (coquilles, mises à jour de spec) ou si une des règles ci-dessus change. Un script réexécutable permet de régénérer `reference/design` à l'identique à chaque fois, à partir des mêmes règles.

Ce point découle mécaniquement des points 1 à 5 — il est mentionné ici pour que l'équipe sache ce qui suit une fois ces points validés, et pour resituer l'effort restant : la partie modélisation/conception est faite, il reste l'implémentation outillée de ce qui a été décidé.

---

## 7. Relecture de Cédric Marin sur `reference/design` (2026-09-21)

Trois retours distincts, de gravité différente.

### 7.1 `structural.node` posé sans discernement — **corrigé**

**Constat de Cédric** : « toutes les métaclasses sont flaguées `{structural.node}` ==> chaque élément de modèle va être dans son propre fichier ! » (chaque classe stéréotypée `Semantic` devient une unité de persistance séparée, cf. tableau du point 6).

**Vérifié en direct sur le modèle live** : les 171 classes de `reference/design`, y compris les 8 classes abstraites (`KerMLModelElement`, `Relationship`, `ConnectorAsUsage`, `ControlNode`, `LoopActionUsage`, `Expose`, `Import`, `InstantiationExpression`), portaient toutes la propriété `Semantic.structural.node` cochée. Or le point 6 documente déjà la règle « jamais cochée sur une métaclasse abstraite » — jamais appliquée par le script `phase5d_fix_and_members.jy`, qui la posait en boucle sur toutes les classes sans filtre.

**Correctif final appliqué** : après le retrait initial sur les 8 classes abstraites, `phase11_normalize_structural_nodes.jy` a supprimé 135 tags supplémentaires et ajouté le tag manquant sur `SysMLProject`. Il reste exactement 28 grains : `SysMLProject`, `Package`, `LibraryPackage` et les 25 `Definition` concrètes présentes dans le design. Aucun `Usage`, expression, relation, membership, multiplicité ou autre détail embarqué n'est un fichier séparé. Une seconde exécution a produit 0 ajout, 0 retrait et a sauté la sauvegarde. `phase5d_fix_and_members.jy` applique désormais cette même liste blanche lors d'une régénération.

### 7.2 `KerMLModelElement` : `Name` redéfini, `elementId` — **corrigé**

**Constat de Cédric** : `KerMLModelElement` (greffe du point 1, `KerML::Element` étendant `infrastructure::ModelElement`) redéfinit `Name` alors que `ModelElement` la porte déjà nativement, et porte aussi `elementId`.

**Vérifié** : `phase2_copy_members.jy` recopie tels quels tous les attributs propres de `KerML::Element` depuis `reference/spec`, dont `name`/`declaredName` (dupliquant `ModelElement.Name`, déjà hérité) et `elementId` (l'identifiant `String{id}` propre à KerML, à comparer à l'UUID natif que porte déjà tout objet Modelio).

**Décision et correctif** : `name` et `elementId` ont été supprimés en direct de `KerMLModelElement` par `phase10_remove_kerml_model_element_duplicates.jy`. Le nom repose sur `ModelElement.Name` et l'identité sur l'UUID natif Modelio. Les propriétés KerML distinctes (`declaredName`, `declaredShortName`, `shortName`, `qualifiedName`, `aliasIds`, `isImpliedIncluded`, `isLibraryElement`) sont conservées. `phase2_copy_members.jy` ignore désormais les deux doublons lors d'une régénération. Vérification live : aucun doublon restant, parent unique `ModelElement`, projet non sale.

### 7.3 Associations abstraites/dérivées (union/subset) — **drapeaux corrigés, génération incomplète**

**Constat de Cédric**, illustré par lui : `SmDependency ownedElementDep; SmDependency ownedRelationshipDep` — sentiment que le design duplique le même contenu sous deux noms.

**Analyse** : `KerML::Element` porte, dans la spec, une propriété dérivée abstraite `/ownedElement : Element [0..*] {ordered}` et son sous-ensemble concret stocké `ownedRelationship : Relationship [0..*] {subsets relationship, ordered}` — le même patron (union abstraite dérivée + multiples `subsets`/`redefines` concrets) se répète largement dans la spec (`Type.ownedSpecialization`, `Namespace.ownedMember`, `Membership.memberElementId`/`ownedMemberElementId`…). `reference/spec` recopie fidèlement ce patron ; `reference/design` n'a pour l'instant aucune règle pour le résoudre avant génération SemGen, avec le risque que les deux (l'union abstraite et chaque sous-ensemble concret) finissent stockés séparément — même contenu dupliqué en mémoire/persistance.

**Orientation de conception** : éviter les stockages indépendants pour une même propriété redéfinie. Les redéfinitions, les sous-ensembles et les unions dérivées demandent toutefois des traitements distincts : une redéfinition restreint la même propriété, elle ne doit pas simplement filtrer et masquer des valeurs interdites. Modelio expose `AssociationEnd.isDerived`, mais pas les liens UML `isDerivedUnion`, `subsettedProperty` ou `redefinedProperty` sur `AssociationEnd`. Le drapeau seul ne suffit donc pas à générer leur sémantique ; les liens normatifs doivent aussi être conservés et exploités.

**Correctif appliqué** : sur 556 rôles d'association du design, 548 ont été appariés sans ambiguïté à `reference/spec` par propriétaire, nom de rôle, propriétaire opposé et nom opposé. `phase12_restore_derived_association_ends.jy` a restauré 291 drapeaux dérivés ; 8 extrémités techniques non appariées autour des annotations et multiplicités ont été laissées intactes. Vérification centrale : `KerMLModelElement.ownedElement.isDerived = true`, tandis que `ownedRelationship.isDerived = false`. Une seconde exécution a produit 0 changement et a sauté la sauvegarde. `phase4_associations.jy` copie désormais `isDerived` lors d'une régénération.

**Rectification après audit du 24/09/2026** : la restauration des drapeaux est effective, mais ne constitue pas une résolution complète. Le Java produit par SemGen `4.0.05` contient encore 14 collisions de champs `Data` hérités et 47 paires de redéfinitions XMI avec stockage déclaré des deux côtés (comptages qui se recouvrent). L'audit trouve aussi 858 appels vers 397 getters de dépendance absents après suppression des descripteurs dérivés. Les 69 redéclarations d'API ne sont pas toutes fautives : une surcharge légitime n'est pas un stockage supplémentaire.

**Solution en cours, non livrée** : partage du stockage et du descripteur pour les redéfinitions compatibles ; alias Java pour les renommages ; prototype de collection typée sans copie du stockage. Les tests vérifient les mutations et la propagation inverse du noyau, mais reproduisent également un contournement par une écriture inverse non protégée. Les restrictions de type/cardinalité et les propriétés dérivées ne sont donc pas encore prises en charge de bout en bout. Le candidat local `4.0.06` n'est pas déployé et son archive précède les dernières modifications. Le déploiement sera réalisé par l'utilisateur après validation.

**Exemple du risque inverse** : si `CommandeProfessionnelle.client` n'accepte que des `ClientProfessionnel`, contrôler son setter ne suffit pas. Un client ordinaire peut essayer `client.commandes.add(commandeProfessionnelle)` depuis l'autre extrémité. Cette opération doit être refusée avant de modifier les liens existants. Une vue qui constate l'erreur à la lecture suivante ne suffit pas.

**Avancement du prototype au 24/09, après revue indépendante** : le contrôleur simule les valeurs finales des extrémités affectées avant mutation, y compris l'ancien propriétaire lors d'une réaffectation. Les tests sur les opérations réelles du noyau, avec persistance en mémoire, couvrent les refus sans modification et les remplacements valides. Une faille supplémentaire de callback réentrant a été reproduite puis corrigée : les nouvelles écritures non prévues pendant une mutation sont refusées. Cela ne garantit pas le rollback si un callback laisse remonter une exception après une suppression intermédiaire.

**Raccordement en cours** : `RuntimeSupportSource` prépare l'extraction AST et la reconstruction des classes de support dans un autre package ; `AssociationGuardCode` produit les méthodes d'interception Java. Aucun de ces helpers n'est encore raccordé au flux complet de génération. La disponibilité du compilateur JDK dans Modelio, le partage d'un runtime unique entre KerML/SysML et la conservation des notes manuelles restent à valider. Preuves distinctes : 8 tests de comportement passent après correction de réentrance ; le sous-agent rapporte 6 tests de compilation des interceptions réussis ; les tests d'extraction du runtime ont été interrompus et ne sont pas déclarés réussis. Le dernier résultat global établi reste celui des 41 tests antérieurs à ces ajouts. Aucun nouveau module livrable ni déploiement n'est annoncé.

**Périmètre actuel** : modifications du code SemGen et de ses tests, sans changement du noyau ni du modèle live. La phase 13 n'a pas démontré le nettoyage des trois rôles résiduels : elle inspecte des attributs UML au lieu des extrémités d'association. Détails, preuves et critères de livraison : [état des redéfinitions SemGen](../reference-design-transform/WIP-2026-09-27-semgen-redefinitions-status.md). Les slides seront finalisées une fois la solution complète validée.

### 7.4 Documentation SemGen/Javadoc — **copiée**

La documentation normative présente dans `reference/spec` sous forme de `Note`
Modelio a été copiée vers les éléments correspondants de `reference/design` par
`phase9_copy_documentation.jy` : 935 notes ajoutées (169 classes, 81 attributs,
567 rôles d'association, 96 opérations, 19 littéraux d'énumération et 3
packages). SemGen utilise ces Notes pour produire la Javadoc de l'API générée.

Le script conserve les notes techniques déjà présentes et évite les doublons de
contenu. Vérification ciblée sur le métamodèle Analyst : `Dictionary` porte une
note longue de `Description`, puis une note courte de `Summary` contenant son
nom. `phase9_copy_documentation.jy` applique désormais ce même patron dans
`reference/spec` et `reference/design` : la description normative est
conservée, et le nom de l'élément est ajouté comme résumé quand aucun résumé
n'existe. Une seconde exécution n'a supprimé aucune note et n'a créé aucun
doublon ; elle réécrit toutefois les contenus typés via l'API Modelio. Les
éléments exclus ou
redirigés par le design (`Comment`, `Documentation`, `Dependency`,
`MetadataDefinition`, `MetadataUsage`) ainsi que les membres non recopiés par
les phases précédentes restent à traiter si leur documentation doit aussi être
exposée côté infrastructure ou génération.

**Correctif après relecture manuelle (2026-09-26) : `KerMLModelElement` avait
été entièrement oublié.** `phase9_copy_documentation.jy` apparie les éléments
de `reference/spec` à ceux de `reference/design` par une clé exacte
`(métaclasse, nom de la classe propriétaire, nom du membre)`. Or `KerML::Element`
a été délibérément renommé en `KerMLModelElement` dans `reference/design` (point
1) — un changement d'identité qui n'existe pas côté spec. Le nom du propriétaire
ne correspondant jamais, la clé échouait systématiquement pour cette classe et
pour chacun de ses membres (leur clé embarque aussi le nom du propriétaire) :
`KerMLModelElement` — la classe la plus fondamentale du modèle, celle dont
héritent toutes les autres — s'est retrouvée sans aucune documentation, ni sur
la classe elle-même ni sur ses 7 attributs, 17 rôles d'association ou 5
opérations. Vérifié en direct sur le modèle live avant correction, pas supposé :
`reference/spec.Element` porte bien une description normative complète.

Un diff complet des noms de classes entre `reference/spec` (175) et
`reference/design` (171) confirme qu'il s'agit du seul cas de ce type : les 5
autres noms présents seulement côté spec sont les redirections déjà
documentées ci-dessus (`Comment`, `Documentation`, `Dependency`,
`MetadataDefinition`, `MetadataUsage`), et le seul autre nom présent seulement
côté design (`SysMLProject`) est une classe entièrement nouvelle, sans
équivalent spec dont hériter une documentation.

Corrigé par `phase18_copy_element_documentation.jy` (réutilise telle quelle la
logique de `phase9_copy_documentation.jy`, appliquée à cette seule paire
classe-à-classe en ignorant volontairement la divergence de nom du
propriétaire) : 33 notes typées ajoutées, 6 résumés écrits, 21 notes brutes
côté spec reconverties. 8 membres restaient sans documentation propre
(`relationship`, `sourceRelationship`, `targetRelationship`,
`annotatingElements`, `annotation`, `membershipImport`, `accessExpression`,
`namespace`) — vérifié à l'époque que `reference/spec.Element` n'avait
lui-même aucune description pour ces membres non plus. Faux en partie : voir
la correction suivante.

**Deuxième correctif (2026-09-26) : le manque touchait tout le modèle, pas
seulement `Element`.** En vérifiant directement le XMI normatif (pas seulement
`reference/spec` déjà extrait), 4 des 8 membres ci-dessus
(`accessExpression`, `annotation`, `namespace`, `membershipImport`) se sont
révélés porter une vraie description normative dans le XMI — simplement
déclarée différemment : comme `<ownedEnd>` de l'`Association` elle-même,
et non comme `<ownedAttribute>` de la `Class`. Le script d'extraction initial
(`extract_descriptions2.py`, session du 20/08) ne parcourait que les
`ownedAttribute` des classes ; cette seconde forme, pourtant très courante
pour les rôles dérivés de navigation inverse, était systématiquement ignorée
— pas seulement pour `Element`, potentiellement pour tout le modèle.

Extraction complète et systématique des deux fichiers XMI (KerML + SysML) :
244 propriétés `ownedEnd` documentées trouvées (239 noms distincts, 5 réutilisés
sur des associations réellement différentes). Confronté aux 276 bouts
d'association actuellement vides dans `reference/spec` (parcours complet du
modèle live, pas un échantillon) : 232 correspondent sans ambiguïté par nom ;
9 nécessitaient de choisir entre deux candidats homonymes (tranché par le
texte de chaque commentaire et le nom de son association — ex. « The owning
Definition of this VariantMembership » ne peut désigner que le bout porté
par `VariantMembership`, pas celui porté par `Usage` — vérifié contre
l'`association_id` exact extrait, pas retapé à la main) ; 35 restent
réellement non documentés dans la norme elle-même (aucun `ownedComment`,
confirmé un par un) — rien à récupérer pour ceux-là.

Les 241 corrections résolues ont été appliquées :
- `phase19_backfill_ownedend_descriptions_spec.jy` sur `reference/spec` :
  241/241 appliquées, 0 conflit, 0 propriété introuvable.
- `phase20_propagate_ownedend_descriptions_design.jy` sur `reference/design`
  (même règle de correspondance de noms que plus haut, `Element` →
  `KerMLModelElement`) : 158/241 appliquées directement. 47 déjà porteuses
  d'une note « Redefines/Subsets (per normative XMI): ... » dans ce même
  champ de description partagé — refusées à raison par la règle « ne jamais
  écraser », mais laissées sans prose humaine du coup. 36 introuvables côté
  design (34 bouts + 2 classes) : entièrement expliqué par les exclusions
  déjà actées ci-dessus — les 32 associations diagramme-seul KerML→SysML
  (point 3 ; ex. `exposingView`, `clientDependency`/`supplierDependency`, les
  rôles `defined*` vers une classe `*Definition` SysML) et le chevauchement
  `MetadataUsage`/`MetadataDefinition` (point 3 également) — vérifié contre
  ce même document, pas supposé.
- `phase21_append_prose_alongside_redefines_design.jy` complète les 47 en
  ajoutant la prose humaine **au-dessus** de la ligne `Redefines`/`Subsets`
  déjà présente, sans jamais la remplacer — même principe qu'un rôle portant
  déjà à la fois une ligne `Subsets` et une ligne `Redefines` dans une seule
  note. 47/47 appliquées, 0 cas inattendu (aucune note existante ne s'est
  révélée être autre chose qu'une directive `per normative XMI` pure).

Bilan final : 205 des 241 corrections sont maintenant sur `reference/design`
(158 + 47), les 36 restantes sont des absences volontaires déjà actées, pas
un manque.
### 7.5 Discipline de temps et de coût des runs SemGen — règle de travail

L'expérience de cette session montre que le coût dominant ne vient pas des
petites corrections ciblées du modèle, mais des exécutions lourdes de SemGen /
JavaDesigner sur le métamodèle complet. Les retours de Cédric ont confirmé la
règle suivante : il faut corriger le design avant de demander une génération
coûteuse, et non l'inverse.

**Règle de discipline à appliquer dans le log de chaque run :**

- Date/heure de départ et de fin.
- Nom du script ou du sous-ensemble ciblé (`phase8_fix_structural_node_abstract.jy`,
  `phase9_copy_documentation.jy`, génération SemGen complète, reverse JavaDesigner…).
- Durée totale observée.
- Résultat exact : OK / warning / erreur / timeout.
- Effet de bord observé : nombre d'éléments modifiés, nombre de doublons supprimés,
  classes abstraites nettoyées, etc.
- Décision suivante : "OK pour valider", ou "stop au design, corriger d'abord".

**Ce que le log doit retenir pour optimiser les prochains runs :**

- Les scripts de correction locale sont rapides et doivent être utilisés en boucle
  tant que le modèle n'est pas stabilisé.
- Les audits globaux sur l'ensemble du modèle ne sont pas un debug normal ; ils
  doivent rester rares et justifiés, car ils sont lents et peuvent masquer la
  vraie cause derrière une traversée trop large.
- Une génération SemGen complète doit être traitée comme une validation finale,
  pas comme un test intermédiaire à chaque étape.
- Les trois corrections de design de la relecture Cédric sont désormais
  fermées. La prochaine génération complète sert de validation finale de ces
  décisions, pas de boucle de mise au point.

**Politique d'optimisation concrète :**

1. Corriger le modèle sur un sous-ensemble exact.
2. Vérifier le résultat localement et ne pas lancer la génération complète.
3. Une fois le design stabilisé, exécuter un seul run de validation finale.
4. Conserver dans le log le temps réel constaté pour chaque exécution, afin
   d'ajuster les futures demandes et d'éviter les relances prématurées.

Cette règle doit rester la norme jusqu'à la dernière validation de la greffe.

**Incident et temps observés le 2026-09-22 :** un run idempotent de Phase 8
avait retiré 0 tag mais appelait malgré tout `saveProject()`. Cette sauvegarde
globale a révélé une collision de cache sur une `Generalization` déjà supprimée
et fait passer le fragment SVN `Modelio - modelio.sysml2` à l'état `DOWN`.
Récupération par redémarrage complet via `H:\modelio\DEV - Modeliotool.lnk` :
environ 68 secondes entre le démarrage du processus et la fin de
l'authentification, puis chargement séparé et long de `Modelio.All`. Règle
ajoutée : toute phase idempotente saute `saveProject()` si son compteur de
mutations est nul ; ne jamais sonder ni redémarrer pendant l'authentification
ou l'ouverture de `Modelio.All`.

**Baseline mesurée de génération KerML :** commande SemGen reçue à
`13:21:28.480`, première ligne du journal de génération à `13:21:47`,
`GENERATION SUCCESSFUL` à `13:43:24`, puis `END` à `13:43:25`. Durée utile du
journal : **21 min 37 s** jusqu'au succès, **21 min 38 s** jusqu'à la fin ; coût
mur-à-mur depuis le déclenchement Modelio : environ **21 min 56 s**. Un run
KerML complet doit donc être budgété à **22 minutes minimum** et ne doit être
demandé qu'après toutes les validations ciblées et la revue des diffs.

Après restauration des 291 rôles dérivés, le run KerML suivant est passé de
`15:46:16` à `15:57:46`, soit **11 min 30 s**. Le run SysML post-correctifs a
ensuite révélé un littéral vide orphelin sous `RequirementConstraintKind` : le
package `Requirements` entier était exclu du lot (86 métaclasses au lieu de
97), puis la génération échouait sur les types manquants. Le littéral a été
retiré durablement et SemGen `4.0.03` possède désormais un contrôle bloquant
avant sélection des métaclasses et avant transaction de génération.

---

## Points ouverts / non couverts par le plan actuel

> **Note de mise à jour, validée par génération réelle** : toute l'investigation ci-dessous (`SemGenManual`, reverse JavaDesigner, `implements Secondary` écrit à la main) répondait à un problème que le design final de l'axe secondaire (point 5, association composée) **n'a plus** — la classe primaire ne cherche plus à faire `implements` l'interface Java générée pour la classe secondaire, elle porte juste une référence composée vers une vraie instance de cette classe. Aucune bascule de stéréotype ni écriture manuelle par cas n'est nécessaire : SemGen génère directement le bon résultat à partir de l'association. Section conservée pour l'historique de l'investigation, mais la procédure décrite plus bas ne fait plus partie du plan réel. Voir plus loin dans cette section (« Génération réelle validée bout en bout ») pour l'état actuel, effectivement testé.

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

- **Génération réelle validée bout en bout — `KerML` et `SysML` génèrent tous les deux `GENERATION SUCCESSFUL`, séparément** (session ultérieure à ce qui précède). Deux problèmes réels ont dû être résolus, tous deux confirmés sur le vrai modèle et documentés dans `ModelioSkill/skills/modelio/references/api-gotchas.md` (Erreurs 36 et 37) :

  1. **`Metamodel.isExtension` seul ne suffit pas** pour qu'un composant résolve les types d'un autre métamodèle (classes ET énumérations). Il faut un vrai `ElementImport` (`Component.getOwnedImport()`, différent de `getOwnedPackageImport()`) du composant dépendant vers chaque métamodèle référencé. Confirmé en retrouvant le vrai motif sur trois métamodèles déjà fonctionnels dans la même instance Modelio : `Analyst`, `Archimate`, et le composant `Standard` de `platform.core` possèdent chacun exactement un `ElementImport` vers le même composant `Infrastructure` — tout métamodèle en dépend (confirmé par Antonin et Cédric Marin). `SysML` a donc reçu un `ElementImport` vers `Infrastructure` et un second vers `KerML` ; `KerML` un `ElementImport` vers `Infrastructure`. Sans ça : `Collecting MDAKit metaclasses... Collected 0 MDAKit metaclasses...` en permanence, imports non résolus pour les classes (dégradation silencieuse, pas fatale) et **plantage fatal pour toute énumération** référencée d'un autre métamodèle (`NullPointerException`).
  2. **Un `EnumerationLiteral` avec un nom vide plante SemGen** exactement comme un `AssociationEnd` sans nom (déjà documenté, erreur 34) — et peut en plus faire disparaître silencieusement tout le paquetage qui le contient du lot de génération (symptôme qui ressemble à un cache de scan périmé, mais qui ne se résout pas de façon fiable par un simple redémarrage puisque la vraie cause est une donnée, pas un cache). Trouvé sur `RequirementConstraintKind` (paquetage `Requirements` de `SysML`) : 3 littéraux au lieu de 2, le troisième vide. Vérifié : **les 7 énumérations de `reference/spec`** portaient ce même littéral vide parasite (confirmé absent du vrai `.ecore` normatif OMG, `KerML.ecore`/`SysML.ecore`, dépôt `Systems-Modeling/SysML-v2-Pilot-Implementation` sur GitHub) — corrigé à la fois dans `reference/spec` et `reference/design`.

  Avec ces deux corrections, la génération complète (81 métaclasses `KerML` + 97 métaclasses `SysML`) est propre — seules restent les erreurs `Attribute X has no initial value` déjà documentées et délibérément non corrigées (la spec elle-même ne fixe aucune valeur par défaut sur ces attributs, vérifié directement dans `kerml.txt`/`sysml.txt`).
