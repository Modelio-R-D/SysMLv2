import re

SPECS = {
    "kerml": r"c:\Users\jcadavid\OneDrive - LA POSTE GROUPE\SysMLv2\specs\kerml.txt",
    "sysml": r"c:\Users\jcadavid\OneDrive - LA POSTE GROUPE\SysMLv2\specs\sysml.txt",
}

# (metaclass, property) pairs found duplicated in the generated code
CASES = [
    ("AnnotatingElement", "annotation"),
    ("AttributeUsage", "isReference"),
    ("EventOccurrenceUsage", "isReference"),
    ("ReferenceUsage", "isReference"),
    ("CollectExpression", "operator"),
    ("FeatureChainExpression", "operator"),
    ("IndexExpression", "operator"),
    ("SelectExpression", "operator"),
    ("ConnectionDefinition", "isSufficient"),
    ("Connector", "association"),
    ("EndFeatureMembership", "ownedMemberFeature"),
    ("EnumerationDefinition", "isVariation"),
    ("Expose", "visibility"),
    ("Expose", "isImportAll"),
    ("FramedConcernMembership", "kind"),
    ("RequirementVerificationMembership", "kind"),
    ("Namespace", "membership"),
    ("Redefinition", "owningFeature"),
]

text = {}
lines = {}
for k, p in SPECS.items():
    with open(p, "r", encoding="utf-8", errors="replace") as f:
        t = f.read()
    text[k] = t
    lines[k] = t.split("\n")

# lines that declare a redefinition of the property
RED = "{{redefines {p}}}"

print("%-36s %-20s %s" % ("METACLASS", "PROPERTY", "VERDICT"))
print("-" * 92)

for cls, prop in CASES:
    hits = []
    for k in SPECS:
        pat = re.compile(r"redefines\s+" + re.escape(prop) + r"\b")
        for i, ln in enumerate(lines[k]):
            if pat.search(ln):
                # look for the class name within a +/- 6 line window
                lo = max(0, i - 6)
                hi = min(len(lines[k]), i + 7)
                window = "\n".join(lines[k][lo:hi])
                near = re.search(r"\b" + re.escape(cls) + r"\b", window)
                hits.append((k, i + 1, bool(near), lines[k][i].strip()[:90]))

    near_hits = [h for h in hits if h[2]]
    any_red = len(hits) > 0

    if near_hits:
        verdict = "REDEFINITION (class found near)"
    elif any_red:
        verdict = "redefines exists for prop, class NOT near (%d hits)" % len(hits)
    else:
        verdict = "NO 'redefines' found -> likely genuine new attribute"

    print("%-36s %-20s %s" % (cls, prop, verdict))
    for k, ln, near, txt in near_hits[:2]:
        print("%-57s %s:%d  %s" % ("", k, ln, txt))
