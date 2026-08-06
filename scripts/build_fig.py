# -*- coding: utf-8 -*-
"""Chaine complete SVG -> `.pen` -> `.fig`, avec ses verifications.

POURQUOI UN SCRIPT PLUTOT QU'UNE LIGNE DE COMMANDE. Trois pieges se paient
comptant sur ce poste, et ils ne se devinent pas :

  1. La CLI OpenPencil headless appelle `Bun.file`. Lancee par `npx` sous Node,
     elle echoue sur « Bun is not defined ». Elle doit tourner sous Bun.
  2. Sous Windows, le chargeur CanvasKit d'OpenPencil calcule le chemin du
     module WebAssembly avec `new URL(...).pathname`, ce qui rend `/C:/...`.
     Node comme Bun resolvent ensuite `\\C:\\...`, qui n'existe pas : tout
     export raster echoue. Un correctif d'une ligne, applique a la copie
     locale de l'outil et non au depot, retire le `/` de tete.
  3. `convert` ecrit un `.fig` sans vignette. `export -f fig` en calcule une,
     et Figma affiche cette vignette dans la liste des fichiers.

L'outillage est installe hors du depot, dans un bac a sable dedie, pour ne pas
polluer les dependances du projet avec une chaine qui ne sert qu'au design.

Usage : python scripts/build_fig.py
"""
import json
import os
import pathlib
import shutil
import subprocess
import sys

RACINE = pathlib.Path(__file__).resolve().parent.parent
SORTIE = RACINE / "design-system" / "bacchus"
BAC = pathlib.Path(os.environ.get("LOCALAPPDATA", pathlib.Path.home())) / "openpencil-env"
VERSION = "0.13.2"
CLI = BAC / "node_modules" / "@open-pencil" / "cli" / "bin" / "openpencil.js"
CANVASKIT = BAC / "node_modules" / "@open-pencil" / "core" / "dist" / "io" / "formats" / "raster" / "headless.js"

PATHNAME_BOGUE = 'const binDir = new URL(".", ckPath).pathname;'
PATHNAME_CORRIGE = ('const binDir = new URL(".", ckPath).pathname'
                    '.replace(/^\\/([A-Za-z]:\\/)/, "$1");')


def bun():
    chemin = shutil.which("bun")
    if not chemin:
        raise SystemExit("bun introuvable : installer Bun, la CLI OpenPencil ne "
                         "tourne pas sous Node (voir en-tete du script)")
    return chemin


def prepare_outil():
    """Installe puis corrige la copie locale de l'outil. Idempotent."""
    if not CLI.exists():
        BAC.mkdir(parents=True, exist_ok=True)
        (BAC / "package.json").write_text(
            json.dumps({"name": "openpencil-env", "private": True, "type": "module"}),
            encoding="utf-8")
        subprocess.run([bun(), "add", f"@open-pencil/cli@{VERSION}"], cwd=BAC, check=True)
    source = CANVASKIT.read_text(encoding="utf-8")
    if PATHNAME_BOGUE in source:
        CANVASKIT.write_text(source.replace(PATHNAME_BOGUE, PATHNAME_CORRIGE), encoding="utf-8")
        print("outil : correctif de chemin CanvasKit applique")


def openpencil(*args, silencieux=False):
    r = subprocess.run([bun(), str(CLI), *args], cwd=SORTIE,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0:
        print(r.stdout, r.stderr, file=sys.stderr)
        raise SystemExit(f"echec de `openpencil {args[0]}`")
    if not silencieux:
        print(r.stdout.rstrip())
    return r.stdout


def main():
    # La CLI decore sa sortie de coches et de couleurs. La console Windows est
    # en cp1252 par defaut et casserait sur le premier caractere hors table.
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    prepare_outil()

    subprocess.run([sys.executable, str(RACINE / "scripts" / "gen_pen.py")], check=True)

    # `export -f fig` et non `convert` : seul le premier calcule la vignette.
    openpencil("export", "maquette-bacchus.pen", "-f", "fig", "-o", "maquette-bacchus.fig")

    print("\n--- info ---")
    openpencil("info", "maquette-bacchus.fig")

    # Preuve de rendu : un `.fig` qui s'inspecte mais ne se dessine pas ne prouve
    # rien. La verification tire une image et exige qu'elle ne soit pas vide.
    apercu = SORTIE / "apercu-verification.png"
    openpencil("export", "maquette-bacchus.fig", "-f", "png", "-s", "0.12",
               "-o", apercu.name, silencieux=True)
    poids = apercu.stat().st_size
    apercu.unlink()
    if poids < 20_000:
        raise SystemExit(f"rendu suspect : {poids} octets seulement")

    cadres = openpencil("find", "maquette-bacchus.fig", "--type", "FRAME", silencieux=True)
    fig = SORTIE / "maquette-bacchus.fig"
    print(f"\n{fig.relative_to(RACINE)} : {fig.stat().st_size / 1024:.0f} ko, "
          f"{cadres.count('[frame]')} cadres, rendu verifie ({poids / 1024:.0f} ko de PNG)")


if __name__ == "__main__":
    main()
