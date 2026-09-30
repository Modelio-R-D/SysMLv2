"""
Dry run of SemGen's property-redefinition preflight against the live reference/design model.

WHY THIS EXISTS
    SemGen's preflight runs over every metaclass before the generation transaction opens, and any
    metadata defect aborts the whole run. Without this script the only way to find defects is to run a
    generation, read the one error it reports, fix it, and run again -- one defect per run, each run
    costing a full Modelio generation. This finds them all in a single pass.

    It is what caught CrossSubsetting.crossingFeature, ReferenceSubsetting.referencingFeature and
    Flow.interaction together (2026-09-26), after the first real run aborted on the first of them.

RUN IT
    python3 reference-design-transform/preflight_dryrun.py
    Needs Modelio running with the ScriptServer module on port 9999 and the sysml2 project open.
    Read-only: it opens no transaction and changes nothing.

WHAT IT MIRRORS  (com.modeliosoft.tools.semgen.utils.PropertyRedefinition)
    canonical()                       -> MALFORMED / UNRESOLVED / AMBIGUOUS / CYCLE / MERGES   [HARD]
    storedEnds/storedAttributes       -> storage-name COLLISION, SHADOWS inherited name        [HARD]
    associationStorage/attributeStorage shape checks                                           [soft]

    Degradation follows the same rule as the generator: a property that cannot reach its full canonical
    storage settles on the FURTHEST ancestor along its declared chain that it can still share safely,
    not on itself at the first failure. Only properties that end up on a slot of their own ("OWN SLOT")
    are genuinely duplicated members; "PARTIAL" ones are still deduplicated, just not all the way.

READING THE OUTPUT
    HARD DEFECTS must be zero. Anything listed there will abort the next generation run, and the
    message says which property and why.
    NOT FULLY DEDUPLICATED is expected to be non-empty; see WIP-2026-09-27-semgen-redefinitions-status.md for the
    current list and why each one is there.

KEEPING IT HONEST
    This is a reimplementation, so it can drift from the Java. Two deviations have already bitten:
      - it once followed each declaration only one hop instead of the whole chain, and so missed the
        merge defect that aborted the first run;
      - it once used the tolerant resolution for opposite ends, where the Java uses the strict
        canonical, which made two functions mutually recursive and blew the stack.
    If it and a real run ever disagree, trust the run and fix this file.
"""
import sys
sys.path.insert(0, r"C:\Users\jcadavid\OneDrive - LA POSTE GROUPE\SysMLv2\ModelioSkill\skills\modelio\scripts")
from core import send_to_scriptserver

jy = r'''
import re

DECLARATION = re.compile(r"Redefines \(per normative XMI\):\s*([^<\r\n]+)")
REFERENCE = re.compile(r"([A-Za-z_][\w]*)\.([A-Za-z_][\w]*)")
GAP = re.compile(r"^[\s,;]*$")
TAIL = re.compile(r"^[\s,;.]*$")

def find_child(el, name):
    for c in el.getCompositionChildren():
        if c.getName() == name:
            return c
    return None

sysml2Root = None
for root in modelingSession.getModel().getModelRoots():
    if root.getName() == "sysml2":
        sysml2Root = root
        break
pkgRoot = find_child(sysml2Root, "modelio.sysml")
refPkg = find_child(pkgRoot, "reference")
designPkg = find_child(refPkg, "design")

mmExt = modelingSession.getMetamodelExtensions()
_noteCache = {}

def desc(element):
    key = str(element.getUuid())
    if key in _noteCache:
        return _noteCache[key]
    value = None
    for nt in mmExt.findNoteTypes("", element.getMClass()):
        if nt.getName().lower() == "description":
            note = element.getNote(nt)
            value = note.getContent() if note else None
            break
    _noteCache[key] = value
    return value

classes = []
def collect(pkg, depth=0):
    if depth > 60:
        return
    for c in pkg.getCompositionChildren():
        try:
            if c.getMClass().getName() == "Class":
                classes.append(c)
        except:
            pass
        collect(c, depth + 1)
collect(designPkg)

def parents(cls):
    return [g.getSuperType() for g in cls.getParent() if g.getSuperType() is not None]

def uid(e):
    return str(e.getUuid())

def label(p):
    o = p.getCompositionOwner()
    return "%s.%s" % (o.getName() if o is not None else "?", p.getName())

HARD = []
SOFT = []

def resolve(prop, className, propName, isAttr):
    owner = prop.getCompositionOwner()
    pending = [owner]
    visited = []
    seen = set()
    matches = []
    while pending:
        anc = pending.pop(0)
        if uid(anc) in seen:
            continue
        seen.add(uid(anc))
        visited.append(anc)
        if anc.getName() == className:
            for m in (anc.getOwnedAttribute() if isAttr else anc.getOwnedEnd()):
                if m.getName() == propName and not m.equals(prop):
                    matches.append(m)
        pending.extend(parents(anc))
    if len(matches) == 0:
        raise ValueError("UNRESOLVED|%s names %s.%s, absent from its ancestry (%s)" % (
            label(prop), className, propName, ", ".join([a.getName() for a in visited[:12]])))
    if len(matches) > 1:
        raise ValueError("AMBIGUOUS|%s names %s.%s, matching %d (%s)" % (
            label(prop), className, propName, len(matches), ", ".join([label(m) for m in matches])))
    return matches[0]

def declaredParents(prop, isAttr):
    description = desc(prop)
    if not description:
        return []
    out = []
    for m in DECLARATION.finditer(description):
        references = m.group(1).strip()
        end = 0
        found = False
        for r in REFERENCE.finditer(references):
            gap = references[end:r.start()]
            if not GAP.match(gap):
                raise ValueError("MALFORMED|%s: cannot read %r; problem at %r" % (label(prop), references, gap.strip()))
            end = r.end()
            found = True
            out.append(("%s.%s" % (r.group(1), r.group(2)), resolve(prop, r.group(1), r.group(2), isAttr)))
        if not found:
            raise ValueError("MALFORMED|%s: no Class.property reference in %r" % (label(prop), references))
        if not TAIL.match(references[end:]):
            raise ValueError("MALFORMED|%s: trailing text %r in %r" % (label(prop), references[end:].strip(), references))
    return out

def canonical(prop, isAttr, path=None):
    if path is None:
        path = []
    if uid(prop) in [uid(p) for p in path]:
        raise ValueError("CYCLE|%s; cycle: %s" % (label(prop), " -> ".join([label(p) for p in path] + [label(prop)])))
    path = path + [prop]
    canon = None
    canonSource = None
    for refText, parent in declaredParents(prop, isAttr):
        cand = canonical(parent, isAttr, path)
        if canon is not None and not canon.equals(cand):
            raise ValueError("MERGES|%s redefines both %s (storage %s) and %s (storage %s)" % (
                label(prop), canonSource, label(canon), refText, label(cand)))
        canon = cand
        canonSource = refText
    return prop if canon is None else canon

def bound(b):
    return -1 if b == "*" else int(b)

def isNarrowingType(a, b):
    if a is None or b is None:
        return False
    if a.equals(b):
        return True
    pending = parents(a)
    seen = set([uid(a)])
    while pending:
        anc = pending.pop(0)
        if uid(anc) in seen:
            continue
        seen.add(uid(anc))
        if anc.equals(b):
            return True
        pending.extend(parents(anc))
    return False

def softReason(prop, storage, isAttr):
    if storage.equals(prop):
        return None
    if isAttr:
        if (str(prop.getType()) != str(storage.getType())
                or prop.getMultiplicityMin() != storage.getMultiplicityMin()
                or prop.getMultiplicityMax() != storage.getMultiplicityMax()):
            return "attribute shape differs from storage"
        return None
    if prop.getTarget() is None:
        return "no target type"
    if storage.getOpposite() is None:
        return "storage %s has no opposite" % label(storage)
    if not storage.isNavigable():
        return "storage %s is not navigable" % label(storage)
    if str(prop.getAggregation()) != str(storage.getAggregation()):
        return "aggregation %s vs storage %s" % (prop.getAggregation(), storage.getAggregation())
    # Matches Java's unsafeAssociationReason: the opposites are compared at the CANONICAL level, not the
    # tolerant one. Using the tolerant resolution here would make storageOrSelf and softReason mutually
    # recursive through the opposite chain.
    po = canonical(prop.getOpposite(), isAttr) if prop.getOpposite() is not None else None
    so = canonical(storage.getOpposite(), isAttr) if storage.getOpposite() is not None else None
    if (po is None) != (so is None) or (po is not None and not po.equals(so)):
        return "opposite %s resolves to %s, storage's opposite %s resolves to %s" % (
            label(prop.getOpposite()), label(po) if po else None,
            label(storage.getOpposite()), label(so) if so else None)
    if not isNarrowingType(prop.getTarget(), storage.getTarget()):
        return "target %s not a subtype of storage target %s" % (
            prop.getTarget().getName(), storage.getTarget().getName())
    if bound(prop.getMultiplicityMin()) < bound(storage.getMultiplicityMin()):
        return "multiplicity min below storage's"
    sMax = bound(storage.getMultiplicityMax())
    if sMax != -1:
        pMax = bound(prop.getMultiplicityMax())
        if pMax == -1 or pMax > sMax:
            return "multiplicity max above storage's"
    return None

_storageCache = {}

def storageOrSelf(prop, isAttr, path=None):
    if path is None:
        path = []
    key = uid(prop)
    if key in _storageCache:
        return _storageCache[key]
    if key in [uid(p) for p in path]:
        return prop
    declared = declaredParents(prop, isAttr)
    if not declared:
        _storageCache[key] = prop
        return prop
    parentStorage = storageOrSelf(declared[0][1], isAttr, path + [prop])
    if parentStorage.equals(prop):
        result = prop
    elif softReason(prop, parentStorage, isAttr) is None:
        result = parentStorage
    else:
        result = prop
    _storageCache[key] = result
    return result

checked = 0
for cls in classes:
    for isAttr, members in ((True, cls.getOwnedAttribute()), (False, cls.getOwnedEnd())):
        for prop in members:
            if not isAttr and not prop.isNavigable():
                continue
            checked += 1
            try:
                canon = canonical(prop, isAttr)
                actual = storageOrSelf(prop, isAttr)
                if not actual.equals(canon):
                    if actual.equals(prop):
                        SOFT.append("OWN SLOT   %s (wanted %s)" % (label(prop), label(canon)))
                    else:
                        SOFT.append("PARTIAL    %s -> %s (wanted %s)" % (label(prop), label(actual), label(canon)))
            except ValueError, e:
                HARD.append(str(e))
            except Exception, e:
                HARD.append("ERROR|%s: %s" % (label(prop), e))

def primaryAncestors(cls):
    out = []
    p = parents(cls)
    pending = [p[0]] if p else []
    seen = set()
    while pending:
        anc = pending.pop(0)
        if uid(anc) in seen:
            continue
        seen.add(uid(anc))
        out.append(anc)
        pending.extend(parents(anc))
    return out

def secondaryAncestors(cls):
    out = []
    seen = set(uid(a) for a in primaryAncestors(cls))
    seen.add(uid(cls))
    pending = parents(cls)[1:]
    while pending:
        anc = pending.pop(0)
        if uid(anc) in seen:
            continue
        seen.add(uid(anc))
        out.append(anc)
        pending.extend(parents(anc))
    return out

for cls in classes:
    for isAttr in (True, False):
        try:
            inherited = {}
            for anc in primaryAncestors(cls):
                for p in (anc.getOwnedAttribute() if isAttr else anc.getOwnedEnd()):
                    if not isAttr and not p.isNavigable():
                        continue
                    st = storageOrSelf(p, isAttr)
                    inherited[uid(st)] = st
            candidates = list(cls.getOwnedAttribute() if isAttr else cls.getOwnedEnd())
            for sec in secondaryAncestors(cls):
                candidates.extend(sec.getOwnedAttribute() if isAttr else sec.getOwnedEnd())
            result = {}
            for p in candidates:
                if not isAttr and not p.isNavigable():
                    continue
                st = storageOrSelf(p, isAttr)
                if uid(st) in inherited:
                    continue
                name = st.getName()
                if name in result and not result[name].equals(st):
                    HARD.append("COLLISION|%s: %s and %s both want slot %r (second via %s)" % (
                        cls.getName(), label(result[name]), label(st), name, label(p)))
                else:
                    result[name] = st
                for ist in inherited.values():
                    if ist.getName() == name:
                        HARD.append("SHADOWS|%s: %s needs slot %r, already inherited from %s" % (
                            cls.getName(), label(p), name, label(ist)))
        except ValueError, e:
            pass
        except Exception, e:
            HARD.append("ERROR|%s (collision pass): %s" % (cls.getName(), e))

print "classes scanned:", len(classes)
print "properties checked:", checked
print ""
print "HARD DEFECTS (abort generation):", len(set(HARD))
for d in sorted(set(HARD)):
    kind, rest = d.split("|", 1)
    print "  [%s] %s" % (kind, rest)
print ""
print "NOT FULLY DEDUPLICATED:", len(set(SOFT))
for s in sorted(set(SOFT)):
    print "  %s" % s
print "DONE"
'''

print(send_to_scriptserver(jy, timeout=600))
