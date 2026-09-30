# Guide visuel - production des icones SysML v2 (Modelio)

Regles condensees issues de la revue PO du 2026-09-24/25 (32 icones produites, 4 rounds de
corrections). A suivre pour tout nouveau lot d'icones, avant meme de commencer a dessiner.

## Format et canevas

- Format de sortie : **SVG**, `viewBox="0 0 64 64"` (taille de reference validee par le PO -
  ne pas confondre avec le PNG source 24x24).
- Toujours dessiner d'abord dans un espace de travail **24 unites** (memes proportions que les PNG
  source, plus simple a raisonner), puis multiplier chaque coordonnee/epaisseur par `64/24 (=2.667)`
  au moment d'ecrire le SVG final. Ne jamais changer seulement le chiffre du viewBox sans reechelonner
  les traits - un trait pense pour 24 unites devient invisible/trop fin sur un canevas 64.
- Fonction utilitaire type (a reprendre telle quelle) :
  ```python
  SCALE = 64 / 24
  def s(v):
      v = v * SCALE
      r = round(v, 2)
      return int(r) if r == int(r) else r
  ```

## Palette

- Couleur retenue (2026-09-24) : **bleu**. Une option violette a ete prototypee mais non retenue
  (reste possible en complement plus tard si besoin).
- Trois tons a utiliser partout :
  - remplissage clair : `#dbe9f6`
  - trait / contour : `#2c70ba`
  - ton fonce (soulignement Usage, badges de detail) : `#1f4f86`

## Convention Definition / Usage

- **Definition** = icone de base telle quelle.
- **Usage** = meme icone + un **trait souligne** sous l'icone (`stroke="#1f4f86"`, meme epaisseur que
  le trait principal), inspire de la convention deja utilisee par Modelio pour classifieur/instance
  (`class.png`/`instance.png`, `component.png`/`componentinstance.png`).
- Le trait de soulignement doit correspondre a la **largeur reelle** de l'icone (pas une largeur
  generique) - ne doit ni deborder a droite, ni toucher/coller le bas de l'icone. Si l'icone est haute
  (ex. Requirement/Concern, forme de document), **compresser verticalement le dessin** pour degager la
  place necessaire au trait plutot que de le coller au bord du canevas.

## Fidelite a la source vs redessin

- Priorite : reprendre la **silhouette** de l'icone SysML1/UML source quand elle est semantiquement
  correcte - ne jamais vectoriser automatiquement le PNG (rendu "blocky"), toujours redessiner
  proprement a la main a partir de la silhouette observee.
- **Jamais de lettre/texte grave en dur** si elle ne correspond plus au nom du concept cible. Exemples
  reels rencontres : `valuetype.png` contient "VT" (OK, reste `AttributeDefinition` = le type lui-meme) ;
  `problem.png` contient "P" (PAS OK pour `Concern` -> remplace par un pictogramme neutre) ;
  `note.png` contient "N" (PAS OK pour `Comment` -> remplace). Verifier ce point systematiquement en
  zoomant sur chaque source avant de decider de la reprendre telle quelle.
- Pour les **relations** (Association, Generalization, Dependency, Aggregation, Composition, Trace,
  Import, Connection, Flow, Allocation...) : reproduire **l'orientation et le style exact** de la
  source (ex. `itemflow.png`/`connector.png` sont HORIZONTAUX, pas en diagonale) plutot que d'imposer
  une convention generique. Verifier l'image source avant de choisir un axe.
- Certaines icones sources contiennent un badge stereotype (`<a>` pour Allocate, guillemets + lettre) :
  le conserver si le PO le demande explicitement (cas d'Allocate), sinon eviter le texte grave (cf
  point precedent).

## Cadre (frame) vs forme libre

Deux familles visuelles, a ne pas melanger :

- **Elements types/structurels** (Part, Constraint, Attribute, Enumeration, Interface, VerificationCase,
  Concern, UseCase, Viewpoint, View, Requirement, Port...) : rectangle de cadre
  `x=3 y=4 width=17 height=15` (espace 24u) + pictogramme interieur. Interface fait exception (juste un
  cercle plein, comme la notation UML "lollipop", pas de cadre).
- **Relations pures** (Association, Dependency, Generalization, Aggregation, Composition, Trace,
  Import, Connection, Flow, Allocation) : **pas de cadre**, juste le trait/fleche/glyphe, fidele a la
  source (cf section precedente).

## Relations : alignement par calcul vectoriel (obligatoire)

Erreur rencontree et corrigee : des fleches/losanges places a la main (coordonnees devinees) rendent
"tordus", pas alignes sur l'axe du trait. **Toujours** calculer le marqueur (fleche, triangle, losange)
a partir d'un vecteur direction + perpendiculaire, jamais de coordonnees approximatives :

```python
import math
TAIL = (5, 18); HEAD = (17, 6)          # axe diagonal standard pour les relations
dx, dy = HEAD[0]-TAIL[0], HEAD[1]-TAIL[1]
L = math.hypot(dx, dy)
d = (dx/L, dy/L)      # unitaire le long du trait
p = (-d[1], d[0])     # perpendiculaire unitaire
# un point "en avant de t sur l'axe, decale de w perpendiculairement" :
def offset(base, along_t, perp_t):
    return (base[0] + d[0]*along_t + p[0]*perp_t, base[1] + d[1]*along_t + p[1]*perp_t)
```
Le trait doit s'arreter exactement au point de jonction avec le marqueur (pas de chevauchement ni de
trou). Pour un noeud a plusieurs branches (ex. `MergeNode`), toutes les branches doivent rejoindre
**exactement** le meme sommet du polygone central, sinon l'effet "decale" revient.

## Tailles de trait et de pointe (penser au rendu final ~16x16 px)

- Les **pointes de fleche** doivent etre nettement plus grandes que ce qu'on dessinerait "naturellement"
  - a cette echelle une pointe fine disparait completement. Zone de wing typique validee :
  along=-6.2, perp=±3.1 (espace 24u), stroke-width de la pointe ≈ 2.1 (nettement plus epais que le
  trait, ≈1.6).
- Les **pointilles** (dependency, allocate...) doivent au contraire rester **fins et espaces**
  (`stroke-width` reduit ~1.1, `stroke-dasharray` genereux type `1.6,2.4`) - un pointille trop epais et
  trop dense devient un trait plein a petite taille.
- Les **points/dots** (ex. les 2 points de Constraint) doivent etre des cercles (`<circle>`), pas des
  petits carres - plus lisibles a petite taille - et suffisamment ecartes du reste du glyphe pour ne
  pas se fondre dedans (ecarter les elements voisins plutot que reduire les points).

## Glyphes particuliers

- **Accolades `{ }`** (Constraint) : utiliser de vraies courbes de Bezier (`C ...`), pas un zigzag de
  lignes droites - sinon ca ressemble a des crochets `[ ]`, pas des accolades. Prevoir un ecart
  suffisant entre les deux accolades pour laisser la place aux 2 points au milieu.
- **Rayons/eventail "soleil"** (View, Viewpoint) : rayons partant d'un point central mais **avec un vide
  visible entre le centre et le debut de chaque rayon** (ne jamais faire converger tous les traits en un
  point unique - ni les faire toucher) - fidele a la silhouette source qui montre deja cet espacement.
  Gap valide : ~2.6 unites (espace 24u) entre le hub et le debut de chaque trait.
- **Direction de port** (`PortUsage direction in/out/inout`) : chevron `<`, `>` ou `<>` **a l'interieur**
  du petit carre de port, jamais un badge/fleche accolee a l'exterieur du carre - illisible une fois
  reduit.
- **Conjugaison** (`ConjugatedPortDefinition`...) : reprendre le tilde `~` **normatif KerML** (meme
  longueur que le cote concerne, place au-dessus/a cote), pas une inversion miroir de la forme - plus
  juste semantiquement et plus simple a produire. Lecon retenue apres une premiere tentative (miroir)
  corrigee par le PO.
- **Glyphes-badges centres** (Assert/Invariant sur base Constraint, etc.) : le marqueur ajoute
  (coche, double-trait...) doit etre **centre au milieu du cadre**, pas cale dans un coin - plus
  lisible et plus coherent visuellement avec les accolades qui l'entourent.

## Nommage des fichiers

`sysml.<conceptDefinition-ou-Usage-en-minuscules>.svg`, ex. `sysml.partdefinition.svg`,
`sysml.portusagedirectionin.svg`. Quand deux lignes du mapping pointent vers le **meme** concept
(ex. `itemflow` et `informationflow` -> tous deux `FlowDefinition`/`FlowUsage`), ne produire qu'**un
seul** fichier, partage entre les deux lignes du mapping (`chemin_icone_sysml2` identique).

## Verifier les doublons visuels avant de presenter un lot

Avant de proposer un nouveau lot, comparer chaque nouvelle icone aux icones **deja produites** (pas
seulement entre elles). Si deux icones se ressemblent trop (meme silhouette, meme trait, meme marqueur)
- **le signaler explicitement au PO** (nommer les deux icones concernees) plutot que de laisser
  decouvrir le probleme a la revue, et proposer une piste de differenciation (ou demander laquelle
  privilegier).
- Cas reel rencontre : `Dependency` et `IncludeUseCaseUsage` utilisaient exactement le meme trait
  pointille + meme fleche -> signale au PO avant validation.
- Attention particuliere aux familles "cadre + 2-3 traits horizontaux" (Attribute, Reference,
  Enumeration) et "ligne diagonale + marqueur" (toutes les relations) qui se ressemblent facilement.

## Workflow de validation (a respecter)

1. Generer le nouveau lot directement avec le **nom final** dans `09-icones-a-valider/`.
2. Construire une page de comparaison (Artifact HTML) : icone source (PNG, `image-rendering: pixelated`)
   a cote de chaque candidat SVG, Definition et Usage cote a cote.
3. Attendre une validation **explicite et non ambigue** avant de copier vers `08-icones-sysml2/`. En cas
   de doute sur le sens d'un message court ("tous les icones valides"), **poser la question** plutot que
   de supposer - un malentendu a deja fait passer un lot en "produit" par erreur, corrige ensuite.
4. Une fois valide : copier (pas deplacer) dans `08-icones-sysml2/`, vider `09-icones-a-valider/`,
   mettre a jour la colonne `avancement` du mapping (`a_faire` / `a_valider` / `produit`).
5. Pour des corrections post-validation (retours PO sur un icone deja en production) : corriger
   directement dans `08-icones-sysml2/` et regenerer les pages de comparaison pour reverification -
   pas besoin de repasser par `09-icones-a-valider/` sauf si le changement est substantiel.

## References

- Mapping complet avec statut de chaque icone : [03-mapping-sysml1-vers-sysml2.csv](03-mapping-sysml1-vers-sysml2.csv)
  (colonnes `chemin_icone_source`, `chemin_icone_sysml2`, `avancement`).
- Sources brutes : [07-icones-sources/](07-icones-sources/) (`sysml1/` + `uml/`).
- Historique complet des decisions et corrections : [00-methodologie.md](00-methodologie.md).
