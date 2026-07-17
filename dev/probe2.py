from gradio_client import Client
for sp in ["stabilityai/TripoSR", "JeffreyXiang/TRELLIS", "tencent/Hunyuan3D-2mini-Turbo"]:
    print("=" * 40, sp)
    try:
        c = Client(sp, verbose=False)
        print(c.view_api(return_format="str")[:1400])
    except Exception as e:
        print("FAIL:", str(e)[:150])
