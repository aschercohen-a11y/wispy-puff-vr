import bpy, sys, math, os
from mathutils import Vector

argv = sys.argv
glb = argv[argv.index("--") + 1]
outdir = argv[argv.index("--") + 2]
N = 16
os.makedirs(outdir, exist_ok=True)

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)

mn = Vector((1e9,)*3); mx = Vector((-1e9,)*3)
for o in bpy.context.scene.objects:
    if o.type == 'MESH':
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            for i in range(3):
                mn[i] = min(mn[i], w[i]); mx[i] = max(mx[i], w[i])
center = (mn + mx) * 0.5
size = max((mx-mn).x, (mx-mn).y, (mx-mn).z, 0.1)

def look_at(obj, t):
    d = obj.location - t; obj.rotation_euler = d.to_track_quat('Z', 'Y').to_euler()

cam_data = bpy.data.cameras.new("Cam"); cam = bpy.data.objects.new("Cam", cam_data)
bpy.context.scene.collection.objects.link(cam); bpy.context.scene.camera = cam

# lumieres fixes
for loc, e in [((1, -1, 2), 2.2), ((-1, 1, 1), 1.0)]:
    ld = bpy.data.lights.new("L", type='SUN'); ld.energy = e
    lo = bpy.data.objects.new("L", ld); bpy.context.scene.collection.objects.link(lo)
    lo.location = center + Vector(loc)*size; look_at(lo, center)
w = bpy.data.worlds.new("W"); bpy.context.scene.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.55, 0.72, 0.9, 1)

sc = bpy.context.scene
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 16; sc.cycles.use_denoising = True
try: sc.view_settings.view_transform = 'Standard'
except Exception: pass
sc.render.resolution_x = 440; sc.render.resolution_y = 440

dist = size * 2.0
tgt = center + Vector((0, 0, size * 0.05))
for i in range(N):
    a = 2 * math.pi * i / N
    cam.location = center + Vector((math.cos(a)*dist, math.sin(a)*dist, dist*0.42))
    look_at(cam, tgt)
    sc.render.filepath = os.path.join(outdir, "f%02d.png" % i)
    bpy.ops.render.render(write_still=True)
print("FRAMES_DONE")
