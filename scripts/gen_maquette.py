# -*- coding: utf-8 -*-
"""Assemble la maquette complete Bacchus en un SVG importable dans Figma.

POURQUOI UN SVG. Le format .fig est proprietaire et sans specification publique.
Figma importe le SVG nativement en conservant les groupes comme calques, les
formes comme vecteurs et les <text> comme texte editable. Un .fig natif est
produit a part par scripts/build_fig.py, depuis ce meme SVG.

CE QUI REND LE FICHIER UTILISABLE, et qu'un export naif rate :
  - chaque surface est un <g id="..."> nomme, qui devient un calque nomme ;
  - le texte reste du <text>, jamais des courbes ;
  - les ombres sont des rectangles decales, pas des filtres : un feDropShadow
    s'importe mal et serait flou, donc contraire au style ;
  - les jetons sont LUS dans tokens.css, jamais recopies.

Usage : python scripts/gen_maquette.py
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from maquette_core import COL, DISPLAY, H, INK, INK2, L, LIGNE, RACINE, BODY, defs, texte  # noqa: E402
from maquette_marque import PLANCHES_MARQUE  # noqa: E402
from maquette_lot_1_parcours import ECRANS as LOT1  # noqa: E402
from maquette_lot_2_coupe_gorge import ECRANS as LOT2  # noqa: E402
from maquette_lot_3_modes import ECRANS as LOT3  # noqa: E402
from maquette_lot_4_achat import ECRANS as LOT4  # noqa: E402
from maquette_lot_5_reglages import ECRANS as LOT5  # noqa: E402
from maquette_lot_6_systeme import ECRANS as LOT6  # noqa: E402

SORTIE = RACINE / "design-system" / "bacchus" / "maquette-bacchus.svg"

# Les planches de marque d'abord : on lit le systeme avant ses applications.
# Elles gardent la palette ENTIERE, c'est leur role de la documenter, alors que
# les ecrans s'en tiennent a la palette resserree. Documenter une couleur et
# s'en servir partout sont deux choses differentes.
SECTIONS = [
    ("MARQUE", PLANCHES_MARQUE),
    ("PARCOURS", LOT1),
    ("LE COUPE-GORGE", LOT2),
    ("LES MODES DE JEU", LOT3),
    ("ACHAT ET PREMIUM", LOT4),
    ("REGLAGES ET REGLES", LOT5),
    ("SYSTEME ET LEGAL", LOT6),
]

COLONNES = 6
MARGE = 110
TITRE_SECTION = 100

s = []
y = MARGE + 100
plan = []
for nom_section, ecrans in SECTIONS:
    plan.append((nom_section, y, ecrans))
    lignes = (len(ecrans) + COLONNES - 1) // COLONNES
    y += TITRE_SECTION + lignes * LIGNE

total = sum(len(e) for _, e in SECTIONS)
LARGEUR = MARGE * 2 + (COLONNES - 1) * COL + L
HAUTEUR = y + MARGE

s.append(f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" '
         f'width="{LARGEUR}" height="{HAUTEUR}" viewBox="0 0 {LARGEUR} {HAUTEUR}">')
s.append(f'  <rect width="{LARGEUR}" height="{HAUTEUR}" fill="#E8E2D8"/>')
s.append(defs())
s.append(f'  {texte(MARGE, 66, "BACCHUS - MAQUETTE COMPLETE", 44, DISPLAY, INK)}')
s.append(f'  {texte(MARGE, 98, f"{total} surfaces - genere par scripts/gen_maquette.py, jetons lus dans src/styles/tokens.css. Ne pas editer a la main.", 15, BODY, INK2)}')

for nom_section, y0, ecrans in plan:
    s.append(f'  {texte(MARGE, y0, nom_section, 30, DISPLAY, INK, espacement=1.5)}')
    for i, fn in enumerate(ecrans):
        cx = MARGE + (i % COLONNES) * COL
        cy = y0 + 64 + (i // COLONNES) * LIGNE
        fn(s, cx, cy)

s.append('</svg>')

SORTIE.parent.mkdir(parents=True, exist_ok=True)
SORTIE.write_text("\n".join(s), encoding="utf-8")
print(f"{SORTIE.relative_to(RACINE)} : {total} surfaces, {SORTIE.stat().st_size / 1024:.0f} ko")
