# Spec complète — Greffe SysML v2/KerML sur l'infrastructure Modelio

Document de synthèse unifiant les **points à trancher** (`points-a-trancher.md`) et les **points issus de la réunion du 27 août 2026** (Antonin, Cédric, Juan, Bilal, Fadwa, Laurent) qui n'y figuraient pas encore. Objectif : disposer d'un document de spec unique, structuré par thème, servant de base d'arbitrage et de référence pour l'implémentation.

> **Convention de lecture** : chaque section reprend d'abord la proposition/le constat, puis la question à trancher. Les apports issus de la réunion (non présents dans le document original) sont signalés par le tag **🆕 Réunion 27/08**.

---

## Partie 0 — Principe directeur transverse 🆕

**Décision énoncée par Antonin (réunion 27/08)** : on ne vise **pas** une conformité à 100 % au métamodèle SysML v2/KerML.

> « On accepte de faire des adaptations au niveau du métamodèle pour coller au concept déjà existant dans Modelio [...] Si le besoin métier est bien couvert par ce qui existe dans Modelio, le concept sort du métamodèle SysML et on garde celui de Modelio. »

Ce principe **chapeaute toutes les décisions de mapping** (Partie 2) : dès qu'un concept Modelio couvre l'intention métier d'un concept SysML v2/KerML, même de façon imparfaite, on réutilise l'existant plutôt que de dupliquer.

**Conséquence directe — désynchronisation texte/modèle 🆕** : à chaque fois qu'on choisit cette voie, le nom et la structure utilisés dans la **syntaxe textuelle SysML v2** (ex. « metadata ») peuvent diverger de ceux du **modèle Modelio sous-jacent** (ex. « stereotype », « property table »). Il faudra un composant de traduction/mapping entre les deux, dont la responsabilité (équipe Modelio vs équipe parsing textuel) reste à clarifier.

**Question à trancher** : 
- Valide-t-on formellement ce principe de non-conformité à 100 % comme règle par défaut du projet ?
- Qui a la responsabilité d'écrire/maintenir le mapping nom-à-nom entre syntaxe textuelle et modèle interne ?

---

## Partie 1 — Points de greffe sur l'infrastructure

### 1.1 Point de greffe des éléments

**Proposition** : le point de greffe est `ModelElement`. `KerML::Element` est renommé, dans `implementation` uniquement, en `KerMLModelElement`, et étend directement `ModelElement` — même patron que l'implémentation UML de Modelio (`UmlModelElement extends ModelElement`).

**Bénéfice confirmé en réunion 🆕** : Antonin souligne qu'hériter de `ModelElement` donne **gratuitement** l'accès aux stéréotypes, TaggedValue et PropertyTable définis dans Modelio — aucun développement supplémentaire n'est nécessaire pour ce mécanisme dès lors que la greffe est faite au bon endroit.

**Question à trancher** : valide-t-on ce renommage et ce point de greffe ?

### 1.2 Point de greffe du projet

**Proposition** : `SysMLProject extends AbstractProject`, sur le même patron que `Project` (UML). Nommé côté SysML et non KerML — pas d'éditeur KerML autonome, seulement un éditeur SysML v2 ; KerML reste une couche fondationnelle interne sans surface de projet propre.

**Question à trancher** : valide-t-on ce nom, ce point de greffe, et le principe que KerML n'a pas besoin de sa propre surface de projet ?

---

## Partie 2 — Chevauchements avec l'infrastructure Modelio

### 2.1 AnnotatingElement (Comment, Documentation, TextualRepresentation, MetadataFeature) → Note ou Constraint ?

**Rappel de la hiérarchie KerML** (`KerML::Root::Annotations`) : `AnnotatingElement` est la super-classe abstraite ; ses sous-types sont `Comment`, `Documentation`, `TextualRepresentation` et `MetadataFeature` (ce dernier traité à part en 2.3 via `MetadataUsage`). Le lien vers l'élément annoté passe par une relation `Annotation`, avec l'attribut dérivé `/annotatedElement : Element [1..*] {ordered}` — **la cardinalité multiple est portée par la super-classe `AnnotatingElement` elle-même**, donc elle s'applique à `Comment` et `Documentation` de la même façon.

| Concept KerML | Candidat Modelio | Cardinalité cible | Traitement proposé |
|---|---|---|---|
| `Comment`, `Documentation` | `infrastructure::Note` | `Subject : ModelElement` (1 seul) | Écarté en l'état — cardinalité incompatible |
| `Comment`, `Documentation` | `infrastructure::Constraint` | `ConstrainedElement : List<T>` (plusieurs) | Candidat retenu pour investigation — cardinalité compatible |

**Deux propositions confrontées en réunion 🆕** :
- **Juan** proposait initialement `Note` par analogie directe de rôle (élément descriptif attaché à un objet).
- **Cédric** a objecté que `Note` ne convient pas : « Pas avec les notes [...] c'est avec les contraintes qu'on peut le faire. Et ça peut poser problème d'ailleurs. »

**Vérification faite sur les fiches API Modelio (`org.modelio.metamodel.uml.infrastructure`)** :

| | `Note` | `Constraint` |
|---|---|---|
| Relation vers l'élément annoté | `Subject : ModelElement` — **un seul** élément, Note **composée** dans son Subject | `ConstrainedElement : List<T extends UmlModelElement>` — **liste**, donc plusieurs éléments en une seule instance |
| Attributs porteurs | `Content : String`, `MimeType : String` | `Body : String`, `Language : String`, `BaseClass : String` |
| Sémantique Modelio | Élément purement descriptif (documentation libre, aucune portée formelle) | Restriction/règle exprimable (« express restrictions and relationships that cannot be expressed using UML notation »), peut porter des stéréotypes de rôle prédéfinis (pré/post-condition, invariant) |
| Composition | Note appartient à son Subject (analogue à `Documentation` KerML : élément documenté = propriétaire) | D'après la doc API : « In Modelio, a Constraint is not made up of anything. It is only managed by specific copy/transfer rules » — pas de règle de composition simple équivalente |

**Analyse de l'arbitrage — aucun des deux candidats ne matche parfaitement** :
- `Note` a la **bonne sémantique** (purement descriptive, pas de portée formelle) mais la **mauvaise cardinalité** (1 seul élément).
- `Constraint` a la **bonne cardinalité** (liste d'éléments contraints) mais une **sémantique différente** : un `Constraint` Modelio induit une notion de *restriction/règle*, potentiellement interprétée par d'autres mécanismes de l'outil (génération de code, validation, stéréotypes de pré/post-condition) — ce qui ne correspond pas à l'intention d'un simple `Comment` KerML, purement informatif. C'est probablement le sens de la remarque de Cédric : « ça peut poser problème d'ailleurs » — réutiliser `Constraint` pour de la simple documentation risque de déclencher/impliquer des traitements non désirés ailleurs dans Modelio.
- Pas de composition native connue pour `Constraint` (contrairement à `Note`/`Documentation`) — à vérifier plus précisément avant de trancher (règle de rattachement, cycle de vie, suppression en cascade).

**`TextualRepresentation` 🆕** : sous-type d'`AnnotatingElement` portant `language : String [1]` et `body : String [1]` — structurellement très proche de `Comment`/`Documentation` (mêmes attributs, même cardinalité `[1..*]` sur l'élément annoté héritée de la super-classe). Aucun concept Modelio dédié identifié à ce stade ; à traiter avec la même décision que `Comment`/`Documentation` (`Note` ou `Constraint`), l'attribut `language` pouvant se rapprocher du `MimeType` de `Note` ou du `Language` de `Constraint`.

**Propriété `locale`** : présente sur `Comment` et `Documentation` (optionnelle) pour l'internationalisation — non portée nativement ni par `Note` ni par `Constraint`. À ajouter quel que soit le candidat retenu, ou fonctionnalité repoussée à un cycle ultérieur.

**Question à trancher** :
- Retient-on `Constraint` plutôt que `Note` pour héberger `Comment`/`Documentation`/`TextualRepresentation`, en acceptant le décalage sémantique (restriction formelle vs simple description) ?
- Si `Constraint` est retenu : vérifie-t-on qu'aucun mécanisme Modelio existant (génération, validation, pré/post-condition) ne s'active par erreur sur ces instances réutilisées à des fins purement descriptives ?
- Sinon, développe-t-on un concept dédié dans `implementation` (nouvelle métaclasse + vue de propriétés), au prix d'un effort de développement supplémentaire ?
- Supporte-t-on `locale` dès la v1, et sur quel attribut du candidat retenu ?

### 2.2 Dependency → Dependency

**Rappel spec KerML** (`8.3.2.2.2`) : `Dependency.client : Element [1..*]` **et** `Dependency.supplier : Element [1..*]` — les deux côtés sont des listes (relation **n-aire** : capable de relier plusieurs clients à plusieurs fournisseurs en une seule instance, ex. `dependency A, B to X, Y, Z;`). Une relation **binaire**, par opposition, ne relie jamais que 2 éléments (1 source, 1 cible) — c'est la limite de Modelio ici.

| Concept KerML | Infrastructure Modelio | Traitement proposé |
|---|---|---|
| `Dependency` | `infrastructure::Dependency` | Alias direct sur l'interface **de base**, pas une spécialisation |

**Achoppements identifiés** :
1. **Vérifié 🆕** : le `Dependency` de base Modelio ne porte **aucun stéréotype UML appliqué par défaut** — il est sémantiquement neutre (juste la mécanique générique de traçabilité/analyse d'impact : `getDependsOnDependency()`, `getImpactedDependency()`, réutilisable sans risque). En revanche, Modelio implémente les « saveurs » classiques de dépendance UML (`Usage`, `Abstraction`, `ElementRealization`, `Substitution`, `MethodologicalLink`…) comme des **métaclasses concrètes distinctes** héritant de `Dependency`, chacune ajoutant sa propre sémantique (mapping spécification/implémentation, substituabilité runtime, sémantique pilotée par stéréotype externe). **Le risque réel n'est donc pas sur `Dependency` lui-même, mais sur le point de greffe exact** : il faut s'assurer que l'alias cible précisément l'interface `Dependency` de base, et non l'une de ses spécialisations qui importeraient des notions étrangères à KerML.
2. **Pas de support n-aire côté Modelio, confirmé en réunion 🆕** : toute la famille `Dependency` de Modelio est **strictement binaire des deux côtés** (`Dependency`, `Abstraction`, `Usage`, `MethodologicalLink`, `ElementRealization` — tous limités à 1 client/1 fournisseur). Cédric : « On supporte pas ça [le n-aire]. On a sabré, simplifié. » Antonin : « Tu traduis par 2 dépendances chez nous, faut voir ça comme ça » (`X→Y` et `X→Z`).

**Précédent trouvé dans l'infrastructure confirmant cette approche 🆕** : `ComponentRealization` (« un Component peut être réalisé par plusieurs Classifiers ») résout exactement ce même problème de multiplicité — non pas via une liste sur l'attribut (`RealizingClassifier` reste singulier), mais en laissant le Component **posséder plusieurs instances `ComponentRealization`**, chacune pointant vers un seul Classifier. C'est le patron exact de la décomposition n-aire → plusieurs binaires déjà proposée pour `Dependency`.

**Point non résolu 🆕** : cette décomposition n-aire → binaire doit être assurée par un traducteur (probablement au niveau du parsing textuel). Reste à clarifier :
- Qui implémente ce parseur (équipe Modelio vs équipe parsing, cf. Bilal) ?
- La transformation est-elle réversible pour un roundtrip modèle → texte → modèle sans perte ?

**Question à trancher** : valide-t-on l'alias direct sur l'interface `Dependency` de base (pas une spécialisation) et la stratégie de décomposition n-aire → binaire(s), sur le précédent `ComponentRealization` ?

### 2.3 MetadataDefinition/MetadataUsage → Stereotype/TaggedValue ou PropertyTable

**Rappel spec SysML v2** (`8.3.27`) : `MetadataUsage extends ItemUsage, MetadataFeature` ; `MetadataFeature extends Feature, AnnotatingElement` — `MetadataUsage` hérite donc de la **même cardinalité multi-cible `[1..*]`** que `Comment`/`Documentation` (2.1), via `AnnotatingElement.annotatedElement`. `MetadataDefinition extends ItemDefinition, Metaclass` (pas d'attribut propre).

| Concept KerML/SysML | Infrastructure Modelio | Cardinalité cible côté Modelio | Traitement proposé |
|---|---|---|---|
| `MetadataDefinition`, `MetadataUsage` | `infrastructure::Stereotype` + `TaggedValue`/`TagType` | `TaggedValue.Annoted : ModelElement` (1 seul) | Mapper sur le sous-système Stereotype/TaggedValue |
| `MetadataDefinition`, `MetadataUsage` | `infrastructure.properties::PropertyTableDefinition` + `TypedPropertyTable` | `PropertyTable.Owner : ModelElement` (1 seul, hérité par `TypedPropertyTable`) | Mapper sur le sous-système PropertyTable |

**Achoppement le plus significatif des trois — confirmé et précisé par vérification API 🆕** : un `MetadataUsage` s'attache à plusieurs cibles à la fois en une seule instance (`about A, B, C`). **Aucun des deux mécanismes Modelio candidats n'est multi-cible** :
- `Stereotype` (définition) peut être appliqué à plusieurs éléments, mais **chaque application** (`ExtensionValue`) ne concerne qu'un seul élément de base.
- `TaggedValue.Annoted` et `PropertyTable.Owner` sont tous deux typés `ModelElement` (singulier, pas de liste) — vérifié sur les fiches API (`org.modelio.metamodel.uml.infrastructure` et `.properties`).

**Constat transversal avec la section 2.1 🆕** : sur les **trois** concepts `AnnotatingElement` étudiés (`Comment`, `TextualRepresentation`, `MetadataUsage`), tous héritent de la cardinalité multi-cible `[1..*]` en KerML/SysML, et **tous les mécanismes Modelio candidats identifiés à ce jour sont mono-cible** (`Note.Subject`, `TaggedValue.Annoted`, `PropertyTable.Owner`), **à l'exception de `Constraint.ConstrainedElement` (liste)**. Cela pose la question de fond : faut-il traiter la perte de multi-cible comme un compromis accepté (cas par cas, un mapping différent par concept), ou existe-t-il un principe commun (ex. Constraint généralisé, ou développement d'un mécanisme n-aire dédié) applicable aux trois cas ?

**Arbitrage IHM/technique détaillé en réunion 🆕** :
- Cédric précise qu'il y a un **choix technique interne** à trancher : TaggedValue/TagType (mécanisme historique, non typé — que du `String`) **vs** PropertyTable (mécanisme plus récent, permettant des tables typées via des `Definition`).
- Antonin tranche : « Dans tous les cas les properties [PropertyTable] sont le meilleur choix, puisque les tagged value de base c'est que du String, pas de typage. À partir du moment où tu veux du typage, c'est une Definition. »
- **Rapprochement structurel noté par Cédric** : `MetadataDefinition` ressemble à une `PropertyTableDefinition`, et `MetadataUsage` ressemble à une `PropertyTable` — « 2 méta-classes qui matcheraient ».

**Risque UX identifié 🆕 (Fadwa)** : « L'utilisateur il va chercher metadata, il va pas penser à property table [...] ça serait bien que ça soit la même metadata [nommée pareil]. » 
Réponse Antonin/Cédric : possible de renommer/adapter l'IHM (vues de propriétés spécifiques) sans dupliquer le mécanisme sous-jacent — « si tu fais une vue spécifique système, après tu fais ce que tu veux. »

**Question à trancher** :
- Confirme-t-on **PropertyTable** (plutôt que TaggedValue) comme mécanisme cible pour `MetadataDefinition`/`MetadataUsage` ?
- Accepte-t-on la perte du multi-cible en une seule instance (`about A, B, C`) ?
- Budgète-t-on une vue IHM dédiée nommée « Metadata » (plutôt que « Property Table ») pour ne pas perdre l'utilisateur ?
- Qui assure le mapping texte SysML (`metadata`) ↔ modèle Modelio (`property table`) pour le parsing ?

### 2.4 Bilan des chevauchements

Relecture des 19 classes du package `infrastructure` face aux 182 classes de `reference` : aucun autre chevauchement conceptuel net trouvé. Le reste se répartit en (a) plomberie de support des 3 chevauchements ci-dessus (`NoteType`, `TagType`, `TagParameter`, `MetaclassReference`), et (b) concepts propres à Modelio sans équivalent (`Resource`/`Document`, `ExternProcessor`, `Profile`, `MethodologicalLink`). `AbstractProject` déjà couvert en 1.2.

**Question à trancher** : confirme-t-on qu'il n'y a pas de 4ᵉ chevauchement à traiter (les 3 exemples de cette partie ont été vérifiés en réunion et jugés vraisemblablement corrects, sous réserve d'exemples complets à valider) ?

---

## Partie 3 — Héritage multiple KerML → Java

### 3.1 Constat et stratégie générale

**Constat** : 34 classes de `reference` ont deux (ou trois) super-types directs — impossible à traduire tel quel en Java.

**Historique — deux approches essayées et abandonnées 🆕** :
1. *Interface `mm.api` à double `extends` + délégué interne (« Behavior »)* — proposition initiale (Fowler, *Replace Inheritance with Delegation*). Abandonnée : reproduire fidèlement la hiérarchie réelle de l'axe secondaire dans chaque délégué obligeait soit à dupliquer tous les attributs/opérations hérités (classes énormes), soit à construire une hiérarchie fantôme parallèle d'une quarantaine de classes `XxxBehavior` — coût de maintenance jugé disproportionné pour un problème purement outillage.
2. *Attribut composé typé directement par la vraie classe secondaire* (ex. `AttributeDefinition.dataType : DataType` en attribut) — plus simple sur le papier, mais **confirmé en échouant à la génération réelle SemGen + Java Architect 🆕** : un attribut `Semantic` ne peut être typé que par un type Java primitif restreint (cf. 4.2), jamais par une autre métaclasse.

**Solution retenue et validée par génération réelle 🆕 — association composée vers la vraie classe secondaire** : pour chaque cas, l'axe **Definition/Usage** gagne `extends` (axe primaire) ; l'autre axe est modélisé comme une **relation d'agrégation composite** entre la classe primaire et **la vraie métaclasse secondaire elle-même** (pas de délégué synthétique) — stéréotype `Semantic` aux deux bouts, composition côté primaire. Validée d'abord sur un métamodèle jetable, puis appliquée aux 33 cas réels dans `reference/design` : génération SemGen + Java Architect propre, sans erreur. Chaque association composée porte une `Note` signalant qu'elle résulte de la résolution d'un héritage multiple et n'existe pas dans `reference/spec`.

**Contrainte technique à l'origine de ce choix, révélée en réunion 🆕** : Cédric confirme que **SemGen rejette (bloque) toute métaclasse portant un héritage multiple réel** dans le modèle, y compris pour la seule interface `mm.api`. Il n'y a donc pas de marge : la métaclasse ne doit physiquement plus porter qu'une seule généralisation, quelle que soit la solution retenue pour représenter l'axe secondaire — l'association composée n'est pas qu'une préférence de conception, c'est la seule voie compatible avec SemGen tel qu'il existe aujourd'hui.

**Avantage confirmé sur les cas en cascade 🆕** : contrairement au pattern délégué (qui obligeait à chaîner des objets `Behavior` synthétiques à la main), la cascade est désormais **gratuite** — la classe secondaire réelle (ex. `Association` pour le cas 5) porte déjà sa propre association composée pour son propre cas (ex. `Classifier`), donc la navigation se fait par simple chaîne d'appels sur des objets réels (`getInteraction().getAssociation().getClassifier()`), sans rien construire de spécial pour les cas 5, 15, 16, 21, 32, 34.

**Compromis assumé à documenter — perte de substituabilité polymorphique Java 🆕** : avec ce patron, une classe comme `AttributeDefinition` n'*est plus* un `DataType` au sens Java (pas d'`instanceof`, pas de passage en paramètre typé `DataType`, pas de collection `List<DataType>` qui la contiendrait implicitement) — elle *a* un `DataType`, accessible via un accesseur dédié (ex. `getDataType()`). Tout algorithme qui reposerait sur une polymorphie générique de l'axe secondaire (recherche de tous les `DataType` du modèle, vérifications de type génériques) devra explicitement passer par cet accesseur. **À vérifier avant généralisation** : existe-t-il aujourd'hui, ou dans les besoins de l'équipe parsing (Bilal, cf. 5.2), des algorithmes qui présupposent cette polymorphie ? Si oui, prévoir une convention de nommage uniforme des accesseurs pour limiter la friction.

**Point de vigilance UX 🆕** : l'instance composée est un vrai élément persisté (propre identité, propre place dans l'arbre de composition). À trancher : faut-il la masquer dans les vues standard de l'explorateur de modèle Modelio pour éviter qu'un utilisateur SysML v2 final ne voie apparaître un enfant technique (ex. un `DataType` sous chaque `AttributeDefinition`) sans rapport avec son intention de modélisation — même famille de risque que la remarque de Fadwa en 2.3 sur `PropertyTable`/Metadata ?

**Conséquence pratique sur le script 🆕** : le script de transformation `reference → implementation` (Partie 4) doit produire, pour chaque cas, une classe avec un seul `extends` réel (axe primaire) + une association composite vers la vraie classe secondaire (jamais un second `extends`/`implements`, jamais de classe déléguée synthétique) — stéréotype `Semantic` aux deux bouts, conformément aux conventions déjà décrites en 4.2.

**Question à trancher** : 
- Valide-t-on ce patron (association composée vers la vraie classe secondaire) comme règle par défaut pour les 34 cas ?
- Valide-t-on une convention de nommage uniforme pour les accesseurs de la facette secondaire (ex. nommés d'après le type secondaire) ?
- Décide-t-on de masquer ou non ces associations techniques dans les vues utilisateur standard de Modelio ?

### 3.2 Piste d'évolution outillage 🆕 (largement caduque pour ce besoin)

Juan proposait initialement de **contribuer à SemGen** pour qu'il applique automatiquement un pattern de délégation plutôt que de traiter les 34 cas à la main. **Mise à jour 🆕** : le patron d'association composée retenu en 3.1 fonctionne avec SemGen **tel qu'il existe aujourd'hui**, sans aucune évolution outillage nécessaire — cette piste perd donc l'essentiel de son intérêt pour ce besoin précis. Elle pourrait rester pertinente pour d'autres métamodèles futurs présentant un héritage multiple, mais n'est plus un prérequis ni une urgence pour ce projet.

**Question à trancher** : maintient-on cette piste dans le backlog long terme (bénéfice : futurs métamodèles), ou l'abandonne-t-on complètement puisque le blocage initial est résolu autrement ?

### 3.3 Les 34 résolutions individuelles

Cas 1–7 : noyau KerML. Cas 8–34 : niveau SysML. **Note de lecture 🆕** : la colonne « axe délégué » ci-dessous désigne désormais la **vraie métaclasse secondaire** vers laquelle pointe l'association composée (cf. 3.1) — il ne s'agit plus d'une interface implémentée par un objet `Behavior` synthétique, mais d'une relation d'agrégation composite vers une instance réelle de cette classe.

| # | Classe | `extends` (axe primaire) | Association composée vers (axe secondaire) |
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

**Répartition du contenu des délégués** : 17 cas ont un délégué portant un état/comportement réel (attribut ou opération, direct ou en cascade) ; 17 cas ont un délégué « pur marqueur » (aucun attribut/opération listé, juste un rôle de classification), qui pourrait rester une classe quasi vide tant que la spec ne lui ajoute rien.

**Cas particulier** : `ConnectorAsUsage` (#17) est la seule classe **abstraite** des 34 cas — le script devra reporter la propriété `Abstract`.

**Point de méthode soulevé en réunion 🆕 (Bilal)** : pour chaque cas non trivial, documenter un **exemple métier concret** (pas seulement la définition formelle) — ex. l'exemple donné par Bilal pour `subset` : relation `équipe/joueur` où un `capitaine` est un `joueur` à un instant donné (`subset` de `capitaineship` sur `membership`). Objectif : vérifier que chaque résolution couvre bien les cas d'usage réels, pas seulement la structure XMI.

**Question à trancher** : valide-t-on la règle générale et laisse-t-on les 34 cas en découler automatiquement, ou souhaite-t-on une revue cas par cas avec exemples à l'appui pour les cas contestables ?

---

## Partie 4 — Script de transformation `reference` → `implementation` et SemGen

### 4.1 Objectif

Une fois les points 1 à 3 tranchés, un script Jython construit `implementation` automatiquement à partir de `reference`, en appliquant mécaniquement les règles décidées plutôt que de recopier les 182 classes à la main.

### 4.2 Stéréotypes et propriétés SemGen à appliquer

SemGen génère `mm.api`/`mm.impl` à partir d'un métamodèle stéréotypé ; Java Architect prend ensuite le relai pour produire le plugin Eclipse final.

**Sur le composant racine** — stéréotype `SemGen::Metamodel` : `Name`, `Id`, `Version`, `Provider`/`Provider version`, `Production namespace` (ex. `org.modelio.sysml2.metamodel`), et `Metamodel.isExtension` à cocher systématiquement (confirmé par Cédric Marin).

**Sur chaque métaclasse** — l'un des deux, jamais les deux :
- `Semantic` — classes-concepts (majorité des 182 classes).
- `SemanticLinkMetaclass` — classes-relations (`Association`, `Connector`, `Dependency`, `Succession`, `Flow`… recoupe le noyau KerML cas 1–7).

**Propriétés sur les métaclasses `Semantic`** :
- `structural.node` — cochée = persistée dans son propre fichier ; non cochée = persistée avec son parent. Jamais cochée sur une métaclasse abstraite.
- `semantic.orphans.allowed` — réservée aux racines de métamodèle (chez nous : `SysMLProject`, sur le principe d'`ArchimateProject`).

**Propriétés sur les attributs `Semantic`** : type Java restreint (`String`, `Text`, `Boolean`, `Integer`, `Unsigned`, `Float`, énuméré), multiplicité toujours 1, valeur par défaut (`Value`). Deux propriétés **non honorées par le moteur actuel** (confirmé par Cédric) : `fpIndexed` et `EInoExternalize` — ne jamais cocher cette dernière en pensant obtenir un attribut transient, ça ne fonctionne pas.

**Propriétés sur les `AssociationEnd`** — `structural.partOf` et `structural.isToDelete` sont **implicites pour composition/agrégation**, à renseigner explicitement **seulement pour les associations pures** (convention : le rôle de cardinalité la plus faible porte le champ) ; `persistency.optional` pour optimiser les cardinalités élevées ; `Semantic.link.source`/`Semantic.link.target` sur les `SemanticLinkMetaclass` (rares exceptions où le lien n'appartient pas à sa source, ex. `DataFlow` cité par Cédric).

**Propriété `Abstract`** (onglet standard UML, indépendant de SemGen) : génère une classe/interface Java abstraite, aucune instance directe ; s'applique aussi aux relations (« relation chapeau »). Concerne `ConnectorAsUsage` parmi les 34 cas.

### 4.3 Tableau récapitulatif des effets

| Propriété SemGen | Effet réel |
|---|---|
| `structural.node` coché | Fichier de persistance dédié, granularité Teamwork propre. Classe/API toujours générées. |
| `structural.node` non coché | Persisté avec le parent, pas de fichier séparé. |
| `semantic.orphans.allowed` | Autorise une instance sans parent de composition (racines de métamodèle). |
| `Metamodel.isExtension` | À cocher systématiquement. |
| Type d'attribut | Mappage direct Java ; énumération → classe enum dédiée. |
| `structural.partOf` coché | Classe Java portant physiquement le champ de la relation. |
| `structural.isToDelete` coché | Suppression en cascade. |
| `persistency.optional` | Optimisation de stockage pour cardinalités élevées. |
| `Semantic.link.source`/`target` | Accès Java à la source/cible du lien. |
| `Abstract` coché | Classe/interface abstraite, sans instanciation directe. |
| `fpIndexed` / `EInoExternalize` | **Aucun effet** — non honorées par le moteur actuel. |

**Rappel important** : la classe et l'API Java d'une métaclasse sont **toujours générées**, quelle que soit la valeur de ces propriétés — elles ne déterminent que le mode de persistance/stockage, pas l'existence du code.

### 4.4 Documentation SemGen existante à valider 🆕

Fadwa a rédigé une documentation technique sur l'usage de SemGen. Cédric devait la valider (« j'ai passé ça, j'ai eu du mal à finaliser » — validation restée incomplète au moment de la réunion).

**Action à faire** : terminer la validation par Cédric Marin et intégrer cette documentation comme référence officielle du processus SemGen dans ce projet, en complément de la Partie 4.2 ci-dessus.

---

## Partie 5 — Organisation du projet 🆕

Points de méthode/process évoqués en réunion, sans lien direct avec les décisions de mapping mais nécessaires pour la suite.

### 5.1 Format du livrable de spec

Antonin tranche explicitement : un **document de spec unifié**, pas une multitude de tickets Jira (« c'est chiant à manipuler [...] plutôt il nous faut un document de spec basé sur ça »). Cédric propose en complément de créer des **exigences (« requirements »)** dans un projet Modelio dédié, en plus du document.

**Question à trancher** : structure finale retenue — document de spec seul, ou document + exigences Modelio en parallèle pour la traçabilité ?

### 5.2 Communication avec l'équipe de parsing textuel (Bilal)

Bilal souligne sa dépendance aux décisions de mapping Modelio pour pouvoir réutiliser des parseurs existants côté éditeur textuel SysML v2 : « Si on arrive à supporter un maximum de concepts, de leur vraie sémantique, ça me facilitera la tâche [...] je pourrais réutiliser certains des parsers. » Il demande explicitement à être informé « en parallèle » de l'avancement, même sans participer à toutes les réunions.

**Action à faire** : mettre en place un canal/rythme de communication régulier (compte-rendu partagé, ou réunions ponctuelles) entre l'équipe Modelio et l'équipe parsing, pour éviter les divergences tardives sur les noms/mappings (cf. Partie 0 — désynchronisation texte/modèle).

### 5.3 Documenter systématiquement les choix non triviaux

Demande explicite de Bilal en clôture de réunion : documenter **chaque décision de mapping difficile** et sa justification (« toute difficulté, toute décision qui n'est pas straightforward [...] tout mapping qui n'était pas facile à faire »), pas seulement le résultat final.

**Action à faire** : chaque section de mapping (Partie 2 notamment) doit conserver une trace du raisonnement et des alternatives écartées — déjà amorcé dans ce document via les citations, à poursuivre dans la spec définitive.

### 5.4 Exemples métier à l'appui de chaque concept

Cf. Partie 3.3 — généraliser la pratique à **tous** les concepts couverts par le document (pas seulement les 34 cas d'héritage), pour faciliter la revue et la validation par des non-experts du domaine SysML/ingénierie système.

---

## Synthèse des questions à trancher

| # | Sujet | Section | Urgence |
|---|---|---|---|
| 1 | Non-conformité 100 % comme règle par défaut | Partie 0 | Critique |
| 2 | Responsable du mapping texte ↔ modèle | Partie 0 | Critique |
| 3 | Renommage `KerML::Element` → `KerMLModelElement extends ModelElement` | 1.1 | Normale |
| 4 | `SysMLProject extends AbstractProject`, pas de surface KerML | 1.2 | Normale |
| 5 | Arbitrage `Comment/Documentation/TextualRepresentation → Note` (bonne sémantique, mauvaise cardinalité) ou `Constraint` (bonne cardinalité, sémantique de restriction formelle) | 2.1 | Critique |
| 6 | Support de `locale` dès la v1, sur le candidat retenu | 2.1 | Normale |
| 7 | Alias `Dependency`, décomposition n-aire → binaire(s) | 2.2 | Normale |
| 8 | `PropertyTable` (pas TaggedValue) pour `MetadataDefinition/Usage` | 2.3 | Critique |
| 9 | Vue IHM dédiée « Metadata » pour ne pas perdre l'utilisateur | 2.3 | Normale |
| 10 | Pas de 4ᵉ chevauchement à traiter | 2.4 | Normale |
| 11 | Patron d'association composée pour héritage multiple (remplace le pattern délégué) + convention de nommage des accesseurs | 3.1 | Critique |
| 12 | Maintenir ou abandonner la piste d'évolution SemGen (largement caduque) | 3.2 | Faible |
| 13 | Revue cas par cas des 34 résolutions (avec exemples) | 3.3 | Normale |
| 14 | Structure finale du livrable (spec seule ou + exigences Modelio) | 5.1 | Normale |
| 15 | Canal de communication avec l'équipe parsing | 5.2 | Critique |

---

*Sources : `points-a-trancher.md` (plan d'implémentation initial) et transcription de la réunion du 27 août 2026 (39 min, participants : Juan Cadavid, Antonin Abhervé, Cédric Marin, Bilal Said, Fadwa Rekik, Laurent Gonçalves).*
