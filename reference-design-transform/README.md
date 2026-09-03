# reference/spec → reference/design transformation scripts

Builds `reference/design` (SemGen-ready) from `reference/spec` (pure UML fidelity
mirror, untouched) in the live `sysml2` Modelio project. See
`deck-implementation-plan/points-a-trancher.md` (points 1–6 and "Points ouverts")
for the full design rationale.

Run each script via ScriptServer:
```
python3 ../ModelioSkill/skills/modelio/scripts/modelio-cli.py phase1_copy_skeleton_sysml.jy
```

## Pipeline, in order

1. `phase1_copy_skeleton_sysml.jy`, `phase1_copy_skeleton_kerml.jy` — recreate the
   real nested package/class/enum tree (not flat), skip the 5 chevauchement
   source classes. Writes `class_map_sysml.json`/`class_map_kerml.json`.
2. `phase2_copy_members.jy` — attributes, operations, enum literals.
3. `phase3_generalizations_and_composed_attrs.jy` — real generalizations for all
   classes (single parent each); for the 32 multi-inheritance cases, a plain
   composed `Attribute` on the primary typed directly by the real secondary
   class (no synthetic delegate class — see point 5), each annotated with a
   traceability `Note`.
4. `phase4_associations.jy` — associations + ends, chevauchement redirects.
   **Sets `setTarget()` explicitly on each end** — without it the GUI shows
   `<no type>` everywhere even though owner/opposite/multiplicity are correct
   (`api-gotchas.md` Error 28).
5. `phase5_semgen_stereotypes.jy`, `phase5b_package_enum_stereotypes.jy`,
   `phase5c_remaining_tags.jy`, `phase5d_fix_and_members.jy` — `Metamodel` on
   both components, `Semantic`/`SemanticLinkMetaclass` on classes/packages/
   enums/attributes/association ends, boolean tags (empty-`TaggedValue`
   convention, confirmed against the real `archimate` metamodel).
6. `phase6_graft_points.jy` — `Element` → `KerMLModelElement extends ModelElement`;
   new `SysMLProject extends AbstractProject`.
7. `phase7_final_verification.jy` — full count comparison against `reference/spec`
   with the documented expected delta.

`phase1_verify.jy` and `verify_root_ancestry.jy` are standalone re-checks, safe
to run any time (read-only).

## `archive/`

Superseded designs and one-off investigation/fix scripts, kept for history:
two abandoned Phase-3 delegate designs (nested-flattened, then a shared
Generalization-chain hierarchy — both replaced by the direct-typed composed
attribute in the final `phase3_generalizations_and_composed_attrs.jy`), plus
every `inspect_`/`probe_`/`check_`/`diagnose_`/`spotcheck_`/`test_` script used
to discover the real Modelio API along the way. Not part of the reusable
pipeline — API findings from them are already folded into
`ModelioSkill/skills/modelio/references/api-gotchas.md`.

## Known gaps (don't block generation — see `points-a-trancher.md`)

- Attribute type-constraint tag (`PropertyType`) / `Value` defaults not set.
- Association-end properties (`structural.partOf`/`isToDelete`,
  `persistency.optional`, `Semantic.link.source`/`target`) not set — needs a
  per-association aggregation-kind pass.
- Whether SemGen/JavaDesigner/reverse generation itself is scriptable from
  Jython (vs. GUI menu only) is untested.
