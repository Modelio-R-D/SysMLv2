# Spec complète — Greffe SysML v2/KerML sur l'infrastructure Modelio

Document de synthèse unifiant les **points à trancher** (`points-a-trancher.md`) et les **points issus de la réunion du 27 août 2026** (Antonin, Cédric, Juan, Bilal, Fadwa, Laurent) qui n'y figuraient pas encore. Objectif : disposer d'un document de spec unique, structuré par thème, servant de base d'arbitrage et de référence pour l'implémentation.

> **Convention de lecture** : chaque section reprend d'abord la proposition/le constat, puis la question à trancher. Les apports issus de la réunion (non présents dans le document original) sont signalés par le tag **🆕 Réunion 27/08**. Les apports de la **réunion du 09/09/2026** (Antonin, Cédric, Juan, Bilal, Fadwa) et du suivi de commits associé sont signalés par le tag **🆕 Réunion 09/09**.

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

Relecture des 19 classes du package `infrastructure` face aux 182 classes de `reference` : aucun autre chevauchement conceptuel net trouvé **à l'époque de la réunion du 27/08**. Le reste se répartit en (a) plomberie de support des 3 chevauchements ci-dessus (`NoteType`, `TagType`, `TagParameter`, `MetaclassReference`), et (b) concepts propres à Modelio sans équivalent (`Resource`/`Document`, `ExternProcessor`, `Profile`, `MethodologicalLink`). `AbstractProject` déjà couvert en 1.2.

**Mise à jour 🆕 — 4 chevauchements supplémentaires trouvés par vérification directe sur l'instance Modelio live** (au-delà du seul package `infrastructure` — l'analyse initiale ne couvrait pas `statik`, `stateMachineModel`, `usecaseModel`, `informationFlow`) : cf. Parties 2.5 à 2.8 ci-dessous. **Point méthodologique important** : la documentation scrapée localement (`Modelio-API-Markdown-CHUB`) s'est révélée incomplète sur le package `stateMachineModel` (aucune classe `State`/`Transition`/`Region` recensée) — vérifié et corrigé par introspection directe de l'instance Modelio live via le ScriptServer plutôt que via la documentation seule. **Recommandation** : ne plus se fier uniquement à la documentation scrapée pour affirmer l'absence d'un concept Modelio — vérifier sur l'instance live avant de conclure à un chevauchement manquant.

**Question à trancher** : confirme-t-on qu'il n'y a pas de 4ᵉ chevauchement à traiter *dans le périmètre `infrastructure`* (les 3 exemples de cette partie ont été vérifiés en réunion et jugés vraisemblablement corrects) — sachant que le périmètre complet (au-delà d'`infrastructure`) contient au moins 4 chevauchements de plus, désormais documentés ?

### 2.5 États/Transitions SysML v2 → `State`/`Transition`/`Region` (stateMachineModel) 🆕

**Découverte** : Modelio possède nativement `State`, `Transition`, `Region`, `StateMachine`, `StateVertex` dans `org.modelio.metamodel.uml.behavior.stateMachineModel` — absents de toute documentation locale scrapée (trou de documentation, pas une absence réelle, cf. 2.4).

**Vérification API précise (introspection Java réelle)** :

| Concept SysML v2 | Attribut/relation | Candidat Modelio | Verdict |
|---|---|---|---|
| `TransitionUsage.source`/`.target` | — | `Transition.getSource()`/`.getTarget()` | ✅ correspondance directe |
| `TransitionUsage.guardExpression` | — | `Transition.getGuard()` | ✅ correspondance directe |
| `TransitionUsage.triggerAction` | — | `Transition.getTrigger()` | ✅ correspondance directe |
| `TransitionUsage.effectAction` | — | `Transition.getEffect()`/`getEffects()`/`getBehaviorEffect()` | ✅ correspondance directe |
| `StateDefinition.entryAction`/`.doAction`/`.exitAction` | — | *Aucun accesseur équivalent trouvé sur `State`* (`getEntryPoint()`/`getExitPoint()` sont des points de connexion de pseudo-états, pas des comportements) | ❌ manque structurel net |
| `StateUsage.isParallel` (régions parallèles via un booléen plat) | — | `Region` (objet dédié, régions orthogonales structurées) | ⚠️ décalage de paradigme — SysML aplati en booléen ce que Modelio structure en objets `Region` séparés |

**Verdict global** : `Transition` est un **excellent candidat** (4/4 attributs clés correspondent). `State` est un **candidat partiel** — la coquille structurelle (imbrication, régions, transitions entrantes/sortantes) correspond bien, mais **le rattachement des comportements d'entrée/sortie/activité manque** dans l'API observée (à revérifier — peut-être porté autrement, ex. stéréotype ou attaché à un état via un mécanisme non standard).

**Question à trancher** : confirmer précisément comment (ou si) `State` de Modelio permet de rattacher un comportement à l'entrée/la sortie/l'activité — avant de valider ou d'écarter ce mapping pour `StateDefinition`/`StateUsage`.

### 2.6 AssociationStructure/ConnectionDefinition → `ClassAssociation` (statik) 🆕

**Découverte clé** : `ClassAssociation` (*« A ClassAssociation is represented in UML as a Class that plays the role of an Association »*) — vérifié par introspection : **implémente uniquement `UmlModelElement`, pas `Class` ni `Association`**. Sa structure réelle :

```
ClassAssociation implements UmlModelElement {
    getClassPart() / setClassPart(Class)            // la facette Class, cardinalité 1
    getAssociationPart() / setAssociationPart(...)   // la facette Association, cardinalité 1
    getNaryAssociationPart() / setNaryAssociationPart(...)  // variante n-aire
}
```

**Pourquoi c'est une découverte importante pour la Partie 3** : `ClassAssociation` **résout exactement le même problème que `AssociationStructure`** (un concept qui est à la fois une classe et une association) — et Modelio l'a résolu **avec le même patron que le nôtre** : pas un double `extends`, mais une classe porteuse avec une **association composée vers chaque facette** (`ClassPart`, `AssociationPart`), chacune de cardinalité 1. **C'est un précédent historique interne à Modelio qui valide directement le choix retenu en Partie 3.1** — argument concret à faire valoir à Cédric : le patron d'association composée n'est pas une improvisation pour ce projet, Modelio l'a déjà utilisé pour résoudre le même type de problème structurel sur `ClassAssociation`.

**Cardinalité** : `ClassPart`/`AssociationPart` sont singuliers (pas de liste) — correspond exactement à la cardinalité attendue pour `AssociationStructure` (une seule facette `Structure`, cf. cas #2 déjà résolu de la même manière).

**Question à trancher** : remplace-t-on l'association composée générique déjà mise en place pour `AssociationStructure`/`ConnectionDefinition` (Partie 3.1, cas #2/#15) par un alias direct sur `ClassAssociation`, qui porte déjà nativement ce même patron avec du code Modelio existant (potentiel gain de développement) ?

### 2.7 UseCaseDefinition/UseCaseUsage → `UseCase` + `UseCaseDependency` (usecaseModel) 🆕

**Vérification API** : `UseCase implements GeneralClass` — un `Classifier` UML générique standard, sans attribut dédié pour acteur/sujet/objectif (confirme le constat déjà fait dans l'étude SysML : bon socle, mais la richesse de paramétrage de `CaseDefinition` — `subjectParameter`, `actorParameter`, `objectiveRequirement` — devra être ajoutée par-dessus, rien de prêt à l'emploi côté Modelio pour cette partie).

`UseCaseDependency` : `getOrigin()`/`setOrigin()`, `getTarget()`/`setTarget()` — relation **strictement binaire** (comme toute la famille `Dependency`, cf. Partie 2.2). Convient bien à `IncludeUseCaseUsage` (une inclusion relie toujours exactement 2 `UseCaseUsage`).

**Question à trancher** : valide-t-on `UseCase` comme alias direct pour le socle de `UseCaseDefinition`/`UseCaseUsage`, avec développement complémentaire pour la couche paramétrage héritée de `CaseDefinition` ?

### 2.8 FlowDefinition/FlowUsage → `DataFlow`/`InformationFlow` (informationFlow) 🆕

**Vérification API** :
- `DataFlow` : `getOrigin()`/`setOrigin()`, `getDestination()`/`setDestination()` — **strictement binaire** (1 origine, 1 destination), mais **sans attribut de type de payload** — juste un lien brut entre 2 éléments.
- `InformationFlow` : `getInformationSource()`, `getInformationTarget()`, `getConveyed()` (le ou les `InformationItem` transportés), `getChannel()`, plus des accesseurs de **réalisation** (`getRealizingActivityEdge()`, `getRealizingMessage()`, `getRealizingLink()`…) — suggère un concept **plus abstrait/logique**, réalisé concrètement par d'autres liens de plus bas niveau.

**Comparaison avec `Flow` KerML** : `Flow.flowEnd` est plafonné à 2 (*« A FlowDefinition may not have more than two flowEnds »*, déjà noté en Partie 3.3) — donc **binaire par construction**, ce qui correspond bien à `DataFlow` (strictement binaire) plutôt qu'à `InformationFlow` (potentiellement multi-source/cible selon la cardinalité réelle de `getInformationSource()`/`getInformationTarget()`, à vérifier). `InformationItem` (implémente `Classifier` complet) pourrait correspondre au type du `payloadFeature` de `Flow`.

**Verdict** : ⚠️ équivalent partiel — `DataFlow` correspond bien à la cardinalité binaire de `Flow`, mais ne porte pas nativement de notion de type de payload (à ajouter) ; `InformationFlow`/`InformationItem` sont plus riches mais leur cardinalité exacte (source/cible multiples ?) reste à vérifier avant de trancher lequel des deux mapper.

**Question à trancher** : vérifier précisément la cardinalité de `InformationFlow.getInformationSource()`/`getInformationTarget()` (singulier ou liste ?) avant de choisir entre `DataFlow` (simple, binaire, sans payload typé) et `InformationFlow` (plus riche, réalisation par des liens de bas niveau) comme cible pour `Flow`/`FlowUsage`.

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

**Réserves précisées par Cédric Marin (échange post-réunion) 🆕** : interrogé sur ses doutes (perte d'information ? polymorphisme perdu ?), Cédric recadre le vrai risque : *« Multiplication du nombre d'éléments de modèle qui représentent un seul élément, avec des conséquences sur : les performances, la consommation mémoire, des contrôles de cohérence supplémentaires (ne pas laisser quelqu'un créer un morceau sans l'autre, et qu'ils soient reliés entre eux), API de façade pour que ça ne se voie pas. »* Concrètement :
- **Performance/mémoire** : chaque instance utilisateur des 34 cas crée un objet composé supplémentaire — sur un modèle système de grande taille, ce n'est pas négligeable (potentiellement des dizaines de milliers d'objets « fantômes » en plus).
- **Cohérence** : l'objet composé pourrait être supprimé ou désynchronisé indépendamment de son primaire — nécessite des **règles d'audit dédiées** (probablement bloquantes/synchrones, cf. Partie 4.6) pour garantir que les deux existent et restent liés ensemble.
- **Façade API** : confirme le besoin déjà identifié d'accesseurs uniformes, mais formulé plus explicitement comme une vraie couche de façade à concevoir, pas juste une convention de nommage.

**Contexte stratégique motivant cette exigence 🆕** : Cédric rappelle que Modelio a déjà, il y a 15 ans, implementé UML2 « en taillant à la hache », sans respecter le métamodèle de la norme, **à cause de ce même problème d'héritage multiple**. Il constate que SysML v2 hérite du même problème (via UML2) et souhaite le régler à la source cette fois — motivé en partie par la concurrence (un outil Dassault revendiquerait une conformité à 100 % à la norme), pour éviter d'être bloqué plus tard si un client demande un meilleur support d'une partie du spec.

**Point de vigilance UX 🆕** : l'instance composée est un vrai élément persisté (propre identité, propre place dans l'arbre de composition). À trancher : faut-il la masquer dans les vues standard de l'explorateur de modèle Modelio pour éviter qu'un utilisateur SysML v2 final ne voie apparaître un enfant technique (ex. un `DataType` sous chaque `AttributeDefinition`) sans rapport avec son intention de modélisation — même famille de risque que la remarque de Fadwa en 2.3 sur `PropertyTable`/Metadata ?

**Conséquence pratique sur le script 🆕** : le script de transformation `reference → implementation` (Partie 4) doit produire, pour chaque cas, une classe avec un seul `extends` réel (axe primaire) + une association composite vers la vraie classe secondaire (jamais un second `extends`/`implements`, jamais de classe déléguée synthétique) — stéréotype `Semantic` aux deux bouts, conformément aux conventions déjà décrites en 4.2.

**Question à trancher** : 
- Valide-t-on ce patron (association composée vers la vraie classe secondaire) comme règle par défaut pour les 34 cas ?
- Valide-t-on une convention de nommage uniforme pour les accesseurs de la facette secondaire (ex. nommés d'après le type secondaire) ?
- Décide-t-on de masquer ou non ces associations techniques dans les vues utilisateur standard de Modelio ?

### 3.2 Piste d'évolution outillage 🆕 (réouverte)

Juan proposait initialement de **contribuer à SemGen** pour qu'il applique automatiquement un pattern de délégation plutôt que de traiter les 34 cas à la main. Conclusion précédente : le patron d'association composée retenu en 3.1 fonctionne avec SemGen tel qu'il existe aujourd'hui, rendant cette piste largement caduque pour ce besoin précis.

**Rebondissement 🆕** : suite aux réserves de Cédric précisées en 3.1 (performance, mémoire, cohérence), **Juan** (qui avait déjà proposé cette piste initialement, cf. historique ci-dessus) y revient en clôture d'échange, en ouverture de la discussion prévue le lendemain : *« ceci dit, en ouvre-bouche, je crois qu'il faudra bien modifier le générateur SemGen pour gérer ces cas d'héritage multiple. »* La piste n'est donc plus caduque — elle redevient une option à examiner sérieusement, potentiellement pour répondre directement aux réserves de performance/cohérence de Cédric plutôt que de les traiter uniquement via des règles d'audit compensatoires (cf. 4.6).

**Question à trancher** : programme-t-on une évolution de SemGen pour traiter nativement l'héritage multiple (bénéfice : répond aux réserves de Cédric à la racine, futurs métamodèles), ou maintient-on le patron d'association composée actuel en le compensant par des règles d'audit de cohérence (4.6) ? Point à trancher lors du point d'avancement dédié à ce sujet (Juan et Cédric).

**Mise à jour 🆕 Réunion 09/09 — décision prise : on part sur le correctif SemGen, avec une limite majeure révélée par Cédric.**

Le point d'avancement dédié annoncé ci-dessus a eu lieu le 09/09. Juan y a rejoué en direct l'exemple `TestChild`/`TestPrimary`/`TestSecondary` (cf. `limitation-heritage-multiple-semgen.md` §2) : SemGen aujourd'hui ne génère qu'une seule généralisation, y compris sur l'interface `mm.api` où Java aurait pourtant accepté un `extends` multiple. Antonin a demandé confirmation à Cédric : *« Est-ce que 2 interfaces comme ça règle le problème pour toi ? »* — Cédric : *« Oui. »*

**Mais Cédric introduit une limite plus profonde que le seul générateur SemGen** : même une fois l'interface `mm.api` corrigée pour porter un vrai héritage multiple, ça suppose des **modifications du noyau Modelio** (les classes de métamodèle interne `MClass`/`SmClass`), qui aujourd'hui ne portent qu'**une seule généralisation par élément** (« Pour l'instant ils ont qu'un seul [Generalization] par un, pour en avoir plusieurs [...] y a plein de trucs, y a des trucs qui vont plus compiler »). Ce changement de noyau **change le major de Modelio** — Antonin confirme : « C'est Modelio 7 [...] ça dépend si vous arrivez au bout. Si vous arrivez au bout, oui — mais l'objectif c'est ça, on va vous aider. »

**Deux chantiers désormais distincts, à ne pas confondre** :
1. **Correctif SemGen (couche génération de code)** — déjà engagé et prototypé les 09-10/09 (Cédric a transmis le code source, cf. `d981cf0`) : `ApiGenerator` boucle désormais sur tous les parents pour générer l'interface `mm.api` à héritage multiple réel, et un nouvel utilitaire `ModelUtils` aplatit les membres du 2ᵉ (ou 3ᵉ) parent directement sur la classe `Impl` feuille plutôt que de générer une délégation — 9 points d'appel modifiés dans 7 fichiers, build Maven/JDK21 réussi (`SemGen_4.0.00.jmdac`). Détail technique complet : [semgen-patch-heritage-multiple.md](semgen-patch-heritage-multiple.md) ; suivi de décision : [limitation-heritage-multiple-semgen.md](limitation-heritage-multiple-semgen.md). **Non encore validé en régénération réelle** — prochaine étape : lancer `Generate Metamodel` sur le métamodèle de test `SemGenMultiParentProbe` (stéréotypé le 2026-09-10) dans un projet local séparé (`UML-BPMN`, hors du fragment SysML2 partagé de `modelio.all` — exigence explicite d'Antonin), avec `FlowUsage` (cas #22, 3 parents) comme cas de test réel une fois validé sur le probe.
2. **Support natif multi-parent au niveau du noyau Modelio** — ce que Cédric vise à terme pour que la substituabilité polymorphique soit réelle (pas seulement l'aplatissement de membres). Non chiffré, non planifié, positionné comme un chantier **Modelio 7** (changement de version majeure), donc hors du périmètre temporel de ce projet SysML v2. Reste à clarifier si le correctif SemGen (point 1) suffit en pratique pour ce projet sans ce chantier de noyau, ou si des limitations subsisteront (ex. persistance `structural.node` d'une classe qui serait 2ᵉ parent, point resté ouvert dans `limitation-heritage-multiple-semgen.md` §Statut/point 7).

**Question à trancher (mise à jour)** : le correctif SemGen (point 1), une fois validé en régénération réelle sur les 34 cas, est-il suffisant pour ce projet, ou certains cas (ex. `FlowUsage`, 3 parents) exposent-ils des limites qui ne se résoudront vraiment qu'avec le chantier noyau Modelio 7 (point 2) ? Qui porte la décision de lancer ou non ce chantier noyau, et sur quel horizon ?

### 3.2bis Pistes de solution aux réserves de Cédric — le problème est plus petit qu'il n'y paraît 🆕

**Vérification faite sur le modèle live** : parmi les 20 classes secondaires distinctes des 34 cas, **seules 3 portent un attribut réellement stocké** (`Relationship.isImplied`, `Function.isModelLevelEvaluable`, `Expression.isModelLevelEvaluable` — trois simples booléens). **Les 17 autres classes secondaires n'ont strictement aucun attribut stocké** (`Classifier`, `Structure`, `Step`, `Association`, `AnnotatingElement`, `Succession`, `Behavior`, `DataType`, `BindingConnector`, `AssociationStructure`, `ConnectorAsUsage`, `Predicate`, `BooleanExpression`, `Connector`, `Flow`, `Metaclass`, `MetadataFeature`) — leur contenu réel, quand il existe, n'est que du calcul (opérations), pas de l'état persisté.

**Conséquence directe** : la « multiplication du nombre d'éléments de modèle » redoutée par Cédric ne concerne réellement qu'une quinzaine de cas sur 34, pas la totalité — la majorité des associations composées actuelles n'ont **aucune charge utile** à porter.

**Solutions concrètes, par catégorie de cas** :

| Catégorie | Cas concernés | Solution | Coût résiduel |
|---|---|---|---|
| Secondaire à un seul booléen | #3 (`Connector`→`Relationship`), #13 (`CalculationDefinition`→`Function`), #14 (`CalculationUsage`→`Expression`) | **Aplatir l'attribut directement sur la classe primaire** (`Semantic` attribute natif) — supprime l'objet composé entièrement | Zéro |
| Marqueur pur (0 attribut stocké) | Les 17 cas listés ci-dessus | **Accesseurs manuels** (déjà prévus en Partie 4.6) qui implémentent l'interface secondaire par délégation à l'état de la classe primaire, sans instance séparée — ou un **singleton/flyweight partagé** unique par métaclasse si un objet est requis pour une convention d'accès | Zéro à négligeable |
| Secondaire = vrai objet métier riche (ex. `StateUsage` cas #20) | Cas résiduels (~14) | **Instanciation paresseuse** : ne créer l'objet composé qu'au premier accès réel (`getDataType()`…), pas systématiquement à la création de l'élément primaire | Réel, mais différé et non systématique |
| Cohérence primaire/composé | Cas résiduels avec objet réel | **Règles d'audit bloquantes/synchrones** — déjà sur la propre checklist de Cédric (Partie 4.6, `AnalystCheckerFactory`), pas une nouvelle idée à développer, juste à appliquer à ces cas |
| Visibilité développeur | Tous | **Méthodes par défaut sur l'interface `mm.api`** — façade qui masque la composition, cohérent avec la « API de façade » évoquée par Cédric lui-même |

**Argument de contexte à faire valoir en réunion** : le précédent `ClassAssociation` (Partie 2.6) montre que Modelio paie déjà ce type de coût de duplication en production depuis 15 ans (`ClassPart` + `AssociationPart`) sans que ce soit un problème bloquant connu — élément de réassurance sur les cas résiduels qui ne peuvent pas être optimisés.

**Question à trancher** : valide-t-on cette classification par catégorie (aplatir/marqueur pur/paresseux) comme plan d'action concret, plutôt que de traiter les 34 cas de façon uniforme avec le seul patron d'association composée systématique ?

**Convergence 🆕 Réunion 09/09** : le correctif SemGen prototypé (cf. 3.2) implémente de fait une forme de la stratégie « aplatir » ci-dessus, mais généralisée à **tous** les membres du/des parent(s) secondaire(s) (attributs et associations, pas seulement les 3 cas à un seul booléen) plutôt que réservée aux seuls marqueurs sans contenu — l'aplatissement se fait désormais au niveau du générateur lui-même (`ModelUtils.getFlattenedOwnedAttributes`/`getFlattenedOwnedEnds`), pas au cas par cas dans `reference/design`. Reste ouvert : la classification par catégorie de cette section garde son intérêt pour décider **où** le composé (association composée) est encore nécessaire une fois l'aplatissement des membres généralisé — la perte de classification/polymorphisme (§4.5 de `limitation-heritage-multiple-semgen.md`) n'est en revanche pas résolue par l'aplatissement, seul le contenu (attributs/opérations) l'est.

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

### 4.5 Implémentation des bibliothèques normatives (Kernel Semantic Library / Systems Model Library) 🆕

**Constat** : KerML et SysML v2 ne sont pas *seulement* des métamodèles abstraits (les 182 classes de `reference` déjà couvertes Parties 1 à 3) — chacun s'accompagne d'une **bibliothèque de modèles normative** que toute métaclasse concrète doit obligatoirement spécialiser :
- KerML impose la **Kernel Semantic Library** (`Base`, `Links`, `Occurrences`, `Objects`, `Performances`, `Transfers`… — détaillée dans [kerml-sysml-metamodeles-detailles.md](../docs/kerml-sysml-metamodeles-detailles.md), Partie 3).
- SysML v2 impose par-dessus sa propre **Systems Model Library** (`Parts::Part`, `Ports::Port`, `Actions::Action`, `Requirements::RequirementCheck`… — même document, Partie 4.2), qui spécialise elle-même en cascade la Kernel Semantic Library.

**Pourquoi c'est obligatoire, pas une simple bonne pratique** : les deux specs truffent leurs métaclasses de contraintes du type `specializesFromLibrary('Base::Anything')`, `specializesFromLibrary('Parts::Part')`, `specializesFromLibrary('Occurrences::happensBeforeLinks')`, etc. — déjà rencontrées des dizaines de fois dans les deux études comparatives. Ce ne sont pas des suggestions : ce sont des **contraintes de conformité normatives**. Concrètement, une `PartDefinition` qui ne spécialise pas (directement ou indirectement) `Parts::Part` de la Systems Model Library **n'est pas un modèle SysML v2 valide**, quelle que soit la justesse de son implémentation Java par ailleurs. **Sans une instance réelle de ces bibliothèques présente dans le projet, aucun modèle utilisateur ne peut satisfaire ces contraintes** — la validité de tout modèle SysML v2 en dépend structurellement, pas seulement son « exhaustivité » ou sa « qualité ».

**Conséquence pratique pour l'implémentation Modelio** : il ne suffit pas de générer les métaclasses `implementation` (Parties 1 à 4) — il faut aussi **fournir, comme contenu de départ de tout projet SysML v2, les paquetages réels des deux bibliothèques**, avec leurs éléments (`Anything`, `Part`, `happensBeforeLinks`…) réellement instanciés et navigables, faute de quoi le mécanisme `specializesFromLibrary(...)` n'a tout simplement rien à cibler. C'est l'équivalent, côté Modelio, de ce qui existe déjà pour d'autres métamodèles (bibliothèques de types prédéfinis livrées avec un module) — mais ici la couverture doit être complète : chaque des ~20 packages de la Systems Model Library (Parts, Ports, Connections, Interfaces, Allocations, Flows, Actions, States, Calculations, Constraints, Requirements, Cases, AnalysisCases, VerificationCases, UseCases, Views, StandardViewDefinitions, Metadata…) et des ~6 packages de la Kernel Semantic Library (Base, Links, Occurrences, Objects, Performances, Transfers…) doit exister comme contenu réel, pas seulement comme référence documentaire.

**Questions ouvertes à trancher** :
- **Mode de livraison — affiné par le retour d'expérience SysML v1 (réunion Étienne Brosse, 25/08) 🆕** : la question « contenu par défaut vs module chargé à la demande » se résout différemment selon la bibliothèque concernée, une fois la distinction Systems Model Library / Domain Libraries prise en compte (cf. §4.3 du document [kerml-sysml-metamodeles-detailles.md](../docs/kerml-sysml-metamodeles-detailles.md)) :
  - La **Systems Model Library cœur** (celle portant les contraintes `specializesFromLibrary` obligatoires — `Parts`, `Ports`, `Actions`…) doit être **systématique et automatique** pour tout `SysMLProject`, sans action utilisateur — le principe reste inchangé.
  - Les **Domain Libraries optionnelles** (`Quantities and Units`, `Cause and Effect`, `Analysis`, `Requirement Derivation`…), elles-mêmes explicitement facultatives dans la spec (*« a conformant tool may provide one or more domain libraries »*), peuvent en revanche suivre le précédent déjà établi en SysML v1 chez Modelio : Étienne confirme que la bibliothèque SI (unités) de SysML v1 est un modèle construit dans un projet séparé, **packagé en `.jmdac`** et embarqué (ou proposé en déploiement à la demande) plutôt que dupliqué dans chaque projet. Étienne envisage explicitement de reproduire ce patron pour SysML v2 : *« ça sera peut-être pas à embarquer à chaque fois avec le métamodèle, mais une collection de [modules] à offrir [...] et se permettre d'offrir peut-être au client de déployer telle librairie pour s'en servir. »*
  - **Mécanisme technique confirmé (pas juste supposé)** : le précédent SysML v1 valide bien l'option « paquetage partagé, packagé en module Modelio (`.jmdac`), livré/déployé indépendamment » comme un mécanisme réel et déjà pratiqué chez Modelio — ça répond au point qui restait non vérifié précédemment.
- **Format d'échange normatif identifié 🆕** : Fadwa a confirmé que les bibliothèques SysML v2 (et plus généralement tout modèle SysML v2 conforme) sont distribuées/échangées sous le format **`.kpar`** (« KerML/SysML Project Archive »), le format d'interchange normatif exigé par la clause de conformité de la spec (*« every conformant SysML modeling tool shall demonstrate at least abstract syntax conformance »* via ce format) — cf. aussi `9.1` de `kerml.txt` sur les fichiers d'interchange normatifs, dont on a maintenant le nom concret. La **SysML v2 Pilot Implementation** (implémentation de référence de l'OMG) sait déjà parser ce format — ressource à évaluer pour l'équipe parsing (Bilal) et/ou pour importer directement le contenu des bibliothèques plutôt que de le reconstruire à la main.
- **Séquencement confirmé par Étienne 🆕** : l'import/export `.kpar` ne peut **pas** être construit avant d'avoir un métamodèle `implementation` fonctionnel avec un éditeur capable d'instancier réellement les métaclasses (« tu peux pas faire l'import-export tant que t'as pas un méta modèle avec la possibilité de créer des instances de tes métaclasses ») — confirme que ce chantier est **postérieur** aux Parties 1 à 4 de cette spec, pas un prérequis.
- **Origine du contenu** : génère-t-on ces paquetages **automatiquement** à partir des fichiers d'interchange `.kpar` normatifs publiés par l'OMG (la spec précise que chaque bibliothèque a une représentation machine-lisible normative, avec des `elementId` UUID stables calculés par une règle précise — cf. `9.1` de `kerml.txt`), ou les reconstruit-on manuellement dans Modelio ? La première option garantit la conformité aux UUID normatifs (traçabilité/interopérabilité avec d'autres outils SysML v2, et réutilise directement le format déjà identifié ci-dessus), la seconde est plus rapide mais risque des divergences.
- **Statut en écriture** : ces paquetages doivent-ils être **protégés en lecture seule** pour l'utilisateur final (cohérent avec leur rôle de référence normative), avec un mécanisme de mise à jour centralisé si l'OMG publie une révision ?
- **Impact sur le script de transformation** (4.1) : le script doit-il aussi importer/générer ces bibliothèques, ou est-ce un chantier séparé mené en parallèle ?

### 4.6 Étapes post-génération SemGen — intégration plugin Eclipse complète 🆕

Checklist technique transmise par Cédric Marin (basée sur les modules existants `Analyst` et `ArchiMate`) — ce qui reste à faire **après** que SemGen/Java Architect aient généré `mm.api`/`mm.impl` (Partie 4.1-4.3), avant d'avoir un module SysML v2 utilisable dans Modelio :

| Étape | Détail | Exemple de référence |
|---|---|---|
| Accesseurs manuels | Compléter les getters/setters non couverts par la génération automatique (ex. accesseurs de facette secondaire des associations composées, cf. 3.1) | — |
| Règles d'audit **bloquantes** (synchrones) | Contrôles de cohérence qui empêchent l'action si violés — candidat naturel pour garantir la cohérence primaire/composé exigée par Cédric (3.1) | `org.modelio.metamodel.impl.mmextensions.analyst.modelshield.AnalystCheckerFactory` |
| Règles d'audit **non bloquantes** (asynchrones) | Avertissements affichés a posteriori, sans bloquer l'utilisateur | `org.modelio.archimate.ui.audit.ArchimateAuditExtension` |
| Points d'extension du métamodèle | Code Java branchant un comportement personnalisé sur le métamodèle généré, via les services héritant de `org.modelio.vcore.smkernel.mapi.services.IMetamodelDependentService` (points d'extension Eclipse) | `org.modelio.metamodel.impl.mmextensions.analyst.AnalystMetamodelExtension` |
| IHM — icônes/images | Point d'extension `org.modelio.platform.model.ui.element.imageprovider`, interfaces `IElementImageProvider`/`IMetamodelImageProvider` | `org.modelio.archimate.ui.image.ArchimateElementImageProvider` |
| IHM — labels (arbre du modèle) | Point d'extension `org.modelio.platform.model.ui.labelprovider`, classe implémentant `IModelioElementLabelProvider` | `org.modelio.archimate.ui.browser.contrib.ArchimateBrowserLabelProvider` (déclaré dans `archimate.ui/plugin.xml`) |
| IHM — boîte de propriétés | Fournisseur dédié | `org.modelio.archimate.ui.modelproperty.ArchimatePropertyModelProvider` |
| IHM — menu « Create element » | Menu contextuel de création dédié | `org.modelio.archimate.ui.browser.context.ElementCreationDynamicMenuManager` |
| Diagrammes spécifiques | Éditeurs graphiques dédiés SysML v2 | — |

**Point de séquencement 🆕** : cette checklist s'ajoute à la mise en place des plugins elle-même, à traiter dans un premier temps selon Cédric — confirme que l'intégration Eclipse complète (au-delà de la seule génération du métamodèle) est un chantier à part entière, distinct des Parties 1 à 3.

**Action à faire** : programmer un point d'avancement dédié à l'héritage multiple avec Cédric (réserves de performance/mémoire/cohérence, cf. 3.1, et réévaluation de la piste SemGen, cf. 3.2).

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

### 5.5 Répartition des chantiers et infrastructure des plugins 🆕 Réunion 09/09

Antonin découpe le travail en deux chantiers parallèles, en plus du correctif SemGen déjà couvert en 3.2 :

- **Juan** continue sur le correctif SemGen (3.2) et contacte Christophe pour l'accès au projet de développement du module SMGen.
- **Fadwa** (avec l'appui de Juan) met en place les **plugins Eclipse** nécessaires à l'implémentation du métamodèle, sur le modèle du module **Archimate** pris comme référence (« il y a aucune doc [...] la méthode c'est de regarder ce qui est fait pour Archimède »).

Plugins à créer (implémentation vide au départ, l'implémentation réelle sera générée par SemGen une fois disponible) :

| Plugin | Rôle |
|---|---|
| Metamodel API | Interfaces `mm.api` générées par SemGen |
| Metamodel IMPL | Classes d'implémentation `mm.impl` générées par SemGen |
| Metamodel UI | Contributions au browser Modelio (entrées, ordre de parcours, commandes) |
| Diagram | Implémentation des diagrammes SysML v2 — prévu comme le plus gros lot de travail |
| Contribution | Points d'extension/bouchons pour les contributions externes (« la plupart des cas, c'est des bouchons qui font pas grand-chose ») |

**Convention de nommage** : `org.modelio.<domaine>.sysml2[.diagram|.metamodel.api|...]` (Antonin : « c'est du `.org` [...] ça pourra changer derrière »). Une **feature** (SFP, au sens Eclipse/RCP) rassemble ces plugins pour les intégrer à Modelio ; test recommandé : inclure la feature dans un packaging Modelio et lancer en debug, même avec une implémentation vide, pour valider que Modelio démarre avec les plugins chargés.

### 5.6 Workflow Git et accès module SMGen 🆕 Réunion 09/09

- **Branche de développement** : Antonin crée une branche `feature/SysML2` à partir de la branche Modelio `6.2` — tous les commits de l'équipe SysML v2 (plugins + métamodèle) s'y font exclusivement.
- **Cas particulier du module SMGen** : pas de branche séparée pour ce module — Antonin tranche pour un **tag**, posé par Christophe avant de donner l'accès en écriture à Juan, plutôt qu'une branche : « on ne va pas maintenir 2 versions de SemGen en parallèle [...] il nous faut qu'une version qui supporte les 2 [métamodèles mono- et multi-parent], qui gère les 2. » Le tag sert de filet de sécurité (retour arrière possible) sans fragmenter durablement le développement du module.
- **Méthode de travail sur le module SMGen** : projet de développement de module Modelio standard — générer le module une première fois, puis utiliser la commande Modelio de synchronisation des ressources SVN pour récupérer le contenu réel dans l'espace de travail.
- **Méthode de test recommandée par Antonin** : développer et valider d'abord dans un **projet Modelio local**, avec un petit bout de métamodèle propre à chaque testeur — jamais directement contre la base de développement partagée ou le fragment SysML2 de `modelio.all`. Une fois la génération validée en local, le module patché est déployé dans `modelio.all` pour tester sur le cas réel (cf. déjà appliqué dans les faits pour le correctif SemGen, projet de test `UML-BPMN`, cf. 3.2).

### 5.7 Chantier parallèle — prototype d'éditeur textuel synchronisé (Bilal) 🆕 Réunion 09/09

Bilal avance en parallèle sur la synchronisation bidirectionnelle éditeur textuel ↔ modèle graphique, sans attendre la finalisation du métamodèle SysML v2 :

- **Constat de marché** (revue de 4-5 ateliers de modélisation dont MagicDraw) : aucun ne supporte une vraie synchronisation continue à double sens — soit un import/export différé avec écrasement silencieux, soit l'éditeur textuel qui fait autorité et les diagrammes ne sont que générés.
- **Piste retenue** : s'appuyer sur l'implémentation par défaut **Xtext** de l'EMF (« vraiment pas mal ») plutôt que repartir de zéro, pour bénéficier nativement de l'auto-complétion, de la vue Problèmes, etc.
- **Risque technique identifié par Cédric** : les éditeurs Eclipse basés sur Xtext (et les éditeurs de diagrammes web Eclipse) reposent en interne sur un modèle **EMF** — y compris pour les éditeurs XMI. Une couche d'adaptation (AST) entre ce modèle EMF et le framework **MObject/MCore** de Modelio sera probablement nécessaire ; non garantie de fonctionner, mais poserait au moins les limites et contraintes réelles.
- **Décision** : Bilal prototype d'abord avec des **éléments UML génériques** (pseudo-langage), pas directement avec SysML v2, pour obtenir rapidement un résultat concret à démontrer — « une petite étude de faisabilité ».
- **Recommandation d'Antonin** : travailler sur la distribution **toolkit** (propriétaire) de Modelio plutôt que l'open source pur, pour disposer d'un environnement de debug complet dès le départ (la configuration Eclipse pour l'open source n'est probablement plus à jour) — même retour d'expérience que sur Tosca Designer par le passé (Juan/Amina) : toujours développer comme si c'était propriétaire, livrer une release open source seulement une fois prêt.

**Question à trancher** : ce prototype (hors périmètre du métamodèle SysML v2 lui-même) doit-il être suivi/synchronisé avec l'avancement du métamodèle (2.x, 3.x) pour éviter une divergence de noms/concepts, cf. Partie 0 et 5.2 ?

### 5.8 Lien avec le CIR 🆕 Réunion 09/09

Antonin propose à Bilal d'inclure ces travaux sur le support des métamodèles en graphe dans le CIR (crédit impôt recherche) si pertinent. Bilal attend d'avoir un résultat plus concret avant de se prononcer sur ce qui pourra être valorisé.

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
| 10 | Pas de 4ᵉ chevauchement à traiter dans `infrastructure` (mais 4 de plus trouvés hors périmètre) | 2.4 | Normale |
| 10b | Confirmer le rattachement des comportements entrée/sortie/activité sur `State` avant de valider le mapping | 2.5 | Normale |
| 10c | Remplacer l'association composée `AssociationStructure`/`Structure` par un alias direct `ClassAssociation` | 2.6 | Normale |
| 10d | Valider `UseCase`/`UseCaseDependency` comme socle de `UseCaseDefinition`/`UseCaseUsage` | 2.7 | Normale |
| 10e | Vérifier la cardinalité de `InformationFlow` avant de choisir entre `DataFlow` et `InformationFlow` pour `Flow` | 2.8 | Normale |
| 11 | Patron d'association composée pour héritage multiple, face aux réserves de Cédric (performance/mémoire/cohérence) | 3.1 | Critique |
| 12 | Réévaluer l'évolution de SemGen pour l'héritage multiple (piste rouverte) vs compenser par des règles d'audit | 3.2 | Critique |
| 12b | Adopter la classification par catégorie (aplatir/marqueur pur/paresseux) plutôt que le patron uniforme | 3.2bis | Critique |
| 13 | Revue cas par cas des 34 résolutions (avec exemples) | 3.3 | Normale |
| 14 | Structure finale du livrable (spec seule ou + exigences Modelio) | 5.1 | Normale |
| 15 | Canal de communication avec l'équipe parsing | 5.2 | Critique |
| 16 | Correctif SemGen (interface + aplatissement) suffisant seul, ou chantier noyau Modelio 7 nécessaire pour une vraie substituabilité polymorphique | 3.2 | Critique |
| 17 | Suivi du prototype d'éditeur textuel de Bilal en parallèle de l'avancement du métamodèle, pour éviter une divergence de noms/concepts | 5.7 | Normale |

---

*Sources : `points-a-trancher.md` (plan d'implémentation initial), transcription de la réunion du 27 août 2026 (39 min, participants : Juan Cadavid, Antonin Abhervé, Cédric Marin, Bilal Said, Fadwa Rekik, Laurent Gonçalves), transcription de la réunion du 09 septembre 2026 (33 min, participants : Juan Cadavid, Antonin Abhervé, Cédric Marin, Bilal Said, Fadwa Rekik), et suivi de commits `juancadavid` du 09-10/09/2026 (`limitation-heritage-multiple-semgen.md`, `semgen-patch-heritage-multiple.md`).*
