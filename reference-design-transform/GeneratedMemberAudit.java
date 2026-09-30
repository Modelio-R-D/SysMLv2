import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Deque;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;
import java.util.TreeSet;
import java.util.regex.Pattern;

import javax.lang.model.element.Modifier;
import javax.tools.Diagnostic;
import javax.tools.DiagnosticCollector;
import javax.tools.JavaCompiler;
import javax.tools.JavaFileObject;
import javax.tools.StandardJavaFileManager;
import javax.tools.ToolProvider;

import com.sun.source.tree.AnnotatedTypeTree;
import com.sun.source.tree.ArrayTypeTree;
import com.sun.source.tree.ClassTree;
import com.sun.source.tree.CompilationUnitTree;
import com.sun.source.tree.ExpressionTree;
import com.sun.source.tree.ImportTree;
import com.sun.source.tree.LiteralTree;
import com.sun.source.tree.MemberSelectTree;
import com.sun.source.tree.MethodInvocationTree;
import com.sun.source.tree.MethodTree;
import com.sun.source.tree.ParameterizedTypeTree;
import com.sun.source.tree.ParenthesizedTree;
import com.sun.source.tree.ReturnTree;
import com.sun.source.tree.Tree;
import com.sun.source.tree.TypeCastTree;
import com.sun.source.tree.TypeParameterTree;
import com.sun.source.tree.VariableTree;
import com.sun.source.util.JavacTask;
import com.sun.source.util.TreeScanner;
import com.sun.source.util.Trees;

public class GeneratedMemberAudit {
    record Member(String name, String type, String location, Set<Modifier> flags) {}
    record DependencyCall(String owner, String target, String method, String location) {}
    static class TypeInfo {
        String name;
        String packageName;
        String location;
        boolean generated;
        boolean api;
        List<String> parents = new ArrayList<>();
        Map<String, String> imports = new HashMap<>();
        List<String> wildcardImports = new ArrayList<>();
        List<Member> fields = new ArrayList<>();
        List<Member> methods = new ArrayList<>();
    }
    static final Map<String, TypeInfo> types = new LinkedHashMap<>();
    static final Map<String, Integer> counts = new TreeMap<>();
    static final Map<String, Integer> versions = new TreeMap<>();
    static final Set<String> cmsNodes = new TreeSet<>();
    static final Set<String> unresolvedParents = new TreeSet<>();
    static final List<String> findings = new ArrayList<>();
    static final List<DependencyCall> dependencyCalls = new ArrayList<>();

    static void report(String category, String detail) {
        counts.merge(category, 1, Integer::sum);
        findings.add(category + "\t" + detail);
    }

    static String erase(Tree tree) {
        if (tree == null) return "void";
        if (tree instanceof ParameterizedTypeTree parameterized) return erase(parameterized.getType());
        if (tree instanceof ArrayTypeTree array) return erase(array.getType()) + "[]";
        if (tree instanceof AnnotatedTypeTree annotated) return erase(annotated.getUnderlyingType());
        return tree.toString();
    }

    static String resolve(String name, TypeInfo owner) {
        if (name.endsWith("[]")) return resolve(name.substring(0, name.length() - 2), owner) + "[]";
        if (owner.imports.containsKey(name)) return owner.imports.get(name);
        if (types.containsKey(owner.packageName + "." + name)) return owner.packageName + "." + name;
        for (String prefix : owner.wildcardImports) {
            if (types.containsKey(prefix + "." + name)) return prefix + "." + name;
        }
        if (Set.of("Object", "String", "Class", "Boolean", "Integer", "Long", "Double").contains(name)) {
            return "java.lang." + name;
        }
        return name;
    }

    static String signature(Member method, TypeInfo owner) {
        return method.name() + "(" + Arrays.stream(method.type().split(","))
                .filter(type -> !type.isEmpty()).map(type -> resolve(type, owner))
                .reduce((left, right) -> left + "," + right).orElse("") + ")";
    }

    static List<TypeInfo> ancestors(TypeInfo owner) {
        List<TypeInfo> result = new ArrayList<>();
        Set<String> seen = new HashSet<>();
        Deque<TypeInfo> pending = new ArrayDeque<>();
        pending.add(owner);
        while (!pending.isEmpty()) {
            TypeInfo current = pending.removeFirst();
            for (String parent : current.parents) {
                String qualified = resolve(parent, current);
                if (!seen.add(qualified)) continue;
                TypeInfo resolved = types.get(qualified);
                if (resolved == null) {
                    unresolvedParents.add(qualified);
                } else {
                    result.add(resolved);
                    pending.addLast(resolved);
                }
            }
        }
        return result;
    }

    public static void main(String[] args) throws Exception {
        if (args.length < 2) throw new IllegalArgumentException("Usage: java GeneratedMemberAudit.java API_SRC IMPL_SRC [REFERENCE_SRC ...]");
        JavaCompiler compiler = ToolProvider.getSystemJavaCompiler();
        DiagnosticCollector<JavaFileObject> diagnostics = new DiagnosticCollector<>();
        List<Path> paths = new ArrayList<>();
        Path apiRoot = Path.of(args[0]).toAbsolutePath().normalize();
        Path implRoot = Path.of(args[1]).toAbsolutePath().normalize();
        for (String root : args) {
            try (var walk = Files.walk(Path.of(root))) {
                paths.addAll(walk.filter(path -> path.toString().endsWith(".java")).sorted().toList());
            }
        }
        int generatedFiles = 0;
        try (StandardJavaFileManager manager = compiler.getStandardFileManager(diagnostics, null, java.nio.charset.StandardCharsets.UTF_8)) {
            JavacTask task = (JavacTask) compiler.getTask(null, manager, diagnostics,
                    List.of("-proc:none"), null, manager.getJavaFileObjectsFromPaths(paths));
            Trees trees = Trees.instance(task);
            for (CompilationUnitTree unit : task.parse()) {
                Path path = Path.of(unit.getSourceFile().toUri()).toAbsolutePath().normalize();
                boolean generated = path.startsWith(apiRoot) || path.startsWith(implRoot);
                String source = unit.getSourceFile().getCharContent(true).toString();
                if (generated) {
                    generatedFiles++;
                    var version = Pattern.compile("Generator version:\\s*(\\S+)").matcher(source);
                    versions.merge(version.find() ? version.group(1) : "NO_HEADER", 1, Integer::sum);
                }
                new TreeScanner<Void, String>() {
                    String location(Tree tree) {
                        return path + ":" + unit.getLineMap().getLineNumber(trees.getSourcePositions().getStartPosition(unit, tree));
                    }

                    @Override public Void visitClass(ClassTree declaration, String enclosing) {
                        if (declaration.getSimpleName().isEmpty()) return null;
                        TypeInfo info = new TypeInfo();
                        info.packageName = unit.getPackageName().toString();
                        info.name = (enclosing == null ? info.packageName : enclosing) + "." + declaration.getSimpleName();
                        info.location = location(declaration);
                        info.generated = generated;
                        info.api = path.startsWith(apiRoot) && declaration.getKind() == Tree.Kind.INTERFACE;
                        for (ImportTree imported : unit.getImports()) {
                            if (imported.isStatic()) continue;
                            String importedName = imported.getQualifiedIdentifier().toString();
                            if (importedName.endsWith(".*")) info.wildcardImports.add(importedName.substring(0, importedName.length() - 2));
                            else info.imports.put(importedName.substring(importedName.lastIndexOf('.') + 1), importedName);
                        }
                        if (declaration.getExtendsClause() != null) info.parents.add(erase(declaration.getExtendsClause()));
                        declaration.getImplementsClause().forEach(parent -> info.parents.add(erase(parent)));
                        for (Tree member : declaration.getMembers()) {
                            if (member instanceof VariableTree field) {
                                info.fields.add(new Member(field.getName().toString(), erase(field.getType()), location(field), field.getModifiers().getFlags()));
                            } else if (member instanceof MethodTree method) {
                                Map<String, String> variables = new HashMap<>();
                                List<TypeParameterTree> parameters = new ArrayList<>(declaration.getTypeParameters());
                                parameters.addAll(method.getTypeParameters());
                                for (TypeParameterTree parameter : parameters) {
                                    variables.put(parameter.getName().toString(), parameter.getBounds().isEmpty() ? "Object" : erase(parameter.getBounds().get(0)));
                                }
                                List<String> parameterTypes = method.getParameters().stream().map(parameter -> {
                                    String type = erase(parameter.getType());
                                    return variables.getOrDefault(type, type);
                                }).toList();
                                info.methods.add(new Member(method.getName().toString(), String.join(",", parameterTypes), location(method), method.getModifiers().getFlags()));
                                if (generated && method.getBody() != null) {
                                    new TreeScanner<Void, Void>() {
                                        @Override public Void visitMethodInvocation(MethodInvocationTree invocation, Void unused) {
                                            if (invocation.getArguments().isEmpty() && invocation.getMethodSelect() instanceof MemberSelectTree selected
                                                    && selected.getIdentifier().toString().matches("get.+Dep")) {
                                                ExpressionTree receiver = selected.getExpression();
                                                while (receiver instanceof ParenthesizedTree wrapped) receiver = wrapped.getExpression();
                                                if (receiver instanceof TypeCastTree cast) {
                                                    dependencyCalls.add(new DependencyCall(info.name, erase(cast.getType()),
                                                            selected.getIdentifier().toString(), location(invocation)));
                                                }
                                            }
                                            return super.visitMethodInvocation(invocation, unused);
                                        }
                                    }.scan(method.getBody(), null);
                                }
                                if (generated && method.getName().contentEquals("isCmsNode") && method.getBody() != null
                                        && method.getBody().getStatements().stream().anyMatch(statement -> statement instanceof ReturnTree returned
                                        && returned.getExpression() instanceof LiteralTree literal && Boolean.TRUE.equals(literal.getValue()))) {
                                    cmsNodes.add(info.name);
                                }
                            }
                        }
                        TypeInfo previous = types.put(info.name, info);
                        if (previous != null && generated) report("DUPLICATE_TYPE", info.location + " " + info.name + " previous=" + previous.location);
                        for (Tree member : declaration.getMembers()) {
                            if (member instanceof ClassTree nested) visitClass(nested, info.name);
                        }
                        return null;
                    }
                }.scan(unit, null);
            }
        }
        for (Diagnostic<? extends JavaFileObject> diagnostic : diagnostics.getDiagnostics()) {
            if (diagnostic.getKind() == Diagnostic.Kind.ERROR) report("PARSE_ERROR", diagnostic.toString());
        }
        for (TypeInfo info : types.values()) {
            if (!info.generated) continue;
            Map<String, Member> ownFields = new HashMap<>();
            for (Member field : info.fields) {
                Member previous = ownFields.put(field.name(), field);
                if (previous != null) report("DUPLICATE_FIELD", field.location() + " " + field.name() + " previous=" + previous.location());
            }
            Map<String, Member> ownMethods = new HashMap<>();
            for (Member method : info.methods) {
                Member previous = ownMethods.put(signature(method, info), method);
                if (previous != null) report("DUPLICATE_METHOD", method.location() + " " + signature(method, info) + " previous=" + previous.location());
            }
            List<TypeInfo> parents = ancestors(info);
            if (info.name.endsWith("Data")) {
                for (Member field : info.fields) {
                    if (field.flags().contains(Modifier.STATIC)) continue;
                    for (TypeInfo parent : parents) {
                        for (Member inherited : parent.fields) {
                            if (field.name().equals(inherited.name()) && !inherited.flags().contains(Modifier.STATIC)) {
                                report("DUPLICATE_STORAGE", field.location() + " " + info.name + "." + field.name() + " inherited=" + inherited.location());
                            }
                        }
                    }
                }
            }
            if (info.api) {
                for (Member method : info.methods) {
                    if (method.flags().contains(Modifier.STATIC) || method.flags().contains(Modifier.PRIVATE)) continue;
                    String key = signature(method, info);
                    boolean found = false;
                    for (TypeInfo parent : parents) {
                        for (Member inherited : parent.methods) {
                            if (key.equals(signature(inherited, parent))) {
                                report("API_REDECLARATION", method.location() + " " + info.name + "." + key + " inherited=" + inherited.location());
                                found = true;
                                break;
                            }
                        }
                        if (found) break;
                    }
                }
            }
        }
        Set<String> missingDependencies = new TreeSet<>();
        for (DependencyCall call : dependencyCalls) {
            TypeInfo owner = types.get(call.owner());
            TypeInfo target = types.get(resolve(call.target(), owner));
            if (target == null || !target.generated) continue;
            List<TypeInfo> search = new ArrayList<>(ancestors(target));
            search.add(target);
            boolean exists = search.stream().flatMap(type -> type.methods.stream())
                    .anyMatch(method -> method.name().equals(call.method()) && method.type().isEmpty());
            if (!exists) {
                missingDependencies.add(target.name + "." + call.method());
                report("MISSING_DEP_ACCESSOR", call.location() + " " + target.name + "." + call.method() + "() target=" + target.location);
            }
        }
        System.out.println("MISSING_DEPENDENCY_METHODS=" + missingDependencies.size());
        System.out.println("GENERATED_FILES=" + generatedFiles);
        System.out.println("PARSED_TYPES=" + types.size());
        System.out.println("GENERATOR_HEADERS=" + versions);
        System.out.println("COUNTS=" + counts);
        System.out.println("CMS_NODES=" + cmsNodes.size() + " " + cmsNodes);
        System.out.println("UNRESOLVED_PARENTS=" + unresolvedParents);
        findings.forEach(System.out::println);
        if (counts.containsKey("PARSE_ERROR")) System.exit(2);
    }
}