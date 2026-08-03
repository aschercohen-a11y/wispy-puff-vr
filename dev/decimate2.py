"""Décimation Blender avec soudure préalable des sommets.

Usage :
  blender -b -P dev/decimate2.py -- ENTREE.glb SORTIE.glb NB_TRIANGLES_CIBLE [SEUIL_SOUDURE]

Pourquoi ce script et pas `gltf-transform simplify` : les modèles Meshy sortent
découpés en nombreuses pièces séparées. meshoptimizer préserve les bords de
maillage, donc quand presque chaque triangle touche un bord il ne peut plus rien
effondrer — on bute sur un plancher (255 k triangles pour la résidence, quelle
que soit la valeur de --ratio). Souder les sommets coïncidents supprime ces
bords artificiels et débloque la décimation.
"""
import bpy, bmesh, sys

argv = sys.argv[sys.argv.index("--") + 1:]
src, dst, target = argv[0], argv[1], int(argv[2])
weld = float(argv[3]) if len(argv) > 3 else 0.0005

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)

meshes = [o for o in bpy.context.scene.objects if o.type == 'MESH']
if not meshes:
    raise SystemExit("aucun maillage importe")
bpy.context.view_layer.objects.active = meshes[0]
for o in meshes:
    o.select_set(True)
if len(meshes) > 1:
    bpy.ops.object.join()
obj = bpy.context.view_layer.objects.active

before = len(obj.data.polygons)

# Soudure des sommets coïncidents (supprime les bords entre pièces jointives).
bm = bmesh.new()
bm.from_mesh(obj.data)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=weld)
bm.to_mesh(obj.data)
bm.free()
welded = len(obj.data.polygons)

ratio = min(1.0, max(0.002, target / float(welded)))
dec = obj.modifiers.new("dec", 'DECIMATE')
dec.decimate_type = 'COLLAPSE'
dec.use_collapse_triangulate = True
dec.ratio = ratio
bpy.ops.object.modifier_apply(modifier="dec")
after = len(obj.data.polygons)

bpy.ops.export_scene.gltf(
    filepath=dst,
    export_format='GLB',
    export_apply=True,
    export_yup=True,
)
print("RESULTAT %d -> soude %d -> ratio %.4f -> %d triangles" % (before, welded, ratio, after))
