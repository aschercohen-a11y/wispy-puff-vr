import bpy, sys, math, random

argv = sys.argv
out = argv[argv.index("--") + 1] if "--" in argv else "carrot.glb"
bpy.ops.wm.read_factory_settings(use_empty=True)
random.seed(7)

def mat(name, col, rough=0.5):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*col, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = 0.0
    return m

# --- Palette fidèle à la référence ---
orange = mat("Orange", (0.93, 0.37, 0.045), 0.42)   # carotte vif
green = mat("Green", (0.28, 0.58, 0.11), 0.5)       # feuille foncée
green2 = mat("Green2", (0.48, 0.78, 0.20), 0.5)     # feuille claire
green3 = mat("Green3", (0.37, 0.68, 0.15), 0.5)     # feuille moyenne
wood = mat("Wood", (0.49, 0.29, 0.13), 0.6)         # bois porte
tan = mat("Tan", (0.85, 0.70, 0.44), 0.6)           # pierre/cadre beige
dark = mat("Glass", (0.11, 0.17, 0.25), 0.25)       # vitre bleu nuit
chim = mat("Chim", (0.80, 0.62, 0.40), 0.7)         # cheminée bois clair
grass = mat("Grass", (0.30, 0.62, 0.16), 0.9)       # herbe vive

def sm(o, flat=False):
    for p in o.data.polygons: p.use_smooth = (not flat)

# --- CORPS carotte (effilé vers le bas) + rainures ---
bpy.ops.mesh.primitive_uv_sphere_add(radius=1.0, segments=56, ring_count=36, location=(0, 0, 1.55))
body = bpy.context.active_object; body.name = "Body"
body.scale = (1.0, 1.0, 1.40)
for v in body.data.vertices:
    tz = (v.co.z + 1.40) / 2.80
    fac = 0.52 + 0.48 * tz
    ridge = 1.0 + 0.024 * math.sin(v.co.z * 22)
    v.co.x *= fac * ridge; v.co.y *= fac * ridge
sm(body); body.data.materials.append(orange)
TOPZ = 1.55 + 1.40

# --- FANES : feuilles larges, courbées, 3 tons, en éventail (2 couches) ---
def leaf(h, wflat, tilt, ang, mtl):
    bpy.ops.mesh.primitive_cone_add(vertices=12, radius1=0.17, radius2=0.0, depth=h, location=(0, 0, 0))
    lf = bpy.context.active_object
    lf.scale = (1, wflat, 1)
    # courbe la feuille : on penche + on décale la pointe
    lf.rotation_euler = (math.radians(tilt) * math.cos(ang), math.radians(tilt) * math.sin(ang), 0)
    lf.location = (math.cos(ang) * 0.20, math.sin(ang) * 0.20, TOPZ + h * 0.45 - 0.12)
    sm(lf); lf.data.materials.append(mtl)
tones = [green, green3, green2]
for i in range(11):
    a = (i / 11) * 2 * math.pi
    leaf(1.6 + random.uniform(-0.2, 0.35), 0.42, 38 + random.uniform(-7, 7), a, tones[i % 3])
for i in range(7):
    a = (i / 7) * 2 * math.pi + 0.3
    leaf(1.15 + random.uniform(-0.1, 0.2), 0.40, 20 + random.uniform(-5, 5), a, green2)
leaf(1.8, 0.42, 5, 0, green2)   # feuille centrale

FRONT = -0.94

# --- PORTE arquée : cadre pierre + porte bois + fenêtre ronde + poignée ---
def arched(w, h, d, z, material, y):
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, y, z))
    box = bpy.context.active_object; box.scale = (w, d, h * 0.5); box.data.materials.append(material)
    bpy.ops.mesh.primitive_cylinder_add(vertices=28, radius=w, depth=d, location=(0, y, z + h * 0.5))
    ar = bpy.context.active_object; ar.rotation_euler = (math.radians(90), 0, 0); sm(ar); ar.data.materials.append(material)
arched(0.37, 0.98, 0.10, 0.66, tan, FRONT + 0.03)
arched(0.29, 0.80, 0.12, 0.62, wood, FRONT - 0.03)
bpy.ops.mesh.primitive_cylinder_add(vertices=20, radius=0.10, depth=0.06, location=(0, FRONT - 0.10, 1.02))
dw = bpy.context.active_object; dw.rotation_euler = (math.radians(90), 0, 0); sm(dw); dw.data.materials.append(dark)
bpy.ops.mesh.primitive_uv_sphere_add(radius=0.035, location=(0.14, FRONT - 0.12, 0.66))
kn = bpy.context.active_object; sm(kn); kn.data.materials.append(tan)

# --- FENÊTRES rondes (anneau bois + vitre + croix) ---
def window(x, z, R):
    bpy.ops.mesh.primitive_torus_add(major_radius=R, minor_radius=R * 0.27, location=(x, FRONT + 0.02, z))
    rg = bpy.context.active_object; rg.rotation_euler = (math.radians(90), 0, 0); sm(rg); rg.data.materials.append(wood)
    bpy.ops.mesh.primitive_cylinder_add(vertices=28, radius=R * 0.9, depth=0.05, location=(x, FRONT + 0.06, z))
    gl = bpy.context.active_object; gl.rotation_euler = (math.radians(90), 0, 0); sm(gl); gl.data.materials.append(dark)
    for rot in (0, 1):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(x, FRONT - 0.02, z))
        cr = bpy.context.active_object
        cr.scale = (R * 0.92, 0.03, 0.035) if rot == 0 else (0.035, 0.03, R * 0.92)
        cr.data.materials.append(wood)
window(0.60, 1.72, 0.24)
window(-0.56, 2.06, 0.19)

# --- CHEMINÉE (bois clair) ---
bpy.ops.mesh.primitive_cylinder_add(vertices=18, radius=0.16, depth=0.72, location=(0.70, 0.30, TOPZ - 0.15))
ch = bpy.context.active_object; ch.rotation_euler = (math.radians(12), 0, 0); sm(ch); ch.data.materials.append(chim)

# --- BOÎTE AUX LETTRES (orange sur poteau) ---
bpy.ops.mesh.primitive_cylinder_add(vertices=8, radius=0.03, depth=0.35, location=(0.95, -0.55, 0.28))
po = bpy.context.active_object; sm(po); po.data.materials.append(wood)
bpy.ops.mesh.primitive_cube_add(size=1, location=(0.95, -0.55, 0.5))
mb = bpy.context.active_object; mb.scale = (0.09, 0.14, 0.08); sm(mb); mb.data.materials.append(orange)

# --- BASE : butte + buissons ronds ---
bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=1.5, depth=0.28, location=(0, 0, 0.1))
mound = bpy.context.active_object; sm(mound); mound.data.materials.append(grass)
for i in range(10):
    a = random.uniform(0, 6.28); rr = random.uniform(0.85, 1.35)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=random.uniform(0.12, 0.24), location=(math.cos(a) * rr, math.sin(a) * rr, 0.26))
    bsh = bpy.context.active_object; sm(bsh); bsh.data.materials.append([grass, green2, green3][i % 3])

bpy.ops.export_scene.gltf(filepath=out, export_format='GLB')
print("CARROT_EXPORTED:", out)
