import bpy, sys
argv = sys.argv
glb = argv[argv.index("--")+1]; out = argv[argv.index("--")+2]; ratio = float(argv[argv.index("--")+3])
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=glb)
meshes = [o for o in bpy.context.scene.objects if o.type=='MESH']
bpy.context.view_layer.objects.active = meshes[0]
for o in meshes: o.select_set(True)
if len(meshes) > 1: bpy.ops.object.join()
obj = bpy.context.view_layer.objects.active
before = len(obj.data.polygons)
dec = obj.modifiers.new("d", 'DECIMATE'); dec.ratio = ratio
bpy.ops.object.modifier_apply(modifier="d")
after = len(obj.data.polygons)
bpy.ops.export_scene.gltf(filepath=out, export_format='GLB')
print("DECIMATED tris:", before, "->", after)
