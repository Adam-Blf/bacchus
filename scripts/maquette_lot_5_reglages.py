# -*- coding: utf-8 -*-
"""Lot 5 : reglages, restauration d'achat, regles personnalisees, cookies.

Copie et ordre repris des composants reels, pas inventes :
  - src/components/screens/SettingsScreen.tsx (sections, libelles, statuts,
    messages de restauration, texte de reinitialisation, bloc A propos) ;
  - src/components/ui/ConfirmDialog.tsx (titre, message, libelles des boutons) ;
  - src/components/screens/CustomRulesScreen.tsx (etat vide, cartes de regle,
    feuille editeur, jetons, compteur sur 280, pastilles de modes, penalites) ;
  - src/components/cookies/CookieConsent.tsx (niveaux 1 et 2, poids egal entre
    refus et acceptation, ligne Necessaire toujours active).

PALETTE. BG et INK portent chaque ecran. NEON ne sert qu'a l'action primaire,
JAUNE qu'a la selection, DANGER et SUCCES qu'a un etat. PREMIUM n'apparait que
la ou il est question d'achat. Deux couleurs saturees visibles au maximum.

ALIGNEMENT. Marge laterale unique de 26, blocs pleine largeur de L - 52, grille
a deux colonnes de 180 posee en 26 et 224, pas vertical constant par liste.
"""
from maquette_core import (BG, BODY, CARD_RED, DANGER, DISPLAY, H, INK, INK2, INK3, JAUNE, L,
                           ORANGE_INK, PREMIUM, SUCCES, SURFACE, SURFACE_HAUT, TILE_INK,
                           T_CORPS, T_LABEL, T_MICRO, T_SOUS,
                           bloc, bouton, ecran, entete, icone, paragraphe, texte)

MARGE = 26
LARG = L - 2 * MARGE      # 378, largeur d'un bloc pleine largeur
COL_G, COL_D, COL_W = 26, 224, 180   # grille a deux colonnes, gouttiere de 18
RETRAIT = 22              # retrait du texte a l'interieur d'une carte
# Grille interne d'une feuille : la feuille consomme la marge de 26, son contenu
# reprend la meme logique un cran plus loin, en 44 / 224, colonnes de 162.
INT_G, INT_D, INT_W = 44, 224, 162
INT_LARG = LARG - 36      # 342, largeur pleine a l'interieur d'une feuille


# ---------------------------------------------------------------- primitives


def _titre_section(cx, y, libelle):
    """Intitule de section : meme taille, meme couleur, meme graisse partout."""
    return texte(cx + MARGE, y, libelle.upper(), T_LABEL, DISPLAY, INK3, espacement=1.2)


def _carte(cx, y, h, cerne=None, fond=None):
    return bloc(cx + MARGE, y, LARG, h, fond or SURFACE, r=12,
                cerne=cerne or INK, epaisseur=2, ombre=3, ombre_couleur=cerne or INK)


def _rangee(cx, y, libelle, valeur=None, h=44, chevron=False):
    """Ligne de reglage : libelle a gauche sur le retrait, valeur a droite."""
    b = [_carte(cx, y, h),
         texte(cx + MARGE + RETRAIT, y + h / 2 + 5, libelle, T_LABEL, BODY, INK, gras=700)]
    if valeur:
        b.append(texte(cx + L - MARGE - RETRAIT, y + h / 2 + 5, valeur,
                       T_MICRO, BODY, INK3, ancre="end"))
    if chevron:
        b.append(texte(cx + L - MARGE - RETRAIT, y + h / 2 + 7, "›", T_SOUS, DISPLAY, INK3,
                       ancre="end"))
    return "\n      ".join(b)


def _liste(cx, y, libelles, pas=34):
    """Carte unique portant plusieurs entrees au meme pas vertical."""
    h = pas * len(libelles)
    b = [_carte(cx, y, h)]
    for i, lab in enumerate(libelles):
        if i:
            b.append(f'<line x1="{cx + MARGE + RETRAIT}" y1="{y + i * pas}" '
                     f'x2="{cx + L - MARGE - RETRAIT}" y2="{y + i * pas}" '
                     f'stroke="{INK}" stroke-width="1" opacity="0.28"/>')
        b.append(texte(cx + MARGE + RETRAIT, y + i * pas + pas / 2 + 5, lab, T_LABEL, BODY, INK))
        b.append(texte(cx + L - MARGE - RETRAIT, y + i * pas + pas / 2 + 6, "›",
                       T_LABEL, DISPLAY, INK3, ancre="end"))
    return "\n      ".join(b)


def _etiquette(x, y, libelle, encre=INK3, bord=INK, fond=SURFACE, h=26, taille=T_MICRO - 1):
    """Pastille de statut, cernee et non remplie : elle informe, elle ne crie pas."""
    w = 20 + len(libelle) * (taille * 0.66)
    return (bloc(x - w, y, w, h, fond, r=h / 2, cerne=bord, epaisseur=2)
            + "\n      " + texte(x - w / 2, y + h / 2 + 4, libelle.upper(), taille, DISPLAY,
                                 encre, ancre="middle", espacement=0.6))


def _case(x, y, cochee=False, taille=24):
    """Case a cocher. Cochee, elle passe au JAUNE : le seul pop autorise."""
    fond = JAUNE if cochee else SURFACE
    bord = TILE_INK if cochee else INK
    b = [bloc(x, y, taille, taille, fond, r=6, cerne=bord, epaisseur=3)]
    if cochee:
        b.append(f'<path d="M{x + 6} {y + taille / 2} l{taille * 0.22} {taille * 0.24} '
                 f'l{taille * 0.42} -{taille * 0.46}" fill="none" stroke="{TILE_INK}" '
                 f'stroke-width="3.4" stroke-linecap="square"/>')
    return "\n      ".join(b)


def _action(bx, by, geste):
    """Bouton d'action d'une carte de regle. Les pictogrammes sont traces, pas
    ecrits : un caractere fantaisie tombe en carre vide des que la police manque.
    """
    b = [bloc(bx, by, 36, 36, SURFACE, r=10, cerne=INK, epaisseur=2)]
    t = f'fill="none" stroke="{INK2}" stroke-width="2" stroke-linejoin="round"'
    if geste == "modifier":
        b.append(f'<path d="M{bx + 10} {by + 26} l1.5 -6 l9 -9 l4.5 4.5 l-9 9 z" {t}/>')
        b.append(f'<path d="M{bx + 20.5} {by + 11} l2.5 -2.5 l4.5 4.5 l-2.5 2.5" {t}/>')
    else:
        b.append(f'<path d="M{bx + 9} {by + 13} h18" {t}/>')
        b.append(f'<path d="M{bx + 12} {by + 13} l1 14 h10 l1 -14" {t}/>')
        b.append(f'<path d="M{bx + 14} {by + 13} v-3 h8 v3" {t}/>')
    return "\n      ".join(b)


def _pastille(x, y, libelle, actif=False, taille=12, h=32):
    """Pastille de selection. Renvoie (svg, largeur) pour chainer une rangee."""
    w = 24 + len(libelle) * (taille * 0.64)
    fond = JAUNE if actif else SURFACE
    bord = TILE_INK if actif else INK
    svg = (bloc(x, y, w, h, fond, r=h / 2, cerne=bord, epaisseur=2,
                ombre=3 if actif else 0, ombre_couleur=TILE_INK)
           + "\n      " + texte(x + w / 2, y + h / 2 + 4, libelle, taille, BODY,
                                TILE_INK if actif else INK, gras=700, ancre="middle"))
    return svg, w


def _rangee_pastilles(cx, y, libelles, actifs):
    b, x = [], cx + MARGE
    for lab in libelles:
        svg, w = _pastille(x, y, lab, lab in actifs)
        b.append(svg)
        x += w + 8
    return "\n      ".join(b)


def _jeton(x, y, libelle):
    """Jeton insere dans le texte de la regle, sur fond SURFACE donc cerne INK."""
    w = 22 + len(libelle) * 7.2
    svg = (bloc(x, y, w, 34, SURFACE, r=17, cerne=INK, epaisseur=2)
           + "\n      " + texte(x + w / 2, y + 22, libelle, T_MICRO + 1, BODY, INK,
                                gras=700, ancre="middle"))
    return svg, w


def _sceau(x, y, taille=20):
    """Sceau de cire : objet physique, donc couleur fixe dans les deux themes."""
    r = taille / 2
    return "\n      ".join([
        f'<circle cx="{x + r}" cy="{y + r}" r="{r}" fill="{CARD_RED}" stroke="{TILE_INK}" stroke-width="2"/>',
        f'<circle cx="{x + r}" cy="{y + r}" r="{r - 4}" fill="none" stroke="{TILE_INK}" stroke-width="1.4" opacity="0.55"/>',
        texte(x + r, y + r + 4, "M", taille * 0.5, BODY, TILE_INK, gras=700, ancre="middle"),
    ])


def _pointille(x, y, w, h, r=16):
    return "\n      ".join([
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{SURFACE}"/>',
        f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="none" stroke="{INK}" '
        f'stroke-width="3" stroke-dasharray="13 9" stroke-opacity="0.55"/>',
    ])


def _penalites(cx, y, valeur=2):
    """Reglage des penalites : libelle a gauche, incrementeur cale a droite."""
    return "\n      ".join([
        texte(cx + MARGE, y + 28, "Penalites en cas d'echec", T_LABEL, BODY, INK, gras=700),
        bloc(cx + 272, y, 44, 44, SURFACE, r=12, cerne=INK, epaisseur=3),
        texte(cx + 294, y + 30, "-", 22, DISPLAY, INK, ancre="middle"),
        texte(cx + 334, y + 30, str(valeur), 20, DISPLAY, INK, ancre="middle"),
        bloc(cx + 360, y, 44, 44, SURFACE, r=12, cerne=INK, epaisseur=3),
        texte(cx + 382, y + 30, "+", 22, DISPLAY, INK, ancre="middle"),
    ])


def _voile(cx, cy, opacite=0.7):
    return (f'<rect x="{cx}" y="{cy}" width="{L}" height="{H}" rx="38" '
            f'fill="{TILE_INK}" opacity="{opacite}"/>')


def _feuille(cx, cy, y):
    """Feuille basse : cernee en haut, elle vient poser un choix sur l'ecran."""
    h = H - (y - cy) - 26
    return "\n      ".join([
        bloc(cx + MARGE, y, LARG, h, SURFACE_HAUT, r=18, cerne=INK, epaisseur=3,
             ombre=6, ombre_couleur=INK),
    ])


# ------------------------------------------------------------------ reglages


def _corps_reglages(cx, cy, premium=False):
    """Corps commun de SettingsScreen. Le statut premium retire une seule ligne,
    tout le reste de la pile remonte du meme pas : la grille ne bouge pas."""
    d = 0 if not premium else -50
    b = [entete(cx, cy, "REGLAGES"),
         _titre_section(cx, cy + 148, "Apparence"),
         _rangee(cx, cy + 156, "Theme clair"),
         _etiquette(cx + L - MARGE - RETRAIT, cy + 165, "Changer"),
         _titre_section(cx, cy + 220, "Premium"),
         _carte(cx, cy + 228, 44),
         _sceau(cx + MARGE + RETRAIT, cy + 240),
         texte(cx + MARGE + RETRAIT + 30, cy + 255, "Statut", T_LABEL, BODY, INK, gras=700)]
    if premium:
        b.append(_etiquette(cx + L - MARGE - RETRAIT, cy + 237, "Premium actif",
                            PREMIUM, PREMIUM, SURFACE_HAUT))
        b.append(bouton(cx + MARGE, cy + 278, LARG, "RESTAURER MES ACHATS", False, 44, 16))
    else:
        b.append(_etiquette(cx + L - MARGE - RETRAIT, cy + 237, "Invite"))
        b.append(bouton(cx + MARGE, cy + 278, LARG, "DEBLOQUER LE PREMIUM", True, 44, 16))
        b.append(bouton(cx + MARGE, cy + 328, LARG, "RESTAURER MES ACHATS", False, 44, 16))
    b += [
        _titre_section(cx, cy + 392 + d, "Confidentialite"),
        _carte(cx, cy + 400 + d, 48),
        texte(cx + MARGE + RETRAIT, cy + 421 + d, "Mesure d'audience", T_LABEL, BODY, INK, gras=700),
        texte(cx + MARGE + RETRAIT, cy + 439 + d, "PostHog (instance EU), 13 mois maximum.",
              T_MICRO, BODY, INK3),
        _case(cx + L - MARGE - RETRAIT - 24, cy + 412 + d),
        _liste(cx, cy + 454 + d, ["Gerer les cookies", "Politique de confidentialite"]),
        _titre_section(cx, cy + 542 + d, "Contenu"),
        _rangee(cx, cy + 550 + d, "Mes regles", chevron=True),
        _titre_section(cx, cy + 614 + d, "Legal"),
        _liste(cx, cy + 622 + d, ["Mentions legales", "CGU / CGV", "Politique de confidentialite"]),
        _titre_section(cx, cy + 744 + d, "A propos"),
        _carte(cx, cy + 752 + d, 58, fond=SURFACE_HAUT),
        texte(cx + MARGE + RETRAIT, cy + 776 + d, "BACCHUS", 18, DISPLAY, INK),
        texte(cx + MARGE + RETRAIT, cy + 796 + d, "Version 0.41.0", T_MICRO, BODY, INK2),
        texte(cx + L - MARGE - RETRAIT, cy + 796 + d,
              "Editeur : Adam Beloucif, nom commercial BLF Lab's", T_MICRO - 1, BODY, INK3,
              ancre="end"),
        _titre_section(cx, cy + 830 + d, "Reinitialiser"),
        bloc(cx + MARGE, cy + 838 + d, LARG, 44, SURFACE, r=12, cerne=DANGER, epaisseur=3,
             ombre=3, ombre_couleur=DANGER),
        texte(cx + L / 2, cy + 866 + d, "REINITIALISER LA TABLEE", 16, DISPLAY, DANGER,
              ancre="middle"),
        texte(cx + MARGE, cy + 900 + d, "Efface les joueurs et la partie en cours sur cet appareil.",
              T_MICRO, BODY, INK3),
    ]
    if premium:
        b.append(texte(cx + MARGE, cy + 918 + d,
                       "Le statut premium et les achats ne sont jamais touches.",
                       T_MICRO, BODY, INK3))
    return b


def reglages_invite(s, cx, cy):
    ecran(s, "Reglages - compte invite", cx, cy, "\n      ".join(_corps_reglages(cx, cy, False)))


def reglages_premium(s, cx, cy):
    ecran(s, "Reglages - premium actif", cx, cy, "\n      ".join(_corps_reglages(cx, cy, True)))


def reglages_restauration(s, cx, cy):
    """Section Premium en cours de restauration, puis les trois reponses possibles
    du magasin. Le vert n'est pas un decor ici : il marque un etat de succes."""
    b = [entete(cx, cy, "REGLAGES"),
         _titre_section(cx, cy + 148, "Premium"),
         _carte(cx, cy + 156, 44),
         _sceau(cx + MARGE + RETRAIT, cy + 168),
         texte(cx + MARGE + RETRAIT + 30, cy + 183, "Statut", T_LABEL, BODY, INK, gras=700),
         _etiquette(cx + L - MARGE - RETRAIT, cy + 165, "Invite"),
         bouton(cx + MARGE, cy + 206, LARG, "DEBLOQUER LE PREMIUM", True, 44, 16),
         # Bouton occupe : opacite reduite, aucune ombre, il n'invite plus au clic.
         bloc(cx + MARGE, cy + 256, LARG, 44, SURFACE, r=12, cerne=INK, epaisseur=3, opacite=0.55),
         f'<circle cx="{cx + 150}" cy="{cy + 278}" r="9" fill="none" stroke="{INK3}" '
         f'stroke-width="3" stroke-dasharray="14 9"/>',
         texte(cx + 172, cy + 284, "RESTAURATION EN COURS", 15, DISPLAY, INK3),
         texte(cx + L / 2, cy + 326, "Premium restaure avec succes.", T_CORPS, BODY, SUCCES,
               gras=700, ancre="middle"),
         _titre_section(cx, cy + 366, "Reponses possibles du magasin")]
    reponses = [("Premium restaure avec succes.",
                 "Un achat a vie est retrouve sur cet appareil.", SUCCES),
                ("Aucun achat actif trouve pour cet appareil.",
                 "Rien a restaurer, le compte reste invite.", INK2),
                ("Bientot disponible.",
                 "Le magasin n'est pas encore branche sur cette version.", INK3)]
    for i, (titre, note, encre) in enumerate(reponses):
        y = cy + 376 + i * 78
        b.append(_carte(cx, y, 66))
        b.append(texte(cx + MARGE + RETRAIT, y + 28, titre, T_LABEL, BODY, encre, gras=700))
        b.append(texte(cx + MARGE + RETRAIT, y + 50, note, T_MICRO, BODY, INK3))
    b += [
        _titre_section(cx, cy + 630, "Ce que la restauration fait"),
        _carte(cx, cy + 638, 118, fond=SURFACE_HAUT),
        paragraphe(cx + MARGE + RETRAIT, cy + 666,
                   ["Elle interroge le magasin de l'appareil, rien d'autre.",
                    "Aucun compte n'est cree, aucune donnee n'est envoyee.",
                    "Les achats restent lies au compte du magasin.",
                    "Le statut premium reste local a cet appareil."], T_MICRO, INK2, 22),
        _titre_section(cx, cy + 786, "Une fois le premium actif"),
        _carte(cx, cy + 794, 62),
        texte(cx + MARGE + RETRAIT, cy + 820, "Le bouton Debloquer disparait.", T_LABEL, BODY,
              INK, gras=700),
        texte(cx + MARGE + RETRAIT, cy + 840, "Seul Restaurer mes achats subsiste.", T_MICRO,
              BODY, INK3),
        _etiquette(cx + L - MARGE - RETRAIT, cy + 812, "Premium actif", PREMIUM, PREMIUM,
                   SURFACE_HAUT),
        texte(cx + MARGE, cy + 890, "Le message de statut est annonce aux lecteurs d'ecran.",
              T_MICRO, BODY, INK3),
    ]
    ecran(s, "Reglages - restauration d'achat", cx, cy, "\n      ".join(b))


def reglages_confirmation(s, cx, cy):
    """ConfirmDialog pose sur les reglages : l'ecran reste lisible dessous."""
    b = _corps_reglages(cx, cy, False)
    b.append(_voile(cx, cy, 0.72))
    b.append(bloc(cx + 50, cy + 330, 330, 300, SURFACE_HAUT, r=18, cerne=INK, epaisseur=3,
                  ombre=7, ombre_couleur=INK))
    b.append(texte(cx + L / 2, cy + 388, "REINITIALISER", 24, DISPLAY, INK, ancre="middle"))
    b.append(texte(cx + L / 2, cy + 414, "LA TABLEE ?", 24, DISPLAY, INK, ancre="middle"))
    b.append(paragraphe(cx + L / 2, cy + 448,
                        ["Les joueurs et la partie en cours seront",
                         "effaces sur cet appareil. Cette action",
                         "est irreversible."], T_LABEL, INK2, 21, "middle"))
    b.append(bouton(cx + 76, cy + 512, 278, "REINITIALISER", True, 50, 17))
    b.append(texte(cx + L / 2, cy + 600, "Annuler", T_CORPS, BODY, INK2, ancre="middle"))
    ecran(s, "Reglages - confirmer la reinitialisation", cx, cy, "\n      ".join(b))


# ---------------------------------------------------------------- mes regles


_INTRO_REGLES = ["Cree tes propres regles : elles se glissent dans les jeux de",
                 "cartes ou s'ajoutent a la roulette, et restent enregistrees",
                 "sur ton telephone."]


def regles_vide(s, cx, cy):
    b = [entete(cx, cy, "MES REGLES"),
         paragraphe(cx + MARGE, cy + 156, _INTRO_REGLES, T_LABEL, INK2, 21),
         _pointille(cx + MARGE, cy + 240, LARG, 208),
         icone("disc3", cx + L / 2 - 22, cy + 278, 44),
         texte(cx + L / 2, cy + 358, "AUCUNE REGLE POUR L'INSTANT", 20, DISPLAY, INK,
               ancre="middle"),
         texte(cx + L / 2, cy + 388, "Ta premiere regle est a un tap d'ici.", T_CORPS, BODY,
               INK2, ancre="middle"),
         bouton(cx + MARGE, cy + 474, LARG, "+  NOUVELLE REGLE", True, 54, 18),
         _titre_section(cx, cy + 566, "Ce qu'une regle peut devenir")]
    exemples = [("Carte de jeu", "Elle se melange aux paquets des jeux de cartes,",
                 "et sort a son tour comme n'importe quelle carte."),
                ("Roulette", "Elle devient un segment de la roue du destin,",
                 "aux cotes des segments livres avec le jeu."),
                ("Sur l'appareil", "Rien ne part en ligne : tes regles restent",
                 "enregistrees sur ce telephone, et nulle part ailleurs.")]
    for i, (titre, l1, l2) in enumerate(exemples):
        y = cy + 576 + i * 96
        b.append(_carte(cx, y, 84))
        b.append(texte(cx + MARGE + RETRAIT, y + 28, titre.upper(), 15, DISPLAY, INK))
        b.append(paragraphe(cx + MARGE + RETRAIT, y + 52, [l1, l2], T_MICRO, INK2, 18))
    b.append(texte(cx + MARGE, cy + 890, "Une regle se desactive sans etre supprimee.",
                   T_MICRO, BODY, INK3))
    ecran(s, "Mes regles - aucune regle", cx, cy, "\n      ".join(b))


_REGLES = [
    (True, ["{player} imite un animal choisi", "par {player2}, sinon 2 penalites."],
     "Tous les jeux de cartes - 2 penalites"),
    (True, ["Le dernier a lever son verre", "distribue une penalite a qui il veut."],
     "Roulette - 1 penalite"),
    (True, ["{player} parle avec l'accent de", "son choix jusqu'a son prochain tour."],
     "Le Taulier, Action ou Verite - 1 penalite"),
    (False, ["Interdit de prononcer le mot", "boire pendant trois tours."],
     "Tous les jeux de cartes - 3 penalites"),
]


def regles_liste(s, cx, cy):
    """Liste de CustomRulesScreen : meme pas vertical, regle desactivee attenuee.

    L'attenuation porte sur un groupe qui englobe la carte ET son contenu. Poser
    une opacite sur le seul rectangle laisserait l'ombre portee, opaque, remonter
    au travers : la carte virait au gris sale au lieu de s'effacer.
    """
    b = [entete(cx, cy, "MES REGLES"),
         paragraphe(cx + MARGE, cy + 156, _INTRO_REGLES, T_LABEL, INK2, 21)]
    for i, (active, lignes, portee) in enumerate(_REGLES):
        y = cy + 240 + i * 122
        b.append(f'<g opacity="{1 if active else 0.45}">')
        b.append(bloc(cx + MARGE, y, LARG, 110, SURFACE, r=14, cerne=INK, epaisseur=3,
                      ombre=4, ombre_couleur=INK))
        b.append(_case(cx + MARGE + 16, y + 22, active))
        b.append(paragraphe(cx + MARGE + 56, y + 36, lignes, T_CORPS, INK, 22))
        b.append(texte(cx + MARGE + 56, y + 88, portee, T_MICRO, BODY, INK3))
        for j, geste in enumerate(["modifier", "supprimer"]):
            b.append(_action(cx + L - MARGE - 52, y + 16 + j * 42, geste))
        b.append('</g>')
    b += [
        bouton(cx + MARGE, cy + 754, LARG, "+  NOUVELLE REGLE", True, 54, 18),
        texte(cx + MARGE, cy + 838, "La case decoche la regle sans la supprimer : elle reste",
              T_MICRO, BODY, INK3),
        texte(cx + MARGE, cy + 856, "dans la liste, simplement mise de cote.", T_MICRO, BODY, INK3),
        texte(cx + MARGE, cy + 890, "4 regles enregistrees sur cet appareil.", T_MICRO, BODY, INK3),
    ]
    ecran(s, "Mes regles - liste", cx, cy, "\n      ".join(b))


def _entete_editeur(cx, cy, titre, kind):
    """Feuille editeur : titre puis choix du type, en grille a deux colonnes."""
    b = [_voile(cx, cy, 0.6),
         f'<rect x="{cx}" y="{cy + 120}" width="{L}" height="{H - 120 - 20}" rx="20" fill="{BG}"/>',
         f'<line x1="{cx}" y1="{cy + 120}" x2="{cx + L}" y2="{cy + 120}" stroke="{INK}" stroke-width="4"/>',
         f'<rect x="{cx + L / 2 - 32}" y="{cy + 134}" width="64" height="5" rx="2.5" fill="{INK}" opacity="0.4"/>',
         texte(cx + MARGE, cy + 180, titre.upper(), 22, DISPLAY, INK)]
    for x, lab in ((COL_G, "Carte de jeu"), (COL_D, "Roulette")):
        actif = lab == kind
        b.append(bloc(cx + x, cy + 200, COL_W, 48, JAUNE if actif else SURFACE, r=12,
                      cerne=TILE_INK if actif else INK, epaisseur=3,
                      ombre=4 if actif else 0, ombre_couleur=TILE_INK))
        b.append(texte(cx + x + COL_W / 2, cy + 231, lab, 16, DISPLAY,
                       TILE_INK if actif else INK, ancre="middle"))
    return b


def editeur_carte(s, cx, cy):
    b = _entete_editeur(cx, cy, "Nouvelle regle", "Carte de jeu")
    b += [
        texte(cx + MARGE, cy + 282, "Texte de la regle", T_LABEL, BODY, INK, gras=700),
        bloc(cx + MARGE, cy + 292, LARG, 92, SURFACE, r=12, cerne=INK, epaisseur=3),
        paragraphe(cx + MARGE + 18, cy + 322,
                   ["{player} imite un animal choisi par {player2},",
                    "sinon 2 penalites."], T_CORPS, INK, 24),
    ]
    x = cx + MARGE
    for jeton in ("{player}", "{player2}"):
        svg, w = _jeton(x, cy + 396, jeton)
        b.append(svg)
        x += w + 10
    b += [
        texte(cx + L - MARGE, cy + 418, "66/280", T_MICRO, BODY, INK3, ancre="end"),
        bloc(cx + MARGE, cy + 444, LARG, 56, SURFACE, r=12, cerne=INK, epaisseur=2),
        texte(cx + MARGE + 18, cy + 470, "Apercu", T_MICRO, DISPLAY, INK3, espacement=0.8),
        texte(cx + MARGE + 18, cy + 490, "Alex imite un animal choisi par Sam, sinon 2 penalites.",
              T_MICRO, BODY, INK2),
        texte(cx + MARGE, cy + 534, "Jeux concernes", T_LABEL, BODY, INK, gras=700),
        texte(cx + MARGE + 124, cy + 534, "(aucun = tous)", T_LABEL, BODY, INK3),
        _rangee_pastilles(cx, cy + 548, ["Le Taulier", "Action ou Verite", "7 Secondes"],
                          {"Le Taulier", "Action ou Verite"}),
        _rangee_pastilles(cx, cy + 588, ["Je n'ai jamais", "Qui de nous", "Tu preferes"], set()),
        _rangee_pastilles(cx, cy + 628, ["C'est un 10 mais"], set()),
        _penalites(cx, cy + 676, 2),
        bouton(cx + MARGE, cy + 744, LARG, "AJOUTER LA REGLE", True, 54, 18),
        texte(cx + L / 2, cy + 834, "Annuler", T_CORPS, BODY, INK2, ancre="middle"),
        texte(cx + L / 2, cy + 878, "Enregistree sur cet appareil, jamais en ligne.",
              T_MICRO, BODY, INK3, ancre="middle"),
    ]
    ecran(s, "Mes regles - editeur carte de jeu", cx, cy, "\n      ".join(b))


def editeur_roulette(s, cx, cy):
    """Type Roulette : le bloc des jeux concernes disparait, le reste ne bouge pas."""
    b = _entete_editeur(cx, cy, "Modifier la regle", "Roulette")
    b += [
        texte(cx + MARGE, cy + 282, "Texte de la regle", T_LABEL, BODY, INK, gras=700),
        bloc(cx + MARGE, cy + 292, LARG, 92, SURFACE, r=12, cerne=INK, epaisseur=3),
        paragraphe(cx + MARGE + 18, cy + 322,
                   ["Le dernier a lever son verre distribue",
                    "une penalite a {player}, puis rejoue."], T_CORPS, INK, 24),
    ]
    x = cx + MARGE
    for jeton in ("{player}", "{player2}"):
        svg, w = _jeton(x, cy + 396, jeton)
        b.append(svg)
        x += w + 10
    b += [
        texte(cx + L - MARGE, cy + 418, "72/280", T_MICRO, BODY, INK3, ancre="end"),
        bloc(cx + MARGE, cy + 444, LARG, 74, SURFACE, r=12, cerne=INK, epaisseur=2),
        texte(cx + MARGE + 18, cy + 470, "Apercu", T_MICRO, DISPLAY, INK3, espacement=0.8),
        texte(cx + MARGE + 18, cy + 490, "Le dernier a lever son verre distribue une penalite",
              T_MICRO, BODY, INK2),
        texte(cx + MARGE + 18, cy + 508, "a Alex, puis rejoue.", T_MICRO, BODY, INK2),
        _carte(cx, cy + 546, 98, fond=SURFACE_HAUT),
        texte(cx + MARGE + RETRAIT, cy + 578, "CE QUE DEVIENT CETTE REGLE", 15, DISPLAY, INK),
        paragraphe(cx + MARGE + RETRAIT, cy + 602,
                   ["Elle s'ajoute a la roue du destin comme un segment.",
                    "Les jeux de cartes ne sont pas concernes, il n'y a",
                    "donc rien a cibler ici."], T_MICRO, INK2, 18),
        _penalites(cx, cy + 676, 1),
        bouton(cx + MARGE, cy + 744, LARG, "ENREGISTRER", True, 54, 18),
        texte(cx + L / 2, cy + 834, "Annuler", T_CORPS, BODY, INK2, ancre="middle"),
        texte(cx + L / 2, cy + 878, "La modification remplace la regle existante.",
              T_MICRO, BODY, INK3, ancre="middle"),
    ]
    ecran(s, "Mes regles - editeur roulette", cx, cy, "\n      ".join(b))


# ------------------------------------------------------------------- cookies


def _fond_cookies(cx, cy):
    """Ce que la feuille recouvre : l'accueil, encore lisible sous le voile."""
    return [texte(cx + L / 2, cy + 262, "BACCHUS", 54, DISPLAY, INK, ancre="middle"),
            texte(cx + L / 2, cy + 298, "La taverne ouvre ses portes", T_CORPS, BODY, INK2,
                  ancre="middle"),
            bouton(cx + MARGE, cy + 340, LARG, "ENTRER DANS LA TAVERNE", True, 56, 18),
            _voile(cx, cy, 0.45)]


def _entete_cookies(cx, y, lignes):
    """Pastille, titre, texte : le texte demarre sur le meme retrait que le titre."""
    return [bloc(cx + INT_G, y, 44, 44, SURFACE, r=12, cerne=INK, epaisseur=2),
            icone("disc3", cx + INT_G + 8, y + 8, 28),
            texte(cx + INT_G + 58, y + 22, "COOKIES", 20, DISPLAY, INK),
            paragraphe(cx + INT_G + 58, y + 48, lignes, T_LABEL, INK2, 21)]


def cookies_niveau_1(s, cx, cy):
    """Niveau 1. Refus et acceptation ont le meme poids visuel : meme largeur,
    meme fond, meme cerne. Aucun bouton primaire ici, c'est la regle CNIL."""
    y = cy + 552
    b = _fond_cookies(cx, cy)
    b.append(_feuille(cx, cy, y))
    b += _entete_cookies(cx, y + 26, [
        "Bacchus utilise des traceurs pour mesurer",
        "l'audience et ameliorer l'experience de jeu.",
        "Vous pouvez accepter, refuser, ou personnaliser",
        "vos choix. En savoir plus :"])
    b += [
        texte(cx + INT_G + 58, y + 158, "politique de confidentialite", T_LABEL, BODY, ORANGE_INK,
              gras=700),
        f'<line x1="{cx + INT_G + 58}" y1="{y + 163}" x2="{cx + INT_G + 240}" y2="{y + 163}" '
        f'stroke="{ORANGE_INK}" stroke-width="1.6"/>',
        bloc(cx + INT_G, y + 186, INT_W, 52, SURFACE, r=12, cerne=INK, epaisseur=3, ombre=5,
             ombre_couleur=INK),
        # Meme taille, meme fond, meme cerne que l'acceptation : exigence CNIL.
        texte(cx + INT_G + INT_W / 2, y + 219, "TOUT REFUSER", 13, DISPLAY, INK, ancre="middle"),
        bloc(cx + INT_D, y + 186, INT_W, 52, SURFACE, r=12, cerne=INK, epaisseur=3, ombre=5,
             ombre_couleur=INK),
        texte(cx + INT_D + INT_W / 2, y + 219, "ACCEPTER L'ANALYSE", 13, DISPLAY, INK,
              ancre="middle"),
        texte(cx + L / 2, y + 278, "Personnaliser", T_CORPS, BODY, INK2, ancre="middle"),
        f'<line x1="{cx + L / 2 - 44}" y1="{y + 283}" x2="{cx + L / 2 + 44}" y2="{y + 283}" '
        f'stroke="{INK2}" stroke-width="1.4"/>',
        texte(cx + L / 2, y + 316, "Aucun traceur ne se declenche avant ce choix.", T_MICRO,
              BODY, INK3, ancre="middle"),
    ]
    ecran(s, "Cookies - niveau 1", cx, cy, "\n      ".join(b))


def cookies_niveau_2(s, cx, cy):
    """Niveau 2. Necessaire est indiquee active sans interrupteur : elle ne se
    refuse pas, donc on ne feint pas de proposer un choix."""
    y = cy + 424
    b = _fond_cookies(cx, cy)
    b.append(_feuille(cx, cy, y))
    b += _entete_cookies(cx, y + 26, [
        "Choisissez les traceurs actifs sur Bacchus.",
        "Le refus est aussi simple que l'acceptation."])
    lignes = [("Necessaire", "Session d'authentification Supabase.", "Toujours actif.", None),
              ("Mesure d'audience", "PostHog (instance EU), 13 mois maximum.",
               "Depose seulement apres accord.", True)]
    for i, (titre, l1, l2, coche) in enumerate(lignes):
        ly = y + 136 + i * 92
        b.append(bloc(cx + INT_G, ly, INT_LARG, 80, SURFACE, r=12, cerne=INK, epaisseur=2))
        b.append(texte(cx + INT_G + 22, ly + 28, titre, T_LABEL, BODY, INK, gras=700))
        b.append(texte(cx + INT_G + 22, ly + 48, l1, T_MICRO, BODY, INK3))
        b.append(texte(cx + INT_G + 22, ly + 66, l2, T_MICRO, BODY, INK3))
        if coche:
            b.append(_case(cx + INT_G + INT_LARG - 46, ly + 28, True))
        else:
            b.append(_etiquette(cx + INT_G + INT_LARG - 22, ly + 30, "Actif"))
    b += [
        bouton(cx + INT_G, y + 328, INT_LARG, "ENREGISTRER MES CHOIX", True, 52, 17),
        bloc(cx + INT_G, y + 392, INT_LARG, 52, SURFACE, r=12, cerne=INK, epaisseur=3,
             ombre=5, ombre_couleur=INK),
        texte(cx + L / 2, y + 425, "TOUT ACCEPTER", 16, DISPLAY, INK, ancre="middle"),
        texte(cx + L / 2, y + 470, "Ce choix se modifie a tout moment depuis les reglages.",
              T_MICRO, BODY, INK3, ancre="middle"),
    ]
    ecran(s, "Cookies - niveau 2", cx, cy, "\n      ".join(b))


ECRANS = [reglages_invite, reglages_premium, reglages_restauration, reglages_confirmation,
          regles_vide, regles_liste, editeur_carte, editeur_roulette,
          cookies_niveau_1, cookies_niveau_2]
