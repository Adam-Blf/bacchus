# -*- coding: utf-8 -*-
"""Lot 4 : les sept etats de PremiumPaywallModal, l'unique surface d'achat.

CE QUI EST LU DANS LE CODE, jamais invente :
  - src/components/premium/PremiumPaywallModal.tsx pour l'ordre des blocs, les
    libelles de boutons, les deux consentements de l'article 14 des CGU/CGV, le
    message d'attente, celui d'erreur et celui de succes ;
  - src/content/premium-catalog.json pour les cinq packs et leur volume.

PALETTE. Fond creme et encre noire portent l'ecran. NEON (et son encre profonde
ORANGE_INK pour le titre) est le seul accent d'action. PREMIUM est admis ici, et
seulement ici, parce que c'est la surface d'achat : cerne de la carte, sceau,
pastille de l'offre, puces du catalogue. DANGER et SUCCES n'apparaissent que
comme ETAT, une seule fois, sur les ecrans concernes, et le sceau devient alors
vert pour ne pas cumuler deux familles saturees. Le halo DEPTH reprend celui du
composant (bg-depth/[0.14]) : ambiance a peine perceptible sur un voile sombre,
pas un aplat. Aucun rose, bleu ni lime.

ALIGNEMENT. Marge laterale de 26 : la carte fait L - 52 et commence a cx + 26.
Retrait interne constant de 24, donc une colonne de texte de 330 de large. Tous
les blocs empiles partagent leur pas. Les hauteurs de carte changent d'un etat a
l'autre parce que le formulaire disparait vraiment quand l'achat aboutit : la
carte reste centree verticalement, comme la modale du composant.
"""
from maquette_core import (BG_HAUT, BODY, CARD_FACE, DANGER, DEPTH, DISPLAY, H, INK,
                           INK2, INK3, L, NEON, ORANGE_INK, PREMIUM, SUCCES, SURFACE,
                           SURFACE_HAUT, TILE_INK, T_CORPS, T_LABEL, T_MICRO,
                           bloc, bouton, ecran, paragraphe, puce, texte)

MARGE = 26
RETRAIT = 24
GAUCHE = MARGE + RETRAIT          # 50 : bord gauche du texte dans la carte
DROITE = L - MARGE - RETRAIT      # 380 : bord droit, aligne sur la meme grille
COLONNE = DROITE - GAUCHE         # 330

# Ordonnancement vertical interne, mesure depuis le HAUT de la carte.
Y_SCEAU, T_SCEAU = 24, 52
Y_TITRE = 122
Y_SOUS = 150
Y_LABEL = 198
Y_CATALOGUE, PAS_CATALOGUE = 220, 34
Y_ZONE = 392                       # premier bloc variable, sous le catalogue

CATALOGUE = [("Action ou Verite - Extreme", "80 cartes"),
             ("C'est un 10 mais - Red Flags", "80 cartes"),
             ("Je n'ai jamais - Hot", "80 cartes"),
             ("Le Taulier - Chaos", "80 cartes"),
             ("Qui de nous - Sale", "80 cartes")]

CONSENTEMENTS = [["Je demande l'execution immediate du contenu",
                  "numerique des la confirmation du paiement,",
                  "avant la fin du delai de retractation de 14 jours."],
                 ["Je reconnais qu'en acceptant cette execution",
                  "immediate, je perds mon droit de retractation",
                  "de 14 jours."]]


def _croix(x, y, t, couleur, opacite=1):
    """Le X de fermeture : deux traits francs, jamais un glyphe de police."""
    return (f'<path d="M {x} {y} L {x + t} {y + t} M {x + t} {y} L {x} {y + t}" '
            f'fill="none" stroke="{couleur}" stroke-width="2.6" stroke-linecap="round" '
            f'opacity="{opacite}"/>')


def _coche(x, y, t, couleur):
    return (f'<path d="M {x} {y + t * 0.52} L {x + t * 0.38} {y + t * 0.84} L {x + t} {y + t * 0.12}" '
            f'fill="none" stroke="{couleur}" stroke-width="3" stroke-linecap="round" '
            f'stroke-linejoin="round"/>')


def _roue(x, y, r, couleur):
    """Roue d'attente : anneau plein plus un arc, sans flou ni degrade."""
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="none" stroke="{couleur}" '
            f'stroke-width="3" opacity="0.3"/>\n      '
            f'<path d="M {x} {y - r} A {r} {r} 0 0 1 {x + r} {y}" fill="none" '
            f'stroke="{couleur}" stroke-width="3" stroke-linecap="round"/>')


def _sceau(x, y, couleur, ouvert=False):
    """Sceau rond avec cadenas. Ouvert une fois l'achat abouti, ferme sinon."""
    t = T_SCEAU
    out = [bloc(x, y, t, t, SURFACE, r=t / 2, cerne=couleur, epaisseur=3),
           bloc(x + 16, y + 25, 20, 15, couleur, r=3, epaisseur=0)]
    if ouvert:
        anse = f'M {x + 21} {y + 25} L {x + 21} {y + 17} A 5 5 0 0 1 {x + 31} {y + 17}'
    else:
        anse = (f'M {x + 21} {y + 25} L {x + 21} {y + 20} A 5 5 0 0 1 {x + 31} {y + 20} '
                f'L {x + 31} {y + 25}')
    out.append(f'<path d="{anse}" fill="none" stroke="{couleur}" stroke-width="3" '
               f'stroke-linecap="round"/>')
    return "\n      ".join(out)


def _bouton_inactif(x, y, w, libelle, h=56, taille=17):
    """Action indisponible : pas d'ombre portee, donc pas de relief, donc pas cliquable."""
    return (bloc(x, y, w, h, SURFACE, r=12, cerne=INK, epaisseur=3, opacite=0.45)
            + "\n      " + texte(x + w / 2, y + h / 2 + 6, libelle, taille, DISPLAY, INK3,
                                 ancre="middle"))


def _bouton_attente(x, y, w, libelle, h=56, taille=17):
    return "\n      ".join([
        bloc(x, y, w, h, NEON, r=12, cerne=TILE_INK, epaisseur=3, ombre=5, ombre_couleur=TILE_INK),
        _roue(x + w / 2 - 74, y + h / 2, 11, TILE_INK),
        texte(x + w / 2 + 16, y + h / 2 + 6, libelle, taille, DISPLAY, TILE_INK, ancre="middle"),
    ])


def _case(x, y, cochee, t=22):
    if cochee:
        return (bloc(x, y, t, t, INK, r=5, cerne=INK, epaisseur=3)
                + "\n      " + _coche(x + 5, y + 4, t - 10, BG_HAUT))
    return bloc(x, y, t, t, SURFACE, r=5, cerne=INK, epaisseur=3)


def _consentement(cx, y, index, cochee):
    """Une case et son texte, alignes sur le meme retrait que le reste de la carte."""
    return "\n      ".join([
        bloc(cx + GAUCHE, y, COLONNE, 54, BG_HAUT, r=10, cerne=INK, epaisseur=2),
        _case(cx + GAUCHE + 14, y + 16, cochee),
        paragraphe(cx + GAUCHE + 46, y + 20, CONSENTEMENTS[index], T_MICRO, INK2, 14),
    ])


def _tarif(cx, y, prix, badge=True):
    """Bloc d'offre reelle : formule, pastille Seule offre, prix, note."""
    out = [bloc(cx + GAUCHE, y, COLONNE, 76, BG_HAUT, r=12, cerne=PREMIUM, epaisseur=3,
                ombre=4, ombre_couleur=INK),
           texte(cx + GAUCHE + 20, y + 34, "A vie", 20, DISPLAY, INK),
           texte(cx + DROITE - 20, y + 34, prix, 20, DISPLAY, INK, ancre="end"),
           texte(cx + GAUCHE + 20, y + 58, "Paiement unique, acces perpetuel", T_MICRO, BODY, INK2)]
    if badge:
        out.insert(2, puce(cx + GAUCHE + 84, y + 16, "SEULE OFFRE", PREMIUM, CARD_FACE, T_MICRO - 1, 24))
    return "\n      ".join(out)


def _tarif_absent(cx, y, libelle):
    """Repli du composant quand aucune offre n'est joignable, ou pendant la requete."""
    return "\n      ".join([
        bloc(cx + GAUCHE, y, COLONNE, 66, BG_HAUT, r=12, cerne=INK, epaisseur=2),
        texte(cx + GAUCHE + COLONNE / 2, y + 43, libelle, 24, DISPLAY, INK, ancre="middle"),
    ])


def _socle(cx, cy, hauteur, sceau=PREMIUM, ouvert=False, ferme_actif=True):
    """Voile, halo, carte, sceau et en-tete : le tronc commun des sept etats.

    Renvoie (y_haut_de_carte, liste de fragments) pour que chaque etat n'ait plus
    qu'a poser sa zone variable et ses actions.
    """
    y = cy + int((H - hauteur) / 2)
    b = [f'<rect x="{cx}" y="{cy}" width="{L}" height="{H}" rx="38" fill="{TILE_INK}" opacity="0.78"/>',
         f'<circle cx="{cx + L / 2}" cy="{cy + H / 2}" r="190" fill="{DEPTH}" opacity="0.14"/>',
         bloc(cx + MARGE, y, L - 2 * MARGE, hauteur, SURFACE_HAUT, r=20, cerne=PREMIUM,
              epaisseur=3, ombre=8, ombre_couleur=INK),
         _sceau(cx + GAUCHE, y + Y_SCEAU, sceau, ouvert),
         bloc(cx + DROITE - 40, y + Y_SCEAU + 6, 40, 40, SURFACE, r=20, cerne=INK,
              epaisseur=2, opacite=None if ferme_actif else 0.45),
         _croix(cx + DROITE - 26, y + Y_SCEAU + 20, 12, INK, 1 if ferme_actif else 0.4),
         texte(cx + GAUCHE, y + Y_TITRE, "BACCHUS PREMIUM", 30, DISPLAY, ORANGE_INK),
         paragraphe(cx + GAUCHE, y + Y_SOUS, ["Debloque tous les packs premium de la",
                                              "collection, directement dans l'app."], T_LABEL, INK2, 19),
         texte(cx + GAUCHE, y + Y_LABEL, "CE QUE TU DEBLOQUES", T_MICRO, DISPLAY, INK3, espacement=1.6)]
    for i, (titre, volume) in enumerate(CATALOGUE):
        yy = y + Y_CATALOGUE + i * PAS_CATALOGUE
        marque = SUCCES if ouvert else PREMIUM
        if ouvert:
            b.append(_coche(cx + GAUCHE, yy - 12, 12, marque))
        else:
            b.append(bloc(cx + GAUCHE + 1, yy - 10, 10, 10, marque, r=2, epaisseur=0))
        b.append(texte(cx + GAUCHE + 24, yy, titre, T_LABEL, BODY, INK, gras=700))
        b.append(texte(cx + DROITE, yy, volume, T_MICRO, BODY, INK3, ancre="end"))
        if i < len(CATALOGUE) - 1:
            b.append(f'<line x1="{cx + GAUCHE}" y1="{yy + 11}" x2="{cx + DROITE}" y2="{yy + 11}" '
                     f'stroke="{INK}" stroke-width="1" opacity="0.12"/>')
    return y, b


def _pied(cx, y, hauteur, action, message=None, couleur_message=INK3, plus_tard=True):
    """Message d'etat, action principale, puis le lien Plus tard, toujours au meme pas."""
    b = []
    if message:
        b.append(texte(cx + L / 2, y + hauteur - 118, message, T_MICRO, BODY, couleur_message,
                       ancre="middle"))
    b.append(action(cx + GAUCHE, y + hauteur - 100, COLONNE))
    if plus_tard:
        b.append(texte(cx + L / 2, y + hauteur - 30, "Plus tard", T_CORPS, BODY, INK2, ancre="middle"))
    return b


HAUTEUR_PLEINE = 800     # offre affichee : tarif, mention, deux consentements
HAUTEUR_COURTE = 680     # pas d'offre a afficher, donc pas de formulaire
HAUTEUR_SUCCES = 620     # formulaire retire une fois l'achat abouti

MENTION = ["Acces premium a vie : paiement unique,", "14,99 EUR, aucun renouvellement."]


def premium_chargement(s, cx, cy):
    y, b = _socle(cx, cy, HAUTEUR_COURTE)
    b += [_tarif_absent(cx, y + Y_ZONE, "...")]
    b += _pied(cx, y, HAUTEUR_COURTE,
               lambda x, yy, w: _bouton_inactif(x, yy, w, "BIENTOT DISPONIBLE"))
    ecran(s, "Premium - chargement de l'offre", cx, cy, "\n      ".join(b))


def premium_sans_consentement(s, cx, cy):
    y, b = _socle(cx, cy, HAUTEUR_PLEINE)
    b += [_tarif(cx, y + Y_ZONE + 8, "14,99 EUR"),
          paragraphe(cx + L / 2, y + Y_ZONE + 108, MENTION, T_MICRO, INK2, 15, "middle"),
          _consentement(cx, y + Y_ZONE + 144, 0, False),
          _consentement(cx, y + Y_ZONE + 206, 1, False)]
    b += _pied(cx, y, HAUTEUR_PLEINE,
               lambda x, yy, w: _bouton_inactif(x, yy, w, "DEBLOQUER BACCHUS PREMIUM", taille=16),
               "Coche les deux cases ci-dessus pour activer le paiement.")
    ecran(s, "Premium - offre sans consentement", cx, cy, "\n      ".join(b))


def premium_consentement_donne(s, cx, cy):
    y, b = _socle(cx, cy, HAUTEUR_PLEINE)
    b += [_tarif(cx, y + Y_ZONE + 8, "14,99 EUR"),
          paragraphe(cx + L / 2, y + Y_ZONE + 108, MENTION, T_MICRO, INK2, 15, "middle"),
          _consentement(cx, y + Y_ZONE + 144, 0, True),
          _consentement(cx, y + Y_ZONE + 206, 1, True)]
    b += _pied(cx, y, HAUTEUR_PLEINE,
               lambda x, yy, w: bouton(x, yy, w, "DEBLOQUER BACCHUS PREMIUM", True, 56, 16))
    ecran(s, "Premium - consentement donne", cx, cy, "\n      ".join(b))


def premium_achat_en_cours(s, cx, cy):
    y, b = _socle(cx, cy, HAUTEUR_PLEINE, ferme_actif=False)
    b += [_tarif(cx, y + Y_ZONE + 8, "14,99 EUR"),
          paragraphe(cx + L / 2, y + Y_ZONE + 108, MENTION, T_MICRO, INK2, 15, "middle"),
          _consentement(cx, y + Y_ZONE + 144, 0, True),
          _consentement(cx, y + Y_ZONE + 206, 1, True),
          # Voile franc sur le formulaire : pendant l'appel, plus rien ne se modifie.
          bloc(cx + GAUCHE, y + Y_ZONE + 8, COLONNE, 252, SURFACE_HAUT, r=12, opacite=0.55,
               epaisseur=0)]
    b.append(_bouton_attente(cx + GAUCHE, y + HAUTEUR_PLEINE - 100, COLONNE, "ACHAT EN COURS", taille=16))
    b.append(texte(cx + L / 2, y + HAUTEUR_PLEINE - 30, "Plus tard", T_CORPS, BODY, INK3,
                   ancre="middle", opacite=0.45))
    ecran(s, "Premium - achat en cours", cx, cy, "\n      ".join(b))


def premium_achat_reussi(s, cx, cy):
    y, b = _socle(cx, cy, HAUTEUR_SUCCES, sceau=SUCCES, ouvert=True)
    b += [bloc(cx + GAUCHE, y + Y_ZONE, COLONNE, 86, BG_HAUT, r=12, cerne=SUCCES, epaisseur=3,
               ombre=4, ombre_couleur=INK),
          texte(cx + GAUCHE + COLONNE / 2, y + Y_ZONE + 38, "PREMIUM DEBLOQUE", 20, DISPLAY,
                SUCCES, ancre="middle"),
          texte(cx + GAUCHE + COLONNE / 2, y + Y_ZONE + 64, "Premium debloque, bonne soiree !",
                T_LABEL, BODY, INK2, ancre="middle")]
    b.append(bouton(cx + GAUCHE, y + HAUTEUR_SUCCES - 84, COLONNE, "FERMER", True, 56, 18))
    ecran(s, "Premium - achat reussi", cx, cy, "\n      ".join(b))


def premium_achat_echec(s, cx, cy):
    y, b = _socle(cx, cy, HAUTEUR_PLEINE)
    b += [_tarif(cx, y + Y_ZONE + 8, "14,99 EUR"),
          paragraphe(cx + L / 2, y + Y_ZONE + 108, MENTION, T_MICRO, INK2, 15, "middle"),
          _consentement(cx, y + Y_ZONE + 144, 0, True),
          _consentement(cx, y + Y_ZONE + 206, 1, True)]
    b += _pied(cx, y, HAUTEUR_PLEINE,
               lambda x, yy, w: bouton(x, yy, w, "DEBLOQUER BACCHUS PREMIUM", True, 56, 16),
               "L'achat n'a pas abouti. Reessaie dans un instant.", DANGER)
    ecran(s, "Premium - achat en echec", cx, cy, "\n      ".join(b))


def premium_indisponible(s, cx, cy):
    y, b = _socle(cx, cy, HAUTEUR_COURTE)
    b += [_tarif_absent(cx, y + Y_ZONE, "Bientot disponible")]
    b += _pied(cx, y, HAUTEUR_COURTE,
               lambda x, yy, w: _bouton_inactif(x, yy, w, "BIENTOT DISPONIBLE"))
    ecran(s, "Premium - indisponible", cx, cy, "\n      ".join(b))


ECRANS = [premium_chargement, premium_sans_consentement, premium_consentement_donne,
          premium_achat_en_cours, premium_achat_reussi, premium_achat_echec,
          premium_indisponible]
