# Correctif SemGen — héritage multiple : changements réels et build

Référence technique du correctif décidé et suivi dans `limitation-heritage-multiple-semgen.md` (section « Statut » — lire ce document pour le contexte, la décision et les réserves de Cédric). Ici : le code réellement modifié, lu directement depuis le checkout SemGen sur ce poste (`H:\modelio\work\eclipse\modules\SemGen`, accessible en lecture directe depuis ce workspace — pas seulement rapporté par échange de messages avec l'autre session), et l'artefact construit.

Correctif mené par une session Claude Code distincte, dans le dépôt SemGen lui-même — pas dans ce workspace de transformation du modèle.

---

## 1. Artefact construit

| | |
|---|---|
| Fichier | `H:\modelio\work\eclipse\modules\SemGen\target\SemGen_4.0.02.jmdac` |
| Module id / classe | `SemGen` / `com.modeliosoft.tools.semgen.impl.SemGenMdac` (`module.xml`) |
| Version module / binaryversion | `4.0.00` / `6.2.0` |
| uid | `ca5bf67e-736b-4202-844d-9d3a867b2182` |
| Classpath embarqué | `lib/semgen-4.0.00.jar`, `lib/semgenerator-1.4.00.jar` |
| Build | Maven, JDK 21, contre `repository.modelio.org` — compile sans erreur |
| Construit le | 2026-09-10 |

**Pas encore installé ni testé contre une vraie instance Modelio.** Consigne d'Antonin : le premier test de régénération doit se faire dans un **projet local séparé**, pas dans le fragment SysML2 partagé de `modelio.all`.

---

## 2. Changement 1 — l'interface `mm.api` porte réellement l'héritage multiple

**Fichier** : `base/apigen/ApiGenerator.java`, méthode `doGenerateInheritance` (règle : la classe/l'interface `mm.api` d'une métaclasse à N parents directs doit `extends` les N interfaces `mm.api` correspondantes).

Avant (comportement d'origine, partagé avec les 6 autres générateurs listés dans `limitation-heritage-multiple-semgen.md` §5) : un seul appel à `createGeneralization`, sur `mmClass.getParent().get(0)` uniquement.

Après :

```java
protected void doGenerateInheritance(final MClassSet cs) {
    final GeneralClass mmClass = cs.getMmClass();

    // Enumeration are a special case
    if (mmClass instanceof Enumeration) {
        getCtx().getModel().createInterfaceRealization(cs.getEmfClass(), (Interface) getCtx().getType("Enumerator"));
        return;
    }

    final GeneralClass emfClass = cs.getEmfClass();
    final java.util.List<Generalization> parents = mmClass.getParent();

    if (parents.isEmpty()) {
        generateInheritanceLink(cs, emfClass, null);
        return;
    }

    for (final Generalization g : parents) {
        generateInheritanceLink(cs, emfClass, (Class) g.getSuperType());
    }
}

private void generateInheritanceLink(final MClassSet cs, final GeneralClass emfClass, final Class mmParentClass) {
    final GeneralClass mmClass = cs.getMmClass();

    MClassSet parentClassSet = null;
    if (mmParentClass == null || getCtx().getClassSet(mmParentClass) == null) {
        parentClassSet = getCtx().getDefaultRootClassSet();
        LOG.warning("%s: no parent class for %s, defaulting to defaulting to %s", getClass().getSimpleName(),
                mmClass.getName(), parentClassSet.getMmClass() != null ? parentClassSet.getMmClass().getName() : "unknown");
    } else {
        parentClassSet = getCtx().getClassSet(mmParentClass);
    }

    // Create Generalization XXX -> parent of(XXX) (interfaces)
    getCtx().getModel().createGeneralization(emfClass, parentClassSet.getEmfClass());

    // Hack: add MObject if defaulting to EObject
    if (parentClassSet.getEmfClass().equals(getCtx().getType("EObject"))) {
        getCtx().getModel().createGeneralization(emfClass, getCtx().getType("MObject"));
    }
}
```

Le corps de `generateInheritanceLink` reprend exactement l'ancienne logique à-un-seul-parent (résolution du `MClassSet` parent, warning si absent, hack `MObject`/`EObject`) — seule différence : elle est maintenant appelée une fois par parent au lieu d'une seule fois avec `getParent().get(0)`. `interface AttributeDefinition extends Definition, DataType` devient possible.

---

## 3. Changement 2 — nouvel utilitaire de mise à plat (`ModelUtils`)

**Fichier** : `utils/ModelUtils.java` (classe utilitaire existante, méthodes ajoutées — le reste du fichier, non listé ici, est inchangé).

### `getSecondaryAncestorsToFlatten`

Pour une métaclasse à N parents, retourne les classes ancêtres atteignables uniquement via les parents secondaires (index ≥ 1) — dédoublonnées contre la chaîne complète du parent primaire et entre elles :

```java
public static List<GeneralClass> getSecondaryAncestorsToFlatten(final GeneralClass mmClass) {
    final List<Generalization> parents = mmClass.getParent();
    final List<GeneralClass> result = new ArrayList<>();
    if (parents.size() <= 1) {
        return result;
    }

    final Set<GeneralClass> covered = new LinkedHashSet<>();
    covered.add(mmClass);
    final GeneralClass primary = (GeneralClass) parents.get(0).getSuperType();
    if (primary != null) {
        collectAncestorsInto(primary, covered);
    }

    final Set<GeneralClass> visited = new LinkedHashSet<>();
    for (int i = 1; i < parents.size(); i++) {
        final GeneralClass secondary = (GeneralClass) parents.get(i).getSuperType();
        if (secondary != null) {
            collectSecondaryAncestors(secondary, covered, visited, result);
        }
    }
    return result;
}
```

`collectAncestorsInto` (chaîne primaire, alimente `covered`) et `collectSecondaryAncestors` (chaîne(s) secondaire(s), alimente `result` en sautant tout ce qui est déjà dans `covered`) sont toutes deux **récursives** — répond au point de vigilance signalé : la chaîne complète des ancêtres secondaires est remontée, pas seulement les membres propres du parent secondaire direct. Gère aussi un parent primaire lui-même multi-parenté (la récursion suit tous les `getParent()` rencontrés, pas un seul niveau).

### `getFlattenedOwnedAttributes` / `getFlattenedOwnedEnds`

Combinent les membres propres de la classe avec ceux de chaque ancêtre secondaire, en ignorant (et journalisant) toute collision de nom plutôt que de produire un doublon silencieusement cassé :

```java
public static List<Attribute> getFlattenedOwnedAttributes(final GeneralClass mmClass) {
    final List<Attribute> result = new ArrayList<>(mmClass.getOwnedAttribute());
    final Set<String> seenNames = new HashSet<>();
    for (final Attribute a : result) {
        seenNames.add(a.getName());
    }
    for (final GeneralClass anc : getSecondaryAncestorsToFlatten(mmClass)) {
        for (final Attribute a : anc.getOwnedAttribute()) {
            if (!seenNames.add(a.getName())) {
                LOG.warning("Flattened inheritance: '%s' already has an attribute named '%s'; skipping the one from secondary parent branch '%s'.",
                        mmClass.getName(), a.getName(), anc.getName());
                continue;
            }
            result.add(a);
        }
    }
    return result;
}
```

`getFlattenedOwnedEnds` est la même logique pour les `AssociationEnd`. **Traitement des collisions : ignorer + avertir, pas une vraie résolution** — un membre secondaire en collision de nom n'est simplement pas émis (le membre déjà présent, primaire ou d'un ancêtre secondaire précédent, gagne). Aucune collision connue parmi les 34 cas à ce jour, mais non vérifié systématiquement.

---

## 4. Changement 3 — 9 points d'appel élargis, dans 7 fichiers

Chaque générateur qui énumérait auparavant `mmClass.getOwnedAttribute()`/`getOwnedEnd()` (membres propres seulement) appelle maintenant `ModelUtils.getFlattenedOwnedAttributes(...)`/`getFlattenedOwnedEnds(...)` :

| Fichier | Méthode | Couche | Ce que ça émet |
|---|---|---|---|
| `base/mcgen/MetaclassSmAttributeGenerator.java` | `run` | `mc` | Descripteur `SmAttribute` (champ + getter + classe interne `XSmAttribute`) — la pièce manquante réelle : sans ça, le `SmClass` de la classe feuille n'enregistre jamais les attributs du 2ᵉ parent, puisqu'il n'hérite pas du `SmClass` de ce parent |
| `base/mcgen/MetaclassSmDependencyGenerator.java` | `run` | `mc` | Idem pour les `SmDependency` (associations) |
| `base/mcgen/MetaclassLoadGenerator.java` | (deux boucles, une méthode) | `mc` (chargement) | Code du `load()` généré : initialisation/enregistrement des `SmAttribute` puis des `SmDependency` sur l'instance chargée |
| `base/datagen/DataGenerator.java` | `doGenerateAttributes` | `Data` | Champs de stockage réels (le `private DataType xxx;` physique) — ajoutés directement sur la classe `Data` de la feuille |
| `base/datagen/DataGenerator.java` | `doGenerateAssocs` | `Data` | Idem pour les champs de stockage des associations |
| `base/impgen/AttributeHelper.java` | (boucle interne) | `Impl` | Corps des accesseurs Java (`getXxx()`/`setXxx()`) des attributs sur la classe `Impl` |
| `base/impgen/DependencyHelper.java` | (boucle interne) | `Impl` | Corps des accesseurs Java des associations à navigabilité simple |
| `base/impgen/CompositionAccessorHelper.java` | (boucle interne) | `Impl` | Corps des accesseurs Java des associations de composition |

`base/mcgen/MetaclassGenerator.java` (le descripteur de métaclasse lui-même, pas ses attributs/dépendances) et `base/mcgen/MetaclassLoadGenerator`'s propre résolution du parent unique restent volontairement en single-parent — cf. §5.

---

## 5. Ce qui n'a délibérément **pas** changé

- **`base/impgen/ImplGenerator.java` (`doGenerateInheritance`) : zéro modification.** Son `createInterfaceRealization(implClass, emfClass)` existant pointe déjà vers l'interface `mm.api` de la classe — qui étend désormais correctement tous les parents grâce au changement §2. Java ne vérifie pas que l'interface implémentée étend elle-même un ou plusieurs parents ; la classe `Impl` continue de n'`extends` qu'une seule classe concrète (contrainte Java réelle, cf. `limitation-heritage-multiple-semgen.md` §5), mais implémente maintenant correctement les membres du 2ᵉ parent grâce à l'aplatissement (§3-4).
- **`MetaclassGenerator`, `MetaclassLoadGenerator` (résolution du parent unique), `DataGenerator` (`doGenerateInheritance`) : leur propre logique d'héritage simple, sur la classe concrète elle-même (`SmClass`/`Data`), reste inchangée.** Une classe Java concrète ne peut toujours avoir qu'un seul parent — ce n'est pas cette partie du problème que le patch résout, seulement les *membres* du 2ᵉ parent (§3-4), pas sa place dans la hiérarchie `extends`.
- **`MonogeApiGenerator.java` (variante Monoge de `ApiGenerator`) : non touché, garde le motif d'origine** (`mmClass.getParent().isEmpty() ? null : mmClass.getParent().get(0)`, un seul appel). Classe marquée `@Deprecated`.
- **`MonogeDataGenerator.java` : son `doGenerateInheritance` propre reste aussi en single-parent** (même motif, non touché) **— mais `doGenerateAttributes`/`doGenerateAssocs` ne sont PAS surchargées dans cette classe**, elle hérite donc directement des versions aplaties de `DataGenerator` (§4). Classe marquée `@Deprecated` également. Non vérifié si le mode Monoge est seulement legacy/inutilisé ou encore actif pour `reference/design` — même statut d'incertitude que le mode Toutatis ci-dessous.
- **`base/toutatis/expert/*` (générateurs de vérification de liens/dépendances en mode Toutatis)** : non touchés, ne voient toujours que la chaîne primaire. Non vérifié si `reference/design` tourne en mode Toutatis.

---

## 6. Statut des tests

- Compilation : ✅ (`SemGen_4.0.02.jmdac` construit sans erreur, §1).
- Round-trip Modelio (édition manuelle → reverse JavaDesigner → ré-import propre) : ✅ confirmé sur les 9 fichiers touchés.
- Régénération réelle contre `KerML` : ✅ génération complète de 81 métaclasses réussie dans le projet live. `DataType`, `Class`, `Structure`, `Flow` et les autres classes concernées sont présentes; les membres des parents secondaires sont aplatis sans réintroduire les associations techniques supprimées.
- Question ouverte, non vérifiable depuis le seul code source : interaction de l'aplatissement avec la persistance par classe de Modelio (`structural.node`) pour une classe qui serait le 2ᵉ parent d'un cas tout en restant une classe `Semantic` normale ailleurs — à confirmer par la régénération réelle.

La génération KerML live confirme le comportement attendu. La validation restante porte sur la restauration des 34 généralisations dans `reference/design`, puis sur une génération SysML complète et les experts Toutatis.
