import bpy, sys, math

argv = sys.argv
out = argv[argv.index("--") + 1] if "--" in argv else "house.glb"
bpy.ops.wm.read_factory_settings(use_empty=True)

def mat(name, base, rough=0.7, emit=None, es=0.0):
    m = bpy.data.materials.new(name); m.use_nodes = True
    b = m.node_tree.nodes.get("Principled BSDF")
    b.inputs["Base Color"].default_value = (*base, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = 0.0
    if emit and "Emission Color" in b.inputs:
        b.inputs["Emission Color"].default_value = (*emit, 1)
        b.inputs["Emission Strength"].default_value = es
    return m

def box(name, sx, sy, sz, loc, material):
    bpy.ops.mesh.primitive_cube_add(size=2, location=loc)
    o = bpy.context.active_object; o.name = name
    o.scale = (sx, sy, sz)
    for p in o.data.polygons: p.use_smooth = False
    o.data.materials.append(material)
    return o

wall_m = mat("Wall", (0.94, 0.88, 0.74))
roof_m = mat("Roof", (0.78, 0.30, 0.26))
door_m = mat("Door", (0.42, 0.26, 0.16))
win_m  = mat("Win",  (1.0, 0.86, 0.5), rough=0.3, emit=(1.0, 0.82, 0.45), es=2.2)
chim_m = mat("Chim", (0.55, 0.42, 0.36))

# Murs
box("Walls", 1.4, 1.4, 1.1, (0, 0, 1.1), wall_m)

# Toit : pyramide (cône 4 côtés) qui déborde, tourné 45° pour aligner sur le carré
bpy.ops.mesh.primitive_cone_add(vertices=4, radius1=2.2, radius2=0, depth=1.5, location=(0, 0, 2.95))
roof = bpy.context.active_object; roof.name = "Roof"
roof.rotation_euler[2] = math.pi / 4
for p in roof.data.polygons: p.use_smooth = False
roof.data.materials.append(roof_m)

# Porte (façade -Y)
box("Door", 0.32, 0.08, 0.55, (0, -1.42, 0.55), door_m)
# Fenêtres (façade -Y), lumineuses
box("WinL", 0.34, 0.06, 0.34, (-0.75, -1.42, 1.35), win_m)
box("WinR", 0.34, 0.06, 0.34, (0.75, -1.42, 1.35), win_m)
# Fenêtre côté +X
box("WinS", 0.06, 0.34, 0.34, (1.42, 0.3, 1.35), win_m)
# Cheminée
box("Chimney", 0.2, 0.2, 0.55, (0.7, 0.5, 3.0), chim_m)

bpy.ops.export_scene.gltf(filepath=out, export_format='GLB')
print("HOUSE_EXPORTED:", out)
