import os
import re
import sys
from collections import defaultdict

API_ROOT = r"H:\src\modelio\modelio\sysml\sysml.metamodel.api\src"
NATIVE_ROOT = r"H:\src\modelio\modelio\core\core.metamodel.api\src"

IFACE_RE = re.compile(
    r"public\s+interface\s+(\w+)\s*(?:extends\s+([^{]+?))?\s*\{", re.S)
# return type + method name + params, ending with ';'
METHOD_RE = re.compile(
    r"^[ \t]*(?:public\s+|default\s+|static\s+)*"
    r"(?:<[^>]+>\s+)?"
    r"([\w.$]+(?:\s*<[^;{}]*?>)?(?:\s*\[\])?)\s+"
    r"(\w+)\s*\(([^)]*)\)\s*;",
    re.M)

STRIP_COMMENTS = re.compile(r"/\*.*?\*/|//[^\n]*", re.S)


def simple(t):
    t = t.strip()
    t = re.sub(r"\s+", "", t)
    t = t.split("<")[0]
    return t.split(".")[-1]


def param_sig(params):
    params = params.strip()
    if not params:
        return ""
    out = []
    depth = 0
    cur = ""
    for ch in params:
        if ch == "<":
            depth += 1
        elif ch == ">":
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur)
            cur = ""
        else:
            cur += ch
    out.append(cur)
    res = []
    for p in out:
        p = p.strip()
        if not p:
            continue
        toks = p.split()
        if len(toks) >= 2:
            res.append(simple(" ".join(toks[:-1])))
        else:
            res.append(simple(p))
    return ",".join(res)


def parse_dir(root):
    """name -> (extends list, {sig: (file, line)})"""
    out = {}
    for dirpath, _, files in os.walk(root):
        for fn in files:
            if not fn.endswith(".java"):
                continue
            path = os.path.join(dirpath, fn)
            try:
                with open(path, "r", encoding="utf-8", errors="replace") as f:
                    raw = f.read()
            except OSError:
                continue
            src = STRIP_COMMENTS.sub("", raw)
            m = IFACE_RE.search(src)
            if not m:
                continue
            name = m.group(1)
            parents = []
            if m.group(2):
                depth = 0
                cur = ""
                for ch in m.group(2):
                    if ch == "<":
                        depth += 1
                    elif ch == ">":
                        depth -= 1
                    if ch == "," and depth == 0:
                        parents.append(simple(cur))
                        cur = ""
                    else:
                        cur += ch
                if cur.strip():
                    parents.append(simple(cur))
            body = src[m.end():]
            methods = {}
            for mm in METHOD_RE.finditer(body):
                ret, mname, params = mm.group(1), mm.group(2), mm.group(3)
                if simple(ret) in ("return", "new"):
                    continue
                sig = "%s(%s)" % (mname, param_sig(params))
                line = raw.count("\n", 0, raw.find(mm.group(0).strip())) + 1 \
                    if mm.group(0).strip() in raw else 0
                methods[sig] = (path, line, simple(ret))
            out[name] = (parents, methods)
    return out


gen = parse_dir(API_ROOT)
native = parse_dir(NATIVE_ROOT)
print("generated interfaces: %d" % len(gen))
print("native interfaces   : %d" % len(native))

allifaces = {}
allifaces.update(native)
allifaces.update(gen)


def ancestors(name, seen=None):
    if seen is None:
        seen = set()
    for p in allifaces.get(name, ([], {}))[0]:
        if p in seen or p not in allifaces:
            continue
        seen.add(p)
        ancestors(p, seen)
    return seen


findings = []
for name in sorted(gen):
    parents, methods = gen[name]
    anc = ancestors(name)
    inherited = {}
    for a in anc:
        for sig, info in allifaces[a][1].items():
            inherited.setdefault(sig, a)
    for sig, info in sorted(methods.items()):
        if sig in inherited:
            src = inherited[sig]
            findings.append((name, sig, src, "native" if src in native else "generated"))

ACCESSOR_RE = re.compile(r"^(get|set|is)([A-Z]\w*)")


def prop_of(sig):
    m = ACCESSOR_RE.match(sig)
    if not m:
        return None
    p = m.group(2)
    if p.startswith("Is") and len(p) > 2 and p[2].isupper():
        p = p[2:]
    return p


print("")
print("=== members redeclared although already inherited: %d ===" % len(findings))

props = defaultdict(set)
ops = []
for name, sig, src, _ in findings:
    p = prop_of(sig)
    if p:
        props[(name, p, src)].add(sig)
    else:
        ops.append((name, sig, src))

print("")
print("--- A. duplicated PROPERTIES (real duplicate storage): %d ---"
      % len(props))
for (name, p, src) in sorted(props):
    print("  %-34s %-22s <- %s" % (name, p, src))

print("")
print("--- B. redeclared OPERATIONS (harmless, spec redefinitions): %d ---"
      % len(ops))
for name, sig, src in sorted(ops):
    print("  %-34s %-46s <- %s" % (name, sig, src))
