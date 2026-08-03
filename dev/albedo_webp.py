"""Ne garde que la texture albédo, la ré-encode en WebP, réécrit le GLB.

Usage :
  python dev/albedo_webp.py ENTREE.glb SORTIE.glb [TAILLE=2048] [QUALITE=88]

Pourquoi : builder.html rend tout en MeshBasicMaterial et n'utilise donc que
`map` (l'albédo). Les cartes normal / roughness / métallique / occlusion sont
téléchargées puis jamais affichées — environ 60 % du poids du fichier pour rien.
Les retirer paie largement le passage de l'albédo en 2048.

Contourne aussi le plantage de `gltf-transform --texture-compress webp` sur
cette machine (sharp/libvips : "VipsInterpretation" valeur 32 invalide).
"""
import json, struct, io, sys
from PIL import Image

ALBEDO_KEYS_TO_DROP = (
    ('metallicRoughnessTexture', 'pbr'),
    ('normalTexture', 'mat'),
    ('occlusionTexture', 'mat'),
    ('emissiveTexture', 'mat'),
)


def read_glb(path):
    data = open(path, 'rb').read()
    off, js, binc = 12, None, b''
    while off < len(data):
        ln, ty = struct.unpack_from('<II', data, off)
        off += 8
        chunk = data[off:off + ln]
        off += ln
        if ty == 0x4E4F534A:
            js = json.loads(chunk)
        elif ty == 0x004E4942:
            binc = chunk
    return js, binc


def write_glb(path, js, binc):
    j = json.dumps(js, separators=(',', ':')).encode('utf-8')
    j += b' ' * ((4 - len(j) % 4) % 4)
    b = binc + b'\x00' * ((4 - len(binc) % 4) % 4)
    out = struct.pack('<III', 0x46546C67, 2, 12 + 8 + len(j) + 8 + len(b))
    out += struct.pack('<II', len(j), 0x4E4F534A) + j
    out += struct.pack('<II', len(b), 0x004E4942) + b
    open(path, 'wb').write(out)


def convert(src, dst, size=2048, quality=88):
    js, binc = read_glb(src)

    dropped = 0
    for m in js.get('materials', []):
        pbr = m.get('pbrMetallicRoughness', {})
        for key, where in ALBEDO_KEYS_TO_DROP:
            holder = pbr if where == 'pbr' else m
            if key in holder:
                holder.pop(key)
                dropped += 1
        m.pop('emissiveFactor', None)

    # Les textures/images devenues orphelines doivent être SUPPRIMÉES du JSON et les
    # index renumérotés : les laisser en place avec un bufferView périmé fait planter
    # les outils en aval ("Cannot read properties of undefined (reading 'buffer')").
    used_tex = []
    for m in js.get('materials', []):
        bct = m.get('pbrMetallicRoughness', {}).get('baseColorTexture')
        if bct is not None and bct['index'] not in used_tex:
            used_tex.append(bct['index'])
    tex_remap = {old: new for new, old in enumerate(used_tex)}
    for m in js.get('materials', []):
        bct = m.get('pbrMetallicRoughness', {}).get('baseColorTexture')
        if bct is not None:
            bct['index'] = tex_remap[bct['index']]

    all_tex = js.get('textures', [])
    js['textures'] = [all_tex[i] for i in used_tex]

    used_img = []
    for t in js['textures']:
        s = t.get('extensions', {}).get('EXT_texture_webp', {}).get('source', t.get('source'))
        if s is not None and s not in used_img:
            used_img.append(s)
    img_remap = {old: new for new, old in enumerate(used_img)}
    for t in js['textures']:
        if 'source' in t:
            t['source'] = img_remap[t['source']]
        ext = t.get('extensions', {}).get('EXT_texture_webp')
        if ext and 'source' in ext:
            ext['source'] = img_remap[ext['source']]

    all_img = js.get('images', [])
    js['images'] = [all_img[i] for i in used_img]
    keep = set(range(len(js['images'])))

    bv = js['bufferViews']
    img_views = {im['bufferView'] for im in js.get('images', []) if 'bufferView' in im}

    new_bin = bytearray()
    newbv = []
    remap = {}
    for i in sorted(range(len(bv)), key=lambda k: bv[k].get('byteOffset', 0)):
        if i in img_views:
            continue
        v = bv[i]
        o = v.get('byteOffset', 0)
        payload = binc[o:o + v['byteLength']]
        while len(new_bin) % 4:
            new_bin.append(0)
        nv = dict(v)
        nv['byteOffset'] = len(new_bin)
        remap[i] = len(newbv)
        newbv.append(nv)
        new_bin += payload

    # Un matériau à découpe/transparence utilise le canal alpha de l'albédo :
    # le convertir en RGB effacerait les feuillages et les vitres.
    need_alpha = any(m.get('alphaMode', 'OPAQUE') != 'OPAQUE' for m in js.get('materials', []))

    stats = []
    for idx, im in enumerate(js.get('images', [])):
        if idx not in keep or 'bufferView' not in im:
            continue
        v = bv[im['bufferView']]
        o = v.get('byteOffset', 0)
        raw = binc[o:o + v['byteLength']]
        img = Image.open(io.BytesIO(raw))
        img = img.convert('RGBA' if need_alpha else 'RGB')
        w0, h0 = img.size
        if max(img.size) > size:
            img = img.resize((size, size), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, 'WEBP', quality=quality, method=5)
        blob = buf.getvalue()
        stats.append("%dx%d %dKo -> %dx%d WebP %dKo" % (w0, h0, len(raw) // 1024, img.size[0], img.size[1], len(blob) // 1024))
        while len(new_bin) % 4:
            new_bin.append(0)
        newbv.append({'buffer': 0, 'byteOffset': len(new_bin), 'byteLength': len(blob)})
        im['bufferView'] = len(newbv) - 1
        im['mimeType'] = 'image/webp'
        new_bin += blob

    def fix(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if k == 'bufferView' and isinstance(v, int) and v in remap:
                    node[k] = remap[v]
                else:
                    fix(v)
        elif isinstance(node, list):
            for x in node:
                fix(x)

    for key in ('accessors', 'meshes', 'skins', 'animations'):
        fix(js.get(key, []))

    js['bufferViews'] = newbv
    js['buffers'] = [{'byteLength': len(new_bin)}]
    write_glb(dst, js, bytes(new_bin))
    return dropped, stats


if __name__ == '__main__':
    a = sys.argv[1:]
    d, s = convert(a[0], a[1], int(a[2]) if len(a) > 2 else 2048, int(a[3]) if len(a) > 3 else 88)
    print("  cartes inutiles retirees : %d" % d)
    for line in s:
        print("  albedo : %s" % line)
