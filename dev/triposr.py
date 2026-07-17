from gradio_client import Client, handle_file
import shutil

IMG = r"C:\Users\asche\Downloads\Nouveau dossier (123)\maison1.png"
OUT = r"C:\Users\asche\Downloads\claude\Oculus\models\carrot_ai.glb"

c = Client("stabilityai/TripoSR", verbose=False)
print("Preprocess (détourage)...")
proc = c.predict(handle_file(IMG), True, 0.85, api_name="/preprocess")
print("  processed:", proc)
print("Génération 3D...")
res = c.predict(handle_file(proc), 256, api_name="/generate")
print("RESULT:", res)
glb = res[1] if isinstance(res, (list, tuple)) else res
if isinstance(glb, dict):
    glb = glb.get("path") or glb.get("value")
shutil.copy(glb, OUT)
print("SAVED:", OUT)
