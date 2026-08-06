# -*- coding: utf-8 -*-
"""Lot 3 : les surfaces de jeu des huit modes a ecran dedie, plus les regles.

CE QUE CE MODULE CORRIGE PAR RAPPORT AU LOT PRECEDENT.

  - PALETTE. L'ancienne planche posait rose, bleu, lime et jaune a poids egal :
    sans dominante, rien ne ressort et tout se vaut. Ici la base est BG + INK,
    l'accent unique est NEON (actions primaires et titre de mode), le seul pop
    tolere est JAUNE (selection, mise en avant), DANGER et SUCCES ne disent
    qu'un ETAT, jamais un decor. CARD_FACE et CARD_RED restent pour les cartes,
    qui sont des objets physiques. Deux couleurs saturees visibles au maximum.
  - ALIGNEMENT. Une seule marge laterale (M = 26), donc tout bloc pleine largeur
    fait L - 52 et commence a cx + M. La grille a deux colonnes reprend le pas
    des modules voisins (26 / 226, colonnes de 178) : c'est le seul couple qui
    garde la marge de 26 des DEUX cotes, ce qu'un pas de 192 casserait a droite.
  - RYTHME. Les listes empilees d'un meme ecran partagent toutes le meme pas
    vertical, et le pied de page est toujours aux memes ordonnees (PIED_HAUT /
    PIED_BAS), pour que les ecrans se lisent en colonne sans sautiller.
  - ENCRE. Un fond qui reste clair dans les deux themes (JAUNE, NEON, CARD_FACE)
    porte cerne et ombre TILE_INK, fixes. Un fond qui s'inverse (SURFACE, BG)
    porte INK. Les deux ne se melangent jamais sur un meme aplat.

La copie est celle de l'application : QuizScreen, RankingScreen, AuctionScreen,
TribunalScreen, WouldYouRatherScreen, RouletteScreen, PromptGameScreen,
ModeRulesScreen, plus les contenus de src/content et le registre des modes.
Comme dans les modules voisins de la maquette, elle est ecrite sans accents.
"""
import math

from maquette_core import (BG, BG_HAUT, BODY, CARD_FACE, CARD_RED, DANGER, DISPLAY, H, INK,
                           INK2, INK3, JAUNE, L, NEON, ORANGE_INK, SUCCES, SURFACE,
                           SURFACE_HAUT, TILE_INK, T_CORPS, T_LABEL, T_MICRO, T_SOUS,
                           T_TITRE, bloc, bouton, ecran, entete, icone, paragraphe, puce,
                           texte)

# --------------------------------------------------------------------------
# Grille commune. Rien ne se pose en dehors de ces reperes.
# --------------------------------------------------------------------------
M = 26                  # marge laterale unique
W = L - 2 * M           # largeur d'un bloc pleine largeur : 378
CA, CB, CW = 26, 226, 178   # grille a deux colonnes, marges de 26 des deux cotes

Y_MODE = 118            # surtitre de mode (NEON)
Y_NOM = 152             # nom du joueur en cours (DISPLAY 30)
Y_SOUS = 176            # sous-titre de l'entete

PIED_HAUT, PIED_BAS = 712, 788   # deux boutons empiles, hauteur 64
H_BOUTON = 64
Y_LIEN = 886            # lien discret de bas d'ecran

CENTRE = L / 2


# --------------------------------------------------------------------------
# Primitives locales. Le jeu d'icones embarque (13 PNG) ne couvre ni l'oeil,
# ni la coche, ni la corbeille : on les dessine plutot que de detourner une
# icone qui dirait autre chose.
# --------------------------------------------------------------------------
def _croix(x, y, t=16, couleur=INK, ep=3):
    d = t / 2
    return (f'<line x1="{x - d}" y1="{y - d}" x2="{x + d}" y2="{y + d}" stroke="{couleur}" '
            f'stroke-width="{ep}" stroke-linecap="round"/>\n      '
            f'<line x1="{x + d}" y1="{y - d}" x2="{x - d}" y2="{y + d}" stroke="{couleur}" '
            f'stroke-width="{ep}" stroke-linecap="round"/>')


def _coche(x, y, t=26, couleur=SUCCES, ep=4):
    """Coche centree sur (x, y). Double le sens porte par la couleur : un
    verdict se distingue avant d'etre lu, et rouge contre vert est justement
    le couple que la protanopie confond."""
    return (f'<polyline points="{x - t / 2:.1f},{y:.1f} {x - t / 8:.1f},{y + t / 3:.1f} '
            f'{x + t / 2:.1f},{y - t / 2.4:.1f}" fill="none" stroke="{couleur}" '
            f'stroke-width="{ep}" stroke-linecap="round" stroke-linejoin="round"/>')


def _oeil(x, y, t=48, barre=False, couleur=TILE_INK):
    """Oeil ouvert ou barre, pour les ecrans de passage du telephone."""
    w, h = t, t * 0.46
    d = (f'M {x - w / 2:.1f} {y:.1f} Q {x:.1f} {y - h:.1f} {x + w / 2:.1f} {y:.1f} '
         f'Q {x:.1f} {y + h:.1f} {x - w / 2:.1f} {y:.1f} Z')
    out = [f'<path d="{d}" fill="none" stroke="{couleur}" stroke-width="3.5"/>',
           f'<circle cx="{x}" cy="{y}" r="{t * 0.16:.1f}" fill="{couleur}"/>']
    if barre:
        out.append(f'<line x1="{x - w / 2:.1f}" y1="{y + h * 0.9:.1f}" x2="{x + w / 2:.1f}" '
                   f'y2="{y - h * 0.9:.1f}" stroke="{couleur}" stroke-width="4" '
                   f'stroke-linecap="round"/>')
    return "\n      ".join(out)


def _signe(x, y, plus=True, t=22, couleur=INK):
    out = [f'<rect x="{x - t / 2}" y="{y - 2}" width="{t}" height="4" rx="2" fill="{couleur}"/>']
    if plus:
        out.append(f'<rect x="{x - 2}" y="{y - t / 2}" width="4" height="{t}" rx="2" fill="{couleur}"/>')
    return "\n      ".join(out)


def _corbeille(x, y, t=18, couleur=INK3):
    d = t / 2
    return "\n      ".join([
        f'<rect x="{x - d + 2}" y="{y - d + 4}" width="{t - 4}" height="{t - 2}" rx="2" '
        f'fill="none" stroke="{couleur}" stroke-width="2"/>',
        f'<line x1="{x - d}" y1="{y - d + 4}" x2="{x + d}" y2="{y - d + 4}" stroke="{couleur}" '
        f'stroke-width="2" stroke-linecap="round"/>',
        f'<line x1="{x - 3}" y1="{y - d}" x2="{x + 3}" y2="{y - d}" stroke="{couleur}" '
        f'stroke-width="2" stroke-linecap="round"/>',
    ])


def _parchemin(x, y, t=46, couleur=NEON):
    """Rouleau de regles. Remplace l'icone lucide ScrollText de ModeRulesScreen."""
    w, h = t, t * 0.82
    return "\n      ".join([
        f'<rect x="{x - w / 2}" y="{y - h / 2}" width="{w}" height="{h}" rx="6" fill="none" '
        f'stroke="{couleur}" stroke-width="3"/>',
        f'<line x1="{x - w / 2 + 9}" y1="{y - h / 2 + 11}" x2="{x + w / 2 - 9}" '
        f'y2="{y - h / 2 + 11}" stroke="{couleur}" stroke-width="3" stroke-linecap="round"/>',
        f'<line x1="{x - w / 2 + 9}" y1="{y}" x2="{x + w / 2 - 9}" y2="{y}" stroke="{couleur}" '
        f'stroke-width="3" stroke-linecap="round"/>',
        f'<line x1="{x - w / 2 + 9}" y1="{y + h / 2 - 11}" x2="{x + w / 2 - 14}" '
        f'y2="{y + h / 2 - 11}" stroke="{couleur}" stroke-width="3" stroke-linecap="round"/>',
    ])


def _interrupteur(x, y, actif=True):
    """Interrupteur de la feuille Mes themes. Rail clair fixe quand il est actif,
    donc cerne et bouton en TILE_INK ; rail themable quand il ne l'est pas."""
    rail = bloc(x, y, 52, 26, JAUNE if actif else BG_HAUT, r=13,
                cerne=TILE_INK if actif else INK, epaisseur=2)
    cx_ = x + 38 if actif else x + 14
    return rail + "\n      " + (f'<circle cx="{cx_}" cy="{y + 13}" r="8" '
                                f'fill="{TILE_INK if actif else INK}"/>')


def _secteur(ox, oy, r, a0, a1, fond):
    x0, y0 = ox + r * math.cos(math.radians(a0)), oy + r * math.sin(math.radians(a0))
    x1, y1 = ox + r * math.cos(math.radians(a1)), oy + r * math.sin(math.radians(a1))
    grand = 1 if (a1 - a0) > 180 else 0
    return (f'<path d="M {ox:.1f} {oy:.1f} L {x0:.1f} {y0:.1f} A {r} {r} 0 {grand} 1 '
            f'{x1:.1f} {y1:.1f} Z" fill="{fond}"/>')


def _roue(ox, oy, r, depart=0.0):
    """Roue a huit secteurs. Les quatre aplats pop de l'app sont ramenes a deux
    tons : la regle de palette interdit rose, bleu et lime en decor, et huit
    secteurs alternes se lisent de toute facon mieux en deux tons qu'en quatre."""
    out, pas = [], 45.0
    for i in range(8):
        a0 = depart + i * pas - 90
        out.append(_secteur(ox, oy, r, a0, a0 + pas, JAUNE if i % 2 == 0 else CARD_FACE))
    for i in range(8):
        a = math.radians(depart + i * pas - 90)
        out.append(f'<line x1="{ox}" y1="{oy}" x2="{ox + r * math.cos(a):.1f}" '
                   f'y2="{oy + r * math.sin(a):.1f}" stroke="{TILE_INK}" stroke-width="3"/>')
    out.append(f'<circle cx="{ox}" cy="{oy}" r="{r}" fill="none" stroke="{INK}" stroke-width="4"/>')
    # Pointeur fixe : il borde la PAGE, qui s'inverse, donc il suit INK et non TILE_INK.
    out.append(f'<path d="M {ox - 13} {oy - r - 18} L {ox + 13} {oy - r - 18} L {ox} {oy - r + 8} Z" '
               f'fill="{INK}"/>')
    hub = 30 if r > 130 else 26
    out.append(f'<circle cx="{ox}" cy="{oy}" r="{hub}" fill="{SURFACE}" stroke="{INK}" stroke-width="3"/>')
    out.append(icone("disc3", ox - hub * 0.5, oy - hub * 0.5, hub))
    return out


# --------------------------------------------------------------------------
# Fragments de gabarit partages par les ecrans de jeu.
# --------------------------------------------------------------------------
def _coins(cx, cy, regles=True):
    """QuitButton en haut a gauche, ModeRulesButton en haut a droite."""
    out = [bloc(cx + M, cy + 52, 40, 40, SURFACE, r=20, cerne=INK, epaisseur=2),
           _croix(cx + M + 20, cy + 72, 15, INK)]
    if regles:
        out += [bloc(cx + L - M - 40, cy + 52, 40, 40, SURFACE, r=20, cerne=INK, epaisseur=2),
                texte(cx + L - M - 20, cy + 79, "?", T_SOUS, DISPLAY, INK, ancre="middle")]
    return out


def _tete(cx, cy, mode, joueur=None, sous=None):
    out = [texte(cx + CENTRE, cy + Y_MODE, mode, T_LABEL, DISPLAY, NEON, ancre="middle",
                 espacement=1.6)]
    if joueur:
        out.append(texte(cx + CENTRE, cy + Y_NOM, joueur, T_TITRE, DISPLAY, INK, ancre="middle"))
    if sous:
        out.append(texte(cx + CENTRE, cy + Y_SOUS, sous, T_LABEL, BODY, INK2, ancre="middle"))
    return out


def _carte(x, y, w, h, cerne=TILE_INK, epaisseur=3):
    """Carte a jouer : objet physique, donc fond fixe et encre fixe."""
    return bloc(x, y, w, h, CARD_FACE, r=16, cerne=cerne, epaisseur=epaisseur, ombre=7,
                ombre_couleur=TILE_INK)


def _panneau(x, y, w, h, cerne=INK, epaisseur=2):
    return bloc(x, y, w, h, SURFACE, r=14, cerne=cerne, epaisseur=epaisseur, ombre=3,
                ombre_couleur=INK)


def _pied1(cx, cy, libelle, taille=19):
    return bouton(cx + M, cy + PIED_BAS, W, libelle, True, H_BOUTON, taille)


def _pied2(cx, cy, haut, bas, t_haut=19, t_bas=19, haut_primaire=True):
    return [bouton(cx + M, cy + PIED_HAUT, W, haut, haut_primaire, H_BOUTON, t_haut),
            bouton(cx + M, cy + PIED_BAS, W, bas, not haut_primaire, H_BOUTON, t_bas)]


def _pied_desactive(cx, cy, libelle, taille=18):
    """Bouton primaire inactif : l'ombre disparait avec l'aplat, sinon le bouton
    semble encore enfonçable."""
    return [bloc(cx + M, cy + PIED_BAS, W, H_BOUTON, SURFACE, r=12, cerne=INK, epaisseur=3,
                 opacite=0.45),
            texte(cx + CENTRE, cy + PIED_BAS + 40, libelle, taille, DISPLAY, INK3, ancre="middle")]


def _lien(cx, cy, libelle, y=None):
    return texte(cx + CENTRE, cy + (y or Y_LIEN), libelle, T_LABEL, DISPLAY, INK3,
                 ancre="middle", espacement=1.4)


def _pastille_creuse(x, y, libelle, w, couleur=TILE_INK, fond=CARD_FACE, h=30, taille=T_MICRO):
    """Pastille non pleine, posee sur une carte : elle ne consomme pas de pop."""
    return (bloc(x, y, w, h, fond, r=h / 2, cerne=couleur, epaisseur=2) + "\n      "
            + texte(x + w / 2, y + h / 2 + 4, libelle, taille, DISPLAY, couleur, ancre="middle"))


# ==========================================================================
# QUITTE OU DOUBLE - QuizScreen
# ==========================================================================
QUESTION = ["Combien y a-t-il de pays", "frontaliers de la France", "metropolitaine ?"]
REPONSE = ["8 (Belgique, Luxembourg, Allemagne,", "Suisse, Italie, Monaco, Espagne,", "Andorre)"]


def _quiz_socle(cx, cy):
    """Entete commune aux trois etats : cagnotte du joueur et tour sur total."""
    b = _coins(cx, cy) + _tete(cx, cy, "QUITTE OU DOUBLE", "NAWEL")
    b += [puce(cx + 130, cy + 168, "CAGNOTTE : 6", JAUNE),
          texte(cx + 254, cy + 189, "TOUR 3/12", T_LABEL, DISPLAY, INK3, espacement=1.2)]
    return b


def quiz_question(s, cx, cy):
    b = _quiz_socle(cx, cy)
    b += [_carte(cx + M, cy + 214, W, 476),
          puce(cx + 50, cy + 242, "HISTOIRE-GEO", JAUNE),
          _pastille_creuse(cx + 256, cy + 242, "2 POINTS EN JEU", 124),
          paragraphe(cx + CENTRE, cy + 380, QUESTION, 21, TILE_INK, 32, "middle"),
          bloc(cx + 104, cy + 556, 222, 58, CARD_FACE, r=12, cerne=TILE_INK, epaisseur=3,
               ombre=4, ombre_couleur=TILE_INK),
          _oeil(cx + 140, cy + 585, 24),
          texte(cx + 232, cy + 592, "VOIR LA REPONSE", T_LABEL, DISPLAY, TILE_INK, ancre="middle"),
          bouton(cx + CA, cy + PIED_BAS, CW, "RATE", False, H_BOUTON, 19),
          bouton(cx + CB, cy + PIED_BAS, CW, "BONNE REPONSE", True, H_BOUTON, 16)]
    ecran(s, "Quitte ou Double - la question", cx, cy, "\n      ".join(b))


def quiz_reponse(s, cx, cy):
    b = _quiz_socle(cx, cy)
    b += [_carte(cx + M, cy + 214, W, 476),
          puce(cx + 50, cy + 242, "HISTOIRE-GEO", JAUNE),
          _pastille_creuse(cx + 256, cy + 242, "2 POINTS EN JEU", 124),
          paragraphe(cx + CENTRE, cy + 350, QUESTION, 21, TILE_INK, 32, "middle"),
          # La reponse revelee est une mise en avant, donc le seul pop autorise.
          bloc(cx + 50, cy + 452, 330, 134, JAUNE, r=12, cerne=TILE_INK, epaisseur=3, ombre=4,
               ombre_couleur=TILE_INK),
          texte(cx + CENTRE, cy + 484, "LA REPONSE", T_MICRO, DISPLAY, TILE_INK, ancre="middle",
                espacement=1.6),
          paragraphe(cx + CENTRE, cy + 516, REPONSE, T_LABEL, TILE_INK, 22, "middle"),
          texte(cx + CENTRE, cy + 736, "SOFIANE A CRAQUE : 5 PENALITES !", T_LABEL, DISPLAY,
                INK2, ancre="middle", espacement=1.2),
          bouton(cx + CA, cy + PIED_BAS, CW, "RATE", False, H_BOUTON, 19),
          bouton(cx + CB, cy + PIED_BAS, CW, "BONNE REPONSE", True, H_BOUTON, 16)]
    ecran(s, "Quitte ou Double - reponse revelee", cx, cy, "\n      ".join(b))


def quiz_choix(s, cx, cy):
    b = _coins(cx, cy) + _tete(cx, cy, "QUITTE OU DOUBLE", "NAWEL")
    b += [bloc(cx + M, cy + 214, W, 400, JAUNE, r=16, cerne=TILE_INK, epaisseur=3, ombre=7,
               ombre_couleur=TILE_INK),
          icone("brain", cx + CENTRE - 22, cy + 250, 44),
          texte(cx + CENTRE, cy + 340, "BIEN JOUE !", T_TITRE, DISPLAY, TILE_INK, ancre="middle"),
          texte(cx + CENTRE, cy + 440, "6", 72, DISPLAY, TILE_INK, ancre="middle"),
          texte(cx + CENTRE, cy + 470, "TA CAGNOTTE", T_MICRO, DISPLAY, TILE_INK, ancre="middle",
                espacement=1.8),
          paragraphe(cx + CENTRE, cy + 528, ["Tu la laisses grossir…",
                                             "ou tu la distribues maintenant ?"],
                     T_CORPS, TILE_INK, 24, "middle")]
    b += _pied2(cx, cy, "JE DISTRIBUE MES 6 POINTS", "JE CUMULE (QUITTE OU DOUBLE)", 18, 17)
    ecran(s, "Quitte ou Double - quitte ou double", cx, cy, "\n      ".join(b))


# ==========================================================================
# LE TABLEAU D'HONNEUR - RankingScreen
# ==========================================================================
PODIUM = ["Nawel", "Adam", "Emilien", "Amina", "Sofiane"]
CHOIX_RANG = ["Du plus gros dormeur au plus matinal",
              "Du plus dramatique au plus zen",
              "Du plus radin au plus depensier",
              "Du plus bavard au plus mysterieux"]


def _rang_tete(cx, cy):
    return _coins(cx, cy) + [
        texte(cx + CENTRE, cy + Y_MODE, "LE TABLEAU D'HONNEUR", T_LABEL, DISPLAY, NEON,
              ancre="middle", espacement=1.6),
        texte(cx + CENTRE, cy + 146, "manche 2", T_LABEL, BODY, INK2, ancre="middle")]


def rang_passage(s, cx, cy):
    b = _rang_tete(cx, cy)
    b += [bloc(cx + M, cy + 190, W, 510, JAUNE, r=16, cerne=TILE_INK, epaisseur=3, ombre=7,
               ombre_couleur=TILE_INK),
          _oeil(cx + CENTRE, cy + 290, 58, barre=True),
          texte(cx + CENTRE, cy + 372, "Personne d'autre ne regarde !", T_CORPS, BODY, TILE_INK,
                ancre="middle"),
          texte(cx + CENTRE, cy + 434, "PASSE LE TELEPHONE", 27, DISPLAY, TILE_INK, ancre="middle"),
          texte(cx + CENTRE, cy + 468, "A LEA", 27, DISPLAY, TILE_INK, ancre="middle"),
          paragraphe(cx + CENTRE, cy + 540, ["Lea est le juge de cette manche :",
                                             "une question secrete l'attend."],
                     T_LABEL, TILE_INK, 22, "middle"),
          _pied1(cx, cy, "JE SUIS LEA, J'AI LE TELEPHONE", 17)]
    ecran(s, "Tableau d'Honneur - passage au juge", cx, cy, "\n      ".join(b))


def rang_classement(s, cx, cy):
    b = _rang_tete(cx, cy)
    b += [_carte(cx + M, cy + 176, W, 122),
          texte(cx + CENTRE, cy + 210, "QUESTION SECRETE - CHUT !", T_LABEL, DISPLAY, TILE_INK,
                ancre="middle", espacement=1.2, opacite=0.6),
          paragraphe(cx + CENTRE, cy + 248, ["Du plus gros dormeur", "au plus matinal"],
                     17, TILE_INK, 24, "middle"),
          texte(cx + M, cy + 330, "Tape tes potes dans l'ordre, du haut", T_LABEL, BODY, INK2),
          texte(cx + M, cy + 352, "du podium vers le bas :", T_LABEL, BODY, INK2)]
    for i, nom in enumerate(PODIUM):
        py = cy + 374 + i * 68            # pas vertical unique de la liste
        pris = i < 3
        b.append(bloc(cx + M, py, W, 56, JAUNE if pris else SURFACE, r=12,
                      cerne=TILE_INK if pris else INK, epaisseur=3, ombre=4,
                      ombre_couleur=TILE_INK if pris else INK))
        b.append(bloc(cx + 46, py + 12, 32, 32, TILE_INK if pris else BG_HAUT, r=16,
                      cerne=TILE_INK if pris else INK, epaisseur=2))
        b.append(texte(cx + 62, py + 34, str(i + 1) if pris else "-", T_LABEL, DISPLAY,
                       JAUNE if pris else INK3, ancre="middle"))
        b.append(texte(cx + 96, py + 35, nom, 17, BODY, TILE_INK if pris else INK, gras=700))
    b += _pied_desactive(cx, cy, "VALIDER MON PODIUM")
    ecran(s, "Tableau d'Honneur - le juge classe", cx, cy, "\n      ".join(b))


def rang_retour(s, cx, cy):
    b = _rang_tete(cx, cy)
    b += [bloc(cx + M, cy + 190, W, 510, JAUNE, r=16, cerne=TILE_INK, epaisseur=3, ombre=7,
               ombre_couleur=TILE_INK),
          _oeil(cx + CENTRE, cy + 300, 58),
          texte(cx + CENTRE, cy + 408, "PODIUM", T_TITRE, DISPLAY, TILE_INK, ancre="middle"),
          texte(cx + CENTRE, cy + 444, "VERROUILLE !", T_TITRE, DISPLAY, TILE_INK, ancre="middle"),
          paragraphe(cx + CENTRE, cy + 520, ["Lea, repose le telephone",
                                             "au centre de la table."],
                     T_CORPS, TILE_INK, 24, "middle"),
          _pied1(cx, cy, "LE TELEPHONE EST AU CENTRE", 17)]
    ecran(s, "Tableau d'Honneur - retour a la table", cx, cy, "\n      ".join(b))


def _podium_juge(cx, cy):
    out = [_panneau(cx + M, cy + 176, W, 238),
           texte(cx + CENTRE, cy + 208, "LE PODIUM DE LEA", T_LABEL, DISPLAY, INK3,
                 ancre="middle", espacement=1.4)]
    for i, nom in enumerate(PODIUM):
        py = cy + 246 + i * 34            # pas vertical unique
        out.append(icone("medal", cx + 48, py - 15, 20))
        out.append(texte(cx + 80, py, f"{i + 1}.", T_LABEL, DISPLAY, INK3))
        out.append(texte(cx + 106, py, nom, T_CORPS, BODY, INK, gras=700))
    return out


def rang_devinette(s, cx, cy):
    b = _rang_tete(cx, cy) + _podium_juge(cx, cy)
    b += [texte(cx + M, cy + 452, "Quelle question secrete a produit ce", T_LABEL, BODY, INK2),
          texte(cx + M, cy + 474, "classement ? Mettez-vous d'accord :", T_LABEL, BODY, INK2)]
    for i, txt in enumerate(CHOIX_RANG):
        py = cy + 502 + i * 72
        b.append(_panneau(cx + M, py, W, 58))
        b.append(texte(cx + 48, py + 35, txt, T_LABEL, BODY, INK))
    ecran(s, "Tableau d'Honneur - le groupe devine", cx, cy, "\n      ".join(b))


def rang_revelation(s, cx, cy):
    b = _rang_tete(cx, cy) + _podium_juge(cx, cy)
    b += [texte(cx + CENTRE, cy + 462, "RATE - LE GROUPE PREND 1 PENALITE", T_LABEL, DISPLAY,
                DANGER, ancre="middle", espacement=1.2)]
    for i, txt in enumerate(CHOIX_RANG):
        py = cy + 502 + i * 72
        if i == 0:                          # la vraie question
            b.append(bloc(cx + M, py, W, 58, SURFACE, r=14, cerne=SUCCES, epaisseur=3, ombre=3,
                          ombre_couleur=INK))
            b.append(texte(cx + 48, py + 35, txt, T_LABEL, BODY, INK, gras=700))
            b.append(_coche(cx + 366, py + 29, 22))
        elif i == 1:                        # le choix errone du groupe
            b.append(bloc(cx + M, py, W, 58, SURFACE, r=14, cerne=DANGER, epaisseur=3, ombre=3,
                          ombre_couleur=INK))
            b.append(texte(cx + 48, py + 35, txt, T_LABEL, BODY, DANGER))
            b.append(_croix(cx + 366, py + 29, 18, DANGER))
        else:
            b.append(bloc(cx + M, py, W, 58, SURFACE, r=14, cerne=INK, epaisseur=2, opacite=0.45))
            b.append(texte(cx + 48, py + 35, txt, T_LABEL, BODY, INK3, opacite=0.7))
    b.append(_pied1(cx, cy, "MANCHE SUIVANTE"))
    ecran(s, "Tableau d'Honneur - revelation", cx, cy, "\n      ".join(b))


# ==========================================================================
# LA CRIEE - AuctionScreen
# ==========================================================================
def _criee_theme(cx, cy, y=160, h=160):
    return [_carte(cx + M, cy + y, W, h),
            icone("megaphone", cx + CENTRE - 19, cy + y + 22, 38),
            texte(cx + CENTRE, cy + y + 88, "LE THEME", T_MICRO, DISPLAY, TILE_INK, ancre="middle",
                  espacement=1.8, opacite=0.6),
            texte(cx + CENTRE, cy + y + 126, "DES CAPITALES EUROPEENNES", 21, DISPLAY, TILE_INK,
                  ancre="middle")]


def criee_encheres(s, cx, cy):
    b = _coins(cx, cy) + _tete(cx, cy, "LA CRIEE") + _criee_theme(cx, cy)
    b += [paragraphe(cx + CENTRE, cy + 360, ["Annoncez a voix haute combien vous pouvez",
                                             "en citer en 1 minute. Surencherissez…",
                                             "ou criez « tu mens ! »"],
                     T_LABEL, INK2, 22, "middle"),
          bloc(cx + 56, cy + 470, 60, 60, SURFACE, r=12, cerne=INK, epaisseur=3, ombre=4,
               ombre_couleur=INK),
          _signe(cx + 86, cy + 500, False),
          texte(cx + CENTRE, cy + 524, "7", 72, DISPLAY, INK, ancre="middle"),
          bloc(cx + 314, cy + 470, 60, 60, JAUNE, r=12, cerne=TILE_INK, epaisseur=3, ombre=4,
               ombre_couleur=TILE_INK),
          _signe(cx + 344, cy + 500, True, 22, TILE_INK),
          texte(cx + CENTRE, cy + 576, "DERNIERE ENCHERE ANNONCEE", T_MICRO, DISPLAY, INK3,
                ancre="middle", espacement=1.8),
          bouton(cx + M, cy + 690, W, "« TU MENS ! » - LANCER LE CHRONO", True, H_BOUTON, 16),
          bloc(cx + CA, cy + 770, CW, 56, SURFACE, r=12, cerne=INK, epaisseur=2),
          texte(cx + CA + CW / 2, cy + 804, "CHANGER DE THEME", T_LABEL, DISPLAY, INK,
                ancre="middle"),
          bloc(cx + CB, cy + 770, CW, 56, SURFACE, r=12, cerne=INK, epaisseur=2),
          texte(cx + CB + CW / 2, cy + 804, "MES THEMES (3)", T_LABEL, DISPLAY, INK, ancre="middle")]
    ecran(s, "La Criee - encheres", cx, cy, "\n      ".join(b))


def criee_defi(s, cx, cy):
    b = _coins(cx, cy) + _tete(cx, cy, "LA CRIEE") + _criee_theme(cx, cy)
    b += [texte(cx + CENTRE, cy + 430, "08s", 78, DISPLAY, DANGER, ancre="middle"),
          texte(cx + CENTRE, cy + 476, "Cite-les ! La table valide chaque bonne reponse.",
                T_LABEL, BODY, INK2, ancre="middle"),
          bloc(cx + 56, cy + 530, 60, 60, SURFACE, r=12, cerne=INK, epaisseur=3, ombre=4,
               ombre_couleur=INK),
          _signe(cx + 86, cy + 560, False),
          texte(cx + 200, cy + 586, "5", 66, DISPLAY, INK, ancre="middle"),
          texte(cx + 232, cy + 586, "/7", 26, DISPLAY, INK3),
          bloc(cx + 314, cy + 530, 60, 60, JAUNE, r=12, cerne=TILE_INK, epaisseur=3, ombre=4,
               ombre_couleur=TILE_INK),
          _signe(cx + 344, cy + 560, True, 22, TILE_INK),
          # Jauge du chrono : le decompte rouge se double d'une forme, il reste
          # lisible sans distinguer la couleur.
          bloc(cx + M, cy + 650, W, 16, SURFACE, r=8, cerne=INK, epaisseur=2),
          bloc(cx + M + 3, cy + 653, 50, 10, DANGER, r=5, epaisseur=0),
          bouton(cx + M, cy + PIED_BAS, W, "ARRETER LE DEFI", False, H_BOUTON, 19)]
    ecran(s, "La Criee - le defi", cx, cy, "\n      ".join(b))


def _criee_resultat(s, cx, cy, nom, gagne):
    couleur = SUCCES if gagne else DANGER
    b = _coins(cx, cy) + _tete(cx, cy, "LA CRIEE") + _criee_theme(cx, cy, 160, 140)
    b += [_carte(cx + M, cy + 330, W, 300, couleur, 4)]
    if gagne:
        b += [_coche(cx + CENTRE, cy + 396, 46, SUCCES, 5),
              texte(cx + CENTRE, cy + 476, "PARI TENU !", 32, DISPLAY, SUCCES, ancre="middle"),
              paragraphe(cx + CENTRE, cy + 524, ["7 cites sur 7. Celui qui a crie",
                                                 "« tu mens » prend 7 penalites."],
                         T_CORPS, TILE_INK, 26, "middle")]
    else:
        b += [_croix(cx + CENTRE, cy + 396, 40, DANGER, 5),
              texte(cx + CENTRE, cy + 476, "CA SENTAIT LE BLUFF…", 26, DISPLAY, DANGER,
                    ancre="middle"),
              paragraphe(cx + CENTRE, cy + 524, ["4 cites sur 7 annonces.",
                                                 "L'encherisseur prend 7 penalites."],
                         T_CORPS, TILE_INK, 26, "middle")]
    b += _pied2(cx, cy, "NOUVEAU THEME", "TERMINER LA PARTIE")
    ecran(s, nom, cx, cy, "\n      ".join(b))


def criee_pari_tenu(s, cx, cy):
    _criee_resultat(s, cx, cy, "La Criee - pari tenu", True)


def criee_bluff(s, cx, cy):
    _criee_resultat(s, cx, cy, "La Criee - bluff demasque", False)


THEMES_TABLEE = [("Des series des annees 2000", True),
                 ("Des trucs qu'on dit a l'apero", True),
                 ("Des chansons qui passent en boite", True),
                 ("Des capitales d'Asie", False),
                 ("Des marques de baskets", False)]


def _feuille(cx, cy, y, h):
    """Feuille modale : voile sur la page, puis panneau cerne ancre en bas."""
    return [f'<rect x="{cx}" y="{cy}" width="{L}" height="{H}" rx="38" fill="{TILE_INK}" '
            f'opacity="0.5"/>',
            bloc(cx + 10, cy + y, L - 20, h, BG, r=20, cerne=INK, epaisseur=3),
            texte(cx + 36, cy + y + 46, "MES THEMES", 22, DISPLAY, INK),
            bloc(cx + 340, cy + y + 22, 44, 44, SURFACE, r=12, cerne=INK, epaisseur=2),
            _croix(cx + 362, cy + y + 44, 16, INK)]


def criee_mes_themes(s, cx, cy):
    b = _coins(cx, cy) + _tete(cx, cy, "LA CRIEE") + _criee_theme(cx, cy)
    b += _feuille(cx, cy, 250, 580)
    b += [paragraphe(cx + 36, cy + 336, ["Vos themes rejoignent la pioche de la Criee et",
                                         "restent enregistres sur cet appareil."],
                     T_LABEL, INK2, 21),
          bloc(cx + 36, cy + 386, 274, 48, BG_HAUT, r=12, cerne=INK, epaisseur=2),
          texte(cx + 54, cy + 416, "Des choses qu'on crie au comptoir…", T_LABEL, BODY, INK3),
          bloc(cx + 322, cy + 386, 62, 48, NEON, r=12, cerne=TILE_INK, epaisseur=3, ombre=4,
               ombre_couleur=TILE_INK),
          _signe(cx + 353, cy + 410, True, 22, TILE_INK)]
    for i, (txt, actif) in enumerate(THEMES_TABLEE):
        py = cy + 456 + i * 66            # pas vertical unique de la liste
        b.append(bloc(cx + 36, py, 348, 54, SURFACE, r=12, cerne=INK, epaisseur=2))
        b.append(_interrupteur(cx + 52, py + 14, actif))
        b.append(texte(cx + 120, py + 33, txt, T_LABEL, BODY, INK if actif else INK3))
        if not actif:
            larg = len(txt) * 6.4
            b.append(f'<line x1="{cx + 120}" y1="{py + 29}" x2="{cx + 120 + larg:.0f}" '
                     f'y2="{py + 29}" stroke="{INK3}" stroke-width="1.5"/>')
        b.append(_corbeille(cx + 356, py + 27, 18))
    ecran(s, "La Criee - mes themes", cx, cy, "\n      ".join(b))


def criee_mes_themes_vide(s, cx, cy):
    b = _coins(cx, cy) + _tete(cx, cy, "LA CRIEE") + _criee_theme(cx, cy)
    b += _feuille(cx, cy, 330, 500)
    b += [paragraphe(cx + 36, cy + 416, ["Vos themes rejoignent la pioche de la Criee et",
                                         "restent enregistres sur cet appareil."],
                     T_LABEL, INK2, 21),
          bloc(cx + 36, cy + 466, 274, 48, BG_HAUT, r=12, cerne=INK, epaisseur=2),
          texte(cx + 54, cy + 496, "Des choses qu'on crie au comptoir…", T_LABEL, BODY, INK3),
          # Ajout desactive tant que le champ est vide : pas d'ombre, sinon le
          # bouton continue de promettre un appui.
          bloc(cx + 322, cy + 466, 62, 48, SURFACE, r=12, cerne=INK, epaisseur=2, opacite=0.45),
          _signe(cx + 353, cy + 490, True, 22, INK3),
          bloc(cx + 36, cy + 540, 348, 216, BG_HAUT, r=14, cerne=INK, epaisseur=2, opacite=0.7),
          icone("megaphone", cx + CENTRE - 21, cy + 596, 42),
          texte(cx + CENTRE, cy + 682, "AUCUN THEME POUR L'INSTANT", T_LABEL, DISPLAY, INK3,
                ancre="middle", espacement=1.4),
          texte(cx + CENTRE, cy + 712, "La pioche tourne sur les themes embarques.", T_MICRO,
                BODY, INK3, ancre="middle")]
    ecran(s, "La Criee - mes themes, aucun", cx, cy, "\n      ".join(b))


# ==========================================================================
# LE PILORI - TribunalScreen
# ==========================================================================
ACCUSATION = ["Usage abusif du telephone en", "pleine partie, au vu et au su", "de la table."]


def pilori_ouverture(s, cx, cy):
    b = _coins(cx, cy) + _tete(cx, cy, "LE PILORI")
    b += [icone("gavel", cx + CENTRE - 26, cy + 306, 52),
          texte(cx + CENTRE, cy + 430, "LA COUR EST OUVERTE", 27, DISPLAY, INK, ancre="middle"),
          paragraphe(cx + CENTRE, cy + 480, ["Chacun ecrit une accusation secrete",
                                             "contre la table… ou vous laissez l'app",
                                             "fournir les chefs d'accusation."],
                     T_CORPS, INK2, 26, "middle")]
    b += _pied2(cx, cy, "ON ECRIT NOS ACCUSATIONS", "ACCUSATIONS DE L'APP")
    ecran(s, "Le Pilori - ouverture", cx, cy, "\n      ".join(b))


def pilori_passage(s, cx, cy):
    b = _coins(cx, cy) + _tete(cx, cy, "LE PILORI")
    b += [bloc(cx + M, cy + 190, W, 470, JAUNE, r=16, cerne=TILE_INK, epaisseur=3, ombre=7,
               ombre_couleur=TILE_INK),
          _oeil(cx + CENTRE, cy + 290, 58, barre=True),
          texte(cx + CENTRE, cy + 380, "Accusation secrete 2/5", T_CORPS, BODY, TILE_INK,
                ancre="middle"),
          texte(cx + CENTRE, cy + 456, "PASSE LE TELEPHONE", 27, DISPLAY, TILE_INK, ancre="middle"),
          texte(cx + CENTRE, cy + 492, "A KARIM", 27, DISPLAY, TILE_INK, ancre="middle"),
          texte(cx + CENTRE, cy + 570, "PERSONNE D'AUTRE NE REGARDE", T_MICRO, DISPLAY, TILE_INK,
                ancre="middle", espacement=1.8, opacite=0.7),
          _pied1(cx, cy, "C'EST MOI, KARIM", 18)]
    ecran(s, "Le Pilori - passage du telephone", cx, cy, "\n      ".join(b))


def pilori_accusation(s, cx, cy):
    b = _coins(cx, cy) + _tete(cx, cy, "LE PILORI")
    b += [texte(cx + CENTRE, cy + 176, "Karim, accuse qui tu veux - ton", T_LABEL, BODY, INK2,
                ancre="middle"),
          texte(cx + CENTRE, cy + 198, "accusation restera anonyme.", T_LABEL, BODY, INK2,
                ancre="middle"),
          bloc(cx + M, cy + 226, W, 394, SURFACE, r=16, cerne=INK, epaisseur=3, ombre=4,
               ombre_couleur=INK),
          paragraphe(cx + 48, cy + 268, ["Ex. : quelqu'un ici a deja quitte une",
                                         "soiree sans dire au revoir…"],
                     T_CORPS, INK3, 26),
          f'<rect x="{cx + 48}" y="{cy + 252}" width="2" height="22" fill="{NEON}"/>',
          texte(cx + L - M - 22, cy + 650, "0/200", T_LABEL, BODY, INK3, ancre="end")]
    b += _pied_desactive(cx, cy, "ACCUSATION DEPOSEE")
    ecran(s, "Le Pilori - accusation secrete", cx, cy, "\n      ".join(b))


def pilori_defense(s, cx, cy):
    b = _coins(cx, cy) + _tete(cx, cy, "LE PILORI", "KARIM", "comparait devant la cour")
    b += [_carte(cx + M, cy + 200, W, 330),
          icone("gavel", cx + CENTRE - 17, cy + 232, 34),
          paragraphe(cx + CENTRE, cy + 330, ACCUSATION, 17, TILE_INK, 28, "middle"),
          texte(cx + CENTRE, cy + 470, "ACCUSATION ANONYME DE LA TABLE", T_MICRO, DISPLAY,
                TILE_INK, ancre="middle", espacement=1.6, opacite=0.55),
          paragraphe(cx + CENTRE, cy + 590, ["Karim a 30 secondes pour se defendre.",
                                             "Ecoutez… puis votez."],
                     T_CORPS, INK2, 26, "middle"),
          _pied1(cx, cy, "PASSER AU VOTE")]
    ecran(s, "Le Pilori - la defense", cx, cy, "\n      ".join(b))


def _pilori_compteurs(cx, cy, y, coupable, innocent, fige=False):
    op = {"opacite": 0.5} if fige else {}
    out = [bloc(cx + CA, cy + y, CW, 140, SURFACE, r=14, cerne=INK, epaisseur=3, ombre=4,
                ombre_couleur=INK, **op),
           bloc(cx + CB, cy + y, CW, 140, SURFACE, r=14, cerne=INK, epaisseur=3, ombre=4,
                ombre_couleur=INK, **op),
           icone("gavel", cx + CA + CW / 2 - 15, cy + y + 22, 30),
           _coche(cx + CB + CW / 2, cy + y + 38, 30, SUCCES),
           texte(cx + CA + CW / 2, cy + y + 104, str(coupable), 30, DISPLAY, INK, ancre="middle"),
           texte(cx + CB + CW / 2, cy + y + 104, str(innocent), 30, DISPLAY, INK, ancre="middle"),
           texte(cx + CA + CW / 2, cy + y + 128, "COUPABLE", T_MICRO, DISPLAY, INK3,
                 ancre="middle", espacement=1.4),
           texte(cx + CB + CW / 2, cy + y + 128, "NON COUPABLE", T_MICRO, DISPLAY, INK3,
                 ancre="middle", espacement=1.4)]
    return out


def pilori_vote(s, cx, cy):
    b = _coins(cx, cy) + _tete(cx, cy, "LE PILORI", "KARIM", "comparait devant la cour")
    b += [_carte(cx + M, cy + 200, W, 216),
          paragraphe(cx + CENTRE, cy + 268, ACCUSATION, T_CORPS, TILE_INK, 24, "middle"),
          texte(cx + CENTRE, cy + 384, "ACCUSATION ANONYME DE LA TABLE", T_MICRO, DISPLAY,
                TILE_INK, ancre="middle", espacement=1.6, opacite=0.55)]
    b += _pilori_compteurs(cx, cy, 470, 3, 2)
    b += [_pied1(cx, cy, "VERDICT"),
          texte(cx + CENTRE, cy + Y_LIEN, "ARDOISE - AMINA : 2 - EMILIEN : 1", T_LABEL, DISPLAY,
                INK3, ancre="middle", espacement=1.4)]
    ecran(s, "Le Pilori - le vote", cx, cy, "\n      ".join(b))


def pilori_verdict(s, cx, cy):
    b = _coins(cx, cy) + _tete(cx, cy, "LE PILORI", "KARIM", "comparait devant la cour")
    b += [_carte(cx + M, cy + 200, W, 216),
          paragraphe(cx + CENTRE, cy + 268, ACCUSATION, T_CORPS, TILE_INK, 24, "middle"),
          texte(cx + CENTRE, cy + 384, "ACCUSATION ANONYME DE LA TABLE", T_MICRO, DISPLAY,
                TILE_INK, ancre="middle", espacement=1.6, opacite=0.55)]
    b += _pilori_compteurs(cx, cy, 440, 4, 1, fige=True)
    b += [icone("gavel", cx + 76, cy + 616, 30),
          texte(cx + 116, cy + 640, "COUPABLE - 1 PENALITE", 24, DISPLAY, NEON)]
    b += _pied2(cx, cy, "PROCES SUIVANT", "TERMINER ET VOIR L'ADDITION", 19, 17)
    ecran(s, "Le Pilori - le verdict", cx, cy, "\n      ".join(b))


# ==========================================================================
# TU PREFERES - WouldYouRatherScreen
# ==========================================================================
OPT_A = ["Vivre dans une maison faite", "uniquement de portes vitrees"]
OPT_B = ["Vivre dans une maison faite", "uniquement d'escaliers", "en colimacon"]


def tp_vote(s, cx, cy):
    b = _coins(cx, cy)
    b += [texte(cx + CENTRE, cy + Y_MODE, "TU PREFERES - MANCHE 3/12", T_LABEL, DISPLAY, NEON,
                ancre="middle", espacement=1.4),
          bloc(cx + 150, cy + 140, 130, 32, SURFACE, r=16, cerne=INK, epaisseur=2),
          icone("users", cx + 164, cy + 148, 16),
          texte(cx + 250, cy + 161, "4/6 VOTES", T_MICRO, DISPLAY, INK, ancre="middle"),
          texte(cx + CENTRE, cy + 206, "Au tour de Nawel : passe le telephone,", T_LABEL, BODY,
                INK2, ancre="middle"),
          texte(cx + CENTRE, cy + 228, "choisis ton camp en secret.", T_LABEL, BODY, INK2,
                ancre="middle"),
          # Les deux camps sont deux objets identiques : meme aplat, meme cerne,
          # meme encre. Les teinter differemment designerait un favori.
          _carte(cx + M, cy + 250, W, 190),
          texte(cx + 50, cy + 288, "OPTION A", T_MICRO, DISPLAY, TILE_INK, espacement=1.8,
                opacite=0.6),
          paragraphe(cx + 50, cy + 340, OPT_A, 18, TILE_INK, 28, gras=700),
          texte(cx + CENTRE, cy + 476, "OU", T_LABEL, DISPLAY, INK3, ancre="middle",
                espacement=2.4),
          _carte(cx + M, cy + 500, W, 190),
          texte(cx + 50, cy + 538, "OPTION B", T_MICRO, DISPLAY, TILE_INK, espacement=1.8,
                opacite=0.6),
          paragraphe(cx + 50, cy + 590, OPT_B, 18, TILE_INK, 28, gras=700),
          bloc(cx + M, cy + 800, W, 52, SURFACE, r=12, cerne=INK, epaisseur=2),
          texte(cx + CENTRE, cy + 832, "TERMINER LA PARTIE", T_LABEL, DISPLAY, INK3,
                ancre="middle", espacement=1.4)]
    ecran(s, "Tu preferes - vote secret", cx, cy, "\n      ".join(b))


def _tp_verdict(s, cx, cy, nom, minorite):
    b = _coins(cx, cy)
    b += [texte(cx + CENTRE, cy + Y_MODE, "TU PREFERES - MANCHE 3/12", T_LABEL, DISPLAY, NEON,
                ancre="middle", espacement=1.4),
          _carte(cx + M, cy + 176, W, 500 if minorite else 440),
          texte(cx + CENTRE, cy + 216, "LE VERDICT DE LA TABLE", T_LABEL, DISPLAY, TILE_INK,
                ancre="middle", espacement=1.6, opacite=0.6)]
    colonnes = [(cx + 50, "4" if minorite else "3", OPT_A, False),
                (cx + 222, "2" if minorite else "3", ["Vivre dans une maison faite",
                                                      "uniquement d'escaliers",
                                                      "en colimacon"], minorite)]
    for x, n, lignes, perdant in colonnes:
        b.append(bloc(x, cy + 250, 158, 156, CARD_FACE, r=12,
                      cerne=DANGER if perdant else TILE_INK, epaisseur=3 if perdant else 2))
        b.append(texte(x + 79, cy + 300, n, 34, DISPLAY, DANGER if perdant else TILE_INK,
                       ancre="middle"))
        b.append(paragraphe(x + 79, cy + 334, lignes, T_MICRO, TILE_INK, 17, "middle"))
    if minorite:
        b += [texte(cx + CENTRE, cy + 456, "Le camp minoritaire prend la penalite !", T_CORPS,
                    BODY, TILE_INK, ancre="middle"),
              _pastille_creuse(cx + 96, cy + 490, "AMINA", 104, DANGER, CARD_FACE, 32, T_LABEL),
              _pastille_creuse(cx + 218, cy + 490, "SOFIANE", 116, DANGER, CARD_FACE, 32, T_LABEL),
              texte(cx + CENTRE, cy + 588, "2 JOUEURS PENALISES", T_MICRO, DISPLAY, TILE_INK,
                    ancre="middle", espacement=1.6, opacite=0.55)]
    else:
        b += [paragraphe(cx + CENTRE, cy + 466, ["Personne n'est penalise :",
                                                 "egalite ou unanimite."],
                         T_CORPS, TILE_INK, 26, "middle"),
              texte(cx + CENTRE, cy + 560, "AUCUNE PASTILLE, AUCUN CAMP EN ROUGE", T_MICRO,
                    DISPLAY, TILE_INK, ancre="middle", espacement=1.4, opacite=0.5)]
    b += [_pied1(cx, cy, "DILEMME SUIVANT"),
          _lien(cx, cy, "TERMINER LA PARTIE")]
    ecran(s, nom, cx, cy, "\n      ".join(b))


def tp_minorite(s, cx, cy):
    _tp_verdict(s, cx, cy, "Tu preferes - verdict minorite", True)


def tp_egalite(s, cx, cy):
    _tp_verdict(s, cx, cy, "Tu preferes - egalite ou unanimite", False)


# ==========================================================================
# LA ROUE DU DESTIN - RouletteScreen
# ==========================================================================
def roue_lancer(s, cx, cy):
    b = _coins(cx, cy) + _tete(cx, cy, "LA ROUE DU DESTIN")
    b += _roue(cx + CENTRE, cy + 400, 150)
    b += [bouton(cx + M, cy + 660, W, "LANCER LA ROUE", True, H_BOUTON, 21),
          # Second etat du meme bouton, pendant la rotation : aplat attenue et
          # ombre retiree, comme tout controle qui n'accepte plus l'appui.
          bloc(cx + M, cy + 748, W, H_BOUTON, NEON, r=12, cerne=TILE_INK, epaisseur=3,
               opacite=0.55),
          texte(cx + CENTRE, cy + 788, "CA TOURNE…", 21, DISPLAY, TILE_INK, ancre="middle",
                opacite=0.7),
          texte(cx + CENTRE, cy + 848, "ETAT PENDANT LA ROTATION", T_MICRO, DISPLAY, INK3,
                ancre="middle", espacement=1.6)]
    ecran(s, "La Roue du Destin - lancer", cx, cy, "\n      ".join(b))


def roue_resultat(s, cx, cy):
    b = _coins(cx, cy) + _tete(cx, cy, "LA ROUE DU DESTIN")
    b += _roue(cx + CENTRE, cy + 350, 122, depart=22.5)
    b += [_carte(cx + M, cy + 496, W, 180),
          texte(cx + CENTRE, cy + 556, "MIME MUET", 28, DISPLAY, CARD_RED, ancre="middle"),
          paragraphe(cx + CENTRE, cy + 600, ["Mime un metier, la tablee devine",
                                             "en trente secondes."],
                     T_CORPS, TILE_INK, 26, "middle")]
    b += _pied2(cx, cy, "LANCER LA ROUE", "TERMINER LA PARTIE", 21, 19)
    ecran(s, "La Roue du Destin - resultat", cx, cy, "\n      ".join(b))


# ==========================================================================
# JEUX DE GAGES - PromptGameScreen (un gabarit, sept surfaces)
# ==========================================================================
def _ecran_gage(s, cx, cy, nom, surtitre, joueur, lignes, tour="7/40", avance=0.42,
                cible=None, penalite=None, bouton_penalite="1 PENALITE", pastilles=None):
    """Gabarit unique des modes a cartes. Seuls l'entete, la copie de la carte et
    la ligne de penalite changent d'un mode a l'autre : c'est exactement ce que
    fait PromptGameScreen, qui sert sept modes avec un seul rendu."""
    h_carte = 380 if pastilles else 430
    bas_carte = 240 + h_carte
    b = _coins(cx, cy)
    b += [texte(cx + CENTRE, cy + Y_MODE, surtitre, T_LABEL, DISPLAY, NEON, ancre="middle",
                espacement=1.4),
          bloc(cx + M, cy + 146, 268, 14, SURFACE, r=7, cerne=INK, epaisseur=2),
          bloc(cx + M + 3, cy + 149, int(262 * avance), 8, NEON, r=4, epaisseur=0),
          bloc(cx + 308, cy + 138, 96, 30, SURFACE, r=15, cerne=INK, epaisseur=2),
          texte(cx + 356, cy + 158, tour, T_LABEL, DISPLAY, INK, ancre="middle"),
          texte(cx + CENTRE, cy + 214, joueur, T_TITRE, DISPLAY, INK, ancre="middle"),
          _carte(cx + M, cy + 240, W, h_carte)]
    hauteur_extra = (52 if cible else 0) + (52 if penalite else 0)
    centre_texte = 240 + (h_carte - hauteur_extra) / 2 + 244 - 236
    y0 = cy + centre_texte - (len(lignes) - 1) * 14
    b.append(paragraphe(cx + CENTRE, y0, lignes, 17, TILE_INK, 28, "middle"))
    if cible:
        b.append(texte(cx + CENTRE, cy + bas_carte - (104 if penalite else 52), cible, T_LABEL,
                       DISPLAY, ORANGE_INK, ancre="middle", espacement=1.4))
    if penalite:
        b.append(texte(cx + CENTRE, cy + bas_carte - 52, penalite, T_LABEL, DISPLAY, DANGER,
                       ancre="middle", espacement=1.4))
    if pastilles:
        x = cx + M
        for i, (libelle, plein) in enumerate(pastilles):
            larg = 26 + len(libelle) * 6.9
            if plein:
                b.append(puce(x, cy + 656, libelle, JAUNE, TILE_INK, T_MICRO, 32))
            else:
                b.append(_pastille_creuse(x, cy + 656, libelle, larg, ORANGE_INK, SURFACE, 32))
            x += larg + 10
    b += _pied2(cx, cy, bouton_penalite, "FAIT", 19, 22, haut_primaire=False)
    ecran(s, nom, cx, cy, "\n      ".join(b))


def gage_taulier(s, cx, cy):
    _ecran_gage(s, cx, cy, "Le Taulier - carte de gage", "LE TAULIER - SOIREE", "NAWEL",
                ["Nawel, tu es le Roi des questions.",
                 "Des que tu poses une question, ceux",
                 "qui repondent prennent une penalite.",
                 "Si on te repond « Ta gueule ! »,",
                 "c'est toi qui prends 2 penalites."],
                penalite="2 PENALITES", bouton_penalite="2 PENALITES")


def gage_action_verite(s, cx, cy):
    _ecran_gage(s, cx, cy, "Action ou Verite - carte de gage", "ACTION OU VERITE - CLASSIQUE",
                "ADAM", ["Quelle est la chose la plus bizarre",
                         "que tu aies cherchee sur internet ?"],
                tour="12/60", avance=0.2, penalite="1 PENALITE SI TU ESQUIVES")


def gage_jamais(s, cx, cy):
    _ecran_gage(s, cx, cy, "Je n'ai jamais - carte de gage", "JE N'AI JAMAIS - CLASSIQUE",
                "TOUTE LA TABLE", ["Je n'ai jamais stalke un ex", "sur les reseaux"],
                tour="4/50", avance=0.08, penalite="1 PENALITE SI TU L'AS DEJA FAIT")


def gage_qui_de_nous(s, cx, cy):
    _ecran_gage(s, cx, cy, "Qui de nous - carte de gage", "QUI DE NOUS - CLASSIQUE", "AMINA",
                ["Qui est le plus susceptible", "de devenir celebre ?"],
                tour="9/45", avance=0.2, cible="C'EST A AMINA DE JOUER",
                penalite="1 PENALITE POUR LE PLUS DESIGNE")


def gage_dix_mais(s, cx, cy):
    _ecran_gage(s, cx, cy, "C'est un 10 mais - carte de gage", "C'EST UN 10 MAIS - CLASSIQUE",
                "KARIM", ["C'est un 10 mais…", "il ou elle met du ketchup", "sur les pates"],
                tour="6/40", avance=0.15, penalite="1 PENALITE SI TU ESQUIVES LE DEBAT")


def gage_sept_secondes(s, cx, cy):
    _ecran_gage(s, cx, cy, "7 Secondes - carte de gage", "7 SECONDES - CLASSIQUE", "SOFIANE",
                ["Cite 3 capitales europeennes"], tour="3/40", avance=0.07,
                penalite="1 PENALITE SI TU RATES OU SI TU TRAINES")


def gage_regles_en_cours(s, cx, cy):
    _ecran_gage(s, cx, cy, "Jeux de gages - regles en cours", "LE TAULIER - SOIREE", "EMILIEN",
                ["Emilien, tu es le Valet des pouces.", "Quand tu poses le pouce sur la table,",
                 "le dernier a t'imiter prend 2 penalites."],
                tour="18/40", avance=0.45, penalite="2 PENALITES", bouton_penalite="2 PENALITES",
                pastilles=[("NAWEL - ROLE", True), ("ENCORE 3 TOURS", False),
                           ("JUSQU'A LA FIN", False)])


def gage_chargement(s, cx, cy):
    """Aucune session vivante apres un rechargement : PromptGameScreen renvoie au
    hub et n'affiche qu'un mot en attendant. Un ecran sobre est ici le bon
    livrable, pas un cadre a remplir."""
    b = [texte(cx + CENTRE, cy + 466, "chargement…", T_CORPS, BODY, INK3, ancre="middle")]
    ecran(s, "Jeux de gages - chargement", cx, cy, "\n      ".join(b))


# ==========================================================================
# REGLES D'UN MODE - ModeRulesScreen
# ==========================================================================
ETAPES_PILORI = [["Chacun ecrit une accusation secrete contre la",
                  "table, ou vous jouez avec celles de l'app."],
                 ["Une accusation est tiree au sort,", "un accuse est designe."],
                 ["L'accuse a 30 secondes pour se defendre", "devant la cour."],
                 ["La table vote a main levee :", "coupable ou non coupable."],
                 ["Coupable : 1 penalite pour l'accuse.", "Non coupable : libere, proces suivant."]]


def regles_mode(s, cx, cy):
    b = [entete(cx, cy, "REGLES - LE PILORI"),
         _parchemin(cx + CENTRE, cy + 170, 46)]
    for i, lignes in enumerate(ETAPES_PILORI):
        py = cy + 220 + i * 128           # pas vertical unique de la liste d'etapes
        b.append(_panneau(cx + M, py, W, 104))
        b.append(bloc(cx + 46, py + 22, 32, 32, BG_HAUT, r=16, cerne=INK, epaisseur=2))
        b.append(texte(cx + 62, py + 44, str(i + 1), T_LABEL, DISPLAY, INK, ancre="middle"))
        b.append(paragraphe(cx + 96, py + 44, lignes, T_LABEL, INK2, 22))
    ecran(s, "Regles d'un mode", cx, cy, "\n      ".join(b))


def regles_mode_vide(s, cx, cy):
    b = [_parchemin(cx + CENTRE, cy + 360, 58, INK3),
         paragraphe(cx + CENTRE, cy + 452, ["Aucune regle a afficher", "pour le moment."],
                    T_CORPS, INK2, 26, "middle"),
         bouton(cx + 126, cy + 528, 178, "RETOUR", True, 60, 19)]
    ecran(s, "Regles d'un mode - aucun mode", cx, cy, "\n      ".join(b))


ECRANS = [quiz_question, quiz_reponse, quiz_choix,
          rang_passage, rang_classement, rang_retour, rang_devinette, rang_revelation,
          criee_encheres, criee_defi, criee_pari_tenu, criee_bluff,
          criee_mes_themes, criee_mes_themes_vide,
          pilori_ouverture, pilori_passage, pilori_accusation, pilori_defense,
          pilori_vote, pilori_verdict,
          tp_vote, tp_minorite, tp_egalite,
          roue_lancer, roue_resultat,
          gage_taulier, gage_action_verite, gage_jamais, gage_qui_de_nous,
          gage_dix_mais, gage_sept_secondes, gage_regles_en_cours, gage_chargement,
          regles_mode, regles_mode_vide]
