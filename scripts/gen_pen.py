# -*- coding: utf-8 -*-
"""Compose `maquette-bacchus.pen`, l'etape qui manque avant le vrai `.fig`.

POURQUOI PASSER PAR LA. OpenPencil sait ECRIRE le `.fig` mais ne sait LIRE que
`.fig` et `.pen`. Le SVG de la maquette lui est illisible. On construit donc le
document d'echange `.pen`, puis `openpencil convert` produit le `.fig` natif.

POURQUOI IMPORTER `gen_maquette`. Ce module expose, apres import, la liste des
fragments SVG deja assemblee avec la meme grille et les memes appels d'ecrans.
La reutiliser garantit que le `.fig` et le SVG decrivent la MEME maquette. La
recopier ici creerait deux geometries a maintenir, donc une divergence a terme.
Effet de bord assume : l'import reecrit le SVG, a l'identique.

CE QUE PRODUIT LE DOCUMENT :
  - une page portant le nom du cadre racine ;
  - un cadre racine qui tient toute la planche ;
  - 36 CADRES Figma, un par surface, nommes comme les groupes du SVG, chacun
    contenant ses rectangles, ellipses, textes et chemins ;
  - les titres de sections et les libelles de surfaces poses sur la planche.

Usage : python scripts/gen_pen.py
"""
import json
import pathlib
import sys
import xml.etree.ElementTree as ET

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

import gen_maquette  # noqa: E402  import a effet de bord, voir en-tete
from maquette_core import BG, H, INK, L, RACINE  # noqa: E402
from pen_core import CONVERTISSEURS, ident  # noqa: E402

NS = "{http://www.w3.org/2000/svg}"
SORTIE = RACINE / "design-system" / "bacchus" / "maquette-bacchus.pen"


def convertir(el, ox, oy, rot=None):
    """Descend un sous-arbre SVG et rend la liste de noeuds `.pen` equivalente."""
    tag = el.tag.replace(NS, "")
    if tag == "g":
        t = el.get("transform", "")
        if t.startswith("rotate("):
            a, px, py = (float(v) for v in t[7:t.index(")")].split())
            rot = (a, px, py)
        out = []
        for enfant in el:
            out += convertir(enfant, ox, oy, rot)
        return out
    fn = CONVERTISSEURS.get(tag)
    return fn(el, ox, oy, rot) if fn else []


def cadre_ecran(groupe):
    """Un groupe `<g id="...">` devient un cadre nomme, plus son libelle."""
    nom = groupe.get("id")
    interieur = groupe.find(f"{NS}g")
    chassis = interieur.find(f"{NS}rect")
    cx, cy = float(chassis.get("x")), float(chassis.get("y"))

    enfants = []
    for el in interieur:
        enfants += convertir(el, cx, cy)

    # Le cadre est sans fond : le chassis, premier enfant, porte deja l'aplat,
    # la trame et le cerne arrondi de l'ecran.
    cadre = {"type": "frame", "id": ident("f"), "name": nom,
             "x": cx, "y": cy, "width": L, "height": H,
             "fill": [], "cornerRadius": 38, "clip": True, "children": enfants}

    libelles = [n for el in groupe if el.tag == f"{NS}text"
                for n in convertir(el, 0, 0)]
    return cadre, libelles


racine = ET.fromstring("\n".join(gen_maquette.s))
ecrans, planche = [], []
fond = BG

for el in racine:
    tag = el.tag.replace(NS, "")
    if tag == "defs":
        continue
    if tag == "g" and el.get("id"):
        cadre, libelles = cadre_ecran(el)
        ecrans.append(cadre)
        planche += libelles
    elif tag == "rect":
        # Le fond de planche est repris par le cadre racine, pas duplique.
        fond = el.get("fill", BG)
    else:
        planche += convertir(el, 0, 0)

# Le lecteur nomme la page d'apres le premier noeud du document : un cadre
# racine donne donc a la fois une page nommee et une planche deplacable.
document = {
    "version": "1.0",
    "children": [{
        "type": "frame", "id": "planche", "name": "Bacchus - maquette complete",
        "x": 0, "y": 0, "width": gen_maquette.LARGEUR, "height": gen_maquette.HAUTEUR,
        "fill": fond, "stroke": {"align": "inside", "thickness": 1, "fill": INK},
        "children": planche + ecrans,
    }],
}

SORTIE.parent.mkdir(parents=True, exist_ok=True)
SORTIE.write_text(json.dumps(document, ensure_ascii=False, indent=1), encoding="utf-8")


def compte(noeuds):
    return sum(1 + compte(n.get("children", [])) for n in noeuds)


print(f"{SORTIE.relative_to(RACINE)} : {len(ecrans)} cadres, "
      f"{compte(document['children'])} noeuds, {SORTIE.stat().st_size / 1024:.0f} ko")
