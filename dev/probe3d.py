from gradio_client import Client
import sys

spaces = [
    "stabilityai/stable-fast-3d",
    "tencent/Hunyuan3D-2",
    "microsoft/TRELLIS",
    "stabilityai/TripoSR",
    "hysts/TripoSR",
]
for sp in spaces:
    print("=" * 50)
    print("SPACE:", sp)
    try:
        c = Client(sp, verbose=False)
        api = c.view_api(return_format="dict")
        named = api.get("named_endpoints", {})
        print("  OK — endpoints:", list(named.keys())[:8])
    except Exception as e:
        print("  FAIL:", str(e)[:160])
