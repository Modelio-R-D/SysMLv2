# Etude icones SysML v2 - Methodologie

## Sources identifiees

- **Icones UML** (base Modelio) : `H:\modelio\work\modelio-source\modelio\uml\uml.ui\mmimages`
  - PNG 24x24, ARGB32, fond transparent, palette orange/jaune, contour noir.
  - Convention de nommage : `standard.<qualifiedName-en-minuscules>.png` (+ variantes `.image.png` pour les vignettes de diagramme).
  - Inventaire : [01-inventaire-uml.csv](01-inventaire-uml.csv)

- **Icones SysML v1** (module SysMLArchitect, depot open source Modelio) :
  `C:\Users\frekik\Documents\GIT\ExtensionsForModelio\SysMLArchitect\src\main\conf\res\icons`
  - Depot : https://github.com/ModelioOpenSource/ExtensionsForModelio
  - Inventaire : [02-inventaire-sysml1.csv](02-inventaire-sysml1.csv) (colonnes `chemin_source` /
    `chemin_destination` ajoutees le 2026-09-24 pour tracer chaque icone vers sa copie dans ce depot)
  - **Base de depart (2026-09-24, proposition PO)** : les 117 icones ont ete copiees (pas deplacees -
    le depot ExtensionsForModelio externe n'est pas modifie) dans
    [07-icones-sources/sysml1/](07-icones-sources/sysml1/), qui devient le point de depart versionne
    pour la production.

- **Reference du metamodele SysML v2** (pour valider les correspondances, pas pour les icones) :
  https://github.com/Systems-Modeling/SysML-v2-Release (spec + bibliotheque normative `sysml.library`)
  - Fichiers `.sysml` du dossier `sysml.library/Systems Library` consultes pour confirmer les noms de
    metaclasses Definition/Usage (Ports.sysml, Flows.sysml, Parts.sysml, Interfaces.sysml,
    Connections.sysml, Requirements.sysml, Cases.sysml, UseCases.sysml, VerificationCases.sysml,
    AnalysisCases.sysml, Views.sysml, Allocations.sysml, Metadata.sysml).

- **Cible** (module a completer dans le depot principal) :
  `H:\modelio\work\modelio-source\modelio\sysml\sysml.ui\mmimages`
  (mecanisme de resolution : `SysmlElementImageProvider`, meme convention que UML)

- **Notation graphique officielle SysML v2** (verifiee le 2026-09-24) :
  `doc/Intro to the SysML v2 Language-Graphical Notation.pdf` du meme depot
  `Systems-Modeling/SysML-v2-Release` (support de Sanford Friedenthal, 123 pages, dernier release
  2023-03-07 - genere manuellement sous Visio, prototypes de visualisation Tom Sawyer/PlantUML).
  **Constat : la notation normative ne propose aucun pictogramme/icone par concept.** Elle repose
  uniquement sur : un rectangle a compartiments portant un mot-cle entre guillemets («part def»,
  «port def», «enum def», «action», «state», ...) et, seule distinction visuelle *Definition/Usage*
  explicitement definie dans la spec, la **forme du rectangle** (coins droits = Definition, coins
  arrondis = Usage) - convention differente de celle proposee dans ce document (contour plein/allege,
  empruntee au pattern classifieur/instance de Modelio). Aucune mention d'icone/pictogramme/badge n'a
  ete trouvee dans les 123 pages, y compris dans la section "Contrasting SysML v2 with SysML v1" et le
  tableau de correspondance terminologique v1->v2, qui ne evoquent que du texte et des formes.
  **Consequence pour cette etude** : le jeu d'icones Modelio (arbre de modele, palette de diagramme)
  reste une amelioration d'ergonomie propre a l'outil, non couverte par la norme - aucune contrainte
  ni proposition officielle a respecter sur le plan graphique/pictogramme ; a l'inverse, la convention
  coins droits/coins arrondis pourrait etre reprise en complement (ou a la place) du contour plein/
  allege pour rester alignes avec la notation normative dans les diagrammes (hors icones d'arbre).

## Constat de depart

Le module `sysml` du depot principal ne contient aujourd'hui qu'une seule icone
(`sysml.sysmlproject.png`). Les icones SysML v2 sont entierement a creer.

## Etapes

### 0. Inventaire et mapping (prealable)

Construire un tableau de correspondance avant toute manipulation d'image :
`concept SysML v2 (Definition/Usage) -> icone SysML v1 la plus proche -> icone UML la plus proche -> action`.

Voir [03-mapping-sysml1-vers-sysml2.csv](03-mapping-sysml1-vers-sysml2.csv) (brouillon a valider/completer
par rapport a la bibliotheque normative SysML v2). Une version [.xlsx](03-mapping-sysml1-vers-sysml2.xlsx)
est egalement disponible avec une feuille `legende` qui documente chaque colonne - a regenerer depuis le
csv (source de verite, versionne) apres toute modification, le xlsx n'est qu'une vue de confort pour
Excel.

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

**Fait (2026-09-24)** : toutes les icones source utilisees comme base sont regroupees sous
[07-icones-sources/](07-icones-sources/), avec deux sous-dossiers par origine :
`07-icones-sources/sysml1/` (117 icones SysMLArchitect, base de depart complete) et
`07-icones-sources/uml/` (17 icones UML de repli, pour les lignes du mapping sans base SysML1 -
`action = derive`/`recolorer` avec repli UML cite en commentaire). Ancienne organisation
(`04-sources-brutes/sysml1|uml/`) consolidee ici le 2026-09-24 pour n'avoir qu'une seule racine de
provenance, plus coherente avec la demande du PO de "base de depart" unique.

### 2. Generation d'une variation de couleur (base SysML v2)

- Script de recoloration cible (Pillow/ImageMagick) : remplacement precis de la couleur de
  remplissage (garder traits noirs + alpha), pas de hue-shift global (deteriore l'anti-aliasing).
  - Palette actuelle a differencier :
    - UML : orange/jaune
    - SysML v1 : a confirmer par extraction de la palette reelle des PNG
    - SysML v2 (proposition) : bleu/violet, a valider avec le PO avant production en masse
- Sortie : set "base SysML v2" couvrant les concepts ayant un equivalent direct (`action = recolorer`
  ou `derive` dans le mapping).

**Prototype (2026-09-24)** : 3 icones (`block`, `port`, `requirement`) en Definition/Usage x
bleu (`#2c70ba`) / violet (`#6c3fa6`), redessinees en SVG ([06-prototype-svg/](06-prototype-svg/),
vectoriel a partir de la meme silhouette - pas de vectorisation automatique du bitmap). Un premier
essai avait aussi produit une variante PNG (remap HLS, dossier `05-prototype-couleur/`) pour comparer
les deux formats avant la contrainte SVG du PO (voir plus bas) ; supprime le 2026-09-24 une fois le
choix du SVG acte, pour ne pas garder un prototype obsolete. Distinction Definition/Usage prototypee
via **soulignement** (convention deja utilisee par Modelio pour classifieur/instance : `class.png`/
`instance.png`, `component.png`/`componentinstance.png`) plutot que contour allege/pointille ou
coins droits/arrondis - a valider avec le PO en meme temps que la couleur. Apercu partage :
artefact `Palette SysML v2`.

**Nouvelle contrainte PO (2026-09-24) : production en SVG.** Decision : produire les icones en SVG
des maintenant, sans attendre de trancher comment Modelio les affichera. Point technique releve pour
memoire (a traiter separement, plus tard) : le chargement d'icones dans Modelio passe par
`org.eclipse.swt.graphics.Image` (SWT, raster uniquement - voir `ElementImageService`/
`IElementImageProvider` dans `platform.model.ui`), sans aucun rasterizer SVG (type Apache Batik)
trouve dans `uml.ui` ni `sysml.ui`. **Validation PO (2026-09-24, reunion)** : couleur **bleu** (`#2c70ba`) retenue - une deuxieme teinte
(violet) reste envisageable en complement plus tard si besoin, pas d'urgence. Style et distinction
Definition/Usage (soulignement) valides sur les 3 icones prototype en bleu (`block.bleu.usage.svg`,
`port.bleu.usage.svg`, `requirement.bleu.usage.svg`). Suite demandee par le PO : construire une base
de depart en copiant les icones SysMLArchitect dans ce depot (voir section Sources ci-dessus,
[07-icones-sources/](07-icones-sources/)) et tracer systematiquement source/destination dans les
tableaux - fait le meme jour (colonnes ajoutees a
[02-inventaire-sysml1.csv](02-inventaire-sysml1.csv) et
[03-mapping-sysml1-vers-sysml2.csv](03-mapping-sysml1-vers-sysml2.csv)).

Consequence pratique pour l'etape 2/3 : dessiner directement en
vectoriel (formes simples redessinees a partir de la silhouette de reference), pas de vectorisation
automatique des PNG source qui donnerait un rendu "blocky" fidele aux pixels plutot qu'un trace propre.

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

## Etat d'avancement (2026-09-24) - consolidation

Une deuxieme copie de cette etude avait ete demarree en parallele dans
`C:\Users\frekik\Documents\GIT\SysML_v2\icons-study` (hors depot git). Les deux ont ete comparees et
fusionnees ici (seul emplacement conserve, versionne dans ce depot) :

- Les inventaires 01/02 de la copie parallele couvraient exactement les memes fichiers que ceux-ci (avec
  en plus les vignettes `*.image.png` du set UML, volontairement exclues ici car redondantes avec l'icone
  de base sur le plan conceptuel).
- Le mapping 03 de la copie parallele avait ete construit par balayage exhaustif des 183 metaclasses du
  metamodele Java implemente sur cette branche (`modelio/sysml/sysml.metamodel.api`), en complement de la
  bibliotheque normative deja utilisee ici. Cette validation croisee a permis de :
  - completer ce tableau avec ~35 lignes manquantes, surtout autour des familles Action/State/ControlNode
    (AcceptActionUsage, SendActionUsage, IfActionUsage, LoopActionUsage, PerformActionUsage,
    TerminateActionUsage, ForkNode/JoinNode/MergeNode/DecisionNode, TransitionUsage, EventOccurrenceUsage,
    ExhibitStateUsage), ainsi que AssertConstraintUsage, Invariant, ConjugatedPortDefinition,
    BindingConnectorAsUsage, SatisfyRequirementUsage, IncludeUseCaseUsage, CalculationDefinition/Usage,
    LibraryPackage ;
  - completer la couverture des icones SysML1 elles-memes : variantes 48px (block48, constraintblock48,
    valuetype48, view48, viewpoint48, unit48, quantitykind48, flowspecification48), vignettes de port
    (flowport_in/inout/outdiagram), actor, constraint, sysmldiagram, traceability ;
  - corriger la ligne `MetadataDefinition`/`MetadataUsage` : la metaclasse reellement implementee est
    `MetadataFeature` (sans dualite Definition/Usage) ;
  - identifier un ecart a signaler au PO : `IndividualDefinition`/`IndividualUsage` (present dans la
    bibliotheque normative) n'existent pas dans le metamodele Java implemente sur cette branche - a
    verifier si prevu pour une iteration ulterieure.
- Attention : ce metamodele Java (`SysML2Metamodel`, version `0.0.1`) est un travail en cours sur la
  branche `feature/sysml2` (cf commit "chargement du metamodele + repro du blocage heritage multiple") -
  a utiliser comme complement de validation, pas comme reference unique face a la bibliotheque normative.
