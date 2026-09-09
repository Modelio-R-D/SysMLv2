---
marp: true
theme: docaposte
paginate: true
---

<!-- _class: title -->

# Héritage multiple SysML v2
## Ce que SemGen ne sait pas faire, et ce que ça coûte

Réunion de suivi · Septembre 2026

---

# Un exemple concret : `AttributeDefinition`

La norme SysML v2 dit : *A `AttributeDefinition` is a `Definition` that is also a `DataType`.*

<div class="two-col">
<div>

**Ce que dit la norme (`reference/spec`)**

Deux vraies généralisations UML, sur la même instance :

```
AttributeDefinition :> Definition
AttributeDefinition :> DataType
```

Une seule instance, deux types à la fois.

</div>
<div>

**Pourquoi c'est un problème**

34 classes du métamodèle sont dans ce cas : `AttributeDefinition`, `ActionDefinition`, `ConstraintUsage`, `ConnectorAsUsage`, etc.

Java ne sait pas faire `class X extends A, B`.

</div>
</div>

<div class="takeaway">Une seule instance, deux types — c'est ce que la norme demande. La question : comment le générer en Java ?</div>

---

<!-- _class: "section theme-mint" -->

# Ce qu'on a testé

---

<!-- _class: dense -->

# SemGen perd silencieusement le deuxième parent — même sur l'interface

Test construit dans le modèle live : `TestChild` avec **deux vraies généralisations réelles** (`:> TestPrimary` et `:> TestSecondary`).

```java
// Généré par SemGen :
public interface TestChild extends TestPrimary { ... }
public class TestChildImpl extends TestPrimaryImpl implements TestChild { ... }

// TestSecondary a disparu. Pas d'erreur, pas d'avertissement.
```

<div class="box p">
Reproduit deux fois à l'identique. Trois autres mécanismes testés
(<code>SemGenAllowedDependency</code>, <code>SemGenAllowedLink</code>, <code>Realization</code> UML) :
les trois négatifs aussi.
</div>

<div class="takeaway">SemGen ne sait générer aucune forme d'héritage multiple, sur aucun axe, par aucun mécanisme testé.</div>

---

<!-- _class: "section theme-mint" -->

# La solution actuelle

---

<!-- _class: dense -->

# On a remplacé le 2ᵉ axe par une référence composée

```java
public interface AttributeDefinition extends Definition {
    DataType getDataType();
    void setDataType(DataType value);
}

public class AttributeDefinitionImpl extends DefinitionImpl
        implements AttributeDefinition {
    private DataType dataType;   // ← un OBJET SÉPARÉ, pas une vraie identité
    public DataType getDataType() { return dataType; }
    public void setDataType(DataType value) { this.dataType = value; }
}
```

<div class="takeaway"><code>AttributeDefinitionImpl</code> n'implémente PAS <code>DataType</code>. Il porte une référence vers un <code>DataType</code> séparé — <code>instanceof DataType</code> est faux. Génère proprement (<code>GENERATION SUCCESSFUL</code>), mais ce n'est pas ce que dit la norme.</div>

---

# Ce que ça coûte — les 4 réserves de Cédric

<div class="two-col">
<div>

**1. Multiplication des éléments**
1 concept SysML = 2 objets Modelio/Java reliés, sur 34 cas.

**2. Performance & mémoire**
2 objets au lieu d'1, à chaque instance créée dans un vrai modèle utilisateur — pas juste au niveau métamodèle.

</div>
<div>

**3. Cohérence à garantir**
Rien n'empêche de créer l'un sans l'autre, ou de les laisser se désynchroniser.

**4. Façade nécessaire**
Il faudrait cacher cette duplication aux utilisateurs — travail d'ingénierie en plus.

</div>
</div>

<div class="stat-box"><span class="number">32</span><span class="label">cas concernés par ces 4 points</span></div>

---

<!-- _class: dense -->

# Sur 32 cas, 8 perdent du contenu réel — mesuré, pas supposé

| Cas | Contenu propre de la classe secondaire |
|---|---|
| `Connector` → `Relationship` | 1 attribut, 2 opérations |
| `CalculationUsage` → `Expression` | 1 attribut, 3 opérations |
| `AssertConstraintUsage` → `Invariant` | 1 attribut |
| `CalculationDefinition` → `Function` | 1 attribut |
| `ExhibitStateUsage` → `StateUsage` | 1 attribut, 1 opération |
| `MembershipExpose` / `NamespaceExpose` | 1 opération chacun |
| `PerformActionUsage` → `EventOccurrenceUsage` | 1 attribut |

<div class="takeaway">14 attributs/opérations au total, plus atteignables comme membres directs — seulement via <code>.getDataType().laPropriete()</code>. Les 25 autres cas (ex. <code>AttributeDefinition</code>) n'ont aucun contenu propre, mais perdent quand même la classification elle-même : <code>AttributeDefinition</code> n'est plus reconnu comme un <code>DataType</code> par le modèle.</div>

---

<!-- _class: "section theme-poussin" -->

# Pourquoi ce n'est qu'un contournement

---

<!-- _class: dense -->

# La vraie contrainte vient de Java — mais SemGen va plus loin qu'elle ne l'exige

Java interdit `extends` sur plusieurs classes. Mais **plusieurs interfaces**, c'est du Java 100% valide :

```java
// Ceci compilerait parfaitement en Java :
public interface AttributeDefinition extends Definition, DataType { }

public class AttributeDefinitionImpl extends DefinitionImpl
        implements AttributeDefinition {
    // méthodes de Definition ET DataType, sur UN SEUL objet
}
```

<div class="box y">
Si ce Java-là était généré : <strong>zéro</strong> des 4 problèmes précédents — un seul objet, aucune duplication, aucune cohérence à vérifier, aucune façade.
</div>

<div class="takeaway">Preuve directe que SemGen ne le fait pas : dans le test <code>TestChild</code>, même l'INTERFACE générée n'a gardé qu'un seul parent — alors que Java aurait accepté les deux à ce niveau-là.</div>

---

<!-- _class: dense -->

# Confirmé dans le code source : c'est codé en dur, pas une limite de config

Même patron dupliqué dans 7 générateurs — un seul appel à `createGeneralization`, jamais de boucle au-delà du premier parent :

| Générateur | Émet |
|---|---|
| `ApiGenerator`, `MonogeApiGenerator` | L'interface `mm.api` — **celui qui compte** : Java autorise `extends` multiple ici |
| `MetaclassGenerator`, `MetaclassLoadGenerator` | Descripteur / chargeur de métaclasse |
| `DataGenerator`, `MonogeDataGenerator` | La classe `XData` |
| `ImplGenerator` | `XImpl` — ici la limite Java (une classe mère) est réelle, pas un choix du générateur |

<div class="box p">Aucune échappatoire : <code>IAnnotationScheme</code> a des points d'extension (<code>isAllowedLinkFlow</code>...) mais <code>doGenerateInheritance</code> ne les consulte jamais.</div>

<div class="takeaway">Un vrai correctif : 6 générateurs à faire boucler sur tous les parents, plus une décision de conception pour <code>XImpl</code> (composition cachée ou façade déléguante). Périmètre connu, pas à explorer — à cadrer avec Cédric.</div>

---

# Un problème déjà connu, il y a 15 ans

<div class="box p">
L'implémentation UML2 de Modelio a buté sur exactement ce mur — bricolée à l'époque, sans respecter le métamodèle de la norme, pour cette même raison.
</div>

<div class="box m">
SysML v2 (via KerML, qui reprend des schémas de UML2) réintroduit le même besoin. Cédric note qu'un concurrent (un outil Dassault, selon son souvenir) revendiquerait une conformité à 100% à la norme — non vérifié de notre côté.
</div>

<div class="takeaway">Régler « à la source » = faire évoluer le générateur SemGen/JavaDesigner lui-même, pas continuer à contourner modèle par modèle.</div>

---

# Ce qui est en notre pouvoir — et ce qui ne l'est pas

<div class="two-col">
<div>

**Hors de portée ici**
Modifier le générateur SemGen/JavaDesigner — périmètre maintenant connu (6 générateurs + 1 décision de conception), mais reste un chantier de code source partagé à cadrer avec l'équipe outillage, pas ce projet de transformation.

</div>
<div>

**Dans notre pouvoir**
Délégation écrite à la main pour les 8 cas avec du contenu réel (procédure déjà validée). Règle §4 pour ces 8 cas — pas la classification, pas la duplication d'objets.

</div>
</div>

---

<!-- _class: large -->

# Recommandation

1. **Court terme** — garder l'association composée, documentée explicitement comme contournement temporaire, pas comme solution conforme.
2. **Moyen terme** — délégation manuelle pour les 8 cas à contenu réel, si l'usage le justifie.
3. **Le vrai sujet, niveau outillage** — faire évoluer SemGen/JavaDesigner pour générer une interface à héritage multiple + une seule implémentation. Périmètre du correctif confirmé en source : pas une exploration à refaire.

<div class="takeaway">Le point 3 est la seule option qui règle les 4 réserves de Cédric en même temps — et qui rapproche Modelio d'une vraie conformité à la norme.</div>

---

<!-- _class: closing -->

# Discussion

Questions et retours bienvenus.
