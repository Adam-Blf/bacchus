# -*- coding: utf-8 -*-
"""Traduit les primitives SVG de la maquette en noeuds du format `.pen`.

POURQUOI CE MODULE EXISTE. OpenPencil ne sait LIRE que deux formats, `.fig`
(binaire natif) et `.pen` (JSON d'echange). Il ne lit pas le SVG. Pour obtenir
un vrai `.fig`, il faut donc composer un document `.pen` puis le convertir.
Plutot que de redessiner la maquette une seconde fois, on traduit la sortie des
modules `maquette_*` : la geometrie reste ecrite une seule fois, et une planche
qui bouge dans le SVG bouge dans le `.fig` sans effort.

CE QUE LE FORMAT `.pen` SAIT FAIRE, verifie dans les sources du paquet
`@open-pencil/core` (dist/io/formats/pen) et non devine :
  - types de noeuds : frame, rectangle, ellipse, text, path, ref ;
  - `fill` accepte une couleur, un tableau vide voulant dire « aucun fond » ;
  - `stroke` porte epaisseur, couleur et alignement, sans pointilles ;
  - `rotation` pivote autour du CENTRE du noeud, comme le `rotate` de SVG ;
  - `path` prend une geometrie SVG, mais le lecteur la RENORMALISE dans la
    boite du noeud, d'ou la translation a l'origine faite ici.

CE QU'IL NE SAIT PAS FAIRE, et qu'aucune ruse ne contourne :
  - pas de noeud image : les PNG d'icones et les SVG embarques deviennent des
    reperes nommes, faute de quoi le document mentirait sur son contenu ;
  - pas de motif : la trame diagonale de fond est omise, son poids visuel reel
    est inferieur au pour cent ;
  - pas de pointilles : les traits en tirets deviennent des traits pleins.
"""
import math
import re

# Le texte `.pen` se positionne par le HAUT de sa boite, le texte SVG par sa
# ligne de base. Le rapport mesure a l'export vaut 0.80 em pour une hauteur de
# ligne de 1.0, verifie au rendu sur un gabarit de calibrage.
ASCENDANTE = 0.80

_compteur = [0]


def ident(prefixe="n"):
    _compteur[0] += 1
    return f"{prefixe}{_compteur[0]}"


def nb(el, cle, defaut=0.0):
    v = el.get(cle)
    return defaut if v is None else float(v)


def _fond(valeur):
    """`None` veut dire « noeud a ignorer », `[]` veut dire « sans fond »."""
    if valeur is None:
        return []
    if valeur == "none":
        return []
    if valeur.startswith("url("):
        return None
    return valeur


def _cerne(el):
    couleur = el.get("stroke")
    if not couleur or couleur == "none":
        return None
    # Alignement centre : c'est la semantique du trait SVG, decaler ici
    # deplacerait les aplats d'une demi-epaisseur.
    return {"align": "center", "thickness": nb(el, "stroke-width", 1.0), "fill": couleur}


def _pivote(cx, cy, rot):
    """Applique la rotation heritee du groupe parent au centre d'un noeud."""
    if rot is None:
        return cx, cy, 0.0
    angle, px, py = rot
    r = math.radians(angle)
    dx, dy = cx - px, cy - py
    return px + dx * math.cos(r) - dy * math.sin(r), py + dx * math.sin(r) + dy * math.cos(r), angle


def _boite(x, y, w, h, ox, oy, rot):
    """Coordonnees du noeud dans son cadre parent, rotation comprise."""
    cx, cy, angle = _pivote(x + w / 2, y + h / 2, rot)
    return {"x": round(cx - w / 2 - ox, 2), "y": round(cy - h / 2 - oy, 2),
            "width": round(w, 2), "height": round(h, 2),
            **({"rotation": angle} if angle else {})}


def _rayon(el):
    r = el.get("rx")
    return {} if r is None else {"cornerRadius": float(r)}


def _opacite(el):
    o = el.get("opacity")
    return {} if o is None else {"opacity": float(o)}


def rectangle(el, ox, oy, rot):
    fond = _fond(el.get("fill"))
    if fond is None:
        return []  # motif : non representable, cf. en-tete du module
    n = {"type": "rectangle", "id": ident("r"), "fill": fond,
         **_boite(nb(el, "x"), nb(el, "y"), nb(el, "width"), nb(el, "height"), ox, oy, rot),
         **_rayon(el), **_opacite(el)}
    c = _cerne(el)
    if c:
        n["stroke"] = c
    return [n]


def ellipse(el, ox, oy, rot):
    r = nb(el, "r")
    fond = _fond(el.get("fill"))
    if fond is None:
        return []
    n = {"type": "ellipse", "id": ident("e"), "fill": fond,
         **_boite(nb(el, "cx") - r, nb(el, "cy") - r, 2 * r, 2 * r, ox, oy, rot),
         **_opacite(el)}
    c = _cerne(el)
    if c:
        n["stroke"] = c
    return [n]


def ligne(el, ox, oy, rot):
    """Un trait devient un rectangle mince : le format n'a pas de noeud trait,
    et un chemin de hauteur nulle ferait echouer la renormalisation du lecteur.
    """
    x1, y1, x2, y2 = nb(el, "x1"), nb(el, "y1"), nb(el, "x2"), nb(el, "y2")
    ep = nb(el, "stroke-width", 1.0)
    if abs(y1 - y2) < 0.01:
        x, y, w, h = min(x1, x2), y1 - ep / 2, abs(x2 - x1), ep
    elif abs(x1 - x2) < 0.01:
        x, y, w, h = x1 - ep / 2, min(y1, y2), ep, abs(y2 - y1)
    else:
        raise ValueError("trait oblique non gere : le convertisseur doit etre etendu")
    return [{"type": "rectangle", "id": ident("l"), "fill": el.get("stroke", "#000000"),
             **_boite(x, y, w, h, ox, oy, rot), **_opacite(el)}]


def texte(el, ox, oy, rot):
    contenu = "".join(el.itertext())
    if not contenu.strip():
        return []
    taille = nb(el, "font-size", 14.0)
    famille = el.get("font-family", "Inter").split(",")[0].strip()
    ancre = el.get("text-anchor", "start")
    haut = nb(el, "y") - taille * ASCENDANTE
    n = {"type": "text", "id": ident("t"), "name": contenu[:40],
         "content": contenu, "fontSize": taille, "fontFamily": famille,
         "fill": el.get("fill", "#000000"), "lineHeight": 1.0, **_opacite(el)}
    if el.get("font-weight"):
        n["fontWeight"] = int(float(el.get("font-weight")))
    if el.get("letter-spacing"):
        n["letterSpacing"] = float(el.get("letter-spacing"))
    if ancre == "start":
        # Sans largeur, le lecteur mesure lui-meme la boite et cale a gauche.
        b = _boite(nb(el, "x"), haut, len(contenu) * taille * 0.65, taille, ox, oy, rot)
        n.update({"x": b["x"], "y": b["y"]})
        if b.get("rotation"):
            n["rotation"] = b["rotation"]
        return [n]
    # Ancre centree ou a droite : le format n'a pas d'ancre, seulement un
    # alignement dans une boite. On donne une boite large, l'alignement fait
    # le reste, et le trop-plein est vide donc invisible.
    largeur = len(contenu) * taille * 1.1 + 24
    gauche = nb(el, "x") - (largeur / 2 if ancre == "middle" else largeur)
    n.update(_boite(gauche, haut, largeur, taille, ox, oy, rot))
    n["textAlign"] = "center" if ancre == "middle" else "right"
    return [n]


def image(el, ox, oy, rot):
    """Repere nomme : le format n'a pas de noeud image, taire l'absence serait
    livrer un document qui ment sur ce qu'il contient."""
    href = el.get("{http://www.w3.org/1999/xlink}href", "")
    genre = "SVG" if "image/svg" in href else "PNG"
    return [{"type": "rectangle", "id": ident("i"),
             "name": f"image {genre} - non portee par le format",
             "fill": "#1111111F", "cornerRadius": 8,
             "stroke": {"align": "center", "thickness": 1, "fill": "#11111159"},
             **_boite(nb(el, "x"), nb(el, "y"), nb(el, "width"), nb(el, "height"), ox, oy, rot)}]


_JETON = re.compile(r"[MLAZmlaz]|-?\d*\.?\d+(?:[eE][-+]?\d+)?")
_ARITE = {"M": 2, "L": 2, "A": 7, "Z": 0}


def _lire_chemin(d):
    """Decoupe un `d` en commandes. Seuls M, L, A et Z sont produits par la
    maquette : tout le reste doit lever plutot que d'etre approxime en silence.
    """
    jetons = _JETON.findall(d)
    sortie, i = [], 0
    while i < len(jetons):
        cmd = jetons[i].upper()
        if cmd not in _ARITE:
            raise ValueError(f"commande de chemin non geree : {jetons[i]}")
        if jetons[i] != cmd:
            raise ValueError("chemin en coordonnees relatives non gere")
        n = _ARITE[cmd]
        sortie.append((cmd, [float(v) for v in jetons[i + 1:i + 1 + n]]))
        i += 1 + n
    return sortie


def _points_arc(x0, y0, rx, ry, phi_deg, laf, sf, x1, y1, pas=96):
    """Echantillonne un arc elliptique, conversion extremites vers centre de la
    specification SVG F.6.5. Sert uniquement a mesurer la boite englobante.
    """
    phi = math.radians(phi_deg)
    dx2, dy2 = (x0 - x1) / 2, (y0 - y1) / 2
    x1p = math.cos(phi) * dx2 + math.sin(phi) * dy2
    y1p = -math.sin(phi) * dx2 + math.cos(phi) * dy2
    rx, ry = abs(rx), abs(ry)
    lam = (x1p / rx) ** 2 + (y1p / ry) ** 2
    if lam > 1:
        rx, ry = rx * math.sqrt(lam), ry * math.sqrt(lam)
    num = rx * rx * ry * ry - rx * rx * y1p * y1p - ry * ry * x1p * x1p
    den = rx * rx * y1p * y1p + ry * ry * x1p * x1p
    coef = math.sqrt(max(num, 0) / den) * (-1 if laf == sf else 1)
    cxp, cyp = coef * rx * y1p / ry, -coef * ry * x1p / rx
    cx = math.cos(phi) * cxp - math.sin(phi) * cyp + (x0 + x1) / 2
    cy = math.sin(phi) * cxp + math.cos(phi) * cyp + (y0 + y1) / 2
    t1 = math.atan2((y1p - cyp) / ry, (x1p - cxp) / rx)
    t2 = math.atan2((-y1p - cyp) / ry, (-x1p - cxp) / rx)
    dt = t2 - t1
    if not sf and dt > 0:
        dt -= 2 * math.pi
    elif sf and dt < 0:
        dt += 2 * math.pi
    return [(cx + rx * math.cos(phi) * math.cos(t1 + dt * k / pas) - ry * math.sin(phi) * math.sin(t1 + dt * k / pas),
             cy + rx * math.sin(phi) * math.cos(t1 + dt * k / pas) + ry * math.cos(phi) * math.sin(t1 + dt * k / pas))
            for k in range(pas + 1)]


def chemin(el, ox, oy, rot):
    """Le lecteur `.pen` recale la geometrie sur la boite du noeud. On lui donne
    donc un chemin deja ramene a l'origine et une boite exactement a sa mesure,
    sinon la forme se retrouve etiree ou posee a des coordonnees absolues.
    """
    cmds = _lire_chemin(el.get("d", ""))
    pts, cur, depart = [], (0.0, 0.0), (0.0, 0.0)
    for cmd, args in cmds:
        if cmd in ("M", "L"):
            cur = (args[0], args[1])
            pts.append(cur)
            if cmd == "M":
                depart = cur
        elif cmd == "A":
            pts.extend(_points_arc(cur[0], cur[1], args[0], args[1], args[2],
                                   int(args[3]), int(args[4]), args[5], args[6]))
            cur = (args[5], args[6])
        else:
            cur = depart
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    bx, by, w, h = min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)
    morceaux = []
    for cmd, args in cmds:
        if cmd in ("M", "L"):
            morceaux.append(f"{cmd} {args[0] - bx:.3f} {args[1] - by:.3f}")
        elif cmd == "A":
            morceaux.append("A {:.3f} {:.3f} {:g} {:g} {:g} {:.3f} {:.3f}".format(
                args[0], args[1], args[2], args[3], args[4], args[5] - bx, args[6] - by))
        else:
            morceaux.append("Z")
    fond = _fond(el.get("fill"))
    n = {"type": "path", "id": ident("p"), "geometry": " ".join(morceaux),
         "fill": [] if fond is None else fond, **_boite(bx, by, w, h, ox, oy, rot),
         **_opacite(el)}
    c = _cerne(el)
    if c:
        n["stroke"] = c
    return [n]


CONVERTISSEURS = {"rect": rectangle, "circle": ellipse, "line": ligne,
                  "text": texte, "image": image, "path": chemin}
