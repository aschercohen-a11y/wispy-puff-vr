"""Régénère tous les modèles de builder.html depuis les originaux Meshy.

Chaîne par modèle :
  1. Blender  decimate2.py   soudure des sommets + décimation au budget de triangles
  2. Python   albedo_webp.py albédo seul, ré-encodé en WebP a la taille voulue
  3. CLI      prune + quantize
  4. Blender  render2.py     rendu de contrôle (validation visuelle)

Sorties : models/_new/NOM.glb  et  dev/preview/NOM.png
Rien n'écrase les modèles en place : le remplacement est une étape séparée.

Usage : python dev/batch_models.py [NOM ...]     (sans argument = tout)
"""
import os, sys, subprocess, json, struct, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DL = r"C:\Users\asche\Downloads"
BLENDER = r"C:\Program Files\Blender Foundation\Blender 5.1\blender.exe"
OUT = os.path.join(ROOT, "models", "_new")
PREV = os.path.join(ROOT, "dev", "preview")
TMP = os.path.join(ROOT, "models", "_tmp")

# nom dans le jeu : (fichier original, triangles visés, taille de texture)
JOBS = {
    "residence":       ("resideance luxe",     45000, 2048),
    "immeuble1":       ("Immeuble1",           40000, 2048),
    "immeuble2":       ("Immeuble2",           40000, 2048),
    "immeuble3":       ("Immeuble3",           35000, 2048),
    "immeuble_large1": ("immeuble8",           45000, 2048),
    "immeuble_large2": ("Immeuble9",           45000, 2048),
    "immeuble_orange": ("Immeible orange",     30000, 2048),
    "bibliotheque":    ("Biblioteque",         35000, 2048),
    "brasserie":       ("Brasserie caf\u00e9", 30000, 2048),
    "pharmacie":       ("Pharmacie",           30000, 2048),
    "station":         ("Station service 1",   30000, 2048),
    "parc":            ("Parc1",               40000, 2048),
    "house1":          ("Maison 1",            25000, 2048),
    "house2":          ("Maison2",             25000, 2048),
    "house_bakery":    ("Boulangerie",         35000, 2048),
    "windmill":        ("Moulin",              25000, 2048),
    "row_grand":       ("3 grande immeuble",   45000, 2048),
    "row_petit":       ("3 Petit immeuble",    35000, 2048),
    "wheel":           ("grande roue",         30000, 2048),
    # petits objets ou objets répétés : budget serré, 1024 suffit
    "wsupport":        ("supprt grand roue",    8000, 1024),
    "palm":            ("Palmier",              8000, 1024),
    "lac":             ("Lac1",                 8000, 1024),
    "lamp":            ("Lampe",                2000, 1024),
    "barrier_train":   ("Barriere de train",    4000, 1024),
    "rail_meshy":      ("Rail",                 3000, 1024),
    "dirigeable":      ("Dirigable1",           8000, 1024),
    "mobilier_urbain": ("Objet1",              12000, 1024),
    "montagne1":       ("Montagne1",            6000, 1024),
    "montagne2":       ("Montagne2",            6000, 1024),
    "montagne3":       ("Montagne3",            6000, 1024),
}


def tris_and_tex(path):
    data = open(path, 'rb').read()
    off, js = 12, None
    while off < len(data):
        ln, ty = struct.unpack_from('<II', data, off)
        off += 8
        if ty == 0x4E4F534A:
            js = json.loads(data[off:off + ln])
        off += ln
    acc = js.get('accessors', [])
    t = 0
    for m in js.get('meshes', []):
        for pr in m.get('primitives', []):
            if 'indices' in pr:
                t += acc[pr['indices']]['count'] // 3
    return t, len(js.get('images', [])), os.path.getsize(path) / 1048576


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, errors='replace', **kw)


def process(name, src_name, target, tex):
    src = os.path.join(DL, src_name + ".glb")
    if not os.path.exists(src):
        return name, None, "original introuvable : %s" % src
    a = os.path.join(TMP, name + "_dec.glb")
    b = os.path.join(TMP, name + "_tex.glb")
    c = os.path.join(TMP, name + "_pr.glb")
    final = os.path.join(OUT, name + ".glb")

    r = run([BLENDER, "-b", "-P", os.path.join(ROOT, "dev", "decimate2.py"), "--", src, a, str(target)])
    if not os.path.exists(a):
        return name, None, "Blender: " + (r.stderr or r.stdout)[-300:]

    sys.path.insert(0, os.path.join(ROOT, "dev"))
    import albedo_webp
    try:
        albedo_webp.convert(a, b, tex, 88)
    except Exception as e:
        return name, None, "texture: %r" % e

    r = run(["npx.cmd", "--yes", "@gltf-transform/cli", "prune", b, c])
    if not os.path.exists(c):
        return name, None, "prune: " + (r.stderr or r.stdout)[-300:]
    r = run(["npx.cmd", "--yes", "@gltf-transform/cli", "quantize", c, final])
    if not os.path.exists(final):
        return name, None, "quantize: " + (r.stderr or r.stdout)[-300:]

    run([BLENDER, "-b", "-P", os.path.join(ROOT, "dev", "render2.py"), "--",
         final, os.path.join(PREV, name + ".png")], cwd=ROOT)

    for f in (a, b, c):
        try:
            os.remove(f)
        except OSError:
            pass
    return name, tris_and_tex(final), None


if __name__ == '__main__':
    for d in (OUT, PREV, TMP):
        os.makedirs(d, exist_ok=True)
    wanted = sys.argv[1:] or list(JOBS)
    print("=== %d modeles a traiter ===" % len(wanted), flush=True)
    ok, bad = [], []
    t0 = time.time()
    for i, name in enumerate(wanted, 1):
        if name not in JOBS:
            print("  ? %s : inconnu" % name, flush=True)
            continue
        src, target, tex = JOBS[name]
        st = time.time()
        n, info, err = process(name, src, target, tex)
        if err:
            bad.append((n, err))
            print("[%2d/%2d] ECHEC %-18s %s" % (i, len(wanted), n, err.replace("\n", " ")[:150]), flush=True)
        else:
            t, im, mb = info
            old = os.path.join(ROOT, "models", n + ".glb")
            oldmb = os.path.getsize(old) / 1048576 if os.path.exists(old) else 0
            ok.append((n, t, mb, oldmb))
            print("[%2d/%2d] OK    %-18s %7s tris  %d tex  %5.2f Mo (avant %5.2f)  %.0fs"
                  % (i, len(wanted), n, f"{t:,}", im, mb, oldmb, time.time() - st), flush=True)
    print("\n=== BILAN : %d reussis, %d echecs, %.1f min ===" % (len(ok), len(bad), (time.time() - t0) / 60), flush=True)
    if ok:
        print("poids total : %.1f Mo -> %.1f Mo" % (sum(x[3] for x in ok), sum(x[2] for x in ok)), flush=True)
    for n, e in bad:
        print("  ECHEC %s : %s" % (n, e.replace("\n", " ")[:200]), flush=True)
