# SemGen redefinitions: work in progress

Date: 2026-09-24, last updated 2026-09-26

## Status

## End state after phase 33 (2026-09-27, SemGen 4.0.21)

Both metamodels generate and the output compiles:

```
705 sources -> 1242 class files, 0 errors
```

**Every property accessor in the generated API is backed by real storage.** The
`UnsupportedOperationException`s that remain are all legitimate:

| | Count | Why |
|---|---|---|
| Operation bodies | 151 | KerML/SysML operations (`path`, `evaluate`, `modelLevelEvaluable`, `effectiveName`, ...) whose behaviour must be hand-written. This is what the `SemGenManual` stereotype is for -- an implementation written against one survives regeneration. |
| `createData` / `createImpl` | 16 | On abstract metaclasses (`KerMLModelElement`, `Relationship`, `Import`, `InstantiationExpression`). Correct: an abstract metaclass cannot be instantiated. |
| Derived properties | **0** | Removed from generation by phase 33. |

### Two generator fixes were needed to get here, and one was based on a misreading

**4.0.20 -- `declaredParents` tolerates ends not owned by a class.** Phase 33
aborted the KerML preflight with `Redefinition owner is not a class: import`.
The cause is pre-existing and worth knowing: **192 of the 556 ends in
reference/design are nested under their opposite end, not under a class** --
Modelio's association factory nests the second end under the first, giving
chains like `Namespace.import < NamespaceImport.importedNamespace <
NamespaceImport(Class)`. `resolve()` walks ancestry from `getCompositionOwner()`
and needs a class to start from. Hiding the derived ends changed which ends get
walked and surfaced it. Such an end now simply has no resolvable declared
parent, which is honest -- its accessors are not being generated anyway.

**4.0.21 -- a stored end may not adopt a derived end as its storage.** Sound in
principle: a derived end has no descriptor, so there is no slot to share.
**But it fixed nothing here.** It was made on the strength of a misreading -- 167
`UnsupportedOperationException`s in the output were taken for stubs of this kind
without checking what they said. They are the 151 + 16 above. No property in
reference/design adopts a derived storage, so the rule is unexercised. It is kept
because it is correct, and the test that pins it records that it was not
evidence-driven.

## Phase 33: derived association ends removed from generation (2026-09-26)

**291 derived navigable association ends in `reference/design` were made
non-navigable.** 262 navigable ends remain -- the stored backbone. Nothing the
generated API exposes is derived any more, so nothing in it throws.

### Why they had to go

A derived property has no storage, so no descriptor is generated for it -- yet
accessors referencing one were. Until 4.0.17 that was 99 compile errors; from
4.0.17 it was 291 methods throwing `UnsupportedOperationException`. Neither is a
foundation anyone can build on.

**Computing the values is not possible from this model.** The normative XMI
states those derivations in OCL and prose. The model's own `Subsets` notes,
which a derived *union* could in principle be assembled from, are demonstrably
incomplete: `Element.owner` records **0** subsetters where the XMI declares
**2**, and the same holds for `ownedElement`, `owningNamespace` and
`owningMembership`. A plan built on those notes would have silently converted
four textbook derived unions into stored fields -- two sources of truth for
where an element lives.

### Why non-navigable rather than deleted

Deleting was the original idea and it is unsafe: the two ends of an association
are nested in one element, so deleting one takes its opposite with it. Deleting
`Definition.ownedPort` would destroy `PortUsage.portOwningDefinition`, which is
**stored** and load-bearing.

Non-navigable produces the identical generated result -- every SemGen generator
gates on `ModelUtils.isNavigable`, which reads exactly this flag -- while leaving
the association and its stored side intact. It is also reversible with one flag.

### Why all 291 rather than a smarter subset

85 of them look like plain inverse roles that could instead be **un-marked**
derived, giving real bidirectional navigation rather than none. That split
depends on the `Subsets` notes -- the same source just proven unreliable. A
uniform change needs no classification and cannot be wrong in that way.
Restoring an individual accessor later is one flag, once someone decides which
conveniences justify a real derivation rule.

### What survives, and what is lost

**Survives:** the Relationship/Membership/Specialization backbone KerML is built
on -- `ownedRelationship`, `owningRelationship`, `Relationship.source`,
`Relationship.target`, `OwningMembership.ownedMemberElement`. Every removed
accessor was a *view* over it, so no structure becomes unrepresentable: a
`ConjugatedPortDefinition`'s containment still travels
`ownedRelationship` -> `OwningMembership` -> `ownedMemberElement`, and typing
still travels `ownedRelationship` -> `FeatureTyping` -> `target`.

Every one of the 291 has a navigable opposite, so no association is left with a
dangling single end.

**Lost:** convenience navigation. Reaching a Definition's ports now means an
explicit hop through the relationship rather than `definition.getOwnedPort()`.
That is a real cost, deliberately accepted -- those accessors did not work
before this change either.

## THE GENERATED METAMODEL COMPILES (2026-09-26, 21:34)

```
705 source files -> 1186 class files, 0 errors
```

Both projects, `sysml.metamodel.api` (180) and `sysml.metamodel.impl` (525),
compiled against Modelio 7.0.0 with SemGen 4.0.19 / semgenerator 1.4.16.

### What it took, and the mistake that made it take four rounds

Six generators referenced `get<Name>Dep()` without checking whether a descriptor
actually exists for that end:

| Site | Errors it caused |
|---|---|
| `AssociationGuardHelper` guard dispatch | 96 |
| `MetaclassSmDependencyGenerator` symmetric wiring | 42 |
| `MetaclassSmDependencyGenerator` redefinition aliases | 29 |
| `CompositionAccessorHelper` composition owners | 28 |
| `DependencyHelper` Impl getters and setters | ~57 |
| `AttributeHelper` multi-valued cast | 1 |

Each surfaced only once the previous was fixed, because a class that fails to
resolve is abandoned before its remaining references are checked. The error
total sat at exactly 100 for three consecutive rounds while the *composition*
changed completely underneath.

**These were patched with six slightly different conditions, and that was the
mistake.** One of them regressed: skipping a redefinition alias whose storage is
derived left the Impl accessors still referencing it. They were all asking one
question, and it now lives in one place:

```java
PropertyRedefinition.hasStorageDescriptor(end)
    // false when the end is derived, or when its storage is derived
```

Every site calls it. The regression is impossible by construction, because the
alias skip and the accessor skip are now the same test. The lesson is to look for
the shared predicate after the second site, not the sixth.

### What compiling does not establish

The code has never been **run**. No instance created, no property read, no
Modelio session has loaded the metamodel. Three known gaps are deliberately
baked in:

- **291 derived properties throw** `UnsupportedOperationException`. That is
  containment, not derived-property support -- 240 of them have no derivation
  rule anywhere in the model. Blocker 2 stands.
- **8 members remain duplicated** -- the thing Cedric raised. Implementing
  derived support would remove them *and* keep their names.
- **`aliasIds`** compiles but is untested at runtime; it is the only `0..*`
  attribute, so multi-valued attribute support is essentially unexercised, and
  `DataGenerator` still initialises such a field to `""` rather than a list.

## Earlier the same day

**On 2026-09-26 both metamodels generated end to end for the first time:
`GENERATION SUCCESSFUL` for KerML (81 metaclasses) and then for SysML (97, with
KerML consumed as a dependency), with SemGen 4.0.12 / semgenerator 1.4.09.**

Descriptors, meta and link experts, model shield factories, metamodel fragments
and visitors were all emitted and committed. The redefinition preflight passed
on both and reported 14 degraded properties for KerML and 10 for SysML -- exactly
the split the dry run predicted, item for item.

What this does **not** yet establish: the generated Java has not been written to
disk, compiled or executed, so the output is unverified beyond having been
produced. Open items: 40 attributes generated with no initial value (classified
below -- 24 are a straight fix from the XMI, 5 are derived, 11 need a decision),
eleven classes whose containment SemGen could not decide, and four
flattened-inheritance collisions.

Current candidate: `H:\modelio\work\eclipse\modules\SemGen\target\SemGen_4.0.12.jmdac`,
94 tests passing. The user owns module deployment.

A dry run mirroring the deployed preflight reports **0 hard defects** and **8
duplicated members** out of 626 properties across 171 classes (24 not reaching
their full canonical storage, of which 16 share a partial slot).

Read in this order:

1. **Cleaning up the notes themselves** -- 15 `Redefines` notes did not match the
   XMI; six were being silently accepted and would have shipped.
2. **Splitting the preflight's two failure modes** -- a metadata defect still
   aborts; a redefinition that cannot share storage no longer does.
3. **The first real run, and what it found** -- the 4.0.08 run aborted, and the
   three problems that surfaced from it (unhelpful messages; finding defects one
   run at a time; a fallback that could itself cause an abort).
4. **The second run** -- 4.0.09 cleared the preflight and reached Java code
   generation, where a latent `JavaImport` tag-type bug in `JavaUtils` surfaced.
5. **The third run** -- 4.0.10 carried the fix but could not run it, because the
   generator was rebuilt without `clean`. Also: the log now names its own build.
6. **The fourth run** -- 4.0.11 generated 24 metaclasses, then one remaining
   strict call site contradicted the preflight's own degradation.
7. **The successful run** -- 4.0.12 completed KerML end to end, and what is left
   to decide.

The redefinition preflight is no longer a blocker, and KerML now generates. That
is not the same as the redefines problem being solved: 8 members are still
duplicated, derived-property computation is unstarted, and the generated code
has not been compiled or exercised. See "Remaining blockers" at the end.

Earlier candidates (4.0.06 / 1.4.03, 4.0.07 / 1.4.04, 4.0.08 / 1.4.05) are
superseded.

## Implemented

- Explicit resolution of `Redefines (per normative XMI): Class.property` in
  ModelerModule description notes. No inference from equal names alone.
- Resolution through renamed properties and ancestor chains, with ambiguity,
  malformed metadata, independent-storage merges and cycles rejected.
- Canonical attribute storage shared by Data fields, SmAttribute descriptors,
  registration and implementation getter/setter bodies.
- Secondary-parent flattening reuses primary inherited storage where present;
  otherwise canonical storage is flattened once.
- Public property names and normative documentation remain unchanged.
- Different attribute types, multiplicities or explicit default values are
  rejected rather than silently losing constraints.
- Full and selected generation validate before their generation transactions.
- Same-shape, non-derived association redefinitions reuse canonical storage
   and descriptor identity. Renamed SmClass getters delegate to the canonical
   getter; Data fields and dependency registration are not duplicated.
- Changed association targets, multiplicities, aggregation, opposite identity,
   or derived semantics still require adapters and are rejected by preflight.

## Integration components

- `RuntimeSupportSource.load(className)` loads either runtime source from
   `META-INF/semgen/runtime-sources/`, packaged as unfiltered Maven resources.
   It uses the JDK AST to extract imports, the class header and members, and
   now also (2026-09-24, later same day) exposes the extends clause,
   implements clauses and type parameters as separate structured accessors
   (`extendsClause()`, `implementsClauses()`, `typeParameters()`), needed to
   drive model-level class creation rather than only `render()`'s standalone
   text. `render(packageName)` still reconstructs a standalone source in a
   destination package and rejects references to the SemGen package.
   Extraction requires JDK 21 compiler facilities (`JavaCompiler`,
   `JavacTask`, `jdk.compiler`); availability inside the actual Modelio
   runtime remains to be checked.
- `AssociationGuardCode.members(guardQualifiedName, validationBody)` emits
   the four kernel mutation overrides and `validateAssociation` with fully
   qualified Java types. `interfaceName(guardQualifiedName)` supplies the
   constraint interface. The caller must supply effective constraints: the
   helper does not compute them or implicitly call parent validation.
- **New (2026-09-24, later same day): `RuntimeSupportGenerator`**
   (`base/impgen/RuntimeSupportGenerator.java`) emits `AssociationMutationGuard`
   and `RedefinedAssociationList` as model-level `JavaClass` elements under
   `<outputNamespace>.impl.runtime`, using the same
   `putNoteContent(JavaClass.MdaTypes.JAVAMEMBERS_NOTETYPE_ELT, ...)` pattern
   `EnumerationHelper` already uses for enum bodies, adapted to a class
   (extends/implements via `JavaClass.setJavaExtends`/`setJavaImplements`,
   type parameters via `Class.getTemplate()`, imports via
   `JavaUtils.addJavaImport`). It caches per instance: a given support class
   is only ever created once per `RuntimeSupportGenerator`/generation run —
   this is the "one shared support class, not a copy per metaclass" mechanism
   Copilot's last message described, now built and passing its own tests
   (4 new tests; `RuntimeSupportSourceTest` gained 1 more for the new
   accessors). Full suite: **56 tests run, 0 failures, 0 errors** — verified
   independently against the surefire output, not just the report that
   produced it (`mvn -o clean test` re-run from this session).

**What this still is not.** `RuntimeSupportGenerator` is called from nowhere
except its own test — confirmed by grep. It is **not** wired into
`ImplGenerator`, `DependencyHelper`, or `CompositionAccessorHelper`, and
`PropertyRedefinition`'s preflight still rejects every narrowing/constrained
association redefinition exactly as before. Deciding *which* metaclasses need
the guard, and computing the effective per-property `Constraint` (target type
+ bounds) that `AssociationGuardCode`'s validation body would need, is
unsolved design work, not plumbing — it was deliberately left alone rather
than guessed at. Two more things are flagged unverified because no working
precedent exists elsewhere in this codebase to copy, only checked via
`javap` against the compiled API: creating a **class-level** (not
operation-level) generic `TemplateParameter` via `Class.getTemplate().add(...)`,
and `JavaClass.setJavaExtends`/`setJavaImplements` (real, documented methods,
but never previously called by any generator here). Neither has been
exercised against a real SemGen→JavaDesigner generation run — a live KerML or
SysML run is the only way to confirm `RedefinedAssociationList<Value>` comes
out with its generic parameter and `implements EList<Value>` intact, and
`RuntimeSupportGeneratorTest` could not exercise the class end-to-end either:
`GenerationContext`'s constructor makes 15+ mandatory lookups against a real
MDAKit reference metamodel that this module has no lightweight fake for, so
the tests instead cover the qualified-name/caching logic through a narrower
static seam plus the (now fully tested) `RuntimeSupportSource` accessors.

Also still required, unchanged from before this addition: preserve
user-owned JavaMembers notes across regeneration, generate constraints and
interception points at the correct inheritance level, and validate exported
Java without a runtime dependency on SemGen. Emitting wrappers at every
inheritance level could intercept the same call again through `super`; this
placement must be tested against the reentrancy policy. "One shared runtime
identity across KerML and SysML" is answered only partially: each run now
gets exactly one copy per support class instead of one per metaclass, but
KerML's and SysML's copies are still two physically distinct classes (one
per output namespace) — a true single cross-component identity would need a
namespace decision that only makes sense against the live model, left alone
here for the same reason.

## Evidence

Subsequent focused validation:

| Test slice | Evidence | Limit |
| --- | --- | --- |
| AssociationAliasBehaviorTest | 8 tests passed at 18:59, including the new callback regression | Kernel operations with in-memory persistence, not live transactions |
| AssociationGuardCodeTest | 6 tests passed at 19:18 (surefire report on disk, superseding the earlier sub-agent BUILD SUCCESS report) | Emitted methods compiled on ClassImpl; kernel mutations not executed by this slice |
| RuntimeSupportSourceTest | 3 tests passed at 19:18 (surefire report on disk) | Extraction/render round-trip only; not wired into generation |

Copilot's last message before that session ended referred to these two
components ("les neuf tests des deux composants passent"):
`AssociationGuardCodeTest` (6) + `RuntimeSupportSourceTest` (3) = 9. The
user, not Copilot, fired the rebuild that produced the surefire reports
confirming this count — both green under
`semgenerator/target/surefire-reports/`, both timestamped 19:18, superseding
the "Surefire run interrupted" line from the previous update of this
document. The count in Copilot's claim matches what that rebuild shows on
disk, but the rebuild itself was a separate, user-initiated action, not
something produced or verified by Copilot's own session.

**Archive is stale relative to this result.** `target/SemGen_4.0.06.jmdac`
is timestamped 19:13 — five minutes before the 19:18 test run that produced
the 9 passing tests above. The candidate archive does not reflect the state
these tests exercised and must not be presented as a tested deliverable.
Rebuild the archive after any further change before treating it as current.

**Full module suite, later the same day: 56 tests run, 0 failures, 0
errors** (`mvn -o clean test` against
`semgenerator/pom.xml`), independently re-run and confirmed against the raw
Surefire console output, not taken from a sub-agent's summary alone. This
includes the pre-existing 41 (see below), the earlier 8+6+3=17 evidence rows
above are subsumed by this same total where they overlap (do not add them
separately — `AssociationAliasBehaviorTest` (8) + `AssociationGuardCodeTest`
(6) + `RuntimeSupportSourceTest`, now 4 not 3 after a new accessor test
(4) + `RuntimeSupportGeneratorTest`, new (4) + `PropertyRedefinitionTest`
(21) + `RedefinedAssociationListTest` (9) + `AssociationEndGenerationTest`
(1) + `BaseGeneratorValidationTest` (3) = 56). This is a real full-module
total, not a partial slice — but it is still only `mvn test` on one Maven
module, not the aggregator/reactor build, and the `.jmdac` archive is now
stale against this too (unchanged since 19:13, well before this run).

These results do not establish a new full **reactor** total (the aggregator
spans more than this one module). No archive rebuild has been established
after these additions.

Last completed full generator-suite run before these additions (2026-09-24,
18:51): **41 tests passed**,
including seven real-kernel association behavior tests, nine constrained-list
tests, 21 redefinition-planning tests and four existing validation tests.
This is a source/test build, not a new candidate archive or live deployment.

Earlier focused run (2026-09-24, 18:39): **11 tests passed**, comprising nine
`RedefinedAssociationListTest` cases and two `AssociationAliasBehaviorTest`
cases. The second kernel-backed test exercises the constrained view and
explicitly reproduces an inverse-write bypass. These counts describe
different test runs and must not be added together as a new full-suite result.

The earlier clean reactor build passed 20 tests. After the association-alias
implementation, the generator test suite passed 26 tests on 2026-09-24 at 18:31,
including 21 property-resolution/storage tests and one compiled-alias behavior
test. The candidate archive has not been rebuilt since these changes.

The behavior test compiles the emitted descriptor-alias body and exercises
real SmObjectImpl and SmList operations on a ClassImpl-based node. It verifies
reads and writes through both descriptor names, replacement, inverse-side
removal/addition, and clearing. Only persistence is replaced by an in-memory
fixture; inverse propagation is performed by the Modelio kernel.

The former compilation blocker was an incomplete test subclass of abstract
SmObjectImpl, not a demonstrated failure of alias generation. Using concrete
ClassImpl resolved it. These checks do not establish transaction/undo behavior,
end-to-end Modelio regeneration, or compilation of the full generated modules.

The earlier audit of Java generated with active SemGen 4.0.05 found:

| Check | Observed result |
| --- | --- |
| Same-class duplicate declarations | None found by the AST audit |
| Inherited Data field collisions | 14 |
| API inherited redeclarations | 69; not all are defects |
| XMI redefinition pairs with storage declared on both sides | 47 of 132 examined pairs |
| Calls to absent dependency getters | 858 calls targeting 397 methods |
| Structural nodes | 28 |

The storage findings overlap and must not be summed. Legitimate API overrides
are not proof of duplicate storage; renamed properties also require following
the actual XMI redefinition links. Evidence: [AST audit](generated-member-audit.txt)
and [XMI storage comparison](generated-redefinition-audit.csv). These are the
4.0.05 baseline, not validation of output from the current candidate.

Build command:

```powershell
mvn -o -f H:\modelio\work\eclipse\modules\SemGen\aggregator\pom.xml clean verify
```

## Constrained view prototype

`RedefinedAssociationList` is an ordinary Java adapter implementing EMF `EList`,
not a Java language feature. It delegates to an existing collection, including
Modelio `SmList`, rather than allocating independent property storage.

- Type and upper-bound validation on reads; invalid values are reported, not
   silently filtered out of the redefined property.
- Type and cardinality checks for mutations through the view, including
   iterator/sublist writes and prevalidation of whole-view bulk operations.
- Single-valued getter/setter projection over the same collection.
- Sorting and permutations delegate to list moves, preserving existing links.
- Incomplete initial lower bounds are allowed during construction; this is
   NOT a complete model-validity or transaction-commit validator.

The adapter exists in the generator source tree but is NOT yet emitted or wired
into generated KerML/SysML accessors. Its runtime packaging also remains to be
resolved; generated modules must not accidentally depend on the SemGen tool.

**Known bypass, reproduced by a test:** an unwrapped inherited collection or
inverse access can still insert an incompatible value. The view detects the
bad state on the next read but does not prevent that external write. Supporting
these redefinitions requires validation of all mutation paths before changes.
The generation preflight therefore remains restrictive.

Prevalidating view constraints does not make a sequence of kernel mutations
transactionally atomic. Persistence failures, undo and rollback need separate
validation in a real modeling session.

## Pre-mutation controller prototype

`AssociationMutationGuard` now simulates the final values of every affected
object/dependency before delegating to the unchanged kernel. Constraints apply
to both ends and to an old owner displaced by inverse reassignment. Planned
internal removals are distinguished from independent writes, allowing valid
replacement of a required link without accepting a final lower-bound breach.
The kernel also attempts no-op removals before multiple appends; these planned
calls are explicitly accounted for.

Kernel-backed tests now confirm rejection BEFORE mutation for incompatible
inverse writes, upper-bound overflow, removal of a required value, indexed
writes and reassignment that would detach a required old owner. Rejected cases
leave the existing links unchanged. Valid replacements and inverse propagation
still work. Per-thread internal permits are cleaned up when the kernel throws.

An independent source review identified a reentrancy bypass: during the
kernel's erase-before-append sequence, an `afterEraseDepVal` callback could
insert another value into the temporarily empty collection. Both local
validations passed, but the outer append then exceeded the final cardinality.
The regression reproduced the issue before the fix. The guard now rejects
unplanned nested mutations with `IllegalStateException`; only explicitly
planned internal kernel calls are allowed. Callbacks must defer new writes.
The passing test catches that rejection inside the callback and lets the outer
operation finish. An uncaught callback exception can interrupt an operation
after an internal removal: atomic rollback is NOT provided by this guard.

This controller is NOT yet wired into generated implementations. The tests use
overrides of `appendDepVal` (both overloads), `eraseDepVal`, and `setDepVal` on
ClassImpl-based nodes implementing its constraint interface. A plain unguarded
node still demonstrates the bypass; no claim is made for direct IMetaOf writes,
transaction rollback/undo, general callback compatibility or concurrent mutation.
Guarded per-call validation also does not make a sequence of calls atomic.

Remaining integration work: generate those interception points and effective
constraints on all relevant metaclasses, share the same runtime support across
KerML and SysML, and emit support into the generated implementation rather than
introducing a runtime dependency on the SemGen module. Source extraction and
override emission helpers now exist (see Integration components). JavaDesigner
exposes a JavaMembers note facility, but model emission/export has not yet been verified.
The existing strict generation preflight is therefore intentionally retained.

## Why inverse writes matter

Consider `Order.customer` and its inverse `Customer.orders`. Setting a customer
must update that customer's orders; adding an order from the inverse side must
update the order's customer as well. If `ProfessionalOrder.customer` narrows
the type to `ProfessionalCustomer`, validating only its setter is insufficient:
an ordinary customer's `orders.add(professionalOrder)` must also be rejected
before any previous link is removed. This example illustrates the remaining
constraint-enforcement work; it is not a claim of implemented support.

## Fresh candidate archive built (2026-09-26): `SemGen_4.0.07.jmdac`

Every prior candidate archive mentioned in this document was stale relative
to the code it was supposed to represent (`4.0.06` predates all of the
`PropertyRedefinition`/`RuntimeSupportGenerator`/`AssociationGuardHelper`
work below). A fresh one was built today: version bumped
`4.0.06` → `4.0.07` (module) and `1.4.03` → `1.4.04` (the `semgenerator`
library jar it embeds) across all three places that need to agree
(`SemGen/pom.xml`, `semgenerator/pom.xml`, `module.xml`), then a full
aggregator build (`mvn -o -f aggregator/pom.xml clean verify`, not just
the `semgenerator` submodule test run used throughout this document) —
**BUILD SUCCESS, 83 tests, 0 failures**, producing
`target/SemGen_4.0.07.jmdac` (26/09/2026 00:10:03). This is the first
archive in this whole effort that actually contains the narrowing fix, the
opposite-check fix, and the guard wiring — not just source and test
results. Still not installed or run against a live project; that remains
the user's step.

## Live-model evidence (2026-09-25): the mismatch rate is the norm, not an edge case

A scoped ScriptServer check against the real `reference/design` package (556
association ends, bounded `getCompositionChildren()` walk from
`findByPath("reference/design")`, not a workspace-wide `findByClass()` scan)
resolved 90 `Redefines (per normative XMI): ...` association-end pairs
against their declared parent. **79 of the 90 differ** in target type,
multiplicity, aggregation, or derived-ness; only 11 are already
same-shape and safely shareable under the current preflight. The dominant
pattern is the KerML relationship backbone itself narrowing
`Relationship.source`/`Relationship.target` (`KerMLModelElement [0..*]`) down
to something concrete and `1..1` — `Specialization.general/specific`,
`Membership.memberElement`, `Subsetting.subsettedFeature`,
`FeatureTyping.typedFeature`, `Association.sourceType/targetType`,
`Connector.sourceFeature/targetFeature`, and more. This is not a rare
corner case to special-case; it is how KerML expresses relationships at
all. 7 association pairs and 2 attribute pairs did not resolve by walking
the direct generalization chain — at least 2 of those
(`RequirementDefinition.reqId`/`RequirementUsage.reqId` →
`Element.declaredShortName`) reference the pre-rename class name `Element`
rather than `KerMLModelElement`, i.e. stale note text, not a resolver bug.
Comparison was one-hop (redefiner vs. its directly declared parent, not the
fully-resolved canonical root `PropertyRedefinition.canonical()` computes);
this can only undercount real divergence for multi-hop chains, not
overcount it.

## Proposed solution (2026-09-25, not yet implemented)

The 79 mismatches are not 79 separate problems. Most are **valid
narrowings**: `Specialization.general : Type [1..1]` redefining
`Relationship.target : KerMLModelElement [0..*]` is a legitimate
specialization (assuming `Type` is a subtype of `KerMLModelElement`, which
needs confirming case-by-case, not assumed), not a modeling error. The
current preflight cannot tell a safe narrowing from a genuine
incompatibility (like the 2 stale `Element`/`KerMLModelElement` references
above, which are real errors) — it rejects both identically. That
distinction is the actual missing piece, and it reframes the problem from
"79 blocked cases needing individual adapters" to "one generation rule that
needs to accept narrowing and keep rejecting incompatibility."

Proposed stages:

1. **Redefine the preflight rule in `PropertyRedefinition`.** A redefinition
   is safe when the redefiner's target is the canonical target or a subtype
   of it, its multiplicity range is a subset of the canonical's, and
   derived-ness only ever goes stored→derived, never the reverse. Anything
   failing this is still rejected exactly as today.
2. **Storage sharing is unchanged** — `PropertyRedefinition`'s existing
   canonical-storage resolution stays as-is.
3. **Wire the already-built, already-tested runtime enforcement.** For each
   class with an accepted narrowing, generate `implements ConstrainedObject`
   plus the four guard overrides (`AssociationGuardCode`, written and unit
   tested, currently called from nowhere) with a `validateAssociation` body
   computed directly from that class's own declared target/multiplicity — no
   new modeling work, it is mechanically derivable from what is already in
   `reference/design`.
4. **Stack guards through inheritance rather than replacing them**: a
   subclass's guard calls `super.validateAssociation(...)` first, then
   applies its own tighter check. Safe because redefinition is monotonic
   (each level only narrows further) — and this is exactly the risk already
   flagged under "Integration components" ("emitting wrappers at every
   inheritance level could intercept the same call again through `super`").
5. **Derived narrowings (`isDerived True vs False` in the mismatch list,
   e.g. `Membership.membershipOwningNamespace`) are a separate, smaller
   case**: no guard, no separate storage, a computed getter narrowing the
   canonical value's type.
6. **Validate on a disposable probe metamodel first**, per this project's
   own established discipline (cheap local checks before an 11–22 min full
   run) — not straight to a live KerML/SysML generation.

Step 1 changes generation behavior for the entire redefinition surface and
is a design decision for Antonin/Cédric, not something to implement
unilaterally. Steps 1 and 3 are the two genuinely new pieces; steps 2, 4
(the delegation pattern), and the runtime classes themselves already exist.

## Step 1 implemented and tested (2026-09-25, later the same day)

`PropertyRedefinition.associationStorage()` now accepts a target-subtype
narrowing (walked via `GeneralClass.getParent()`, same BFS-with-visited-set
pattern already used by `resolve()`/`storedEnds()`, not a new traversal
idiom) and a multiplicity-subset narrowing, and only accepts a derived-ness
narrowing one direction (redefiner derived over stored canonical; not the
reverse). Aggregation, opposite, and navigability are still checked exactly
as strictly as before — deliberately not relaxed in this pass, matching the
scope decision above. A genuine incompatibility (e.g. an unrelated target
type, or aggregation/opposite mismatch alongside an otherwise-valid
narrowing) still throws `IllegalArgumentException` exactly as before.

A new method, `PropertyRedefinition.narrowing(AssociationEnd property)`,
returns `Optional<Narrowing>` — empty for an exact-shape match, or a
`record Narrowing(GeneralClass targetType, int minimum, int maximum)` for a
real narrowing (`maximum == -1` meaning unbounded, matching
`AssociationMutationGuard.Constraint`'s own sentinel convention exactly, so
a caller can construct one directly from the other). It delegates to
`associationStorage()` rather than duplicating validation.

**Verified independently, not taken on report:** file diffs read directly;
full suite re-run from a clean `mvn -o clean test` gave **62 tests run, 0
failures, 0 errors** (`PropertyRedefinitionTest`: 27 — the pre-existing 21
plus 6 new). A targeted grep for `.narrowing(`/`Narrowing(` across
`src/main` matches only inside `PropertyRedefinition.java` itself — nothing
wired into `ImplGenerator`, `DependencyHelper`, `CompositionAccessorHelper`,
`AssociationGuardCode`, or `RuntimeSupportGenerator`.

**One existing test's assertion changed, deliberately.**
`renamedAssociationRejectsNarrowingWithoutMutationGuards` asserted the old,
overly strict behavior (a target-subtype narrowing must throw) — exactly
the case this change is meant to accept. It was renamed to
`renamedAssociationAcceptsTargetSubtypeNarrowing` and now asserts
acceptance, exercising a real 2-hop generalization chain
(`NarrowTarget :> MiddleTarget :> Target`) to prove the BFS walk isn't just
checking direct parents, with a comment at the change explaining why. No
other existing test's outcome changed.

**Step 3 is now also implemented and tested — see the dedicated section
below.** `attributeStorage()` (the attribute/derived-property side) is
still untouched — out of scope, per stage 5. Nothing here has been checked
against whether `Type` really is a subtype of `KerMLModelElement` (or any
of the other 79 real cases) in the live `reference/design` model — that
still needs a live-model check before this rule is trusted against the
real spec, exactly as flagged when the proposal was written.

## Step 3 implemented and tested (2026-09-25, later the same day)

### What this actually does, explained plainly

Picture one real example from the live model: `Specialization.general`
redefines `Relationship.target`. `Relationship.target` can point at
anything (`KerMLModelElement`, the most general type, `0..*` — any number
of them). `Specialization.general` narrows that down: it must point at
exactly one `Type`.

Before step 1, SemGen refused to generate this at all — it saw the shape
was different and gave up. After step 1, it accepts the narrowing and
shares one physical storage slot between `Relationship.target` and
`Specialization.general` (this part already existed before today). But
sharing storage alone does not stop someone from writing a bad value
into that slot through the *wrong* accessor — nothing yet stops code
using the broad `Relationship.target` getter/setter from putting something
in there that is not a `Type`, even though a `Specialization` object is
only supposed to ever hold a `Type` there. Step 3 is what closes that gap.

Concretely, for every generated class that has this kind of narrowing
(`Specialization`, in the example), SemGen now also generates four small
"guard" methods. Every one of these methods is called automatically by
Modelio's own internals whenever *anything*, anywhere, tries to add,
remove, or replace a value in that shared storage slot — not just when
the narrow setter is called, but also when code reaches in from the
*other end* of the association (the inverse-write case described earlier
in this document: `client.commandes.add(commandeProfessionnelle)`). Each
guard method's job is simple: before letting the change through, check
"does this new value satisfy the narrower rule this particular class
declared?" (right type, right count). If not, it refuses the change and
raises an error immediately, before anything is actually written — the
model never ends up in a bad state.

That check itself is delegated to a small shared helper class
(`AssociationMutationGuard`, already built and tested before today) so the
generated code stays tiny: each guard method is really just "ask the
helper to check this, then do what the helper says." One copy of that
helper class is generated once per model (KerML gets one, SysML gets one),
not once per narrowed class — the exact "shared, not copied" requirement
from Copilot's original note that started this whole thread.

**What happens when a class narrows something its parent class already
narrowed?** Example: imagine class `B` narrows a property, and its
subclass `C` narrows that same property even further. `C` does not get a
brand-new, separate set of guard methods — it only gets one small addition:
its own extra check, which runs *after* first calling `B`'s check (`C`
literally says "run my parent's check first, then also check my own,
tighter rule"). This is safe specifically because a redefinition can only
ever make a rule *stricter*, never looser — so stacking checks this way can
never accidentally let through something a parent class would have
blocked.

### What was verified, and how

- Read the actual generated code by hand (not just the report describing
  it) — the logic matches what's described above.
- Independently re-ran the full test suite from a clean build:
  **80 tests run, 0 failures, 0 errors** (`AssociationGuardHelperTest`: 14
  new; `AssociationGuardCodeTest`: 10, 4 new; everything else unchanged
  from before this step).
- Confirmed by reading the actual wiring in `ImplGenerator.java` that this
  new logic is genuinely called during generation (`doGenerateAssociationGuards(cs)`,
  right after the existing association-accessor generation step) — this is
  the one piece of work in this whole effort that is deliberately wired
  in, unlike the two earlier pieces which were built and tested but left
  unconnected on purpose.

### One deliberate deviation, explained

The original plan said the generated check should compare against the
*canonical* (most general) property's own accessor. The actual code
instead compares against *this class's own* accessor for its own
(possibly renamed) property name. This was a considered change, not a
shortcut: every existing accessor-generation code in this project already
works this way (a class's own name and its own property's own name,
never reaching into a parent class's naming by hand), and re-checking the
metaclass-generation code confirmed that, either way, that accessor
always ends up pointing at the exact same underlying shared storage — so
the comparison is correct either way, and this way matches how every
other part of the generator already does it instead of introducing a new,
one-off pattern.

### What is still not proven

Everything above was built and tested using made-up example classes, the
same way step 1 was — none of it has touched the real `reference/design`
model or produced a real generation run yet. In particular, the parts that
actually change the live Modelio model (creating the four guard methods
as real generated methods, declaring `implements ConstrainedObject` on a
real class) cannot be unit-tested at all without a live Modelio session —
exactly the same limitation already noted for `RuntimeSupportGenerator`
earlier in this document. The only way to know this behaves correctly
against the real 79 cases is to actually run a real generation against
`reference/design` — still not done, still the user's call, exactly as
agreed before this work started.

## The live-model check that changed everything (2026-09-25, later still)

Everything up to this point had been checked against made-up example
classes only. This section is the first time any of today's work was
actually checked against the real `reference/design` model — and it found
a real bug, then a real gap in the model's own data, both explained below
in plain terms. This whole section is written to be readable without
already knowing the code.

### First, a bug in the fix itself

Step 1's new rule ("accept a narrowing, reject an incompatibility") also
requires an unrelated thing to stay identical between the redefiner and
the canonical property: the **opposite end** — the property on the
*other* side of the same association. That part of the rule was left
untouched on purpose, "still strict, don't relax it in this pass."

Running the fixed rule against the real 90 redefinition pairs found in
`reference/design` produced a shock: **every single one was still
rejected.** Not because the rule was too strict in a reasonable way — it
turned out the opposite-end check could basically never succeed for a
real case, for a reason that had nothing to do with genuine
incompatibility.

Here is why, with the real example: `Specialization.general` redefines
`Relationship.target`. Its actual opposite (the property on the other end
of the same association) is `Type.generalization` — **not**
`Specialization.specific`, which was the wrong assumption this document
made earlier. Meanwhile `Relationship.target`'s own opposite is
`KerMLModelElement.targetRelationship`. Comparing `Type.generalization`
directly against `KerMLModelElement.targetRelationship` will obviously
never match — they are two completely different, unrelated-looking
properties. But that comparison was asking the wrong question. The right
question is: **does `Type.generalization` redefine the same thing
`KerMLModelElement.targetRelationship` is?** Once the code was changed to
resolve *both* sides through the existing "what does this actually
redefine" logic before comparing them (instead of comparing the two raw
properties directly), the comparison becomes correct.

This was a genuine mistake in the original design, not a coding error —
built and unit-tested exactly as specified, but the specification itself
was wrong in a way that only running it against real data revealed. Fixed
the same day, independently re-verified (**83 tests, 0 failures**).

### Second, a gap in the model's own documentation

Fixing the code above was not enough by itself. Running the corrected
rule against the real model *still* only accepted 1 of 90 cases. The
reason this time was not a code bug at all: almost none of the "opposite"
properties (like `Type.generalization` above) had ever been individually
marked with their own `Redefines (per normative XMI): ...` note. Only the
"forward" direction (`Specialization.general` → `Relationship.target`)
had been documented; nobody had gone back and also written down the
matching fact on the other side of the same association
(`Type.generalization` → `KerMLModelElement.targetRelationship`).

This is not a guess to fill in — it follows directly and mechanically from
what is already known: if `general` redefines `target`, and
`generalization` is `general`'s real, structural opposite in the same
association, then `generalization` **must** redefine `target`'s own
opposite. There is no other consistent possibility. A script
(`reference-design-transform/phase15_backfill_opposite_redefines_notes.jy`)
was written to add exactly this missing, mechanically-derived note
wherever it was absent, touching nothing else — no existing note was
changed or removed, only new ones added where genuinely missing.

Run against the live model: **88 notes added**, all in one transaction,
committed and saved.

### Then a second problem, found immediately by re-checking, and fixed the same way

Re-running the check after adding those 88 notes surfaced one more issue,
caught before it could cause harm: 17 of the 88 added notes turned out to
reference a class that was not actually an ancestor at all — it was the
**same class** the property already belongs to (for example,
`KerMLModelElement.membership` was given a note saying it redefines
`KerMLModelElement.targetRelationship`, but both properties already live
directly on `KerMLModelElement` — there is no inheritance step between
them to redefine across). The real code that reads these notes only ever
looks at **ancestor** classes, never the same class, so it would not
just fail quietly on these 17 — it would throw a hard error the moment
any real generation touched them, and because the class involved
(`KerMLModelElement`) is the root every other class inherits from, that
error would have blocked the *entire* KerML/SysML generation, not just a
handful of classes.

This was caught immediately by rechecking rather than assuming success,
and fixed the same way it was introduced: a second script
(`phase16_revert_same_class_redefines_notes.jy`) removed **exactly those
17 lines**, restoring each property's note to whatever it said before
(nothing, for most of them; for two of them — which already had unrelated
existing text — restoring exactly that prior text, not deleting it).
Nothing else from the first 88 was touched.

### The real, final result

After the fix and the cleanup: **124 of the 161 redefinition pairs that
now carry a note are correctly accepted** as legal narrowings — a huge
jump from the 1 that worked before any of this. The 37 still rejected
split cleanly into three understood, distinct groups, none of them
surprises:

- **13 cases** where the redefining property is computed on the fly
  ("derived") but what it redefines is stored as a real value, the wrong
  way around — this is the separate, already-known, not-yet-attempted
  piece (stage 5 of the proposal, and the same "derived properties" gap
  flagged since the very first version of this document).
- **9 cases** where the redefinition genuinely changes composition
  ownership (e.g. from a plain reference to a true "owns this" relationship)
  — a real, deliberate design difference in the norm, and exactly the kind
  of case this pass of work always said it would leave alone rather than
  guess at.
- **15 cases** where the note that *would* complete the picture cannot be
  written at all, for the same reason 17 notes just had to be reverted:
  the true opposite lives on the same class, not an ancestor, so the
  "redefines a named ancestor's property" note format cannot express it.
  This is a real, separate limitation of the note convention itself — not
  something this pass of work introduced, and not something automatically
  fixable the same way; it needs a person to decide how (or whether) to
  extend the convention for this shape of case.

### The last small piece: 7 of the original 9 "unresolved" pairs, fixed too

Right at the start of this whole live-model investigation, 9 redefinition
pairs failed to resolve at all (7 association pairs, 2 attribute pairs).
It would have been easy to assume all 9 were the same kind of problem —
that assumption was made out loud at one point and was wrong, corrected
before acting on it. Checked individually instead:

- **3 really were the simple case**: they referenced the pre-rename class
  name `Element` instead of `KerMLModelElement` (confirmed by checking that
  the specific attribute/association end they pointed at genuinely exists
  on `KerMLModelElement` today).
- **4 referenced a property name that had been renamed on the very class
  the note already correctly pointed at** — e.g. `AttributeUsage`'s
  redefinable property is now called `attributeOwningDefinition`, not
  `attributeDefinition`. Confirmed by listing that class's real properties
  before touching anything, not guessed from the name alone. The same
  `...Definition` → `...OwningDefinition` pattern repeated identically
  across all 4, which is what made this safe to treat as one mechanical
  fix rather than four separate judgment calls.
- **2 were left alone.** Both reference `ConnectionUsage.connectionDefinition`,
  and `ConnectionUsage` turns out to have zero owned association ends at
  all — not a rename, something that needs real investigation. Not
  touched.

The 7 verified ones were fixed by a script
(`phase17_fix_stale_redefines_note_references.jy`) that checked each
note's exact current text matched what was expected *before* changing
anything, and stopped (raised an error) rather than guess if it didn't.
Re-checked afterward: all 7 now resolve correctly. Two of them still end
up rejected for the same "opposite mismatch" reason as other cases above
— that is the correct, honest outcome, not a new problem: they went from
*silently and completely broken* to *properly evaluated and correctly
flagged*, which is real progress even where the answer is still "not yet."

### What this does and does not prove

This proves the fixed rule is sound against the real KerML/SysML data,
not just invented examples — the single biggest piece of validation this
whole effort has had. It does **not** mean generation has actually been
run, and it does **not** mean the guard-wiring from step 3 has been
exercised against any of these 124 real cases yet — that still requires
an actual SemGen generation, which remains the user's call, unchanged from
every earlier caveat in this document.

## Cleaning up the notes themselves (2026-09-26): phases 24 to 28

Everything above is about the generator. This section is about the *data* the
generator reads. It turned out that several of the `Redefines (per normative
XMI): ...` notes in `reference/design` did not say what the normative XMI says.
They were not typos. They came from three successive guesses, each built on the
one before, and none of them checked against the XMI at the time.

### The chain of mistakes, in order

**Phase 17** assumed that four properties named `<x>Definition` in `spec` had
been renamed `<x>OwningDefinition` in `design`, and "fixed" four notes to point
at the new name. That assumption was wrong. `<x>Definition` and
`<x>OwningDefinition` are two *different* chains in the normative XMI:

- the **typing** chain: `Usage.definition` -> `Feature.type`
  (`attributeDefinition`, `occurrenceDefinition`, ...)
- the **ownership** chain: `Usage.owningDefinition`
  (`attributeOwningDefinition`, ...)

They share a name fragment and nothing else. Phase 17 matched on the name
resemblance instead of on the shape of the declaration.

**Phase 23** then derived five more notes from phase 17's conclusion, using the
rule "if X redefines Y, then the opposite of X redefines the opposite of Y."
The rule is sound. The input was not, so all five came out wrong.

**Phase 27's six** are older than both and have a different origin: whatever
produced them turned a `<subsettedProperty>` into a `Redefines` line. Five of
the six still carried their *correct* `Subsets ... sourceRelationship` line,
with the contradictory `Redefines` line sitting directly underneath it.

### Why a wrong note is not a harmless comment

The note is the only channel the generator has. `PropertyRedefinition` reads the
`Redefines (per normative XMI): Class.prop` line and treats it as an
instruction: *store this property in that other property's slot*. So a wrong
note does one of two things, both bad:

- it names a property that does not exist in `design`, and `resolve()` throws.
  The preflight runs over every metaclass *before* the transaction opens, so one
  throw aborts the entire generation; or
- it names a property that *does* exist but is the wrong one, and the generator
  silently shares the wrong storage slot. Nothing fails. The generated API is
  just wrong.

The six in phase 27 were of the second kind, and six of them were being
**accepted** before the correction. They would have shipped.

### What each phase did

| Phase | What it corrected | Count |
|---|---|---|
| 24 | Rewrote phase 17's four misdirected notes as plain prose naming the true target. The target is one of the 32 associations deliberately absent from `design`, so no directive is possible. | 4 |
| 25 | Same treatment for `InterfaceUsage.interfaceDefinition` and `AllocationUsage.allocationDefinition` (both -> `ConnectionUsage.connectionDefinition`, also absent). These were never misdirected; they simply point at something `design` does not have. | 2 |
| 26 | Reverted phase 23's five. Four are `subsettedProperty` toward `DataType.definedAttribute`, `Class.definedOccurrence`, `Predicate.definedConstraint`, `Function.definedCalculation` -- all themselves among the 32 absent, so recorded as prose. The fifth, `PortDefinition.conjugatedPortDefinition`, already had the correct `Subsets ... Namespace.ownedMember` line; phase 23 had merely added a bogus `Redefines` line on top, so stripping it restores the original. | 5 |
| 27 | Turned six `Redefines ... KerMLModelElement.sourceRelationship` lines into `Subsets ...`, which the generator does not read. The XMI declares no `<redefinedProperty>` on any of them. | 6 |
| 28 | Marked `VariantMembership.ownedVariantUsage` and `ConjugatedPortDefinition.ownedPortConjugator` composite. Both redefine a composite storage property, so they must carry the same aggregation as the slot they write into; both are `owned*` properties, composite everywhere else in `design`; and neither end of their association was composite, so the mark is legal. Same class of omission as the four found in the earlier composition review. | 2 |

Phases 24 to 27 leave `reference/spec` untouched throughout. `spec` is the
fidelity mirror of the normative XMI and is never generated from; where it
already held the correct directive, it keeps it.

### Where the count landed

| | unresolved | accepted | rejected |
|---|---|---|---|
| before phase 24 | 0 | 170 | 14 |
| after phases 24-26 | 0 | 169 | 10 |
| after phase 27 | 0 | 169 | 10 |
| after phase 28 | **0** | **165** | **8** |

Phase 27 looks like it achieved nothing, because the count did not move. What it
actually did was move the rejection from one end of six associations to the
other, and remove six *false acceptances* on the way. 169 accepted before phase
27 included six that were only accepted because of a wrong note. 165 is the
honest number.

`UNRESOLVED: 0` is the important one: no note now names a property that does not
exist, so the preflight no longer aborts on a dangling reference.

**These counts came from a checker that was shallower than the real preflight.**
It followed each declaration one hop and stopped, where `canonical()` follows the
whole chain, and it did not implement the multi-target merge check or the
storage-name collision checks at all. That is why it never flagged
`CrossSubsetting.crossingFeature`, which aborted the first real generation run.
The numbers above are still the right record of what those phases fixed; for the
current state, use the dry run described under "The first real run" below, which
mirrors the deployed preflight properly: 626 properties, 171 classes, 0 hard
defects, 8 duplicated members.

### The 8 that remain, and why

They fall into exactly two groups.

**Group A -- the opposite end only subsets (7 cases).**

`Import.importOwningNamespace`, `Membership.membershipOwningNamespace`,
`Differencing.typeDifferenced`, `Intersecting.typeIntersected`,
`Unioning.typeUnioned`, `FeatureChaining.featureChained` all redefine
`Relationship.source`. `ConjugatedPortDefinition.originalPortDefinition`
redefines `Element.owningNamespace`. All seven redefinitions are real and
verified in the XMI, and all seven narrow safely.

What fails is the opposite end. Storage sharing is symmetric: if
`importOwningNamespace` writes into the `source` slot, then reading
`Namespace.ownedImport` has to read back out of `sourceRelationship`. But
`ownedImport` does not redefine `sourceRelationship` -- it *subsets* it, and it
is composite while `sourceRelationship` is not. A subset is not the same slot;
it is a filtered view over part of one. Producing it needs a derived,
computed accessor, which is the derived-property work in blocker 2 below.

The guard is right to reject these. It is refusing to generate an accessor pair
that would disagree with itself.

**Group B -- composite redefines reference (1 case).**

`OwningMembership.ownedMemberElement` is composite and redefines
`Membership.memberElement`, which is a plain reference. The XMI confirms the
redefinition. The semantics are real too: an `OwningMembership` owns its member,
a plain `Membership` only points at one. Sharing one slot between an owning
accessor and a referencing accessor would decide the containment tree twice.
This is a genuine modelling question, not a defect, and not one to settle
unilaterally.

## Splitting the preflight's two failure modes (2026-09-26): `SemGen_4.0.08.jmdac`

Until now the preflight treated every failure the same way: one throw, whole
generation aborted. That conflated two very different things, and it meant the 8
cases above blocked everything.

They are now separated.

**A defect in the metadata still aborts the run.** A declaration naming a
property that does not exist, a malformed declaration, a cycle, a merge of
independent storage, an ambiguous or shadowed storage name -- all still fatal.
Generating from bad metadata produces a silently wrong API, which is worse than
not generating at all. The phase 27 six are exactly why this half must stay
strict: they were being *accepted*, and nothing would have told anyone.

**A redefinition that cannot share storage safely no longer aborts anything.**
It keeps its own storage slot, and the case is reported. That is a known
limitation of the storage-sharing scheme, not a defect in the model.

The cost is precise and small: those 8 properties stay duplicated. The other 165
are still deduplicated. Before this work, all 173 were duplicated.

### How it is implemented

| Piece | Where |
|---|---|
| `UnsafeRedefinitionException extends IllegalArgumentException` -- the marker for "limitation, not defect" | `utils/PropertyRedefinition.java` |
| Thrown at the three "requires an adapter" sites, and only those | `attributeStorage` (x2), `associationStorage` |
| `attributeStorageOrSelf` / `associationStorageOrSelf` -- catch it, return the property's own storage | same file |
| `unsafeRedefinitions(GeneralClass)` -- enumerate the degradations for reporting | same file |
| Tolerant callers: `storedEnds`, `storedAttributes`, `narrowing`, `attributeStorageName`, `MetaclassSmDependencyGenerator` | generator paths |
| Preflight logs each degradation after `validate()` | `base/BaseGenerator.java` |

`associationStorage` and `attributeStorage` themselves stay **strict**. Only the
`OrSelf` wrappers degrade. That keeps every existing test meaningful: the eleven
that assert a soft refusal call the strict methods directly.

An unsafe end also yields no narrowing, so no runtime guard is emitted for it --
correct, since it now owns the slot it writes into and there is nothing to
constrain.

### Tests

**92 pass, 0 fail** (was 86). One existing test asserted the old policy and was
rewritten to pin both halves of the split instead of one; six are new:

- `degradesUnsafeAssociationRedefinitionToItsOwnStorage` -- the declaration still
  resolves, the strict call still throws `UnsafeRedefinitionException`, the
  tolerant call returns the property itself, no guard is emitted, `validate`
  does not throw, and the degradation is reported rather than silent.
- `excludesEndsThatDegradedToTheirOwnStorageInsteadOfPropagating` -- the same
  case seen through `AssociationGuardHelper`, which previously had no coverage
  of this path.
- `BaseGeneratorRedefinitionPreflightTest` (5 tests) -- the preflight had no test
  at all before. Covers: no redefinitions at all; a declaration resolving to
  nothing (aborts); an ambiguous declaration (aborts); a redefinition that
  cannot share storage (does **not** abort); and a defect sitting next to a
  degraded case, to prove the degradation does not mask it.

### The archive

The first build of 4.0.08 packaged **two** generator jars -- 1.4.04 was still
sitting in `target/lib/` from the previous build, and `package` without `clean`
does not remove it. `module.xml` named 1.4.05, so it would probably have loaded
the right one, but an archive carrying two versions of its own generator is not
something to hand over. **Build SemGen with `clean` from now on**, and check the
archive afterwards: it must contain exactly one `lib/semgenerator-*.jar`.

## The first real run, and what it found (2026-09-26)

4.0.08 was deployed and a generation was run. It aborted:

```
11:16:10 ERROR   Redefinition merges independent storage: crossingFeature
11:16:10 ERROR   Generation failed: java.lang.IllegalArgumentException: ...
```

That is the preflight working as intended -- a genuine metadata defect, caught
before the transaction opened, with nothing half-written. But it exposed three
separate problems, described below in the order they were found.

### Problem 1: the error messages said almost nothing

`Redefinition merges independent storage: crossingFeature` does not say which
class owns the property, which two declarations disagree, what each resolves to,
or what to do about it. Every message the preflight can produce has been
rewritten to carry all four. The same failure now reads:

> Redefinition merges independent storage: CrossSubsetting.crossingFeature
> declares that it redefines both Subsetting.owningFeature (whose storage
> resolves to Specialization.owningType) and Subsetting.subsettingFeature (whose
> storage resolves to Relationship.source). A property can occupy only one
> storage slot, so these two cannot both be its storage. If the normative XMI
> relates them by subsetting rather than leaving them independent, keep only the
> narrower one on the 'Redefines' line and record the other as 'Subsets (per
> normative XMI): ...', which is not read as a storage instruction.

Every other message was given the same treatment: the unresolved-reference
message now lists the ancestor classes actually searched; the ambiguous one
names the competing properties; the cycle one prints the cycle; the malformed
one quotes the exact text it could not read; the shadowing one names the
inherited property and gives the line to add. The three "cannot share storage"
messages now name the specific mismatch -- aggregation, opposite, target type or
multiplicity -- instead of a single generic sentence for all of them.

*(The `AVERTISSEMENT` / `GRAVE` labels that appear when running the unit tests
under Maven are `java.util.logging` rendering its level names in the JVM's
locale. SemGen's own formatters hardcode `ERROR` and `WARNING`, so the Modelio
log is unaffected.)*

### Problem 2: finding defects one generation run at a time

Fixing `crossingFeature` alone would just move the abort to the next defect.
Instead the preflight's logic was reimplemented as a dry run against the live
model (`canonical()`'s parse and resolution, plus `storedEnds`/
`storedAttributes`' collision checks), so every hard defect is found in one pass.

It found exactly **three**, all the same kind, and phase 29 fixed them:

| Property | Declares two targets | Resolving to | Kept |
|---|---|---|---|
| `CrossSubsetting.crossingFeature` | `Subsetting.owningFeature` + `Subsetting.subsettingFeature` | `Specialization.owningType` / `Relationship.source` | `owningFeature` |
| `ReferenceSubsetting.referencingFeature` | same two | same two | `owningFeature` |
| `Flow.interaction` | `Connector.association` + `Step.behavior` | `Feature.type` / `Step.behavior` | `Connector.association` |

All three declarations are faithful to the XMI -- each really does carry two
`<redefinedProperty>` children. What design cannot carry is the relation
*between* the two targets, which is what makes them one slot in KerML:

- For the first two, `Subsetting.owningFeature` **subsets**
  `Subsetting.subsettingFeature`, so in KerML they coincide for these
  properties. The XMI therefore decides it: the narrower one, `owningFeature`,
  is the storage.
- For `Flow.interaction`, `Connector.association` redefines `Feature.type` while
  `Step.behavior` only subsets it. Neither subsets the other, so **the XMI does
  not decide this one**. `Connector.association` was kept because its storage is
  `Feature.type` itself, the widest slot the three share. This is a modelling
  decision and should be confirmed by the team.

The dropped target is recorded as prose on a second line in each case,
deliberately without the literal `Redefines (per normative XMI):` phrase so the
parser reads exactly one reference.

### Problem 3: degrading to "own storage" was too blunt, and could still abort

With the three merges fixed, the dry run surfaced a defect that the fallback had
*created*:

```
[SHADOWS] EndFeatureMembership.ownedMemberFeature needs slot 'ownedMemberFeature',
          already inherited from FeatureMembership.ownedMemberFeature
```

Both properties sit on the same chain:

```
EndFeatureMembership.ownedMemberFeature
  -> FeatureMembership.ownedMemberFeature
    -> OwningMembership.ownedMemberElement
      -> Membership.memberElement          <- only THIS hop is unsafe
```

Only the last hop is refused (a composite property writing into a reference
slot). But "degrade to own storage" collapsed *every* property on the chain to
its own slot. Two of them are named `ownedMemberFeature` and sit in a
generalization relationship, so the lower one shadowed the upper -- and
shadowing is a **fatal** check. The fallback had turned a limitation into an
abort.

The rule is now: **settle on the furthest ancestor along the declared chain that
can still be shared safely.** Only the broken link takes a slot of its own;
everything below it shares that link.

The effect on this model is large:

| | properties not reaching their full canonical storage | of those, taking a slot of their own |
|---|---|---|
| collapse-to-self | 24 | **24** |
| furthest-safe-link | 24 | **8** |

Sixteen members that would have been duplicated are not. Fifteen share
`OwningMembership.ownedMemberElement`; one shares
`Membership.membershipOwningNamespace`.

### Where it stands now

Dry run against the live model, mirroring the deployed preflight:

- **0 hard defects.** Nothing aborts.
- **8 duplicated members**, in the two groups described under "The 8 that
  remain, and why" above -- 7 whose opposite only subsets, and
  `OwningMembership.ownedMemberElement`.

### Tests

**93 pass, 0 fail.** Beyond the six added for the preflight split, one more pins
the chain-walking rule directly
(`settlesOnTheFurthestSafeLinkRatherThanTakingItsOwnStorage`), building the same
four-link shape as the `ownedMemberFeature` chain and asserting that the two
lower properties share the middle link, that nothing shadows anything, and that
`validate` does not throw. That bug was subtle enough -- a fallback creating a
fatal error -- that it must not regress silently.

## The second run: past the preflight, into code generation (2026-09-26)

4.0.09 was deployed and run. The preflight **passed**. It printed its 14
warnings, prepared all 81 metaclasses, and got into Java code generation before
failing on something else entirely:

```
11:46:55 WARNING 14 property redefinition(s) cannot share their canonical storage safely; ...
11:46:55         Full metamodel generation: generate 81 metaclasses...
11:46:55         Generating Java classes features for metaclass 'KerMLModelElement'
11:47:01 ERROR   java.lang.IllegalArgumentException: 'JavaImport' tag type is not unique in module 'JavaArchitect'
```

### The dry run predicted this exactly

The run reported **14**; the dry run reports **24**. That is not a discrepancy:
this run generates KerML only, and the dry run scans all of `reference/design`.
Removing the 10 SysML-owned entries from the dry run's list leaves exactly the
14 the run printed, item for item — 7 keeping their own slot and 7 sharing a
partial one. The dry run can be trusted for the SysML generation too.

### The `JavaImport` failure was mine

`JavaArchitect` declares a **separate `JavaImport` tag type for each metaclass**
— Class, Interface, Enumeration and Package. So looking it up by name alone
identifies four of them, and `IUmlModel.createTaggedValue(module, name, owner)`
refuses, out of `InfrastructureModelFactoryImpl`.

`JavaUtils.addJavaImport` had always done that string lookup, but until now its
only callers were the Monoge generators, which this Toutatis run does not
execute. `RuntimeSupportGenerator` — added earlier in this work to emit
`AssociationMutationGuard` and `RedefinedAssociationList` — was the first caller
on the Toutatis path, so it was the first to reach the latent bug.

The fix resolves the tag type from the target's metaclass, using the
JavaArchitect API's own constants (`JavaClass.MdaTypes.JAVAIMPORT_TAGTYPE_ELT`
and its Interface/Enumeration/Package siblings). This is the same pattern the
adjacent line already used for note types
(`JavaClass.MdaTypes.JAVAMEMBERS_NOTETYPE_ELT`). The string-based signature is
kept and now delegates, so the Monoge callers are fixed too.

**Rule: never look up a JavaArchitect tag or note type by `(module, name)`.**
Use the metaclass-specific constant from its API.

### Two things this run confirmed in passing

- `element.getTemplate().add(tp)` in `RuntimeSupportGenerator`, flagged in a
  comment as UNVERIFIED against a live run, executes without throwing — the
  failure came after it. It is not yet confirmed to produce *correct* output.
- `KerMLModelElement` has **four** composition dependencies (`owner`,
  `owningRelationship`, `owningMembership`, `owningNamespace`), and SemGen warns
  that `GetCompositionRelation()` cannot choose between them. In the normative
  XMI these are derived unions. This is not fatal and is not a redefinition
  issue, but it is worth a decision before trusting the generated containment.

## The third run: a build mistake, not a code one (2026-09-26)

4.0.10 reached the same point and failed with:

```
12:32:45 ERROR   Generation failed: 'void com.modeliosoft.tools.semgen.utils.JavaUtils
                 .addJavaImport(IUmlModel, GeneralClass, String)'
```

That message is a `NoSuchMethodError`, and the signature it prints is the **old**
one. The `JavaImport` fix widened that parameter from `GeneralClass` to
`ModelElement` -- source-compatible, but **binary-incompatible**. The
semgenerator subproject was rebuilt with `mvn install` and no `clean`, so Maven
recompiled only the edited `JavaUtils.java` and left `RuntimeSupportGenerator
.class` still linked against the signature that no longer existed.

So 4.0.10 contained the correct fix and could not run it.

**`clean` on both build steps, always.** The lesson had already been learned
once, for the packaging step (4.0.08 shipped two generator jars), and was then
not applied to the generator step. The two failures are different symptoms of
the same omission:

| Step built without `clean` | Symptom |
|---|---|
| `SemGen` (packaging) | archive contains two `semgenerator-*.jar`, only one named in `module.xml` |
| `semgenerator` (compile) | `NoSuchMethodError` naming a signature that no longer exists |

And verify rather than assume. After a signature change, every call site in the
built jar must show the new descriptor:

```
javap -p -c -cp semgenerator-<v>.jar <CallerClass> | Select-String addJavaImport
```

For 4.0.11 all seven call sites link against `...ModelElement;Ljava/lang/String;)V`,
with no `GeneralClass` descriptor left anywhere.

### The log now identifies its own build

A stale deployment failing reads exactly like current code failing, and a log
pasted into a chat or a ticket carries nothing to tell them apart. Every
generation now opens with:

```
SemGen <version> generating '<component>'
```

from `getConfig().getGeneratorVersion()`, which `GeneratorConfig` already held
from `module.getVersion()` and simply never logged. Requested by the user after
this run; it would have identified the 4.0.10 problem immediately.

## The fourth run: 24 metaclasses in, and a strict/tolerant contradiction (2026-09-26)

4.0.11 generated 24 metaclasses before failing on the 25th:

```
12:40:56 ERROR   UnsafeRedefinitionException: EndFeatureMembership.ownedMemberFeature ->
                 Relationship.target: aggregation differs ...
```

That is a **soft** failure escaping at generation time — and six minutes earlier
in the same log, the preflight had reported the same property as successfully
degraded:

```
12:40:50 WARNING EndFeatureMembership.ownedMemberFeature -> ... It shares
                 OwningMembership.ownedMemberElement instead, the furthest ancestor it can safely reach.
```

The two halves of the generator disagreed about the same property.

**Cause: one call site still resolved strictly.** `MetaclassSmDependencyGenerator`
decides whether a renamed redefinition needs an alias getter by resolving the
storage *tolerantly* and comparing names. For `ownedMemberFeature` the tolerant
answer is `OwningMembership.ownedMemberElement` — a different name, so an alias
is needed. It then called `associationAliasBody`, which re-resolved the same
property **strictly** and threw.

`associationAliasBody` now uses `associationStorageOrSelf`, so the alias names
the slot the property actually occupies. That is also what the alias is *for*:
forwarding to the real storage descriptor, which for a degraded redefinition is
the furthest ancestor it reached, not the canonical it could not.

**The general shape of this bug is worth remembering:** when one code path
decides *whether* to do something from the tolerant resolution and another
decides *what to emit* from the strict one, they contradict each other exactly
on the degraded properties. After this fix the only strict callers left are
`unsafeRedefinitions` (which catches, by design) and the tests.

Pinned by `aliasBodyNamesTheSlotADegradedRedefinitionActuallyGot`.

### Candidate

`H:\modelio\work\eclipse\modules\SemGen\target\SemGen_4.0.12.jmdac`
(SemGen 4.0.12 / semgenerator 1.4.09), both projects built with `clean`, one
generator jar, **94 tests** passing. Supersedes 4.0.09 (`JavaImport`), 4.0.10
(`NoSuchMethodError`) and 4.0.11 (strict/tolerant contradiction).

### What this does and does not mean

The redefinition preflight no longer blocks a generation run on this model, and
the run gets further than it ever has. That is not the same as the generated
output being correct: a full generation has still never completed end to end
here, so nothing downstream of the preflight has been exercised on real data.
The remaining blockers below are unchanged, and the 8 duplicated members are
deferred work, not closed questions.

## The successful run (2026-09-26, 13:36) -- KerML end to end

4.0.12 completed:

```
13:36:42         Commiting transaction...
13:36:42         GENERATION SUCCESSFUL
```

What it produced: 81 metaclasses generated (79 with `SmClass` descriptors; the
two enumerations `VisibilityKind` and `FeatureDirectionKind` do not get one),
then the model shield checker factory, the `KerMLMetamodel` fragment, 37
metamodel link experts, 79 meta experts, the visitors, and the missing imports
-- all committed in one transaction.

The redefinition work behaved exactly as predicted throughout: 14 warnings, the
same 14 the dry run listed for KerML, 7 keeping their own slot and 7 sharing a
partial one. Nothing in the redefinition path failed.

### What is NOT established by this

The generation wrote API and implementation classes **into the Modelio model**.
That Java has not been generated to disk, compiled, or executed. "Successful"
here means SemGen produced its output without error, not that the output is
correct.

### 28 attributes generated with no initial value

Logged at ERROR, but non-fatal -- generation continued past every one. A boolean
or enum metamodel attribute with no default is a real gap, so these want fixing
before the generated code is trusted:

| Class | Attributes |
|---|---|
| `KerMLModelElement` | `isImpliedIncluded`, `isLibraryElement` |
| `Relationship` | `isImplied` |
| `Import` | `visibility`, `isRecursive`, `isImportAll` |
| `Membership` | `visibility` |
| `Type` | `isAbstract`, `isSufficient`, `isConjugated` |
| `Feature` | `direction`, `isComposite`, `isConstant`, `isDerived`, `isEnd`, `isOrdered`, `isPortion`, `isUnique`, `isVariable` |
| `Function` | `isModelLevelEvaluable` |
| `Expression` | `isModelLevelEvaluable` |
| `Invariant` | `isNegated` |
| `LiteralBoolean` / `LiteralInteger` / `LiteralRational` | `value` |
| `FeatureValue` | `isInitial`, `isDefault` |
| `LibraryPackage` | `isStandard` |

(`Type`'s three and `Relationship.isImplied` are logged more than once, from the
flattened-inheritance passes over `Association`, `Connector` and `Interaction`.)

The normative XMI gives defaults for most of these, so this is a fixable data
gap rather than a decision.

### Four classes whose containment SemGen could not decide

`GetCompositionRelation(): class '<X>' has several (<n>) composition dependencies.`

| Class | Composition dependencies |
|---|---|
| `Feature` | 5 -- `endOwningType`, `owningType`, `owningEndFeatureMembership`, `owningFeatureMembership`, `owningParameterMembership` |
| `KerMLModelElement` | 4 -- `owner`, `owningRelationship`, `owningMembership`, `owningNamespace` |
| `Expression` | 3 -- `owningResultExpressionMembership`, `expressedValuation`, `owningFilter` |
| `Annotation` | 2 -- `owningAnnotatedElement`, `owningAnnotatingElement` |

These are derived unions in the normative XMI: an element has exactly one owner
at a time, reached through whichever relationship applies. Modelio's containment
tree wants a single composition, so SemGen picks one. **This decides where
elements live in the generated model**, so it should be settled deliberately.
It is a modelling decision, not a defect, and it is unrelated to redefinitions.

### One flattened-inheritance collision

```
WARNING Flattened inheritance: 'Association' already has an operation named
        'visibleMemberships'; skipping the one from secondary parent branch 'Namespace'.
```

`Association` inherits `visibleMemberships` down two branches and SemGen kept the
primary one. Benign if the two are the same operation, which should be checked
once.

## SysML generated too (2026-09-26, 13:46)

```
13:46:22         GENERATION SUCCESSFUL
```

97 metaclasses, 92 with `SmClass` descriptors (five enumerations do not get
one), 28 link experts, 92 meta experts, the `SysML2Metamodel` fragment,
visitors, imports -- committed in one transaction.

KerML was consumed cleanly as a dependency: `Found 81 metaclasses in
sysml2.modelio.sysml.reference.design.KerML.Model`, alongside the 42
infrastructure metaclasses, for 123 collected.

**The dry run's prediction was exact again:** 10 degraded properties, precisely
the complement of KerML's 14, out of the 24 the dry run lists for all of
`reference/design`. Nine share `OwningMembership.ownedMemberElement`; only
`ConjugatedPortDefinition.originalPortDefinition` keeps a slot of its own.

So both metamodels generate, and the redefinition mechanism behaved exactly as
predicted on both.

## The missing initial values, classified (2026-09-26)

The two runs reported 40 attributes with no initial value. Checked against the
normative XMI, they fall into three groups, and only the first is a simple fix.

### Fixable directly from the XMI -- 24

The XMI declares a default; `reference/design` just does not carry it.

| Default | Attributes |
|---|---|
| `false` | `KerMLModelElement.isImpliedIncluded`, `Relationship.isImplied`, `Import.isRecursive`, `Import.isImportAll`, `Type.isAbstract`, `Type.isSufficient`, `Feature.isComposite`, `isConstant`, `isDerived`, `isEnd`, `isOrdered`, `isPortion`, `isVariable`, `Invariant.isNegated`, `FeatureValue.isInitial`, `FeatureValue.isDefault`, `LibraryPackage.isStandard`, `OccurrenceDefinition.isIndividual`, `OccurrenceUsage.isIndividual`, `StateDefinition.isParallel`, `StateUsage.isParallel` |
| `true` | `Feature.isUnique` |
| enum | `Import.visibility` = `private`, `Membership.visibility` = `public` |

Note `Feature.isUnique` defaults to **true** while every other boolean here
defaults to false -- worth not fixing these in bulk without reading each one.

### Derived, so no stored default belongs here -- 5

`KerMLModelElement.isLibraryElement`, `Type.isConjugated`,
`Function.isModelLevelEvaluable`, `Expression.isModelLevelEvaluable`,
`Usage.isReference` are all `isDerived="true"` in the XMI. They are computed,
not stored. Giving them an initial value would paper over the fact that they
need the derived-property work (blocker 2), so the right fix is to mark them
derived in `reference/design` instead.

### Needs a decision -- 11

| Attribute | Why |
|---|---|
| `Feature.direction`, `OccurrenceUsage.portionKind` | **0..1** -- optional, so absence is meaningful and no default is needed. SemGen's ERROR is arguably a false alarm for these two. |
| `LiteralBoolean.value`, `LiteralInteger.value`, `LiteralRational.value` | 1..1, and the value *is* the literal's content. The spec declares no default; `false` / `0` / `0.0` would be the conventional choice. |
| `Definition.isVariation`, `Usage.isVariation` | 1..1 boolean, spec declares no default, but `false` is the obvious reading (nothing is a variation unless declared one). |
| `TriggerInvocationExpression.kind`, `StateSubactionMembership.kind`, `TransitionFeatureMembership.kind`, `RequirementConstraintMembership.kind` | 1..1 mandatory enums with no declared default. Each needs a chosen literal, which is a modelling decision. |

## Three offline findings (2026-09-26, XMI and SemGen source only)

### The flattened-inheritance collisions are benign -- closed

Both families are the **same operation declared identically on both branches**, so
SemGen skipping one is harmless:

| Operation | Declared on | Signature |
|---|---|---|
| `visibleMemberships` | `Namespace` and `Type` (KerML) | `(excluded: Namespace, isRecursive: Boolean, includeAll: Boolean) : Membership` -- identical |
| `modelLevelEvaluable` | `Expression` (KerML), `CalculationUsage`, `ConstraintUsage` (SysML) | `(visited: Feature) : Boolean` -- identical |

`Association` inherits `visibleMemberships` from both `Type` and `Namespace`;
`IncludeUseCaseUsage` does not declare `modelLevelEvaluable` at all and simply
inherits it. Nothing to decide.

### The four `kind` enums have no "unset" literal

Each is a genuine three- or two-way discriminator with no neutral value:

| Attribute | Enum | Literals, in declaration order |
|---|---|---|
| `TriggerInvocationExpression.kind` | `TriggerKind` | `when`, `at`, `after` |
| `StateSubactionMembership.kind` | `StateSubactionKind` | `entry`, `do`, `exit` |
| `TransitionFeatureMembership.kind` | `TransitionFeatureKind` | `trigger`, `guard`, `effect` |
| `RequirementConstraintMembership.kind` | `RequirementConstraintKind` | `assumption`, `requirement` |

So any default is arbitrary. In practice it is only ever seen by an element
created without setting the kind, which real code always does set, so the value
matters less than having one at all. The mechanical choice is the
**first-declared literal**, which gives `when`, `entry`, `trigger`,
`assumption`. The one place semantics pull the other way is the last:
`requirement` reads more naturally than `assumption` for a
`RequirementConstraintMembership`.

### The 8 duplicated members cannot be removed by editing the model

This is the important one, given the goal of having no duplicates.

Each of the 8 is a **pair**: the property keeps a slot of its own *and* the class
still inherits the canonical slot it failed to share. `Import` ends up with both
`source` (inherited from `Relationship`) and `importOwningNamespace`, meaning the
same thing, stored twice.

Three routes were checked, and only the third works:

1. **Make them share the slot after all.** Not possible. Modelio's dependency
   descriptor is bidirectional -- sharing a slot shares it in both directions.
   For `Import`, writing `importOwningNamespace` would write the `source` slot,
   whose inverse is `sourceRelationship`; but the opposite end `ownedImport` is a
   *different*, composite slot and would not be updated, so the Import would be
   referenced and yet not contained. The guard is right to refuse.

2. **Mark the redundant end derived**, so it gets no storage. Half-works, and the
   half that fails is fatal. `isIsDerived()` is honoured in `datagen` and `mcgen`
   (`DataGenerator:97`, `MetaclassLoadGenerator:106`,
   `MetaclassSmDependencyGenerator:50`) so the field and descriptor would indeed
   disappear -- but it appears **nowhere in `apigen` or `impgen`**, so the API and
   implementation would still emit accessors, now reading a descriptor that does
   not exist. This is exactly the previously audited "858 calls to 397 absent
   dependency getters after derived descriptors were suppressed".

3. **Delete the redundant end from `reference/design`** and let callers use the
   inherited one. This is the only route that removes the duplicate today. It
   costs the domain-friendly accessor name (`getImportOwningNamespace()` becomes
   `getSource()`), and it is destructive surgery on associations -- deleting an
   `AssociationEnd` deletes its opposite too, so each one needs checking first.

Route 2 becomes the right answer as soon as derived-property computation exists
(blocker 2), because the computation for all 8 is trivial -- each is its
canonical storage, narrowed. Adding the missing `isIsDerived()` guard to
`apigen`/`impgen` together with a generated computed body would remove all 8
duplicates and keep the names.

## Two workflow answers (2026-09-26)

### The generation log is already written to a file, and now kept

`GenerateMetamodelCommand` and `GenerateMetaclassCommand` both call
`LOG.setLogFile(<project>/semgenlog.html)`, so every run already writes a full
HTML log -- no need to paste console output, and nothing gets truncated. For
this project that is:

```
H:\modelio\work\modelio\modelio.all\semgenlog.html
```

**It was being destroyed between runs.** `setLogFile` starts with
`Files.deleteIfExists(logFile)` and the path is a fixed name, so generating
KerML and then SysML left only the SysML log -- the first run's evidence was
gone before anyone could read it, and getting it back costs a full regeneration.

Since **4.0.14**, each finished log is also copied to
`<project>/semgen-logs/<yyyyMMdd-HHmmss>-<MetamodelName>.html`. The copy happens
after `setLogFile(null)`, which flushes and closes the handler, so the archived
file is complete. Archiving is best-effort: a failure to keep the copy never
fails a generation that succeeded.

### Clearing the previous output before regenerating is not required

**SemGen regenerates in place.** Every generator cleans its own target class
before rewriting it:

| Generator | Call |
|---|---|
| `ApiGenerator` | `doClean(cs.getEmfClass())` (line 55) |
| `DataGenerator` | `doClean(cs.getDataClass())` (line 73) |
| `ImplGenerator` | `doClean(cs.getImplClass())` (line 82) |
| `MetaclassGenerator` | `doClean(cs)` (line 69) |

`doClean` deletes the previous generalizations, `JavaExtends`/`JavaImplements`
tags, interface realizations, attributes and association ends, keeping anything
the annotation scheme marks as manual. Class and package creation goes through
`JavaUtils.makeJavaClass`/`makeJavaPackage`, which look the element up first and
only create it when absent. So a second run overwrites rather than accumulates.

**The one thing a rerun does not clean is orphans**: generated classes whose
metaclass has since been renamed or removed. Nothing walks the output looking
for those, so they would linger and keep compiling into the result.

**One generator was appending instead of cleaning.** `RuntimeSupportGenerator`
reused its existing class and then added to it: template parameters via
`element.getTemplate().add(tp)` and imports via `addJavaImport`, which appends a
tag parameter. Over two runs that emits `RedefinedAssociationList<Value, Value>`
and every import twice -- and imports written by an older, buggy SemGen survive
next to the corrected ones, so a fix looks like it did not work. Given a
`doClean` in **4.0.16**.

### Measured: skipping the clear is not actually faster

| | Time |
|---|---|
| KerML, 4.0.16, no prior clear | **13:58** |
| SysML, 4.0.16, no prior clear | **12:31** |
| Both runs | **26:29** |
| KerML into a freshly cleared model (14:18) | ~24 seconds |
| Manual clear | ~20 minutes |

So clearing-then-generating and generating-in-place cost about the same. The
deletion work does not disappear when the manual clear is skipped -- `doClean`
does the same deletions one class at a time, and somewhat less efficiently than
the bulk clear.

**Practical rule:** either approach is fine when the metamodel's metaclasses and
their names are unchanged, which is the case for phases 30 and 31. Generating in
place is one step instead of two and avoids a twenty-minute window in which
Modelio is unresponsive and every ScriptServer call times out, but it is not a
time saving. Clear only after renaming or removing a metaclass, and then only
the orphans need to go.

### A practical note on re-running generations

**Clearing the previous generation's output is slow** -- slow enough that Modelio
is unresponsive for a long stretch and every ScriptServer call times out while
it runs. A generation creates thousands of API and implementation classes,
descriptors, experts and visitors in the model; removing them again is not
cheap. Plan around it: do not queue ScriptServer work straight after a
generation, and read a timeout in that window as "Modelio is busy", not as a
broken script.

## Phase 30 applied (2026-09-26)

29 attributes changed in `reference/design`, each re-read from the model
afterwards and verified:

- **24 initial values**, every one the default the normative XMI declares.
  Listed individually rather than bulk-defaulted, because `Feature.isUnique`
  defaults to `true` while the other 21 booleans default to `false`. The two
  enums were written bare (`private`, `public`), which `getAttributeInitialValue`
  turns into `VisibilityKind.PRIVATE` / `VisibilityKind.PUBLIC`.
- **5 marked derived**: `KerMLModelElement.isLibraryElement`,
  `Type.isConjugated`, `Function.isModelLevelEvaluable`,
  `Expression.isModelLevelEvaluable`, `Usage.isReference`.

**The 5 derived marks will not silence their errors**, and that was known before
applying them. `DataGenerator`'s attribute loop (line 118) has no
`isIsDerived()` check, unlike every association-end path, so a derived attribute
still gets a data field and still reports a missing initial value. The mark is a
fidelity fix: the design now says what the XMI says, and it records why those
five have no default.

Expected effect on the next run: **24 of the 40 reported attributes clear**, 16
remain -- the 5 derived, plus the 11 that need a decision.

## Phase 31 applied (2026-09-26)

The 9 attributes that needed a chosen value. **Unlike phase 30's 24, the XMI
declares no default for any of these**, so every value here is a deliberate
decision taken to get compilable generated code, not a fact read from the spec.

| Attribute | Value | Why |
|---|---|---|
| `TriggerInvocationExpression.kind` | `when` | first-declared literal |
| `StateSubactionMembership.kind` | `entry` | first-declared literal |
| `TransitionFeatureMembership.kind` | `trigger` | first-declared literal |
| `RequirementConstraintMembership.kind` | `requirement` | **not** first-declared: a requirement constraint is normally a requirement, `assumption` being the special case |
| `Definition.isVariation`, `Usage.isVariation` | `false` | nothing is a variation unless declared one |
| `LiteralBoolean.value` | `false` | zero of its type |
| `LiteralInteger.value` | `0` | zero of its type |
| `LiteralRational.value` | `0.0` | zero of its type (`double`) |

The script validates each value against the attribute's own type before writing
-- an enum value must be a real literal of that enumeration, a boolean must be
`true`/`false`, an integer must parse as one -- so a typo produces a refusal
rather than Java that will not compile.

**Left empty deliberately:** `Feature.direction` (`FeatureDirectionKind`) and
`OccurrenceUsage.portionKind` (`PortionKind`), both **0..1**. Absence is
meaningful there: a Feature with no direction is not a Feature with direction
`in`. SemGen will still log an ERROR for these two, and that ERROR is a false
alarm for an optional attribute.

### Where the 40 stand

| | |
|---|---|
| Phase 30 -- XMI-declared default applied | 24 |
| Phase 31 -- value chosen | 9 |
| Marked derived (error persists, see phase 30) | 5 |
| Left empty on purpose, ERROR is a false alarm | 2 |

Expected on the next run: **33 of 40 cleared**, 7 remaining, all understood --
5 awaiting derived-property support, 2 false alarms.

### Confirmed on the KerML run of 14:18 -- GENERATION SUCCESSFUL

KerML went from 28 distinct attributes reporting to **5**, in 6 ERROR lines
(`Type.isConjugated` appears twice, the second via `Association`'s flattened
branch):

| Still reporting | Why |
|---|---|
| `KerMLModelElement.isLibraryElement` | derived |
| `Type.isConjugated` | derived |
| `Function.isModelLevelEvaluable` | derived |
| `Expression.isModelLevelEvaluable` | derived |
| `Feature.direction` | 0..1, false alarm |

**23 of KerML's 28 cleared**, and the 5 remaining are exactly the ones predicted,
for the predicted reasons. Nothing new surfaced once the noise dropped. The
composition-dependency and flattened-inheritance warnings are unchanged, as
expected -- phases 30 and 31 did not touch them.

### Confirmed on the SysML run of 14:20 -- GENERATION SUCCESSFUL

SysML went from 12 distinct own attributes reporting to **2**, in 6 ERROR lines
(four of them inherited repeats):

| Still reporting | Why |
|---|---|
| `Usage.isReference` | derived |
| `OccurrenceUsage.portionKind` | 0..1, false alarm |
| `Function.isModelLevelEvaluable` (via `CalculationDefinition`, `ConstraintDefinition`) | derived, inherited from KerML |
| `Expression.isModelLevelEvaluable` (via `CalculationUsage`, `ConstraintUsage`) | derived, inherited from KerML |

**10 of SysML's 12 cleared.** All four `kind` enums are silent, so the literals
chosen in phase 31 were accepted -- `when`, `entry`, `trigger`, `requirement`
each generated without complaint. Both `isVariation`, both `isIndividual` and
both `isParallel` are gone, as are the previously inherited
`Relationship.isImplied` and `Invariant.isNegated`.

### Both runs together

**33 of the 40 cleared, as predicted, with nothing unexpected surfacing.** The 7
that remain are the 5 derived attributes (which need derived-property support,
not a value) and the 2 optional ones (where SemGen's ERROR is a false alarm).

The composition-dependency and flattened-inheritance warnings are unchanged in
both runs, as expected -- phases 30 and 31 did not touch them, and the
flattened-inheritance ones are confirmed benign.

## The generated Java compiled for the first time (2026-09-26)

705 files were exported to `H:\src\modelio\modelio\sysml\` --
`sysml.metamodel.api` (180) and `sysml.metamodel.impl` (525). Both are Tycho
`eclipse-plugin` projects, so they were compiled directly with `javac` against
the Modelio jars in the local Maven repository rather than through the full
reactor. That is enough to answer the only question that mattered: does any of
this output compile?

### Round 1: 34 errors, all in one file, and it was mine

Every error was in `AssociationMutationGuard.java` (generated once per
metamodel), lines 23-31 -- the import block:

```java
import import java.util.ArrayList;;
```

`RuntimeSupportSource.imports()` returns whole statements sliced from the
runtime source, while a `JavaImport` tag parameter holds only the name --
JavaArchitect adds the keyword and the semicolon itself. **Fixed** by
`RuntimeSupportGenerator.importedName(...)`, which strips both and leaves a bare
name untouched so it is safe to apply twice.

Those were *syntax* errors, which stop javac before semantic analysis, so they
said nothing about the other 703 files. Patching them locally and recompiling
was what produced the real picture.

### Round 2: 100 errors, three distinct causes

| Cause | Errors | Whose |
|---|---|---|
| `AssociationMutationGuard` referenced under the wrong package | 33 | mine, **fixed** |
| Derived association ends: accessor emitted, descriptor not | ~57 | pre-existing, blocker 2 |
| `aliasIds` multi-valued attribute generated as single-valued | 1 | **new finding** |
| `variable parentClasses` | 8 | probably the ad-hoc classpath, needs the real build |

**The wrong package.** `qualifiedName` formatted
`<outputNamespace>.impl.runtime.<SimpleName>`, giving
`org.modelio.sysml2.metamodel.kerml.impl.runtime`, while the class actually
lands in `org.modelio.sysml.metamodel.kerml.impl.runtime` -- no `2`. A model
package name and a Java package name are not the same thing. It now asks
`IJavaArchitectPeerModule.getFullName(...)`, the only component that knows the
mapping, and **throws rather than guessing** when that module is unavailable.

Three unit tests pinned the old formatting. All three passed, and the formatting
matched its own documentation exactly -- the *premise* was wrong. They were
removed rather than adjusted; a replacement unit test would only have re-pinned
an assumption. This path is covered by compiling the output.

**Derived association ends.** The missing symbols are `getOwnerDep()`,
`getOwningNamespaceDep()`, `getOwningTypeDep()`, `getMemberDep()`,
`getRelatedElementDep()` and similar -- all derived unions in KerML.
`isIsDerived()` is honoured in `datagen`/`mcgen` but appears nowhere in
`apigen`/`impgen`, so the accessor is emitted and the descriptor is not. This is
the same structural gap predicted when phase 30 marked five *attributes* derived,
now confirmed on association ends, and it is the previously audited "858 calls to
397 absent dependency getters" -- today measured at ~57.

**`aliasIds`.** `KerMLModelElementImpl:56` returns
`(String) getAttVal(...getAliasIdsAtt())` from a method declared
`List<String>`. `aliasIds` is `0..*`; the getter was generated as if it were
single-valued. A genuine multiplicity defect in attribute generation, unrelated
to redefinitions.

### Round 3 (4.0.16): the API project compiles clean

After three more generator fixes and one correction to how the sources were
being compiled:

```
API PROJECT ALONE: 180 files, 0 errors, 180 class files produced
```

The impl project still reports 100 errors, and they are now exactly two causes,
neither of them introduced by this work:

| Cause | Errors |
|---|---|
| Missing `get<X>Dep()` -- derived association ends | 99 |
| `aliasIds` multi-valued generated as single-valued | 1 |

### The three further generator bugs, all found only by compiling

**`validateAssociation` emitted `List<List<SmObjectImpl>>`** (35 errors, fixed in
4.0.15). The `values` parameter was created `0..*` on a type that is already
`List`, so JavaArchitect wrapped it twice. The signature then did not match
`ConstrainedObject.validateAssociation(SmDependency, List<SmObjectImpl>)`: 28
argument-type mismatches, 6 name clashes, one unimplemented abstract method.
Collection-ness comes from the type plus `JavaBind`, not from the multiplicity --
`DependencyHelper`'s `EList<T>` parameters are `0..1` for the same reason. These
35 were invisible until the guard-package bug was fixed, because a class that
fails to resolve its supertype is abandoned before its method signatures are
checked.

**`RuntimeSupportGenerator` appended instead of cleaning** (fixed in 4.0.16).
See the workflow section above -- this is the one that would have resurrected the
old broken imports on any regeneration without a full manual clear.

**A note on counting.** The total sat at 100 across three rounds, which looks
like no progress and is the opposite. Each fix let javac get further into classes
it had previously abandoned, exposing more of the same underlying derived-end
problem. Only the *composition* of the errors is informative: guard-package and
`validateAssociation` errors went from 68 to 0, while derived-end errors rose
from ~57 to 99 as more classes became analysable.

### Not a defect: `parentClasses`

Fifteen `cannot find symbol: variable parentClasses` errors were an artifact of
how these sources were being compiled, not of the generated code.

The generated projects inherit from `modelio-parent 7.0.0-SNAPSHOT`, and
`SmClass.parentClasses` -- a `Collection<SmClass>` -- **exists only in 7.0.0**.
Every release from 5.4.1 to 6.2.0 has `parentClass`, singular. The ad-hoc
classpath assembled from the local Maven repository contained all five versions
of each artifact, and javac resolved whichever came first.

That plural field is the kernel-side multi-parent support this whole effort
depends on, so seeing it is a good sign. Rebuilding the classpath as one jar per
artifact, preferring `7.0.0-SNAPSHOT` (104 jars instead of 204), removed all
fifteen.

**When compiling generated sources by hand, deduplicate the classpath by
artifact and match the target platform** -- here Modelio 7.0.0, per the parent
pom, not the 6.2.0 the module's `binaryversion` names.

### Candidate

`H:\modelio\work\eclipse\modules\SemGen\target\SemGen_4.0.16.jmdac`
(SemGen 4.0.16 / semgenerator 1.4.13), clean build, 93 tests passing. Carries
every generator fix found by compiling.

## Next
- **Decide the 11 remaining** -- most are small, the four `kind` enums least so.
- **Decide the multi-composition cases.** KerML has four classes; SysML adds
  `Usage` (2), `VariantMembership` (2), `PartUsage` (2), `RequirementUsage` (2),
  `CalculationUsage` (3), `IncludeUseCaseUsage` (3) and `ConstraintUsage` (4).
- **Check the flattened-inheritance collisions.** KerML:
  `Association.visibleMemberships`. SysML: `modelLevelEvaluable` on
  `CalculationUsage`, `ConstraintUsage` and `IncludeUseCaseUsage`, each skipped
  from the `Expression` branch. Benign if the two sides are the same operation.
- **Generate the Java to disk and compile it** -- still the first real test of
  whether any of this output is correct.

## Remaining blockers

1. Association adapters must maintain one canonical storage location while
   supporting renamed/narrowed access, inherited access paths, mutation through
   both paths, multiplicity checks and inverse-link consistency. For example,
   `Redefinition.redefinedFeature` redefines `Subsetting.subsettedFeature`,
   eventually reaching `Relationship.target`. Replacing only a field or getter
   leaves the different inverse relations incoherent. Pre-mutation constraint
   validation is now tested as a runtime component, but its automatic generation
   and the semantics of distinct specialized opposites remain unfinished.
2. Derived-property computation is not implemented by the attribute-storage
   patch. The previous generated-code audit found 858 calls to 397 absent
   dependency getters after derived descriptors were suppressed.
3. Type/multiplicity/default changes need explicit semantics, not simple
   descriptor reuse. The preflight no longer aborts on them (see "Splitting the
   preflight's two failure modes"); it degrades them to their own storage and
   reports them, which is a containment, not a solution.
4. The description-note convention is the available metadata bridge, not a
   native UML redefinedProperty link. Missing metadata is not guessed.
5. Phase 13 inspected owned UML attributes, whereas the three reported residual
   roles are association ends. Its earlier no-op did not prove their removal.
   Review the associations and inverse roles against XMI before changing them.

## Release gate

Finish association adapters and derived implementations, exercise generated
Java and inverse mutations on an isolated model (including rejected writes,
rollback and undo), rerun the AST and XMI audits, and compile generated modules.
Then build a uniquely identified candidate, verify its embedded generator,
finalize documentation and slides, and hand the archive to the user for
deployment. Preserve the live model and current installation until then.