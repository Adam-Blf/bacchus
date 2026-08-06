# -*- coding: utf-8 -*-
"""Lot 2 : Le Coupe-Gorge, de la feuille d'options a la galerie des 52 cartes.

Copie et ordre lus dans le code, jamais inventes :
  - HubScreen.tsx        feuille « Le Coupe-Gorge - options »
  - GameBoard.tsx        pioche, revelation, encart de regle, choix du contestataire
  - ContestModal.tsx     badge de niveau, penalite geante, escalade, choix du perdant
  - BorderlandScreen.tsx les deux ConfirmDialog (remelange, sortie)
  - PlayingCard.tsx      dispositions de pips, figures, Joker, coins mono
  - CardGallery.tsx      page de controle /?cards
  - RulesScreen.tsx      intro, quatre regles d'enseigne, Joker, Le Contest
  - types/index.ts       SUIT_RULES, JOKER_RULE, SUIT_SYMBOLS, CONTEST_MULTIPLIERS

Palette resserree : creme et encre en dominante, NEON en accent unique, JAUNE
comme seul pop de selection. Les rouges et verts restent semantiques. Les
cartes a jouer gardent CARD_FACE et CARD_RED : ce sont des objets physiques,
pas du decor.
"""
import math

from maquette_core import (BG, BG_HAUT, BODY, CARD_FACE, CARD_RED, DANGER,
                           DISPLAY, H, INK, INK2, INK3, JAUNE, L, NEON, ORANGE_INK,
                           SURFACE, SURFACE_HAUT, TILE_INK,
                           T_CORPS, T_LABEL, T_MICRO, T_SOUS,
                           bloc, bouton, dos_carte, ecran, entete,
                           paragraphe, puce, texte)

# --------------------------------------------------------------------------
# Grille commune. Une seule marge, un seul pas de colonne, partout.
# --------------------------------------------------------------------------
MARGE = 26
PLEINE = L - 2 * MARGE          # 378
COL_G, COL_D, COL_W = 26, 192, 180

SYMBOLES = {"clubs": "♣", "diamonds": "♦", "hearts": "♥", "spades": "♠"}
ENSEIGNES = ["clubs", "diamonds", "hearts", "spades"]
ROUGES = ("hearts", "diamonds")
NOMS_FR = {"clubs": "Trefle", "diamonds": "Carreau", "hearts": "Coeur", "spades": "Pique"}
REGLES = {
    "clubs": ("Le Guess", ["Avant de retourner la carte, demande a un joueur de",
                           "deviner sa valeur exacte (ex. : Roi). S'il a juste, tu",
                           "distribues. Sinon, c'est lui qui prend la penalite."]),
    "diamonds": ("L'Action", ["Donne une action au joueur de ton choix."]),
    "hearts": ("La Question", ["Pose une question au joueur de ton choix."]),
    "spades": ("La Contrainte", ["Donne une contrainte a accomplir au joueur de",
                                 "ton choix."]),
}
REGLE_JOKER = ("Le Joker", ["Carte blanche ! Invente une regle qui s'applique",
                            "a toute la table jusqu'au prochain Joker… ou annule",
                            "une penalite qui vient de tomber. A toi de choisir."])
RANGS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

# Disposition des pips, recopiee de PIP_LAYOUTS (PlayingCard.tsx), en pourcentage
# de la zone centrale. La moitie basse est retournee, comme sur un vrai jeu.
PIPS = {
    "2": [(50, 12), (50, 88)],
    "3": [(50, 12), (50, 50), (50, 88)],
    "4": [(28, 12), (72, 12), (28, 88), (72, 88)],
    "5": [(28, 12), (72, 12), (50, 50), (28, 88), (72, 88)],
    "6": [(28, 12), (72, 12), (28, 50), (72, 50), (28, 88), (72, 88)],
    "7": [(28, 12), (72, 12), (50, 31), (28, 50), (72, 50), (28, 88), (72, 88)],
    "8": [(28, 12), (72, 12), (50, 31), (28, 50), (72, 50), (50, 69), (28, 88), (72, 88)],
    "9": [(28, 10), (72, 10), (28, 37), (72, 37), (50, 50),
          (28, 63), (72, 63), (28, 90), (72, 90)],
    "10": [(28, 10), (72, 10), (50, 23), (28, 37), (72, 37),
           (28, 63), (72, 63), (50, 77), (28, 90), (72, 90)],
}


# --------------------------------------------------------------------------
# Primitives locales
# --------------------------------------------------------------------------
def _pivote(contenu, angle, px, py):
    return f'<g transform="rotate({angle} {px} {py})">{contenu}</g>'


def _trait(x1, y1, x2, y2, couleur=None, epaisseur=2, opacite=None, tirets=None):
    a = [f'x1="{x1}"', f'y1="{y1}"', f'x2="{x2}"', f'y2="{y2}"',
         f'stroke="{couleur or INK}"', f'stroke-width="{epaisseur}"']
    if opacite is not None:
        a.append(f'opacity="{opacite}"')
    if tirets:
        a.append(f'stroke-dasharray="{tirets}"')
    return f'<line {" ".join(a)}/>'


def _cadre_pointille(x, y, w, h, couleur, r=8, epaisseur=2, tirets="7 5"):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="none" '
            f'stroke="{couleur}" stroke-width="{epaisseur}" stroke-dasharray="{tirets}"/>')


# Les pictogrammes sont VECTORIELS, jamais des glyphes. Une etoile, une croix ou
# une fleche de reprise posees en <text> dependent d'une police qui possede le
# caractere : Anton et Bricolage ne l'ont pas, et l'import affiche un carre vide.
# Un polygone est identique partout, Figma comme navigateur.
def _etoile(px, py, r, couleur, opacite=None):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.42
        pts.append(f"{px + rr * math.cos(ang):.1f},{py + rr * math.sin(ang):.1f}")
    o = f' opacity="{opacite}"' if opacite is not None else ""
    return f'<polygon points="{" ".join(pts)}" fill="{couleur}"{o}/>'


def _croix(px, py, r, couleur):
    return (_trait(px - r, py - r, px + r, py + r, couleur, 2.6)
            + "\n      " + _trait(px + r, py - r, px - r, py + r, couleur, 2.6))


def _coche(x, y, w, couleur):
    return (f'<polyline points="{x},{y + w * 0.52} {x + w * 0.38},{y + w * 0.86} '
            f'{x + w},{y + w * 0.12}" fill="none" stroke="{couleur}" stroke-width="3" '
            f'stroke-linecap="round" stroke-linejoin="round"/>')


def _maison(px, py, r, couleur):
    return (f'<path d="M {px - r} {py} L {px} {py - r} L {px + r} {py} Z" fill="none" '
            f'stroke="{couleur}" stroke-width="2.4" stroke-linejoin="round"/>'
            + "\n      "
            + f'<rect x="{px - r * 0.6}" y="{py}" width="{r * 1.2}" height="{r * 0.85}" '
              f'fill="none" stroke="{couleur}" stroke-width="2.4"/>')


def _reprise(px, py, r, couleur):
    """Fleche circulaire du bouton Recommencer."""
    return (f'<path d="M {px + r} {py} A {r} {r} 0 1 1 {px} {py - r}" fill="none" '
            f'stroke="{couleur}" stroke-width="2.4" stroke-linecap="round"/>'
            + "\n      "
            + f'<polygon points="{px - 4},{py - r - 4} {px + 4},{py - r} {px - 4},{py - r + 4}" '
              f'fill="{couleur}"/>')


def _sceau(px, py, r, couleur):
    """Cachet de cire du verrou premium, reduit a sa silhouette."""
    return (f'<circle cx="{px}" cy="{py}" r="{r}" fill="none" stroke="{couleur}" '
            f'stroke-width="2"/>'
            + "\n      " + _etoile(px, py, r * 0.52, couleur))


def _halo(x, y, w, h, r=14, couleur=None):
    """Rendu du battement : deux contours francs decales, jamais de flou."""
    c = couleur or NEON
    return "\n      ".join([
        f'<rect x="{x - 10}" y="{y - 10}" width="{w + 20}" height="{h + 20}" rx="{r + 8}" '
        f'fill="none" stroke="{c}" stroke-width="2" opacity="0.18"/>',
        f'<rect x="{x - 5}" y="{y - 5}" width="{w + 10}" height="{h + 10}" rx="{r + 4}" '
        f'fill="none" stroke="{c}" stroke-width="2" opacity="0.35"/>',
    ])


def _carte(x, y, w, h, rang, enseigne, surlignee=False):
    """Une carte face visible, fidele a PlayingCard : coins mono en haut a gauche
    et en bas a droite (retournes), centre propre a chaque rang."""
    sym = SYMBOLES[enseigne]
    encre = CARD_RED if enseigne in ROUGES else TILE_INK
    o = [bloc(x, y, w, h, CARD_FACE, r=max(6, w * 0.08), cerne=TILE_INK,
              epaisseur=3 if w > 60 else 2, ombre=5 if w > 60 else 3)]
    if surlignee:
        o.append(f'<rect x="{x - 5}" y="{y - 5}" width="{w + 10}" height="{h + 10}" '
                 f'rx="{max(6, w * 0.08) + 4}" fill="none" stroke="{NEON}" stroke-width="3"/>')

    tc = max(8, round(w * 0.115))
    pad = max(5, w * 0.075)
    if rang == "JOKER":
        # Coins remplaces par des etoiles : ni rang ni enseigne sur le Joker.
        o.append(_etoile(x + pad + tc * 0.4, y + pad + tc * 0.6, tc * 0.55, encre))
        o.append(_etoile(x + pad + tc * 0.4, y + pad + tc * 1.9, tc * 0.55, encre))
        o.append(_etoile(x + w - pad - tc * 0.4, y + h - pad - tc * 0.6, tc * 0.55, encre))
        o.append(_etoile(x + w - pad - tc * 0.4, y + h - pad - tc * 1.9, tc * 0.55, encre))
    else:
        o.append(texte(x + pad, y + pad + tc, rang, tc, BODY, encre, gras=700))
        o.append(texte(x + pad, y + pad + tc * 2.15, sym, tc, BODY, encre))
        coin = (texte(x + w - pad, y + h - pad - tc * 1.15, rang, tc, BODY, encre,
                      gras=700, ancre="end")
                + "\n      " + texte(x + w - pad, y + h - pad - tc * 0.15, sym, tc, BODY,
                                     encre, ancre="end"))
        o.append(_pivote(coin, 180, x + w - pad - tc / 2, y + h - pad - tc))

    cx0, cy0 = x + w / 2, y + h / 2
    if w < 62:
        # Vignette de galerie : le centre se resume au symbole, les pips seraient
        # illisibles a cette echelle.
        o.append(texte(cx0, cy0 + w * 0.17, sym, w * 0.42, BODY, encre, ancre="middle"))
        return "\n      ".join(o)

    if rang == "A":
        o.append(texte(cx0, cy0 + w * 0.21, sym, w * 0.52, BODY, encre, ancre="middle"))
    elif rang == "JOKER":
        iw, ih = w - pad * 2.4, h - pad * 4.4
        ix, iy = x + pad * 1.2, y + pad * 2.2
        o.append(_cadre_pointille(ix, iy, iw, ih, encre, r=8, epaisseur=2))
        o.append(_etoile(cx0, cy0 - h * 0.05, w * 0.15, encre))
        o.append(texte(cx0, cy0 + h * 0.13, "JOKER", w * 0.13, DISPLAY, encre,
                       ancre="middle", espacement=1.6))
    elif rang in ("J", "Q", "K"):
        iw, ih = w - pad * 2.4, h - pad * 4.4
        ix, iy = x + pad * 1.2, y + pad * 2.2
        o.append(bloc(ix, iy, iw, ih, "none", r=8, cerne=encre, epaisseur=2))
        o.append(_trait(ix, iy + ih, ix + iw, iy, encre, 2, opacite=0.25))
        o.append(texte(ix + iw * 0.2, iy + ih * 0.19, sym, w * 0.17, BODY, encre, ancre="middle"))
        o.append(_pivote(texte(ix + iw * 0.8, iy + ih * 0.87, sym, w * 0.17, BODY, encre,
                               ancre="middle"), 180, ix + iw * 0.8, iy + ih * 0.82))
        pw, ph = w * 0.3, h * 0.17
        o.append(bloc(cx0 - pw / 2, cy0 - ph / 2, pw, ph, CARD_FACE, r=6, cerne=encre, epaisseur=2))
        o.append(texte(cx0, cy0 + ph * 0.3, rang, w * 0.21, DISPLAY, encre, ancre="middle"))
    else:
        zx, zy = x + pad * 1.3, y + pad * 2.6
        zw, zh = w - pad * 2.6, h - pad * 5.2
        for px, py in PIPS[rang]:
            gx, gy = zx + zw * px / 100, zy + zh * py / 100
            t = texte(gx, gy + w * 0.06, sym, w * 0.17, BODY, encre, ancre="middle")
            o.append(_pivote(t, 180, gx, gy) if py > 50 else t)
    return "\n      ".join(o)


def _dos(x, y, w, h, angle=None):
    d = dos_carte(x, y, w, h)
    cadre = (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{max(6, w * 0.08)}" '
             f'fill="none" stroke="{TILE_INK}" stroke-width="3"/>')
    ombre = bloc(x + 5, y + 5, w, h, TILE_INK, r=max(6, w * 0.08), epaisseur=0)
    bloc_dos = "\n      ".join([ombre, d, cadre])
    return _pivote(bloc_dos, angle, x + w / 2, y + h / 2) if angle else bloc_dos


def _rond(x, y, picto, d=44):
    return (bloc(x, y, d, d, SURFACE, r=d / 2, cerne=INK, epaisseur=2)
            + "\n      " + picto(x + d / 2, y + d / 2, 9, INK))


def _barres_ecran(cx, cy):
    """Les deux commandes permanentes du plateau : accueil et remelange."""
    return [_rond(cx + 24, cy + 58, _maison), _rond(cx + L - 68, cy + 58, _reprise)]


def _hud(cx, cy, nom, restant, total, sous="C'est ton tour de distribuer"):
    """StatusBar : nom du joueur, sous-titre, barre de progression, compteur."""
    avance = 0 if total == 0 else (total - restant) / total
    o = _barres_ecran(cx, cy)
    o += [texte(cx + L / 2, cy + 186, nom.upper(), 34, DISPLAY, INK, ancre="middle"),
          texte(cx + L / 2, cy + 212, sous, T_LABEL, BODY, INK2, ancre="middle"),
          bloc(cx + MARGE, cy + 244, 250, 10, SURFACE, r=5, cerne=INK, epaisseur=2)]
    if avance > 0:
        o.append(bloc(cx + MARGE, cy + 244, max(10, 250 * avance), 10, NEON, r=5,
                      cerne=INK, epaisseur=2))
    o += [bloc(cx + 290, cy + 232, 114, 34, SURFACE, r=17, cerne=INK, epaisseur=2),
          texte(cx + 347, cy + 254, f"{restant}/{total}", T_LABEL, DISPLAY, INK,
                ancre="middle")]
    return o


def _scrim(cx, cy):
    return bloc(cx, cy, L, H, INK, r=38, epaisseur=0, opacite=0.74)


def _plateau_muet(cx, cy):
    """Le plateau tel qu'il reste visible sous une modale : carte revelee, HUD."""
    o = _hud(cx, cy, "Nawel", 48, 52)
    o.append(_carte(cx + 152, cy + 300, 126, 182, "3", "hearts"))
    o.append(bloc(cx + MARGE, cy + 512, PLEINE, 150, SURFACE_HAUT, r=14, cerne=INK, epaisseur=2))
    o.append(texte(cx + L / 2, cy + 560, "LA QUESTION", 22, DISPLAY, INK, ancre="middle"))
    o.append(paragraphe(cx + L / 2, cy + 592, ["Pose une question au joueur de ton choix."],
                        T_LABEL, INK2, ancre="middle"))
    o.append(texte(cx + L / 2, cy + 632, "VALEUR   3 ♥", T_LABEL, DISPLAY, NEON, ancre="middle"))
    return o


def _sous_titre(cx, cy, y, libelle):
    return texte(cx + MARGE, cy + y, libelle, T_CORPS, BODY, INK, gras=700)


# --------------------------------------------------------------------------
# Feuille d'options du Coupe-Gorge (HubScreen)
# --------------------------------------------------------------------------
def _feuille_options(cx, cy, paquets=1, jokers=True, infini=None, enseignes_hors=(),
                     rangs_hors=(), compteur="52 cartes dans le paquet", actif=True):
    """Trois etats de la meme feuille : nominal, paquet vide, infini premium.

    `infini` vaut None (verrouille par sceau), True (actif) ou False (off).
    """
    b = [_scrim(cx, cy),
         bloc(cx, cy + 130, L, 762, BG, r=18, cerne=INK, epaisseur=3),
         texte(cx + MARGE, cy + 180, "LE COUPE-GORGE - OPTIONS", T_SOUS, DISPLAY, INK)]

    b.append(_sous_titre(cx, cy, 220, "Nombre de paquets"))
    pas = (PLEINE - 119) / 2
    for i, n in enumerate((1, 2, 3)):
        bx = cx + MARGE + i * pas
        pris = n == paquets
        b.append(bloc(bx, cy + 234, 119, 54, JAUNE if pris else SURFACE, r=10,
                      cerne=TILE_INK if pris else INK, epaisseur=3,
                      ombre=4 if pris else 0, ombre_couleur=TILE_INK))
        b.append(texte(bx + 59.5, cy + 258, str(n), T_SOUS, DISPLAY,
                       TILE_INK if pris else INK, ancre="middle"))
        b.append(texte(bx + 59.5, cy + 277, f"({n * 52} cartes)", T_MICRO, BODY,
                       TILE_INK if pris else INK2, ancre="middle"))

    b.append(bloc(cx + MARGE, cy + 304, PLEINE, 56, SURFACE, r=10, cerne=INK, epaisseur=3))
    b.append(texte(cx + 48, cy + 338, "Jokers (2 par paquet)", T_CORPS, BODY, INK, gras=700))
    b.append(bloc(cx + L - 74, cy + 320, 24, 24, JAUNE if jokers else SURFACE, r=5,
                  cerne=TILE_INK if jokers else INK, epaisseur=2))
    if jokers:
        b.append(_coche(cx + L - 69, cy + 326, 14, TILE_INK))

    on = infini is True
    b.append(bloc(cx + MARGE, cy + 376, PLEINE, 56, JAUNE if on else SURFACE, r=10,
                  cerne=TILE_INK if on else INK, epaisseur=3,
                  ombre=4 if on else 0, ombre_couleur=TILE_INK))
    b.append(texte(cx + 48, cy + 410, "Cartes aleatoires a l'infini", T_CORPS, BODY,
                   TILE_INK if on else INK, gras=700))
    if infini is None:
        b.append(bloc(cx + 282, cy + 392, 122, 26, SURFACE, r=13, cerne=INK, epaisseur=2))
        b.append(_sceau(cx + 299, cy + 405, 8, INK))
        b.append(texte(cx + 314, cy + 410, "PREMIUM", T_MICRO, DISPLAY, INK, espacement=1.4))
    else:
        b.append(texte(cx + L - 48, cy + 410, "ACTIVE" if on else "OFF", T_LABEL, DISPLAY,
                       TILE_INK if on else INK, ancre="end", espacement=1))

    b.append(_sous_titre(cx, cy, 466, "Composition du paquet"))
    for i, ens in enumerate(ENSEIGNES):
        bx = cx + (COL_G if i % 2 == 0 else COL_D)
        by = cy + 480 + (i // 2) * 64
        hors = ens in enseignes_hors
        b.append(bloc(bx, by, COL_W, 52, SURFACE, r=10, cerne=INK, epaisseur=3,
                      ombre=0 if hors else 4, ombre_couleur=INK,
                      opacite=0.45 if hors else None))
        b.append(texte(bx + 18, by + 34, SYMBOLES[ens], T_SOUS, BODY, INK,
                       opacite=0.45 if hors else None))
        b.append(texte(bx + 46, by + 33, REGLES[ens][0], T_CORPS, BODY, INK, gras=700,
                       opacite=0.45 if hors else None))
        if hors:
            b.append(_trait(bx + 44, by + 28, bx + COL_W - 14, by + 28, INK, 2, opacite=0.7))

    pasr = (PLEINE - 40) / 7
    for i, r in enumerate(RANGS):
        rx = cx + MARGE + (i % 8) * pasr
        ry = cy + 620 + (i // 8) * 52
        hors = r in rangs_hors
        b.append(bloc(rx, ry, 40, 42, SURFACE if hors else JAUNE, r=9,
                      cerne=INK if hors else TILE_INK, epaisseur=2,
                      ombre=0 if hors else 3, ombre_couleur=TILE_INK,
                      opacite=0.45 if hors else None))
        b.append(texte(rx + 20, ry + 28, r, T_LABEL, DISPLAY, INK if hors else TILE_INK,
                       ancre="middle", opacite=0.45 if hors else None))
        if hors:
            b.append(_trait(rx + 7, ry + 21, rx + 33, ry + 21, INK, 2, opacite=0.7))

    if actif:
        b.append(texte(cx + MARGE, cy + 752, compteur, T_LABEL, BODY, INK3))
    else:
        b.append(paragraphe(cx + MARGE, cy + 746, ["Paquet vide - reintegre au moins une",
                                                   "couleur et une valeur."], T_LABEL, DANGER,
                            interligne=19, gras=700))

    if actif:
        b.append(bouton(cx + MARGE, cy + 782, PLEINE, "C'EST PARTI !", True, 66, 20))
    else:
        b.append(bloc(cx + MARGE, cy + 782, PLEINE, 66, SURFACE, r=12, cerne=INK3, epaisseur=3))
        b.append(texte(cx + L / 2, cy + 823, "C'EST PARTI !", 20, DISPLAY, INK3, ancre="middle"))
    return b


def options(s, cx, cy):
    b = _feuille_options(cx, cy)
    ecran(s, "Coupe-Gorge - options", cx, cy, "\n      ".join(b))


def options_paquet_vide(s, cx, cy):
    b = _feuille_options(cx, cy, enseignes_hors=tuple(ENSEIGNES), rangs_hors=tuple(RANGS),
                         actif=False)
    ecran(s, "Coupe-Gorge - options, paquet vide", cx, cy, "\n      ".join(b))


def options_infini_premium(s, cx, cy):
    b = _feuille_options(cx, cy, paquets=2, infini=True, compteur="104 cartes dans le paquet")
    ecran(s, "Coupe-Gorge - options, infini premium actif", cx, cy, "\n      ".join(b))


# --------------------------------------------------------------------------
# Plateau de jeu (GameBoard)
# --------------------------------------------------------------------------
def pioche(s, cx, cy):
    b = _hud(cx, cy, "Nawel", 52, 52)
    b += [_dos(cx + 128, cy + 348, 176, 254, angle=-7),
          _dos(cx + 122, cy + 342, 176, 254, angle=-3),
          _dos(cx + 118, cy + 336, 176, 254),
          bloc(cx + 178, cy + 556, 56, 28, CARD_FACE, r=14, cerne=TILE_INK, epaisseur=2),
          texte(cx + 206, cy + 576, "52", T_LABEL, DISPLAY, TILE_INK, ancre="middle"),
          texte(cx + L / 2, cy + 668, "TOUCHE LE PAQUET POUR TIRER", 22, DISPLAY, INK,
                ancre="middle"),
          texte(cx + L / 2, cy + 698, "Nawel, la table t'attend", T_CORPS, BODY, INK2,
                ancre="middle")]
    ecran(s, "Coupe-Gorge - la pioche", cx, cy, "\n      ".join(b))


def trefle_face_cachee(s, cx, cy):
    b = _hud(cx, cy, "Nawel", 51, 52)
    b += [_dos(cx + 118, cy + 288, 194, 280),
          texte(cx + L / 2, cy + 614, "TREFLE - LE GUESS", 21, DISPLAY, INK, ancre="middle"),
          paragraphe(cx + L / 2, cy + 642, ["Fais deviner sa valeur exacte a la table",
                                            "avant de la retourner"], T_CORPS, INK2,
                     interligne=22, ancre="middle"),
          _halo(cx + 62, cy + 700, 306, 48, r=24),
          bloc(cx + 62, cy + 700, 306, 48, SURFACE, r=24, cerne=INK, epaisseur=3, ombre=4,
               ombre_couleur=INK),
          bloc(cx + 84, cy + 719, 10, 10, NEON, r=5, epaisseur=0),
          texte(cx + L / 2, cy + 730, "TOUCHER POUR REVELER", T_LABEL, DISPLAY, INK,
                ancre="middle", espacement=1.4),
          bloc(cx + 336, cy + 719, 10, 10, NEON, r=5, epaisseur=0)]
    ecran(s, "Coupe-Gorge - trefle face cachee", cx, cy, "\n      ".join(b))


def _encart_regle(cx, cy, y, hauteur, symbole, titre, lignes, valeur=None, accent=True):
    """Encart de regle : filigrane d'enseigne, pastille, titre, filet, description.

    `symbole` vaut None pour le Joker, qui porte une etoile vectorielle.
    """
    teinte = NEON if accent else INK
    o = [bloc(cx + MARGE, cy + y, PLEINE, hauteur, SURFACE_HAUT, r=14, cerne=INK, epaisseur=2)]
    if symbole:
        o.append(texte(cx + L - 34, cy + y + hauteur - 6, symbole, 96, BODY, INK,
                       ancre="end", opacite=0.06))
    else:
        o.append(_etoile(cx + L - 68, cy + y + hauteur - 42, 44, INK, opacite=0.06))
    o += [bloc(cx + L / 2 - 23, cy + y + 18, 46, 46, SURFACE, r=23, cerne=teinte, epaisseur=2)]
    if symbole:
        o.append(texte(cx + L / 2, cy + y + 50, symbole, T_SOUS, BODY, teinte, ancre="middle"))
    else:
        o.append(_etoile(cx + L / 2, cy + y + 41, 12, teinte))
    o += [texte(cx + L / 2, cy + y + 96, titre.upper(), 24, DISPLAY, INK, ancre="middle"),
          _trait(cx + 48, cy + y + 112, cx + L - 48, cy + y + 112, INK, 1, opacite=0.35),
          paragraphe(cx + L / 2, cy + y + 138, lignes, T_CORPS, INK2, interligne=22,
                     ancre="middle")]
    if valeur:
        o.append(texte(cx + L / 2 - 42, cy + y + hauteur - 22, "VALEUR", T_LABEL, DISPLAY,
                       INK2, ancre="end", espacement=1.2))
        o.append(texte(cx + L / 2 - 30, cy + y + hauteur - 21, valeur, T_SOUS, DISPLAY, NEON))
    return o


def carte_revelee(s, cx, cy):
    b = _hud(cx, cy, "Nawel", 51, 52)
    b.append(_carte(cx + 140, cy + 286, 150, 216, "3", "hearts", surlignee=True))
    b += _encart_regle(cx, cy, 528, 190, SYMBOLES["hearts"], "La Question",
                       ["Pose une question au joueur de ton choix."], valeur="3 ♥")
    b.append(bouton(cx + MARGE, cy + 742, PLEINE, "CONTESTER", True, 62, 19))
    b.append(bouton(cx + MARGE, cy + 818, PLEINE, "TOUR SUIVANT", False, 62, 19))
    ecran(s, "Coupe-Gorge - carte revelee", cx, cy, "\n      ".join(b))


def joker(s, cx, cy):
    b = _hud(cx, cy, "Nawel", 50, 52)
    b.append(_carte(cx + 140, cy + 286, 150, 216, "JOKER", "spades", surlignee=True))
    b += _encart_regle(cx, cy, 528, 234, None, REGLE_JOKER[0], REGLE_JOKER[1])
    b.append(bouton(cx + MARGE, cy + 800, PLEINE, "TOUR SUIVANT", False, 62, 19))
    ecran(s, "Coupe-Gorge - Joker", cx, cy, "\n      ".join(b))


def qui_conteste(s, cx, cy):
    b = _plateau_muet(cx, cy)
    b.append(_scrim(cx, cy))
    b.append(bloc(cx + MARGE, cy + 306, PLEINE, 320, SURFACE_HAUT, r=16, cerne=NEON,
                  epaisseur=3, ombre=6, ombre_couleur=INK))
    b.append(texte(cx + L / 2, cy + 358, "QUI CONTESTE ?", 22, DISPLAY, INK, ancre="middle"))
    for i, nom in enumerate(["Adam", "Emilien", "Amina"]):
        by = cy + 388 + i * 68
        b.append(bloc(cx + 48, by, 334, 56, SURFACE, r=10, cerne=INK, epaisseur=3, ombre=4,
                      ombre_couleur=INK))
        b.append(texte(cx + 215, by + 36, nom, 17, BODY, INK, gras=700, ancre="middle"))
    b.append(texte(cx + L / 2, cy + 660, "Toucher hors de la fenetre pour fermer",
                   T_LABEL, BODY, BG, ancre="middle", opacite=0.75))
    ecran(s, "Coupe-Gorge - qui conteste", cx, cy, "\n      ".join(b))


# --------------------------------------------------------------------------
# ContestModal
# --------------------------------------------------------------------------
def _modale_contest(cx, cy, niveau, penalite, multiplicateur, escalade=None):
    b = _plateau_muet(cx, cy)
    b.append(_scrim(cx, cy))
    haut = 180
    bas = 772 if escalade else 700
    b.append(bloc(cx + MARGE, cy + haut, PLEINE, bas - haut, SURFACE_HAUT, r=16, cerne=NEON,
                  epaisseur=3, ombre=6, ombre_couleur=INK))
    b.append(bloc(cx + 140, cy + haut - 15, 150, 30, NEON, r=15, cerne=TILE_INK, epaisseur=2))
    b.append(texte(cx + 215, cy + haut + 5, f"NIVEAU {niveau}/3", T_LABEL, DISPLAY, TILE_INK,
                   ancre="middle", espacement=1.4))
    b.append(_croix(cx + L - 54, cy + haut + 36, 8, INK3))
    b.append(texte(cx + L / 2, cy + haut + 78, "CONTESTATION", 26, DISPLAY, NEON, ancre="middle"))

    for bx, label, nom in ((cx + 50, "ATTAQUANT", "Adam"), (cx + 246, "DEFIE", "Nawel")):
        b.append(texte(bx + 67, cy + haut + 120, label, T_MICRO, DISPLAY, INK2,
                       ancre="middle", espacement=1.6))
        b.append(bloc(bx, cy + haut + 130, 134, 46, SURFACE_HAUT, r=10, cerne=INK, epaisseur=2))
        b.append(texte(bx + 67, cy + haut + 160, nom, 17, BODY, INK, gras=700, ancre="middle"))
    b.append(texte(cx + L / 2, cy + haut + 162, "VS", T_SOUS, DISPLAY, INK3, ancre="middle"))

    b.append(_halo(cx + 74, cy + haut + 200, 282, 66, r=14))
    b.append(texte(cx + L / 2, cy + haut + 250, penalite, 44, DISPLAY, NEON, ancre="middle"))
    b.append(texte(cx + L / 2, cy + haut + 296, "Multiplicateur actuel :", T_LABEL, BODY, INK2,
                   ancre="middle"))
    b.append(texte(cx + L / 2, cy + haut + 318, f"x{multiplicateur}", T_SOUS, DISPLAY, INK,
                   ancre="middle"))

    y = haut + 344
    if escalade:
        b.append(bouton(cx + MARGE, cy + y, PLEINE, f"ESCALADER (X{escalade})", True, 60, 19))
        y += 78
    b.append(texte(cx + L / 2, cy + y + 18, "QUI PERD LA CONTESTATION ?", T_LABEL, DISPLAY,
                   INK2, ancre="middle", espacement=1.4))
    b.append(bouton(cx + MARGE, cy + y + 34, PLEINE, "ADAM PREND LA PENALITE", False, 56, 16))
    b.append(bouton(cx + MARGE, cy + y + 102, PLEINE, "NAWEL PREND LA PENALITE", False, 56, 16))
    return b


def contestation_niveau_1(s, cx, cy):
    b = _modale_contest(cx, cy, 1, "3 penalites", 1, escalade=2)
    ecran(s, "Contestation - niveau 1", cx, cy, "\n      ".join(b))


def contestation_niveau_3(s, cx, cy):
    b = _modale_contest(cx, cy, 3, "12 penalites", 4)
    ecran(s, "Contestation - niveau 3", cx, cy, "\n      ".join(b))


def pioche_epuisee(s, cx, cy):
    b = _hud(cx, cy, "Nawel", 0, 52, sous="Derniere carte distribuee")
    b += [_cadre_pointille(cx + 128, cy + 336, 176, 254, INK, r=14, epaisseur=3, tirets="10 8"),
          texte(cx + L / 2, cy + 470, "0", 56, DISPLAY, INK, ancre="middle", opacite=0.28),
          texte(cx + L / 2, cy + 500, "PAQUET EPUISE", T_LABEL, DISPLAY, INK3, ancre="middle",
                espacement=1.6),
          bloc(cx + MARGE, cy + 700, PLEINE, 150, SURFACE_HAUT, r=14, cerne=INK, epaisseur=2),
          texte(cx + L / 2, cy + 772, "FIN DE PARTIE", 34, DISPLAY, NEON, ancre="middle"),
          texte(cx + L / 2, cy + 806, "Toutes les cartes ont ete jouees", T_CORPS, BODY, INK2,
                ancre="middle"),
          texte(cx + L / 2, cy + 832, "Place a l'addition", T_LABEL, BODY, INK3, ancre="middle")]
    ecran(s, "Coupe-Gorge - pioche epuisee", cx, cy, "\n      ".join(b))


# --------------------------------------------------------------------------
# ConfirmDialog (BorderlandScreen)
# --------------------------------------------------------------------------
def _dialogue(cx, cy, titre, lignes, confirmer, y=316, hauteur=300):
    b = _plateau_muet(cx, cy)
    b.append(_scrim(cx, cy))
    b.append(bloc(cx + 52, cy + y, L - 104, hauteur, SURFACE_HAUT, r=16, cerne=INK,
                  epaisseur=3, ombre=6, ombre_couleur=INK))
    b.append(texte(cx + L / 2, cy + y + 52, titre.upper(), 23, DISPLAY, INK, ancre="middle"))
    b.append(paragraphe(cx + L / 2, cy + y + 88, lignes, T_LABEL, INK2, interligne=21,
                        ancre="middle"))
    b.append(bouton(cx + 78, cy + y + hauteur - 148, L - 156, confirmer, True, 58, 17))
    b.append(bouton(cx + 78, cy + y + hauteur - 78, L - 156, "ANNULER", False, 58, 17))
    return b


def confirmer_remelange(s, cx, cy):
    b = _dialogue(cx, cy, "Recommencer ?",
                  ["La partie en cours sera perdue et un",
                   "nouveau paquet sera melange, avec les",
                   "memes joueurs."],
                  "OUI, ON REMELANGE")
    ecran(s, "Coupe-Gorge - confirmer le remelange", cx, cy, "\n      ".join(b))


def confirmer_sortie(s, cx, cy):
    b = _dialogue(cx, cy, "Quitter la partie ?",
                  ["La partie en cours sera perdue.",
                   "Vous pourrez en relancer une depuis",
                   "l'accueil."],
                  "QUITTER")
    b.append(texte(cx + L / 2, cy + 660, "Le retour materiel ouvre le meme dialogue",
                   T_LABEL, BODY, BG, ancre="middle", opacite=0.75))
    ecran(s, "Coupe-Gorge - confirmer la sortie", cx, cy, "\n      ".join(b))


# --------------------------------------------------------------------------
# Planches PlayingCard
# --------------------------------------------------------------------------
def _titre_planche(cx, cy, titre, sous):
    return [texte(cx + MARGE, cy + 96, titre.upper(), T_SOUS, DISPLAY, INK),
            paragraphe(cx + MARGE, cy + 122, sous, T_LABEL, INK2, interligne=19),
            _trait(cx + MARGE, cy + 140 + 19 * (len(sous) - 1), cx + L - MARGE,
                   cy + 140 + 19 * (len(sous) - 1), INK, 3)]


def cartes_as_et_figures(s, cx, cy):
    b = _titre_planche(cx, cy, "Cartes - As et figures",
                       ["As au grand symbole central, figures a cadre en miroir :",
                        "diagonale de separation et lettre sur pastille."])
    modeles = [("A", "spades", "AS - GRAND SYMBOLE"),
               ("J", "diamonds", "VALET - A L'EPEE"),
               ("Q", "hearts", "DAME - AU JOYAU"),
               ("K", "clubs", "ROI - COURONNE")]
    for i, (rang, ens, label) in enumerate(modeles):
        bx = cx + (COL_G if i % 2 == 0 else COL_D)
        by = cy + 210 + (i // 2) * 320
        b.append(bloc(bx, by, COL_W, 288, SURFACE, r=14, cerne=INK, epaisseur=2))
        b.append(_carte(bx + 25, by + 22, 130, 188, rang, ens))
        b.append(puce(bx + 18, by + 234, label, JAUNE))
        b.append(texte(bx + 18, by + 274, f"{rang} de {NOMS_FR[ens]}", T_MICRO, BODY, INK3))
    ecran(s, "Cartes - As et figures", cx, cy, "\n      ".join(b))


def cartes_chiffrees_et_dos(s, cx, cy):
    b = _titre_planche(cx, cy, "Cartes - chiffrees et dos",
                       ["Dispositions de pips 2 a 10, moitie basse retournee.",
                        "Coins mono en haut a gauche et en bas a droite."])
    pas = (PLEINE - 84) / 3
    for i, rang in enumerate(["2", "3", "4", "5", "6", "7", "8", "9", "10"]):
        bx = cx + MARGE + (i % 4) * pas
        by = cy + 200 + (i // 4) * 158
        b.append(_carte(bx, by, 84, 120, rang, "spades" if i % 2 == 0 else "diamonds"))
    b.append(_dos(cx + MARGE + pas, cy + 516, 84, 120))
    b.append(puce(cx + MARGE + pas * 2, cy + 552, "DOS CARD-BACK", JAUNE))
    b.append(bloc(cx + MARGE, cy + 690, PLEINE, 176, SURFACE, r=14, cerne=INK, epaisseur=2))
    b.append(texte(cx + 48, cy + 728, "CE QUE CHAQUE RANG CHANGE", T_LABEL, DISPLAY, INK,
                   espacement=1.4))
    b.append(paragraphe(cx + 48, cy + 758, [
        "Chaque carte a sa silhouette propre : les pips de la",
        "moitie basse sont retournes, comme sur un vrai jeu.",
        "Les coins portent le rang en mono, en haut a gauche",
        "et en bas a droite pivote. Le dos est un asset creme",
        "fixe, cerne d'encre de tuile dans les deux themes."], T_LABEL, INK2, interligne=21))
    ecran(s, "Cartes - chiffrees et dos", cx, cy, "\n      ".join(b))


def cartes_joker(s, cx, cy):
    b = _titre_planche(cx, cy, "Cartes - Joker",
                       ["La carte hors norme du paquet : cadre interieur pointille,",
                        "etoile scintillante, lettrage JOKER, coins en etoiles."])
    b.append(_carte(cx + 115, cy + 220, 200, 288, "JOKER", "spades"))
    for i, (label, ligne) in enumerate([
            ("CADRE POINTILLE", "border-dashed, jamais un aplat plein"),
            ("ETOILE SCINTILLANTE", "le seul centre sans pip ni figure"),
            ("LETTRAGE JOKER", "police d'affichage, interlettrage large"),
            ("COINS EN ETOILES", "l'etoile remplace rang et enseigne")]):
        by = cy + 552 + i * 76
        b.append(bloc(cx + MARGE, by, PLEINE, 64, SURFACE, r=12, cerne=INK, epaisseur=2))
        b.append(texte(cx + 48, by + 28, label, T_LABEL, DISPLAY, INK, espacement=1.2))
        b.append(texte(cx + 48, by + 50, ligne, T_LABEL, BODY, INK2))
    ecran(s, "Cartes - Joker", cx, cy, "\n      ".join(b))


def galerie_52_cartes(s, cx, cy):
    b = [texte(cx + MARGE, cy + 96, "GALERIE DES 52 CARTES", T_SOUS, DISPLAY, INK),
         texte(cx + MARGE, cy + 120, "Page de controle, ouverte par /?cards", T_LABEL, BODY, INK3),
         _trait(cx + MARGE, cy + 138, cx + L - MARGE, cy + 138, INK, 3)]
    lw, lh = 50, 71
    pas = (PLEINE - lw) / 6
    y0 = cy + 166
    for si, ens in enumerate(ENSEIGNES):
        base = y0 + si * 172
        for ri, rang in enumerate(RANGS):
            col = ri % 7
            lig = ri // 7
            b.append(_carte(cx + MARGE + col * pas, base + lig * 82, lw, lh, rang, ens))
    ecran(s, "Galerie des 52 cartes", cx, cy, "\n      ".join(b))


# --------------------------------------------------------------------------
# RulesScreen
# --------------------------------------------------------------------------
def regles_coupe_gorge(s, cx, cy):
    b = [entete(cx, cy, "Regles du Coupe-Gorge")]
    b.append(paragraphe(cx + L / 2, cy + 154, [
        "Chaque carte arrive face cachee : fais deviner sa valeur",
        "avant de la retourner. Chaque couleur a ensuite sa regle."],
        T_LABEL, INK2, interligne=20, ancre="middle"))
    b.append(texte(cx + L / 2, cy + 200, "Les As valent une PENALITE MAJEURE.", T_CORPS,
                   BODY, ORANGE_INK, gras=700, ancre="middle"))

    def fiche(y, symbole, titre, lignes, accent=INK):
        o = [bloc(cx + MARGE, cy + y, PLEINE, 104, SURFACE, r=14, cerne=INK, epaisseur=2)]
        # Filigrane d'abord, puis la pastille, puis son symbole : l'ordre de
        # l'ancienne version noyait le symbole SOUS la pastille.
        if symbole:
            o.append(texte(cx + L - 36, cy + y + 100, symbole, 72, BODY, accent, ancre="end",
                           opacite=0.07))
        else:
            o.append(_etoile(cx + L - 62, cy + y + 74, 32, accent, opacite=0.07))
        o.append(bloc(cx + 48, cy + y + 13, 36, 36, BG_HAUT, r=9, cerne=INK, epaisseur=2))
        if symbole:
            o.append(texte(cx + 66, cy + y + 38, symbole, T_SOUS, BODY, accent, ancre="middle"))
        else:
            o.append(_etoile(cx + 66, cy + y + 31, 11, accent))
        o += [texte(cx + 96, cy + y + 39, titre.upper(), 19, DISPLAY, INK),
              paragraphe(cx + 48, cy + y + 64, lignes, T_LABEL, INK2, interligne=16)]
        return o

    for i, ens in enumerate(ENSEIGNES):
        titre, lignes = REGLES[ens]
        b += fiche(220 + i * 112, SYMBOLES[ens], titre, lignes,
                   accent=NEON if ens in ROUGES else INK)
    b += fiche(668, None, REGLE_JOKER[0], REGLE_JOKER[1], accent=NEON)

    b.append(bloc(cx + MARGE, cy + 784, PLEINE, 104, SURFACE_HAUT, r=14, cerne=NEON, epaisseur=2))
    b.append(texte(cx + 48, cy + 816, "LE CONTEST", 19, DISPLAY, ORANGE_INK))
    b.append(paragraphe(cx + 48, cy + 840, [
        "Tu peux contester une carte pour doubler la mise. Le",
        "joueur suivant peut accepter ou escalader (x2, puis x4).",
        "Celui qui accepte prend tout. Courage ou folie ?"], T_LABEL, INK2, interligne=16))
    ecran(s, "Regles du Coupe-Gorge", cx, cy, "\n      ".join(b))


ECRANS = [
    options,
    options_paquet_vide,
    options_infini_premium,
    pioche,
    trefle_face_cachee,
    carte_revelee,
    joker,
    qui_conteste,
    contestation_niveau_1,
    contestation_niveau_3,
    pioche_epuisee,
    confirmer_remelange,
    confirmer_sortie,
    cartes_as_et_figures,
    cartes_chiffrees_et_dos,
    cartes_joker,
    galerie_52_cartes,
    regles_coupe_gorge,
]
