# Etude icones SysML v2 - Methodologie

## Sources identifiees

- **Icones UML** (base Modelio) : `H:\modelio\work\modelio-source\modelio\uml\uml.ui\mmimages`
  - PNG 24x24, ARGB32, fond transparent, palette orange/jaune, contour noir.
  - Convention de nommage : `standard.<qualifiedName-en-minuscules>.png` (+ variantes `.image.png` pour les vignettes de diagramme).
  - Inventaire : [01-inventaire-uml.csv](01-inventaire-uml.csv)

- **Icones SysML v1** (module SysMLArchitect, depot open source Modelio) :
  `C:\Users\frekik\Documents\GIT\ExtensionsForModelio\SysMLArchitect\src\main\conf\res\icons`
  - Depot : https://github.com/ModelioOpenSource/ExtensionsForModelio
  - Inventaire : [02-inventaire-sysml1.csv](02-inventaire-sysml1.csv)

- **Reference du metamodele SysML v2** (pour valider les correspondances, pas pour les icones) :
  https://github.com/Systems-Modeling/SysML-v2-Release (spec + bibliotheque normative `sysml.library`)
  - Fichiers `.sysml` du dossier `sysml.library/Systems Library` consultes pour confirmer les noms de
    metaclasses Definition/Usage (Ports.sysml, Flows.sysml, Parts.sysml, Interfaces.sysml,
    Connections.sysml, Requirements.sysml, Cases.sysml, UseCases.sysml, VerificationCases.sysml,
    AnalysisCases.sysml, Views.sysml, Allocations.sysml, Metadata.sysml).

- **Cible** (module a completer dans le depot principal) :
  `H:\modelio\work\modelio-source\modelio\sysml\sysml.ui\mmimages`
  (mecanisme de resolution : `SysmlElementImageProvider`, meme convention que UML)

## Constat de depart

Le module `sysml` du depot principal ne contient aujourd'hui qu'une seule icone
(`sysml.sysmlproject.png`). Les icones SysML v2 sont entierement a creer.

## Etapes

### 0. Inventaire et mapping (prealable)

Construire un tableau de correspondance avant toute manipulation d'image :
`concept SysML v2 (Definition/Usage) -> icone SysML v1 la plus proche -> icone UML la plus proche -> action`.

Voir [03-mapping-sysml1-vers-sysml2.csv](03-mapping-sysml1-vers-sysml2.csv) (brouillon a valider/completer
par rapport a la bibliotheque normative SysML v2).

Colonnes :
- `icone_sysml1` : fichier source dans SysMLArchitect
- `type_sysml2` : `element` (metaclasse structurelle/comportementale KerML/SysML v2), `relation` (specialisation,
  dependency, import... - pas de dualite Definition/Usage), `diagramme`, ou `autre` (annotation, fonctionnalite
  Modelio, bibliotheque de valeurs...)
- `concept_sysml2_definition` / `concept_sysml2_usage` : metaclasses SysML v2 correspondantes. Pour les lignes
  `type_sysml2=element`, les deux colonnes doivent normalement pouvoir etre remplies (dualite Definition/Usage) -
  si une seule l'est, verifier qu'une autre ligne du tableau couvre l'autre moitie (cf. commentaire), sinon c'est
  un trou a combler. Pour les lignes `relation`/`diagramme`/`autre`, la dualite ne s'applique pas : seule la
  colonne `concept_sysml2_definition` est utilisee comme "concept principal".
- `action` : `recolorer` (reprise directe + nouvelle couleur), `derive` (reprise + leger ajustement de forme/badge),
  `creer` (aucun equivalent direct, a dessiner)
- `confiance` : `haute` / `moyenne` / `basse` (fiabilite de la correspondance proposee, a lever avant production)
- `commentaire` : point d'attention

Ordre de priorite pour choisir une base par concept SysML v2 :
1. icone SysML v1 existante (cas le plus frequent - action `recolorer`/`derive`) ;
2. a defaut, icone UML proche par analogie semantique (action `derive`), ex. `OccurrenceDefinition/Usage`
   -> `standard.event.png`, `IndividualDefinition/Usage` -> `standard.instance.png` ;
3. si aucune des deux bases n'est pertinente (`MetadataDefinition/Usage`, `RenderingDefinition/Usage`),
   creation ex nihilo en etape 3 - cas rares (5 lignes sur ~95 dans le mapping actuel).

Convention visuelle Definition/Usage : reprendre le pattern deja utilise par Modelio pour
classifieur/instance (`standard.class.png` vs `standard.instance.png`, `component.png` vs
`componentinstance.png`) : contour plein = *Definition*, contour allege/pointille = *Usage*.

### 1. Isolement des icones de base (UML proches + SysML v1)

- Copier dans ce dossier d'etude les icones source retenues par le mapping (pas de modification).
- Objectif : disposer d'un set de reference immuable pour comparaison avant/apres.

### 2. Generation d'une variation de couleur (base SysML v2)

- Script de recoloration cible (Pillow/ImageMagick) : remplacement precis de la couleur de
  remplissage (garder traits noirs + alpha), pas de hue-shift global (deteriore l'anti-aliasing).
  - Palette actuelle a differencier :
    - UML : orange/jaune
    - SysML v1 : a confirmer par extraction de la palette reelle des PNG
    - SysML v2 (proposition) : bleu/violet, a valider avec le PO avant production en masse
- Sortie : set "base SysML v2" couvrant les concepts ayant un equivalent direct (`action = recolorer`
  ou `derive` dans le mapping).

### 3. Creation des icones manquantes

- Concerne les lignes `action = creer` du mapping (concepts sans equivalent UML/SysML v1 :
  `ViewpointDefinition`, `ConcernUsage`, `Metadata`, etc. - liste a completer apres validation du
  mapping avec la bibliotheque normative).
- Methode : fiche de specification par icone (silhouette, badge, couleur, taille 24x24) construite a
  partir de la grammaire visuelle etablie en etape 2, pour garantir la coherence du set complet.

## A valider avec le PO / avant production en masse

1. Localisation confirmee des vraies icones "SysML1" utilisees en production (celles de
   SysMLArchitect ou une autre source si le module differe).
2. Couleur cible du set SysML v2.
3. Perimetre exact des concepts SysML v2 a couvrir (liste de metaclasses figee par rapport a la
   release SysML-v2-Release).
