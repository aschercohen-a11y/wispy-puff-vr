import bpy, sys, math

# --- argument de sortie (apres "--") ---
argv = sys.argv
out = argv[argv.index("--") + 1] if "--" in argv else "crystal.glb"

# --- scene vierge ---
bpy.ops.wm.read_factory_settings(use_empty=True)

# --- cristal : prisme hexagonal + pointe (bipyramide allongee) ---
# corps : cylindre hexagonal
bpy.ops.mesh.primitive_cylinder_add(vertices=6, radius=0.5, depth=1.2)
body = bpy.context.active_object
body.name = "Crystal"

# pointe haute : cone hexagonal
bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.5, radius2=0.0, depth=0.7, location=(0, 0, 0.95))
tip = bpy.context.active_object
# pointe basse : cone hexagonal inverse
bpy.ops.mesh.primitive_cone_add(vertices=6, radius1=0.5, radius2=0.0, depth=0.7, location=(0, 0, -0.95))
tipb = bpy.context.active_object
tipb.rotation_euler[0] = math.pi

# fusionner en un seul objet
bpy.ops.object.select_all(action='DESELECT')
body.select_set(True); tip.select_set(True); tipb.select_set(True)
bpy.context.view_layer.objects.active = body
bpy.ops.object.join()

# facettes nettes (look gemme)
for p in body.data.polygons:
    p.use_smooth = False

# --- materiau : cristal magenta VERRE + GLOW (comme les neons du jeu) ---
mat = bpy.data.materials.new("CrystalMat")
mat.use_nodes = True
bsdf = mat.node_tree.nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value = (0.90, 0.15, 0.80, 1)  # magenta saturé
bsdf.inputs["Metallic"].default_value = 0.0
bsdf.inputs["Roughness"].default_value = 0.08                    # facettes brillantes
if "IOR" in bsdf.inputs:
    bsdf.inputs["IOR"].default_value = 1.45                      # verre
if "Transmission Weight" in bsdf.inputs:
    bsdf.inputs["Transmission Weight"].default_value = 0.25      # un peu translucide, garde la couleur
# GLOW interieur (domine la scene → effet neon)
if "Emission Color" in bsdf.inputs:
    bsdf.inputs["Emission Color"].default_value = (1.0, 0.20, 0.85, 1)
if "Emission Strength" in bsdf.inputs:
    bsdf.inputs["Emission Strength"].default_value = 2.5
body.data.materials.append(mat)

# --- export glb ---
bpy.ops.export_scene.gltf(filepath=out, export_format='GLB')
print("CRYSTAL_EXPORTED:", out)
print("VERTS:", len(body.data.vertices), "FACES:", len(body.data.polygons))
