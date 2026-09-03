# Étude comparative KerML ↔ Infrastructure Modelio — passage classe par classe

Étude complémentaire à [spec-complete-greffe-sysml-modelio.md](./spec-complete-greffe-sysml-modelio.md), qui couvre déjà en détail `AnnotatingElement` (`Comment`, `Documentation`, `TextualRepresentation`), `MetadataUsage`/`MetadataDefinition` et `Dependency` (Partie 2). **Ce document ne les reprend pas** — il étudie systématiquement le **reste** des métaclasses des couches **Root**, **Core** et **Kernel** de KerML (spec `kerml.txt`), en les confrontant une par une à l'infrastructure Modelio (`org.modelio.metamodel.uml.*`, cf. [Modelio-API-Markdown-CHUB/docs-UML/uml.md](../../../Modelio-API-Markdown-CHUB/docs-UML/uml.md)).

## Méthodologie

Pour chaque métaclasse KerML : définition résumée, attributs/cardinalités clés (`[min..max]`), candidat Modelio identifié (ou absence de candidat), verdict, et problèmes de cardinalité/sémantique le cas échéant.

**Légende des verdicts** :
- ✅ **Équivalent net** — même rôle structurel, cardinalités compatibles.
- ⚠️ **Équivalent partiel** — un candidat existe mais diverge (cardinalité, sémantique, ou les deux).
- ❌ **Aucun équivalent** — concept absent de Modelio, à construire entièrement dans `implementation`.
- 🔀 **Faux ami** — un nom identique ou proche existe dans Modelio mais désigne un concept différent (risque de confusion).

---

## Constats transversaux (à lire en premier)

Ces constats dépassent le cadre d'une classe isolée — ils affectent des familles entières de métaclasses et doivent être tranchés comme des **principes d'architecture**, pas comme des cas particuliers.

### 1. ❌ La réification de `Membership`/`Import` n'a pas d'équivalent Modelio — écart le plus fondamental de toute l'étude

En KerML, l'appartenance d'un élément à un espace de noms (`Namespace`) n'est **pas** une simple relation de composition implicite : c'est un objet de relation à part entière, `Membership` (et sa spécialisation `OwningMembership`), qui porte :
- un **nom d'alias** différent du nom propre de l'élément (`memberName`/`memberShortName`, distincts de `Element.name`),
- une **visibilité** (`VisibilityKind` : `public`/`protected`/`private`) **par relation d'appartenance**, pas par élément,
- la possibilité qu'**un même élément soit membre de plusieurs `Namespace` à la fois**, chacun avec son propre alias et sa propre visibilité (« la même `Element` peut être le `memberElement` de plusieurs `Memberships` dans un `Namespace` »).

Le mécanisme d'`Import` (`MembershipImport`/`NamespaceImport`) construit ensuite des `Membership` supplémentaires *dérivées* dans un autre `Namespace`, avec leur propre visibilité et leur propre logique de récursivité (`isRecursive`, `isImportAll`).

**Modelio n'a rien de comparable** : l'appartenance d'un élément à son conteneur est une **composition native** de l'arbre `MObject` (`getCompositionOwner()`/`getCompositionChildren()`), pas un objet de relation. Il n'existe pas de mécanisme permettant à un même élément d'apparaître, avec des noms différents, dans plusieurs espaces de noms distincts, ni de visibilité *par relation d'appartenance* (Modelio a bien un concept de visibilité — `VisibilityMode`, cf. Constat 4 — mais porté par l'élément ou son usage local, pas par une relation réifiée et potentiellement multiple).

**Pourquoi c'est plus grave que les autres écarts déjà documentés** : ce n'est pas une classe isolée qui pose problème, c'est **le mécanisme même de résolution de noms** (`resolve`, `resolveLocal`, `resolveVisible`, `resolveGlobal` sur `Namespace`) qui repose entièrement sur la réification de `Membership`. Tout le moteur de résolution de noms du langage textuel SysML v2 (essentiel pour l'équipe parsing de Bilal, cf. Partie 5.2 de la spec principale) devra soit : (a) être réimplémenté entièrement au-dessus de la composition native de Modelio en simulant `Membership` par un mécanisme parallèle, soit (b) réifier `Membership` comme une vraie nouvelle métaclasse `implementation`, ce qui s'écarte fortement des conventions actuelles de Modelio (où l'appartenance n'est jamais un objet).

**Question à trancher** : réifie-t-on `Membership`/`Import` comme de vraies métaclasses dans `implementation` (fidélité à la spec, mais rupture avec les conventions Modelio), ou tente-t-on de simuler leur effet par-dessus la composition native (moins fidèle, risque de ne jamais couvrir les cas où un même élément est membre de plusieurs espaces de noms) ?

### 2. ❌ L'algèbre de types KerML (`Conjugation`, `Unioning`, `Intersecting`, `Differencing`, `Disjoining`) est un concept sans aucun équivalent Modelio

KerML définit, en plus de la spécialisation simple (`Specialization`, ✅ équivalent net à `Generalization` de Modelio), quatre opérateurs algébriques sur les types qui n'existent dans aucune forme dans le métamodèle UML/Modelio :
- **`Conjugation`** : un type « conjugué » hérite de toutes les Features d'un type original mais avec `in`/`out` inversés (mécanisme des ports SysML v2 notamment).
- **`Unioning`** / **`Intersecting`** / **`Differencing`** : un type peut être défini comme l'union, l'intersection ou la différence ensembliste d'autres types.
- **`Disjoining`** : assertion que deux types n'ont aucune instance en commun.

**Aucun de ces cinq mécanismes n'a de contrepartie dans Modelio**, même approximative — le modèle de classification UML (`Generalization` simple) ne connaît que la spécialisation. Ce ne sont pas des attributs ou des associations qu'on peut ajouter facilement : ce sont des **algorithmes de raisonnement sur les types** (ex. `Type.specializes()`, `Type.supertypes()` doivent tenir compte de la conjugaison pour inverser les directions de Features en cascade) qui devront être **conçus et implémentés from scratch** dans `implementation`, sans le moindre point de départ dans l'infrastructure existante.

**Question à trancher** : ces opérateurs sont-ils dans le périmètre de la v1 (risque de développement significatif, en dehors du strict mapping infra), ou repoussés à une itération ultérieure avec un mode dégradé documenté (ex. `Conjugation` traitée comme une simple duplication manuelle de type inversé, sans mécanisme générique) ?

### 3. ⚠️ `Multiplicity` est un objet réifié typé par des `Expression`, Modelio ne connaît que des entiers plats

En KerML, la cardinalité (`Multiplicity`/`MultiplicityRange`) est elle-même une **Feature** du modèle, dont les bornes (`lowerBound`/`upperBound`) sont des **`Expression`** potentiellement évaluables dynamiquement (ex. une borne paramétrée par la valeur d'un autre attribut). Modelio, lui, stocke min/max comme de simples entiers plats directement sur `Attribute`, `AssociationEnd` ou `Parameter` (pas d'objet dédié, pas d'expression).

**Conséquence** : le mapping fonctionnera **pour le cas courant** (bornes littérales du type `[0..*]`, `[1..1]`), mais perd la possibilité de bornes *calculées* (`[1..n+1]` par exemple) — cas sans doute rare en pratique mais à documenter comme une limitation assumée, pas un oubli.

### 4. 🔀 Faux amis à surveiller — noms partagés, sens différents

| Nom partagé | KerML | Modelio | Risque |
|---|---|---|---|
| **`Interaction`** | `Behavior` + `Association` (KerML 8.3.4.9.4) — concept **abstrait et générique** de contexte reliant plusieurs objets dont les comportements s'influencent (aucun attribut propre) | `Interaction` (`interactionModel`) — concept concret de **diagramme de séquence** (lifelines, messages, fragments combinés) | Confusion quasi-garantie dans le code/la documentation si les deux se retrouvent dans le même espace de noms Java — déjà signalé comme cas #5 de l'héritage multiple (`Interaction extends Behavior implements Association`) : il faut absolument **ne pas** faire hériter/pointer ce `Interaction` KerML vers le `Interaction` UML de Modelio, ce sont deux concepts sans rapport. |
| **`Class`** | Classificateur de « choses distinguables sans égard à leurs relations » (KerML 8.3.4.2) | `Class` (`statik`) — concept central de modélisation orientée objet (UML Class) | Proche mais pas identique : le `Class` Modelio porte des dizaines d'années de sémantique UML (opérations, visibilité, `isActive`…) que `Class` KerML n'a pas. Risque d'importer involontairement des comportements UML non désirés en héritant du `Class` Modelio directement (cf. le principe déjà établi en Partie 0 de la spec principale : accepter le rattachement mais documenter l'écart). |
| **`Structure`** | Classificateur d'objets « principalement structurels » (KerML 8.3.4.3), sans attribut propre | Aucun concept `Structure` dédié dans Modelio — le rôle le plus proche est encore `Class` (souvent avec un stéréotype ou juste `isActive=false`) | Pas un vrai faux ami (le nom n'existe pas tel quel côté Modelio) mais souligne que `Structure` et `Class` KerML se rejoignent tous deux sur le même `Class` Modelio — cohérent avec le choix déjà fait au cas #24 (`ItemDefinition implements Structure`) de traiter `Structure` comme un marqueur pur. |
| **`Succession`** | `Connector` binaire imposant un ordre temporel strict (KerML 8.3.4.5.4) | Aucun concept `Succession` dans le métamodèle `statik`/`infrastructure` — le plus proche serait `GeneralOrdering` (`interactionModel`), mais celui-ci s'applique aux `OccurrenceSpecification` de diagrammes de séquence, pas à des `Connector` structurels | Pas un faux ami direct mais un piège potentiel : ne pas réutiliser `GeneralOrdering` par analogie de nom, le contexte est complètement différent (diagramme de séquence vs modèle structurel). |

---

## Partie A — Couche Root (au-delà d'Annotations/Dependency déjà traités)

### A.1 `Element` (8.3.2.1.2)

Racine absolue de toute la hiérarchie KerML — porte `elementId`, `name`, `shortName`, `qualifiedName`, `ownedRelationship`, `owner`, `documentation`, `textualRepresentation`.

**Candidat Modelio** : `infrastructure::Element` / `ModelElement` — ✅ **équivalent net**, déjà retenu comme point de greffe (Partie 1.1 de la spec principale : `KerMLModelElement extends ModelElement`). Aucun problème de cardinalité identifié à ce niveau — c'est la racine, elle hérite « gratuitement » du mécanisme de composition natif de Modelio (`MObject`).

### A.2 `Relationship` (8.3.2.1.3)

Relation générique avec `source : Element [1..*] {ordered}` et `target : Element [1..*] {ordered}`, plus `relatedElement`, `isImplied`, `ownedRelatedElement`.

**Candidat Modelio** : aucune classe unique « Relationship » générique dans `org.modelio.metamodel.uml.infrastructure` — Modelio n'a pas de super-type commun réifiant toutes ses relations (`Dependency`, `Association`, `Generalization`… sont des interfaces indépendantes, sans racine commune `Relationship`). **⚠️ Équivalent partiel** : le *rôle* existe (chaque relation Modelio a bien une source et une cible), mais il n'y a pas de point de greffe unique pour porter le comportement générique `Relationship` de KerML (ex. `isImplied`, déjà noté comme porté par le délégué `RelationshipBehavior` au cas #3 `Connector`).

**Cardinalité à noter** : `source`/`target` sont `[1..*]` en KerML (une relation peut avoir plusieurs sources ET plusieurs cibles simultanément) — la plupart des relations Modelio (`Dependency`, `Association` binaire...) sont conçues pour 1 source/1 cible ou une liste sur un seul côté, jamais une vraie relation n-aire symétrique des deux côtés (cf. le constat déjà fait sur `Dependency` en Partie 2.2 de la spec principale — ce constat se généralise donc à `Relationship` tout entier, pas seulement à `Dependency`).

### A.3 Namespaces, Membership, Import (8.3.2.4)

Cf. **Constat transversal 1** ci-dessus pour l'analyse de fond. Détail classe par classe :

| Classe KerML | Rôle | Candidat Modelio | Verdict |
|---|---|---|---|
| `Namespace` | Élément contenant d'autres éléments via des `Membership` | `NameSpace` (`statik`) | ⚠️ Le rôle de conteneur existe, mais sans réification de `Membership` (cf. constat 1) — `NameSpace` Modelio ne porte que la composition native |
| `Membership` | Relation réifiée d'appartenance, alias, visibilité | *Aucun* | ❌ Pas d'équivalent — composition native de Modelio, pas de relation réifiée |
| `OwningMembership` | `Membership` qui possède son élément | *Aucun* (composition native) | ❌ |
| `Import` | Relation générique d'import | `PackageImport`/`ElementImport` (`statik`) portent un rôle analogue mais **sans** passer par une `Membership` intermédiaire | ⚠️ Rôle fonctionnel similaire (importer des éléments d'un autre espace de noms), mécanique interne différente |
| `MembershipImport` | Import d'une `Membership` unique | `ElementImport` | ⚠️ Équivalent partiel — `ElementImport` importe un élément, pas une `Membership` avec son alias propre |
| `NamespaceImport` | Import de tous les membres visibles d'un `Namespace` | `PackageImport` | ✅ Assez proche fonctionnellement (importer en bloc le contenu visible d'un package) |
| `VisibilityKind` (`public`/`protected`/`private`) | Visibilité par `Membership` | `VisibilityMode` (Enum, `statik`) | ⚠️ Les valeurs existent (à vérifier si Modelio a bien les 3 mêmes, ou seulement `public`/`private`), mais portée différemment (par élément, pas par relation d'appartenance) |

---

## Partie B — Couche Core (système de types)

### B.1 `Type` (8.3.3.1.10) — la classe la plus structurellement importante de tout KerML

`Type extends Namespace` — porte `isAbstract`, `isSufficient`, `/isConjugated`, et surtout tout le calcul de `supertypes()`, `specializes()`, `multiplicities()`, `feature`, `inheritedFeature`, `ownedFeature`... C'est la classe qui définit ce que signifie « classifier quelque chose » en KerML, mère commune de `Classifier` ET de `Feature` (contrairement à UML où `Classifier` et `Feature`/`Property` sont des hiérarchies séparées).

**Candidat Modelio** : aucun. Modelio a bien un `Classifier` (`statik`), mais **pas de super-type commun entre `Classifier` et `Feature`** — en UML/Modelio, une `Feature` (`Attribute`, `Operation`...) n'est jamais elle-même un type classificateur. **❌ Aucun équivalent** pour le concept `Type` en tant que tel — c'est une différence de paradigme fondamentale : KerML unifie « être un type » et « être une caractéristique typée » sous un même ancêtre (`Type`), Modelio les sépare strictement. Ceci est cohérent avec ce qu'on savait déjà (cas #3 `Connector extends Feature`, cas #11 `AttributeDefinition extends Definition implements DataType`...) mais mérite d'être nommé explicitement comme la cause racine de beaucoup des 34 cas d'héritage multiple déjà traités.

**Cardinalité `isSufficient`** : concept absent de Modelio (pas de notion de « classification suffisante » vs « nécessaire »), à traiter comme une propriété à ajouter sans équivalent, indépendamment du reste.

### B.2 `Classifier` (8.3.3.2.2)

`Classifier extends Type` — ne rajoute qu'une seule opération (`isConjugated`, hérité) et une contrainte de spécialisation. Structurellement un marqueur quasi pur.

**Candidat Modelio** : `Classifier` (`statik`) — ✅ **équivalent net** de nom et de rôle général (« vue abstraite des métaclasses importantes comme Class, UseCase, Actor... »). Bonne nouvelle : c'est un des rares cas où le nom ET le rôle correspondent directement.

### B.3 `Feature` (8.3.3.3.4) — non détaillé en profondeur ici (déjà largement couvert via les 34 cas d'héritage multiple), mais point de cardinalité notable

`Feature extends Type` porte, entre autres, `direction : FeatureDirectionKind [0..1]`, `isEnd`, `isComposite`, `isDerived`, `isOrdered`, `isUnique`, `isPortion`, `isReadOnly`, `isVariable`.

**Candidat Modelio** : `Feature` (`statik`) — ✅ le nom et une bonne partie des attributs (`isComposite`-like via `AggregationKind`, ordering...) coïncident, déjà utilisé comme cible de délégation dans plusieurs des 34 cas (`Connector implements ...`, etc.). Pas de nouveau problème de cardinalité identifié au-delà de ceux déjà documentés.

### B.4 `FeatureDirectionKind` (8.3.3.1.5)

Énumération `in`/`out`/`inout`. **Candidat Modelio** : `PassingMode` (`statik`, Enum pour les `Parameter`) porte une distinction similaire (in/out/inout pour les paramètres d'opération) — ✅ **équivalent net**, mais **seulement dans le contexte des `Parameter`** ; KerML applique `direction` à *toute* `Feature` (pas seulement aux paramètres), ce qui est plus large que l'usage Modelio actuel de `PassingMode`.

### B.5 `FeatureMembership` (8.3.3.1.6)

`FeatureMembership extends OwningMembership` — relation réifiée entre un `owningType` et sa `ownedMemberFeature`. Même remarque que le constat 1 : c'est encore une `Membership`, donc **❌ pas d'équivalent** en tant que relation réifiée — côté Modelio, la possession d'un `Attribute`/`Operation` par une `Classifier` est une composition native, pas un objet à part.

### B.6 Opérateurs algébriques de types — `Specialization`, `Conjugation`, `Disjoining`, `Unioning`, `Intersecting`, `Differencing`

| Classe | Rôle | Candidat Modelio | Verdict |
|---|---|---|---|
| `Specialization` | Généralisation simple (`specific`/`general`) | `Generalization` (`statik`) | ✅ **équivalent net** — le seul des 6 opérateurs à avoir un vrai équivalent |
| `Conjugation` | Inversion des directions de Features | *Aucun* | ❌ cf. constat transversal 2 |
| `Disjoining` | Assertion de disjonction entre 2 types | *Aucun* | ❌ cf. constat transversal 2 |
| `Unioning` | Type = union d'autres types | *Aucun* | ❌ cf. constat transversal 2 |
| `Intersecting` | Type = intersection d'autres types | *Aucun* | ❌ cf. constat transversal 2 |
| `Differencing` | Type = différence ensembliste d'autres types | *Aucun* | ❌ cf. constat transversal 2 |

### B.7 `Multiplicity` (8.3.3.1.9) / `MultiplicityRange` (8.3.4.11.2)

Cf. **constat transversal 3**. `Multiplicity extends Feature` (encore l'unification Type/Feature du constat B.1) ; `MultiplicityRange` porte `lowerBound`/`upperBound : Expression`.

**Candidat Modelio** : pas d'objet dédié — `Attribute`, `AssociationEnd`, `Parameter` portent chacun directement des entiers min/max (à vérifier précisément le nom des attributs par classe, mais le principe est constant dans tout Modelio : pas de réification de la cardinalité). **⚠️ Équivalent partiel** — le résultat final (les bornes numériques) est compatible, mais la structure (objet réifié + expressions évaluables) ne l'est pas. Cf. constat 3 pour la limitation assumée (pas de bornes calculées dynamiquement).

---

## Partie C — Couche Kernel (structures, connecteurs, comportements, expressions)

### C.1 `DataType` (8.3.4.1.2) / `Class` (8.3.4.2.2) / `Structure` (8.3.4.3.2)

Trois classificateurs `Classifier` distingués uniquement par une règle sémantique abstraite (« distinguable ou non sans égard aux relations », « objet structurel ou non »), **sans attribut propre pour aucun des trois**.

| Classe KerML | Candidat Modelio | Verdict |
|---|---|---|
| `DataType` | `DataType` (`statik`) | ✅ **équivalent net** — nom et rôle correspondent (« types incluant nombres, chaînes, valeurs énumérées ») |
| `Class` | `Class` (`statik`) | 🔀 **Faux ami partiel** — cf. constat transversal 4, le nom correspond mais `Class` Modelio porte beaucoup plus de sémantique UML héritée |
| `Structure` | Pas de métaclasse `Structure` dédiée — role couvert par `Class` (souvent avec un stéréotype) | ⚠️ Équivalent partiel, cohérent avec le traitement déjà retenu en cas #24 (marqueur pur délégué) |

### C.2 `Association` / `AssociationStructure` — déjà traités (cas #1/#2 de la spec principale), complément trouvé ici

En creusant l'infrastructure Modelio pour cette étude, une piste plus directe a été identifiée pour `AssociationStructure` : Modelio possède nativement **`ClassAssociation`** (`statik`) — *« A ClassAssociation is represented in UML as a Class that plays the role of an Association »* — qui correspond **exactement** à la définition KerML de `AssociationStructure` (« classifying link objects that are both links and objects »). 

**Recommandation à intégrer à la Partie 3.3 de la spec principale** : pour le cas #2 (`AssociationStructure extends Association` + association composée vers `Structure`), vérifier si un alias direct sur `ClassAssociation` (qui est déjà nativement les deux à la fois dans Modelio) ne serait pas une solution plus simple et plus fidèle que le patron générique d'association composée — à date, **piste non encore validée par une génération SemGen réelle**, à tester avant d'adopter.

### C.3 `Connector` (déjà traité, cas #3) / `BindingConnector` (8.3.4.5.2) / `Succession` (8.3.4.5.4)

| Classe KerML | Rôle | Candidat Modelio | Verdict |
|---|---|---|---|
| `BindingConnector` | `Connector` binaire imposant l'identité des valeurs aux deux bouts | Pas de métaclasse dédiée dans `statik`/`infrastructure` — `Connector` (`statik`) est générique, sans notion de « binding » | ❌ **Aucun équivalent** — à construire (déjà implicitement nécessaire vu le cas #12 `BindingConnectorAsUsage` de la spec principale, mais ce constat s'applique aussi au KerML `BindingConnector` racine lui-même, pas seulement à sa variante SysML) |
| `Succession` | `Connector` binaire imposant un ordre temporel strict | Aucun (cf. constat transversal 4 — ne pas confondre avec `GeneralOrdering`) | ❌ **Aucun équivalent** |

### C.4 `Behavior` (8.3.4.6.2) / `Step` (8.3.4.6.3) / `ParameterMembership` (8.3.4.6.4)

`Behavior extends Class`, porte `parameter`/`step` (dérivés). `Step extends Feature`, typé par un ou plusieurs `Behavior`.

**Candidats Modelio** :
- `Behavior` → `Behavior` (`commonBehaviors`) — ✅ **équivalent net** de nom, mais `Behavior` Modelio est conçu comme abstraction pour `Activity`/`Interaction`/`StateMachine`/`OpaqueBehavior` (diagrammes concrets), pas comme concept générique abstrait — à vérifier que le rattachement n'importe pas de comportement de diagramme non désiré (même logique de prudence que pour `Class`, constat 4).
- `Step` → **❌ aucun équivalent direct**. Le plus proche serait `ActivityNode`/`ActivityAction` (`activityModel`), mais ceux-ci sont eux-mêmes fortement couplés aux diagrammes d'activité UML, pas au concept abstrait KerML de « pas comportemental typé par un Behavior ».
- `ParameterMembership` → encore une spécialisation de `Membership` (cf. constat 1) — ❌ pas d'équivalent réifié ; le rôle (identifier un paramètre) est couvert nativement par `Parameter` (`statik`) mais sans la relation `ParameterMembership` elle-même.

### C.5 Famille `Function`/`Predicate`/`Invariant`/`BooleanExpression`/`Expression` (8.3.4.7—8.3.4.8) — ❌ absence quasi totale côté Modelio

C'est la famille la plus étendue de tout KerML (une vingtaine de classes : `Expression`, `Function`, `Predicate`, `Invariant`, `BooleanExpression`, et tous les types d'expressions concrètes — `LiteralBoolean`, `LiteralInteger`, `LiteralRational`, `LiteralString`, `LiteralInfinity`, `OperatorExpression`, `InvocationExpression`, `FeatureChainExpression`, `FeatureReferenceExpression`, `IndexExpression`, `InstantiationExpression`, `CollectExpression`, `ConstructorExpression`, `SelectExpression`, `MetadataAccessExpression`, `NullExpression`). Ensemble, elles forment un **véritable petit langage d'expression exécutable et évaluable au niveau du modèle** (`isModelLevelEvaluable`), avec littéraux, opérateurs, invocation de fonctions, navigation de chemins de features (`FeatureChainExpression`), etc.

**Modelio n'a aucune notion de langage d'expression dans son métamodèle central.** Le seul point de contact est `Constraint.Body : String` (Partie 2.1 de la spec principale) — un texte libre non structuré, sans évaluation. **❌ Aucun équivalent, pour l'intégralité de la famille.**

**Portée du problème** : `Invariant` (assertions vrai/faux), `Predicate` (fonction booléenne 1..1) et `BooleanExpression` sont directement utilisés dans les 34 cas d'héritage multiple déjà traités (`AssertConstraintUsage implements Invariant`, `ConstraintDefinition implements Predicate`, `ConstraintUsage implements BooleanExpression`, cas #10/#18/#19) — ce constat renforce donc, avec une base factuelle précise, l'ampleur du travail déjà pressenti pour ces cas : ce ne sont pas seulement des problèmes d'héritage multiple à résoudre par association composée, ce sont des concepts **sans aucune brique de départ côté infrastructure**, entièrement à concevoir.

**Question à trancher** : quel niveau de fidélité vise-t-on pour ce langage d'expression dans la v1 ? Options possibles (à arbitrer) :
1. Fidélité complète (réimplémenter tout l'arbre d'expressions KerML comme nouvelles métaclasses `implementation`) — gros effort, mais nécessaire si on veut une vraie évaluation de contraintes/calculs.
2. Fidélité dégradée : stocker le texte de l'expression comme corps libre (à la `Constraint.Body`), sans structure ni évaluation — cohérent avec le traitement déjà proposé pour `Comment`/`Documentation`, mais perd toute capacité de calcul réel (`isModelLevelEvaluable` deviendrait sans objet).
3. Fidélité intermédiaire : ne modéliser que les nœuds réellement utilisés par les contraintes des 34 cas déjà identifiés (`Invariant`, `Predicate`, `BooleanExpression`), sans couvrir tout l'arbre des expressions littérales/opérateurs.

### C.6 `Interaction` (Kernel, 8.3.4.9.4) / `Flow` / `FlowEnd` / `PayloadFeature` / `SuccessionFlow`

Déjà traités dans les 34 cas (cas #5, #4, #7, #21, #22, #34) pour la résolution d'héritage multiple. Complément trouvé ici :

- **`Interaction`** : cf. **constat transversal 4** — ne pas confondre avec `interactionModel::Interaction` de Modelio (faux ami).
- **`FlowEnd`** (`Feature` avec `isEnd`, exactement 1 `ownedFeature`) : ❌ pas d'équivalent Modelio dédié — le concept le plus proche serait `ConnectorEnd` (`statik`), mais celui-ci n'a pas la contrainte spécifique « doit avoir exactement une feature possédée » ; à traiter comme une extension du pattern déjà établi pour `Connector`/`ConnectorEnd`.
- **`PayloadFeature`** : ❌ aucun équivalent (feature qui identifie « ce qui est transporté » par un flux) — concept absent de Modelio, qui n'a pas de notion de flux de données typé au niveau du métamodèle central (les `DataFlow`/`InformationFlow` du package `informationFlow` sont plus proches d'un usage diagrammatique que d'un concept structurel réutilisable ici).

### C.7 `FeatureValue` (8.3.4.10.2)

`FeatureValue extends OwningMembership` — encore une spécialisation de `Membership` (constat 1) qui, en plus, relie une `Feature` à une `Expression` (constat C.5) fournissant sa valeur, avec deux booléens `isInitial`/`isDefault` distinguant valeur liée vs valeur initiale, valeur concrète vs valeur par défaut.

**Candidat Modelio** : `Attribute.DefaultValue` (probable, à vérifier précisément) porte une valeur par défaut **en texte simple**, sans distinction `isInitial`/`isDefault`, et sans passer par une `Expression` structurée. **⚠️ Équivalent partiel très dégradé** — cumule à la fois le problème du constat 1 (pas de `Membership` réifiée) et du constat C.5 (pas d'`Expression` structurée) : c'est un concept qui hérite des deux limitations à la fois.

### C.8 `Metaclass` (8.3.4.12.2)

`Metaclass extends Structure` — type utilisé pour typer les `MetadataFeature` (déjà traité en détail, Partie 2.3 de la spec principale, avec `MetaclassReference` de Modelio identifié comme candidat pour le mécanisme voisin). Rien de nouveau à ajouter ici au-delà de ce qui est déjà documenté.

### C.9 `Package` (8.3.4.13.4) / `LibraryPackage` (8.3.4.13.3) / `ElementFilterMembership` (8.3.4.13.2)

| Classe KerML | Rôle | Candidat Modelio | Verdict |
|---|---|---|---|
| `Package` | `Namespace` de regroupement, avec `filterCondition` (Expression booléenne filtrant les imports) | `Package` (`statik`) | ⚠️ Le rôle de regroupement correspond (✅), mais `filterCondition` dépend de la famille `Expression` (constat C.5, ❌) et repose sur `ElementFilterMembership` (constat 1, ❌) — équivalent partiel dégradé sur ces deux aspects |
| `LibraryPackage` | `Package` marqué comme conteneur de bibliothèque de modèle (`isStandard`) | Pas de métaclasse dédiée identifiée — à vérifier s'il existe un concept Modelio de « bibliothèque de modèle » distinct d'un `Package` ordinaire (hors périmètre de cette étude, à creuser séparément) | ❓ non tranché, à investiguer |
| `ElementFilterMembership` | `Membership` portant une condition de filtrage | *Aucun* | ❌ cf. constat 1 |

---

## Synthèse récapitulative

| Classe KerML | Couche | Candidat Modelio | Verdict |
|---|---|---|---|
| `Element` | Root | `ModelElement` | ✅ |
| `Relationship` | Root | *(aucune racine commune)* | ⚠️ |
| `Namespace` | Root | `NameSpace` | ⚠️ |
| `Membership` | Root | *(composition native)* | ❌ |
| `OwningMembership` | Root | *(composition native)* | ❌ |
| `Import` | Root | `PackageImport`/`ElementImport` | ⚠️ |
| `MembershipImport` | Root | `ElementImport` | ⚠️ |
| `NamespaceImport` | Root | `PackageImport` | ✅ |
| `VisibilityKind` | Root | `VisibilityMode` | ⚠️ |
| `Type` | Core | *(aucun — sépare Classifier/Feature)* | ❌ |
| `Classifier` | Core | `Classifier` | ✅ |
| `Feature` | Core | `Feature` | ✅ |
| `FeatureDirectionKind` | Core | `PassingMode` | ⚠️ |
| `FeatureMembership` | Core | *(composition native)* | ❌ |
| `Specialization` | Core | `Generalization` | ✅ |
| `Conjugation` | Core | *(aucun)* | ❌ |
| `Disjoining` | Core | *(aucun)* | ❌ |
| `Unioning` | Core | *(aucun)* | ❌ |
| `Intersecting` | Core | *(aucun)* | ❌ |
| `Differencing` | Core | *(aucun)* | ❌ |
| `Multiplicity`/`MultiplicityRange` | Core/Kernel | entiers plats sur Attribute/AssociationEnd/Parameter | ⚠️ |
| `DataType` | Kernel | `DataType` | ✅ |
| `Class` | Kernel | `Class` | 🔀 |
| `Structure` | Kernel | `Class` (rôle partagé) | ⚠️ |
| `AssociationStructure` | Kernel | `ClassAssociation` (piste à valider) | ⚠️ |
| `BindingConnector` | Kernel | *(aucun)* | ❌ |
| `Succession` | Kernel | *(aucun — ne pas confondre GeneralOrdering)* | ❌ |
| `Behavior` | Kernel | `Behavior` (commonBehaviors) | ✅ (avec prudence, cf. §C.4) |
| `Step` | Kernel | *(aucun)* | ❌ |
| `ParameterMembership` | Kernel | *(composition native)*, rôle sur `Parameter` | ❌/⚠️ |
| `Function`/`Predicate`/`Invariant`/`BooleanExpression`/`Expression` + littéraux/opérateurs | Kernel | *(aucun)* | ❌ |
| `Interaction` (Kernel) | Kernel | 🔀 ne pas confondre avec `interactionModel::Interaction` | 🔀 |
| `Flow`/`FlowEnd`/`PayloadFeature`/`SuccessionFlow` | Kernel | partiellement `DataFlow`/`InformationFlow`, sinon aucun | ❌ |
| `FeatureValue` | Kernel | `Attribute.DefaultValue` (dégradé) | ⚠️ |
| `Metaclass` | Kernel | `MetaclassReference` (déjà documenté) | ⚠️ |
| `Package` | Kernel | `Package` | ⚠️ (dépend d'Expression/Membership) |
| `LibraryPackage` | Kernel | non identifié | ❓ |
| `ElementFilterMembership` | Kernel | *(aucun)* | ❌ |

**Bilan chiffré de cette passe** (hors classes déjà traitées dans la spec principale) : sur 38 classes étudiées, **7 équivalents nets** (✅), **13 équivalents partiels** (⚠️), **16 sans équivalent** (❌), **2 faux amis** (🔀), **1 non tranché** (❓).

---

## Prochaines étapes suggérées

1. **Trancher le principe du constat 1** (réification ou non de `Membership`/`Import`) — c'est la décision la plus structurante de toute cette étude, elle conditionne l'implémentation de la résolution de noms pour tout le langage textuel.
2. **Décider du niveau de fidélité pour la famille `Expression`** (constat C.5 / option 1, 2 ou 3) — deuxième décision la plus lourde, impacte directement les cas #10/#18/#19 déjà actés dans la spec principale.
3. **Valider ou invalider la piste `ClassAssociation`** pour `AssociationStructure` (§C.2) par un test de génération réelle, comme cela a été fait pour le patron d'association composée.
4. **Investiguer `LibraryPackage`** (seul point non tranché faute de candidat identifié) et les classes non couvertes par cette première passe (notamment le détail complet des opérations/littéraux d'`Expression`, volontairement groupés ici plutôt que traités un par un vu le constat global d'absence d'équivalent).
5. Comme pour la spec principale, chaque décision prise ici devrait être documentée avec sa justification (cf. Partie 5.3 de la spec principale — practice déjà établie).
