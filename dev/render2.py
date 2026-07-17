import bpy, sys, math
from mathutils import Vector

argv = sys.argv
glb = argv[argv.index("--") + 1]
out = argv[argv.index("--") + 2]

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)

# --- bounding box de tout le modele ---
mn = Vector((1e9, 1e9, 1e9)); mx = Vector((-1e9, -1e9, -1e9))
for o in bpy.context.scene.objects:
    if o.type == 'MESH':
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            for i in range(3):
                mn[i] = min(mn[i], w[i]); mx[i] = max(mx[i], w[i])
center = (mn + mx) * 0.5
size = max((mx - mn).x, (mx - mn).y, (mx - mn).z, 0.1)

def look_at(obj, target):
    d = obj.location - target
    obj.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()

# camera : recule selon la taille de l'objet
cam_data = bpy.data.cameras.new("Cam"); cam = bpy.data.objects.new("Cam", cam_data)
bpy.context.scene.collection.objects.link(cam)
dist = size * 1.9
cam.location = center + Vector((dist * 0.8, -dist, dist * 0.55))
look_at(cam, center)
bpy.context.scene.camera = cam

# lumieres
for loc, e in [((1, -1, 2), 2.0), ((-1, -0.5, 1), 0.9)]:
    ld = bpy.data.lights.new("L", type='SUN'); ld.energy = e
    lo = bpy.data.objects.new("L", ld); bpy.context.scene.collection.objects.link(lo)
    lo.location = center + Vector(loc) * size; look_at(lo, center)

# ciel clair
w = bpy.data.worlds.new("W"); bpy.context.scene.world = w
w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.55, 0.72, 0.9, 1)
w.node_tree.nodes["Background"].inputs[1].default_value = 1.0

sc = bpy.context.scene
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 40; sc.cycles.use_denoising = True
try: sc.view_settings.view_transform = 'Standard'
except Exception: pass
sc.render.resolution_x = 700; sc.render.resolution_y = 560
sc.render.filepath = out
bpy.ops.render.render(write_still=True)
print("RENDERED:", out, "size:", round(size, 2))
