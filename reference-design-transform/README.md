# reference/spec → reference/design transformation and repair scripts

This folder is a collection of numbered Modelio scripts, not a single 28-step
pipeline. The initial assembly sequence builds `reference/design` from
`reference/spec` (the UML-fidelity mirror); later scripts record targeted
repairs and corrections, including reversals of earlier changes. The scripts
operate on the live `sysml2` Modelio project. See
`deck-implementation-plan/points-a-trancher.md` (points 1–6 and "Points ouverts")
for the full design rationale.

**Status, 2026-09-24:** the generated metamodel is not yet validated for release.
Redefined storage and derived-accessor generation remain partially implemented.
See [SemGen redefinition status](semgen-redefinitions-status.md) for tested
behavior, known bypasses and the release gate. The 4.0.06 archive is an older
local work-in-progress candidate, not a package of the latest source changes.
The user handles deployment; no automatic module installation is planned.

Latest progress: the pre-mutation controller has a tested callback-reentrancy
guard; runtime-source extraction and Java override emission helpers have been
added. These helpers are not yet wired into generation. Runtime-source tests
still lack a completed result, and the last full-suite result predates these
additions. See the [evidence and integration status](semgen-redefinitions-status.md).

Run each script via ScriptServer:
```
python3 ../ModelioSkill/skills/modelio/scripts/modelio-cli.py phase1_copy_skeleton_sysml.jy
```

## Initial assembly sequence: scripts 1–13

These are the scripts used to assemble and initially repair `reference/design`.
The numbering is historical, and this sequence is **not safe to replay wholesale**:
several scripts create components, members, associations, or generalizations
without checking whether they already exist. Run only the needed script against
the expected model state; do not interpret the list as an automated runner.

1. `phase1_copy_skeleton_sysml.jy`, `phase1_copy_skeleton_kerml.jy` — recreate the
   real nested package/class/enum tree (not flat), skip the 5 chevauchement
   source classes. Writes `class_map_sysml.json`/`class_map_kerml.json`.
2. `phase2_copy_members.jy` — attributes, operations, enum literals. Skips
   `Element.name` and `Element.elementId`, mapped respectively to native
   `ModelElement.Name` and the Modelio object UUID.
3. `phase3_generalizations_and_composed_attrs.jy` — restore all real
   generalizations from `reference/spec` into `reference/design`, idempotently.
   Despite its historical filename, the current script does not create
   composed delegation associations; patched SemGen handles the multiple
   inheritance output.
4. `phase4_associations.jy` — associations + ends, chevauchement redirects,
   and normative `AssociationEnd.isDerived` flags.
   **Sets `setTarget()` explicitly on each end** — without it the GUI shows
   `<no type>` everywhere even though owner/opposite/multiplicity are correct
   (`api-gotchas.md` Error 28).
5. `phase5_semgen_stereotypes.jy`, `phase5b_package_enum_stereotypes.jy`,
   `phase5c_remaining_tags.jy`, `phase5d_fix_and_members.jy` — `Metamodel` on
   both components, `Semantic`/`SemanticLinkMetaclass` on classes/packages/
   enums/attributes/association ends, boolean tags (empty-`TaggedValue`
   convention, confirmed against the real `archimate` metamodel).
6. `phase6_graft_points.jy` — graft the KerML root onto the current Modelio
   Java integration base (`EObject`/`MObject` through `KerMLModelElement`);
   new `SysMLProject extends AbstractProject`.
7. `phase7_final_verification.jy` — prints class/element counts for comparison
   and fails if either tree contains a live, unnamed `EnumerationLiteral`. It
   does **not** enforce an expected count delta; `EXPECTED_DELTA` is empty.
8. `phase8_fix_structural_node_abstract.jy` — one-time live repair removing
   `Semantic.structural.node` from the eight abstract metaclasses. The guard
   in `phase5d_fix_and_members.jy` prevents this from recurring on regeneration.
9. `phase9_copy_documentation.jy` — copy normative Modelio Notes from
   `reference/spec` to matching `reference/design` classes, attributes,
   association ends, operations, packages, and enumeration literals. It writes
   the registered `ModelerModule` `description` and `summary` NoteTypes, and
   adds the short element name as `summary` where that type is available. This
   matches the verified Analyst pattern (`Dictionary`: long description, then
   `Dictionary` summary) and is duplicate-free; repeated runs update the same
   typed notes without creating additional ones.
   10. `phase10_remove_kerml_model_element_duplicates.jy` — one-time live repair
      removing `KerMLModelElement.name` and `elementId`; Phase 2 prevents their
      recreation.
   11. `phase11_normalize_structural_nodes.jy` — keep exactly 28 persistence
      grains: `SysMLProject`, `Package`/`LibraryPackage`, and the 25 concrete
      `Definition` classes present in the design. Usages and implementation
      details remain embedded. Repeated no-op runs skip project save.
   12. `phase12_restore_derived_association_ends.jy` — restore 291 normative
      derived flags across 548 unambiguously matched association ends, leaving
      8 documented transform artifacts untouched. Repeated no-op runs skip save.
   13. `phase13_remove_non_spec_duplicates.jy` — incomplete cleanup attempt for
      `KerMLModelElement.annotation`, `KerMLModelElement.membership`, and
      `Redefinition.owningFeature`. It inspects owned UML attributes, whereas
      these residual roles are association ends. Its no-op did NOT prove their
      removal; they remain in the audited 4.0.05 output. Do not use this script
      as an association-cleanliness check. Review opposite roles before repair.

`phase1_verify.jy` and `verify_root_ancestry.jy` are standalone re-checks, safe
to run any time (read-only).

## History of targeted repairs: scripts 15–28

This is a chronological repair record, not a continuation of the assembly
sequence. Dates below are included only when recorded in
`semgen-redefinitions-status.md`; dates for scripts 15–23 were not found in the
workspace history. The filenames retain their legacy `phase` prefix.

| Script | Date recorded | Operation |
|---|---|---|
| 15 | Not recorded | Backfill opposite-end `Redefines` notes. |
| 16 | Not recorded | Revert same-class notes introduced by script 15. |
| 17 | Not recorded | Correct stale `Redefines` note references. |
| 18 | Not recorded | Copy `Element` documentation onto `KerMLModelElement`. |
| 19 | Not recorded | Backfill documented association-end descriptions in `reference/spec`. |
| 20 | Not recorded | Propagate association-end descriptions to `reference/design`. |
| 21 | Not recorded | Add explanatory prose alongside design redefinition notes. |
| 22 | Not recorded | Reapply same-class redefinition notes. |
| 23 | Not recorded | Backfill second-layer reciprocal notes. |
| 24 | 2026-09-26 | Record four redefinitions that cannot be expressed as generator directives; correct earlier redirects. |
| 25 | 2026-09-26 | Record two further unexpressible connection redefinitions. |
| 26 | 2026-09-26 | Revert five incorrect reciprocal notes from script 23. |
| 27 | 2026-09-26 | Correct six `Redefines` notes that should be `Subsets`. |
| 28 | 2026-09-26 | Add two missing composite marks to redefining association ends. |

Some scripts explicitly undo or correct earlier changes: 16 reverses part of
15; 24 corrects four references from 17; 26 reverts five notes from 23. Scripts
19–21 depend on `final_ownedend_fixes.json` in a user-specific temporary
directory, which is not tracked in this workspace. Review each script's
preconditions and transaction before running it; do not run all numbered
scripts in sequence.

`phase14_create_process_diagram.jy` creates a Modelio diagram for the original
1–13 assembly sequence only. It does not represent this repair history or
execute the scripts, and rerunning it creates more model elements.

## `archive/`

Superseded designs and one-off investigation/fix scripts, kept for history:
three abandoned Phase-3 secondary-axis designs (nested-flattened delegate,
then a shared Generalization-chain delegate hierarchy, then a plain composed
`Attribute` typed directly by the secondary class — all replaced by the
composed-`Association` version in the final
`phase3_generalizations_and_composed_attrs.jy`), plus every
`inspect_`/`probe_`/`check_`/`diagnose_`/`spotcheck_`/`test_` script used to
discover the real Modelio API along the way. Not part of the reusable
pipeline — API findings from them are already folded into
`ModelioSkill/skills/modelio/references/api-gotchas.md`.

## Known gaps (including release blockers)

- Attribute `Value` defaults are not fully resolved. The earlier blanket claim
   that the specifications contain no defaults was incorrect: redefinition
   examples include `isReference = true` and operator literals. Distinguish
   defaults from derived/fixed-value constraints using the normative source;
   do not invent values where none are specified. The current candidate rejects
   explicit changed defaults it cannot preserve.
- Redefinition adapters do not yet protect inherited and inverse mutation
   paths. The typed collection prototype is tested but not wired into generated
   accessors. See [current implementation status](semgen-redefinitions-status.md).
- Restoring association `isDerived` suppresses stored fields/descriptors, but
   the 4.0.05 Java audit still found calls to omitted descriptor getters. Derived
   computations and complete generated-code compilation remain release blockers.
- Association-end properties `structural.isToDelete`,
  `persistency.optional`, `Semantic.link.source`/`target` not set (the
   association-end tags remain lower-priority metadata; the old composed-
   Association secondary-axis recipe is no longer part of the active pipeline.
- Whether SemGen/JavaDesigner/reverse generation itself is scriptable from
  Jython (vs. GUI menu only) is untested.
- The composed-Association secondary-axis design remains only in the archive
   and decision history; patched SemGen now handles the real multiple
   generalizations.

## Cédric Marin review — model repairs and remaining generation work

- **Fixed live**: `phase5d_fix_and_members.jy` was setting `Semantic.structural.node`
  on all 171 design classes unconditionally, including the 8 abstract ones
  (`KerMLModelElement`, `Relationship`, `ConnectorAsUsage`, `ControlNode`,
  `LoopActionUsage`, `Expose`, `Import`, `InstantiationExpression`) — this is
  Cédric's "toutes les métaclasses sont flaguées {structural.node}" (every
  model element ends up in its own persisted file). The convention documented
  in point 6 ("jamais cochée sur une métaclasse abstraite") was never actually
  enforced by the script. Corrected live via `phase8_fix_structural_node_abstract.jy`
  (tag removed from the 8 abstract classes, verified 0/8 flagged afterward)
   and the pipeline script itself patched with the final 28-class whitelist.
- **Fixed live**: `KerMLModelElement.name` and `elementId` removed; native
   `ModelElement.Name` and the Modelio UUID are authoritative. The distinct
   KerML declared/short/qualified naming fields remain.
- **Model flags restored; generation incomplete**: 291 derived ends among
   548 unambiguous mappings; `ownedElement` is derived and `ownedRelationship`
   is stored. This does not implement the derived accessors or establish
   canonical storage for every subset/redefinition. The generated Java audit
   exposed remaining storage duplication and missing descriptor getters.

## Live repository safety

- Never call `projectService.saveProject()` after a no-op transaction. Phase 8
   now skips save when it removes no tag; Phases 11 and 12 do the same.
- A full Modeliotool restart requires interactive login and a slow
   `Modelio.All` mount. Do not treat these delays as a hang or probe the model
   while it is opening.
- After the 2026-09-22 cache collision, a full restart restored the fragment;
   targeted verification found the project clean and no new
   `RepositoryClosedException`/`DuplicateObjectException` in the log.

