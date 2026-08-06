# -*- coding: utf-8 -*-
"""Lot 1 : parcours d'entree, hub et fin de partie.

Copie et ordre lus dans le code (OnboardingScreen, WelcomeScreen, HubScreen,
SessionRecap, modeRegistry, packs de contenu), jamais inventes.

Palette resserree : creme et encre en dominante, NEON en accent unique, JAUNE
comme seul pop de selection, DANGER pour un etat, PREMIUM sur la seule surface
d'achat. Deux couleurs saturees visibles au maximum par ecran.

Grille : marge laterale unique de 26, bloc pleine largeur de 378, deux colonnes
a 26 / 192 de 180 de large, pas vertical constant dans chaque liste.
"""
from maquette_core import (BG, BG_HAUT, SURFACE, SURFACE_HAUT, INK, INK2, INK3,
                           NEON, ORANGE_INK, JAUNE, TILE_INK, DEPTH, DANGER, SUCCES, PREMIUM,
                           CARD_FACE, CARD_RED, BODY, DISPLAY, L, H, T_TITRE, T_SOUS, T_CORPS,
                           T_LABEL, T_MICRO, bloc, bouton, dos_carte, ecran, entete, icone,
                           paragraphe, puce, texte)

# Grille commune a tout le lot.
MARGE = 26
LARGE = L - 2 * MARGE          # 378, largeur de tout bloc pleine largeur
COL2 = 192                      # pas de la grille a deux colonnes
COLW = 180
RETRAIT = 22                    # retrait du texte a l'interieur d'une carte
INTER = LARGE - 2 * RETRAIT     # 334, largeur utile dans une carte

# Ticket de caisse : objet physique, couleurs fixes copiees de SessionRecap.tsx.
PAPIER, ENCRE_TK, GRIS_TK, POINTS_TK, ROUGE_TK = "#FBF7EE", "#1c1a17", "#6e6759", "#b9b0a2", "#8E1F26"
MONO = "Space Mono, Consolas, monospace"

# Les douze modes de la grille, hors Coupe-Gorge, dans l'ordre de GAME_MODES.
MODES = [("Quitte ou Double", "brain", 2), ("Le Tableau d'Honneur", "medal", 4),
         ("La Criee", "megaphone", 2), ("Le Taulier", "crown", 3),
         ("Action ou Verite", "flame", 2), ("Je n'ai jamais", "handmetal", 2),
         ("Qui de nous", "users", 3), ("Tu preferes", "scale", 2),
         ("C'est un 10 mais", "heart", 2), ("7 Secondes", "timer", 2),
         ("Le Pilori", "gavel", 3), ("La Roue du Destin", "disc3", 2)]


# ---------------------------------------------------------------- primitives

def _pointille(x, y, w, h, r=12, couleur=None, ecart="9 7"):
    """Contour pointille : ajout de joueur, bandeau des jeux hors de portee."""
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="none" '
            f'stroke="{couleur or INK3}" stroke-width="2.5" stroke-dasharray="{ecart}"/>')


def _trait(x, y, w, couleur=None, epaisseur=2, opacite=None):
    o = f' opacity="{opacite}"' if opacite is not None else ""
    return (f'<line x1="{x}" y1="{y}" x2="{x + w}" y2="{y}" stroke="{couleur or INK3}" '
            f'stroke-width="{epaisseur}"{o}/>')


def _pastille_choix(x, y, libelle, actif):
    """Genre ou statut : selection en JAUNE, repos en surface cernee d'encre."""
    w = 26 + len(libelle) * 7.4
    if actif:
        corps = bloc(x, y, w, 34, JAUNE, r=17, cerne=TILE_INK, epaisseur=2, ombre=3)
        encre = TILE_INK
    else:
        corps = bloc(x, y, w, 34, BG_HAUT, r=17, cerne=INK3, epaisseur=2)
        encre = INK2
    return corps + "\n      " + texte(x + w / 2, y + 22, libelle, T_LABEL, BODY, encre,
                                      gras=700, ancre="middle"), w


def _sceau(x, y, t=22):
    """Sceau de cire, transpose de WaxSeal.tsx : cire, anneau, monogramme."""
    r = t / 2
    return "\n      ".join([
        f'<circle cx="{x + r}" cy="{y + r}" r="{r}" fill="#A3232B"/>',
        f'<circle cx="{x + r}" cy="{y + r}" r="{r - 2}" fill="#8E1F26"/>',
        f'<circle cx="{x + r}" cy="{y + r}" r="{r - 4}" fill="none" stroke="#701a20" stroke-width="1.6"/>',
        texte(x + r, y + r + t * 0.22, "M", t * 0.62, "Georgia, serif", "#5e151a", gras=700, ancre="middle"),
    ])


def _lune(x, y, t=18):
    """Bascule de theme : croissant obtenu par soustraction visuelle de deux disques."""
    r = t / 2
    return "\n      ".join([
        f'<circle cx="{x + r}" cy="{y + r}" r="{r}" fill="{INK}"/>',
        f'<circle cx="{x + r + t * 0.28}" cy="{y + r - t * 0.18}" r="{r * 0.86}" fill="{SURFACE}"/>',
    ])


def _rouage(x, y, t=18):
    """Reglages : disque cerne, quatre dents, moyeu evide."""
    r, c = t / 2, t / 2
    out = [f'<circle cx="{x + c}" cy="{y + c}" r="{r * 0.68}" fill="none" stroke="{INK}" stroke-width="2.4"/>']
    for dx, dy, w, h in ((0, -r, 3.4, 4.4), (0, r - 4.4, 3.4, 4.4), (-r, 0, 4.4, 3.4), (r - 4.4, 0, 4.4, 3.4)):
        out.append(f'<rect x="{x + c + dx - w / 2 + (w / 2 if abs(dx) == r else 0)}" '
                   f'y="{y + c + dy - h / 2 + (h / 2 if abs(dy) == r else 0)}" '
                   f'width="{w}" height="{h}" fill="{INK}"/>')
    return "\n      ".join(out)


def _confettis(x, y, t=64):
    """Volet 1 : cornet de fete, dessine au trait plutot qu'importe en raster."""
    u = t / 64
    return "\n      ".join([
        f'<path d="M {x + 4 * u} {y + 60 * u} L {x + 28 * u} {y + 24 * u} L {x + 40 * u} {y + 36 * u} Z" '
        f'fill="none" stroke="{TILE_INK}" stroke-width="{3.2 * u}" stroke-linejoin="round"/>',
        f'<path d="M {x + 16 * u} {y + 44 * u} L {x + 28 * u} {y + 52 * u}" stroke="{TILE_INK}" stroke-width="{2.4 * u}"/>',
        f'<rect x="{x + 44 * u}" y="{y + 8 * u}" width="{8 * u}" height="{8 * u}" fill="{TILE_INK}" transform="rotate(20 {x + 48 * u} {y + 12 * u})"/>',
        f'<rect x="{x + 30 * u}" y="{y + 2 * u}" width="{7 * u}" height="{7 * u}" fill="{TILE_INK}" transform="rotate(-15 {x + 33 * u} {y + 5 * u})"/>',
        f'<rect x="{x + 54 * u}" y="{y + 28 * u}" width="{7 * u}" height="{7 * u}" fill="{TILE_INK}" transform="rotate(35 {x + 57 * u} {y + 31 * u})"/>',
        f'<circle cx="{x + 40 * u}" cy="{y + 16 * u}" r="{3.4 * u}" fill="{TILE_INK}"/>',
        f'<circle cx="{x + 58 * u}" cy="{y + 16 * u}" r="{2.6 * u}" fill="{TILE_INK}"/>',
    ])


def _hors_ligne(x, y, t=64):
    """Volet 2 : ondes barrees, le signe hors ligne de l'app."""
    u, cxx, cyy = t / 64, x + 32 * (t / 64), y + 46 * (t / 64)
    arcs = []
    for r, e in ((10, 3.0), (20, 3.0), (30, 3.0)):
        arcs.append(f'<path d="M {cxx - r * u} {cyy - r * 0.38 * u} A {r * u} {r * u} 0 0 1 '
                    f'{cxx + r * u} {cyy - r * 0.38 * u}" fill="none" stroke="{TILE_INK}" '
                    f'stroke-width="{e * u}" stroke-linecap="round"/>')
    arcs.append(f'<circle cx="{cxx}" cy="{cyy + 4 * u}" r="{4 * u}" fill="{TILE_INK}"/>')
    arcs.append(f'<line x1="{x + 6 * u}" y1="{y + 58 * u}" x2="{x + 58 * u}" y2="{y + 6 * u}" '
                f'stroke="{TILE_INK}" stroke-width="{4.4 * u}" stroke-linecap="round"/>')
    return "\n      ".join(arcs)


def _balance(x, y, t=64):
    """Volet 3 : la balance de la table qui tranche."""
    u = t / 64
    return "\n      ".join([
        f'<line x1="{x + 32 * u}" y1="{y + 8 * u}" x2="{x + 32 * u}" y2="{y + 54 * u}" stroke="{TILE_INK}" stroke-width="{3.4 * u}"/>',
        f'<line x1="{x + 8 * u}" y1="{y + 16 * u}" x2="{x + 56 * u}" y2="{y + 16 * u}" stroke="{TILE_INK}" stroke-width="{3.4 * u}"/>',
        f'<line x1="{x + 18 * u}" y1="{y + 54 * u}" x2="{x + 46 * u}" y2="{y + 54 * u}" stroke="{TILE_INK}" stroke-width="{3.4 * u}"/>',
        f'<path d="M {x + 4 * u} {y + 32 * u} L {x + 14 * u} {y + 16 * u} L {x + 24 * u} {y + 32 * u} Z" fill="none" stroke="{TILE_INK}" stroke-width="{2.8 * u}" stroke-linejoin="round"/>',
        f'<path d="M {x + 40 * u} {y + 32 * u} L {x + 50 * u} {y + 16 * u} L {x + 60 * u} {y + 32 * u} Z" fill="none" stroke="{TILE_INK}" stroke-width="{2.8 * u}" stroke-linejoin="round"/>',
    ])


# ------------------------------------------------------------- onboarding x3

def _volet(s, cx, cy, nom, rang, glyphe, titre, corps, libelle_bouton):
    """Gabarit commun des trois volets : meme carte, meme grille, meme rythme.

    L'app donne un aplat pop different a chaque volet ; la palette resserree n'en
    garde qu'un, le JAUNE, sinon le carrousel devient un nuancier.
    """
    b = [texte(cx + MARGE, cy + 78, f"Panneau {rang} sur 3", T_LABEL, BODY, INK3),
         texte(cx + L - MARGE, cy + 78, "Passer", T_LABEL, BODY, INK2, ancre="end"),
         bloc(cx + MARGE, cy + 160, LARGE, 420, JAUNE, r=18, cerne=TILE_INK, epaisseur=3, ombre=7),
         glyphe(cx + L / 2 - 33, cy + 224, 66)]
    for i, ligne in enumerate(titre):
        b.append(texte(cx + L / 2, cy + 392 - (len(titre) - 1 - i) * 38, ligne, 30,
                       DISPLAY, TILE_INK, ancre="middle"))
    b.append(paragraphe(cx + L / 2, cy + 440, corps, T_CORPS, TILE_INK, 28, "middle"))
    for i in range(3):
        actif = i == rang - 1
        b.append(bloc(cx + L / 2 - 26 + i * 24, cy + 636, 22 if actif else 10, 10,
                      NEON if actif else INK3, r=5, epaisseur=0))
    b.append(bouton(cx + MARGE, cy + 790, LARGE, libelle_bouton, True, 62, 20))
    ecran(s, nom, cx, cy, "\n      ".join(b))


def onboarding_volet_1(s, cx, cy):
    _volet(s, cx, cy, "Onboarding - volet 1", 1, _confettis,
           ["LES MEILLEURS", "JEUX DE SOIREE"],
           ["Dans une seule app : cartes, quiz,",
            "gages, tribunal... de quoi tenir toute",
            "la tablee jusqu'au bout de la nuit."],
           "SUIVANT")


def onboarding_volet_2(s, cx, cy):
    _volet(s, cx, cy, "Onboarding - volet 2", 2, _hors_ligne,
           ["ZERO PUB,", "FONCTIONNE HORS LIGNE"],
           ["Pas de connexion, pas de pop-up :",
            "Bacchus joue meme sans reseau, du",
            "sous-sol au fond du jardin."],
           "SUIVANT")


def onboarding_volet_3(s, cx, cy):
    _volet(s, cx, cy, "Onboarding - volet 3", 3, _balance,
           ["VOTRE TABLE DECIDE"],
           ["L'app distribue des penalites, votre",
            "table decide de leur nature : jouable",
            "avec ou sans alcool."],
           "ENTRER CHEZ BACCHUS")


# ----------------------------------------------------------------- accueil x4

def _ligne_joueur(y, x0, index, nom, hauteur, champ, retrait, attr_actif=False):
    """Une ligne de la tablee : numero, champ, attributs, retrait facultatif.

    Le pas est constant d'une ligne a l'autre, et les trois controles gardent la
    meme colonne d'un ecran a l'autre.
    """
    r = hauteur / 2
    b = [bloc(x0, y, hauteur, hauteur, BG_HAUT, r=r, cerne=INK3, epaisseur=2),
         texte(x0 + r, y + r + 5, str(index), T_CORPS, BODY, INK2, gras=700, ancre="middle"),
         bloc(x0 + hauteur + 10, y, champ, hauteur, BG_HAUT, r=10, cerne=INK3, epaisseur=2),
         texte(x0 + hauteur + 26, y + r + 5, nom or f"Joueur {index}", T_CORPS, BODY,
               INK if nom else INK3)]
    bx = x0 + hauteur + 10 + champ + 8
    taille = hauteur - 8
    b.append(bloc(bx, y + 4, taille, taille, JAUNE if attr_actif else BG,
                  r=taille / 2, cerne=TILE_INK if attr_actif else INK3, epaisseur=2))
    for i in range(3):
        yy = y + 4 + taille * (0.32 + i * 0.18)
        b.append(_trait(bx + 8, yy, taille - 16, TILE_INK if attr_actif else INK2, 2))
    if retrait:
        rx = bx + taille + 8
        b.append(bloc(rx, y + 4, taille, taille, BG, r=taille / 2, cerne=INK3, epaisseur=2))
        b.append(texte(rx + taille / 2, y + 4 + taille / 2 + 5, "x", T_CORPS, BODY, INK2, ancre="middle"))
    return "\n      ".join(b)


def _note_attributs(x, y):
    return paragraphe(x, y, ["Genre et statut sont facultatifs, juste pour des jeux plus",
                             "personnalises. Rien ne quitte ton telephone."], T_MICRO, INK3, 16)


def accueil_tablee_incomplete(s, cx, cy):
    x0 = cx + MARGE + RETRAIT
    b = [texte(cx + L / 2, cy + 152, "BACCHUS", 62, DISPLAY, NEON, ancre="middle"),
         texte(cx + L / 2, cy + 186, "Les meilleurs jeux de soiree, servis au comptoir.",
               T_LABEL, BODY, INK2, ancre="middle"),
         bloc(cx + MARGE, cy + 214, LARGE, 542, SURFACE, r=18, cerne=INK, epaisseur=3, ombre=6, ombre_couleur=INK),
         puce(x0, cy + 244, "0 A LA TABLEE", NEON),
         texte(x0, cy + 314, "LA TABLEE", 22, DISPLAY, INK2)]
    for i in range(2):
        b.append(_ligne_joueur(cy + 334 + i * 62, x0, i + 1, "", 46, 232, False))
    b.append(_note_attributs(x0, cy + 486))
    b.append(_pointille(x0, cy + 518, INTER, 50, 10))
    b.append(texte(x0 + INTER / 2, cy + 549, "Une chaise de plus", T_CORPS, BODY, INK, gras=700, ancre="middle"))
    b.append(_trait(x0, cy + 592, INTER, INK3, 2, 0.6))
    b.append(bloc(x0, cy + 608, INTER, 62, BG_HAUT, r=12, cerne=INK3, epaisseur=3))
    b.append(texte(x0 + INTER / 2, cy + 647, "POUSSER LA PORTE", 20, DISPLAY, INK3, ancre="middle"))
    b.append(texte(x0 + INTER / 2, cy + 706, "Ajoute au moins 2 joueurs pour continuer",
                   T_CORPS, BODY, INK3, ancre="middle"))
    b.append(texte(cx + L / 2, cy + 806, "Ces noms seront utilises pour tous les jeux",
                   T_MICRO, BODY, INK3, ancre="middle"))
    ecran(s, "Accueil - tablee incomplete", cx, cy, "\n      ".join(b))


def accueil_tablee_remplie(s, cx, cy):
    x0 = cx + MARGE + RETRAIT
    b = [texte(cx + L / 2, cy + 128, "BACCHUS", 56, DISPLAY, NEON, ancre="middle"),
         texte(cx + L / 2, cy + 160, "Les meilleurs jeux de soiree, servis au comptoir.",
               T_LABEL, BODY, INK2, ancre="middle"),
         bloc(cx + MARGE, cy + 184, LARGE, 640, SURFACE, r=18, cerne=INK, epaisseur=3, ombre=6, ombre_couleur=INK),
         puce(x0, cy + 212, "5 A LA TABLEE", NEON),
         texte(x0, cy + 280, "LA TABLEE", 22, DISPLAY, INK2)]
    for i, nom in enumerate(["Adam", "Nawel", "Emilien", "Amina", "Sofia"]):
        b.append(_ligne_joueur(cy + 296 + i * 56, x0, i + 1, nom, 46, 186, True))
    b.append(_note_attributs(x0, cy + 592))
    b.append(_pointille(x0, cy + 618, INTER, 50, 10))
    b.append(texte(x0 + INTER / 2, cy + 649, "Une chaise de plus", T_CORPS, BODY, INK, gras=700, ancre="middle"))
    b.append(_trait(x0, cy + 688, INTER, INK3, 2, 0.6))
    b.append(bouton(x0, cy + 702, INTER, "POUSSER LA PORTE", True, 62, 20))
    b.append(texte(x0 + INTER / 2, cy + 800, "Minimum 2 joueurs, maximum 8", T_CORPS, BODY, INK3, ancre="middle"))
    b.append(texte(cx + L / 2, cy + 870, "Ces noms seront utilises pour tous les jeux",
                   T_MICRO, BODY, INK3, ancre="middle"))
    ecran(s, "Accueil - tablee remplie", cx, cy, "\n      ".join(b))


def accueil_attributs_deplies(s, cx, cy):
    x0 = cx + MARGE + RETRAIT
    b = [texte(cx + L / 2, cy + 128, "BACCHUS", 56, DISPLAY, NEON, ancre="middle"),
         texte(cx + L / 2, cy + 160, "Les meilleurs jeux de soiree, servis au comptoir.",
               T_LABEL, BODY, INK2, ancre="middle"),
         bloc(cx + MARGE, cy + 184, LARGE, 634, SURFACE, r=18, cerne=INK, epaisseur=3, ombre=6, ombre_couleur=INK),
         puce(x0, cy + 212, "3 A LA TABLEE", NEON),
         texte(x0, cy + 280, "LA TABLEE", 22, DISPLAY, INK2),
         _ligne_joueur(cy + 296, x0, 1, "Adam", 46, 186, True),
         _ligne_joueur(cy + 352, x0, 2, "Nawel", 46, 186, True, attr_actif=True)]
    # Panneau facultatif : aligne sur le champ, pas sur la carte (pl-12 dans l'app).
    px = x0 + 56
    for j, (libelles, actif) in enumerate([(["Homme", "Femme", "Autre"], None),
                                           (["Celibataire", "En couple"], "Celibataire")]):
        curseur = px
        for lib in libelles:
            svg, w = _pastille_choix(curseur, cy + 406 + j * 44, lib, lib == actif)
            b.append(svg)
            curseur += w + 8
    b.append(_ligne_joueur(cy + 500, x0, 3, "Emilien", 46, 186, True))
    b.append(_note_attributs(x0, cy + 572))
    b.append(_pointille(x0, cy + 598, INTER, 50, 10))
    b.append(texte(x0 + INTER / 2, cy + 629, "Une chaise de plus", T_CORPS, BODY, INK, gras=700, ancre="middle"))
    b.append(_trait(x0, cy + 668, INTER, INK3, 2, 0.6))
    b.append(bouton(x0, cy + 682, INTER, "POUSSER LA PORTE", True, 62, 20))
    b.append(texte(x0 + INTER / 2, cy + 782, "Minimum 2 joueurs, maximum 8", T_CORPS, BODY, INK3, ancre="middle"))
    b.append(texte(cx + L / 2, cy + 864, "Ces noms seront utilises pour tous les jeux",
                   T_MICRO, BODY, INK3, ancre="middle"))
    ecran(s, "Accueil - attributs deplies", cx, cy, "\n      ".join(b))


def accueil_tablee_pleine(s, cx, cy):
    x0 = cx + MARGE + RETRAIT
    b = [bloc(cx + MARGE, cy + 58, 44, 44, SURFACE, r=22, cerne=INK, epaisseur=2),
         texte(cx + MARGE + 22, cy + 88, "‹", T_SOUS, DISPLAY, INK, ancre="middle"),
         texte(cx + L / 2, cy + 146, "BACCHUS", 48, DISPLAY, NEON, ancre="middle"),
         texte(cx + L / 2, cy + 172, "Les meilleurs jeux de soiree, servis au comptoir.",
               T_LABEL, BODY, INK2, ancre="middle"),
         bloc(cx + MARGE, cy + 190, LARGE, 674, SURFACE, r=18, cerne=INK, epaisseur=3, ombre=6, ombre_couleur=INK),
         puce(x0, cy + 216, "8 A LA TABLEE", NEON),
         texte(x0, cy + 284, "LA TABLEE", 22, DISPLAY, INK2)]
    for i, nom in enumerate(["Adam", "Nawel", "Emilien", "Amina", "Sofia", "Paul", "Lea", "Karim"]):
        b.append(_ligne_joueur(cy + 300 + i * 50, x0, i + 1, nom, 42, 198, True))
    # A huit joueurs, l'app retire le bouton d'ajout : le plafond se voit, il ne
    # se lit pas dans un message d'erreur.
    b.append(_note_attributs(x0, cy + 716))
    b.append(_trait(x0, cy + 746, INTER, INK3, 2, 0.6))
    b.append(bouton(x0, cy + 760, INTER, "POUSSER LA PORTE", True, 62, 20))
    b.append(texte(x0 + INTER / 2, cy + 850, "Minimum 2 joueurs, maximum 8", T_CORPS, BODY, INK3, ancre="middle"))
    ecran(s, "Accueil - tablee pleine", cx, cy, "\n      ".join(b))


# --------------------------------------------------------------------- hub x3

def _entete_hub(cx, cy, joueurs):
    """Titre, promesse et barre de commandes : identique sur les deux vues du hub."""
    b = [texte(cx + L / 2, cy + 96, "BACCHUS", 46, DISPLAY, NEON, ancre="middle"),
         paragraphe(cx + L / 2, cy + 122, ["Au menu ce soir : 13 jeux, servis",
                                           "sans moderation de mauvaise foi."],
                    T_LABEL, INK2, 18, "middle")]
    y = cy + 156
    for x, w, lab in ((cx + MARGE, 158, f"{joueurs} joueurs - Modifier"), (cx + MARGE + 166, 116, "Mes regles")):
        b.append(bloc(x, y, w, 38, SURFACE, r=19, cerne=INK, epaisseur=2, ombre=3, ombre_couleur=INK))
        b.append(texte(x + w / 2, y + 25, lab, T_LABEL, BODY, INK, gras=700, ancre="middle"))
    for i, glyphe in enumerate((_lune, _rouage)):
        x = cx + MARGE + 290 + i * 48
        b.append(bloc(x, y, 40, 38, SURFACE, r=19, cerne=INK, epaisseur=2, ombre=3, ombre_couleur=INK))
        b.append(glyphe(x + 11, y + 10, 18))
    return b


def _tuile_geante(cx, cy, y):
    """Le Coupe-Gorge : seule surface en NEON, c'est l'accent unique de l'ecran."""
    return [bloc(cx + MARGE, y, LARGE, 156, NEON, r=16, cerne=TILE_INK, epaisseur=3, ombre=7),
            texte(cx + MARGE + 20, y + 46, "♠", 38, BODY, TILE_INK),
            texte(cx + MARGE + 20, y + 88, "LE COUPE-GORGE", 34, DISPLAY, TILE_INK),
            texte(cx + MARGE + 20, y + 110, "52 cartes - 4 regles - 0 pitie.", T_LABEL, BODY, TILE_INK, gras=700),
            bloc(cx + MARGE + 20, y + 120, 96, 30, TILE_INK, r=15),
            texte(cx + MARGE + 68, y + 141, "JOUER", T_LABEL, DISPLAY, CARD_FACE, ancre="middle"),
            texte(cx + MARGE + 130, y + 141, "Regles", T_LABEL, BODY, TILE_INK, gras=700)]


def _tuile_mode(px, py, titre, glyphe):
    """Tuile de mode : surface neutre cernee d'encre, pastille d'aide a droite."""
    return "\n      ".join([
        bloc(px, py, COLW, 68, SURFACE, r=14, cerne=INK, epaisseur=3, ombre=5, ombre_couleur=INK),
        icone(glyphe, px + 12, py + 9, 26),
        bloc(px + COLW - 38, py + 8, 28, 28, BG_HAUT, r=14, cerne=INK, epaisseur=2),
        texte(px + COLW - 24, py + 27, "?", T_LABEL, DISPLAY, INK, ancre="middle"),
        texte(px + 12, py + 56, titre.upper(), 14, DISPLAY, INK),
    ])


def _pied_legal(cx, cy):
    return [texte(cx + L / 2, cy + 850, "Jouez responsable : Bacchus veille sur sa tablee.",
                  T_MICRO, BODY, INK3, ancre="middle"),
            texte(cx + L / 2, cy + 876, "Mentions legales - Confidentialite - CGU / CGV - Cookies",
                  T_MICRO, BODY, INK3, ancre="middle", espacement=0.4)]


def hub_grille_complete(s, cx, cy):
    b = _entete_hub(cx, cy, 5)
    b += _tuile_geante(cx, cy, cy + 206)
    for i, (titre, glyphe, _) in enumerate(MODES):
        px = cx + MARGE + (i % 2) * COL2
        b.append(_tuile_mode(px, cy + 378 + (i // 2) * 76, titre, glyphe))
    b += _pied_legal(cx, cy)
    ecran(s, "Hub - grille complete", cx, cy, "\n      ".join(b))


def hub_jeux_hors_de_portee(s, cx, cy):
    ouverts = [m for m in MODES if m[2] <= 2]
    fermes = [m for m in MODES if m[2] > 2]
    seuil = min(m[2] for m in fermes)
    b = _entete_hub(cx, cy, 2)
    b.append(texte(cx + L / 2, cy + 216, "Il faut au moins 3 joueurs pour lancer Le Taulier.",
                   T_LABEL, BODY, DANGER, gras=700, ancre="middle", espacement=0.3))
    b += _tuile_geante(cx, cy, cy + 232)
    for i, (titre, glyphe, _) in enumerate(ouverts):
        px = cx + MARGE + (i % 2) * COL2
        b.append(_tuile_mode(px, cy + 404 + (i // 2) * 76, titre, glyphe))
    # Les modes hors de portee ne sont pas affiches : on annonce seulement combien
    # s'ouvrent, et a partir de combien de joueurs.
    b.append(_pointille(cx + MARGE, cy + 712, LARGE, 66, 14, INK3, "10 8"))
    b.append(texte(cx + L / 2, cy + 740, f"{len(fermes)} JEUX DE PLUS", T_MICRO, BODY, INK3,
                   gras=700, ancre="middle", espacement=1.4))
    b.append(texte(cx + L / 2, cy + 762, f"a partir de {seuil} joueurs - ajouter du monde a la tablee",
                   T_LABEL, BODY, INK, ancre="middle"))
    b += _pied_legal(cx, cy)
    ecran(s, "Hub - jeux hors de portee", cx, cy, "\n      ".join(b))


def hub_selecteur_de_pack(s, cx, cy):
    """Superposition plein ecran : le choix du pack d'Action ou Verite.

    Un pack gratuit et un pack premium par mode, c'est ce que contient le
    catalogue reel ; la liste ne se remplit pas de packs inventes.
    """
    x0 = cx + MARGE + RETRAIT
    b = [entete(cx, cy, "ACTION OU VERITE"),
         texte(cx + MARGE, cy + 152, "Aveu au comptoir ou gage, choisis", T_LABEL, BODY, INK2)]

    # Les deux cartes partagent exactement la meme grille interne : titre sur deux
    # lignes, sous-titre, nombre de cartes, badge en haut a droite.
    b.append(bloc(cx + MARGE, cy + 172, LARGE, 268, SURFACE, r=16, cerne=INK, epaisseur=3, ombre=6, ombre_couleur=INK))
    b.append(texte(x0, cy + 250, "ACTION OU VERITE", 28, DISPLAY, INK))
    b.append(texte(x0, cy + 286, "CLASSIQUE", 28, DISPLAY, INK))
    b.append(texte(x0, cy + 322, "Choisis ton camp", T_CORPS, BODY, INK2))
    b.append(texte(x0, cy + 356, "80 cartes", T_LABEL, BODY, INK3))

    # Pack premium : fond sourd, sceau de cire, aucune opacite sur le texte, qui
    # doit rester lisible meme verrouille.
    b.append(bloc(cx + MARGE, cy + 456, LARGE, 268, BG_HAUT, r=16, cerne=INK3, epaisseur=3))
    b.append(texte(x0, cy + 534, "ACTION OU VERITE", 28, DISPLAY, INK2))
    b.append(texte(x0, cy + 570, "EXTREME", 28, DISPLAY, INK2))
    b.append(texte(x0, cy + 606, "Interdit aux timides", T_CORPS, BODY, INK3))
    b.append(texte(x0, cy + 640, "80 cartes", T_LABEL, BODY, INK3))
    bx = cx + MARGE + LARGE - RETRAIT - 128
    b.append(bloc(bx, cy + 486, 128, 38, SURFACE, r=19, cerne=PREMIUM, epaisseur=2))
    b.append(_sceau(bx + 9, cy + 494, 22))
    b.append(texte(bx + 42, cy + 511, "PREMIUM", T_MICRO, BODY, PREMIUM, gras=700, espacement=1.4))
    ecran(s, "Hub - selecteur de pack", cx, cy, "\n      ".join(b))


# ---------------------------------------------------------------- addition x2

def _tk(x, y, s, taille=12.5, couleur=None, ancre="start", gras=None, espacement=None):
    return texte(x, y, s, taille, MONO, couleur or ENCRE_TK, gras=gras, ancre=ancre,
                 espacement=espacement)


def _regle_ticket(x, y, w):
    return (f'<line x1="{x}" y1="{y}" x2="{x + w}" y2="{y}" stroke="{POINTS_TK}" '
            f'stroke-width="1.4" stroke-dasharray="4 4"/>')


def _article(x0, x1, y, gauche, droite, taille=12.5, gras=None, suffixe=None):
    """Ligne d'article : libelle a gauche, montant a droite, conduite pointillee.

    Les pointilles sont un trait tirete et non soixante points de texte : meme
    lecture, un noeud au lieu de soixante.
    """
    wg, wd = len(gauche) * taille * 0.6, len(droite) * taille * 0.6
    out = [_tk(x0, y, gauche, taille, gras=gras)]
    if suffixe:
        ws = len(suffixe) * taille * 0.6
        out.append(_tk(x1, y, suffixe, taille, ROUGE_TK, ancre="end", gras=gras))
        out.append(_tk(x1 - ws - 4, y, droite, taille, ancre="end", gras=gras))
        wd += ws + 4
    else:
        out.append(_tk(x1, y, droite, taille, ancre="end", gras=gras))
    if x1 - wd - 8 > x0 + wg + 8:
        out.append(f'<line x1="{x0 + wg + 6}" y1="{y - 4}" x2="{x1 - wd - 6}" y2="{y - 4}" '
                   f'stroke="{POINTS_TK}" stroke-width="1.4" stroke-dasharray="1.5 3.5"/>')
    return "\n      ".join(out)


def _contour_ticket(x, y, w, h, dent=8, n=25):
    """Bords crantes du ticket, transposes du clip-path de SessionRecap.tsx."""
    pts = [(x + w * i / n, y + (dent if i % 2 == 0 else 0)) for i in range(n + 1)]
    pts += [(x + w * i / n, y + h - (dent if i % 2 else 0)) for i in range(n, -1, -1)]
    return "M " + " L ".join(f"{px:.1f} {py:.1f}" for px, py in pts) + " Z"


def _code_barres(x, y, w, h):
    """Faux code-barres : largeurs derivees des scores, comme dans le composant."""
    motif = [1, 3, 2, 1, 2, 3, 1, 2, 2, 1, 3, 2, 1, 1, 3, 2, 2, 1, 2, 3, 1, 2, 1, 3, 2, 1, 2, 2, 3, 1, 2, 1, 3, 2, 1, 2]
    out, curseur = [], x
    for i, m in enumerate(motif):
        lw = 1 + m
        hh = h * (0.7 if i % 5 == 4 else 1)
        out.append(f'<rect x="{curseur:.1f}" y="{y + h - hh:.1f}" width="{lw}" height="{hh:.1f}" fill="{ENCRE_TK}"/>')
        curseur += lw + 2
    return "\n      ".join(out)


def _ticket(cx, cy, yt, hauteur, lignes):
    """Le ticket : papier fixe, cerne et ombre TILE_INK, legere rotation d'objet pose."""
    x = cx + MARGE
    contour = _contour_ticket(x, yt, LARGE, hauteur)
    ombre = _contour_ticket(x + 6, yt + 6, LARGE, hauteur)
    return "\n      ".join([
        f'<g transform="rotate(-1.2 {x + LARGE / 2} {yt + hauteur / 2})">',
        f'<path d="{ombre}" fill="{TILE_INK}"/>',
        f'<path d="{contour}" fill="{PAPIER}" stroke="{TILE_INK}" stroke-width="3"/>',
        "\n      ".join(lignes),
        '</g>',
    ])


def _entete_ticket(x0, x1, yt, table):
    milieu = (x0 + x1) / 2
    return [_tk(milieu, yt + 38, "BACCHUS", 18, gras=700, ancre="middle", espacement=1.2),
            _tk(milieu, yt + 56, "Au coin du comptoir - Chevilly-Larue", 10.5, GRIS_TK, "middle"),
            _tk(milieu, yt + 70, "bacchus.beloucif.com", 10.5, GRIS_TK, "middle"),
            _regle_ticket(x0, yt + 86, x1 - x0),
            _tk(x0, yt + 104, "06/08/2026  22:41", 10.5, GRIS_TK),
            _tk(x1, yt + 104, f"TABLE DE {table}", 10.5, GRIS_TK, "end"),
            _regle_ticket(x0, yt + 118, x1 - x0),
            _tk(x0, yt + 136, "ARTICLE", 10.5, GRIS_TK),
            _tk(x1, yt + 136, "PENALITES", 10.5, GRIS_TK, "end")]


# Une partie du Coupe-Gorge : penalites simples et penalites majeures.
PARTIE = [("Adam", 12, 2), ("Nawel", 9, 1), ("Emilien", 8, 0), ("Amina", 6, 0), ("Sofia", 3, 0)]
# Le cumul de la soiree, tous modes confondus, tenu par nightStore.
SOIREE = [("Nawel", 41), ("Adam", 34), ("Emilien", 22), ("Amina", 18), ("Sofia", 11)]


def fin_de_partie_addition(s, cx, cy):
    x0, x1, yt, ht = cx + MARGE + 18, cx + MARGE + LARGE - 18, cy + 108, 508
    milieu = (x0 + x1) / 2
    lignes = _entete_ticket(x0, x1, yt, len(PARTIE))
    for i, (nom, gorgees, majeures) in enumerate(PARTIE):
        lignes.append(_article(x0, x1, yt + 160 + i * 24, f"{i + 1}. {nom}" + (" *" if i == 0 else ""),
                               str(gorgees), 12.5, 700 if i == 0 else None,
                               f"+{majeures} MAJ" if majeures else None))
    lignes.append(_regle_ticket(x0, yt + 292, x1 - x0))
    lignes.append(_tk(x0, yt + 316, "TOTAL", 16, gras=700))
    lignes.append(_tk(x1, yt + 316, "53", 16, gras=700, ancre="end"))
    lignes.append(_tk(x0, yt + 336, "dont penalites majeures", 10.5, GRIS_TK))
    lignes.append(_tk(x1, yt + 336, "3", 10.5, GRIS_TK, "end"))
    lignes.append(_regle_ticket(x0, yt + 352, x1 - x0))
    lignes.append(_tk(milieu, yt + 376, "* Adam est elu", 11, ancre="middle"))
    lignes.append(_tk(milieu, yt + 392, "CHAMPION DE LA TABLEE", 11, ROUGE_TK, "middle", 700, 0.8))
    lignes.append(_tk(milieu, yt + 412, "Ici, tout le monde regle l'addition.", 10.5, GRIS_TK, "middle"))
    lignes.append(_code_barres(x0 + 44, yt + 430, x1 - x0 - 88, 36))
    lignes.append(_tk(milieu, yt + 486, "MERCI DE VOTRE VISITE", 10, GRIS_TK, "middle", None, 3))

    b = [_ticket(cx, cy, yt, ht, lignes),
         bloc(cx + MARGE, cy + 648, 185, 54, NEON, r=27, cerne=TILE_INK, epaisseur=3, ombre=5),
         texte(cx + MARGE + 92, cy + 682, "PARTAGER", 18, DISPLAY, TILE_INK, ancre="middle"),
         bloc(cx + MARGE + 193, cy + 648, 185, 54, SURFACE, r=27, cerne=INK, epaisseur=3, ombre=5, ombre_couleur=INK),
         texte(cx + MARGE + 285, cy + 682, "REVANCHE", 18, DISPLAY, INK, ancre="middle"),
         bloc(cx + MARGE, cy + 716, LARGE, 54, BG, r=27, cerne=INK3, epaisseur=2),
         texte(cx + L / 2, cy + 750, "RETOUR A L'ACCUEIL", 18, DISPLAY, INK2, ancre="middle"),
         texte(cx + L / 2, cy + 822, "Jouez responsable : Bacchus veille sur sa tablee.",
               T_MICRO, BODY, INK3, ancre="middle")]
    ecran(s, "Fin de partie - l'addition", cx, cy, "\n      ".join(b))


def fin_de_partie_ardoise(s, cx, cy):
    x0, x1, yt, ht = cx + MARGE + 18, cx + MARGE + LARGE - 18, cy + 68, 648
    milieu = (x0 + x1) / 2
    lignes = _entete_ticket(x0, x1, yt, len(PARTIE))
    for i, (nom, gorgees, majeures) in enumerate(PARTIE):
        lignes.append(_article(x0, x1, yt + 158 + i * 22, f"{i + 1}. {nom}" + (" *" if i == 0 else ""),
                               str(gorgees), 12.5, 700 if i == 0 else None,
                               f"+{majeures} MAJ" if majeures else None))
    lignes.append(_regle_ticket(x0, yt + 268, x1 - x0))
    lignes.append(_tk(x0, yt + 290, "TOTAL", 15, gras=700))
    lignes.append(_tk(x1, yt + 290, "53", 15, gras=700, ancre="end"))
    lignes.append(_tk(x0, yt + 308, "dont penalites majeures", 10.5, GRIS_TK))
    lignes.append(_tk(x1, yt + 308, "3", 10.5, GRIS_TK, "end"))
    lignes.append(_regle_ticket(x0, yt + 322, x1 - x0))
    # L'ardoise : cumul cross-modes, visible seulement a partir de la 2e partie.
    lignes.append(_tk(x0, yt + 342, "ARDOISE DE LA SOIREE", 10.5, GRIS_TK))
    lignes.append(_tk(x1, yt + 342, "3 parties - 3 jeux", 10.5, GRIS_TK, "end"))
    for i, (nom, total) in enumerate(SOIREE):
        lignes.append(_article(x0, x1, yt + 364 + i * 20, nom, str(total), 12.5, 700 if i == 0 else None))
    lignes.append(_tk(x0, yt + 482, "cumul de la maison", 10.5, GRIS_TK))
    lignes.append(_tk(x1, yt + 482, "126", 10.5, GRIS_TK, "end"))
    lignes.append(_regle_ticket(x0, yt + 496, x1 - x0))
    lignes.append(_tk(milieu, yt + 518, "* Adam est elu", 11, ancre="middle"))
    lignes.append(_tk(milieu, yt + 534, "CHAMPION DE LA TABLEE", 11, ROUGE_TK, "middle", 700, 0.8))
    lignes.append(_tk(milieu, yt + 552, "Nawel mene l'ardoise de la soiree (41)", 10.5, ancre="middle"))
    lignes.append(_tk(milieu, yt + 568, "Ici, tout le monde regle l'addition.", 10.5, GRIS_TK, "middle"))
    lignes.append(_code_barres(x0 + 44, yt + 574, x1 - x0 - 88, 30))
    lignes.append(_tk(milieu, yt + 622, "MERCI DE VOTRE VISITE", 10, GRIS_TK, "middle", None, 3))

    b = [_ticket(cx, cy, yt, ht, lignes),
         bloc(cx + MARGE, cy + 742, 185, 52, NEON, r=26, cerne=TILE_INK, epaisseur=3, ombre=5),
         texte(cx + MARGE + 92, cy + 775, "PARTAGER", 18, DISPLAY, TILE_INK, ancre="middle"),
         bloc(cx + MARGE + 193, cy + 742, 185, 52, SURFACE, r=26, cerne=INK, epaisseur=3, ombre=5, ombre_couleur=INK),
         texte(cx + MARGE + 285, cy + 775, "REVANCHE", 18, DISPLAY, INK, ancre="middle"),
         bloc(cx + MARGE, cy + 808, LARGE, 52, BG, r=26, cerne=INK3, epaisseur=2),
         texte(cx + L / 2, cy + 841, "RETOUR A L'ACCUEIL", 18, DISPLAY, INK2, ancre="middle"),
         texte(cx + L / 2, cy + 884, "Jouez responsable : Bacchus veille sur sa tablee.",
               T_MICRO, BODY, INK3, ancre="middle")]
    ecran(s, "Fin de partie - ardoise de la soiree", cx, cy, "\n      ".join(b))


ECRANS = [onboarding_volet_1, onboarding_volet_2, onboarding_volet_3,
          accueil_tablee_incomplete, accueil_tablee_remplie, accueil_attributs_deplies,
          accueil_tablee_pleine, hub_grille_complete, hub_jeux_hors_de_portee,
          hub_selecteur_de_pack, fin_de_partie_addition, fin_de_partie_ardoise]
