# Héritage multiple KerML/SysML v2 : ce que SemGen ne sait pas faire, et ce que ça coûte

Document de travail préparé suite à la réserve de Cédric Marin sur l'approche actuelle de résolution des 34 cas d'héritage multiple. Objectif : poser le problème concrètement, avec des exemples réels tirés du modèle, avant la discussion.

> **Statut** : présenté à Cédric Marin, qui a transmis le code source de SemGen. Sur décision de Juan (pas une consigne de Cédric), un **prototype** de correctif a été écrit dans `ApiGenerator.java` (`doGenerateInheritance` boucle désormais sur tous les parents et émet une `Generalization` par parent, au lieu de s'arrêter à l'index 0). Pas encore compilé ni testé (pas de `pom.xml`/build dans ce checkout SemGen) — validation prévue par une régénération réelle côté transformation du modèle (ce workspace), à comparer avec le comportement attendu.
> **Risque `@objid` levé** : ce checkout SemGen est bien la source de vérité, pas un round-trip depuis un modèle Modelio séparé — l'édition manuelle du `.java` est sûre, Juan la reprendra directement dans Modelio ensuite.
> **Portée délibérément limitée à la couche interface** : `MetaclassGenerator`, `MetaclassLoadGenerator`, `DataGenerator`/`MonogeDataGenerator` et `ImplGenerator` (+ variantes Monoge) ciblent tous une vraie classe Java concrète (`cs.getSmMetaclass()`/`getDataClass()`/`getImplClass()`, un `Class` typé) — contrairement à `ApiGenerator`, qui cible une `Interface` (`cs.getEmfClass()`). Boucler sur ces quatre-là ne réglerait rien : une classe Java concrète ne peut toujours avoir qu'un seul parent, l'émission `.java` s'effondrerait à nouveau sur un seul parent, un cran plus bas. Arrêt volontaire à la couche interface, pas un manque de temps.
> **Risque anticipé, pas encore résolu** : corriger `ApiGenerator` seul va probablement faire passer le bug de « le 2ᵉ parent disparaît silencieusement mais ça compile » à « `AttributeDefinitionApi` étend correctement `Definition`+`DataType`, mais `AttributeDefinitionImpl` ne compile plus » sur les 34 classes — `ImplGenerator` n'hérite toujours que d'un seul parent concret alors que l'interface qu'il doit satisfaire s'est élargie. Personne n'a encore conçu le correctif côté `Impl` (aplatir les membres du 2ᵉ parent sur la classe `Impl` feuille, ou une délégation générée automatiquement). La régénération de test prévue vise justement à confirmer si ce risque se matérialise.

---

## 1. Le problème, sur un exemple concret

Prenons **`AttributeDefinition`** (SysML v2), un des 34 cas. La norme le définit ainsi :

> *A `AttributeDefinition` is a `Definition` that is also a `DataType`.*

Concrètement, dans `reference/spec` (miroir fidèle de la norme), `AttributeDefinition` porte **deux vraies généralisations UML** :

```
AttributeDefinition :> Definition   (axe primaire)
AttributeDefinition :> DataType     (axe secondaire)
```

Ça veut dire qu'un `AttributeDefinition`, dans la vraie sémantique de la norme, **EST À LA FOIS** un `Definition` et un `DataType` — la même instance, un seul objet, deux types. C'est le cas pour 34 classes du métamodèle (dont `AttributeDefinition`, `ActionDefinition`, `ConstraintUsage`, `ConnectorAsUsage`, etc.).

---

## 2. Ce qu'on a testé, et le résultat concret

Question : que fait SemGen (l'outil Modelio qui génère le code Java) quand on lui donne une classe avec **deux vraies généralisations réelles** ?

Test construit directement dans le modèle live : `TestChild` avec deux généralisations réelles, `TestChild :> TestPrimary` et `TestChild :> TestSecondary`.

**Résultat, reproduit deux fois à l'identique** :

```java
// Ce qui est généré :
public interface TestChild extends TestPrimary { ... }
public class TestChildImpl extends TestPrimaryImpl implements TestChild { ... }

// TestSecondary a purement et simplement disparu.
// Pas d'erreur, pas d'avertissement spécifique à ce sujet.
```

Le deuxième parent est **silencieusement perdu**, aussi bien sur l'interface générée (`mm.api`) que sur la classe d'implémentation (`mm.impl`). Trois autres mécanismes testés pour contourner ça (`SemGenAllowedDependency`, `SemGenAllowedLink`, un `Realization` UML classique) : les trois négatifs aussi (voir `points-a-trancher.md`, section « Points ouverts » pour le détail complet des 4 tests).

**Conclusion factuelle** : SemGen ne sait générer aucune forme d'héritage multiple, sur aucun axe, par aucun mécanisme testé.

---

## 3. La solution actuelle : association composée

Pour ne pas perdre l'axe secondaire, `reference/design` remplace la deuxième généralisation par une **référence composée** :

```
AttributeDefinition ──dataType (1..1, composition)──> DataType
```

Concrètement, le Java généré aujourd'hui :

```java
public interface AttributeDefinition extends Definition {
    DataType getDataType();
    void setDataType(DataType value);
}

public class AttributeDefinitionImpl extends DefinitionImpl implements AttributeDefinition {
    private DataType dataType;
    public DataType getDataType() { return dataType; }
    public void setDataType(DataType value) { this.dataType = value; }
}
```

**`AttributeDefinitionImpl` n'implémente PAS `DataType`.** Il *porte une référence* vers un `DataType`, mais il n'*est pas* substituable à un `DataType` — `attributeDefinitionInstance instanceof DataType` est faux. Ce que la norme affirme comme une seule instance à deux types, le code généré aujourd'hui le représente comme **deux instances distinctes, reliées par un pointeur**.

Ça génère sans planter (`GENERATION SUCCESSFUL`, confirmé sur les 97 métaclasses SysML réelles), mais **ce n'est pas la même chose que ce que dit la norme**.

---

## 4. Ce que ça coûte concrètement — les 4 points de Cédric, chiffrés

### 4.1 Multiplication des éléments de modèle

Pour représenter **un seul** concept SysML v2 (un `AttributeDefinition`), il faut désormais **deux objets Modelio/Java reliés** : un `AttributeDefinitionImpl` + un `DataTypeImpl` séparé, avec un lien entre les deux. Ça vaut pour les **34 cas**, donc potentiellement pour un très grand nombre d'instances dans un modèle utilisateur réel.

### 4.2 Performance et mémoire

Chaque instance d'un des 34 cas coûte désormais **2 objets au lieu d'1**, dans chaque modèle utilisateur construit avec ce métamodèle — pas seulement au niveau du métamodèle lui-même, mais à l'exécution, pour chaque `AttributeDefinition`/`ActionDefinition`/etc. que quelqu'un crée dans un vrai modèle SysML v2.

### 4.3 Contrôles de cohérence manquants aujourd'hui

Rien n'empêche aujourd'hui de créer un `AttributeDefinitionImpl` sans son `DataTypeImpl`, ou l'inverse — ni de garantir qu'ils restent reliés dans le temps. Dans la vraie norme, cette question n'existe même pas : c'est une seule instance, il n'y a rien à garder synchronisé.

### 4.4 Contenu réellement perdu (mesuré, pas supposé)

Vérifié sur les 32 cas concernés (hors les 2 exclus comme chevauchements) :

| Cas | Contenu propre sur la classe secondaire | Perdu comme membre direct de la classe primaire |
|---|---|---|
| `Connector` → `Relationship` | 1 attribut, 2 opérations | Oui |
| `CalculationUsage` → `Expression` | 1 attribut, 3 opérations | Oui |
| `AssertConstraintUsage` → `Invariant` | 1 attribut | Oui |
| `CalculationDefinition` → `Function` | 1 attribut | Oui |
| `ExhibitStateUsage` → `StateUsage` | 1 attribut, 1 opération | Oui |
| `MembershipExpose` → `MembershipImport` | 1 opération | Oui |
| `NamespaceExpose` → `NamespaceImport` | 1 opération | Oui |
| `PerformActionUsage` → `EventOccurrenceUsage` | 1 attribut | Oui |
| **25 autres cas** (ex. `AttributeDefinition` → `DataType`) | 0 (marqueurs purs) | Rien de concret, mais la classification elle-même est perdue (§4.5) |

**Total mesuré : 14 attributs/opérations** qui existent bien dans `reference/spec` comme membres directs de la classe primaire, et qui ne sont plus atteignables que via `.getXxx().laPropriete()` dans `reference/design` — jamais directement sur la classe primaire.

### 4.5 Perte plus profonde, sur les 32 cas : la classification elle-même

Même pour les 25 cas « marqueurs purs » (aucun contenu propre), la norme affirme un vrai fait sémantique : `AttributeDefinition` **est** un `DataType`. Cette classification (utilisable par exemple pour tester `oclIsKindOf(DataType)`) **disparaît entièrement** dans `reference/design`, remplacée par une simple relation « a un » — une affirmation plus faible que ce que dit la norme, sur les 32 cas, pas seulement les 8 avec du contenu.

---

## 5. Pourquoi c'est un contournement, pas une vraie solution — et où se situe la vraie contrainte

Point important : **la contrainte réelle vient de Java, pas d'un choix arbitraire de SemGen.** Une classe Java ne peut `extends` qu'**une seule** classe (héritage d'implémentation simple) — mais elle peut `implements` **autant d'interfaces qu'elle veut**. C'est du Java 100% valide :

```java
// Ceci est parfaitement légal en Java :
public interface AttributeDefinition extends Definition, DataType { }

public class AttributeDefinitionImpl extends DefinitionImpl implements AttributeDefinition {
    // méthodes de Definition ET de DataType, écrites directement ici
    // UN SEUL objet, pas de duplication, pas de synchronisation à maintenir
}
```

Si ce Java-là était généré, **il n'y aurait aucun des 4 problèmes du §4** : un seul objet, aucune duplication mémoire, aucun contrôle de cohérence à ajouter (une seule instance, toujours cohérente par construction), aucune façade nécessaire.

**Or on a la preuve que ce n'est pas ce que fait SemGen aujourd'hui** : dans le test `TestChild` (§2), même l'**interface générée** n'a gardé qu'un seul parent — alors que Java aurait accepté les deux (`extends TestPrimary, TestSecondary` sur l'interface est valide, même si `TestChildImpl` ne peut `extends` qu'une seule classe). Le générateur de SemGen collabore visiblement sur un modèle à héritage simple partout, y compris là où Java ne l'impose pas.

**Confirmé depuis, directement dans le code source de SemGen** (`H:\modelio\work\eclipse\modules\SemGen\...\semgenerator\`, investigation menée en parallèle sur une session distincte ayant accès au dépôt) : ce n'est pas une limite de configuration qu'on n'aurait pas su activer, c'est **codé en dur**. Le même patron — `final Generalization g = mmClass.getParent().isEmpty() ? null : mmClass.getParent().get(0);` puis un seul appel à `createGeneralization(...)` — est dupliqué dans sept générateurs, sans jamais boucler au-delà de l'index 0 :

| Générateur | Fichier | Ce qu'il émet |
|---|---|---|
| `ApiGenerator` | `base/apigen/ApiGenerator.java:154` | L'interface `mm.api` (`interface X extends Parent`) — **celui qui compte le plus** : Java autorise `extends` multiple sur une interface, mais cette méthode ne le fait jamais |
| `MonogeApiGenerator` | `monoge/apigen/MonogeApiGenerator.java:52` | Variante Monoge de l'interface `mm.api` |
| `ImplGenerator` | `base/impgen/ImplGenerator.java:191` | La classe concrète `XImpl` — ici la limite est réellement celle de Java (une classe, un seul `extends`), pas un choix du générateur |
| `MetaclassGenerator` | `base/mcgen/MetaclassGenerator.java:197` | Le descripteur de métaclasse (`mc`) |
| `MetaclassLoadGenerator` | `base/mcgen/MetaclassLoadGenerator.java:60` | Le chargeur de métaclasse |
| `DataGenerator` / `MonogeDataGenerator` | `base/datagen/DataGenerator.java:209`, `monoge/datagen/MonogeDataGenerator.java:40` | La classe `XData` |

Aucune échappatoire trouvée non plus : `GeneratorConfig.java` ne porte que l'id/nom/version/provider du métamodèle, rien sur une stratégie d'héritage ; `IAnnotationScheme.java` expose bien des points d'extension (`isAllowedLinkFlow`, `isAllowedDependencyFlow` — les mécanismes `SemGenAllowedDependency`/`SemGenAllowedLink` déjà testés négativement en §2), mais `doGenerateInheritance` ne consulte jamais ce schéma d'annotation — il lit directement `mmClass.getParent()`. Ce n'est donc pas un point d'extension qu'on invoquerait mal ; il n'existe pas.

**Conséquence concrète pour un vrai correctif** : il faudrait modifier les six points d'appel non-`Impl` (api, monoge-api, metaclass, metaclass-load, data, monoge-data) pour boucler sur `mmClass.getParent()` et émettre plusieurs `Generalization`, **plus** une décision de conception pour `ImplGenerator`/`XImpl` sur la façon dont une seule classe concrète implémente deux interfaces qui déclarent chacune leur propre état/comportement (composition interne cachée dans le `XImpl` généré, ou façade déléguante) — la limite Java à une seule classe mère reste réelle à ce niveau précis, ce n'est pas, elle, un choix arbitraire du générateur.

**C'est précisément le point de Cédric** : ce n'est pas la première fois — l'implémentation UML2 de Modelio, il y a 15 ans, a buté sur le même mur et a été bricolée pour cette même raison. SysML v2 (via KerML, qui reprend des schémas de UML2) réintroduit le même besoin. Régler ça « à la source » veut dire : faire évoluer le générateur SemGen/JavaDesigner lui-même pour qu'il produise une interface à héritage multiple + une seule classe d'implémentation, plutôt que de continuer à contourner le problème modèle par modèle.

---

## 6. Ce qui est réellement en notre pouvoir, et ce qui ne l'est pas

- **Hors de portée depuis ce projet de transformation** : modifier le générateur SemGen/JavaDesigner lui-même. Le périmètre exact est maintenant connu (§5) — six points d'appel à faire boucler sur tous les parents, plus une décision de conception pour `ImplGenerator`/`XImpl` — mais reste un chantier de code source partagé, pas quelque chose qu'on modifie via le scripting Jython contre le modèle. C'est un chantier pour l'équipe outillage, à cadrer avec Cédric avant toute modification (aucun correctif n'a été tenté ni proposé à ce stade — la source n'a été que lue).
- **Dans notre pouvoir, si on veut limiter la casse en attendant** : ré-introduire une couche de délégation écrite à la main (`implements Secondary` + méthodes qui délèguent vers l'objet composé) — mais seulement pour les 8 cas avec du contenu réel (§4.4), pas les 32. Cette procédure est déjà validée et documentée (bascule de stéréotype `Semantic` → `SemGenManual`, écriture manuelle, `reverse` JavaDesigner pour la traçabilité) — voir `points-a-trancher.md`. Elle règle la perte de contenu direct (§4.4) mais pas la perte de classification (§4.5), ni la duplication d'objets à l'exécution (§4.1–4.3).

## 7. Recommandation

Poser clairement la question comme un choix d'équipe, pas une décision déjà prise côté transformation du modèle :

1. **Court terme** : garder l'association composée (déjà validée, génère proprement), documentée explicitement comme un contournement temporaire — pas une solution conforme à la norme.
2. **Moyen terme, si le contenu perdu (8 cas) pose un vrai problème d'usage** : ajouter la délégation manuelle pour ces 8 cas précisément.
3. **Le vrai sujet, à porter au niveau outillage (pas ce projet)** : faire évoluer SemGen/JavaDesigner pour générer une interface à héritage multiple + une seule implémentation — la seule option qui règle vraiment les 4 points de Cédric en même temps, et qui rapprocherait Modelio d'une conformité réelle à la norme. Périmètre du correctif confirmé au niveau code source (§5) : six générateurs à faire boucler sur tous les parents, plus une décision de conception restant à trancher pour `XImpl`.

**Retenu** : Cédric a transmis le code source de SemGen ; un prototype de correctif existe désormais pour la couche interface (`ApiGenerator.java`), non validé et partiel — voir le statut en tête de document pour le détail (ce qui est fait, ce qui reste, et le risque de régénération `@objid`).
