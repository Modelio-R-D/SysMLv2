---
marp: true
theme: docaposte
paginate: true
---

<!-- _class: title -->

# Revue Cédric Marin

## ARCHIVE HISTORIQUE · État de la revue au 23 septembre 2026

Métamodèle KerML / SysML v2 · archivé le 26 septembre 2026

---

# Trois remarques, trois corrections, trois preuves

<!-- _class: dense -->

| # | Remarque | Correction | Preuve dans le code généré |
|---|----------|-----------|---------------------------|
| 1 | Les 171 métaclasses étaient flaguées `structural.node`, y compris les 8 abstraites | Phase 8 puis Phase 11 (whitelist de 28) | `isCmsNode → true : 28` · `false : 143` |
| 2 | `KerMLModelElement.name` / `elementId` font doublon avec le natif Modelio | Phase 10 | 4 accesseurs absents, API **et** impl |
| 3 | Stockage canonique des associations : `isDerived` perdu | Phase 12 | 291 ends dérivés / 548 mappings |

<div class="takeaway">
Le modèle <strong>et</strong> le code généré sont désormais alignés — plus aucun écart avec la whitelist.
</div>

---

# 1 · La persistance revient à 28 grains au lieu de 171

<div class="two-col">
<div>

## Le problème

Chaque élément de modèle finissait dans **son propre fichier persisté**.

Le script posait le tag sans condition, y compris sur les métaclasses abstraites — alors que la convention l'interdit explicitement.

</div>
<div>

## Le résultat

<div class="stat-box"><span class="number">28</span><span class="label">cms nodes — écart nul vs whitelist</span></div>

`SysMLProject`, `Package` / `LibraryPackage`, et les 25 classes `Definition` concrètes.

Usages et détails d'implémentation restent embarqués.

</div>
</div>

---

# 2 · Le nommage natif Modelio redevient l'autorité

<div class="two-col">
<div>

## Avant

`KerMLModelElement` portait ses propres `name` et `elementId`, en conflit avec `ModelElement.Name` et l'UUID Modelio.

</div>
<div>

## Après

`extends ModelElementImpl` — aucun accesseur dupliqué.

Les champs de nommage propres à KerML sont conservés : `declaredName`, `shortName`, `qualifiedName`, `declaredShortName`.

</div>
</div>

<div class="takeaway">
Vérifié le 23/09 sur les deux fichiers régénérés : <strong>getName, setName, getElementId, setElementId → absents</strong>.
</div>

---

# Ce qui reste ouvert

<div class="two-col">
<div>

## Point 3 partiellement prouvé

`isDerived` est confirmé **côté modèle** par l'exécution de la Phase 12.

Il n'a pas été vérifié par inspection du Java généré.

</div>
<div>

## Étiquette de version incohérente

L'en-tête des fichiers annonce `Generator version: 4.0.02` alors que le module installé est **4.0.04**.

Le contenu généré est correct — l'origine de l'écart n'est pas tracée.

</div>
</div>

---

<!-- _class: closing -->

# Revue soldée

Les 3 remarques de Cédric sont traitées et vérifiées.
