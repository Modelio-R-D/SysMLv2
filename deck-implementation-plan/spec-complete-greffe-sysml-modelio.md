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

### 2.1 Comment / Documentation → Note

| Concept KerML | Infrastructure Modelio | Traitement proposé |
|---|---|---|
| `Comment`, `Documentation` | `infrastructure::Note` | Mapper sur `Note` |

**Achoppements identifiés** :
1. `Comment` a 3 formes textuelles (explicite avec `about`, implicite, avec `locale`) — `Note` devra porter la `locale` et la contrainte structurelle propre à `Documentation` (élément documenté = propriétaire).
2. **Différence structurelle profonde, confirmée en réunion 🆕** : en SysML v2, un `Comment` peut être lié à **plusieurs éléments à la fois** (`about A, B`) ; en Modelio, une `Note` est **contenue en composition** dans l'unique élément qu'elle documente (1..1). Cédric confirme : « Pas avec les notes [...] c'est avec les contraintes qu'on peut le faire, et ça peut poser problème. » Ce n'est donc pas qu'une nuance : **un cas d'usage SysML v2 valide ne peut pas être modélisé tel quel avec l'infrastructure actuelle**.
3. **Propriété `locale` non portée nativement 🆕** : à ajouter sur `Note`, ou fonctionnalité d'internationalisation repoussée à un cycle ultérieur — à trancher explicitement.

**Question à trancher** :
- Valide-t-on le mapping `Comment/Documentation → Note` malgré la perte de multi-cible ?
- Comment représente-t-on la liaison d'un commentaire à plusieurs éléments (duplication ? relation n-aire dédiée ?) — un développement spécifique (nouvelle vue de propriétés) est-il accepté si besoin ?
- Supporte-t-on `locale` dès la v1 ?

### 2.2 Dependency → Dependency

| Concept KerML | Infrastructure Modelio | Traitement proposé |
|---|---|---|
| `Dependency` | `infrastructure::Dependency` | Alias direct |

**Achoppements identifiés** :
1. Le `Dependency` Modelio peut porter des comportements/stéréotypes hérités du contexte UML — à vérifier qu'aucun ne s'applique par erreur à un lien KerML.
2. **Pas de support n-aire côté Modelio, confirmé en réunion 🆕** : KerML permet `dependency X to Y, Z;` (un client, plusieurs fournisseurs en une seule relation). Modelio ne représente qu'un lien binaire. Cédric : « On supporte pas ça [le n-aire]. On a sabré, simplifié. » Antonin : « Tu traduis par 2 dépendances chez nous, faut voir ça comme ça » (`X→Y` et `X→Z`).

**Point non résolu 🆕** : cette décomposition n-aire → binaire doit être assurée par un traducteur (probablement au niveau du parsing textuel). Reste à clarifier :
- Qui implémente ce parseur (équipe Modelio vs équipe parsing, cf. Bilal) ?
- La transformation est-elle réversible pour un roundtrip modèle → texte → modèle sans perte ?

**Question à trancher** : valide-t-on l'alias direct et la stratégie de décomposition n-aire → binaire(s) ?

### 2.3 MetadataDefinition/MetadataUsage → Stereotype/TaggedValue ou PropertyTable

| Concept KerML/SysML | Infrastructure Modelio | Traitement proposé |
|---|---|---|
| `MetadataDefinition`, `MetadataUsage` | `infrastructure::Stereotype` + `TaggedValue`, ou `PropertyTable` | Mapper sur le sous-système Stereotype/TaggedValue/PropertyTable |

**Achoppement le plus significatif des trois** : un `MetadataUsage` s'attache à plusieurs cibles à la fois en une seule instance (`about A, B, C`). En Modelio, un `Stereotype` (définition) peut être appliqué à plusieurs éléments, mais **chaque application** (`ExtensionValue`) ne concerne qu'un seul élément de base.

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

**Proposition** : pour chaque cas, l'axe **Definition/Usage** gagne `extends` ; l'autre axe devient une interface `mm.api`, implémentée par délégation à un objet interne portant son état (« Behavior »). Approche alignée sur *Replace Inheritance with Delegation* / *Role Object* (Fowler) et sur le flattening EMF/Ecore.

**Contrainte technique bloquante, révélée en réunion 🆕** : Cédric confirme que **SemGen rejette (bloque) tout métamodèle contenant un héritage multiple réel**, y compris à titre intermédiaire dans les interfaces `mm.api` si elles sont générées avec 2 `extends`. Antonin nuance : la solution de délégation systématique proposée par Juan **ne peut pas être appliquée mécaniquement partout** — le cas des sous-classes qui utiliseraient elles-mêmes un des deux axes délégués complique la désambiguïsation (pas de solution générique universelle, seulement du cas par cas).

**Conséquence pratique 🆕** : le script de transformation `reference → implementation` (Partie 4) doit produire des classes avec un seul `extends` réel + des `implements` d'interfaces déléguées — jamais une classe/interface avec double `extends` — pour rester compatible avec SemGen tel qu'il existe aujourd'hui.

**Question à trancher** : 
- Valide-t-on le principe général de délégation comme règle par défaut, en acceptant qu'il faille une revue cas par cas (pas un algorithme 100 % automatique) ?
- Le script doit-il détecter/avertir sur les cas où le pattern générique ne suffit pas (sous-classes des axes délégués) ?

### 3.2 Piste d'évolution outillage 🆕 (non tranchée)

Juan propose de **contribuer à SemGen** pour qu'il applique automatiquement le pattern de délégation plutôt que de traiter les 34 cas à la main. Antonin/Cédric ouverts au principe mais posent la question de la pertinence/du coût : « Est-ce que c'est pertinent de le faire ? Faudra qu'on décide. »

**Question à trancher** : investit-on du temps dans une évolution de SemGen (bénéfice : futurs métamodèles), ou traite-t-on les 34 cas manuellement pour ce projet (plus rapide à court terme) ?

### 3.3 Les 34 résolutions individuelles

Cas 1–7 : noyau KerML. Cas 8–34 : niveau SysML.

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
| 5 | Mapping `Comment/Documentation → Note` malgré perte multi-cible | 2.1 | Critique |
| 6 | Support de `locale` sur Note dès la v1 | 2.1 | Normale |
| 7 | Alias `Dependency`, décomposition n-aire → binaire(s) | 2.2 | Normale |
| 8 | `PropertyTable` (pas TaggedValue) pour `MetadataDefinition/Usage` | 2.3 | Critique |
| 9 | Vue IHM dédiée « Metadata » pour ne pas perdre l'utilisateur | 2.3 | Normale |
| 10 | Pas de 4ᵉ chevauchement à traiter | 2.4 | Normale |
| 11 | Règle générale de délégation pour héritage multiple + limites SemGen | 3.1 | Critique |
| 12 | Investir dans une évolution de SemGen ou traiter les 34 cas à la main | 3.2 | Normale |
| 13 | Revue cas par cas des 34 résolutions (avec exemples) | 3.3 | Normale |
| 14 | Structure finale du livrable (spec seule ou + exigences Modelio) | 5.1 | Normale |
| 15 | Canal de communication avec l'équipe parsing | 5.2 | Critique |

---

*Sources : `points-a-trancher.md` (plan d'implémentation initial) et transcription de la réunion du 27 août 2026 (39 min, participants : Juan Cadavid, Antonin Abhervé, Cédric Marin, Bilal Said, Fadwa Rekik, Laurent Gonçalves).*
