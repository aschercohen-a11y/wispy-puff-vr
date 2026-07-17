from gradio_client import Client, handle_file
import shutil, sys

IMG = r"C:\Users\asche\Downloads\Nouveau dossier (123)\maison1.png"
OUT = r"C:\Users\asche\Downloads\claude\Oculus\models\carrot_ai.glb"

print("Connexion à Stable Fast 3D...")
c = Client("stabilityai/stable-fast-3d", verbose=False)
print("Génération 3D (image -> modèle texturé)...")
res = c.predict(
    input_image=handle_file(IMG),
    foreground_ratio=0.85,
    remesh_option="None",
    vertex_count=-1,
    texture_size=2048,
    api_name="/run_button",
)
print("RESULT:", res)
# res = (preview_bg_removal, 3d_model_path)
glb = res[1] if isinstance(res, (list, tuple)) else res
if isinstance(glb, dict):
    glb = glb.get("path") or glb.get("value")
shutil.copy(glb, OUT)
print("SAVED:", OUT)
