# -*- coding: utf-8 -*-
"""Lot 6 : etats systeme et surfaces legales.

Sept surfaces qui n'appartiennent a aucun mode de jeu et qu'une maquette oublie
toujours : les deux visages de l'ErrorBoundary, le fallback de Suspense, la
pastille de sortie, et les trois pages legales servies par LegalLayout.

PARTI PRIS DE COPIE. Toutes les chaines sont relevees dans les composants :
ErrorBoundary.tsx, App.tsx (Loader et ExitToast), MentionsLegalesScreen.tsx,
ConfidentialiteScreen.tsx, CguScreen.tsx. Les pages legales comptent douze a
vingt sections : on developpe les premieres, on rend les autres en sommaire
compact, plutot que d'afficher trois sections dans un cadre a moitie vide.
Les accents sont retires comme dans les autres lots de la planche.

PALETTE. Dominante creme et encre. NEON pour la seule action primaire de la
planche, le bouton de relance. JAUNE pour deux mises en avant seulement,
l'encart de revue RGPD et l'article 14. DANGER et SUCCES ne servent pas ici :
un plantage se dit par la copie, pas par un aplat rouge decoratif.
"""
from maquette_core import (BG_HAUT, BODY, DISPLAY, H, INK, INK2, INK3, JAUNE, L,
                           NEON, ORANGE_INK, SURFACE, SURFACE_HAUT, TILE_INK,
                           T_CORPS, T_LABEL, T_MICRO,
                           bloc, bouton, ecran, entete, icone, paragraphe, puce, texte)

# Grille commune : une seule marge laterale, une seule largeur pleine, deux
# colonnes calees sur 26 et 192. Tout le lot s'y aligne, sans exception.
M = 26
W = L - 2 * M
COL_2 = (M, 192)


def _filigrane(cx, cy, nom, x, y, taille):
    """Icone de mode en filigrane : donne du fond sans ajouter de couleur."""
    return f'<g opacity="0.05">{icone(nom, cx + x, cy + y, taille)}</g>'


def _version(b, cx, y, libelle):
    """Ligne de version des pages legales, en capitales espacees comme dans l'app."""
    b.append(texte(cx + M, y, libelle, T_MICRO, BODY, INK3, espacement=1.6))


def _titre(b, cx, y, libelle):
    b.append(texte(cx + M, y, libelle.upper(), 15, DISPLAY, INK))
    return y + 22


def _corps(b, cx, y, lignes, interligne=18):
    b.append(paragraphe(cx + M, y, lignes, T_LABEL, INK2, interligne))
    return y + len(lignes) * interligne


def _tableau(b, cx, y, colonnes, lignes, h_ligne=32):
    """Tableau legal : entete en capitales, filets francs, zero aplat de couleur.

    `colonnes` est une liste (libelle, largeur) dont la somme fait exactement W,
    `lignes` une liste de lignes, chaque cellule etant une liste de lignes de
    texte deja coupees a la main.
    """
    htot = 26 + len(lignes) * h_ligne
    b.append(f'<rect x="{cx + M}" y="{y}" width="{W}" height="{htot}" rx="12" fill="{BG_HAUT}"/>')
    x = cx + M
    for libelle, largeur in colonnes:
        b.append(texte(x + 9, y + 17, libelle.upper(), T_MICRO - 1, DISPLAY, INK3, espacement=1.1))
        if x > cx + M:
            b.append(f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y + htot}" '
                     f'stroke="{INK}" stroke-width="1" opacity="0.2"/>')
        x += largeur
    b.append(f'<line x1="{cx + M}" y1="{y + 26}" x2="{cx + M + W}" y2="{y + 26}" '
             f'stroke="{INK}" stroke-width="2"/>')
    for i, ligne in enumerate(lignes):
        yy = y + 26 + i * h_ligne
        if i:
            b.append(f'<line x1="{cx + M}" y1="{yy}" x2="{cx + M + W}" y2="{yy}" '
                     f'stroke="{INK}" stroke-width="1" opacity="0.25"/>')
        x = cx + M
        for (_, largeur), cellule in zip(colonnes, ligne):
            b.append(paragraphe(x + 9, yy + 16, cellule, T_MICRO, INK2, 13))
            x += largeur
    b.append(f'<rect x="{cx + M}" y="{y}" width="{W}" height="{htot}" rx="12" fill="none" '
             f'stroke="{INK}" stroke-width="2"/>')
    return y + htot


def _sommaire(b, cx, y, titres, colonnes=1, interligne=15):
    """Sections restantes en liste compacte : la page en compte douze a vingt."""
    par_col = (len(titres) + colonnes - 1) // colonnes
    htot = 30 + (par_col - 1) * interligne
    b.append(bloc(cx + M, y, W, htot, SURFACE, r=12, cerne=INK, epaisseur=2))
    for c in range(colonnes):
        part = titres[c * par_col:(c + 1) * par_col]
        b.append(paragraphe(cx + COL_2[c] + 16, y + 21, part, T_MICRO, INK2, interligne))
    return y + htot


def erreur_plantage(s, cx, cy):
    """ErrorBoundary, branche hasError : ecran de secours au milieu d'une soiree."""
    b = [_filigrane(cx, cy, "spade", L / 2 - 130, 300, 260),
         bloc(cx + M, cy + 236, W, 470, SURFACE, r=18, cerne=INK, epaisseur=3, ombre=6, ombre_couleur=INK),
         bloc(cx + L / 2 - 34, cy + 284, 68, 68, JAUNE, r=16, cerne=TILE_INK, epaisseur=3,
              ombre=4, ombre_couleur=TILE_INK),
         texte(cx + L / 2, cy + 334, "!", 40, DISPLAY, TILE_INK, ancre="middle"),
         texte(cx + L / 2, cy + 408, "OUPS, LA PARTIE A PLANTE.", 24, DISPLAY, INK, ancre="middle"),
         paragraphe(cx + L / 2, cy + 448, ["Une erreur inattendue est survenue.",
                                           "Relance l'application pour reprendre la",
                                           "soiree - il faudra ressaisir la tablee."],
                    T_CORPS, INK2, 22, "middle"),
         bouton(cx + 62, cy + 552, 306, "RELANCER L'APPLICATION", True, 60, 17),
         texte(cx + L / 2, cy + 752, "ECRAN DE SECOURS, TABLEE A RESSAISIR",
               T_MICRO, DISPLAY, INK3, ancre="middle", espacement=1.4),
         texte(cx + L / 2, cy + 800, "BACCHUS", 22, DISPLAY, INK3, ancre="middle", espacement=3),
         texte(cx + L / 2, cy + 824, "Version 0.41.0", T_MICRO, BODY, INK3, ancre="middle")]
    ecran(s, "Erreur - la partie a plante", cx, cy, "\n      ".join(b))


def erreur_nouvelle_version(s, cx, cy):
    """ErrorBoundary, branche recovering : un deploiement a remplace les fichiers."""
    b = [_filigrane(cx, cy, "disc3", L / 2 - 130, 300, 260),
         bloc(cx + M, cy + 276, W, 388, SURFACE, r=18, cerne=INK, epaisseur=3, ombre=6, ombre_couleur=INK)]
    # Trois aplats francs plutot qu'un rond qui tourne : la charte n'a pas de flou.
    for i in range(3):
        b.append(bloc(cx + L / 2 - 52 + i * 38, cy + 330, 26, 26, NEON if i < 2 else SURFACE_HAUT,
                      r=6, cerne=TILE_INK if i < 2 else INK, epaisseur=3))
    b += [texte(cx + L / 2, cy + 434, "NOUVELLE VERSION", 26, DISPLAY, INK, ancre="middle"),
          paragraphe(cx + L / 2, cy + 476, ["L'application se met a jour,", "un instant."],
                     T_CORPS, INK2, 22, "middle"),
          texte(cx + L / 2, cy + 752, "RECHARGEMENT AUTOMATIQUE, UNE SEULE FOIS",
                T_MICRO, DISPLAY, INK3, ancre="middle", espacement=1.4),
          texte(cx + L / 2, cy + 800, "BACCHUS", 22, DISPLAY, INK3, ancre="middle", espacement=3),
          texte(cx + L / 2, cy + 824, "Version 0.41.0", T_MICRO, BODY, INK3, ancre="middle")]
    ecran(s, "Erreur - nouvelle version", cx, cy, "\n      ".join(b))


def chargement_ecran(s, cx, cy):
    """Fallback de Suspense : un ecran differe, mode ou page legale, n'est pas encore la."""
    # La zone en pointilles est vide par construction : l'ecran differe n'existe
    # pas encore, et un squelette invente ferait croire a un contenu prevu.
    b = [f'<rect x="{cx + M}" y="{cy + 150}" width="{W}" height="580" rx="18" fill="none" '
         f'stroke="{INK3}" stroke-width="3" stroke-dasharray="12 10"/>',
         texte(cx + L / 2, cy + 430, "chargement…", T_CORPS, BODY, INK3, ancre="middle", espacement=1.4)]
    for i in range(3):
        b.append(f'<circle cx="{cx + L / 2 - 22 + i * 22}" cy="{cy + 470}" r="5" '
                 f'fill="{INK3}" opacity="{0.9 - i * 0.3}"/>')
    b.append(texte(cx + L / 2, cy + 790, "ECRAN NEUTRE, AUCUN CONTENU AFFICHE",
                   T_MICRO, DISPLAY, INK3, ancre="middle", espacement=1.4))
    b.append(texte(cx + L / 2, cy + 840, "BACCHUS", 22, DISPLAY, INK3, ancre="middle", espacement=3))
    ecran(s, "Chargement d'ecran", cx, cy, "\n      ".join(b))


def toast_sortie(s, cx, cy):
    """ExitToast : le piege de retour materiel arme la pastille pendant deux secondes."""
    # L'ecran courant reste dessine, attenue : la pastille se superpose, elle ne
    # remplace rien et n'assombrit pas la page.
    b = [f'<rect x="{cx + M}" y="{cy + 66}" width="{W}" height="38" rx="10" fill="{SURFACE}" '
         f'stroke="{INK}" stroke-width="2" opacity="0.4"/>']
    for i in range(10):
        x = cx + COL_2[i % 2]
        y = cy + 128 + (i // 2) * 130
        b.append(bloc(x, y, 180, 116, SURFACE, r=14, cerne=INK, epaisseur=3, opacite=0.4))
        b.append(bloc(x + 18, y + 20, 44, 44, BG_HAUT, r=10, cerne=INK, epaisseur=2, opacite=0.4))
        b.append(bloc(x + 18, y + 78, 116, 12, INK, r=6, epaisseur=0, opacite=0.16))
    b += [bloc(cx + 97, cy + 792, 236, 44, SURFACE_HAUT, r=22, cerne=INK, epaisseur=3,
               ombre=5, ombre_couleur=INK),
          texte(cx + L / 2, cy + 820, "Appuie encore pour quitter", T_CORPS, BODY, INK, ancre="middle"),
          texte(cx + L / 2, cy + 876, "DEUX SECONDES POUR CONFIRMER LE RETOUR",
                T_MICRO, DISPLAY, INK3, ancre="middle", espacement=1.4)]
    ecran(s, "Toast de sortie", cx, cy, "\n      ".join(b))


def mentions_legales(s, cx, cy):
    """MentionsLegalesScreen : douze sections, dont le tableau des prestataires."""
    b = [entete(cx, cy, "MENTIONS LEGALES")]
    _version(b, cx, cy + 148, "VERSION APPLICABLE AU 4 AOUT 2026")

    _titre(b, cx, cy + 176, "1. Editeur du site et des applications")
    b.append(bloc(cx + M, cy + 186, W, 182, SURFACE, r=12, cerne=INK, epaisseur=2))
    b.append(paragraphe(cx + M + 18, cy + 210, [
        "Nom : Adam Beloucif, nom commercial BLF Lab's",
        "Statut : entrepreneur individuel, micro-entreprise",
        "Adresse : 6 impasse Edouard Vaillant,",
        "94550 Chevilly-Larue, France",
        "SIREN 108386855 - SIRET 10838685500010",
        "Code APE 6201Z - Programmation informatique",
        "TVA non applicable, art. 293 B du CGI",
        "Contact : adambeloucif@gmail.com",
        "Directeur de la publication : Adam Beloucif"], T_LABEL, INK2, 19))

    y = _titre(b, cx, cy + 388, "2. Activite commerciale")
    _corps(b, cx, y, ["Acces premium a vie et packs a la carte, en",
                      "paiement unique. Micro-entreprise validee par",
                      "l'INSEE et l'URSSAF le 4 aout 2026."])

    y = _titre(b, cx, cy + 466, "3. Hebergement du site web (PWA)")
    _corps(b, cx, y, ["Vercel Inc., 340 S Lemon Ave #4133, Walnut,",
                      "CA 91789, Etats-Unis. vercel.com"])

    y = _titre(b, cx, cy + 544, "4. Fonctionnement et infrastructure")
    y = _corps(b, cx, y, ["Bacchus fonctionne integralement en local sur",
                          "l'appareil. Prestataires techniques :"])
    _tableau(b, cx, cy + 604,
             [("Service", 104), ("Fonction", 144), ("Prestataire", 130)],
             [[["Paiement web"], ["Premium et packs", "sur le site"], ["Stripe Payments", "Europe Ltd."]],
              [["Achats in-app"], ["Verification et", "restauration"], ["RevenueCat Inc."]],
              [["Mesure", "d'audience"], ["Analytics, apres", "consentement"], ["PostHog", "(EU Cloud)"]],
              [["Distribution", "mobile"], ["Boutiques", "d'applications"], ["Google Ireland,", "Apple Distribution"]]],
             h_ligne=32)

    _sommaire(b, cx, cy + 770, ["5. Propriete intellectuelle",
                                "6. Donnees personnelles",
                                "7. Cookies et traceurs",
                                "8. Limitation de responsabilite",
                                "9. Mediation de la consommation",
                                "10. Credits et ressources tierces",
                                "11. Droit applicable et litiges",
                                "12. Contact"], colonnes=2)

    b.append(puce(cx + M, cy + 852, "MEDIATION CM2C"))
    b.append(texte(cx + 186, cy + 872, "01 89 47 00 14 - litiges@cm2c.net", T_MICRO, BODY, INK2))
    ecran(s, "Mentions legales", cx, cy, "\n      ".join(b))


def confidentialite(s, cx, cy):
    """ConfidentialiteScreen : deux tableaux RGPD et l'encart de revue en attente."""
    b = [entete(cx, cy, "POLITIQUE DE CONFIDENTIALITE")]
    _version(b, cx, cy + 148, "VERSION APPLICABLE AU 4 AOUT 2026")

    y = _titre(b, cx, cy + 174, "1. Responsable de traitement")
    _corps(b, cx, y, ["Adam Beloucif, nom commercial BLF Lab's,",
                      "6 impasse Edouard Vaillant, 94550 Chevilly-Larue."])

    y = _titre(b, cx, cy + 242, "2. Donnees collectees et bases legales")
    _corps(b, cx, y, ["Aucun compte, aucun identifiant, aucun mot de",
                      "passe. Seules les donnees de paiement et, si",
                      "consenti, la mesure d'audience."])
    _tableau(b, cx, cy + 320,
             [("Donnee", 98), ("Finalite", 92), ("Base legale", 88), ("Conservation", 100)],
             [[["Prenoms des", "joueurs"], ["Affichage en", "partie locale"],
               ["Traitement sur", "l'appareil"], ["Local, jamais", "transmis"]],
              [["Email et", "paiement web"], ["Recu et", "facture"],
               ["Contrat", "art. 6.1.b"], ["10 ans"]],
              [["Achat mobile", "(RevenueCat)"], ["Restauration", "de l'achat"],
               ["Contrat", "art. 6.1.b"], ["Duree de", "l'entitlement"]],
              [["Evenements", "d'usage"], ["Mesure", "d'audience"],
               ["Consentement", "art. 6.1.a"], ["13 mois"]]],
             h_ligne=38)

    y = _titre(b, cx, cy + 520, "3. Sous-traitants et destinataires")
    _corps(b, cx, y, ["Chaque sous-traitant agit sous DPA, art. 28 RGPD."])
    _tableau(b, cx, cy + 562,
             [("Sous-traitant", 130), ("Fonction", 140), ("Localisation", 108)],
             [[["Stripe Payments", "Europe Ltd."], ["Paiement par carte", "sur le web"],
               ["UE (Irlande)", "et Etats-Unis"]],
              [["RevenueCat Inc."], ["Achats in-app,", "restauration"], ["Etats-Unis", "(clauses types)"]],
              [["PostHog (EU Cloud)"], ["Mesure d'audience"], ["UE (Allemagne)"]]])

    # Encart de revue : seul point encore ouvert de la page, donc seul aplat vif.
    b.append(bloc(cx + M, cy + 700, W, 56, JAUNE, r=12, cerne=TILE_INK, epaisseur=2,
                  ombre=4, ombre_couleur=TILE_INK))
    b.append(texte(cx + M + 18, cy + 722, "A VALIDER", T_MICRO, DISPLAY, TILE_INK, espacement=1.4))
    b.append(paragraphe(cx + M + 106, cy + 720, ["DPA a archiver avec chaque sous-traitant",
                                                 "avant la mise en production complete."],
                        T_MICRO, TILE_INK, 16))

    # Titres raccourcis pour tenir dans la colonne de 166 : au-dela, la premiere
    # colonne mord sur la seconde, defaut vu au rendu de controle.
    _sommaire(b, cx, cy + 772, ["4. Transferts hors UE",
                                "5. Durees de conservation",
                                "6. Droits des personnes",
                                "7. Effacement des donnees",
                                "8. Cookies et traceurs",
                                "9. Public concerne, mineurs",
                                "10. Securite des donnees",
                                "11. Modification de la page",
                                "12. Contact"], colonnes=2)

    b.append(texte(cx + L / 2, cy + 884, "Aucune donnee n'est vendue a des tiers.",
                   T_MICRO, BODY, INK3, ancre="middle"))
    ecran(s, "Politique de confidentialite", cx, cy, "\n      ".join(b))


def cgu_cgv(s, cx, cy):
    """CguScreen : vingt articles, dont le 14 qui fonde l'execution immediate."""
    b = [entete(cx, cy, "CGU / CGV")]
    _version(b, cx, cy + 148, "VERSION APPLICABLE AU 4 AOUT 2026")

    b.append(texte(cx + M, cy + 176, "PARTIE 1 - CONDITIONS GENERALES D'UTILISATION",
                   T_MICRO, DISPLAY, ORANGE_INK, espacement=1.4))
    _sommaire(b, cx, cy + 188, ["1. Objet",
                                "2. Acces au service et age minimum",
                                "3. Fonctionnement hors ligne, sans compte",
                                "4. Comportement de l'utilisateur",
                                "5. Propriete intellectuelle",
                                "6. Disponibilite du service",
                                "7. Responsabilite",
                                "8. Cessation d'utilisation"], interligne=16)

    b.append(texte(cx + M, cy + 348, "PARTIE 2 - CONDITIONS GENERALES DE VENTE",
                   T_MICRO, DISPLAY, ORANGE_INK, espacement=1.4))
    _sommaire(b, cx, cy + 360, ["9. Objet et description de l'offre",
                                "10. Prix et paiement, 14,99 et 2,99 EUR",
                                "11. Livraison du contenu numerique",
                                "12. Absence de renouvellement automatique",
                                "13. Restauration des achats"], interligne=16)

    b.append(bloc(cx + M, cy + 474, W, 36, JAUNE, r=12, cerne=TILE_INK, epaisseur=2,
                  ombre=4, ombre_couleur=TILE_INK))
    b.append(texte(cx + M + 18, cy + 498, "ARTICLE 14 - DROIT DE RETRACTATION",
                   15, DISPLAY, TILE_INK))
    b.append(bloc(cx + M, cy + 518, W, 210, SURFACE, r=14, cerne=INK, epaisseur=3,
                  ombre=5, ombre_couleur=INK))
    b.append(paragraphe(cx + M + 20, cy + 546, ["Delai de principe de 14 jours, art. L221-18.",
                                                "Exception contenu numerique, art. L221-28, 13 :"],
                        T_LABEL, INK2, 19))
    for i, lignes in enumerate([
            ["accord prealable et expres pour que l'execution",
             "commence avant la fin du delai de 14 jours ;"],
            ["reconnaissance expresse de la perte du droit",
             "de retractation."]]):
        yy = cy + 596 + i * 56
        b.append(bloc(cx + M + 20, yy, 24, 24, SURFACE_HAUT, r=6, cerne=INK, epaisseur=3))
        b.append(paragraphe(cx + M + 56, yy + 12, lignes, T_MICRO, INK2, 16))
    b.append(texte(cx + M + 20, cy + 706, "Cases non pre-cochees, recueillies avant paiement.",
                   T_MICRO, BODY, INK3))

    _sommaire(b, cx, cy + 744, ["15. Garantie legale de conformite",
                                "16. Mediation de la consommation, CM2C",
                                "17. Facturation",
                                "18. Modification des CGU/CGV",
                                "19. Droit applicable et juridiction",
                                "20. Contact"], interligne=16)

    b.append(texte(cx + L / 2, cy + 884, "Contact : adambeloucif@gmail.com",
                   T_MICRO, BODY, INK3, ancre="middle"))
    ecran(s, "CGU et CGV", cx, cy, "\n      ".join(b))


ECRANS = [erreur_plantage, erreur_nouvelle_version, chargement_ecran, toast_sortie,
          mentions_legales, confidentialite, cgu_cgv]
