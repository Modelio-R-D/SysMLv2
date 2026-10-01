## Plan: SemGen Spec-Faithful Generation

Modify SemGen to generate Cédric’s six-layer target architecture so `reference/design` can remain structurally close to the normative metamodel without duplicate storage. Target Modelio 7 multi-parent runtime APIs. Redefinitions/subsets remain note-based; derived accessors are generated as throwing stubs with calculation guidance and are preserved after a developer applies `SemGenManual` to the generated operation.

**Steps**

### Phase 1 — Freeze the target contract and characterization baseline
1. Convert Cédric’s E01–E06 examples from `C:\Users\jcadavid\OneDrive - LA POSTE GROUPE\SysML2-Plan\sysml2-archi-brainstorm\subjects\architecture-brainstorm\work\generation-examples\01-inheritance-and-redefinition.md` into generator fixtures covering simple inheritance, diamond inheritance, safe redefinition, unrelated homonyms, multiple independent redefinitions, and derived/subset properties.
2. Add characterization assertions for all six generated layers: API interface, `XxxImpl`, `XxxData` interface, `XxxDataImpl`, `XxxSmClass`, and `SmAttribute`/`SmDependency` descriptors. Capture the current failures before changing generation.
3. Add a Modelio 7 compile fixture proving the target runtime exposes multi-parent SmClass support (`parentClasses`/`initParents`) and make the build fail clearly if an older single-parent runtime is selected.

### Phase 2 — Represent the new generated class set
4. Extend `MClassSet` to hold separate `dataInterface` and `dataImplClass` elements instead of one concrete `dataClass`; retain temporary compatibility accessors only while migrating generators.
5. Update `MClassSetManager.generateClassSet()` and `collectClassSet()` to create/find `XxxData` as a Java interface and `XxxDataImpl` as a concrete class, alongside API, Impl, and SmClass artifacts. Update generated package/import lookup code and root class-set initialization accordingly.
6. Update `BaseGenerator` generation ordering so all class-set artifacts are registered before inheritance/property resolution, then generate Data interfaces before flattened DataImpl classes and descriptors.

### Phase 3 — Build one effective-property/canonical-slot model
7. Refactor `PropertyRedefinition` into a reusable resolution result that separates: requested declaration, contextual view in the concrete metaclass, canonical stored property, and computation-only property. Keep parsing `Redefines (per normative XMI): ...` from `Description` notes; parse `Subsets (per normative XMI): ...` as calculation guidance, never as a storage alias.
8. Resolve redefinition chains before type/multiplicity validation; reject cycles, ambiguous references, and merges of independent slots. Preserve distinct storage for unrelated same-name properties by including the declaring property identity in the slot key.
9. Add an effective-property planner per metaclass that returns inherited Data-interface views, flattened canonical fields for DataImpl, shared descriptors, and derived/no-storage members. Use this single planner from every downstream generator to prevent six layers from drifting.

### Phase 4 — Generate `XxxData` interfaces and flattened `XxxDataImpl`
10. Split `DataGenerator` responsibilities (or introduce focused generators): generate `XxxData` interfaces that extend every direct parent Data interface, expressing the multiple-inheritance contract without fields.
11. Generate `XxxDataImpl extends SmObjectData` with the complete flattened set of effective canonical fields. Emit exactly one field for a diamond-inherited origin and one field for each unrelated homonym; emit no field for derived properties or aliases that share a canonical slot.
12. Generate constructors/accessors/imports against `XxxDataImpl`, and update Impl/data casts so generated `XxxImpl` accesses canonical DataImpl slots while exposing the declarations inherited through Data interfaces.
13. Preserve `SemGenManual` members during cleanup and regeneration. Add a regression test that a generated derived operation, once marked Manual and hand-edited, is neither deleted nor duplicated on the next run.

### Phase 5 — Generate Modelio 7 multi-parent SmClass and shared descriptors
14. Update `MetaclassGenerator.doGenerateInheritance()` and constructor generation to initialize all direct parents through the Modelio 7 multi-parent API (`initParents(...)`/`parentClasses`), preserving declared order and detecting duplicate/cyclic parents.
15. Update `MetaclassSmAttributeGenerator` and `MetaclassSmDependencyGenerator` to create descriptors only for canonical stored declarations. Redefining metaclasses reference the shared descriptor rather than declaring a second one.
16. Update `MetaclassLoadGenerator`, object-factory generation, and metamodel-fragment loading so factories instantiate `XxxDataImpl`, descriptor load code addresses flattened fields, and every contextual declaration resolves to its canonical descriptor.
17. Retain and adapt association mutation guards and `RedefinedAssociationList` behavior so type/cardinality/opposite constraints are evaluated in the concrete metaclass context before mutating the canonical slot.

### Phase 6 — Generate derived/subset API stubs without storage
18. Ensure derived attributes and association ends are excluded consistently from DataImpl fields, SmAttribute/SmDependency descriptors, load code, and persistence registration.
19. Keep navigable derived members in the generated API. Generate getter implementations that throw `UnsupportedOperationException` and include both Javadoc and source comments containing the normative prose plus `Subsets`/`Redefines` calculation guidance. Do not parse OCL or auto-implement even obvious filters in this iteration.
20. Do not generate setters for derived properties. For subset/redefinition stubs, name the base/canonical property and any filter/type condition extracted from notes; malformed references fail preflight rather than producing misleading code.
21. Verify the Manual workflow on generated operations: user applies `SemGenManual`, replaces the throwing body, and subsequent regeneration preserves that implementation.

### Phase 7 — Preserve KerML independence
22. Introduce a one-way metadata resolver for SysML properties that calculate from KerML declarations. Allow SysML generated code/comments to reference KerML canonical properties, but never create an inverse KerML API member, descriptor, or Data-interface dependency on SysML.
23. Add architecture validation that rejects generated KerML→SysML dependencies and reports the offending source property. Keep the intentionally omitted cross-metamodel inverse associations as the explicit exception to spec-identical `reference/design`.

### Phase 8 — Integration and acceptance
24. Expand unit tests in `PropertyRedefinitionTest`, `AssociationEndGenerationTest`, `AssociationAliasBehaviorTest`, `RedefinedAssociationListTest`, `AssociationGuardHelperTest`, `RuntimeSupportGeneratorTest`, and BaseGenerator preflight tests for all E01–E06 cases and the derived/manual workflow.
25. Run the semgenerator unit suite, then the full SemGen aggregator `clean verify` against Modelio 7 dependencies. Treat any duplicate field/descriptor, unresolved parent, stale old `XxxData` concrete class, or KerML→SysML dependency as a failure.
26. Generate bounded KerML and SysML fixtures and compile all generated Java. Assert layer shape, one canonical slot, shared descriptors, Data-interface diamonds, flattened DataImpl fields, throwing derived stubs, and Manual-body survival.
27. Only after fixture acceptance, run full generation against the live `reference/design`; compare generated artifact counts and dependency graph with the baseline, then execute mutation/undo and representative API smoke tests. Do not deploy/install SemGen until this gate passes.

**Relevant files**
- `C:\Users\jcadavid\OneDrive - LA POSTE GROUPE\SysML2-Plan\sysml2-archi-brainstorm\subjects\architecture-brainstorm\work\generation-examples\01-inheritance-and-redefinition.md` — Cédric’s E01–E06 expected generated shapes.
- `C:\Users\jcadavid\OneDrive - LA POSTE GROUPE\SysML2-Plan\sysml2-archi-brainstorm\subjects\architecture-brainstorm\work\04_TARGET_ARCHITECTURE.md` — declaration/view/storage-or-computation model.
- `H:\modelio\work\eclipse\modules\SemGen\src\main\subprojects\semgenerator\src\main\java\com\modeliosoft\tools\semgen\core\MClassSet.java` — add Data interface/DataImpl artifacts.
- `H:\modelio\work\eclipse\modules\SemGen\src\main\subprojects\semgenerator\src\main\java\com\modeliosoft\tools\semgen\core\MClassSetManager.java` — create and collect all six generated layers.
- `H:\modelio\work\eclipse\modules\SemGen\src\main\subprojects\semgenerator\src\main\java\com\modeliosoft\tools\semgen\base\BaseGenerator.java` — preflight and generation order.
- `H:\modelio\work\eclipse\modules\SemGen\src\main\subprojects\semgenerator\src\main\java\com\modeliosoft\tools\semgen\utils\PropertyRedefinition.java` — canonical/contextual property planning and note parsing.
- `H:\modelio\work\eclipse\modules\SemGen\src\main\subprojects\semgenerator\src\main\java\com\modeliosoft\tools\semgen\base\datagen\DataGenerator.java` — split Data interface and flattened DataImpl generation.
- `H:\modelio\work\eclipse\modules\SemGen\src\main\subprojects\semgenerator\src\main\java\com\modeliosoft\tools\semgen\base\impgen\ImplGenerator.java` — generated implementation inheritance/accessors and Manual preservation.
- `H:\modelio\work\eclipse\modules\SemGen\src\main\subprojects\semgenerator\src\main\java\com\modeliosoft\tools\semgen\base\impgen\DependencyHelper.java` — derived association stubs and guidance comments.
- `H:\modelio\work\eclipse\modules\SemGen\src\main\subprojects\semgenerator\src\main\java\com\modeliosoft\tools\semgen\base\impgen\AttributeHelper.java` — derived attribute stubs and canonical DataImpl access.
- `H:\modelio\work\eclipse\modules\SemGen\src\main\subprojects\semgenerator\src\main\java\com\modeliosoft\tools\semgen\base\mcgen\MetaclassGenerator.java` — Modelio 7 multi-parent initialization.
- `H:\modelio\work\eclipse\modules\SemGen\src\main\subprojects\semgenerator\src\main\java\com\modeliosoft\tools\semgen\base\mcgen\MetaclassSmAttributeGenerator.java` — shared attribute descriptors.
- `H:\modelio\work\eclipse\modules\SemGen\src\main\subprojects\semgenerator\src\main\java\com\modeliosoft\tools\semgen\base\mcgen\MetaclassSmDependencyGenerator.java` — shared dependency descriptors.
- `H:\modelio\work\eclipse\modules\SemGen\src\main\subprojects\semgenerator\src\main\java\com\modeliosoft\tools\semgen\base\mcgen\MetaclassLoadGenerator.java` — descriptor/DataImpl load wiring.
- `H:\modelio\work\eclipse\modules\SemGen\src\main\subprojects\semgenerator\src\main\java\com\modeliosoft\tools\semgen\standard\StandardAnnotationScheme.java` — `SemGenManual` detection.

**Verification**
1. Unit tests prove E01–E06 across all six generated layers and malformed-note/cycle/homonym failure modes.
2. Modelio 7 compile fixture proves multi-parent SmClass calls and DataImpl/object-factory compatibility.
3. Generated KerML/SysML fixtures compile with zero duplicate fields/descriptors and zero missing canonical getters.
4. Derived properties have API getters and throwing bodies with actionable comments, but no fields/descriptors/setters.
5. Marking a generated operation `SemGenManual` preserves a handwritten body over a second generation.
6. Dependency analysis reports zero KerML→SysML generated dependencies.
7. Full aggregator verification and representative runtime mutation/undo tests pass before deployment.

**Decisions**
- Target Modelio 7 APIs; no compatibility requirement for current Modelio 6/SaaS runtime.
- Implement Cédric’s `XxxData` interface + flattened `XxxDataImpl` architecture as mandatory scope.
- Keep `Redefines` and `Subsets` metadata in Description notes; add no new stereotypes for them.
- `Redefines` controls canonical storage; `Subsets` supplies calculation guidance only.
- Generate throwing stubs for every derived getter, even when a filter looks mechanically obvious.
- Developers apply `SemGenManual` to the generated operation before replacing its body.
- Cross SysML→KerML calculation references are one-way; no inverse KerML member is generated.
- Do not parse OCL in this iteration.
- Do not deploy/install SemGen until all unit, generated-source, dependency, and runtime gates pass.
