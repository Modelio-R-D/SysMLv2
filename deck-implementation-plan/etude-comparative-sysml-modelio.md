# Étude comparative SysML v2 ↔ Infrastructure Modelio — passage par domaine

Troisième volet de la série d'études de correspondance, après [spec-complete-greffe-sysml-modelio.md](./spec-complete-greffe-sysml-modelio.md) (points de greffe, 3 chevauchements, 34 cas d'héritage multiple) et [etude-comparative-kerml-modelio.md](./etude-comparative-kerml-modelio.md) (couches Root/Core/Kernel de KerML). Ce document couvre la couche **SysML v2** proprement dite (spec `sysml.txt`), dans l'ordre de priorité validé : Requirements → Ports/Interfaces/Items/Connections/Flows → Allocation → Cases → Views → (reste Actions/States, non traité ici, cf. section finale).

**Légende** (identique aux études précédentes) : ✅ équivalent net · ⚠️ équivalent partiel · ❌ aucun équivalent · 🔀 faux ami · ❓ non tranché (information manquante).

---

## Priorité 1 — Requirements

### Constat préalable : le module Requirement de Modelio n'est pas dans le périmètre déjà documenté

Recherche infructueuse de tout package « Requirement » dans la documentation Modelio scrapée jusqu'ici (`Modelio-API-Markdown-CHUB`, couvrant `activityModel`, `commonBehaviors`, `informationFlow`, `infrastructure*`, `interactionModel`, `stateMachineModel`, `statik`, `usecaseModel`) — **aucun résultat**.

En revanche, la documentation interne du projet (`ModelioSkill/skills/modelio/references/api-patterns.md`, `ModelioSkill/skills/modelio/scripts/sync_structure.py`) confirme l'existence d'un **module Modelio optionnel** nommé **« Analyst »**, avec au moins les métaclasses suivantes (déduites de l'usage, pas d'une doc API complète) : `AnalystProject`, `RequirementContainer`, `Requirement`, `Goal`, `GoalContainer`, `KPI`, `KPIContainer`, `Dictionary`. Le code le traite explicitement comme **optionnel** (vérifié via `moduleService.getPeerModule('AnalystModule')` avant utilisation) — il n'est donc pas garanti d'être installé sur toute instance Modelio. Les outils MCP déjà disponibles dans cet environnement (`mcp_modelio-saas_create_modelio_requirement`, `create_enhanced_modelio_requirement`, `list_modelio_requirements`) confirment son usage réel, avec un schéma d'exigence **plat** : `name`, `text`, `category` (`Fonctionnel`/`Non-Fonctionnel`/`Technique`/`Performance`/`Sécurité`/`Interface`), `priority` (`Haute`/`Moyenne`/`Basse`/`Critique`), `status`, `parentId` (hiérarchie simple), `comments`.

**Action à faire avant de trancher** : documenter précisément le module « Analyst » (attributs réels, cardinalités, relations) — non couvert par le scraping actuel, alors que c'est la pièce la plus déterminante pour juger de la qualité du mapping `Requirements` SysML v2 ↔ Modelio. Tant que cette documentation n'existe pas, les verdicts ci-dessous sont **préliminaires**.

### Comparaison préliminaire

| Concept SysML v2 | Attributs/cardinalités clés | Candidat Modelio (déduit) | Verdict préliminaire |
|---|---|---|---|
| `RequirementDefinition`/`RequirementUsage` | `reqId : String [0..1]`, `/text : String [0..*]` (**plusieurs blocs de texte**), `assumedConstraint`/`requiredConstraint` (sous-contraintes typées via `RequirementConstraintMembership`) | `Analyst.Requirement` | ⚠️ La partie « texte + hiérarchie + priorité » colle probablement bien (`Requirement.text`, `RequirementContainer` pour la hiérarchie). Mais **`text` est `[0..*]` côté SysML** (plusieurs blocs) — à vérifier si `Analyst.Requirement` n'a qu'un seul champ texte (ce qui semble être le cas d'après le schéma MCP : un seul `text` par exigence). Les sous-contraintes `assumed`/`required` n'ont probablement **aucun équivalent** dans le modèle plat Analyst. |
| `SubjectMembership`/`ActorMembership`/`StakeholderMembership` | Encore des spécialisations de `ParameterMembership` → `Membership` (cf. **constat transversal 1 de l'étude KerML**, qui se confirme donc aussi au niveau SysML) — identifient des `PartUsage` typés comme sujet/acteur/partie prenante d'une exigence | *Aucun* | ❌ Le modèle plat Analyst n'a vraisemblablement pas de notion de « sujet »/« acteur »/« partie prenante » paramétrés et typés — juste du texte libre et une catégorie. Cohérent avec l'écart déjà documenté sur `Membership`. |
| `ConcernDefinition`/`ConcernUsage` | `RequirementDefinition` spécialisée, avec des « stakeholders » identifiés | *Aucun équivalent direct* — peut-être approximable par une `category` particulière | ❌/⚠️ à confirmer une fois le module Analyst documenté |
| `SatisfyRequirementUsage` | Déjà traité (cas #32 de la spec principale, `extends RequirementUsage implements AssertConstraintUsage`) | — | *(cf. spec principale, non repris ici)* |

**Question à trancher** : documenter le module Analyst en priorité (même méthode que le scraping déjà fait pour `infrastructure`/`statik`) avant de valider un mapping définitif — c'est actuellement le plus gros point aveugle de toute cette série d'études.

---

## Priorité 1 — Ports, Interfaces, Items, Connections, Flows

### `PortDefinition`/`PortUsage` + `PortConjugation`/`ConjugatedPortDefinition`

`PortDefinition extends Structure, OccurrenceDefinition` — point de connexion externe d'un système. Chaque `PortDefinition` (sauf si elle-même conjuguée) doit posséder **exactement un** `ConjugatedPortDefinition` généré automatiquement (nom = `~<nomOriginal>`), qui inverse les directions `in`/`out` de toutes les Features héritées, via une relation `PortConjugation` (spécialisation de `Conjugation`, cf. constat transversal 2 de l'étude KerML).

**Candidat Modelio** : `Port` (`statik`) — ✅ **équivalent net** pour la structure de base (point de connexion typé). En revanche, le mécanisme de **conjugaison automatique** (génération systématique d'un port miroir avec flux inversés) est ❌ **sans aucun équivalent** — cohérent avec l'absence totale de `Conjugation` déjà constatée au niveau KerML. C'est ici un cas concret et à fort impact utilisateur de cette lacune abstraite : sans mécanisme de conjugaison, il faudra soit générer manuellement le port conjugué comme un second `Port` Modelio distinct (perte de la relation formelle de conjugaison), soit développer l'équivalent de `Conjugation` spécifiquement pour ce cas d'usage avant de l'étendre au reste.

### `ItemDefinition`/`ItemUsage`

Déjà couvert au cas #24 de la spec principale (`ItemDefinition implements Structure`). Rien de nouveau à ajouter.

### `ConnectionDefinition`/`ConnectionUsage`

`ConnectionDefinition extends PartDefinition, AssociationStructure` — déjà couvert aux cas #15/#16 de la spec principale, avec la piste `ClassAssociation` de Modelio identifiée dans l'étude KerML (§C.2) comme candidat plus direct que le patron générique d'association composée pour `AssociationStructure`. Cette piste **profite directement** à `ConnectionDefinition`/`ConnectionUsage`, qui en héritent.

### `InterfaceDefinition`/`InterfaceUsage` — 🔀 faux ami détecté

`InterfaceDefinition extends ConnectionDefinition` : « une `ConnectionDefinition` dont toutes les extrémités sont des `PortUsage` » — c'est-à-dire une **connexion typée entre ports**, pas un contrat d'opérations.

**Candidat Modelio évident par le nom** : `Interface` (`statik`) — *« An Interface specifies a contract »*, le concept UML classique d'ensemble d'opérations qu'une classe peut implémenter (`InterfaceRealization`).

**🔀 Faux ami net** : ce sont deux concepts **sans aucun rapport sémantique** malgré le nom identique. Le `InterfaceUsage` SysML v2 est structurellement une **connexion** (héritage de `ConnectionUsage`/`ConnectorAsUsage`), pas un contrat comportemental. **Ne pas mapper `InterfaceDefinition`/`InterfaceUsage` sur `Interface` de Modelio** — ce serait une erreur de conception qui importerait par erreur toute la sémantique UML des contrats d'interface (opérations, réalisation…) sur un concept qui n'en a pas besoin. Le candidat correct est plutôt le même que celui identifié pour `ConnectionDefinition`/`ConnectionUsage` juste au-dessus (`Connector`/`ClassAssociation`), avec une contrainte supplémentaire (extrémités = des `Port`).

**Question à trancher** : confirmer explicitement dans la spec (à ajouter en Partie 2 de la spec principale ou en annexe) que `InterfaceDefinition`/`InterfaceUsage` ne doivent **pas** être rattachés à `infrastructure`/`statik::Interface` malgré la tentation du nom.

### `AllocationDefinition`/`AllocationUsage`

`AllocationDefinition extends ConnectionDefinition` — exprime qu'une responsabilité de réalisation est allouée d'une source vers une cible (mapping inter-structures/hiérarchies).

**Candidats Modelio à confronter à la famille `Dependency`** (déjà étudiée en Partie 2.2 de la spec principale) :
- `Abstraction` (*« relie deux Elements représentant le même concept à des niveaux d'abstraction différents »*) — proche dans l'esprit mais pas identique : une allocation SysML v2 n'est pas nécessairement un changement de niveau d'abstraction, plutôt un transfert de responsabilité.
- `ElementRealization` (spécification ↔ implémentation) — même remarque, proche mais pas exact.

**Verdict** : ⚠️ équivalent partiel — le rôle général (relation dirigée source→cible avec une sémantique métier propre) est couvert par la famille `Dependency`, mais aucune des spécialisations existantes de Modelio (`Abstraction`, `Usage`, `ElementRealization`…) ne porte exactement la sémantique d'« allocation de responsabilité » — cohérent avec le principe déjà établi (Partie 0 de la spec principale) d'accepter un rattachement approximatif au concept métier le plus proche plutôt que d'en camper un nouveau, mais à valider explicitement comme choix assumé plutôt que comme un oubli.

### `FlowDefinition`/`FlowUsage`/`SuccessionFlowUsage`

Déjà couverts en détail par les cas #4, #7, #21, #22, #34 de la spec principale et par le §C.6 de l'étude KerML (rappel du faux ami `Interaction`). Rien de nouveau à ajouter ici.

---

## Priorité 2 — Cases (`Case`/`AnalysisCase`/`VerificationCase`/`UseCase`)

### `CaseDefinition`/`CaseUsage`

`CaseDefinition extends CalculationDefinition` — processus avec sujet, acteurs (`actorParameter : PartUsage [0..*]`), et un objectif (`objectiveRequirement : RequirementUsage [0..1]`, via `ObjectiveMembership`, encore une spécialisation de `FeatureMembership`/`Membership`).

**Candidat Modelio** : *aucun* — pas de concept « Case » (processus d'investigation formalisé avec sujet/acteurs/objectif) dans le métamodèle central Modelio. **❌ Aucun équivalent** pour le concept racine lui-même.

### `UseCaseDefinition`/`UseCaseUsage`/`IncludeUseCaseUsage` — la meilleure nouvelle de cette passe

`UseCaseDefinition extends CaseDefinition` — mais avec une différence de taille : Modelio a un concept **natif et mature** de cas d'utilisation.

**Candidat Modelio** : `UseCase` (`usecaseModel`) — ✅ **équivalent net** pour le concept central, avec en prime `UseCaseDependency` déjà identifié dans Modelio (*« this specific metaclass has been created for the definition of these links »*) qui couvre vraisemblablement les relations `include`/`extend` classiques d'UML, analogues à `IncludeUseCaseUsage`.

**Nuance à documenter** : `UseCaseUsage` hérite de tout l'appareillage `CaseDefinition` (sujet/acteurs/objectif paramétrés typés) que le `UseCase` natif de Modelio n'a pas — Modelio relie ses `UseCase` à des `Actor` par de simples associations, sans la richesse de paramétrage typé de SysML v2. **⚠️ Équivalent partiel** : bon socle, mais la sur-couche de paramétrage (`actorParameter`, `subjectParameter`, `objectiveRequirement`) devra être ajoutée par-dessus, avec les mêmes limitations déjà identifiées pour `Membership`/`ParameterMembership`.

### `AnalysisCaseDefinition`/`AnalysisCaseUsage`

`AnalysisCaseDefinition extends CaseDefinition`, avec un `resultExpression : Expression [0..1]` — dépend directement de la famille `Expression` déjà signalée comme **totalement absente** de Modelio (étude KerML, §C.5). **❌ Aucun équivalent**, et pas seulement par absence de concept « Case » : même si on résolvait le concept `Case`, `resultExpression` resterait bloqué par le manque plus large et déjà connu du langage d'expression.

### `VerificationCaseDefinition`/`VerificationCaseUsage`

`VerificationCaseDefinition extends CaseDefinition`, avec `verifiedRequirement : RequirementUsage [0..*]` (via `RequirementVerificationMembership`, encore une spécialisation de `Membership`). **❌ Aucun équivalent** pour le concept lui-même. Point à recouper avec l'action « documenter le module Analyst » (Priorité 1, Requirements) : si Modelio a une notion native de lien de vérification entre un test/une vérification et une exigence, ce serait le seul point de départ envisageable — actuellement inconnu, même limitation que pour `Requirements`.

---

## Priorité 3 — Views, Viewpoints, Rendering, Expose

**Suspicion confirmée** (formulée dans la question précédente, vérifiée ici) : Modelio n'a **aucun mécanisme** comparable à celui de SysML v2 pour les vues paramétrées. Le concept SysML v2 est riche : `ViewDefinition`/`ViewUsage` (vue filtrée du contenu du modèle, avec `viewCondition : Expression [0..*]` et un `viewRendering`), `ViewpointDefinition`/`ViewpointUsage` (préoccupations de parties prenantes à satisfaire par une vue, spécialisation de `RequirementDefinition`/`Usage`), `RenderingDefinition`/`RenderingUsage` (comment matérialiser une vue), et `Expose`/`MembershipExpose`/`NamespaceExpose` (import spécial qui peuple une vue, encore une famille de spécialisations d'`Import`/`Membership`).

**Les diagrammes de Modelio sont un mécanisme fondamentalement différent** : ce sont des artefacts de présentation graphique (positions, styles) sur des éléments existants, pas des éléments de modèle paramétrés avec des conditions de filtrage évaluables et une notion de point de vue de partie prenante. **❌ Aucun équivalent, pour l'intégralité de la famille** — à traiter comme un développement entièrement nouveau si ces concepts sont dans le périmètre de la v1, avec la même dépendance de fond déjà signalée deux fois (`Expression` pour `viewCondition`, `Membership`/`Import` pour `Expose`).

**Récurrence à noter** : c'est la **troisième fois** dans cette série d'études (après `Membership`/`FeatureMembership` au niveau KerML, et `SubjectMembership`/`ActorMembership`/`ObjectiveMembership` au niveau Requirements/Cases) que le mécanisme `Expose`/`Import`/`Membership` réapparaît comme bloquant. Ce n'est plus une curiosité isolée : **la décision sur la réification ou non de `Membership`** (constat transversal 1 de l'étude KerML) conditionne directement la faisabilité d'au moins quatre familles de concepts SysML v2 distinctes (Annotations, Requirements, Cases, Views). C'est un argument supplémentaire pour trancher ce point en priorité absolue.

---

## Ce qui n'est pas couvert par cette passe (Priorité 4, non traité)

Par souci de proportionner l'effort au reste du projet, cette étude ne couvre pas en détail les classes de la couche **Actions** (8.3.17) et **States** (8.3.18) au-delà de ce qui est déjà couvert par les 34 cas de la spec principale (`ActionDefinition`, `ActionUsage`, `PerformActionUsage`, `ExhibitStateUsage`…). Restent non examinées : `AcceptActionUsage`, `AssignmentActionUsage`, `SendActionUsage`, `TerminateActionUsage`, `TransitionUsage`, `TransitionFeatureMembership`, `GuardExpressionMembership`, `TriggerActionMembership`, ainsi que les classes concrètes de la famille `Expression` déjà groupées (§C.5 de l'étude KerML). **Recommandation** : traiter cette dernière tranche dans un futur incrément une fois les décisions structurantes déjà identifiées (Membership, Expression, Analyst) tranchées — ces classes en dépendent presque toutes directement, donc les étudier avant serait prématuré.

---

## Synthèse de cette passe

| Concept SysML v2 | Candidat Modelio | Verdict |
|---|---|---|
| `RequirementDefinition`/`RequirementUsage` | `Analyst.Requirement` (module optionnel, non documenté) | ⚠️/❓ |
| `SubjectMembership`/`ActorMembership`/`StakeholderMembership` | *(aucun — Membership)* | ❌ |
| `ConcernDefinition`/`ConcernUsage` | *(aucun identifié)* | ❌/❓ |
| `PortDefinition`/`PortUsage` | `Port` (statik) | ✅ (structure de base) |
| `PortConjugation`/`ConjugatedPortDefinition` | *(aucun — Conjugation)* | ❌ |
| `ConnectionDefinition`/`ConnectionUsage` | `ClassAssociation`/`Connector` (piste à valider) | ⚠️ |
| `InterfaceDefinition`/`InterfaceUsage` | 🔀 **PAS** `statik::Interface` — plutôt `Connector`/`ClassAssociation` | 🔀 |
| `AllocationDefinition`/`AllocationUsage` | `Abstraction`/`Dependency` (approximatif) | ⚠️ |
| `CaseDefinition`/`CaseUsage` | *(aucun)* | ❌ |
| `UseCaseDefinition`/`UseCaseUsage`/`IncludeUseCaseUsage` | `UseCase`/`UseCaseDependency` (usecaseModel) | ⚠️ (bon socle, sur-couche à ajouter) |
| `AnalysisCaseDefinition`/`AnalysisCaseUsage` | *(aucun — dépend d'Expression)* | ❌ |
| `VerificationCaseDefinition`/`VerificationCaseUsage` | *(aucun, à recouper avec Analyst)* | ❌ |
| `ViewDefinition`/`ViewpointDefinition`/`RenderingDefinition`/`Expose` (famille complète) | *(aucun)* | ❌ |

**Bilan chiffré** : sur 20 concepts étudiés dans cette passe, **2 équivalents nets** (dont un partiel sur la sur-couche), **5 équivalents partiels**, **1 faux ami**, **10 sans équivalent**, **2 non tranchés faute de documentation du module Analyst**.

## Actions prioritaires issues de cette étude

1. **Documenter le module Modelio « Analyst »** (`Requirement`, `RequirementContainer`, `Goal`, `KPI`…) — c'est la seule vraie inconnue factuelle de cette passe, et elle conditionne le verdict sur `Requirements` ET potentiellement `VerificationCase`.
2. **Ajouter explicitement à la spec principale la mise en garde sur `InterfaceDefinition`/`InterfaceUsage`** — risque concret de mauvais rattachement à `statik::Interface` par réflexe de nommage.
3. **Confirmer par un cas concret** que `PortConjugation` doit être traité comme une occurrence supplémentaire du problème déjà identifié pour `Conjugation` en général (pas un cas isolé à résoudre séparément).
4. Conserver la priorisation « trancher `Membership`/`Import` en premier » de l'étude KerML — cette étude SysML confirme, avec quatre familles de concepts distinctes touchées, que c'est bien le goulot d'étranglement le plus large de tout le projet.
