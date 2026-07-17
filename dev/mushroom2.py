import bpy, sys, math, random

argv = sys.argv
out = argv[argv.index("--") + 1] if "--" in argv else "mushroom2.glb"
bpy.ops.wm.read_factory_settings(use_empty=True)
random.seed(4)

def mat(name, col, rough=0.4, coat=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*col, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = 0.0
    if "Coat Weight" in b.inputs: b.inputs["Coat Weight"].default_value = coat
    return m

red = mat("Cap", (0.74, 0.045, 0.035), rough=0.30, coat=0.12)   # rouge profond
cream = mat("Cream", (0.96, 0.93, 0.83), rough=0.5)

# --- PIED bulbeux, haut (profil de vase) ---
SH = 1.7                                                          # hauteur du pied
bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=0.36, depth=SH, location=(0, 0, SH / 2))
stem = bpy.context.active_object; stem.name = "Stem"
for v in stem.data.vertices:
    t = (v.co.z + SH / 2) / SH                                    # 0 bas .. 1 haut
    prof = 0.60 + 0.78 * math.exp(-((t - 0.14) / 0.14) ** 2) + 0.40 * math.exp(-((t - 0.90) / 0.10) ** 2)
    v.co.x *= prof; v.co.y *= prof
for p in stem.data.polygons: p.use_smooth = True
stem.data.materials.append(cream)

TOP = SH                                                          # haut du pied
# --- Collerette (jupe évasée) ---
bpy.ops.mesh.primitive_cone_add(vertices=32, radius1=0.52, radius2=0.30, depth=0.14, location=(0, 0, TOP - 0.18))
skirt = bpy.context.active_object
for p in skirt.data.polygons: p.use_smooth = True
skirt.data.materials.append(cream)

# --- Lamelles / dessous du chapeau ---
bpy.ops.mesh.primitive_cone_add(vertices=64, radius1=1.18, radius2=0.30, depth=0.34, location=(0, 0, TOP + 0.02))
gills = bpy.context.active_object
for p in gills.data.polygons: p.use_smooth = True
gills.data.materials.append(cream)

# --- Chapeau rouge bombé ---
CZ = TOP + 0.10
CRz = 0.82
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, segments=44, ring_count=26, location=(0, 0, CZ))
cap = bpy.context.active_object; cap.name = "Cap"
cap.scale = (1.22, 1.22, CRz)
for v in cap.data.vertices:
    if v.co.z < 0: v.co.z *= 0.05
for p in cap.data.polygons: p.use_smooth = True
cap.data.materials.append(red)

# --- POIS blancs répartis régulièrement (spirale de Fibonacci) sur le dôme ---
Rx = 1.22
golden = math.pi * (3 - math.sqrt(5))
n = 26
for i in range(n):
    yy = 1 - (i / (n - 1)) * 0.80                                 # cos(phi) : du sommet (1) vers le bord (~0.2)
    r = math.sqrt(max(0.0, 1 - yy * yy))
    theta = golden * i
    x = Rx * r * math.cos(theta)
    y = Rx * r * math.sin(theta)
    z = CZ + CRz * yy
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.105, location=(x, y, z))
    d = bpy.context.active_object
    d.scale = (1, 1, 0.5)
    for p in d.data.polygons: p.use_smooth = True
    d.data.materials.append(cream)

bpy.ops.object.select_all(action='SELECT')
bpy.context.view_layer.objects.active = cap
bpy.ops.object.join()

bpy.ops.export_scene.gltf(filepath=out, export_format='GLB')
print("MUSHROOM2_EXPORTED:", out)
