import bpy, sys
from mathutils import Vector

argv = sys.argv
glb = argv[argv.index("--") + 1]
out = argv[argv.index("--") + 2]

bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)

mn = Vector((1e9, 1e9, 1e9)); mx = Vector((-1e9, -1e9, -1e9))
for o in bpy.context.scene.objects:
    if o.type == 'MESH':
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            for i in range(3):
                mn[i] = min(mn[i], w[i]); mx[i] = max(mx[i], w[i])
center = (mn + mx) * 0.5
size = max((mx - mn).x, (mx - mn).y, (mx - mn).z, 0.1)

# camera VUE DE DESSUS (regarde -Z, donc pile au-dessus en Y-up gltf)
cam_data = bpy.data.cameras.new("Cam"); cam = bpy.data.objects.new("Cam", cam_data)
cam_data.type = 'ORTHO'; cam_data.ortho_scale = size * 1.15
bpy.context.scene.collection.objects.link(cam)
cam.location = center + Vector((0, 0, size * 3))   # au-dessus (axe Z monde blender = Y gltf après import? gltf importe Y-up -> Blender Z-up)
cam.rotation_euler = (0, 0, 0)                       # regarde vers le bas (-Z)
bpy.context.scene.camera = cam

for loc, e in [((0.5, -0.5, 2), 2.5), ((-0.5, 0.5, 1.5), 1.2)]:
    ld = bpy.data.lights.new("L", type='SUN'); ld.energy = e
    lo = bpy.data.objects.new("L", ld); bpy.context.scene.collection.objects.link(lo)
    lo.location = center + Vector(loc) * size

w = bpy.data.worlds.new("W"); bpy.context.scene.world = w
w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.3, 0.3, 0.3, 1)
w.node_tree.nodes["Background"].inputs[1].default_value = 1.0

sc = bpy.context.scene
sc.render.engine = 'CYCLES'; sc.cycles.device = 'CPU'; sc.cycles.samples = 32; sc.cycles.use_denoising = True
try: sc.view_settings.view_transform = 'Standard'
except Exception: pass
sc.render.resolution_x = 600; sc.render.resolution_y = 600
sc.render.filepath = out
bpy.ops.render.render(write_still=True)
print("TOP RENDERED:", out)
